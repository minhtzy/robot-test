---
name: robot-test
description: Use when executing the robot test workflow in VS Code with the robotTestkit MCP tools, VS Code browser tools, Docker simulation for Fairino/UR, FANUC Windows bridge, ROS2 build/lint/run/service/topic commands, safety gates, local memory, and log analysis.
---

# Robot Test

Use this skill for robot test work in this workspace. Prefer MCP tools from the `robotTestkit` server and VS Code `#browser` tools. Use CLI commands only as fallback when MCP tools are unavailable.

## Tool Priority

1. MCP tools from `robotTestkit/*`
2. VS Code `#browser` for robot UI login, UI checks, screenshots, click/type, and dialog handling
3. VS Code terminal/tasks for fallback CLI execution

Do not invent package, node, service, or topic targets. Resolve them from `targets` or `config/robot-testkit.yaml`.

## Long-Running Tools

MCP tools are synchronous request/response calls. For long-running build, lint/test, launch, or scenario work where the user needs live progress without polling, use VS Code tasks or terminal commands instead of MCP.

## MCP Workflow

1. Select a profile, normally `fairino_sim`, `ur_sim`, then `fanuc_windows`; use real robot profiles only after simulation passes.
2. Call `targets` for the selected profile and review build packages, lint packages, nodes, services, and topics.
3. Call `build_source` with the profile. Build uses `colcon build --packages-up-to` so dependencies are built when needed.
4. Call `run_lint_tests` with the profile. Lint/test uses `colcon test --packages-select`.
5. Only if build and lint pass, launch the target.
6. Call `launch_target` for simulation/bridge/attach.
7. Use VS Code `#browser` for robot UI login and verification when available; otherwise call `browser_login`.
8. Call `start_nodes` for all configured nodes or a named subset.
9. Call `call_service` only for configured/allowlisted services. Omit type/payload when the config provides them. Require confirmation for physical actions.
10. Call `monitor_topic` only for configured topics.
11. Call `collect_logs`, `analyze_run`, then `update_memory` only from concrete evidence.

## Fallback CLI

- Targets: `python3 -m robot_testkit.cli targets --profile fairino_sim`
- Build: `python3 -m robot_testkit.cli build --profile fairino_sim`
- Lint: `python3 -m robot_testkit.cli lint --profile fairino_sim`
- Dry-run scenario: `python3 -m robot_testkit.cli --dry-run run-scenario --profile fairino_sim`
- Confirmed service: `python3 -m robot_testkit.cli call-service --profile PROFILE --service SERVICE --confirm`

## References

- Read `references/workflow.md` for the MCP/VS Code tool mapping.
- Read `references/safety.md` before real robot actions.
- Read `references/configuration.md` before changing robot profiles.
