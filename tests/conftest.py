import pytest
from fastapi.testclient import TestClient
from src.main import app
from pydantic_ai import AgentRunResultEvent
from pydantic_ai.messages import PartDeltaEvent, TextPartDelta

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

    async def run_stream_events(self, *args, **kwargs):
        for i, delta in enumerate(self._deltas):
            yield PartDeltaEvent(
                index=i,
                delta=TextPartDelta(content_delta=delta),
            )

        class FakeResult:
            def all_messages(self):
                return []

        yield AgentRunResultEvent(result=FakeResult())


@pytest.fixture
def fake_agent_factory():
    def _factory(deltas):
        return FakeAgent(deltas)

    return _factory
