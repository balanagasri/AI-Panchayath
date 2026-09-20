from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.models.complaint import Complaint, ComplaintCreate
from app.models.issue import ComplaintSummary, Dashboard, Issue, IssueDetails
from app.services.dynamodb_store import dynamodb_store
from app.services.nlp_engine import nlp_engine


ISSUE_DEFINITIONS = {
    'water': {
        'title': 'Water Supply Disruption',
        'category': 'Water & sanitation',
        'severity': 'Critical',
        'population_per_report': 600,
        'summary': 'Reports indicate a shared water access problem affecting connected locations.',
        'actions': ['Dispatch a water department field team', 'Publish an interim tanker schedule', 'Inspect the local distribution line'],
    },
    'garbage': {
        'title': 'Garbage Collection Failure',
        'category': 'Sanitation',
        'severity': 'High',
        'population_per_report': 400,
        'summary': 'Missed pickups are creating a recurring sanitation concern across the reported routes.',
        'actions': ['Confirm missed routes with the sanitation contractor', 'Schedule a temporary collection run'],
    },
    'road': {
        'title': 'Road Damage',
        'category': 'Roads & transport',
        'severity': 'High',
        'population_per_report': 300,
        'summary': 'Road condition reports indicate a safety concern that should be inspected and prioritized.',
        'actions': ['Schedule a safety inspection', 'Place temporary road hazard markers'],
    },
    'light': {
        'title': 'Street Light Outage',
        'category': 'Public safety',
        'severity': 'Medium',
        'population_per_report': 250,
        'summary': 'Reports point to an outage affecting nighttime visibility in the reported area.',
        'actions': ['Inspect the connected electrical circuit', 'Confirm nighttime visibility after repair'],
    },
    'drainage': {
        'title': 'Drainage Blockage',
        'category': 'Water & sanitation',
        'severity': 'Medium',
        'population_per_report': 250,
        'summary': 'Drainage reports suggest a blockage that may affect pedestrian access and local sanitation.',
        'actions': ['Clear the reported inlet', 'Check downstream flow before the next rainfall'],
    },
}


class CivicService:
    def add_complaint(self, payload: ComplaintCreate) -> Complaint:
        complaint = Complaint(
            id=str(uuid4()),
            created_at=datetime.now(UTC),
            **payload.model_dump(),
        )
        dynamodb_store.save_complaint(complaint)
        self._refresh_issues()
        return complaint

    def list_complaints(self) -> list[Complaint]:
        return dynamodb_store.list_complaints()

    def _grouped_complaints(self) -> dict[str, list[Complaint]]:
        return nlp_engine.group(self.list_complaints())

    def _refresh_issues(self) -> list[IssueDetails]:
        grouped = self._grouped_complaints()
        issues = [self._build_issue(issue_id, complaints) for issue_id, complaints in grouped.items()]
        dynamodb_store.replace_issues(issues)
        return issues

    def _build_issue(self, issue_id: str, complaints: list[Complaint]) -> IssueDetails:
        definition = ISSUE_DEFINITIONS.get(issue_id, self._emerging_definition(complaints))
        count = len(complaints)
        locations = list(dict.fromkeys(complaint.location for complaint in complaints))
        today = datetime.now(UTC).date()
        trend = [sum(complaint.created_at.date() == today - timedelta(days=6 - offset) for complaint in complaints) for offset in range(7)]
        status = 'Investigating' if count >= 3 else 'Monitoring'
        return IssueDetails(
            id=issue_id,
            title=definition['title'],
            category=definition['category'],
            severity=definition['severity'],
            reports=count,
            affected_locations=locations,
            affected_population=count * definition['population_per_report'],
            trend=trend,
            trend_label=f'{count} report' + ('' if count == 1 else 's') + ' received',
            status=status,
            summary=definition['summary'],
            recommended_actions=definition['actions'],
            recent_complaints=[complaint.description for complaint in complaints[:5]],
        )

    @staticmethod
    def _emerging_definition(complaints: list[Complaint]) -> dict:
        return {
            'title': 'Emerging Community Issue',
            'category': complaints[0].category,
            'severity': 'Low',
            'population_per_report': 150,
            'summary': 'Local NLP grouped similar community reports into an emerging issue.',
            'actions': ['Review the affected locations', 'Assign a team for initial verification'],
        }

    def list_issues(self) -> list[Issue]:
        issues = dynamodb_store.list_issues()
        if not issues and self.list_complaints():
            issues = self._refresh_issues()
        return [Issue.model_validate(issue) for issue in issues]

    def get_issue(self, issue_id: str) -> IssueDetails | None:
        issue = dynamodb_store.get_issue(issue_id)
        if issue is None and self.list_complaints():
            self._refresh_issues()
            issue = dynamodb_store.get_issue(issue_id)
        return issue

    def dashboard(self) -> Dashboard:
        issues = self.list_issues()
        complaints = self.list_complaints()
        recent_reports = [
            ComplaintSummary(
                id=complaint.id,
                description=complaint.description,
                category=complaint.category,
                location=complaint.location,
                created_at=complaint.created_at.isoformat(),
            )
            for complaint in complaints[:10]
        ]
        return Dashboard(
            total_reports=len(complaints),
            active_issues=sum(issue.status != 'Resolved' for issue in issues),
            emerging_issues=sum(issue.reports < 3 for issue in issues),
            critical_issues=sum(issue.severity == 'Critical' for issue in issues),
            issue_trends={issue.id: issue.trend for issue in issues},
            recent_reports=recent_reports,
        )


civic_service = CivicService()
