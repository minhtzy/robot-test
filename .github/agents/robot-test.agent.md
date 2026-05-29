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

1. Run `robot.build_source` before launch.
2. Run `robot.run_lint_tests` before launch.
3. Use the `targets` tool or `config/robot-testkit.yaml` to identify the selected build packages, lint packages, ROS2 nodes, services, and topics before execution.
4. For Fairino, launch simulation through the `fairino_sim` profile. It uses Docker network `fairino-net` and `docker run -d -P --name fairino-container --privileged -u root --net fairino-net fairino_simmachine`.
5. For UR, launch simulation through the `ur_sim` profile and its own Docker network `ur-net`.
6. For FANUC, use the Windows bridge profile. Do not call Windows API directly from this workspace.
7. Prefer the VS Code integrated browser tools (`#browser`) for login, page checks, screenshots, click/type flows, and dialog handling; fallback to `robot.browser_login`, Playwright, and then system browser.
8. Require explicit confirmation before service calls that initialize sessions, control I/O, move arms, stop arms, or affect a real robot.
9. Collect logs, analyze them, and update local memory only from concrete evidence.
10. Never expose or persist credentials, tokens, passwords, API keys, or browser session secrets.

Use MCP tools from `robotTestkit/*` whenever possible instead of manually reconstructing commands. Use `#browser` when the task requires opening the robot UI, logging in, reading page content, screenshots, or UI interaction.
