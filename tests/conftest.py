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


class FakeWebSocket:
    def __init__(self):
        self.sent = []

    async def send_json(self, data):
        self.sent.append(data)


@pytest.fixture
def fake_websocket():
    return FakeWebSocket()


class FakeStream:
    def __init__(self, deltas=None):
        self._all_messages = []
        self._deltas = deltas or []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def stream_text(self, delta=True):
        for d in self._deltas:
            yield d

    def all_messages(self):
        return []


class FakeAgent:
    def __init__(self, deltas=None):
        self._deltas = deltas or []

    def run_stream(self, *args, **kwargs):
        return FakeStream(self._deltas)


@pytest.fixture
def fake_agent_factory():
    def _factory(deltas):
        return FakeAgent(deltas)

    return _factory
