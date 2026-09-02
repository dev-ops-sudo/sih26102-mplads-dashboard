import { CalendarDays, RotateCcw, SlidersHorizontal } from "lucide-react";
import type { Project } from "../types";
import { MultiSelect } from "./MultiSelect";

export interface Filters {
  states: string[];
  districts: string[];
  constituencies: string[];
  types: string[];
  statuses: string[];
  risks: string[];
  date: string;
}

interface FilterBarProps {
  projects: Project[];
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
}

function unique(values: string[]) {
  return Array.from(new Set(values)).sort();
}

export function FilterBar({ projects, filters, onFiltersChange }: FilterBarProps) {
  const update = (key: keyof Filters, value: string[] | string) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  return (
    <section className="filter-bar" aria-label="Dashboard filters">
      <div className="filter-heading">
        <SlidersHorizontal size={18} />
        <span>National filters</span>
      </div>
      <MultiSelect label="State" options={unique(projects.map((project) => project.state))} selected={filters.states} onChange={(value) => update("states", value)} />
      <MultiSelect label="City / District" options={unique(projects.flatMap((project) => [project.city, project.district]))} selected={filters.districts} onChange={(value) => update("districts", value)} />
      <MultiSelect label="Constituency" options={unique(projects.map((project) => project.constituency))} selected={filters.constituencies} onChange={(value) => update("constituencies", value)} />
      <MultiSelect label="Project type" options={unique(projects.map((project) => project.type))} selected={filters.types} onChange={(value) => update("types", value)} />
      <MultiSelect label="Status" options={unique(projects.map((project) => project.status))} selected={filters.statuses} onChange={(value) => update("statuses", value)} />
      <MultiSelect label="Risk" options={["Low", "Medium", "High", "Critical"]} selected={filters.risks} onChange={(value) => update("risks", value)} />
      <label className="date-filter">
        <span className="filter-label">Review date</span>
        <span>
          <CalendarDays size={15} />
          <input value={filters.date} onChange={(event) => update("date", event.target.value)} type="date" />
        </span>
      </label>
      <button className="reset-button" onClick={() => onFiltersChange({ states: [], districts: [], constituencies: [], types: [], statuses: [], risks: [], date: "2026-09-01" })}>
        <RotateCcw size={15} />
        Reset
      </button>
    </section>
  );
}
