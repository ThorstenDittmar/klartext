import { BrowserRouter, Routes, Route } from "react-router-dom";
import MeineWerke from "./pages/MeineWerke";
import NarrativeDetail from "./pages/NarrativeDetail";
import NarrativeAnalyse from "./pages/NarrativeAnalyse";
import WirkgefuegeVorschlag from "./pages/WirkgefuegeVorschlag";
import CausalModelEditor from "./pages/CausalModelEditor";
import Login from "./pages/Login";

// ---------------------------------------------------------------------------
// App — V2 routing
//
// Screen 0: /                                → MeineWerke
// Screen 1: /narrative/:narrativeId          → NarrativeDetail
// Screen 2: /narrative/:narrativeId/analyse  → NarrativeAnalyse
// Screen 3: /narrative/:narrativeId/wirkgefuege-vorschlag → WirkgefuegeVorschlag
// Screen 4: /causal-model/:modelId           → CausalModelEditor
// ---------------------------------------------------------------------------

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: "100vh", background: "var(--color-bg)" }}>
        <Routes>
          <Route path="/" element={<MeineWerke />} />
          <Route path="/narrative/:narrativeId" element={<NarrativeDetail />} />
          <Route path="/narrative/:narrativeId/analyse" element={<NarrativeAnalyse />} />
          <Route
            path="/narrative/:narrativeId/wirkgefuege-vorschlag"
            element={<WirkgefuegeVorschlag />}
          />
          <Route path="/causal-model/:modelId" element={<CausalModelEditor />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
