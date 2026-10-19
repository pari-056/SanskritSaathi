import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { vi } from "vitest";
import App from "./App";
import { AuthProvider } from "./auth";
import { api, ApiError } from "./api";
import QuizRunner, { QuestionText } from "./components/QuizRunner";
import { validatePassword } from "./pages/AuthPages";

type Handler = (body: any, url: string) => { status?: number; json?: unknown };

function mockFetch(routes: Record<string, Handler>) {
  const calls: { method: string; url: string; body: any; headers: Record<string, string> }[] = [];
  vi.stubGlobal("fetch", vi.fn(async (url: string, init?: RequestInit) => {
    const method = init?.method ?? "GET";
    const body = init?.body ? JSON.parse(init.body as string) : undefined;
    calls.push({ method, url, body, headers: (init?.headers ?? {}) as Record<string, string> });
    const key = `${method} ${url.split("?")[0]}`;
    const h = routes[key];
    if (!h) return new Response(JSON.stringify({ detail: `no mock for ${key}` }), { status: 500 });
    const r = h(body, url);
    return new Response(r.status === 204 ? null : JSON.stringify(r.json ?? {}), { status: r.status ?? 200 });
  }));
  return calls;
}

function renderApp(path = "/") {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}><MemoryRouter initialEntries={[path]}><AuthProvider><App /></AuthProvider></MemoryRouter></QueryClientProvider>,
  );
}

afterEach(() => { vi.unstubAllGlobals(); });

describe("api client", () => {
  it("sends the CSRF header and credentials, and maps validation errors", async () => {
    const calls = mockFetch({ "POST /api/x": () => ({ status: 422, json: { detail: [{ loc: ["body", "password"], msg: "too short" }] } }) });
    await expect(api.post("/api/x", { a: 1 })).rejects.toMatchObject({ status: 422, message: "password: too short" });
    expect(calls[0].headers["X-Requested-With"]).toBe("saathi");
  });
  it("reports network failures clearly", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("offline"); }));
    await expect(api.get("/api/y")).rejects.toBeInstanceOf(ApiError);
    await expect(api.get("/api/y")).rejects.toThrow(/reach the server/);
  });
});

describe("password validation", () => {
  it("enforces 8+ characters", () => {
    expect(validatePassword("short")).toMatch(/at least 8/);
    expect(validatePassword("long-enough")).toBeNull();
  });
});

