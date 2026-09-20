from fastapi import APIRouter, status

from app.models.complaint import Complaint, ComplaintCreate
from app.services.civic_service import civic_service

router = APIRouter(prefix='/api/complaints', tags=['complaints'])


@router.post('', response_model=Complaint, status_code=status.HTTP_201_CREATED)
def create_complaint(payload: ComplaintCreate) -> Complaint:
    return civic_service.add_complaint(payload)


@router.get('', response_model=list[Complaint])
def get_complaints() -> list[Complaint]:
    return civic_service.list_complaints()
