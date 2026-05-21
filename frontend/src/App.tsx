import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Login from "./pages/Login";
import WirkmodellEditor from "./pages/WirkmodellEditor";
import NarrativEditor from "./pages/NarrativEditor";
import Leseansicht from "./pages/Leseansicht";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: "1rem", borderBottom: "1px solid #eee", display: "flex", gap: "1rem" }}>
        <NavLink to="/">Login</NavLink>
        <NavLink to="/wirkmodell">Wirkmodell</NavLink>
        <NavLink to="/narrativ">Narrativ</NavLink>
        <NavLink to="/lesen">Lesen</NavLink>
      </nav>
      <main style={{ padding: "2rem" }}>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/wirkmodell" element={<WirkmodellEditor />} />
          <Route path="/narrativ" element={<NarrativEditor />} />
          <Route path="/lesen" element={<Leseansicht />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
