import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.services.dataset_service import DatasetService
from src.services.session_service import SessionService
from src.routes.session_routes import router as sessions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """load datasets and session singleton and ensure output exist"""
    dataset_service = DatasetService(data_dir="data")
    dataset_service.load()

    app.state.dataset_service = dataset_service
    app.state.session_service = SessionService()

    os.makedirs("output", exist_ok=True)

    yield


app = FastAPI(title="Data Analysis Agent API", lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router, prefix="/api")
