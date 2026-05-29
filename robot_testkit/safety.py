from __future__ import annotations

from .config import RobotProfile
from .errors import SafetyError


PHYSICAL_KEYWORDS = ("init_session", "set_io", "move", "stop", "arm", "io")


def service_requires_confirmation(service: str, profile: RobotProfile) -> bool:
    if profile.is_real:
        return True
    lowered = service.lower()
    return any(keyword in lowered for keyword in PHYSICAL_KEYWORDS)


def assert_service_allowed(service: str, profile: RobotProfile) -> None:
    if service not in profile.allowlist_services:
        raise SafetyError(f"service '{service}' is not allowlisted for profile '{profile.name}'")


def assert_confirmation(service: str, profile: RobotProfile, confirmed: bool) -> None:
    if service_requires_confirmation(service, profile) and not confirmed:
        raise SafetyError(f"service '{service}' requires explicit confirmation for profile '{profile.name}'")

