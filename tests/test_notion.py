import os
import pytest
from notion import NotionClient

def test_notion_client_init_env(monkeypatch):
    monkeypatch.setenv("NOTION_TOKEN", "x" * 40)
    monkeypatch.setenv("NOTION_DB_ID", "y" * 32)
    client = NotionClient()
    assert client.token == "x" * 40
    assert client.database_id == "y" * 32

def test_notion_client_init_invalid():
    os.environ.pop("NOTION_TOKEN", None)
    os.environ.pop("NOTION_DB_ID", None)
    with pytest.raises(ValueError):
        NotionClient(token="short", database_id="short") 