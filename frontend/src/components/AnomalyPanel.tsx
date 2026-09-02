import { AlertTriangle, CopyCheck, Landmark, TimerReset } from "lucide-react";
import type { Project } from "../types";

interface AnomalyPanelProps { project: Project; }

export function AnomalyPanel({ project }: AnomalyPanelProps) {
  const items = [
    { label: "Cost anomaly", score: Math.min(98, project.utilization + 8), icon: Landmark, detail: "Spend pattern is compared with BOQ, peer projects, and progress." },
    { label: "Delay risk", score: project.status === "Delayed" || project.status === "Flagged" ? 82 : 34, icon: TimerReset, detail: "Milestone slippage and inspection gaps are reviewed together." },
    { label: "Financial mismatch", score: project.spentCr / project.budgetCr > project.progress / 100 ? 78 : 28, icon: AlertTriangle, detail: "Voucher progress is checked against physical progress evidence." },
    { label: "Possible duplicate", score: project.anomalyTypes.includes("Possible duplicate") ? 74 : 18, icon: CopyCheck, detail: "Nearby similar works are clustered by text, location, agency, and date." }
  ];
  return (
    <section className="panel" id="anomalies">
      <div className="panel-header"><div><span className="eyebrow">Level 2</span><h2>AI anomaly detection</h2></div></div>
      <div className="anomaly-grid">
        {items.map(({ label, score, icon: Icon, detail }) => (
          <article className="anomaly-card" key={label}><Icon size={20} /><span>{label}</span><strong>{Math.round(score)}%</strong><div className="meter"><span style={{ width: `${score}%` }} /></div><small>{detail}</small></article>
        ))}
      </div>
    </section>
  );
}