describe("routing and auth", () => {
  it("redirects signed-out visitors to the login page", async () => {
    mockFetch({ "GET /api/auth/me": () => ({ status: 401, json: { detail: "Not signed in" } }) });
    renderApp("/learn");
    expect(await screen.findByRole("heading", { name: /welcome back/i })).toBeInTheDocument();
  });

  it("validates the login form before calling the server", async () => {
    const calls = mockFetch({ "GET /api/auth/me": () => ({ status: 401, json: { detail: "x" } }) });
    renderApp("/login");
    const user = userEvent.setup();
    await user.click(await screen.findByRole("button", { name: /sign in/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/valid email/i);
    expect(calls.filter((c) => c.url === "/api/auth/login")).toHaveLength(0);
  });

  it("shows the server's generic error on a bad login", async () => {
    mockFetch({
      "GET /api/auth/me": () => ({ status: 401, json: { detail: "x" } }),
      "POST /api/auth/login": () => ({ status: 401, json: { detail: "Incorrect email or password." } }),
    });
    renderApp("/login");
    const user = userEvent.setup();
    await user.type(await screen.findByLabelText(/email/i), "a@example.com");
    await user.type(screen.getByLabelText(/password/i), "wrong-password");
    await user.click(screen.getByRole("button", { name: /sign in/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Incorrect email or password.");
  });

  it("registers (client-side checks), then lands on the home page", async () => {
    const calls = mockFetch({
      "GET /api/auth/me": () => ({ status: 401, json: { detail: "x" } }),
      "POST /api/auth/register": (b) => ({ status: 201, json: { id: 1, email: b.email, display_name: b.display_name } }),
      "GET /api/progress": () => ({ json: { display_name: "Asha", xp: 0, level: 1, xp_into_level: 0, xp_per_level: 150, streak: 0, best_streak: 0, xp_today: 0, daily_goal: 30, daily_done: false, cards_due: 0, cards_mastered: 0, lessons_completed: 0, lessons_total: 28, next_lesson: "1.1", placement: null, badges: [], all_badges: [], skills: [] } }),
      "GET /api/levels": () => ({ json: [{ level: 1, title_sa: "प्रारम्भः", title: "Foundations", cefr: "A1", description: "d", completed: 0, lessons: [{ id: "1.1", title: "Vowels", title_sa: "स्वराः", unit: "u", minutes: 12, summary: "s", opened: false, completed: false, best: 0, attempts: 0 }] }] }),
    });
    renderApp("/register");
    const user = userEvent.setup();
    await user.type(await screen.findByLabelText(/^name/i), "Asha");
    await user.type(screen.getByLabelText(/^email/i), "asha@example.com");
    await user.type(screen.getByLabelText(/^password/i), "longenough1");
    await user.type(screen.getByLabelText(/confirm password/i), "different123");
    await user.click(screen.getByRole("button", { name: /create account/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/don't match/i);
    await user.clear(screen.getByLabelText(/confirm password/i));
    await user.type(screen.getByLabelText(/confirm password/i), "longenough1");
    await user.click(screen.getByRole("button", { name: /create account/i }));
    expect(await screen.findByText(/नमस्ते, Asha/)).toBeInTheDocument();
    expect(calls.find((c) => c.url === "/api/auth/register")?.body).toEqual({ email: "asha@example.com", password: "longenough1", display_name: "Asha" });
  });
});

describe("QuizRunner", () => {
  const session = { id: "q1", kind: "lesson", lesson_id: "1.1", total: 2, questions: [
    { index: 0, prompt: "Pick the **long** vowel ī", options: ["इ", "ई"], hint: "" },
    { index: 1, prompt: "Pick ai", options: ["ऐ", "ए"], hint: "" },
  ] };

  function setup() {
    const calls = mockFetch({
      "POST /api/quizzes": () => ({ status: 201, json: session }),
      "POST /api/quizzes/q1/answer": (b) => ({ json: { correct: b.index === 0 ? b.pick === 1 : false, picked: b.pick, correct_index: b.index === 0 ? 1 : 0, explanation: "because" } }),
      "POST /api/quizzes/q1/finish": () => ({ json: { correct: 1, total: 2, xp: 5, passed: false, newly_completed: false, missed: [{ prompt: "Pick ai", chosen: "ए", correct: "ऐ", explanation: "ai is a diphthong" }] } }),
    });
    const qc = new QueryClient();
    render(<QueryClientProvider client={qc}><QuizRunner start={{ kind: "lesson", lesson_id: "1.1" }} startLabel="Begin" /></QueryClientProvider>);
    return calls;
  }

  it("walks through questions, shows server feedback and a summary", async () => {
    const calls = setup();
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Begin" }));
    expect(await screen.findByText("long")).toBeInTheDocument(); // **bold** rendered as <strong>
    const check = screen.getByRole("button", { name: /check answer/i });
    expect(check).toBeDisabled();
    await user.click(screen.getByLabelText("ई"));
    await user.click(check);
    expect(await screen.findByText(/Correct!/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /next question/i }));
    await user.click(await screen.findByLabelText("ए"));
    await user.click(screen.getByRole("button", { name: /check answer/i }));
    expect(await screen.findByText(/Not quite/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /see results/i }));
    const result = await screen.findByTestId("quiz-result");
    expect(within(result).getByText(/1 \/ 2 correct \(50%\)/)).toBeInTheDocument();
    expect(within(result).getByText(/Score 70% or more/)).toBeInTheDocument();
    expect(within(result).getByText(/ai is a diphthong/)).toBeInTheDocument();
    expect(calls.filter((c) => c.url.endsWith("/answer"))).toHaveLength(2);
  });

  it("surfaces start failures without crashing", async () => {
    mockFetch({ "POST /api/quizzes": () => ({ status: 404, json: { detail: "Lesson not found" } }) });
    render(<QueryClientProvider client={new QueryClient()}><QuizRunner start={{ kind: "lesson", lesson_id: "9.9" }} /></QueryClientProvider>);
    await userEvent.setup().click(screen.getByRole("button", { name: "Start" }));
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Lesson not found"));
  });
});

describe("QuestionText", () => {
  it("renders emphasis without injecting HTML", () => {
    render(<QuestionText text={'Read **क** and *ka* <img src=x onerror=alert(1)>'} />);
    expect(screen.getByText("क").tagName).toBe("STRONG");
    expect(document.querySelector("img")).toBeNull();
  });
});

describe("Verb explorer", () => {
  it("searches a root and shows its paradigm, switching voice", async () => {
    const table = (voice: string, tense: string) => ({
      key: "01.1137", root: "गम्", iast: "gam", gana: 1, gana_name: "bhvādi", meaning: "गतौ", padas: "P", voice, tense,
      rows: [{ person: 3, person_sa: "प्रथम", sg: voice === "pass" ? "गम्यते" : "गच्छति", du: "गच्छतः", pl: "गच्छन्ति" },
             { person: 2, person_sa: "मध्यम", sg: "गच्छसि", du: "गच्छथः", pl: "गच्छथ" },
             { person: 1, person_sa: "उत्तम", sg: "गच्छामि", du: "गच्छावः", pl: "गच्छामः" }],
      available: { act: [{ id: "lat", label: "present (laṭ)" }], pass: [{ id: "lat", label: "present (laṭ)" }] },
      voice_labels: { act: "Active (parasmaipada)", pass: "Passive" },
      principal_parts: { "past participle (kta)": ["गत"], "infinitive": ["गन्तुम्"] }, athematic_or_listed: false,
    });
    mockFetch({
      "GET /api/lab/verbs": () => ({ json: { total: 1, results: [{ key: "01.1137", root: "गम्", iast: "gam", gana: 1, gana_name: "bhvādi", meaning: "गतौ", padas: "P" }] } }),
      "GET /api/lab/verbs/01.1137": (_b, url) => ({ json: table(new URL(url, "http://x").searchParams.get("voice") ?? "act", "lat") }),
    });
    const { VerbsTab } = await import("./pages/Lab");
    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(<QueryClientProvider client={qc}><VerbsTab /></QueryClientProvider>);
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /search roots/i }));
    await user.click(await screen.findByRole("button", { name: /gam.*bhvādi/ }));
    expect(await screen.findByText("गच्छति")).toBeInTheDocument();
    expect(screen.getByText("गन्तुम्")).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText(/voice/i), "pass");
    expect(await screen.findByText("गम्यते")).toBeInTheDocument();
  });
});
