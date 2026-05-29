from __future__ import annotations

import json
import os
import time
from pathlib import Path


def write_hook_event(name: str) -> None:
    payload = os.environ.get("ROBOT_TESTKIT_HOOK_PAYLOAD", "{}")
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        parsed = {"raw": payload}
    path = Path("logs") / "hooks.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"hook": name, "timestamp": time.time(), "payload": parsed}, sort_keys=True) + "\n")

