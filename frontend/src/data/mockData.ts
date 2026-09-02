import type { Agency, Alert, Prediction, Project, RiskContribution, TimelineEvent } from "../types";

export const projects: Project[] = [
  {
    id: "MP-102-DEL-014",
    title: "Smart Community Health Centre Upgrade",
    state: "Delhi",
    district: "New Delhi",
    constituency: "New Delhi",
    city: "New Delhi",
    type: "Health",
    agency: "Delhi PWD",
    status: "Flagged",
    risk: "Critical",
    budgetCr: 8.6,
    spentCr: 7.9,
    utilization: 92,
    progress: 54,
    sanctionedDate: "2025-10-14",
    expectedCompletion: "2026-11-20",
    lastInspection: "2026-08-22",
    latitude: 28.61,
    longitude: 77.2,
    riskScore: 87,
    anomalyTypes: ["Cost anomaly", "Delay", "Financial mismatch"],
    summary: "Spend is high compared with physical progress and inspection notes show procurement variance."
  },
  {
    id: "MP-102-MH-081",
    title: "Rural School Digital Lab Cluster",
    state: "Maharashtra",
    district: "Pune",
    constituency: "Baramati",
    city: "Baramati",
    type: "Education",
    agency: "Zilla Parishad Pune",
    status: "Delayed",
    risk: "High",
    budgetCr: 5.2,
    spentCr: 3.9,
    utilization: 75,
    progress: 48,
    sanctionedDate: "2025-07-02",
    expectedCompletion: "2026-10-05",
    lastInspection: "2026-08-18",
    latitude: 18.15,
    longitude: 74.58,
    riskScore: 73,
    anomalyTypes: ["Delay", "Possible duplicate"],
    summary: "Milestone slippage detected across three schools with similar work descriptions nearby."
  },
  {
    id: "MP-102-KA-029",
    title: "Lakefront Solar Lighting and CCTV",
    state: "Karnataka",
    district: "Bengaluru Urban",
    constituency: "Bangalore South",
    city: "Bengaluru",
    type: "Urban Development",
    agency: "BBMP",
    status: "On Track",
    risk: "Medium",
    budgetCr: 3.4,
    spentCr: 1.8,
    utilization: 53,
    progress: 61,
    sanctionedDate: "2026-01-12",
    expectedCompletion: "2026-12-16",
    lastInspection: "2026-08-24",
    latitude: 12.97,
    longitude: 77.59,
    riskScore: 42,
    anomalyTypes: ["Minor procurement variance"],
    summary: "Project is broadly on schedule, with vendor invoice clustering requiring routine review."
  },
  {
    id: "MP-102-UP-117",
    title: "Primary Road Drainage Reconstruction",
    state: "Uttar Pradesh",
    district: "Varanasi",
    constituency: "Varanasi",
    city: "Varanasi",
    type: "Roads",
    agency: "UP Rural Engineering",
    status: "Flagged",
    risk: "High",
    budgetCr: 11.8,
    spentCr: 8.4,
    utilization: 71,
    progress: 43,
    sanctionedDate: "2025-05-19",
    expectedCompletion: "2026-09-30",
    lastInspection: "2026-08-20",
    latitude: 25.32,
    longitude: 82.97,
    riskScore: 79,
    anomalyTypes: ["Cost anomaly", "Delay", "Possible duplicate"],
    summary: "Repeated drainage work appears in adjacent wards while current site has weak progress evidence."
  },
  {
    id: "MP-102-TN-044",
    title: "Anganwadi Nutrition Centre Modernisation",
    state: "Tamil Nadu",
    district: "Chennai",
    constituency: "Chennai South",
    city: "Chennai",
    type: "Social Welfare",
    agency: "Greater Chennai Corporation",
    status: "Completed",
    risk: "Low",
    budgetCr: 2.2,
    spentCr: 2.1,
    utilization: 95,
    progress: 100,
    sanctionedDate: "2025-12-03",
    expectedCompletion: "2026-07-14",
    lastInspection: "2026-08-06",
    latitude: 13.08,
    longitude: 80.27,
    riskScore: 18,
    anomalyTypes: [],
    summary: "Work completed with matching image, inspection, and expenditure evidence."
  },
  {
    id: "MP-102-AS-032",
    title: "Flood-Resilient Drinking Water Points",
    state: "Assam",
    district: "Dibrugarh",
    constituency: "Dibrugarh",
    city: "Dibrugarh",
    type: "Water",
    agency: "Assam PHED",
    status: "Delayed",
    risk: "Medium",
    budgetCr: 4.8,
    spentCr: 2.7,
    utilization: 56,
    progress: 52,
    sanctionedDate: "2025-11-28",
    expectedCompletion: "2026-12-01",
    lastInspection: "2026-08-12",
    latitude: 27.47,
    longitude: 94.91,
    riskScore: 55,
    anomalyTypes: ["Delay"],
    summary: "Monsoon disruption explains part of the slippage; early warning remains active."
  }
];

