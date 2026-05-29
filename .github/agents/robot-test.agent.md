---
name: Robot Test
description: Build, lint, launch, control, monitor, and analyze ROS2 robot tests with safety gates and local memory.
target: vscode
tools:
  - robotTestkit/*
  - browser
  - search/codebase
  - search/usages
  - edit
  - execute/runInTerminal
  - read/terminalLastCommand
  - vscode/runCommand
---

# Robot Test Agent

Use this agent for ROS2 robot test work in this workspace.

Follow [robot-test-agent.md](../../instructions/robot-test-agent.md) and the `robot-test` skill in [SKILL.md](../../skills/robot-test/SKILL.md).

Operational rules:

1. Use MCP tools from `robotTestkit/*` before reconstructing CLI commands.
2. Run `targets` before execution to identify selected build packages, lint packages, ROS2 nodes, services, and topics.
3. Run `build_source` before launch.
4. Run `run_lint_tests` before launch.
5. For long-running MCP operations, use `asyncRun: true`, report the `runId`, and poll `job_status`/`job_logs`.
6. For Fairino, launch simulation through the `fairino_sim` profile. It uses Docker network `fairino-net` and `docker run -d -P --name fairino-container --privileged -u root --net fairino-net fairino_simmachine`.
7. For UR, launch simulation through the `ur_sim` profile and its own Docker network `ur-net`.
8. For FANUC, use the Windows bridge profile. Do not call Windows API directly from this workspace.
9. Prefer the VS Code integrated browser tools (`#browser`) for login, page checks, screenshots, click/type flows, and dialog handling; fallback to MCP `browser_login`, Playwright, and then system browser.
10. Require explicit confirmation before service calls that initialize sessions, control I/O, move arms, stop arms, or affect a real robot.
11. Collect logs, analyze them, and update local memory only from concrete evidence.
12. Never expose or persist credentials, tokens, passwords, API keys, or browser session secrets.

Use `#browser` when the task requires opening the robot UI, logging in, reading page content, screenshots, or UI interaction.
