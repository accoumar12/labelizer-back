from fastapi.testclient import TestClient

from labelizer.core.api.fast_api_app import app

client = TestClient(app)

SUCCESS_STATUS_CODE = 200


def test_make_triplet() -> None:
    response = client.get("/triplet")
    assert response.status_code == SUCCESS_STATUS_CODE
