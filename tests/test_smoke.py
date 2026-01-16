import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def patch_analyze(monkeypatch):
    async def fake_analyze(payload):
        return {
            "items_submitted": 1,
            "batches_sent": 1,
            "results": [{"id": "1", "aspects": [{"term": "screen", "sentiment": "positive"}]}],
            "duration_seconds": 0.01,
        }

    monkeypatch.setattr("app.api.analyze.analyze_items", fake_analyze)
    yield


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "timestamp" in data


def test_analyze_text_smoke():
    resp = client.post("/analyze", data={"text": "The screen is great but battery dies quickly."})
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert data["results"][0]["id"] == "1"
