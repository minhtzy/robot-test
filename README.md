# Robot Testkit for VS Code

This workspace contains a ROS2 robot test toolkit with:

- Python orchestration for `colcon`, Docker simulation, ROS2 nodes/services/topics, browser login, FANUC bridge calls, logs, analysis, and local memory.
- A TypeScript MCP server exposing robot test tools, resources, and prompts over local `stdio` and remote Streamable HTTP with legacy SSE compatibility.
- VS Code tasks, Codex skill/instructions, and agent lifecycle hooks.

Python runtime baseline: Python 3.8 or newer.

ROS2 environment sourcing:

- `colcon build` and `colcon test` run after `source /opt/ros/{ros_distro}/install.bash`.
- `ros2 run`, `ros2 service`, and `ros2 topic` run after `source /opt/ros/{ros_distro}/setup.bash && source install/setup.bash`.
- Configure `ros_distro`, `colcon_ros_setup`, `runtime_ros_setup`, and `workspace_setup` in `config/robot-testkit.yaml`.

Robot targets are resolved from each profile before execution:

- `build_packages` become `colcon build --packages-up-to ...` by default, so dependencies are built when needed.
- `lint_packages` become `colcon test --packages-select ...` by default.
- `nodes` define the exact `ros2 run PACKAGE EXECUTABLE` calls.
- `services` define allowed service names plus default type/payload.
- `monitor_topics` defines topics allowed for `ros2 topic echo`.

Full workflow: [docs/test-workflow.md](docs/test-workflow.md).

MCP tools are synchronous request/response calls. For long-running commands where live output matters and polling is not wanted, use VS Code tasks or terminal commands.

Start with dry-run commands until robot profiles are configured:

```bash
python3 -m robot_testkit.cli run-scenario --profile fairino_sim --dry-run
```

Real robot actions require an explicit `--confirm` flag and must be allowlisted in `config/robot-testkit.yaml`.

Fairino simulation uses a dedicated Docker network and `docker run` shape matching the lab command:

```bash
docker network create fairino-net
docker run -d -P --name fairino-container --privileged -u root --net fairino-net fairino_simmachine
```

UR simulation is split into `docker/ur/docker-compose.yaml` with its own `ur-net` network.
