import { NavLink, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { api } from "../api";
import { useAuth } from "../auth";
import type { Progress } from "../types";

const links = [
  ["/", "Home", "🏠"], ["/learn", "Learn", "📚"], ["/script", "Script", "🔤"],
  ["/practice", "Practice", "🎯"], ["/tutor", "Tutor", "💬"], ["/lab", "Lab", "🧪"],
] as const;

export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const { data: p } = useQuery({ queryKey: ["progress"], queryFn: () => api.get<Progress>("/api/progress") });
  return (
    <div className="shell">
      <header className="topbar">
        <Link to="/" className="brand" aria-label="Sanskrit Saathi home">🪷 <span>Sanskrit Saathi</span></Link>
        <nav className="nav" aria-label="Main">
          {links.map(([to, label, icon]) => (
            <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => (isActive ? "navlink active" : "navlink")}>
              <span aria-hidden>{icon}</span> {label}
            </NavLink>
          ))}
        </nav>
        <div className="userbox">
          {p && <span className="chip" title="Level · XP · streak">Lv {p.level} · {p.xp} XP · 🔥 {p.streak}</span>}
          <Link to="/settings" className="navlink">{user?.display_name}</Link>
          <button className="btn btn-ghost" onClick={() => void logout()}>Sign out</button>
        </div>
      </header>
      <main className="main">{children}</main>
      <footer className="footer muted small">
        Sanskrit Saathi · AI features use the Gemini API; your messages are sent to Google. Rule-based results cover a limited lexicon, so verify before scholarly use.
      </footer>
    </div>
  );
}
