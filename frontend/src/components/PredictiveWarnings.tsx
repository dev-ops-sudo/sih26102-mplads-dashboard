import { Activity, Clock3, IndianRupee, ShieldAlert } from "lucide-react";
import type { Prediction } from "../types";

interface PredictiveWarningsProps {
  predictions: Prediction[];
}

const icons = { Cost: IndianRupee, Delay: Clock3, Compliance: ShieldAlert };

export function PredictiveWarnings({ predictions }: PredictiveWarningsProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Level 5</span>
          <h2>Predictive early warning</h2>
        </div>
        <Activity size={20} />
      </div>
      <div className="prediction-grid">
        {predictions.map((prediction) => {
          const Icon = icons[prediction.impact];
          return (
            <article className="prediction-card" key={prediction.id}>
              <Icon size={19} />
              <span>{prediction.impact}</span>
              <strong>{prediction.title}</strong>
              <div className="meter"><span style={{ width: `${prediction.probability}%` }} /></div>
              <small>{prediction.probability}% probability · {prediction.projectId}</small>
              <p>{prediction.recommendation}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
