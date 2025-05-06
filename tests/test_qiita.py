import os
import pytest
from qiita import QiitaClient

def test_qiita_client_init_env(monkeypatch):
    monkeypatch.setenv("QIITA_TOKEN", "x" * 40)
    client = QiitaClient()
    assert client.token == "x" * 40

def test_qiita_client_init_invalid():
    os.environ.pop("QIITA_TOKEN", None)
    with pytest.raises(ValueError):
        QiitaClient(token="short") 