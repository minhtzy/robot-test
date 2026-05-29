# Robot Testkit for VS Code

This workspace contains a ROS2 robot test toolkit with:

- Python orchestration for `colcon`, Docker simulation, ROS2 nodes/services/topics, browser login, FANUC bridge calls, logs, analysis, and local memory.
- A TypeScript MCP server exposing robot test tools, resources, and prompts over local `stdio` and remote Streamable HTTP with legacy SSE compatibility.
- VS Code tasks, Codex skill/instructions, and agent lifecycle hooks.

Python runtime baseline: Python 3.8 or newer.

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
