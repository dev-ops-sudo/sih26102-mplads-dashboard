import { ArrowUpRight, Building2, CalendarClock } from "lucide-react";
import type { Project } from "../types";
import { formatDate, inrCr, riskClass } from "../utils/format";

interface ProjectTableProps {
  projects: Project[];
  selectedProjectId?: string;
  onSelectProject: (project: Project) => void;
}

export function ProjectTable({ projects, selectedProjectId, onSelectProject }: ProjectTableProps) {
  return (
    <section className="panel project-panel" id="projects">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Ongoing projects</span>
          <h2>District project watchlist</h2>
        </div>
        <span className="record-count">{projects.length} records</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Project</th>
              <th>Location</th>
              <th>Budget</th>
              <th>Progress</th>
              <th>Status</th>
              <th>Risk</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => (
              <tr className={selectedProjectId === project.id ? "selected" : ""} key={project.id}>
                <td>
                  <strong>{project.title}</strong>
                  <small>
                    <Building2 size={13} /> {project.agency}
                  </small>
                </td>
                <td>
                  {project.district}
                  <small>{project.constituency}</small>
                </td>
                <td>{inrCr(project.budgetCr)}</td>
                <td>
                  <div className="progress-cell">
                    <span style={{ width: `${project.progress}%` }} />
                  </div>
                  <small>{project.progress}% physical</small>
                </td>
                <td>
                  <span className="status-pill">{project.status}</span>
                </td>
                <td>
                  <span className={`risk-pill ${riskClass(project.risk)}`}>{project.risk}</span>
                </td>
                <td>
                  <button className="row-action" onClick={() => onSelectProject(project)} aria-label={`Open ${project.title}`}>
                    <ArrowUpRight size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="project-cards">
        {projects.map((project) => (
          <button className="project-card" key={project.id} onClick={() => onSelectProject(project)}>
            <span className={`risk-pill ${riskClass(project.risk)}`}>{project.risk}</span>
            <strong>{project.title}</strong>
            <small>{project.district} · {project.type}</small>
            <div className="card-meta">
              <span>{inrCr(project.budgetCr)}</span>
              <span>
                <CalendarClock size={13} /> {formatDate(project.expectedCompletion)}
              </span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}
