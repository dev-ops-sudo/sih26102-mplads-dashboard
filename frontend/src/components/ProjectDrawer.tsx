import { X } from "lucide-react";
import type { Project } from "../types";
import { formatDate, inrCr, riskClass } from "../utils/format";

interface ProjectDrawerProps {
  project: Project | null;
  onClose: () => void;
}

export function ProjectDrawer({ project, onClose }: ProjectDrawerProps) {
  return (
    <aside className={project ? "drawer open" : "drawer"} aria-hidden={!project}>
      {project && (
        <>
          <div className="drawer-header">
            <div>
              <span className="eyebrow">{project.id}</span>
              <h2>{project.title}</h2>
            </div>
            <button className="icon-button" onClick={onClose} aria-label="Close project details">
              <X size={18} />
            </button>
          </div>
          <p>{project.summary}</p>
          <div className="drawer-grid">
            <span>
              <small>State</small>
              <strong>{project.state}</strong>
            </span>
            <span>
              <small>District</small>
              <strong>{project.district}</strong>
            </span>
            <span>
              <small>Budget</small>
              <strong>{inrCr(project.budgetCr)}</strong>
            </span>
            <span>
              <small>Spent</small>
              <strong>{inrCr(project.spentCr)}</strong>
            </span>
            <span>
              <small>Risk score</small>
              <strong>{project.riskScore}/100</strong>
            </span>
            <span>
              <small>Risk</small>
              <strong className={`drawer-risk ${riskClass(project.risk)}`}>{project.risk}</strong>
            </span>
          </div>
          <div className="drawer-section">
            <h3>Anomaly flags</h3>
            <div className="tag-row">
              {(project.anomalyTypes.length ? project.anomalyTypes : ["No major anomaly"]).map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          </div>
          <div className="drawer-section">
            <h3>Project dates</h3>
            <ul className="date-list">
              <li>Sanctioned: {formatDate(project.sanctionedDate)}</li>
              <li>Expected completion: {formatDate(project.expectedCompletion)}</li>
              <li>Last inspection: {formatDate(project.lastInspection)}</li>
            </ul>
          </div>
        </>
      )}
    </aside>
  );
}
