import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import type { SentenceResult, TutorStatus } from "../types";
import Sentence from "../components/Sentence";
import { Dev, ErrorBox, Spinner, Tabs } from "../components/ui";

function useAction<T>() {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  async function run(fn: () => Promise<T>) {
    setBusy(true); setError(null);
    try { setData(await fn()); } catch (e) { setError(e); setData(null); } finally { setBusy(false); }
  }
  return { data, error, busy, run };
}

function SentenceTab() {
  const [text, setText] = useState("रामः विद्यालयं गच्छति।");
  const a = useAction<SentenceResult>();
  const ai = useAction<{ analysis: { devanagari: string; iast: string; translation: string; sandhi_notes: string[]; syntax_notes: string[]; ambiguities: string[]; learner_tip: string;
      tokens: { surface: string; lemma: string; part_of_speech: string; gloss: string; features: string; confidence: string }[] };
    checks: { surface: string; verdict: string; detail: string }[] }>();
  const status = useQuery({ queryKey: ["tutor-status"], queryFn: () => api.get<TutorStatus>("/api/tutor/status") });
  return (
    <div className="stack">
      <textarea value={text} onChange={(e) => setText(e.target.value)} rows={3} maxLength={500} aria-label="Sentence" />
      <div className="row">
        <button className="btn btn-primary" disabled={a.busy || !text.trim()} onClick={() => void a.run(() => api.post<SentenceResult>("/api/lab/sentence", { text }))}>Analyse sentence</button>
        {status.data?.ai_enabled && <button className="btn" disabled={ai.busy || !text.trim()} onClick={() => void ai.run(() => api.post("/api/tutor/analyze", { text }))}>{ai.busy ? "Analysing…" : "Ask AI for a cross-checked analysis"}</button>}
      </div>
      <ErrorBox error={a.error} />{a.data && <Sentence result={a.data} />}
      <ErrorBox error={ai.error} />
      {ai.data && (
        <div className="card">
          <h3><Dev>{ai.data.analysis.devanagari}</Dev> · {ai.data.analysis.iast}</h3>
          <p><em>{ai.data.analysis.translation}</em></p>
          <div className="table-wrap"><table className="table"><thead><tr><th>Word</th><th>Lemma</th><th>POS</th><th>Meaning</th><th>Features</th><th>AI confidence</th><th>Cross-check</th></tr></thead>
            <tbody>{ai.data.analysis.tokens.map((t, k) => {
              const c = ai.data!.checks[k];
              const label = c?.verdict === "verified" ? "✅ verified" : c?.verdict === "disagrees" ? "⚠️ differs from rule engine" : "❔ AI-only";
              return <tr key={k}><td className="dev">{t.surface}</td><td className="dev">{t.lemma}</td><td>{t.part_of_speech}</td><td>{t.gloss}</td><td>{t.features}</td><td>{t.confidence}</td><td title={c?.detail}>{label}</td></tr>;
            })}</tbody></table></div>
          {[["Sandhi", ai.data.analysis.sandhi_notes], ["Syntax", ai.data.analysis.syntax_notes], ["Ambiguities", ai.data.analysis.ambiguities]].map(([title, items]) =>
            (items as string[]).length > 0 && <div key={title as string}><strong>{title as string}</strong><ul>{(items as string[]).map((x, k) => <li key={k}>{x}</li>)}</ul></div>)}
          <div className="alert alert-info">💡 {ai.data.analysis.learner_tip}</div>
          <p className="muted small">"Verified" means the lemma agrees with the rule engine; the rest is the model's own analysis and may contain errors.</p>
        </div>
      )}
      <p className="muted small">Try: <code>अहं संस्कृतं पठामि।</code> · <code>रामेण फलं खादितम्।</code> · <code>बालकाः गच्छति।</code> (agreement error)</p>
    </div>
  );
}

