import os

from fastapi.testclient import TestClient

from app.main import app


def test_api_works_without_aws_region(monkeypatch):
    monkeypatch.delenv('AWS_REGION', raising=False)
    monkeypatch.delenv('AWS_DEFAULT_REGION', raising=False)
    monkeypatch.delenv('AWS_ACCESS_KEY_ID', raising=False)
    monkeypatch.delenv('AWS_SECRET_ACCESS_KEY', raising=False)
    monkeypatch.delenv('AWS_SESSION_TOKEN', raising=False)

    client = TestClient(app)

    health = client.get('/health')
    assert health.status_code == 200
    assert health.json() == {'status': 'ok'}

    complaint_payload = {
        'description': 'Water pipe burst near the school and taps are dry',
        'location': 'Ward 7, Sector 12',
        'category': 'Water & sanitation',
        'image_reference': None,
    }

    complaint_response = client.post('/api/complaints', json=complaint_payload)
    assert complaint_response.status_code == 201, complaint_response.text
    complaint = complaint_response.json()
    assert complaint['description'] == complaint_payload['description']
    assert complaint['location'] == complaint_payload['location']

    issues_response = client.get('/api/issues')
    assert issues_response.status_code == 200, issues_response.text
    issues = issues_response.json()
    assert isinstance(issues, list)
    assert len(issues) >= 1

    dashboard_response = client.get('/api/dashboard')
    assert dashboard_response.status_code == 200, dashboard_response.text
    dashboard = dashboard_response.json()
    assert dashboard['total_reports'] >= 1
    assert 'issue_trends' in dashboard
    assert 'recent_reports' in dashboard

    issue_id = issues[0]['id']
    issue_detail = client.get(f'/api/issues/{issue_id}')
    assert issue_detail.status_code == 200, issue_detail.text
