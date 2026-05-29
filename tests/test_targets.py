import pytest

from robot_testkit.config import load_config
from robot_testkit.errors import ConfigError, SafetyError
from robot_testkit.orchestrator import RobotOrchestrator
from robot_testkit.targets import select_nodes


def test_profile_describes_build_lint_nodes_services_and_topics() -> None:
    config = load_config("config/robot-testkit.yaml")
    targets = RobotOrchestrator(config, dry_run=True).describe_targets(config.profile("fairino_sim"))

    assert targets["build_packages"] == ["project_client", "project_robot_control", "project_arm_control"]
    assert targets["build_package_selector"] == "--packages-up-to"
    assert targets["lint_package_selector"] == "--packages-select"
    assert [node["name"] for node in targets["nodes"]] == ["client", "robot_control", "arm_control"]
    assert "/arm_control/move" in [service["name"] for service in targets["services"]]
    assert targets["topics"] == ["/arm/state"]


def test_build_and_lint_use_profile_packages_in_dry_run() -> None:
    config = load_config("config/robot-testkit.yaml")
    profile = config.profile("fairino_sim")
    orchestrator = RobotOrchestrator(config, dry_run=True)

    build_command = orchestrator.build_source(profile).summary()["command"]
    lint_command = orchestrator.run_lint_tests(profile).summary()["command"]

    assert "--packages-up-to project_client project_robot_control project_arm_control" in build_command
    assert "--packages-select project_client project_robot_control project_arm_control" in lint_command


def test_start_nodes_requires_known_node_name() -> None:
    config = load_config("config/robot-testkit.yaml")
    profile = config.profile("fairino_sim")

    assert [node["name"] for node in select_nodes(profile, ["client"])] == ["client"]
    with pytest.raises(ConfigError):
        select_nodes(profile, ["missing_node"])

    result = RobotOrchestrator(config, dry_run=True).start_nodes(profile, ["client"])[0]
    assert result["background"] is True
    assert result["started"] is False
    assert result["pid"] is None
    assert "ros2 run project_client client_node" in result["command"]


def test_monitor_topic_requires_configured_topic_when_profile_is_supplied() -> None:
    config = load_config("config/robot-testkit.yaml")
    orchestrator = RobotOrchestrator(config, dry_run=True)

    result = orchestrator.monitor_topic("/arm/state", profile=config.profile("fairino_sim"), duration_seconds=1)
    assert result.ok
    with pytest.raises(ConfigError):
        orchestrator.monitor_topic("/unknown/topic", profile=config.profile("fairino_sim"), duration_seconds=1)


def test_call_service_can_resolve_type_and_payload_from_config() -> None:
    config = load_config("config/robot-testkit.yaml")
    orchestrator = RobotOrchestrator(config, dry_run=True)
    profile = config.profile("fairino_sim")

    result = orchestrator.call_service(profile, "/arm_control/move", confirmed=True)

    assert "ros2 service call /arm_control/move example_interfaces/srv/Trigger" in result.summary()["command"]
    with pytest.raises(SafetyError):
        orchestrator.call_service(profile, "/not/configured", confirmed=True)
