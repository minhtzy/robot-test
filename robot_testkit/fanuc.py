from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any
from uuid import uuid4

from .config import FanucBridgeConfig
from .errors import CommandError


def call_fanuc_bridge(
    config: FanucBridgeConfig,
    action: str,
    payload: dict[str, Any] | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    body = {
        "request_id": str(uuid4()),
        "action": action,
        "payload": payload or {},
    }
    if dry_run:
        return {"dry_run": True, "request": body, "endpoint": config.endpoint}

    token = os.environ.get(config.token_env, "")
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        f"{config.endpoint.rstrip('/')}/api/robot/action",
        data=data,
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise CommandError(f"FANUC bridge call failed: {exc}") from exc

