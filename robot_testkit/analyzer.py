from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


FAILURE_PATTERNS = ("ERROR", "FAILED", "Traceback", "Exception", "Timeout", "timed out")
WARNING_PATTERNS = ("WARN", "WARNING")


def analyze_logs(log_dir: Path) -> Dict[str, Any]:
    findings: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []
    if not log_dir.exists():
        return {"status": "unknown", "findings": [{"file": "", "line": "log directory does not exist"}], "warnings": []}

    for path in sorted(log_dir.glob("*.log")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if any(pattern in line for pattern in FAILURE_PATTERNS):
                findings.append({"file": str(path), "line": line[:500]})
            elif any(pattern in line for pattern in WARNING_PATTERNS):
                warnings.append({"file": str(path), "line": line[:500]})

    return {
        "status": "fail" if findings else "pass",
        "findings": findings[:50],
        "warnings": warnings[:50],
    }
