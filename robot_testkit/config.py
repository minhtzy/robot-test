from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml

from .errors import ConfigError


@dataclass(frozen=True)
class WorkspaceConfig:
    root: Path
    ros_setup: str = ""
    build_args: List[str] = field(default_factory=list)
    lint_test_args: List[str] = field(default_factory=list)
    log_dir: Path = Path("logs")
    report_dir: Path = Path("reports")
    memory_dir: Path = Path(".robot-test-memory")


@dataclass(frozen=True)
class BrowserConfig:
    login_url: str
    username_env: str = "ROBOT_USERNAME"
    password_env: str = "ROBOT_PASSWORD"
    vscode_tool_command_env: str = "VSCODE_BROWSER_TOOL_COMMAND"
    adapter_preference: List[str] = field(default_factory=lambda: ["vscode", "playwright", "system"])


@dataclass(frozen=True)
class FanucBridgeConfig:
    endpoint: str
    token_env: str = "FANUC_BRIDGE_TOKEN"
    timeout_seconds: int = 30


@dataclass(frozen=True)
class RobotProfile:
    name: str
    robot_type: str
    target: str
    launch: Dict[str, Any]
    nodes: List[Dict[str, Any]]
    allowlist_services: List[str]
    monitor_topics: List[str]

    @property
    def is_real(self) -> bool:
        return self.target == "real"


@dataclass(frozen=True)
class RobotTestkitConfig:
    path: Path
    workspace: WorkspaceConfig
    browser: BrowserConfig
    fanuc_bridge: FanucBridgeConfig
    robots: Dict[str, RobotProfile]

    def profile(self, name: str) -> RobotProfile:
        try:
            return self.robots[name]
        except KeyError as exc:
            available = ", ".join(sorted(self.robots))
            raise ConfigError(f"unknown robot profile '{name}'. Available: {available}") from exc


def _as_path(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base / path


def load_config(path: Union[str, Path] = "config/robot-testkit.yaml") -> RobotTestkitConfig:
    config_path = Path(path).resolve()
    if not config_path.exists():
        raise ConfigError(f"config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    base = config_path.parent.parent
    workspace_raw = raw.get("workspace", {})
    workspace_root = _as_path(base, workspace_raw.get("root", ".")).resolve()
    workspace = WorkspaceConfig(
        root=workspace_root,
        ros_setup=workspace_raw.get("ros_setup", ""),
        build_args=list(workspace_raw.get("build_args", [])),
        lint_test_args=list(workspace_raw.get("lint_test_args", [])),
        log_dir=_as_path(workspace_root, workspace_raw.get("log_dir", "logs")),
        report_dir=_as_path(workspace_root, workspace_raw.get("report_dir", "reports")),
        memory_dir=_as_path(workspace_root, workspace_raw.get("memory_dir", ".robot-test-memory")),
    )

    browser_raw = raw.get("browser", {})
    browser = BrowserConfig(
        login_url=browser_raw.get("login_url", "http://127.0.0.1"),
        username_env=browser_raw.get("username_env", "ROBOT_USERNAME"),
        password_env=browser_raw.get("password_env", "ROBOT_PASSWORD"),
        vscode_tool_command_env=browser_raw.get("vscode_tool_command_env", "VSCODE_BROWSER_TOOL_COMMAND"),
        adapter_preference=list(browser_raw.get("adapter_preference", ["vscode", "playwright", "system"])),
    )

    fanuc_raw = raw.get("fanuc_bridge", {})
    fanuc_bridge = FanucBridgeConfig(
        endpoint=fanuc_raw.get("endpoint", ""),
        token_env=fanuc_raw.get("token_env", "FANUC_BRIDGE_TOKEN"),
        timeout_seconds=int(fanuc_raw.get("timeout_seconds", 30)),
    )

    robots: Dict[str, RobotProfile] = {}
    for name, profile in (raw.get("robots") or {}).items():
        robots[name] = RobotProfile(
            name=name,
            robot_type=profile["robot_type"],
            target=profile["target"],
            launch=dict(profile.get("launch", {})),
            nodes=list(profile.get("nodes", [])),
            allowlist_services=list(profile.get("allowlist_services", [])),
            monitor_topics=list(profile.get("monitor_topics", [])),
        )

    if not robots:
        raise ConfigError("at least one robot profile is required")

    return RobotTestkitConfig(config_path, workspace, browser, fanuc_bridge, robots)
