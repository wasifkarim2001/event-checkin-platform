import { useState } from "react";
import { useNavigate } from "react-router";
import { api, ApiError, setToken } from "./api";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  async function signIn() {
    setBusy(true);
    setError("");
    try {
      const { token } = await api<{ token: string }>("/auth/token/", {
        method: "POST",
        body: { username, password },
      });
      setToken(token);
      navigate("/staff");
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) setError("Wrong username or password.");
      else if (err instanceof ApiError && err.status === 429) setError("Too many attempts. Wait a minute and try again.");
      else setError("Something went wrong. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <h1>Staff sign-in</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          void signIn();
        }}
      >
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" required />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {error && <p role="alert">{error}</p>}
        <button disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
      </form>
    </main>
  );
}