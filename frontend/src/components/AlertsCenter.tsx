import { BellRing } from "lucide-react";
import type { Alert } from "../types";
import { riskClass } from "../utils/format";

interface AlertsCenterProps { alerts: Alert[]; }

export function AlertsCenter({ alerts }: AlertsCenterProps) {
  return (
    <section className="panel alerts-panel">
      <div className="panel-header"><div><span className="eyebrow">Alerts centre</span><h2>Priority review queue</h2></div><BellRing size={20} /></div>
      <div className="alerts-list">
        {alerts.map((alert) => (
          <article className={`alert-item ${riskClass(alert.severity)}`} key={alert.id}>
            <span className="alert-dot" />
            <div><strong>{alert.title}</strong><small>{alert.district} · {alert.time} · {alert.projectId}</small><p>{alert.description}</p></div>
          </article>
        ))}
      </div>
    </section>
  );
}

