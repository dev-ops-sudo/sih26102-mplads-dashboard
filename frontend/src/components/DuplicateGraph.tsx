import { GitBranch } from "lucide-react";

export function DuplicateGraph() {
  return (
    <section className="panel duplicate-panel">
      <div className="panel-header"><div><span className="eyebrow">Relationship graph</span><h2>Duplicate project cluster</h2></div><GitBranch size={20} /></div>
      <div className="graph-canvas" aria-label="Duplicate project relationship visualization">
        <svg viewBox="0 0 420 230">
          <line x1="210" y1="112" x2="90" y2="55" /><line x1="210" y1="112" x2="325" y2="55" /><line x1="210" y1="112" x2="100" y2="175" /><line x1="210" y1="112" x2="330" y2="175" />
          {[
            [210, 112, "Primary work", "critical"], [90, 55, "Same ward", "high"], [325, 55, "Similar BOQ", "medium"], [100, 175, "Same agency", "high"], [330, 175, "Same period", "medium"]
          ].map(([x, y, label, tone]) => (
            <g key={String(label)}><circle className={`node ${tone}`} cx={Number(x)} cy={Number(y)} r="25" /><text x={Number(x)} y={Number(y) + 44} textAnchor="middle">{String(label)}</text></g>
          ))}
        </svg>
      </div>
    </section>
  );
}
