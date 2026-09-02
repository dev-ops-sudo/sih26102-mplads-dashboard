import { BrainCircuit, FileWarning, MapPinned, Radar } from "lucide-react";
import { IntelligenceNetwork } from "./IntelligenceNetwork";

export function Overview() {
  return (
    <section className="overview-panel" id="overview">
      <IntelligenceNetwork />
      <div className="overview-copy">
        <span className="eyebrow">SIH26102 concept</span>
        <h1>National project intelligence, from signal to action.</h1>
        <p>
          An AI-assisted command centre for detecting delays, overruns, duplicate works, unusual fund use,
          and weak evidence across MPLADS projects, districts, and implementing agencies.
        </p>
        <div className="signal-stats" aria-label="Intelligence platform capabilities">
          <span><strong>24/7</strong><small>Signal watch</small></span>
          <span><strong>5</strong><small>AI layers</small></span>
          <span><strong>100%</strong><small>Explainable risk</small></span>
        </div>
      </div>
      <div className="level-strip" aria-label="Platform intelligence levels">
        {[
          ["Level 1", "Monitoring", MapPinned],
          ["Level 2", "Anomaly detection", FileWarning],
          ["Level 3", "Risk intelligence", Radar],
          ["Level 4", "Investigation", BrainCircuit],
          ["Level 5", "Prediction", Radar]
        ].map(([level, title, Icon]) => (
          <div className="level-item" key={String(title)}>
            <Icon size={18} />
            <span>{level as string}</span>
            <strong>{title as string}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
