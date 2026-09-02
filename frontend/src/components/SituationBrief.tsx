import { FileText, Sparkles } from "lucide-react";

interface SituationBriefProps {
  changedSinceLogin: string[];
}

export function SituationBrief({ changedSinceLogin }: SituationBriefProps) {
  return (
    <section className="panel brief-panel">
      <div className="panel-header">
        <div><span className="eyebrow">AI national situation brief</span><h2>What changed since last login</h2></div>
        <Sparkles size={20} />
      </div>
      <div className="brief-body">
        <div className="brief-summary">
          <FileText size={22} />
          <p>National MPLADS risk posture is elevated in roads, health infrastructure, and school digital lab projects. AI recommends targeted district reviews before the next fund-release cycle.</p>
        </div>
        <ul>{changedSinceLogin.map((item) => <li key={item}>{item}</li>)}</ul>
      </div>
    </section>
  );
}

