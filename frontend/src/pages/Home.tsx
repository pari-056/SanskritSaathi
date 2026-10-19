import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import type { LevelInfo, Progress } from "../types";
import { Bar, ErrorBox, Spinner, Stat } from "../components/ui";

export default function Home() {
  const p = useQuery({ queryKey: ["progress"], queryFn: () => api.get<Progress>("/api/progress") });
  const lv = useQuery({ queryKey: ["levels"], queryFn: () => api.get<LevelInfo[]>("/api/levels") });
  if (p.isLoading || lv.isLoading) return <Spinner />;
  if (p.error || lv.error) return <ErrorBox error={p.error ?? lv.error} />;
  const prog = p.data!;
  const levels = lv.data!;
  const next = levels.flatMap((l) => l.lessons).find((l) => l.id === prog.next_lesson);

  return (
    <div className="stack">
      <section className="hero">
        <div className="eyebrow">संस्कृतसहायकः</div>
        <h1>नमस्ते, {prog.display_name}! 🙏</h1>
        <p>Learn Sanskrit from the alphabet to Pāṇini: lessons, quizzes, flashcards and an AI tutor checked by a grammar engine.</p>
      </section>

      <section className="grid4">
        <Stat label="Level" value={prog.level} sub={`${prog.xp_into_level}/${prog.xp_per_level} XP to next`} />
        <Stat label="Streak" value={`🔥 ${prog.streak}`} sub={`best ${prog.best_streak} days`} />
        <Stat label="Today" value={`${prog.xp_today} XP`} sub={`goal ${prog.daily_goal}`} />
        <Stat label="Cards due" value={prog.cards_due} sub={`${prog.cards_mastered} mastered`} />
      </section>
      <Bar value={prog.xp_today} max={prog.daily_goal} label="Daily goal" />

      <section className="card">
        <h2>Your next step</h2>
        {next ? (
          <>
            <p><strong>Lesson {next.id}: {next.title}</strong> <span className="muted">({next.title_sa}) · about {next.minutes} min</span></p>
            <p className="muted">{next.summary}</p>
            <Link className="btn btn-primary" to={`/learn/${next.id}`}>{next.opened ? "Continue lesson" : "Start lesson"}</Link>
          </>
        ) : <p>🎓 You've completed every lesson. Keep sharp with the daily challenge and flashcards.</p>}
        {!prog.placement && <p className="muted small">Not sure where to start? Take the <Link to="/practice">placement test</Link>.</p>}
        {!prog.daily_done && <p className="small">🎯 <Link to="/practice">Today's challenge</Link> is waiting (+30 XP).</p>}
      </section>

      <section className="card">
        <h2>Roadmap</h2>
        {levels.map((l) => (
          <div key={l.level} className="roadmap-row">
            <div><strong>Level {l.level} · {l.title_sa} · {l.title}</strong> <span className="muted">({l.cefr}) {l.description}</span></div>
            <Bar value={l.completed} max={l.lessons.length} label={`${l.completed}/${l.lessons.length} lessons`} />
          </div>
        ))}
      </section>

      <section className="card">
        <h2>Badges</h2>
        <div className="chips">
          {prog.all_badges.map((b) => (
            <span key={b.id} className={b.earned ? "badge earned" : "badge"} title={b.description}>{b.title}</span>
          ))}
        </div>
      </section>

      {prog.skills.filter((s) => s.weight > 1.2).length > 0 && (
        <section className="card">
          <h2>Needs practice</h2>
          <p>{prog.skills.filter((s) => s.weight > 1.2).slice(0, 5).map((s) => s.skill.replace("lesson:", "lesson ").replace("case:", "case ")).join(" · ")}</p>
        </section>
      )}
    </div>
  );
}
