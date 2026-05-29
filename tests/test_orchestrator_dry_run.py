from robot_testkit.config import load_config
from robot_testkit.orchestrator import RobotOrchestrator


def test_dry_run_build_and_lint_do_not_require_colcon() -> None:
    orchestrator = RobotOrchestrator(load_config("config/robot-testkit.yaml"), dry_run=True)

    assert orchestrator.build_source().ok
    assert orchestrator.run_lint_tests().ok

