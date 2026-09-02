import { Bell, Menu, Search, ShieldCheck, UserRound, X } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../auth/KeycloakProvider";

interface TopNavProps {
  search: string;
  onSearchChange: (value: string) => void;
  unreadAlerts: number;
}

const navItems = ["Overview", "Projects", "Risk Intelligence", "Anomalies", "Geo Intelligence", "Reports"];

export function TopNav({ search, onSearchChange, unreadAlerts }: TopNavProps) {
  const [open, setOpen] = useState(false);
  const { logout } = useAuth();

  return (
    <header className="top-nav">
      <div className="brand">
        <span className="brand-mark"><ShieldCheck size={20} /></span>
        <div><strong>MPLADS Intelligence</strong><span>SIH26102 command dashboard</span></div>
      </div>
      <nav className={open ? "nav-links open" : "nav-links"} aria-label="Primary navigation">
        {navItems.map((item) => <a href={`#${item.toLowerCase().replaceAll(" ", "-")}`} key={item}>{item}</a>)}
      </nav>
      <div className="nav-actions">
        <label className="search-box">
          <Search size={16} />
          <input value={search} onChange={(event) => onSearchChange(event.target.value)} placeholder="Search projects, districts, agencies" />
        </label>
        <button className="icon-button pulse-dot" aria-label={`${unreadAlerts} unread alerts`}><Bell size={18} /><span>{unreadAlerts}</span></button>
        <button className="profile-button" aria-label="Officer profile" onClick={() => logout()}><UserRound size={18} /><span>Logout</span></button>
        <button className="mobile-menu" onClick={() => setOpen((value) => !value)} aria-label="Toggle navigation">{open ? <X size={20} /> : <Menu size={20} />}</button>
      </div>
    </header>
  );
}

