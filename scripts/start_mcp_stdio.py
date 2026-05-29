#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    mcp_dir = repo / "mcp"
    server = mcp_dir / "dist" / "src" / "server.js"

    if should_build(mcp_dir, server):
        subprocess.run(["npm", "install"], cwd=mcp_dir, check=True, stdout=sys.stderr, stderr=sys.stderr)
        subprocess.run(["npm", "run", "build"], cwd=mcp_dir, check=True, stdout=sys.stderr, stderr=sys.stderr)

    os.chdir(repo)
    os.execvp("node", ["node", str(server), "--transport", "stdio"])
    return 1


def should_build(mcp_dir: Path, server: Path) -> bool:
    if not server.exists():
        return True
    server_mtime = server.stat().st_mtime
    for source in (mcp_dir / "src").glob("**/*.ts"):
        if source.stat().st_mtime > server_mtime:
            return True
    for source in (mcp_dir / "tests").glob("**/*.ts"):
        if source.stat().st_mtime > server_mtime:
            return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
