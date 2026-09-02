export type RiskLevel = "Low" | "Medium" | "High" | "Critical";
export type ProjectStatus = "On Track" | "Delayed" | "Flagged" | "Completed";

export interface Project {
  id: string;
  title: string;
  state: string;
  district: string;
  constituency: string;
  city: string;
  type: string;
  agency: string;
  status: ProjectStatus;
  risk: RiskLevel;
  budgetCr: number;
  spentCr: number;
  utilization: number;
  progress: number;
  sanctionedDate: string;
  expectedCompletion: string;
  lastInspection: string;
  latitude: number;
  longitude: number;
  riskScore: number;
  anomalyTypes: string[];
  summary: string;
}

export interface Alert {
  id: string;
  projectId: string;
  title: string;
  district: string;
  severity: RiskLevel;
  time: string;
  description: string;
}

export interface Agency {
  name: string;
  projects: number;
  avgDelayDays: number;
  riskScore: number;
  completionRate: number;
}

export interface TimelineEvent {
  date: string;
  title: string;
  state: "done" | "active" | "risk" | "upcoming";
  detail: string;
}

export interface RiskContribution {
  label: string;
  weight: number;
  score: number;
  explanation: string;
}

export interface Prediction {
  id: string;
  title: string;
  probability: number;
  impact: "Cost" | "Delay" | "Compliance";
  projectId: string;
  recommendation: string;
}

