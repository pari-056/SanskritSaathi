import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import Layout from "./components/Layout";
import { Spinner } from "./components/ui";
import { ForgotPage, LoginPage, RegisterPage, ResetPage } from "./pages/AuthPages";
import Home from "./pages/Home";
import Learn from "./pages/Learn";
import Script from "./pages/Script";
import Practice from "./pages/Practice";
import Tutor from "./pages/Tutor";
import Lab from "./pages/Lab";
import Settings from "./pages/Settings";

function Protected() {
  const { user, loading } = useAuth();
  if (loading) return <Spinner label="Loading…" />;
  if (!user) return <Navigate to="/login" replace />;
  return <Layout><Outlet /></Layout>;
}

function PublicOnly() {
  const { user, loading } = useAuth();
  if (loading) return <Spinner label="Loading…" />;
  if (user) return <Navigate to="/" replace />;
  return <Outlet />;
}

export default function App() {
  return (
    <Routes>
      <Route element={<PublicOnly />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>
      <Route path="/forgot-password" element={<ForgotPage />} />
      <Route path="/reset-password" element={<ResetPage />} />
      <Route element={<Protected />}>
        <Route path="/" element={<Home />} />
        <Route path="/learn" element={<Learn />} />
        <Route path="/learn/:lessonId" element={<Learn />} />
        <Route path="/script" element={<Script />} />
        <Route path="/practice" element={<Practice />} />
        <Route path="/tutor" element={<Tutor />} />
        <Route path="/lab" element={<Lab />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
