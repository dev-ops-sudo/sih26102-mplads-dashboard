import { Building2 } from "lucide-react";
import type { Agency } from "../types";

interface AgencyIntelligenceProps {
  agencies: Agency[];
}

export function AgencyIntelligence({ agencies }: AgencyIntelligenceProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Agency intelligence</span>
          <h2>Implementation agency performance</h2>
        </div>
        <Building2 size={20} />
      </div>
      <div className="agency-list">
        {agencies.map((agency) => (
          <article className="agency-row" key={agency.name}>
            <div>
              <strong>{agency.name}</strong>
              <small>{agency.projects} active MPLADS works · avg delay {agency.avgDelayDays} days</small>
            </div>
            <div className="agency-score">
              <span>{agency.completionRate}% completion</span>
              <div className="meter"><span style={{ width: `${agency.completionRate}%` }} /></div>
            </div>
            <b>{agency.riskScore}</b>
          </article>
        ))}
      </div>
    </section>
  );
}
