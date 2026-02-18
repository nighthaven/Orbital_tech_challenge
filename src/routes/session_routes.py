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


def get_session_service(
    request: Optional[Request] = None,
    web_socket: Optional[WebSocket] = None,
) -> SessionService:
    if request is not None:
        return request.app.state.session_service
    elif web_socket is not None:
        return web_socket.app.state.session_service
    else:
        raise RuntimeError("Either request or web_socket must be provided")


def get_dataset_service(
    request: Optional[Request] = None,
    web_socket: Optional[WebSocket] = None,
) -> DatasetService:
    if request:
        return request.app.state.dataset_service
    elif web_socket:
        return web_socket.app.state.dataset_service
    else:
        raise RuntimeError("Either request or web_socket must be provided")


@router.post("/", response_model=SessionResponse)
def create_session(
    session_service: Annotated[SessionService, Depends(get_session_service)],
):
    session_id = session_service.create_session()
    return SessionResponse(session_id=session_id)


@router.delete("/{session_id}", status_code=204)
def delete_session(
    session_id: str,
    session_service: Annotated[SessionService, Depends(get_session_service)],
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
    dataset_service: Annotated[DatasetService, Depends(get_dataset_service)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
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
    dataset_service: DatasetService = Depends(get_dataset_service),
    session_service: SessionService = Depends(get_session_service),
):
    await web_socket.accept()
    chat_usecase = ChatUseCase(dataset_service, session_service)
    try:
        await chat_usecase.stream_ask(web_socket, session_id)
    except WebSocketDisconnect:
        print(f"Session {session_id} disconnected")
    finally:
        await web_socket.close()
