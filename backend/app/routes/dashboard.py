from fastapi import APIRouter

from app.models.issue import Dashboard
from app.services.civic_service import civic_service

router = APIRouter(prefix='/api/dashboard', tags=['dashboard'])


@router.get('', response_model=Dashboard)
def get_dashboard() -> Dashboard:
    return civic_service.dashboard()
