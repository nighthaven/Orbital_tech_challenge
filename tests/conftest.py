import pytest
from fastapi.testclient import TestClient
from src.main import app

from src.services.session_service import SessionService


@pytest.fixture
def client()-> TestClient:
    with TestClient(app) as test_client:
        app.state.session_service = SessionService()
        yield test_client