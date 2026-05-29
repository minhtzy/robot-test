from __future__ import annotations

from typing import Any, Dict, List, Optional

from .runner import CommandResult, CommandRunner


def build_docker_run_command(launch: Dict[str, Any]) -> List[str]:
    command = ["docker", "run"]
    if launch.get("detach", True):
        command.append("-d")
    if launch.get("publish_all_ports", False):
        command.append("-P")
    if launch.get("name"):
        command.extend(["--name", launch["name"]])
    if launch.get("privileged", False):
        command.append("--privileged")
    if launch.get("user"):
        command.extend(["-u", str(launch["user"])])
    if launch.get("network"):
        command.extend(["--net", launch["network"]])
    for key, value in launch.get("env", {}).items():
        command.extend(["-e", f"{key}={value}"])
    for port in launch.get("ports", []):
        command.extend(["-p", str(port)])
    for volume in launch.get("volumes", []):
        command.extend(["-v", str(volume)])
    command.append(launch["image"])
    command.extend(str(arg) for arg in launch.get("args", []))
    return command


def ensure_docker_network(runner: CommandRunner, network: Optional[str], log_prefix: str) -> None:
    if not network:
        return
    inspect = runner.run(["docker", "network", "inspect", network], check=False, log_name=f"{log_prefix}_network_inspect")
    if not inspect.ok:
        runner.run(["docker", "network", "create", network], log_name=f"{log_prefix}_network_create")


def remove_existing_container(runner: CommandRunner, name: Optional[str], log_prefix: str) -> None:
    if not name:
        return
    runner.run(["docker", "rm", "-f", name], check=False, log_name=f"{log_prefix}_container_replace")
