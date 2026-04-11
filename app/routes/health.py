from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {
        "project": settings.app_name,
        "version": settings.app_version,
        "status": "ok",
        "email_check_enabled": settings.enable_email_check,
    }
