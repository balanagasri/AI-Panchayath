const API_BASE_URL = 'http://127.0.0.1:8000'

export type Severity = 'Critical' | 'High' | 'Medium' | 'Low'
export type IssueStatus = 'Investigating' | 'In progress' | 'Monitoring' | 'Resolved'

export type ComplaintCreate = {
  description: string
  location: string
  category: string
  image_reference: string | null
}

export type Complaint = ComplaintCreate & {
  id: string
  created_at: string
}

export type ComplaintSummary = {
  id: string
  description: string
  category: string
  location: string
  created_at: string
}

export type Issue = {
  id: string
  title: string
  category: string
  severity: Severity
  reports: number
  affected_locations: string[]
  affected_population: number
  trend: number[]
  trend_label: string
  status: IssueStatus
}

export type IssueDetails = Issue & {
  summary: string
  recommended_actions: string[]
  recent_complaints: string[]
}

export type Dashboard = {
  total_reports: number
  active_issues: number
  emerging_issues: number
  critical_issues: number
  issue_trends: Record<string, number[]>
  recent_reports: ComplaintSummary[]
}

export type AwsStatus = {
  aws_sdk: string
  production_storage: string
  mode: 'local' | 'dynamodb'
  aws_configured: boolean
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options?.headers },
    })
  } catch {
    throw new Error('Unable to connect to CivicSignal API. Is FastAPI running?')
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

export const api = {
  getDashboard: () => request<Dashboard>('/api/dashboard'),
  getIssues: () => request<Issue[]>('/api/issues'),
  getIssue: (issueId: string) => request<IssueDetails>(`/api/issues/${encodeURIComponent(issueId)}`),
  createComplaint: (payload: ComplaintCreate) => request<Complaint>('/api/complaints', { method: 'POST', body: JSON.stringify(payload) }),
  getAwsStatus: () => request<AwsStatus>('/api/aws-status'),
}
