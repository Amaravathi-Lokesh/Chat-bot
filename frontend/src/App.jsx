import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./login";
import Chat from "./chat";

export default function App() { 
  const user = localStorage.getItem("user");

  return (
    <Routes>
      {/* LOGIN */}
      <Route path="/" element={<Login />} />

      {/* CHAT (PROTECTED) */}
      <Route
        path="/chat"
        element={<Chat/>}
      />

      {/* fallback */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}