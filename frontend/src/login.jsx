import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const endpoint = isLogin
        ? "http://127.0.0.1:8000/auth/login"
        : "http://127.0.0.1:8000/auth/register";

      const payload = isLogin
        ? { username, password }
        : { username, email, password };

      const res = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      console.log("STATUS:", res.status);

      let data = null;

      try {
        data = await res.json();
      } catch (err) {
        console.error("JSON Parse Error:", err);
      }

      console.log("RESPONSE DATA:", data);

      if (!res.ok) {
        alert(data?.detail || "Request Failed");
        return;
      }

      if (isLogin) {
        if (!data) {
          alert("Backend returned empty response");
          return;
        }

        localStorage.setItem(
          "user",
          data.username || username
        );

        localStorage.setItem(
          "access_token",
          data.access_token || ""
        );
        localStorage.setItem(
          "refresh_token",
          data.refresh_token || ""
        );
        localStorage.setItem(
          "token_type",
          data.token_type || "bearer"
        )
        console.log("LOGIN SUCCESS");

        navigate("/chat");
      } else {
        alert("Registration Successful");
        setIsLogin(true);
      }

    } catch (err) {
      console.error("LOGIN ERROR:", err);
      alert("Server Error");
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-slate-950 text-white">

      <div className="w-96 bg-slate-900 p-6 rounded-xl border border-slate-800">

        <h1 className="text-2xl text-cyan-400 mb-4 text-center">
          AI Chatbot
        </h1>

        <form
          onSubmit={handleSubmit}
          className="space-y-3"
        >

          <input
            className="w-full p-3 bg-slate-800 rounded"
            placeholder="Username"
            value={username}
            onChange={(e) =>
              setUsername(e.target.value)
            }
            required
          />

          {!isLogin && (
            <input
              className="w-full p-3 bg-slate-800 rounded"
              placeholder="Email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              required
            />
          )}

          <input
            className="w-full p-3 bg-slate-800 rounded"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            required
          />

          <button
            type="submit"
            className="w-full bg-cyan-500 text-black p-3 rounded"
          >
            {isLogin ? "Login" : "Register"}
          </button>

        </form>

        <button
          onClick={() => setIsLogin(!isLogin)}
          className="mt-3 text-cyan-400 w-full"
        >
          {isLogin
            ? "Create Account"
            : "Already have an account?"}
        </button>

      </div>

    </div>
  );
}