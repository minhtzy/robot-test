from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List


class MemoryStore:
    def __init__(self, memory_dir: Path) -> None:
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.lessons_path = self.memory_dir / "lessons.jsonl"
        self.runs_path = self.memory_dir / "runs.jsonl"

    def append_run(self, run: Dict[str, Any]) -> None:
        self._append(self.runs_path, run)

    def append_lesson(self, lesson: Dict[str, Any]) -> None:
        required = {"run_id", "robot_type", "failure_signature", "lesson", "confidence"}
        missing = required - set(lesson)
        if missing:
            raise ValueError(f"lesson missing required fields: {', '.join(sorted(missing))}")
        self._append(self.lessons_path, lesson)

    def read_lessons(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.lessons_path.exists():
            return []
        lines = self.lessons_path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines[-limit:] if line.strip()]

    @staticmethod
    def _redact(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: ("<redacted>" if any(token in key.upper() for token in ("PASSWORD", "TOKEN", "SECRET", "KEY")) else MemoryStore._redact(item))
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [MemoryStore._redact(item) for item in value]
        return value

    def _append(self, path: Path, payload: Dict[str, Any]) -> None:
        record = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **self._redact(payload)}
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