export const alerts: Alert[] = [
  {
    id: "AL-901",
    projectId: "MP-102-DEL-014",
    title: "Financial progress exceeds physical progress by 38%",
    district: "New Delhi",
    severity: "Critical",
    time: "18 min ago",
    description: "Voucher pattern and inspection progress diverge beyond the normal tolerance band."
  },
  {
    id: "AL-902",
    projectId: "MP-102-UP-117",
    title: "Possible duplicate drainage work detected",
    district: "Varanasi",
    severity: "High",
    time: "42 min ago",
    description: "Three nearby works share similar scope, agency, and sanction period."
  },
  {
    id: "AL-903",
    projectId: "MP-102-MH-081",
    title: "Milestone completion confidence dropped",
    district: "Pune",
    severity: "High",
    time: "2 hr ago",
    description: "Site image sequence and contractor reporting do not support the claimed milestone."
  },
  {
    id: "AL-904",
    projectId: "MP-102-AS-032",
    title: "Delay probability elevated due to weather window",
    district: "Dibrugarh",
    severity: "Medium",
    time: "5 hr ago",
    description: "Forecasted site accessibility window may push handover by 24-32 days."
  }
];

export const agencies: Agency[] = [
  { name: "Delhi PWD", projects: 22, avgDelayDays: 41, riskScore: 76, completionRate: 68 },
  { name: "UP Rural Engineering", projects: 31, avgDelayDays: 35, riskScore: 72, completionRate: 64 },
  { name: "BBMP", projects: 18, avgDelayDays: 12, riskScore: 38, completionRate: 81 },
  { name: "Greater Chennai Corporation", projects: 16, avgDelayDays: 5, riskScore: 24, completionRate: 91 }
];

export const riskContributions: RiskContribution[] = [
  {
    label: "Cost variance",
    weight: 30,
    score: 92,
    explanation: "Expenditure is above peer benchmark for current progress."
  },
  {
    label: "Schedule slippage",
    weight: 25,
    score: 81,
    explanation: "Milestone trend suggests completion may miss the sanctioned window."
  },
  {
    label: "Evidence confidence",
    weight: 20,
    score: 68,
    explanation: "Inspection notes, geo images, and bills are partially inconsistent."
  },
  {
    label: "Duplicate similarity",
    weight: 15,
    score: 74,
    explanation: "Nearby works share matching descriptions and agency assignment."
  },
  {
    label: "Agency history",
    weight: 10,
    score: 59,
    explanation: "Agency has moderate delay history in similar works."
  }
];

export const predictions: Prediction[] = [
  {
    id: "PR-1",
    title: "Likely completion delay beyond 60 days",
    probability: 82,
    impact: "Delay",
    projectId: "MP-102-DEL-014",
    recommendation: "Schedule joint inspection and freeze non-critical fund release until evidence improves."
  },
  {
    id: "PR-2",
    title: "Cost overrun risk crossing 18%",
    probability: 71,
    impact: "Cost",
    projectId: "MP-102-UP-117",
    recommendation: "Compare BOQ line items with neighbouring drainage works before approving next tranche."
  },
  {
    id: "PR-3",
    title: "Duplicate sanction investigation required",
    probability: 64,
    impact: "Compliance",
    projectId: "MP-102-MH-081",
    recommendation: "Run constituency-level similarity audit across school digital lab projects."
  }
];

export const timeline: TimelineEvent[] = [
  {
    date: "2025-10-14",
    title: "Sanction approved",
    state: "done",
    detail: "Initial release approved after district-level validation."
  },
  {
    date: "2026-01-08",
    title: "Procurement completed",
    state: "done",
    detail: "Primary civil and equipment procurement recorded."
  },
  {
    date: "2026-05-22",
    title: "First risk signal",
    state: "risk",
    detail: "Spend crossed 55% while physical progress remained below 35%."
  },
  {
    date: "2026-08-22",
    title: "Inspection mismatch",
    state: "active",
    detail: "Latest officer inspection contradicted contractor milestone claim."
  },
  {
    date: "2026-09-10",
    title: "Recommended review",
    state: "upcoming",
    detail: "AI recommends escalation to district review committee."
  }
];

export const monthlyTrend = [
  { month: "Mar", spend: 18, progress: 20, alerts: 18 },
  { month: "Apr", spend: 31, progress: 29, alerts: 22 },
  { month: "May", spend: 46, progress: 35, alerts: 34 },
  { month: "Jun", spend: 58, progress: 43, alerts: 39 },
  { month: "Jul", spend: 72, progress: 49, alerts: 51 },
  { month: "Aug", spend: 79, progress: 54, alerts: 64 }
];

export const sectorRisk = [
  { sector: "Roads", risk: 79 },
  { sector: "Health", risk: 87 },
  { sector: "Education", risk: 73 },
  { sector: "Water", risk: 55 },
  { sector: "Urban", risk: 42 },
  { sector: "Welfare", risk: 18 }
];

export const changedSinceLogin = [
  "14 new project risk alerts were generated across 6 states.",
  "Delhi PWD moved from High to Critical due to evidence mismatch.",
  "Three duplicate-work clusters were detected in Varanasi and Baramati.",
  "Projected cost overrun exposure increased by ₹12.4 Cr."
];
