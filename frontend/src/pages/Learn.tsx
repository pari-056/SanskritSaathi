import { useEffect, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api";
import type { Lesson, LevelInfo, Progress, SentenceResult, TutorStatus } from "../types";
import ChatPanel from "../components/ChatPanel";
import QuizRunner from "../components/QuizRunner";
import Sentence from "../components/Sentence";
import { Dev, ErrorBox, Markdown, Spinner, Tabs } from "../components/ui";

export default function Learn() {
  const { lessonId } = useParams();
  const levels = useQuery({ queryKey: ["levels"], queryFn: () => api.get<LevelInfo[]>("/api/levels") });
  const prog = useQuery({ queryKey: ["progress"], queryFn: () => api.get<Progress>("/api/progress") });
  if (levels.isLoading || prog.isLoading) return <Spinner />;
  if (levels.error) return <ErrorBox error={levels.error} />;
  if (!lessonId) return <Navigate to={`/learn/${prog.data?.next_lesson ?? "1.1"}`} replace />;
  const lessonLevel = Number(lessonId.split(".")[0]);

  return (
    <div className="learn">
      <aside className="sidebar" aria-label="Lessons">
        {levels.data!.map((l) => (
          <details key={l.level} open={l.level === lessonLevel}>
            <summary><strong>Level {l.level} · {l.title}</strong> <span className="muted small">{l.completed}/{l.lessons.length}</span></summary>
            <ul className="lesson-list">
              {l.lessons.map((x) => (
                <li key={x.id}>
                  <Link className={x.id === lessonId ? "lesson-link active" : "lesson-link"} to={`/learn/${x.id}`}>
                    <span aria-hidden>{x.completed ? "✅" : x.id === lessonId ? "▶️" : "⭕"}</span> {x.id} {x.title}
                  </Link>
                </li>
              ))}
            </ul>
          </details>
        ))}
      </aside>
      <section className="lesson-pane"><LessonView id={lessonId} /></section>
    </div>
  );
}

function LessonView({ id }: { id: string }) {
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["lesson", id], queryFn: () => api.get<Lesson>(`/api/lessons/${id}`) });
  const status = useQuery({ queryKey: ["tutor-status"], queryFn: () => api.get<TutorStatus>("/api/tutor/status") });

  useEffect(() => {
    api.post(`/api/lessons/${id}/open`).then(() => qc.invalidateQueries({ queryKey: ["levels"] })).catch(() => undefined);
  }, [id, qc]);

  if (q.isLoading) return <Spinner />;
  if (q.error) return <ErrorBox error={q.error} />;
  const l = q.data!;
  const ai = status.data?.ai_enabled ?? false;

  return (
    <div>
      <h2>Lesson {l.id} · {l.title}</h2>
      <div className="chips">
        <span className="pill dev">{l.title_sa}</span><span className="pill">~{l.minutes} min</span><span className="pill">Level {l.level}</span>
        {l.state.completed && <span className="pill ok">✅ completed</span>}
        {l.state.attempts > 0 && <span className="pill">best {Math.round(l.state.best * 100)}%</span>}
      </div>
      <p className="muted">{l.summary}</p>
      <Tabs
        tabs={[
          { label: "📖 Lesson", content: <LessonBody l={l} /> },
          { label: "🧪 Practice", content: l.has_practice
              ? <QuizRunner key={`p${id}`} start={{ kind: "practice", lesson_id: id }} startLabel="Start practice" aiEnabled={ai}
                  intro="Fresh generated questions on this lesson's topic. Each correct answer earns XP." />
              : <p className="muted">This lesson has no generated practice. Try the quiz.</p> },
          { label: "📝 Quiz", content: <QuizRunner key={`q${id}`} start={{ kind: "lesson", lesson_id: id }} startLabel="Start lesson quiz" aiEnabled={ai}
              intro={l.state.completed ? "✅ Completed. Retake any time to improve your best score." : "Score 70% or more to complete this lesson."} /> },
          { label: "💬 Ask the tutor", content: <ChatPanel key={`c${id}`} lessonId={id}
              settings={{ level: "Beginner", focus: "Grammar", language: "English with Sanskrit", use_tools: true }}
              suggestions={["Summarise this lesson in 5 lines", "Quiz me on this lesson", "Give me 3 example sentences"]} /> },
        ]}
      />
    </div>
  );
}

function LessonBody({ l }: { l: Lesson }) {
  return (
    <div>
      <Markdown>{l.body}</Markdown>
      {l.vocab.length > 0 && (
        <>
          <h3>Vocabulary</h3>
          <div className="table-wrap"><table className="table"><thead><tr><th>Sanskrit</th><th>IAST</th><th>Meaning</th></tr></thead>
            <tbody>{l.vocab.map((v) => <tr key={v.sanskrit}><td><Dev>{v.sanskrit}</Dev></td><td>{v.iast}</td><td>{v.meaning}</td></tr>)}</tbody></table></div>
          <p className="muted small">These words are added to your flashcards.</p>
        </>
      )}
      {l.examples.length > 0 && (
        <>
          <h3>Examples</h3>
          {l.examples.map((e) => <Example key={e.sanskrit} e={e} />)}
        </>
      )}
      <div className="row-between">
        {l.prev ? <Link className="btn" to={`/learn/${l.prev}`}>← {l.prev}</Link> : <span />}
        {l.next ? <Link className="btn btn-primary" to={`/learn/${l.next}`}>{l.next} →</Link> : <span />}
      </div>
    </div>
  );
}

function Example({ e }: { e: Lesson["examples"][number] }) {
  const [res, setRes] = useState<SentenceResult | null>(null);
  const [err, setErr] = useState<unknown>(null);
  async function analyse() {
    setErr(null);
    try { setRes(await api.post<SentenceResult>("/api/lab/sentence", { text: e.sanskrit })); } catch (x) { setErr(x); }
  }
  return (
    <div className="example">
      <Dev big>{e.sanskrit}</Dev>
      <div className="muted">{e.iast && `${e.iast} · `}{e.translation}</div>
      {e.analysable && !res && <button className="btn btn-small" onClick={() => void analyse()}>Analyse</button>}
      <ErrorBox error={err} />
      {res && <Sentence result={res} />}
    </div>
  );
}
