---
name: robot-test
description: Use when building, linting, launching, controlling, monitoring, or analyzing ROS2 robot test workflows in VS Code with MCP, Docker simulation for Fairino/UR, FANUC Windows bridge, browser login, safety gates, local memory, and agent hooks.
---

# Robot Test

Use this skill for robot test work in this workspace.

## Workflow

1. Load `config/robot-testkit.yaml` and select a robot profile.
2. Run `colcon build`.
3. Run `colcon test` with the configured lint options.
4. Only if build and lint pass, launch the target.
5. For Fairino/UR simulation, use Docker Compose profiles.
6. For FANUC, call the Windows bridge service.
7. Login through the browser adapter order: VS Code browser tool, Playwright, system browser.
8. Start configured ROS2 nodes with `ros2 run`.
9. Call only allowlisted services. Require confirmation for physical actions.
10. Monitor configured topics, collect logs, analyze, then update local memory from evidence.

## Commands

- Build: `python -m robot_testkit.cli build`
- Lint: `python -m robot_testkit.cli lint`
- Dry-run scenario: `python -m robot_testkit.cli --dry-run run-scenario --profile fairino_sim`
- Confirmed service call: `python -m robot_testkit.cli call-service --profile PROFILE --service SERVICE --type TYPE --payload PAYLOAD --confirm`

## References

- Read `references/safety.md` before real robot actions.
- Read `references/configuration.md` before changing robot profiles.

