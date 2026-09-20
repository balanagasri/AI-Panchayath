from typing import Literal

from pydantic import BaseModel


Severity = Literal['Critical', 'High', 'Medium', 'Low']
IssueStatus = Literal['Investigating', 'In progress', 'Monitoring', 'Resolved']


class Issue(BaseModel):
    id: str
    title: str
    category: str
    severity: Severity
    reports: int
    affected_locations: list[str]
    affected_population: int
    trend: list[int]
    trend_label: str
    status: IssueStatus


class IssueDetails(Issue):
    summary: str
    recommended_actions: list[str]
    recent_complaints: list[str]


class Dashboard(BaseModel):
    total_reports: int
    active_issues: int
    emerging_issues: int
    critical_issues: int
    issue_trends: dict[str, list[int]]
    recent_reports: list['ComplaintSummary']


class ComplaintSummary(BaseModel):
    id: str
    description: str
    category: str
    location: str
    created_at: str
