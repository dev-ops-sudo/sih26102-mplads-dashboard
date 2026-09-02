import { Images, MoveHorizontal } from "lucide-react";

export function ImageIntelligence() {
  return (
    <section className="panel image-panel">
      <div className="panel-header"><div><span className="eyebrow">Image intelligence</span><h2>Before, during, after evidence review</h2></div><Images size={20} /></div>
      <div className="image-compare">
        <div className="site-shot before"><span>Before</span></div>
        <div className="compare-handle" aria-hidden="true"><MoveHorizontal size={18} /></div>
        <div className="site-shot during"><span>During</span></div>
        <div className="site-shot after"><span>After</span></div>
      </div>
      <div className="evidence-grid"><span><strong>86%</strong> geo-tag match</span><span><strong>62%</strong> claimed progress confidence</span><span><strong>3</strong> inspection gaps</span></div>
    </section>
  );
}
