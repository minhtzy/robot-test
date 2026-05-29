from __future__ import annotations

import importlib.util
import os
import sys
import webbrowser
from dataclasses import dataclass

from .config import BrowserConfig
from .runner import CommandResult, CommandRunner


@dataclass(frozen=True)
class BrowserLoginResult:
    adapter: str
    opened: bool
    message: str


def select_browser_adapter(config: BrowserConfig) -> str:
    for adapter in config.adapter_preference:
        if adapter == "vscode" and os.environ.get(config.vscode_tool_command_env):
            return "vscode"
        if adapter == "playwright" and importlib.util.find_spec("playwright"):
            return "playwright"
        if adapter == "system":
            return "system"
    return "system"


def browser_login(config: BrowserConfig, runner: CommandRunner) -> BrowserLoginResult:
    username = os.environ.get(config.username_env, "")
    password = os.environ.get(config.password_env, "")
    adapter = select_browser_adapter(config)

    if adapter == "vscode":
        command = os.environ[config.vscode_tool_command_env].split()
        command.append(config.login_url)
        runner.run(command, check=False, log_name="browser_vscode")
        return BrowserLoginResult("vscode", True, "opened login URL with VS Code browser tool command")

    if adapter == "playwright":
        runner.run([sys.executable, "-m", "robot_testkit.playwright_login", config.login_url], check=False, log_name="browser_playwright")
        return BrowserLoginResult("playwright", True, "opened login URL with Playwright")

    if not runner.dry_run:
        webbrowser.open(config.login_url)
    _ = (username, password)
    return BrowserLoginResult("system", True, "opened login URL with system browser")
