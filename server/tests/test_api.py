from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz():
    assert client.get("/healthz").json() == {"status": "ok"}


def test_arrange_returns_jianzi_and_explanation():
    r = client.post("/api/arrange", json={"notes": [{"pitch": 53}], "auto_key": False})
    assert r.status_code == 200
    body = r.json()
    assert body["transpose"] == 0
    p = body["placements"][0]
    assert p["string"] == 3
    assert p["explain"] == "名指按七徽，勾三弦"


def test_auto_key_transposes_low_melody():
    r = client.post("/api/arrange", json={"notes": [{"pitch": 24}, {"pitch": 26}]})
    assert r.status_code == 200
    assert r.json()["transpose"] == 12


def test_unplayable_note_is_422():
    r = client.post("/api/arrange", json={"notes": [{"pitch": 20}], "auto_key": False})
    assert r.status_code == 422
    assert r.json()["detail"]["index"] == 0


def test_unknown_tuning_is_422():
    r = client.post("/api/arrange", json={"notes": [{"pitch": 48}], "tuning": "ruibin"})
    assert r.status_code == 422
