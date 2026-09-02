import { Gauge } from "lucide-react";
import type { RiskContribution } from "../types";

interface RiskScoringPanelProps {
  score: number;
  contributions: RiskContribution[];
}

export function RiskScoringPanel({ score, contributions }: RiskScoringPanelProps) {
  return (
    <section className="panel risk-panel" id="risk-intelligence">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Level 3</span>
          <h2>Explainable risk scoring</h2>
        </div>
        <Gauge size={20} />
      </div>
      <div className="risk-layout">
        <div className="gauge-wrap" style={{ "--score": score } as React.CSSProperties}>
          <div className="gauge-arc" />
          <div className="gauge-value">
            <strong>{score}</strong>
            <span>Risk score</span>
          </div>
        </div>
        <div className="contribution-list">
          {contributions.map((item) => (
            <div className="contribution" key={item.label}>
              <div>
                <strong>{item.label}</strong>
                <small>{item.explanation}</small>
              </div>
              <span>{item.weight}% weight</span>
              <div className="meter"><span style={{ width: `${item.score}%` }} /></div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
