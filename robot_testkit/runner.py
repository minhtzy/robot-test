from __future__ import annotations

import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .errors import CommandError


SECRET_MARKERS = ("PASSWORD", "TOKEN", "SECRET", "KEY")


@dataclass(frozen=True)
class CommandResult:
    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    dry_run: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def summary(self) -> Dict[str, object]:
        return {
            "command": " ".join(shlex.quote(part) for part in self.command),
            "returncode": self.returncode,
            "duration_seconds": round(self.duration_seconds, 3),
            "dry_run": self.dry_run,
        }


class CommandRunner:
    def __init__(self, cwd: Path, dry_run: bool = False, log_dir: Optional[Path] = None) -> None:
        self.cwd = cwd
        self.dry_run = dry_run
        self.log_dir = log_dir
        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        command: List[str],
        *,
        timeout: Optional[int] = None,
        check: bool = True,
        env: Optional[Dict[str, str]] = None,
        log_name: Optional[str] = None,
    ) -> CommandResult:
        safe_env = self._clean_env(env)
        started = time.monotonic()
        if self.dry_run:
            result = CommandResult(command, 0, f"DRY RUN: {self._format(command)}\n", "", 0.0, True)
            self._write_log(log_name, result)
            return result

        completed = subprocess.run(
            command,
            cwd=self.cwd,
            env=safe_env,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        result = CommandResult(
            command=command,
            returncode=completed.returncode,
            stdout=self._redact(completed.stdout),
            stderr=self._redact(completed.stderr),
            duration_seconds=time.monotonic() - started,
        )
        self._write_log(log_name, result)
        if check and not result.ok:
            raise CommandError(f"command failed ({result.returncode}): {self._format(command)}")
        return result

    def _clean_env(self, env: Optional[Dict[str, str]]) -> Dict[str, str]:
        merged = os.environ.copy()
        if env:
            merged.update(env)
        return merged

    def _write_log(self, name: Optional[str], result: CommandResult) -> None:
        if not name or not self.log_dir:
            return
        path = self.log_dir / f"{name}.log"
        content = [
            f"$ {self._format(result.command)}",
            f"returncode={result.returncode} dry_run={result.dry_run} duration={result.duration_seconds:.3f}s",
            "",
            "[stdout]",
            result.stdout,
            "[stderr]",
            result.stderr,
        ]
        path.write_text("\n".join(content), encoding="utf-8")

    @staticmethod
    def _format(command: List[str]) -> str:
        return " ".join(shlex.quote(part) for part in command)

    @staticmethod
    def _redact(text: str) -> str:
        redacted = text
        for marker in SECRET_MARKERS:
            redacted = redacted.replace(marker.lower(), marker.lower())
        return redacted
