import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import type { ChatSettings, LevelInfo, TutorStatus } from "../types";
import ChatPanel from "../components/ChatPanel";
import { Spinner } from "../components/ui";

export default function Tutor() {
  const status = useQuery({ queryKey: ["tutor-status"], queryFn: () => api.get<TutorStatus>("/api/tutor/status") });
  const levels = useQuery({ queryKey: ["levels"], queryFn: () => api.get<LevelInfo[]>("/api/levels") });
  const [lesson, setLesson] = useState("");
  const [s, setS] = useState<ChatSettings>({ level: "Beginner", focus: "Conversation", language: "English with Sanskrit", use_tools: true });
  if (status.isLoading || levels.isLoading) return <Spinner />;
  const lessons = levels.data?.flatMap((l) => l.lessons) ?? [];
  const set = <K extends keyof ChatSettings>(k: K, v: ChatSettings[K]) => setS({ ...s, [k]: v });

  return (
    <div>
      <h2>संस्कृतेन सम्भाषामहे</h2>
      <p className="muted">Ask in English or Sanskrit. Sanskrit you write is checked by the rule engine before the tutor replies.
        {status.data?.ai_enabled ? ` Model: ${status.data.model}. Daily limit: ${status.data.daily_limit} messages.` : ""}</p>
      <div className="settings-row">
        <label>Context
          <select value={lesson} onChange={(e) => setLesson(e.target.value)}>
            <option value="">General</option>
            {lessons.map((l) => <option key={l.id} value={l.id}>Lesson {l.id}: {l.title}</option>)}
          </select></label>
        <label>Level
          <select value={s.level} onChange={(e) => set("level", e.target.value as ChatSettings["level"])}>
            {["Beginner", "Intermediate", "Advanced"].map((x) => <option key={x}>{x}</option>)}</select></label>
        <label>Focus
          <select value={s.focus} onChange={(e) => set("focus", e.target.value as ChatSettings["focus"])}>
            {["Conversation", "Grammar", "Vocabulary", "Translation", "Computational linguistics"].map((x) => <option key={x}>{x}</option>)}</select></label>
        <label>Language
          <select value={s.language} onChange={(e) => set("language", e.target.value as ChatSettings["language"])}>
            {["English with Sanskrit", "Mostly Sanskrit", "English"].map((x) => <option key={x}>{x}</option>)}</select></label>
        <label className="inline"><input type="checkbox" checked={s.use_tools} onChange={(e) => set("use_tools", e.target.checked)} /> Verified tools</label>
      </div>
      <ChatPanel key={lesson} lessonId={lesson || null} settings={s}
        greeting={"नमस्ते! 🙏 अहं संस्कृताभ्यासे तव साहाय्यं करिष्यामि।\n\nHello! Ask me about your lessons, a word, a sentence or grammar, or practise a conversation."}
        suggestions={lesson ? ["Summarise this lesson in 5 lines", "Quiz me on this lesson"] : ["Teach me to introduce myself", "What does गच्छति mean?", "Give me a beginner exercise"]} />
    </div>
  );
}
