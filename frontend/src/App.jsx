import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./Login";
import Chat from "./Chat";

export default function App() {
  const user = localStorage.getItem("user");

  return (
    <Routes>
      {/* LOGIN */}
      <Route path="/" element={<Login />} />

      {/* CHAT (PROTECTED) */}
      <Route
        path="/chat"
        element={user ? <Chat /> : <Navigate to="/" />}
      />

      {/* fallback */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}