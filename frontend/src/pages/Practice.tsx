import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api";
import type { CardQueue, PlacementResult, Progress, TutorStatus } from "../types";
import QuizRunner from "../components/QuizRunner";
import { Bar, Dev, ErrorBox, Spinner, Tabs } from "../components/ui";

const FIRST_LESSON: Record<number, string> = { 1: "1.1", 2: "2.1", 3: "3.1", 4: "4.1" };
const LEVEL_NAMES = ["Foundations", "Elementary", "Intermediate", "Advanced"];

export default function Practice() {
  const status = useQuery({ queryKey: ["tutor-status"], queryFn: () => api.get<TutorStatus>("/api/tutor/status") });
  const prog = useQuery({ queryKey: ["progress"], queryFn: () => api.get<Progress>("/api/progress") });
  const ai = status.data?.ai_enabled ?? false;
  return (
    <div>
      <h2>दैनिकः अभ्यासः · Practice hub</h2>
      <Tabs tabs={[
        { label: "🎯 Daily challenge", content: (
          <div className="stack">
            {prog.data?.daily_done && <div className="alert alert-ok">Today's challenge is complete (+30 XP earned). Come back tomorrow or try a mixed review.</div>}
            <QuizRunner start={{ kind: "daily" }} startLabel="Start today's 10 questions" aiEnabled={ai}
              intro="Ten questions from the lessons you've opened. The set is the same all day, so you can retry it." />
          </div>) },
        { label: "🗂️ Flashcards", content: <Flashcards /> },
        { label: "🔁 Mixed review", content: <Review ai={ai} /> },
        { label: "🧭 Placement", content: <Placement ai={ai} saved={prog.data?.placement ?? null} /> },
        { label: "📊 Skills", content: <Skills skills={prog.data?.skills ?? []} /> },
      ]} />
    </div>
  );
}

function Review({ ai }: { ai: boolean }) {
  const [level, setLevel] = useState(2);
  const [n, setN] = useState(10);
  return (
    <div className="stack">
      <div className="row">
        <label>Include lessons up to level
          <select value={level} onChange={(e) => setLevel(Number(e.target.value))}>
            {[1, 2, 3, 4].map((l) => <option key={l} value={l}>{l} · {LEVEL_NAMES[l - 1]}</option>)}
          </select></label>
        <label>Questions: {n}<input type="range" min={5} max={20} value={n} onChange={(e) => setN(Number(e.target.value))} /></label>
      </div>
      <QuizRunner key={`${level}-${n}`} start={{ kind: "review", level, n }} startLabel="Start review" aiEnabled={ai}
        intro="A shuffled mix of hand-written and generated questions." />
    </div>
  );
}

function Placement({ ai, saved }: { ai: boolean; saved: PlacementResult | null }) {
  const [res, setRes] = useState<PlacementResult | null>(null);
  const shown = res ?? saved;
  return (
    <div className="stack">
      <QuizRunner start={{ kind: "placement" }} startLabel="Start placement test" aiEnabled={ai}
        intro="Sixteen questions across all four levels (about five minutes). It suggests where to start and won't mark lessons complete."
        onFinished={(r) => r.placement && setRes(r.placement)} />
      {shown && (
        <div className="alert alert-ok">
          Suggested starting level: <strong>{shown.recommended_level} · {LEVEL_NAMES[shown.recommended_level - 1]}</strong>{" "}
          <Link className="btn btn-small" to={`/learn/${FIRST_LESSON[shown.recommended_level]}`}>Go to Level {shown.recommended_level}</Link>
        </div>
      )}
    </div>
  );
}

function Skills({ skills }: { skills: { skill: string; weight: number }[] }) {
  if (!skills.length) return <p className="muted">Answer some questions and your weak spots will appear here.</p>;
  return (
    <div className="table-wrap"><table className="table"><thead><tr><th>Skill</th><th>Focus weight</th><th>Status</th></tr></thead>
      <tbody>{skills.map((s) => <tr key={s.skill}><td>{s.skill}</td><td>{s.weight}</td><td>{s.weight > 1.2 ? "needs work" : s.weight < 0.8 ? "solid" : "ok"}</td></tr>)}</tbody></table>
      <p className="muted small">A higher weight means you miss this more often, so it appears more in drills.</p></div>
  );
}

function Flashcards() {
  const qc = useQueryClient();
  const [lex, setLex] = useState(false);
  const [newN, setNewN] = useState(8);
  const [reverse, setReverse] = useState(false);
  const [deck, setDeck] = useState<CardQueue | null>(null);
  const [i, setI] = useState(0);
  const [show, setShow] = useState(false);
  const [tally, setTally] = useState({ again: 0, good: 0, easy: 0 });
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const info = useQuery({ queryKey: ["flashcards", lex, newN], queryFn: () => api.get<CardQueue>(`/api/flashcards/queue?lexicon=${lex}&new=${newN}`), enabled: !deck });

  async function start() {
    setError(null);
    try { setDeck(await api.get<CardQueue>(`/api/flashcards/queue?lexicon=${lex}&new=${newN}`)); setI(0); setShow(false); setTally({ again: 0, good: 0, easy: 0 }); }
    catch (e) { setError(e); }
  }
  async function grade(g: "again" | "good" | "easy") {
    if (!deck || busy) return;
    setBusy(true); setError(null);
    try {
      await api.post("/api/flashcards/review", { card_id: deck.cards[i].id, grade: g });
      setTally((t) => ({ ...t, [g]: t[g] + 1 })); setI(i + 1); setShow(false);
    } catch (e) { setError(e); } finally { setBusy(false); }
  }
  function finish() {
    setDeck(null);
    void qc.invalidateQueries({ queryKey: ["progress"] });
    void qc.invalidateQueries({ queryKey: ["flashcards"] });
  }

  if (!deck) {
    const d = info.data;
    return (
      <div className="stack">
        <label><input type="checkbox" checked={lex} onChange={(e) => setLex(e.target.checked)} /> Also introduce words from the core lexicon (nouns, verbs, particles)</label>
        <label>New cards this session: {newN}<input type="range" min={0} max={20} value={newN} onChange={(e) => setNewN(Number(e.target.value))} /></label>
        <label><input type="checkbox" checked={reverse} onChange={(e) => setReverse(e.target.checked)} /> Reverse: English → Sanskrit</label>
        {info.isLoading ? <Spinner /> : d && <p><strong>{d.due}</strong> due · <strong>{d.new}</strong> new · <strong>{d.mastered}</strong> mastered</p>}
        <ErrorBox error={error ?? info.error} />
        {d && d.cards.length === 0
          ? <p className="muted">Nothing to review yet. Open a lesson (its vocabulary becomes cards) or tick the core-lexicon box.</p>
          : <button className="btn btn-primary" onClick={() => void start()} disabled={!d}>Start flashcards</button>}
      </div>
    );
  }
  if (i >= deck.cards.length) {
    return (
      <div className="stack">
        <div className="alert alert-ok">Session complete: {tally.easy} easy · {tally.good} good · {tally.again} to repeat</div>
        <button className="btn btn-primary" onClick={finish}>Finish</button>
      </div>
    );
  }
  const c = deck.cards[i];
  const front = reverse ? <div className="card-text">{c.meaning}</div> : <><Dev big>{c.sanskrit}</Dev><div className="muted">{c.iast}</div></>;
  const back = reverse ? <><Dev big>{c.sanskrit}</Dev><div className="muted">{c.iast}</div></> : <div className="card-text">{c.meaning}</div>;
  return (
    <div className="stack">
      <Bar value={i} max={deck.cards.length} label={`Card ${i + 1} of ${deck.cards.length}`} />
      <div className="flashcard" data-testid="flashcard">{front}{show && <><hr />{back}</>}</div>
      <ErrorBox error={error} />
      {!show ? <button className="btn btn-primary" onClick={() => setShow(true)}>Show answer</button> : (
        <div className="row">
          <button className="btn" onClick={() => void grade("again")} disabled={busy}>🔁 Again</button>
          <button className="btn" onClick={() => void grade("good")} disabled={busy}>👍 Good</button>
          <button className="btn" onClick={() => void grade("easy")} disabled={busy}>⚡ Easy</button>
        </div>
      )}
    </div>
  );
}
