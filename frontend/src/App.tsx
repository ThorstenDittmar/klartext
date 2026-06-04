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
      <nav style={{ padding: "1rem", borderBottom: "1px solid #eee", display: "flex", gap: "1rem" }}>
        <NavLink to="/">Login</NavLink>
        <NavLink to="/causal-model">Wirkmodell</NavLink>
        <NavLink to="/narrative">Narrativ</NavLink>
        <NavLink to="/reading">Lesen</NavLink>
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