function TranslitTab() {
  const [text, setText] = useState("rAmaH vidyAlayaM gacchati");
  const a = useAction<Record<string, string>>();
  return (
    <div className="stack">
      <input value={text} onChange={(e) => setText(e.target.value)} maxLength={2000} aria-label="Text to transliterate" />
      <button className="btn btn-primary" disabled={a.busy || !text.trim()} onClick={() => void a.run(() => api.post("/api/lab/transliterate", { text }))}>Convert</button>
      <ErrorBox error={a.error} />
      {a.data && <div className="stack">
        <p className="muted">Detected: <code>{a.data.detected}</code></p>
        {[["Devanagari", "devanagari"], ["IAST", "iast"], ["Harvard-Kyoto", "hk"], ["SLP1", "slp1"]].map(([label, k]) => (
          <div key={k}><div className="muted small">{label}</div><pre className="out">{a.data![k]}</pre></div>))}
      </div>}
    </div>
  );
}

function SandhiTab() {
  const [first, setFirst] = useState("रामः");
  const [second, setSecond] = useState("अस्ति");
  const [fused, setFused] = useState("तत्रेति");
  const j = useAction<{ result: { devanagari: string; iast: string }; rule: string; alternatives: { result: { devanagari: string }; rule: string }[] }>();
  const s = useAction<{ splits: string[][] }>();
  return (
    <div className="grid2">
      <div className="stack">
        <h3>Join (external sandhi)</h3>
        <input value={first} onChange={(e) => setFirst(e.target.value)} maxLength={60} aria-label="First word" />
        <input value={second} onChange={(e) => setSecond(e.target.value)} maxLength={60} aria-label="Second word" />
        <button className="btn btn-primary" disabled={j.busy} onClick={() => void j.run(() => api.post("/api/lab/sandhi/join", { first, second }))}>Join</button>
        <ErrorBox error={j.error} />
        {j.data && <div><Dev big>{j.data.result.devanagari}</Dev><div className="muted">{j.data.result.iast} · {j.data.rule}</div>
          {j.data.alternatives.map((a, k) => <div key={k} className="muted small">Also: {a.result.devanagari} — {a.rule}</div>)}</div>}
      </div>
      <div className="stack">
        <h3>Split (lexicon-constrained)</h3>
        <input value={fused} onChange={(e) => setFused(e.target.value)} maxLength={60} aria-label="Fused text" />
        <button className="btn btn-primary" disabled={s.busy} onClick={() => void s.run(() => api.post("/api/lab/sandhi/split", { text: fused }))}>Split</button>
        <ErrorBox error={s.error} />
        {s.data && (s.data.splits.length ? s.data.splits.map((sp, k) => <Dev key={k} big>{sp.join(" + ")}</Dev>)
          : <div className="alert alert-info">No split found: both parts must be forms in the built-in lexicon.</div>)}
      </div>
    </div>
  );
}

function WordTab() {
  const [text, setText] = useState("गच्छन्ति");
  const a = useAction<{ found: boolean; analyses: { lemma: string; type: string; features: string; meaning: string; note: string }[]; splits: string[][]; suggestions: string[] }>();
  return (
    <div className="stack">
      <input value={text} onChange={(e) => setText(e.target.value)} maxLength={200} aria-label="Word" />
      <button className="btn btn-primary" disabled={a.busy || !text.trim()} onClick={() => void a.run(() => api.post("/api/lab/word", { text }))}>Analyse word</button>
      <ErrorBox error={a.error} />
      {a.data && (a.data.found
        ? <div className="table-wrap"><table className="table"><thead><tr><th>Lemma</th><th>Type</th><th>Features</th><th>Meaning</th><th>Note</th></tr></thead>
            <tbody>{a.data.analyses.map((x, k) => <tr key={k}><td>{x.lemma}</td><td>{x.type}</td><td>{x.features}</td><td>{x.meaning}</td><td>{x.note}</td></tr>)}</tbody></table></div>
        : <div className="alert alert-warn">Not in the built-in lexicon.
            {a.data.splits.length > 0 && <div>Possible splits: {a.data.splits.map((s) => s.join(" + ")).join(" · ")}</div>}
            {a.data.suggestions.length > 0 && <div>Did you mean: {a.data.suggestions.join(", ")}</div>}</div>)}
    </div>
  );
}

interface Stems { stems: { key: string; label: string; meaning: string; kind: string }[]; n_forms: number; tenses: { id: string; label: string }[] }
interface Paradigm { kind: string; title: string; meaning: string;
  rows?: { person: number; person_sa: string; sg: string; du: string; pl: string }[];
  extras?: { participle: string | null; gerund: string | null; infinitive: string | null };
  tables?: { gender: string | null; gender_label: string; rows: { case: number; case_sa: string; case_en: string; sg: string; du: string; pl: string }[] }[] }

