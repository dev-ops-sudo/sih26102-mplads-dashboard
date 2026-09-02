import type { TimelineEvent } from "../types";
import { formatDate } from "../utils/format";

interface TimelineProps {
  events: TimelineEvent[];
}

export function Timeline({ events }: TimelineProps) {
  return (
    <section className="panel timeline-panel">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Project timeline</span>
          <h2>Evidence and milestone history</h2>
        </div>
      </div>
      <ol className="timeline">
        {events.map((event) => (
          <li className={event.state} key={`${event.date}-${event.title}`}>
            <span>{formatDate(event.date)}</span>
            <strong>{event.title}</strong>
            <p>{event.detail}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
