export interface User { id: number; email: string; display_name: string }

export interface LessonSummary {
  id: string; title: string; title_sa: string; unit: string; minutes: number; summary: string;
  opened: boolean; completed: boolean; best: number; attempts: number;
}
export interface LevelInfo {
  level: number; title_sa: string; title: string; cefr: string; description: string;
  completed: number; lessons: LessonSummary[];
}
export interface Lesson {
  id: string; level: number; unit: string; title: string; title_sa: string; minutes: number; summary: string; body: string;
  vocab: { sanskrit: string; iast: string; meaning: string }[];
  examples: { sanskrit: string; iast: string; translation: string; analysable: boolean }[];
  has_practice: boolean; prev: string | null; next: string | null;
  state: { opened: boolean; completed: boolean; best: number; attempts: number };
}
export interface BadgeInfo { id: string; title: string; description: string; earned?: boolean }
export interface Progress {
  display_name: string; xp: number; level: number; xp_into_level: number; xp_per_level: number;
  streak: number; best_streak: number; xp_today: number; daily_goal: number; daily_done: boolean;
  cards_due: number; cards_mastered: number; lessons_completed: number; lessons_total: number;
  next_lesson: string | null; placement: PlacementResult | null;
  badges: BadgeInfo[]; all_badges: BadgeInfo[]; skills: { skill: string; weight: number }[];
}
export interface PlacementResult {
  recommended_level: number; accuracy: Record<string, number>; counts: Record<string, [number, number]>;
}

export type QuizKind = "lesson" | "practice" | "daily" | "review" | "placement" | "script";
export interface QuizStart { kind: QuizKind; lesson_id?: string; level?: number; n?: number; script_kinds?: string[] }
export interface QuizQuestion { index: number; prompt: string; options: string[]; hint: string }
export interface QuizSession { id: string; kind: QuizKind; lesson_id: string | null; total: number; questions: QuizQuestion[] }
export interface AnswerResult { correct: boolean; picked: number; correct_index: number; explanation: string }
export interface QuizResult {
  correct: number; total: number; xp: number; passed: boolean; newly_completed: boolean; daily_bonus?: number;
  placement?: PlacementResult;
  missed: { prompt: string; chosen: string; correct: string; explanation: string }[];
}

export interface Card { id: string; sanskrit: string; iast: string; meaning: string; kind: string }
export interface CardQueue { cards: Card[]; due: number; new: number; mastered: number }

export interface Reading {
  lemma: string; pos: string; features: string; meaning?: string;
}
export interface TokenRow {
  token: string; iast: string; status: string; role: string;
  analysis: { surface: string; lemma: string; pos: string; features: string; gloss: string } | null;
  alternatives: Reading[]; possible_sandhi_splits: string[][];
}
export interface SentenceResult {
  text: string; tokens: TokenRow[]; issues: { severity: "error" | "warning" | "info"; message: string; suggestion: string }[];
  notes: string[];
}

export interface ChatMsg { role: "user" | "assistant"; content: string; tools?: string[] }
export interface ChatSettings {
  level: "Beginner" | "Intermediate" | "Advanced";
  focus: "Conversation" | "Grammar" | "Vocabulary" | "Translation" | "Computational linguistics";
  language: "English with Sanskrit" | "Mostly Sanskrit" | "English";
  use_tools: boolean;
}
export interface TutorStatus { ai_enabled: boolean; model: string | null; daily_limit: number }
