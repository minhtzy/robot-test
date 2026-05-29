from robot_testkit.docker import build_docker_run_command


def test_build_fairino_docker_run_command() -> None:
    command = build_docker_run_command(
        {
            "image": "fairino_simmachine",
            "name": "fairino-container",
            "network": "fairino-net",
            "detach": True,
            "publish_all_ports": True,
            "privileged": True,
            "user": "root",
        }
    )

    assert command == [
        "docker",
        "run",
        "-d",
        "-P",
        "--name",
        "fairino-container",
        "--privileged",
        "-u",
        "root",
        "--net",
        "fairino-net",
        "fairino_simmachine",
    ]
