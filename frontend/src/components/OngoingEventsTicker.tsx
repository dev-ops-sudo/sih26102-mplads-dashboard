import { Activity, AlertTriangle, MapPin, Pause, Play, ShieldAlert } from "lucide-react";
import { useMemo, useState } from "react";
import type { Alert, Project } from "../types";
import { riskClass } from "../utils/format";

interface OngoingEventsTickerProps {
  projects: Project[];
  alerts: Alert[];
  priorityActive: boolean;
  onSelectProject: (project: Project) => void;
  onTogglePriority: () => void;
}

interface FeedItem {
  id: string;
  projectId: string;
  title: string;
  location: string;
  detail: string;
  tone: string;
  kind: "alert" | "project";
}

export function OngoingEventsTicker({
  projects,
  alerts,
  priorityActive,
  onSelectProject,
  onTogglePriority
}: OngoingEventsTickerProps) {
  const [paused, setPaused] = useState(false);

  const feed = useMemo<FeedItem[]>(() => {
    const alertItems = alerts.map((alert) => ({
      id: `alert-${alert.id}`,
      projectId: alert.projectId,
      title: alert.title,
      location: alert.district,
      detail: alert.time,
      tone: riskClass(alert.severity),
      kind: "alert" as const
    }));

    const projectItems = projects
      .filter((project) => project.status !== "Completed")
      .map((project) => ({
        id: `project-${project.id}`,
        projectId: project.id,
        title: project.title,
        location: project.district,
        detail: `${project.progress}% progress · ${project.status}`,
        tone: riskClass(project.risk),
        kind: "project" as const
      }));

    return [...alertItems, ...projectItems];
  }, [alerts, projects]);

  const selectFeedItem = (item: FeedItem) => {
    const project = projects.find((candidate) => candidate.id === item.projectId);
    if (project) onSelectProject(project);
  };

  const renderSet = (clone: boolean) => (
    <div className={clone ? "ticker-set ticker-clone" : "ticker-set"} aria-hidden={clone || undefined}>
      {feed.map((item) => (
        <button
          className={`ticker-item ${item.tone}`}
          key={`${clone ? "clone" : "primary"}-${item.id}`}
          onClick={() => selectFeedItem(item)}
          tabIndex={clone ? -1 : 0}
          type="button"
        >
          <span className="ticker-kind" aria-hidden="true">
            {item.kind === "alert" ? <AlertTriangle size={14} /> : <Activity size={14} />}
          </span>
          <span className="ticker-copy">
            <strong>{item.title}</strong>
            <small><MapPin size={12} /> {item.location} · {item.detail}</small>
          </span>
        </button>
      ))}
    </div>
  );

  return (
    <section className="activity-ticker" aria-label="Live ongoing project events">
      <div className="ticker-lead">
        <span className="live-indicator" aria-hidden="true" />
        <span><strong>Live field feed</strong><small>{feed.length} active updates</small></span>
      </div>

      <div className="ticker-viewport">
        <div className={paused ? "ticker-track paused" : "ticker-track"}>
          {renderSet(false)}
          {renderSet(true)}
        </div>
      </div>

      <div className="ticker-actions">
        <button
          className={priorityActive ? "ticker-focus active" : "ticker-focus"}
          onClick={onTogglePriority}
          type="button"
          aria-pressed={priorityActive}
          aria-label={priorityActive ? "Show all project risks" : "Focus on high and critical risk projects"}
          title={priorityActive ? "Show all project risks" : "Focus on priority risks"}
        >
          <ShieldAlert size={15} />
          <span>{priorityActive ? "Show all" : "Priority only"}</span>
        </button>
        <button
          className="ticker-control"
          onClick={() => setPaused((value) => !value)}
          type="button"
          aria-label={paused ? "Resume live feed" : "Pause live feed"}
          title={paused ? "Resume live feed" : "Pause live feed"}
        >
          {paused ? <Play size={16} /> : <Pause size={16} />}
        </button>
      </div>
    </section>
  );
}
