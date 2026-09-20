export type Severity = 'Critical' | 'High' | 'Medium' | 'Low'
export type IssueStatus = 'Investigating' | 'In progress' | 'Monitoring' | 'Resolved'

export type Issue = {
  id: string
  title: string
  category: string
  severity: Severity
  reports: number
  locations: string[]
  population: string
  trend: number[]
  trendLabel: string
  status: IssueStatus
  summary: string
  actions: string[]
  complaints: { quote: string; location: string; time: string }[]
}

export const issues: Issue[] = [
  { id: 'water', title: 'Water Supply Disruption', category: 'Water & sanitation', severity: 'Critical', reports: 31, locations: ['Ward 12', 'Mahalaxmi Nagar', 'Shivaji Colony'], population: '18,400', trend: [28, 36, 35, 48, 44, 62, 72], trendLabel: '+18% this week', status: 'Investigating', summary: 'Reports cluster around a supply interruption affecting three connected neighborhoods. The timing and locations suggest a shared distribution-line fault rather than isolated household issues.', actions: ['Dispatch a water department field team to Ward 12', 'Publish an interim tanker schedule for affected streets', 'Inspect the Shivaji Colony distribution valve'], complaints: [{ quote: 'No water since yesterday morning. The whole lane is affected.', location: 'Mahalaxmi Nagar', time: '12 min ago' }, { quote: 'The tanker did not arrive today and the school is running out.', location: 'Shivaji Colony', time: '38 min ago' }, { quote: 'Pressure has been low for three days now.', location: 'Ward 12', time: '1 hr ago' }] },
  { id: 'garbage', title: 'Garbage Collection Failure', category: 'Sanitation', severity: 'High', reports: 24, locations: ['Green Park', 'Old Market Road'], population: '9,800', trend: [40, 44, 51, 46, 55, 52, 59], trendLabel: '+11% this week', status: 'In progress', summary: 'Missed pickups are concentrated on two collection routes, causing overflow near the market and residential lanes.', actions: ['Confirm missed routes with the sanitation contractor', 'Add a temporary pickup at Old Market Road'], complaints: [{ quote: 'Bins have been overflowing since Monday.', location: 'Green Park', time: '2 hrs ago' }] },
  { id: 'roads', title: 'Road Damage', category: 'Roads & transport', severity: 'High', reports: 19, locations: ['Station Road', 'Nehru Chowk'], population: '7,250', trend: [26, 32, 30, 38, 42, 40, 46], trendLabel: '+6% this week', status: 'Monitoring', summary: 'Pothole reports are increasing along the main bus corridor, with the highest concentration near Station Road.', actions: ['Schedule a safety inspection before the next rainfall', 'Place temporary road hazard markers'], complaints: [{ quote: 'Two-wheelers are swerving into traffic to avoid the crater.', location: 'Station Road', time: '3 hrs ago' }] },
  { id: 'lights', title: 'Street Light Outage', category: 'Public safety', severity: 'Medium', reports: 16, locations: ['Lake View Lane', 'Sector 4'], population: '5,600', trend: [34, 31, 29, 35, 32, 30, 28], trendLabel: '-4% this week', status: 'In progress', summary: 'Outages are limited to two connected electrical circuits and are declining after replacement work began.', actions: ['Complete the Sector 4 fixture replacement', 'Confirm nighttime visibility with residents'], complaints: [{ quote: 'The lane is completely dark after 7pm.', location: 'Lake View Lane', time: 'Yesterday' }] },
  { id: 'drainage', title: 'Drainage Blockage', category: 'Water & sanitation', severity: 'Medium', reports: 12, locations: ['Kalyan East', 'Market Extension'], population: '4,100', trend: [18, 22, 20, 26, 25, 31, 35], trendLabel: '+9% this week', status: 'Investigating', summary: 'Blocked drains are beginning to affect pedestrian access around Market Extension ahead of forecast rain.', actions: ['Clear the Market Extension inlet', 'Check downstream flow before the weekend'], complaints: [{ quote: 'The drain smells and water is backing up onto the footpath.', location: 'Market Extension', time: 'Yesterday' }] },
]

export const recentReports = [
  { text: 'No water since yesterday morning', category: 'Water', location: 'Mahalaxmi Nagar', time: '12 min ago', tone: 'red' },
  { text: 'Garbage not collected for 3 days', category: 'Sanitation', location: 'Green Park', time: '24 min ago', tone: 'amber' },
  { text: 'Large pothole near bus stop', category: 'Roads', location: 'Station Road', time: '1 hr ago', tone: 'blue' },
  { text: 'Street light flickering at night', category: 'Safety', location: 'Lake View Lane', time: '2 hrs ago', tone: 'violet' },
]

export const trendData = [31, 42, 38, 56, 48, 63, 58, 74, 66, 86, 78, 94]