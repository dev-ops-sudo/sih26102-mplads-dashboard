import { BarChart3 } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface ChartsSectionProps {
  monthlyTrend: Array<{ month: string; spend: number; progress: number; alerts: number }>;
  sectorRisk: Array<{ sector: string; risk: number }>;
}

export function ChartsSection({ monthlyTrend, sectorRisk }: ChartsSectionProps) {
  return (
    <section className="panel chart-panel">
      <div className="panel-header">
        <div>
          <span className="eyebrow">National analytics</span>
          <h2>Spend, progress, and sector risk</h2>
        </div>
        <BarChart3 size={20} />
      </div>
      <div className="charts-grid">
        <div className="chart-card">
          <strong>Spend vs physical progress</strong>
          <ResponsiveContainer width="100%" height={230}>
            <AreaChart data={monthlyTrend}>
              <defs>
                <linearGradient id="spend" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.34} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#d8dee9" />
              <XAxis dataKey="month" tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip />
              <Area type="monotone" dataKey="spend" stroke="#06b6d4" fill="url(#spend)" strokeWidth={3} />
              <Area type="monotone" dataKey="progress" stroke="#10b981" fill="transparent" strokeWidth={3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-card">
          <strong>Risk by project type</strong>
          <ResponsiveContainer width="100%" height={230}>
            <BarChart data={sectorRisk}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d8dee9" />
              <XAxis dataKey="sector" tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip />
              <Bar dataKey="risk" fill="#fb7185" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}
