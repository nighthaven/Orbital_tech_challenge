from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from typing import Annotated, Optional

from src.exceptions.session.session_not_found_exception import SessionNotFoundException
from src.schemas.session_schemas.session_response import SessionResponse
from src.services.dataset_service import DatasetService
from src.services.session_service import SessionService
from src.schemas.session_schemas.ask_response_model import AskResponseModel
from src.schemas.session_schemas.ask_query import AskQuery
from src.usecases.chat_usecase import ChatUseCase

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
)


# pour les routes HTTP
def get_session_service_http(request: Request) -> SessionService:
    return request.app.state.session_service

def get_dataset_service_http(request: Request) -> DatasetService:
    return request.app.state.dataset_service

# pour les websockets
def get_session_service_ws(web_socket: WebSocket) -> SessionService:
    return web_socket.app.state.session_service

def get_dataset_service_ws(web_socket: WebSocket) -> DatasetService:
    return web_socket.app.state.dataset_service


@router.post("/", response_model=SessionResponse)
def create_session(
    session_service: Annotated[SessionService, Depends(get_session_service_http)],
):
    session_id = session_service.create_session()
    return SessionResponse(session_id=session_id)


@router.delete("/{session_id}", status_code=204)
def delete_session(
    session_id: str,
    session_service: Annotated[SessionService, Depends(get_session_service_http)],
) -> None:
    try:
        session_service.delete_session(session_id)
    except SessionNotFoundException:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found. session id provided: {session_id}",
        )


@router.post("/{session_id}/ask", response_model=AskResponseModel)
async def ask(
    session_id: str,
    query: AskQuery,
    dataset_service: Annotated[DatasetService, Depends(get_dataset_service_http)],
    session_service: Annotated[SessionService, Depends(get_session_service_http)],
):
    try:
        chat_usecase = ChatUseCase(dataset_service, session_service)
        return await chat_usecase.ask(session_id, query.question)
    except SessionNotFoundException:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found. session id provided: {session_id}",
        )


@router.websocket("/{session_id}/chat")
async def chat_websocket(
    web_socket: WebSocket,
    session_id: str,
    dataset_service: DatasetService = Depends(get_dataset_service_ws),
    session_service: SessionService = Depends(get_session_service_ws),
):
    await web_socket.accept()
    chat_usecase = ChatUseCase(dataset_service, session_service)
    try:
        await chat_usecase.stream_ask(web_socket, session_id)
    except WebSocketDisconnect:
        print(f"Session {session_id} disconnected")
    finally:
        await web_socket.close()
