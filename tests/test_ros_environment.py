from pathlib import Path

from robot_testkit.config import load_config
from robot_testkit.orchestrator import RobotOrchestrator
from robot_testkit.runner import CommandRunner


def test_wrap_with_sources_uses_bash_source_chain() -> None:
    command = CommandRunner.wrap_with_sources(
        ["ros2", "topic", "echo", "/arm/state"],
        [Path("/opt/ros/humble/setup.bash"), Path("install/setup.bash")],
    )

    assert command == [
        "bash",
        "-lc",
        "source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 topic echo /arm/state",
    ]


def test_colcon_and_runtime_sources_are_separate() -> None:
    orchestrator = RobotOrchestrator(load_config("config/robot-testkit.yaml"), dry_run=True)

    assert [str(path) for path in orchestrator._colcon_sources()] == ["/opt/ros/humble/install.bash"]
    runtime_sources = [str(path) for path in orchestrator._runtime_sources()]
    assert runtime_sources[0] == "/opt/ros/humble/setup.bash"
    assert runtime_sources[1].endswith("/install/setup.bash")
