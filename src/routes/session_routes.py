from fastapi import APIRouter, Depends, Request
from typing import Annotated

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
