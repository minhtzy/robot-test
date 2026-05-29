# Safety

- Do not call non-allowlisted ROS2 services.
- Require confirmation for real robot actions and service names involving session, I/O, arm movement, or stop.
- Do not store credentials in reports, logs, or memory.
- FANUC actions must go through the configured Windows bridge service.

