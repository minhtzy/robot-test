# Workflow Tool Mapping

Use this mapping when operating the robot test workflow from VS Code.

| Step | Preferred Tool | Fallback |
| --- | --- | --- |
| Resolve targets | MCP `targets` | `python3 -m robot_testkit.cli targets --profile PROFILE` |
| Build | MCP `build_source` | `python3 -m robot_testkit.cli build --profile PROFILE` |
| Lint/test | MCP `run_lint_tests` | `python3 -m robot_testkit.cli lint --profile PROFILE` |
| Launch | MCP `launch_target` | `python3 -m robot_testkit.cli launch --profile PROFILE` |
| Browser login/UI | VS Code `#browser`, then MCP `browser_login` | `python3 -m robot_testkit.cli browser-login --profile PROFILE` |
| Start nodes | MCP `start_nodes` | `python3 -m robot_testkit.cli start-nodes --profile PROFILE [--node NAME]` |
| Call service | MCP `call_service` | `python3 -m robot_testkit.cli call-service --profile PROFILE --service SERVICE --confirm` |
| Monitor topic | MCP `monitor_topic` | `python3 -m robot_testkit.cli monitor-topic --profile PROFILE --topic TOPIC --seconds N` |
| Collect logs | MCP `collect_logs` | `python3 -m robot_testkit.cli collect-logs` |
| Analyze | MCP `analyze_run` | `python3 -m robot_testkit.cli analyze` |
| Update memory | MCP `update_memory` | `python3 -m robot_testkit.cli update-memory --profile PROFILE` |

MCP calls are synchronous. For long-running steps where live output matters and polling is not wanted, use VS Code tasks or terminal commands.

## Required Order

1. Resolve targets.
2. Build.
3. Lint/test.
4. Launch only if build and lint pass.
5. Browser login/UI checks.
6. Start configured nodes.
7. Call configured services with confirmation when physical behavior is involved.
8. Monitor configured topics.
9. Collect logs and analyze.
10. Update memory from evidence.

## Live Output Without Polling

Use VS Code tasks or terminal commands for live output:

- `Robot: Build`
- `Robot: Lint Test`
- `Robot: Run Scenario`
- `python3 -m robot_testkit.cli build --profile PROFILE`
- `python3 -m robot_testkit.cli lint --profile PROFILE`

`start_nodes` is special: it starts configured `ros2 run` commands as background processes and returns PID/log metadata immediately.

## Safety

- Use simulation profiles before real robot profiles.
- Do not run unconfigured packages, nodes, services, or topics.
- Require confirmation for session init, I/O, arm move, arm stop, or any real robot action.
- Do not store credentials, tokens, browser sessions, or API keys in logs/reports/memory.
