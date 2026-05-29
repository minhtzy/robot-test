---
name: robot-test
description: Use when building, linting, launching, controlling, monitoring, or analyzing ROS2 robot test workflows in VS Code with MCP, Docker simulation for Fairino/UR, FANUC Windows bridge, browser login, safety gates, local memory, and agent hooks.
---

# Robot Test

Use this skill for robot test work in this workspace.

## Workflow

1. Load `config/robot-testkit.yaml` and select a robot profile.
2. Resolve profile targets: build packages, lint packages, ROS2 nodes, services, and topics.
3. Run `colcon build` for the profile's selected packages.
4. Run `colcon test` for the profile's selected lint packages and configured lint options.
5. Only if build and lint pass, launch the target.
6. For Fairino/UR simulation, use Docker configuration from the profile.
7. For FANUC, call the Windows bridge service.
8. Login through the browser adapter order: VS Code browser tool, Playwright, system browser.
9. Start only configured ROS2 nodes with `ros2 run`.
10. Call only configured/allowlisted services. Use configured type/payload when command arguments are omitted. Require confirmation for physical actions.
11. Monitor only configured topics, collect logs, analyze, then update local memory from evidence.

## Commands

- Build: `python3 -m robot_testkit.cli build --profile fairino_sim`
- Lint: `python3 -m robot_testkit.cli lint --profile fairino_sim`
- Show targets: `python3 -m robot_testkit.cli targets --profile fairino_sim`
- Dry-run scenario: `python3 -m robot_testkit.cli --dry-run run-scenario --profile fairino_sim`
- Confirmed service call: `python3 -m robot_testkit.cli call-service --profile PROFILE --service SERVICE --confirm`

## References

- Read `references/safety.md` before real robot actions.
- Read `references/configuration.md` before changing robot profiles.
