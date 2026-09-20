from fastapi import APIRouter, HTTPException, status

from app.models.issue import Issue, IssueDetails
from app.services.civic_service import civic_service

router = APIRouter(prefix='/api/issues', tags=['issues'])


@router.get('', response_model=list[Issue])
def get_issues() -> list[Issue]:
    return civic_service.list_issues()


@router.get('/{issue_id}', response_model=IssueDetails)
def get_issue(issue_id: str) -> IssueDetails:
    issue = civic_service.get_issue(issue_id)
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Issue not found')
    return issue
