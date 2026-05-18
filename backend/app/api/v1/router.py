from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.api.v1.endpoints.auth_runtime import router as auth_router
from app.api.v1.endpoints.analyze_runtime import router as analyze_router
from app.api.v1.endpoints.reports_runtime import router as reports_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(analyze_router, prefix="/analyze", tags=["analyze"])
router.include_router(reports_router, prefix="/reports", tags=["reports"])
router.include_router(health.router, prefix="/health", tags=["health"])
