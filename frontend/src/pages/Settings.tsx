import { useState, type ChangeEvent, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { api, download } from "../api";
import { useAuth } from "../auth";
import { ErrorBox } from "../components/ui";
import { validatePassword } from "./AuthPages";

export default function Settings() {
  const { user, setUser } = useAuth();
  const nav = useNavigate();
  const qc = useQueryClient();
  const [cur, setCur] = useState("");
  const [next, setNext] = useState("");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState<unknown>(null);
  const [delPw, setDelPw] = useState("");
  const [delErr, setDelErr] = useState<unknown>(null);
  const [ioMsg, setIoMsg] = useState("");
  const [ioErr, setIoErr] = useState<unknown>(null);

  async function changePw(e: FormEvent) {
    e.preventDefault(); setErr(null); setMsg("");
    const v = validatePassword(next);
    if (v) return setErr(new Error(v));
    try { await api.post("/api/auth/change-password", { current_password: cur, new_password: next }); setMsg("Password changed."); setCur(""); setNext(""); }
    catch (x) { setErr(x); }
  }
  async function exportData() {
    setIoErr(null);
    try { download(`saathi_progress_${new Date().toISOString().slice(0, 10)}.json`, await api.get("/api/progress/export")); } catch (x) { setIoErr(x); }
  }
  async function importData(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    setIoErr(null); setIoMsg("");
    try {
      const data = JSON.parse(await f.text());
      await api.post("/api/progress/import", data);
      await qc.invalidateQueries();
      setIoMsg("Progress restored.");
    } catch (x) { setIoErr(x instanceof SyntaxError ? new Error("That file isn't valid JSON.") : x); }
    e.target.value = "";
  }
  async function del(e: FormEvent) {
    e.preventDefault(); setDelErr(null);
    if (!window.confirm("Delete your account and all progress? This cannot be undone.")) return;
    try { await api.post("/api/auth/delete-account", { password: delPw }); qc.clear(); setUser(null); nav("/login", { replace: true }); }
    catch (x) { setDelErr(x); }
  }

  return (
    <div className="stack narrow">
      <h2>Account</h2>
      <div className="card"><p><strong>{user?.display_name}</strong><br /><span className="muted">{user?.email}</span></p></div>
      <form className="card" onSubmit={changePw} noValidate>
        <h3>Change password</h3>
        <label>Current password<input type="password" autoComplete="current-password" value={cur} onChange={(e) => setCur(e.target.value)} /></label>
        <label>New password<input type="password" autoComplete="new-password" value={next} onChange={(e) => setNext(e.target.value)} /></label>
        <ErrorBox error={err} />{msg && <div className="alert alert-ok" role="status">{msg}</div>}
        <button className="btn btn-primary">Update password</button>
      </form>
      <div className="card">
        <h3>Your data</h3>
        <p className="muted">Download your progress as a file, or restore a previous download.</p>
        <div className="row"><button className="btn" onClick={() => void exportData()}>Download progress</button>
          <label className="btn">Restore from file<input type="file" accept="application/json" hidden onChange={(e) => void importData(e)} /></label></div>
        <ErrorBox error={ioErr} />{ioMsg && <div className="alert alert-ok" role="status">{ioMsg}</div>}
      </div>
      <form className="card danger" onSubmit={del} noValidate>
        <h3>Delete account</h3>
        <p className="muted">Permanently removes your account and all learning progress.</p>
        <label>Confirm with your password<input type="password" autoComplete="current-password" value={delPw} onChange={(e) => setDelPw(e.target.value)} /></label>
        <ErrorBox error={delErr} />
        <button className="btn btn-danger" disabled={!delPw}>Delete my account</button>
      </form>
    </div>
  );
}
