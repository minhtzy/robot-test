from __future__ import annotations

import os
import json
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

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

    def run_with_sources(
        self,
        command: List[str],
        sources: Sequence[Path],
        *,
        timeout: Optional[int] = None,
        check: bool = True,
        env: Optional[Dict[str, str]] = None,
        log_name: Optional[str] = None,
    ) -> CommandResult:
        return self.run(
            self.wrap_with_sources(command, sources),
            timeout=timeout,
            check=check,
            env=env,
            log_name=log_name,
        )

    def start_background(
        self,
        command: List[str],
        *,
        env: Optional[Dict[str, str]] = None,
        log_name: Optional[str] = None,
        metadata_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        safe_env = self._clean_env(env)
        log_path = self._log_path(log_name)
        formatted = self._format(command)
        if self.dry_run:
            result = CommandResult(command, 0, f"DRY RUN BACKGROUND: {formatted}\n", "", 0.0, True)
            self._write_log(log_name, result)
            return {
                "command": formatted,
                "pid": None,
                "log_path": str(log_path) if log_path else None,
                "metadata_path": str(metadata_path) if metadata_path else None,
                "dry_run": True,
                "started": False,
                "background": True,
            }

        if not log_path:
            raise CommandError("background commands require log_name")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handle = log_path.open("a", encoding="utf-8")
        handle.write(f"$ {formatted}\n")
        handle.flush()
        process = subprocess.Popen(
            command,
            cwd=str(self.cwd),
            env=safe_env,
            stdout=handle,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
            text=True,
        )
        handle.close()
        payload = {
            "command": formatted,
            "pid": process.pid,
            "log_path": str(log_path),
            "metadata_path": str(metadata_path) if metadata_path else None,
            "dry_run": False,
            "started": True,
            "background": True,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        if metadata_path:
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            metadata_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return payload

    def start_background_with_sources(
        self,
        command: List[str],
        sources: Sequence[Path],
        *,
        env: Optional[Dict[str, str]] = None,
        log_name: Optional[str] = None,
        metadata_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        return self.start_background(
            self.wrap_with_sources(command, sources),
            env=env,
            log_name=log_name,
            metadata_path=metadata_path,
        )

    @staticmethod
    def wrap_with_sources(command: List[str], sources: Sequence[Path]) -> List[str]:
        source_parts = [f"source {shlex.quote(str(path))}" for path in sources]
        command_part = " ".join(shlex.quote(part) for part in command)
        script = " && ".join(source_parts + [command_part])
        return ["bash", "-lc", script]

    def _clean_env(self, env: Optional[Dict[str, str]]) -> Dict[str, str]:
        merged = os.environ.copy()
        if env:
            merged.update(env)
        return merged

    def _write_log(self, name: Optional[str], result: CommandResult) -> None:
        path = self._log_path(name)
        if not path:
            return
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

    def _log_path(self, name: Optional[str]) -> Optional[Path]:
        if not name or not self.log_dir:
            return None
        return self.log_dir / f"{name}.log"

    @staticmethod
    def _format(command: List[str]) -> str:
        return " ".join(shlex.quote(part) for part in command)

    @staticmethod
    def _redact(text: str) -> str:
        redacted = text
        for marker in SECRET_MARKERS:
            redacted = redacted.replace(marker.lower(), marker.lower())
        return redacted
