# Configuration

Robot profiles live in `config/robot-testkit.yaml`.

- Fairino simulation uses `launch.mode: docker_run` with `network: fairino-net`, matching `docker run -d -P --name fairino-container --privileged -u root --net fairino-net fairino_simmachine`.
- UR simulation uses `launch.mode: docker_compose` with `docker/ur/docker-compose.yaml` and `network: ur-net`.
- FANUC uses `launch.mode: fanuc_bridge`.
- Real robot profiles use `target: real` and must include a narrow `allowlist_services` list.
- Browser credentials come from env vars configured by `browser.username_env` and `browser.password_env`.
- `build_packages` define the ROS2 packages selected with `colcon build --packages-up-to` by default, so dependencies are built when needed.
- `lint_packages` define the ROS2 packages selected with `colcon test --packages-select` by default.
- `nodes` define exact `ros2 run` targets by name, package, executable, and args.
- `services` define exact service name, type, and default payload.
- `monitor_topics` defines the topics that may be watched for that profile.
