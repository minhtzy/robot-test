from __future__ import annotations

import json
import sys
import time
from typing import Any, Dict, List, Optional

from .analyzer import analyze_logs
from .browser import browser_login
from .config import RobotProfile, RobotTestkitConfig
from .docker import build_docker_run_command, ensure_docker_network, remove_existing_container
from .fanuc import call_fanuc_bridge
from .memory import MemoryStore
from .runner import CommandResult, CommandRunner
from .safety import assert_confirmation, assert_service_allowed


def run_hook(name: str, runner: CommandRunner, payload: Optional[Dict[str, Any]] = None) -> Optional[CommandResult]:
    hook = runner.cwd / "hooks" / f"{name}.py"
    if not hook.exists():
        return None
    env = {"ROBOT_TESTKIT_HOOK_PAYLOAD": json.dumps(payload or {})}
    return runner.run([sys.executable, str(hook)], check=False, env=env, log_name=f"hook_{name}")


class RobotOrchestrator:
    def __init__(self, config: RobotTestkitConfig, *, dry_run: bool = False) -> None:
        self.config = config
        self.runner = CommandRunner(config.workspace.root, dry_run=dry_run, log_dir=config.workspace.log_dir)
        self.memory = MemoryStore(config.workspace.memory_dir)

    def build_source(self) -> CommandResult:
        run_hook("pre_build", self.runner)
        result = self.runner.run(["colcon", "build", *self.config.workspace.build_args], timeout=None, log_name="colcon_build")
        run_hook("post_build", self.runner, result.summary())
        return result

    def run_lint_tests(self) -> CommandResult:
        result = self.runner.run(["colcon", "test", *self.config.workspace.lint_test_args], timeout=None, log_name="colcon_test_lint")
        run_hook("post_lint", self.runner, result.summary())
        return result

    def launch_target(self, profile: RobotProfile) -> Dict[str, Any]:
        run_hook("pre_launch", self.runner, {"profile": profile.name})
        launch = profile.launch
        mode = launch.get("mode")
        if mode == "docker_run":
            ensure_docker_network(self.runner, launch.get("network"), f"launch_{profile.name}")
            if launch.get("replace_existing", False):
                remove_existing_container(self.runner, launch.get("name"), f"launch_{profile.name}")
            self.runner.run(build_docker_run_command(launch), log_name=f"launch_{profile.name}")
            health_command = launch.get("health_command")
            if health_command:
                self.runner.run(["sh", "-lc", health_command], check=False, log_name=f"health_{profile.name}")
            return {"mode": mode, "container": launch.get("name"), "network": launch.get("network")}
        if mode == "docker_compose":
            compose_file = launch["compose_file"]
            compose_profile = launch["profile"]
            ensure_docker_network(self.runner, launch.get("network"), f"launch_{profile.name}")
            self.runner.run(
                ["docker", "compose", "-f", compose_file, "--profile", compose_profile, "up", "-d"],
                log_name=f"launch_{profile.name}",
            )
            health_command = launch.get("health_command")
            if health_command:
                self.runner.run(["sh", "-lc", health_command], check=False, log_name=f"health_{profile.name}")
            return {"mode": mode, "profile": compose_profile, "network": launch.get("network")}
        if mode == "fanuc_bridge":
            return call_fanuc_bridge(self.config.fanuc_bridge, "launch", {"profile": launch.get("bridge_profile", "default")}, dry_run=self.runner.dry_run)
        if mode == "attach":
            return {"mode": "attach", "profile": profile.name}
        return {"mode": mode or "unknown", "profile": profile.name}

    def login_browser(self) -> Dict[str, Any]:
        result = browser_login(self.config.browser, self.runner)
        return {"adapter": result.adapter, "opened": result.opened, "message": result.message}

    def start_nodes(self, profile: RobotProfile) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for node in profile.nodes:
            command = ["ros2", "run", node["package"], node["executable"], *node.get("args", [])]
            result = self.runner.run(command, check=False, log_name=f"node_{node['name']}")
            results.append({"name": node["name"], **result.summary()})
        return results

    def call_service(self, profile: RobotProfile, service: str, service_type: str, payload: str, *, confirmed: bool) -> CommandResult:
        assert_service_allowed(service, profile)
        assert_confirmation(service, profile, confirmed)
        run_hook("pre_robot_action", self.runner, {"profile": profile.name, "service": service})
        result = self.runner.run(["ros2", "service", "call", service, service_type, payload], log_name=f"service_{service.strip('/').replace('/', '_')}")
        run_hook("post_robot_action", self.runner, result.summary())
        return result

    def monitor_topic(self, topic: str, *, duration_seconds: int = 10) -> CommandResult:
        return self.runner.run(["timeout", str(duration_seconds), "ros2", "topic", "echo", topic], check=False, log_name=f"topic_{topic.strip('/').replace('/', '_')}")

    def collect_logs(self) -> Dict[str, Any]:
        self.config.workspace.report_dir.mkdir(parents=True, exist_ok=True)
        report = analyze_logs(self.config.workspace.log_dir)
        path = self.config.workspace.report_dir / "latest.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"report_path": str(path), **report}

    def update_memory(self, profile: RobotProfile, analysis: Dict[str, Any]) -> Dict[str, Any]:
        run_id = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        record = {"run_id": run_id, "profile": profile.name, "robot_type": profile.robot_type, "analysis": analysis}
        self.memory.append_run(record)
        if analysis.get("status") == "fail" and analysis.get("findings"):
            first = analysis["findings"][0]["line"]
            self.memory.append_lesson(
                {
                    "run_id": run_id,
                    "robot_type": profile.robot_type,
                    "command": "run_scenario",
                    "failure_signature": first[:160],
                    "root_cause": "unknown",
                    "lesson": "Review latest report and matching command log before retrying.",
                    "confidence": 0.3,
                }
            )
        run_hook("on_learning_update", self.runner, record)
        return {"run_id": run_id}

    def run_scenario(self, profile_name: str, *, confirmed: bool = False, monitor_seconds: int = 10) -> Dict[str, Any]:
        profile = self.config.profile(profile_name)
        self.build_source()
        self.run_lint_tests()
        launch = self.launch_target(profile)
        browser = self.login_browser()
        nodes = self.start_nodes(profile)
        topics = [self.monitor_topic(topic, duration_seconds=monitor_seconds).summary() for topic in profile.monitor_topics]
        analysis = self.collect_logs()
        memory = self.update_memory(profile, analysis)
        return {"profile": profile.name, "launch": launch, "browser": browser, "nodes": nodes, "topics": topics, "analysis": analysis, "memory": memory, "confirmed": confirmed}
