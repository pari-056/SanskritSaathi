import { useEffect, useRef, useState, type FormEvent } from "react";
import { api } from "../api";
import type { ChatMsg, ChatSettings } from "../types";
import { ErrorBox } from "./ui";

interface Props {
  lessonId?: string | null;
  settings: ChatSettings;
  greeting?: string;
  suggestions?: string[];
}

export default function ChatPanel({ lessonId, settings, greeting, suggestions = [] }: Props) {
  const [msgs, setMsgs] = useState<ChatMsg[]>(greeting ? [{ role: "assistant", content: greeting }] : []);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [demo, setDemo] = useState(false);
  const end = useRef<HTMLDivElement>(null);

  useEffect(() => { end.current?.scrollIntoView?.({ behavior: "smooth" }); }, [msgs, busy]);

  async function send(content: string) {
    const trimmed = content.trim();
    if (!trimmed || busy) return;
    const next: ChatMsg[] = [...msgs, { role: "user", content: trimmed }];
    setMsgs(next); setText(""); setBusy(true); setError(null);
    try {
      const history = next.filter((m) => m.content).slice(-20).map(({ role, content }) => ({ role, content }));
      const r = await api.post<{ reply: string; tool_calls: string[]; demo: boolean }>("/api/tutor/chat", {
        messages: history, lesson_id: lessonId ?? null, ...settings,
      });
      setDemo(r.demo);
      setMsgs([...next, { role: "assistant", content: r.reply, tools: r.tool_calls }]);
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }

  function submit(e: FormEvent) { e.preventDefault(); void send(text); }

  return (
    <div className="chat">
      {demo && <div className="alert alert-info">Demo mode: the server has no Gemini key, so replies come from the offline rule engine.</div>}
      {suggestions.length > 0 && (
        <div className="chips">{suggestions.map((s) => <button key={s} className="chip chip-btn" onClick={() => void send(s)} disabled={busy}>{s}</button>)}</div>
      )}
      <div className="chat-log" aria-live="polite">
        {msgs.map((m, k) => (
          <div key={k} className={m.role === "user" ? "bubble user" : "bubble bot"}>
            <div className="bubble-text">{m.content}</div>
            {m.tools && m.tools.length > 0 && (
              <details className="small"><summary>🔧 Verified checks used ({m.tools.length})</summary>
                <ul>{m.tools.map((t, j) => <li key={j}><code>{t}</code></li>)}</ul></details>
            )}
          </div>
        ))}
        {busy && <div className="bubble bot muted">Thinking…</div>}
        <div ref={end} />
      </div>
      <ErrorBox error={error} />
      <form className="chat-form" onSubmit={submit}>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Type in Sanskrit or English…" maxLength={4000} aria-label="Message" />
        <button className="btn btn-primary" disabled={busy || !text.trim()}>Send</button>
      </form>
    </div>
  );
}
