import pytest

from robot_testkit.config import load_config
from robot_testkit.errors import SafetyError
from robot_testkit.safety import assert_confirmation, assert_service_allowed


def test_rejects_non_allowlisted_service() -> None:
    profile = load_config("config/robot-testkit.yaml").profile("fairino_sim")

    with pytest.raises(SafetyError):
        assert_service_allowed("/unsafe/service", profile)


def test_requires_confirmation_for_arm_service() -> None:
    profile = load_config("config/robot-testkit.yaml").profile("fairino_sim")

    with pytest.raises(SafetyError):
        assert_confirmation("/arm_control/move", profile, confirmed=False)

    assert_confirmation("/arm_control/move", profile, confirmed=True)

