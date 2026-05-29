from pathlib import Path

from robot_testkit.config import load_config


def test_load_default_config_profiles() -> None:
    config = load_config("config/robot-testkit.yaml")

    assert config.profile("fairino_sim").robot_type == "fairino"
    assert config.profile("fairino_sim").launch["mode"] == "docker_run"
    assert config.profile("fairino_sim").launch["network"] == "fairino-net"
    assert config.profile("ur_sim").launch["profile"] == "ur-sim"
    assert config.profile("ur_sim").launch["network"] == "ur-net"
    assert config.workspace.root == Path.cwd()
