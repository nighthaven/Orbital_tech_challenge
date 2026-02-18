import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.services.dataset_service import DatasetService

from src.services.session_service import SessionService


@pytest.fixture
def client() -> TestClient:  # type: ignore[misc]
    with TestClient(app) as test_client:
        app.state.dataset_service = DatasetService(data_dir="data")
        app.state.dataset_service.load()
        app.state.session_service = SessionService()
        yield test_client
