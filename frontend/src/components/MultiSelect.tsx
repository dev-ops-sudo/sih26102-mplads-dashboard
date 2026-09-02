import { Check, ChevronDown, X } from "lucide-react";
import { useMemo, useState } from "react";

interface MultiSelectProps {
  label: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

export function MultiSelect({ label, options, selected, onChange }: MultiSelectProps) {
  const [open, setOpen] = useState(false);
  const labelText = useMemo(() => {
    if (selected.length === 0) return "All";
    if (selected.length === 1) return selected[0];
    return `${selected.length} selected`;
  }, [selected]);

  function toggle(value: string) {
    onChange(selected.includes(value) ? selected.filter((item) => item !== value) : [...selected, value]);
  }

  return (
    <div className="multi-select">
      <span className="filter-label">{label}</span>
      <button className="select-trigger" onClick={() => setOpen((value) => !value)} aria-expanded={open}>
        <span>{labelText}</span>
        <ChevronDown size={16} />
      </button>
      {open && (
        <div className="select-menu">
          <button className="select-option clear-option" onClick={() => onChange([])}>
            <X size={14} />
            Clear selection
          </button>
          {options.map((option) => (
            <button className="select-option" key={option} onClick={() => toggle(option)}>
              <span className={selected.includes(option) ? "checkbox checked" : "checkbox"}>
                {selected.includes(option) && <Check size={12} />}
              </span>
              {option}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
