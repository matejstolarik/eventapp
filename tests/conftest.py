import pytest


@pytest.fixture(autouse=True)
def _isolated_research_backup(tmp_path, monkeypatch):
    """Task 074: tests never read or write the repo research backup."""
    from pipeline import research_store
    monkeypatch.setattr(research_store, "BACKUP_DIR", tmp_path / "research_backup")
