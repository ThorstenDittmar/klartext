import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Login from "./pages/Login";
import CausalModelEditor from "./pages/CausalModelEditor";
import NarrativeEditor from "./pages/NarrativeEditor";
import NarrativeAnalyse from "./pages/NarrativeAnalyse";
import WirkgefuegeVorschlag from "./pages/WirkgefuegeVorschlag";
import ReadingView from "./pages/ReadingView";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: "12px 20px", borderBottom: "1px solid var(--color-border)", display: "flex", gap: "16px", background: "var(--color-bg)" }}>
        <NavLink to="/" style={({ isActive }) => ({
          color: isActive ? "var(--color-text-primary)" : "var(--color-text-secondary)",
          fontWeight: isActive ? "500" : "normal",
          textDecoration: "none",
          fontSize: "14px",
        })}>Login</NavLink>
        <NavLink to="/causal-model" style={({ isActive }) => ({
          color: isActive ? "var(--color-text-primary)" : "var(--color-text-secondary)",
          fontWeight: isActive ? "500" : "normal",
          textDecoration: "none",
          fontSize: "14px",
        })}>Wirkmodell</NavLink>
        <NavLink to="/narrative" style={({ isActive }) => ({
          color: isActive ? "var(--color-text-primary)" : "var(--color-text-secondary)",
          fontWeight: isActive ? "500" : "normal",
          textDecoration: "none",
          fontSize: "14px",
        })}>Narrativ</NavLink>
        <NavLink to="/reading" style={({ isActive }) => ({
          color: isActive ? "var(--color-text-primary)" : "var(--color-text-secondary)",
          fontWeight: isActive ? "500" : "normal",
          textDecoration: "none",
          fontSize: "14px",
        })}>Lesen</NavLink>
      </nav>
      <main style={{ padding: "2rem" }}>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/causal-model" element={<CausalModelEditor />} />
          <Route path="/narrative" element={<NarrativeEditor />} />
          <Route path="/narrative/:narrativeId/analyse" element={<NarrativeAnalyse />} />
          <Route
            path="/narrative/:narrativeId/wirkgefuege-vorschlag"
            element={<WirkgefuegeVorschlag />}
          />
          <Route path="/reading" element={<ReadingView />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
