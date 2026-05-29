from robot_testkit.browser import select_browser_adapter
from robot_testkit.config import BrowserConfig


def test_browser_prefers_vscode_when_command_env_exists(monkeypatch) -> None:
    monkeypatch.setenv("VSCODE_BROWSER_TOOL_COMMAND", "code --command simpleBrowser.show")

    assert select_browser_adapter(BrowserConfig(login_url="http://robot")) == "vscode"


def test_browser_falls_back_to_system(monkeypatch) -> None:
    monkeypatch.delenv("VSCODE_BROWSER_TOOL_COMMAND", raising=False)

    config = BrowserConfig(login_url="http://robot", adapter_preference=["system"])
    assert select_browser_adapter(config) == "system"

