import { CheckCircle2, Clock3, IndianRupee, ShieldAlert } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { AgencyIntelligence } from "./components/AgencyIntelligence";
import { AlertsCenter } from "./components/AlertsCenter";
import { AnomalyPanel } from "./components/AnomalyPanel";
import { ChartsSection } from "./components/ChartsSection";
import { DuplicateGraph } from "./components/DuplicateGraph";
import { FilterBar, type Filters } from "./components/FilterBar";
import { GeoIntelligenceMap } from "./components/GeoIntelligenceMap";
import { ImageIntelligence } from "./components/ImageIntelligence";
import { InvestigationPanel } from "./components/InvestigationPanel";
import { KpiCard } from "./components/KpiCard";
import { OngoingEventsTicker } from "./components/OngoingEventsTicker";
import { Overview } from "./components/Overview";
import { PredictiveWarnings } from "./components/PredictiveWarnings";
import { ProjectDrawer } from "./components/ProjectDrawer";
import { ProjectTable } from "./components/ProjectTable";
import { RiskScoringPanel } from "./components/RiskScoringPanel";
import { SituationBrief } from "./components/SituationBrief";
import { Timeline } from "./components/Timeline";
import { TopNav } from "./components/TopNav";
import type { Project } from "./types";
import { api } from "./lib/api";

const initialFilters: Filters = {
  states: [],
  districts: [],
  constituencies: [],
  types: [],
  statuses: [],
  risks: [],
  date: "2026-09-01"
};

function matches(values: string[], candidate: string) {
  return values.length === 0 || values.includes(candidate);
}

function App() {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [filters, setFilters] = useState<Filters>(initialFilters);
  const [search, setSearch] = useState("");
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    api.getDashboardSummary()
      .then(data => {
        setDashboardData(data);
        if (data.projects && data.projects.length > 0) {
          setSelectedProject(data.projects[0]);
        }
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    const updateProgress = () => {
      const available = document.documentElement.scrollHeight - window.innerHeight;
      setScrollProgress(available > 0 ? window.scrollY / available : 0);
    };
    updateProgress();
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress);
    return () => {
      window.removeEventListener("scroll", updateProgress);
      window.removeEventListener("resize", updateProgress);
    };
  }, []);

  const filteredProjects = useMemo(() => {
    if (!dashboardData?.projects) return [];
    const query = search.trim().toLowerCase();
    return dashboardData.projects.filter((project: Project) => {
      const searchable = `${project.title} ${project.state} ${project.district} ${project.constituency} ${project.agency} ${project.type}`.toLowerCase();
      return (
        matches(filters.states, project.state) &&
        (filters.districts.length === 0 || filters.districts.includes(project.district) || filters.districts.includes(project.city)) &&
        matches(filters.constituencies, project.constituency) &&
        matches(filters.types, project.type) &&
        matches(filters.statuses, project.status) &&
        matches(filters.risks, project.risk) &&
        (!query || searchable.includes(query))
      );
    });
  }, [filters, search, dashboardData]);

  if (loading) return <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", fontSize: "24px" }}>Loading dashboard...</div>;
  if (error) return <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", color: "red", fontSize: "24px" }}>Error: {error}</div>;
  if (!dashboardData?.projects?.length) return <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", fontSize: "24px" }}>No project data available.</div>;

  const { projects, alerts, agencies, predictions, monthlyTrend, sectorRisk, changedSinceLogin } = dashboardData;

  const focusProject = selectedProject ?? filteredProjects[0] ?? projects[0];
  const totalBudget = filteredProjects.reduce((sum: number, project: Project) => sum + project.budgetCr, 0);
  const criticalCount = filteredProjects.filter((project: Project) => project.risk === "Critical" || project.risk === "High").length;
  const avgProgress = filteredProjects.length ? filteredProjects.reduce((sum: number, project: Project) => sum + project.progress, 0) / filteredProjects.length : 0;
  const priorityActive = filters.risks.length === 2 && filters.risks.includes("High") && filters.risks.includes("Critical");

  const togglePriorityView = () => {
    setFilters((current) => ({
      ...current,
      risks: priorityActive ? [] : ["High", "Critical"]
    }));
  };

  return (
    <>
      <TopNav search={search} onSearchChange={setSearch} unreadAlerts={alerts.filter((alert: any) => alert.severity === "Critical" || alert.severity === "High").length} />
      <div className="page-progress" aria-hidden="true"><span style={{ transform: `scaleX(${scrollProgress})` }} /></div>
      <main>
        <FilterBar projects={projects} filters={filters} onFiltersChange={setFilters} />
        <OngoingEventsTicker
          projects={projects}
          alerts={alerts}
          priorityActive={priorityActive}
          onSelectProject={setSelectedProject}
          onTogglePriority={togglePriorityView}
        />
        <Overview />
        <section className="kpi-grid" aria-label="National KPI overview">
          <KpiCard label="Active projects" value={filteredProjects.length} trend="live filtered view" direction="up" icon={<CheckCircle2 size={19} />} tone="blue" />
          <KpiCard label="Budget monitored" value={totalBudget} prefix="?" suffix=" Cr" trend="+12.4 Cr exposure" direction="up" icon={<IndianRupee size={19} />} tone="green" />
          <KpiCard label="High-risk works" value={criticalCount} trend="needs review" direction="up" icon={<ShieldAlert size={19} />} tone="red" />
          <KpiCard label="Avg progress" value={avgProgress} suffix="%" trend="vs last month" direction="down" icon={<Clock3 size={19} />} tone="amber" />
        </section>

        <section className="dashboard-grid">
          <GeoIntelligenceMap projects={filteredProjects} selectedProjectId={focusProject.id} onSelectProject={setSelectedProject} />
          <SituationBrief changedSinceLogin={changedSinceLogin} />
        </section>

        <ProjectTable projects={filteredProjects} selectedProjectId={focusProject.id} onSelectProject={setSelectedProject} />

        <section className="dashboard-grid">
          <AnomalyPanel project={focusProject} />
          <RiskScoringPanel score={focusProject.riskScore} contributions={[]} />
        </section>

        <section className="dashboard-grid">
          <InvestigationPanel project={focusProject} />
          <PredictiveWarnings predictions={predictions} />
        </section>

        <section className="dashboard-grid">
          <ImageIntelligence />
          <AlertsCenter alerts={alerts} />
        </section>

        <ChartsSection monthlyTrend={monthlyTrend} sectorRisk={sectorRisk} />

        <section className="dashboard-grid">
          <AgencyIntelligence agencies={agencies} />
          <DuplicateGraph />
        </section>

        <Timeline events={[]} />
      </main>
      <ProjectDrawer project={selectedProject} onClose={() => setSelectedProject(null)} />
    </>
  );
}

export default App;