function ParadigmTab() {
  const stems = useQuery({ queryKey: ["stems"], queryFn: () => api.get<Stems>("/api/lab/stems") });
  const [key, setKey] = useState("rAma");
  const [tense, setTense] = useState("lat");
  const p = useQuery({ queryKey: ["paradigm", key, tense], queryFn: () => api.get<Paradigm>(`/api/lab/paradigm?key=${encodeURIComponent(key)}&tense=${tense}`), enabled: !!stems.data });
  if (stems.isLoading) return <Spinner />;
  return (
    <div className="stack">
      <div className="row">
        <label>Stem or root<select value={key} onChange={(e) => setKey(e.target.value)}>
          {stems.data?.stems.map((s) => <option key={s.key} value={s.key}>{s.label} · {s.meaning}</option>)}</select></label>
        {key.startsWith("√") && <label>Tense / mood<select value={tense} onChange={(e) => setTense(e.target.value)}>
          {stems.data?.tenses.map((t) => <option key={t.id} value={t.id}>{t.label}</option>)}</select></label>}
      </div>
      <ErrorBox error={p.error} />
      {p.data?.kind === "verb" && p.data.rows && (
        <div className="table-wrap"><table className="table"><thead><tr><th>Person</th><th>एकवचन</th><th>द्विवचन</th><th>बहुवचन</th></tr></thead>
          <tbody>{p.data.rows.map((r) => <tr key={r.person}><td>{r.person_sa} ({r.person})</td><td className="dev">{r.sg}</td><td className="dev">{r.du}</td><td className="dev">{r.pl}</td></tr>)}</tbody></table>
          {p.data.extras?.participle && <p className="muted small">Participle: {p.data.extras.participle} · gerund: {p.data.extras.gerund} · infinitive: {p.data.extras.infinitive}</p>}</div>
      )}
      {p.data?.tables?.map((t, k) => (
        <div key={k} className="table-wrap">{t.gender_label && <h4>{t.gender_label}</h4>}
          <table className="table"><thead><tr><th>विभक्ति</th><th>एकवचन</th><th>द्विवचन</th><th>बहुवचन</th></tr></thead>
            <tbody>{t.rows.map((r) => <tr key={r.case}><td>{r.case_sa} ({r.case_en})</td><td className="dev">{r.sg}</td><td className="dev">{r.du}</td><td className="dev">{r.pl}</td></tr>)}</tbody></table></div>))}
    </div>
  );
}

interface VerbHit { key: string; root: string; iast: string; gana: number; gana_name: string; meaning: string; padas: string }
interface VerbTable extends VerbHit {
  voice: string; tense: string; rows: { person: number; person_sa: string; sg: string; du: string; pl: string }[];
  available: Record<string, { id: string; label: string }[]>; voice_labels: Record<string, string>;
  principal_parts: Record<string, string[]>; athematic_or_listed: boolean;
}

