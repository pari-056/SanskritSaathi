import { useState, type FormEvent, type ReactNode } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import { ErrorBox } from "../components/ui";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function AuthShell({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <div className="eyebrow">संस्कृतसहायकः</div>
        <h1>🪷 {title}</h1>
        {subtitle && <p className="muted">{subtitle}</p>}
        {children}
      </div>
    </div>
  );
}

export function validatePassword(pw: string): string | null {
  if (pw.length < 8) return "Password must be at least 8 characters.";
  if (pw.length > 128) return "Password is too long (max 128 characters).";
  return null;
}

export function LoginPage() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!EMAIL_RE.test(email)) return setError(new Error("Enter a valid email address."));
    if (!password) return setError(new Error("Enter your password."));
    setBusy(true);
    try {
      await login(email.trim(), password);
      nav("/", { replace: true });
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell title="Welcome back" subtitle="Sign in to continue your Sanskrit journey.">
      <form onSubmit={submit} noValidate>
        <label>Email<input type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label>Password<input type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
        <ErrorBox error={error} />
        <button className="btn btn-primary btn-block" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
      </form>
      <p className="small"><Link to="/forgot-password">Forgot your password?</Link></p>
      <p className="small">New here? <Link to="/register">Create an account</Link></p>
    </AuthShell>
  );
}

export function RegisterPage() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!name.trim()) return setError(new Error("Tell us what to call you."));
    if (!EMAIL_RE.test(email)) return setError(new Error("Enter a valid email address."));
    const pwErr = validatePassword(password);
    if (pwErr) return setError(new Error(pwErr));
    if (password !== confirm) return setError(new Error("Passwords don't match."));
    setBusy(true);
    try {
      await register(email.trim(), password, name.trim());
      nav("/", { replace: true });
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell title="Create your account" subtitle="Free to start. Your progress is saved to your account.">
      <form onSubmit={submit} noValidate>
        <label>Name<input autoComplete="nickname" value={name} maxLength={60} onChange={(e) => setName(e.target.value)} required /></label>
        <label>Email<input type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label>Password<input type="password" autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} required aria-describedby="pwhint" /></label>
        <div id="pwhint" className="muted small">At least 8 characters.</div>
        <label>Confirm password<input type="password" autoComplete="new-password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required /></label>
        <ErrorBox error={error} />
        <button className="btn btn-primary btn-block" disabled={busy}>{busy ? "Creating…" : "Create account"}</button>
      </form>
      <p className="small">Already have an account? <Link to="/login">Sign in</Link></p>
    </AuthShell>
  );
}

export function ForgotPage() {
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!EMAIL_RE.test(email)) return setError(new Error("Enter a valid email address."));
    setBusy(true);
    try {
      const r = await api.post<{ message: string }>("/api/auth/forgot", { email: email.trim() });
      setMsg(r.message);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell title="Reset your password" subtitle="We'll email you a link that works for one hour.">
      {msg ? <div className="alert alert-ok" role="status">{msg}</div> : (
        <form onSubmit={submit} noValidate>
          <label>Email<input type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
          <ErrorBox error={error} />
          <button className="btn btn-primary btn-block" disabled={busy}>{busy ? "Sending…" : "Send reset link"}</button>
        </form>
      )}
      <p className="small"><Link to="/login">Back to sign in</Link></p>
    </AuthShell>
  );
}

export function ResetPage() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const pwErr = validatePassword(password);
    if (pwErr) return setError(new Error(pwErr));
    if (password !== confirm) return setError(new Error("Passwords don't match."));
    setBusy(true);
    try {
      await api.post("/api/auth/reset", { token, password });
      setDone(true);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell title="Choose a new password">
      {!token ? <div className="alert alert-error">This reset link is incomplete. Request a new one.</div> : done ? (
        <div className="alert alert-ok" role="status">Password updated. <Link to="/login">Sign in</Link></div>
      ) : (
        <form onSubmit={submit} noValidate>
          <label>New password<input type="password" autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
          <label>Confirm password<input type="password" autoComplete="new-password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required /></label>
          <ErrorBox error={error} />
          <button className="btn btn-primary btn-block" disabled={busy}>{busy ? "Saving…" : "Update password"}</button>
        </form>
      )}
      <p className="small"><Link to="/forgot-password">Request a new link</Link></p>
    </AuthShell>
  );
}
