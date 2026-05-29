class RobotTestkitError(Exception):
    """Base exception for robot testkit failures."""


class ConfigError(RobotTestkitError):
    """Raised when configuration is invalid."""


class CommandError(RobotTestkitError):
    """Raised when a command fails."""


class SafetyError(RobotTestkitError):
    """Raised when a robot action is blocked by the safety gate."""

