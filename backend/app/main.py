from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import analysis_request, github_cache, report, user
from app.utils.file_storage import ensure_reports_dir

app = FastAPI(title="GitFolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    ensure_reports_dir()

@app.get("/")
def root():
    return {"service": "GitFolio API", "status": "running"}
