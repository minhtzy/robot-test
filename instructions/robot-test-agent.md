# Robot Test Agent Instructions

You are operating a robot test workflow from VS Code. Always run build and lint before launching a simulation or robot target.

Safety rules:

- Prefer simulation profiles first: `fairino_sim`, `ur_sim`, then `fanuc_windows`.
- Resolve and review the selected profile targets before execution: build packages, lint packages, nodes, services, and topics.
- Do not invent ROS2 packages, node executables, service names, service types, payloads, or topics; use `config/robot-testkit.yaml` or the MCP `targets` tool.
- For real robot profiles, require explicit operator confirmation before session init, I/O, arm move, arm stop, or any physical service.
- Reject ROS2 services that are not allowlisted in `config/robot-testkit.yaml`.
- Reject topic monitoring when a profile is supplied and the topic is not in that profile's `monitor_topics`.
- Never print or persist credentials, tokens, passwords, API keys, or browser session secrets.
- Treat FANUC as a Windows bridge target; call the bridge service instead of invoking Windows API directly from this workspace.

Browser login order:

1. Use the VS Code browser tool command from `VSCODE_BROWSER_TOOL_COMMAND` when available.
2. Fall back to Playwright when installed.
3. Fall back to system browser automation.

Learning rules:

- Update `.robot-test-memory/` only from concrete command output, logs, reports, or operator-confirmed results.
- Store evidence-oriented lessons: run id, robot type, command/service/topic, failure signature, root cause if known, lesson, confidence.
- Use previous lessons as suggestions, not as permission to bypass safety gates.
