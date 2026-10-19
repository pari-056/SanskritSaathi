import { useState, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function Spinner({ label = "Loading…" }: { label?: string }) {
  return <div className="spinner" role="status" aria-live="polite">{label}</div>;
}

export function ErrorBox({ error }: { error: unknown }) {
  if (!error) return null;
  const msg = error instanceof Error ? error.message : String(error);
  return <div className="alert alert-error" role="alert">{msg}</div>;
}

export function Bar({ value, max, label }: { value: number; max: number; label?: string }) {
  const pct = max > 0 ? Math.min(100, Math.round((value / max) * 100)) : 0;
  return (
    <div>
      {label && <div className="muted small">{label}</div>}
      <div className="bar" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
        <div className="bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function Markdown({ children }: { children: string }) {
  return <div className="md"><ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown></div>;
}

export function Tabs({ tabs, initial = 0 }: { tabs: { label: string; content: ReactNode }[]; initial?: number }) {
  const [i, setI] = useState(initial);
  return (
    <div>
      <div className="tabs" role="tablist">
        {tabs.map((t, idx) => (
          <button key={t.label} role="tab" aria-selected={idx === i} className={idx === i ? "tab active" : "tab"} onClick={() => setI(idx)}>
            {t.label}
          </button>
        ))}
      </div>
      <div role="tabpanel">{tabs[i].content}</div>
    </div>
  );
}

export function Dev({ children, big }: { children: ReactNode; big?: boolean }) {
  return <span className={big ? "dev dev-big" : "dev"} lang="sa">{children}</span>;
}

export function Stat({ label, value, sub }: { label: string; value: ReactNode; sub?: string }) {
  return (
    <div className="stat">
      <div className="muted small">{label}</div>
      <div className="stat-value">{value}</div>
      {sub && <div className="muted small">{sub}</div>}
    </div>
  );
}
