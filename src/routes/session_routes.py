from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Annotated

from src.exceptions.session.session_not_found_exception import SessionNotFoundException
from src.schemas.session_schemas.session_response import SessionResponse
from src.services.session_service import SessionService

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
)


def get_session_service(request: Request) -> SessionService:
    return request.app.state.session_service


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
