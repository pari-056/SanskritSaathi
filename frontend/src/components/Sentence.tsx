import type { SentenceResult } from "../types";

export default function Sentence({ result }: { result: SentenceResult }) {
  if (!result.tokens.length) return <div className="alert alert-warn">Please enter Sanskrit text.</div>;
  return (
    <div>
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Token</th><th>IAST</th><th>Lemma</th><th>Analysis</th><th>Role</th><th>Status</th></tr></thead>
          <tbody>
            {result.tokens.map((t, k) => (
              <tr key={k}>
                <td className="dev">{t.token}</td>
                <td>{t.iast}</td>
                <td>{t.analysis?.lemma ?? "—"}</td>
                <td>{t.analysis ? `${t.analysis.pos}: ${t.analysis.features || t.analysis.gloss}` : "Not in lexicon"}
                  {t.alternatives.length > 1 && (
                    <details><summary className="small">{t.alternatives.length - 1} other reading(s)</summary>
                      <ul>{t.alternatives.map((a, j) => <li key={j} className="small">{a.lemma} · {a.pos} · {a.features}</li>)}</ul>
                    </details>
                  )}
                </td>
                <td>{t.role || "—"}</td>
                <td>{{ resolved: "✅ resolved", disambiguated: "✅ by agreement", ambiguous: "⚠️ ambiguous", unresolved: "❔ unresolved" }[t.status] ?? t.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {result.issues.map((i, k) => (
        <div key={k} className={i.severity === "error" ? "alert alert-error" : i.severity === "warning" ? "alert alert-warn" : "alert alert-info"}>
          {i.message} {i.suggestion && <strong className="dev"> {i.suggestion}</strong>}
        </div>
      ))}
      {result.notes.map((n, k) => <p key={k} className="muted small">{n}</p>)}
    </div>
  );
}
