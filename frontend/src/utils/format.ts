import type { RiskLevel } from "../types";

export function inrCr(value: number) {
  return `₹${value.toFixed(value >= 10 ? 0 : 1)} Cr`;
}

export function compactNumber(value: number) {
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 1 }).format(value);
}

export function riskClass(risk: RiskLevel) {
  return risk.toLowerCase();
}

export function formatDate(date: string) {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  }).format(new Date(date));
}
