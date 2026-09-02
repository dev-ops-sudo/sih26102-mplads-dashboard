import { MapPinned, Navigation } from "lucide-react";
import type { Project } from "../types";
import { riskClass } from "../utils/format";

interface GeoIntelligenceMapProps {
  projects: Project[];
  selectedProjectId?: string;
  onSelectProject: (project: Project) => void;
}

const positions: Record<string, { x: number; y: number }> = {
  Delhi: { x: 47, y: 31 },
  Maharashtra: { x: 35, y: 62 },
  Karnataka: { x: 42, y: 78 },
  "Uttar Pradesh": { x: 56, y: 38 },
  "Tamil Nadu": { x: 49, y: 89 },
  Assam: { x: 82, y: 35 }
};

export function GeoIntelligenceMap({ projects, selectedProjectId, onSelectProject }: GeoIntelligenceMapProps) {
  return (
    <section className="panel geo-panel" id="geo-intelligence">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Geo intelligence</span>
          <h2>India project risk layer</h2>
        </div>
        <MapPinned size={20} />
      </div>
      <div className="map-grid">
        <div className="india-map" role="img" aria-label="Interactive India risk placeholder map">
          <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
            <path
              className="map-shape"
              d="M47 11 C54 13 60 18 61 26 C68 27 72 32 72 39 C80 40 84 48 80 55 C76 62 67 64 63 70 C59 76 58 85 51 91 C45 84 42 77 37 72 C31 66 24 61 24 53 C24 45 30 40 31 34 C32 25 38 16 47 11 Z"
            />
            <path className="map-line" d="M34 34 C42 39 51 39 61 34" />
            <path className="map-line" d="M31 55 C42 51 55 54 72 49" />
            <path className="map-line" d="M42 75 C46 65 47 50 46 28" />
          </svg>
          {projects.map((project) => {
            const position = positions[project.state] ?? { x: 50, y: 50 };
            return (
              <button
                className={`map-dot ${riskClass(project.risk)} ${project.id === selectedProjectId ? "active" : ""}`}
                style={{ left: `${position.x}%`, top: `${position.y}%` }}
                key={project.id}
                onClick={() => onSelectProject(project)}
                aria-label={`Select ${project.title}`}
              >
                <span />
              </button>
            );
          })}
        </div>
        <div className="geo-list">
          {projects.slice(0, 4).map((project) => (
            <button
              className={project.id === selectedProjectId ? "geo-row active" : "geo-row"}
              key={project.id}
              onClick={() => onSelectProject(project)}
            >
              <Navigation size={15} />
              <span>
                <strong>{project.district}</strong>
                <small>{project.type} · {project.risk} risk</small>
              </span>
              <b>{project.riskScore}</b>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
