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

Long-running MCP steps run async by default. Use `job_status`, `job_logs`, and `job_cancel` with the returned `runId`. Pass `asyncRun: false` only for an explicit synchronous override.

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

## Async Monitoring

Use the default async mode when a command may take more than a few seconds:

1. Call the operation normally.
2. Save and show the returned `runId`.
3. Poll `job_status` until status changes from `running`.
4. Call `job_logs` whenever progress is needed.
5. Call `job_cancel` only when the user asks to stop or safety requires stopping.

## Safety

- Use simulation profiles before real robot profiles.
- Do not run unconfigured packages, nodes, services, or topics.
- Require confirmation for session init, I/O, arm move, arm stop, or any real robot action.
- Do not store credentials, tokens, browser sessions, or API keys in logs/reports/memory.