export function VerbsTab() {
  const [q, setQ] = useState("गम्");
  const search = useAction<{ results: VerbHit[]; total: number }>();
  const [key, setKey] = useState<string | null>(null);
  const [voice, setVoice] = useState("act");
  const [tense, setTense] = useState("lat");
  const table = useQuery({
    queryKey: ["verb", key, voice, tense], enabled: !!key,
    queryFn: () => api.get<VerbTable>(`/api/lab/verbs/${encodeURIComponent(key!)}?voice=${voice}&tense=${tense}`),
  });
  const t = table.data;

  function pick(k: string) { setKey(k); setVoice("act"); setTense("lat"); }
  function changeVoice(v: string) {
    setVoice(v);
    const tenses = t?.available[v] ?? [];
    if (!tenses.some((x) => x.id === tense) && tenses.length) setTense(tenses[0].id);
  }

  return (
    <div className="stack">
      <p className="muted">Search a root in Devanagari, IAST or Harvard-Kyoto (for example <code>गम्</code>, <code>labh</code>, <code>paW</code>). Over 2,200 roots from the Dhātupāṭha are covered, each with active, middle, passive and causative forms where they exist.</p>
      <div className="row">
        <input value={q} onChange={(e) => setQ(e.target.value)} maxLength={40} aria-label="Root" onKeyDown={(e) => { if (e.key === "Enter") void search.run(() => api.get(`/api/lab/verbs?q=${encodeURIComponent(q)}`)); }} />
        <button className="btn btn-primary" disabled={search.busy || !q.trim()} onClick={() => void search.run(() => api.get(`/api/lab/verbs?q=${encodeURIComponent(q)}`))}>Search roots</button>
      </div>
      <ErrorBox error={search.error} />
      {search.data && (search.data.results.length === 0
        ? <div className="alert alert-warn">No root found.</div>
        : <div className="chips">{search.data.results.map((r) => (
            <button key={r.key} className={r.key === key ? "chip chip-btn active" : "chip chip-btn"} onClick={() => pick(r.key)}>
              √{r.root} ({r.iast}) · {r.gana_name}{r.meaning ? ` · ${r.meaning}` : ""}</button>))}
            {search.data.total > search.data.results.length && <span className="muted small">+{search.data.total - search.data.results.length} more, refine your search</span>}</div>)}
      <ErrorBox error={table.error} />
      {t && (
        <div className="stack">
          <h3>√<Dev>{t.root}</Dev> ({t.iast}) <span className="muted small">gaṇa {t.gana} · {t.gana_name}{t.meaning ? ` · ${t.meaning}` : ""}</span></h3>
          <div className="row">
            <label>Voice<select value={voice} onChange={(e) => changeVoice(e.target.value)}>
              {Object.entries(t.voice_labels).map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></label>
            <label>Tense / mood<select value={tense} onChange={(e) => setTense(e.target.value)}>
              {(t.available[voice] ?? []).map((x) => <option key={x.id} value={x.id}>{x.label}</option>)}</select></label>
          </div>
          <div className="table-wrap"><table className="table"><thead><tr><th>Person</th><th>एकवचन</th><th>द्विवचन</th><th>बहुवचन</th></tr></thead>
            <tbody>{t.rows.map((r) => <tr key={r.person}><td>{r.person_sa} ({r.person})</td><td className="dev">{r.sg || "—"}</td><td className="dev">{r.du || "—"}</td><td className="dev">{r.pl || "—"}</td></tr>)}</tbody></table></div>
          <div className="table-wrap"><table className="table"><thead><tr><th>Derived form</th><th>Stem / form</th></tr></thead>
            <tbody>{Object.entries(t.principal_parts).filter(([, v]) => v.length).map(([k, v]) => <tr key={k}><td>{k}</td><td className="dev">{v.join(" / ")}</td></tr>)}</tbody></table></div>
          <p className="muted small">Forms are generated by rule from the root's principal parts and checked against an independent Pāṇinian derivation engine. Rare roots have not been reviewed by hand.</p>
        </div>
      )}
    </div>
  );
}

interface Check { n: number; correct: number; accuracy: number; failures: Record<string, string>[] }
function SelfCheckTab() {
  const a = useAction<Record<"sandhi" | "morphology" | "index", Check>>();
  return (
    <div className="stack">
      <p className="muted">Regression check against textbook gold examples written independently of the rules.</p>
      <button className="btn btn-primary" disabled={a.busy} onClick={() => void a.run(() => api.get("/api/lab/selfcheck"))}>Run self-check</button>
      <ErrorBox error={a.error} />
      {a.data && <div className="grid3">
        {(["sandhi", "morphology", "index"] as const).map((k) => <div key={k} className="stat"><div className="muted small">{k}</div>
          <div className="stat-value">{a.data![k].correct} / {a.data![k].n}</div><div className="muted small">{Math.round(a.data![k].accuracy * 100)}%</div></div>)}
      </div>}
    </div>
  );
}

export default function Lab() {
  return (
    <div>
      <h2>Linguistics lab</h2>
      <Tabs tabs={[
        { label: "Sentence", content: <SentenceTab /> }, { label: "Word", content: <WordTab /> },
        { label: "Sandhi", content: <SandhiTab /> }, { label: "Transliterate", content: <TranslitTab /> },
        { label: "Paradigms", content: <ParadigmTab /> }, { label: "Verbs", content: <VerbsTab /> }, { label: "Self-check", content: <SelfCheckTab /> },
      ]} />
    </div>
  );
}
