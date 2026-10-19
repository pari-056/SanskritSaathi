import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { api } from "../api";
import type { AnswerResult, QuizResult, QuizSession, QuizStart } from "../types";
import { Bar, ErrorBox } from "./ui";

type Phase = "idle" | "loading" | "question" | "feedback" | "finishing" | "done";

interface Props {
  start: QuizStart;
  startLabel?: string;
  intro?: React.ReactNode;
  aiEnabled?: boolean;
  onFinished?: (r: QuizResult) => void;
  renderResult?: (r: QuizResult) => React.ReactNode;
}

export default function QuizRunner({ start, startLabel = "Start", intro, aiEnabled, onFinished, renderResult }: Props) {
  const qc = useQueryClient();
  const [phase, setPhase] = useState<Phase>("idle");
  const [session, setSession] = useState<QuizSession | null>(null);
  const [i, setI] = useState(0);
  const [pick, setPick] = useState<number | null>(null);
  const [fb, setFb] = useState<AnswerResult | null>(null);
  const [aiText, setAiText] = useState<string>("");
  const [aiBusy, setAiBusy] = useState(false);
  const [result, setResult] = useState<QuizResult | null>(null);
  const [error, setError] = useState<unknown>(null);

  function reset() {
    setPhase("idle"); setSession(null); setI(0); setPick(null); setFb(null); setAiText(""); setResult(null); setError(null);
  }

  async function begin() {
    setError(null);
    setPhase("loading");
    try {
      const s = await api.post<QuizSession>("/api/quizzes", start);
      setSession(s); setI(0); setPick(null); setFb(null); setAiText("");
      setPhase("question");
    } catch (e) {
      setError(e); setPhase("idle");
    }
  }

  async function check() {
    if (!session || pick === null) return;
    setError(null);
    try {
      const r = await api.post<AnswerResult>(`/api/quizzes/${session.id}/answer`, { index: session.questions[i].index, pick });
      setFb(r); setPhase("feedback");
    } catch (e) {
      setError(e);
    }
  }

  async function explain() {
    if (!session) return;
    setAiBusy(true); setError(null);
    try {
      const r = await api.post<{ explanation: string }>(`/api/quizzes/${session.id}/explain`, { index: session.questions[i].index });
      setAiText(r.explanation);
    } catch (e) {
      setError(e);
    } finally {
      setAiBusy(false);
    }
  }

  async function next() {
    if (!session) return;
    if (i + 1 < session.questions.length) {
      setI(i + 1); setPick(null); setFb(null); setAiText(""); setPhase("question");
      return;
    }
    setPhase("finishing");
    try {
      const r = await api.post<QuizResult>(`/api/quizzes/${session.id}/finish`);
      setResult(r); setPhase("done");
      void qc.invalidateQueries({ queryKey: ["progress"] });
      void qc.invalidateQueries({ queryKey: ["levels"] });
      void qc.invalidateQueries({ queryKey: ["lesson"] });
      void qc.invalidateQueries({ queryKey: ["flashcards"] });
      onFinished?.(r);
    } catch (e) {
      setError(e); setPhase("feedback");
    }
  }

  if (phase === "idle" || phase === "loading") {
    return (
      <div className="quiz">
        {intro && <div className="muted">{intro}</div>}
        <ErrorBox error={error} />
        <button className="btn btn-primary" onClick={() => void begin()} disabled={phase === "loading"}>
          {phase === "loading" ? "Preparing…" : startLabel}
        </button>
      </div>
    );
  }

  if (phase === "done" && result) {
    const pct = Math.round((result.correct / result.total) * 100);
    return (
      <div className="quiz" data-testid="quiz-result">
        <h3>{pct >= 70 ? "🎉" : "💪"} {result.correct} / {result.total} correct ({pct}%)</h3>
        {result.xp > 0 && (
          <div className="alert alert-ok" role="status">
            +{result.xp} XP{result.daily_bonus ? ` (includes +${result.daily_bonus} daily bonus)` : ""}
            {result.newly_completed ? " · lesson completed! 🎓" : ""}
          </div>
        )}
        {session?.kind === "lesson" && !result.passed && <div className="alert alert-warn">Score 70% or more to complete the lesson.</div>}
        {renderResult?.(result)}
        {result.missed.length > 0 && (
          <details open>
            <summary>Review {result.missed.length} missed question{result.missed.length > 1 ? "s" : ""}</summary>
            <ul className="missed">
              {result.missed.map((m, k) => (
                <li key={k}>
                  <strong>{m.prompt}</strong><br />
                  You chose: {m.chosen} · Correct: <strong>{m.correct}</strong><br />
                  <span className="muted">{m.explanation}</span>
                </li>
              ))}
            </ul>
          </details>
        )}
        <button className="btn" onClick={reset}>Try again</button>
      </div>
    );
  }

  const q = session!.questions[i];
  const locked = phase === "feedback" || phase === "finishing";
  const last = i + 1 === session!.questions.length;
  return (
    <div className="quiz">
      <Bar value={i} max={session!.questions.length} label={`Question ${i + 1} of ${session!.questions.length}`} />
      <p className="q-prompt"><QuestionText text={q.prompt} /></p>
      <div className="options" role="radiogroup" aria-label="Answer options">
        {q.options.map((opt, k) => {
          let cls = "option";
          if (locked && fb) {
            if (k === fb.correct_index) cls += " correct";
            else if (k === fb.picked) cls += " wrong";
          } else if (pick === k) cls += " selected";
          return (
            <label key={k} className={cls}>
              <input type="radio" name={`q${q.index}`} checked={pick === k} disabled={locked} onChange={() => setPick(k)} />
              <span className="dev-inline">{opt}</span>
            </label>
          );
        })}
      </div>
      {q.hint && !locked && <details><summary>Hint</summary><p className="muted">{q.hint}</p></details>}
      <ErrorBox error={error} />
      {!locked ? (
        <button className="btn btn-primary" onClick={() => void check()} disabled={pick === null}>Check answer</button>
      ) : fb && (
        <div>
          <div className={fb.correct ? "alert alert-ok" : "alert alert-error"} role="status">
            {fb.correct ? "✅ Correct! " : "❌ Not quite. "}<QuestionText text={fb.explanation} />
          </div>
          {!fb.correct && aiEnabled && !aiText && (
            <button className="btn" onClick={() => void explain()} disabled={aiBusy}>{aiBusy ? "Thinking…" : "💡 Explain with AI"}</button>
          )}
          {aiText && <div className="alert alert-info">{aiText}</div>}
          <button className="btn btn-primary" onClick={() => void next()} disabled={phase === "finishing"}>
            {last ? "See results" : "Next question →"}
          </button>
        </div>
      )}
    </div>
  );
}

/** Renders **bold** and *italic* from the question text without using raw HTML. */
export function QuestionText({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g).filter(Boolean);
  return (
    <>
      {parts.map((p, k) =>
        p.startsWith("**") ? <strong key={k}>{p.slice(2, -2)}</strong>
        : p.startsWith("*") && p.length > 2 ? <em key={k}>{p.slice(1, -1)}</em>
        : <span key={k}>{p}</span>)}
    </>
  );
}
