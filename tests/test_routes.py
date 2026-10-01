import os


# Use mock mode for testing.
os.environ["MOCK_AI"] = "true"

os.environ[
    "IMAGE_PROVIDER"
] = "placeholder"


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ============================================================
# HEALTH TEST
# ============================================================

def test_health():

    response = client.get(
        "/health"
    )


    assert response.status_code == 200


    assert (
        response.json()["status"]
        == "ok"
    )


# ============================================================
# HOME TEST
# ============================================================

def test_home():

    response = client.get("/")


    assert response.status_code == 200


    assert (
        "ComicCraft"
        in response.text
    )