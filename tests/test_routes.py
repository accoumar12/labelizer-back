from fastapi.testclient import TestClient
from labelizer.core.api.fast_api_app import app

client = TestClient(app)


def test_make_triplet():
    response = client.get("/triplet")
    assert response.status_code == 200
