from robot_testkit.memory import MemoryStore


def test_memory_redacts_secret_keys(tmp_path) -> None:
    store = MemoryStore(tmp_path)
    store.append_run({"run_id": "1", "api_token": "secret-value"})

    text = (tmp_path / "runs.jsonl").read_text(encoding="utf-8")
    assert "secret-value" not in text
    assert "<redacted>" in text

