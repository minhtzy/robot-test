# Robot Test Workflow

This workflow is the standard sequence for testing a robot profile from VS Code, MCP, or the CLI.

## 1. Select Profile And Targets

Choose one profile from `config/robot-testkit.yaml`.

Recommended order:

1. `fairino_sim`
2. `ur_sim`
3. `fanuc_windows`
4. real robot profiles only after simulation passes

Review the resolved targets before running commands:

```bash
python3 -m robot_testkit.cli targets --profile fairino_sim
```

Confirm these fields are correct:

- `build_packages`: packages built with `colcon build --packages-up-to`
- `lint_packages`: packages tested with `colcon test --packages-select`
- `nodes`: exact `ros2 run` package/executable/args targets
- `services`: allowed service names, types, and default payloads
- `topics`: allowed topics for monitoring

Do not run packages, nodes, services, or topics that are not in the selected profile.

## 2. Build

Build the selected profile packages and dependencies:

```bash
python3 -m robot_testkit.cli build --profile fairino_sim
```

The command is executed through:

```bash
source /opt/ros/{ros_distro}/install.bash
colcon build --packages-up-to ...
```

Stop the workflow if build fails. Collect logs before retrying.

## 3. Lint/Test

Run lint/test for the selected profile packages:

```bash
python3 -m robot_testkit.cli lint --profile fairino_sim
```

The command is executed through:

```bash
source /opt/ros/{ros_distro}/install.bash
colcon test --packages-select ...
```

Stop the workflow if lint/test fails. Do not launch simulation or robot until build and lint pass.

## 4. Launch Target

Launch only after build and lint pass:

```bash
python3 -m robot_testkit.cli launch --profile fairino_sim
```

Profile behavior:

- Fairino simulation uses `docker run` with `fairino-net`.
- UR simulation uses `docker/ur/docker-compose.yaml` with `ur-net`.
- FANUC uses the configured Windows bridge service.
- Real robot profiles attach to an existing robot and require stricter confirmation gates.

## 5. Browser Login

Open the robot UI:

```bash
python3 -m robot_testkit.cli browser-login --profile fairino_sim
```

Adapter order:

1. VS Code browser tool command from `VSCODE_BROWSER_TOOL_COMMAND`
2. Playwright
3. System browser

Credentials must come from env vars or VS Code secret/input flow. Do not write credentials to logs, reports, or memory.

## 6. Start ROS2 Nodes

Start all configured nodes:

```bash
python3 -m robot_testkit.cli start-nodes --profile fairino_sim
```

Start one configured node:

```bash
python3 -m robot_testkit.cli start-nodes --profile fairino_sim --node client
```

Each node runs through:

```bash
source /opt/ros/{ros_distro}/setup.bash
source install/setup.bash
ros2 run PACKAGE EXECUTABLE ...
```

Unknown node names are rejected.

## 7. Call Services

Call only configured and allowlisted services.

Example using configured type and payload:

```bash
python3 -m robot_testkit.cli call-service --profile fairino_sim --service /arm_control/move --confirm
```

Example with explicit type and payload:

```bash
python3 -m robot_testkit.cli call-service \
  --profile fairino_sim \
  --service /robot_control/set_io \
  --type example_interfaces/srv/SetBool \
  --payload '{data: true}' \
  --confirm
```

Service calls run through:

```bash
source /opt/ros/{ros_distro}/setup.bash
source install/setup.bash
ros2 service call ...
```

Confirmation is required for session initialization, I/O control, arm movement, arm stop, and all real robot actions.

## 8. Monitor Topics

Monitor only configured topics:

```bash
python3 -m robot_testkit.cli monitor-topic --profile fairino_sim --topic /arm/state --seconds 10
```

Topic commands run through:

```bash
source /opt/ros/{ros_distro}/setup.bash
source install/setup.bash
ros2 topic echo ...
```

Unknown topics are rejected when a profile is supplied.

## 9. Collect Logs And Analyze

Collect and analyze latest logs:

```bash
python3 -m robot_testkit.cli collect-logs
python3 -m robot_testkit.cli analyze
```

Reports are written under `reports/`. Logs are written under `logs/`.

## 10. Update Memory

Update memory only after there is concrete evidence from command output, logs, reports, or operator-confirmed results:

```bash
python3 -m robot_testkit.cli update-memory --profile fairino_sim
```

Memory is local to `.robot-test-memory/`. Do not store secrets.

## End-To-End Dry Run

Before any real execution, run:

```bash
python3 -m robot_testkit.cli --dry-run run-scenario --profile fairino_sim --monitor-seconds 1
```

Review the generated commands for:

- correct profile
- correct `source ...` chain
- `colcon build --packages-up-to`
- `colcon test --packages-select`
- expected `ros2 run`, `ros2 service`, and `ros2 topic` targets

