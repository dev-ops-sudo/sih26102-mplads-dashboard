import type { ReactNode } from "react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { useCountUp } from "../hooks/useCountUp";

interface KpiCardProps {
  label: string;
  value: number;
  suffix?: string;
  prefix?: string;
  trend: string;
  direction: "up" | "down";
  icon: ReactNode;
  tone: "blue" | "green" | "amber" | "red";
}

export function KpiCard({ label, value, suffix = "", prefix = "", trend, direction, icon, tone }: KpiCardProps) {
  const animated = useCountUp(value);
  const shown = Number.isInteger(value) ? Math.round(animated).toLocaleString("en-IN") : animated.toFixed(1);

  return (
    <article className={`kpi-card ${tone}`}>
      <div className="kpi-icon">{icon}</div>
      <span>{label}</span>
      <strong>
        {prefix}
        {shown}
        {suffix}
      </strong>
      <small className={direction}>
        {direction === "up" ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
        {trend}
      </small>
    </article>
  );
}
