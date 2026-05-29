from __future__ import annotations

from typing import Any, Dict, List, Optional

from .config import RobotProfile
from .errors import ConfigError


def selected_packages(profile: Optional[RobotProfile], kind: str) -> List[str]:
    if not profile:
        return []
    packages = profile.build_packages if kind == "build" else profile.lint_packages
    return list(dict.fromkeys(packages))


def colcon_packages_args(profile: Optional[RobotProfile], kind: str) -> List[str]:
    packages = selected_packages(profile, kind)
    return ["--packages-select"] + packages if packages else []


def select_nodes(profile: RobotProfile, node_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    requested = node_names or profile.node_names
    by_name = {node["name"]: node for node in profile.nodes}
    missing = [name for name in requested if name not in by_name]
    if missing:
        raise ConfigError("unknown node(s) for profile '{}': {}".format(profile.name, ", ".join(missing)))
    return [by_name[name] for name in requested]


def resolve_service(profile: RobotProfile, service_name: str) -> Optional[Dict[str, Any]]:
    for service in profile.services:
        if service.get("name") == service_name:
            return service
    return None


def assert_topic_allowed(profile: RobotProfile, topic: str) -> None:
    if topic not in profile.monitor_topics:
        raise ConfigError("topic '{}' is not configured for profile '{}'".format(topic, profile.name))


def describe_profile_targets(profile: RobotProfile) -> Dict[str, Any]:
    return {
        "profile": profile.name,
        "robot_type": profile.robot_type,
        "target": profile.target,
        "build_packages": profile.build_packages,
        "lint_packages": profile.lint_packages,
        "nodes": [
            {
                "name": node["name"],
                "package": node["package"],
                "executable": node["executable"],
                "args": node.get("args", []),
            }
            for node in profile.nodes
        ],
        "services": [
            {
                "name": service["name"],
                "type": service.get("type", ""),
                "payload": service.get("payload", ""),
            }
            for service in profile.services
        ],
        "topics": profile.monitor_topics,
    }
