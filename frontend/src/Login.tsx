import { useState, type FormEvent } from "react"
import { saveSession, type Session } from "./auth"

type LoginProps = {
  onLogin: (session: Session) => void
  onCreateAccount: () => void
  notice?: string
}

function Login({ onLogin, onCreateAccount, notice }: LoginProps) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setError("")

    try {
      const response = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim(), password }),
      })
      const data = await response.json().catch(() => null)
      if (!response.ok) {
        throw new Error(data?.detail || "Could not log in.")
      }
      saveSession(data)
      onLogin(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not log in.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <form className="panel login-panel" onSubmit={handleSubmit}>
        <div className="brand">
          <div className="brand-mark">M</div>
          <span>Meal<span>track</span></span>
        </div>
        <p className="eyebrow">LOG IN</p>
        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        {notice && <p className="muted">{notice}</p>}
        {error && <p className="error-message">{error}</p>}
        <button type="submit" className="primary-button" disabled={loading || !username.trim() || !password}>
          {loading ? "Logging in..." : "Log in"}
        </button>
        <button type="button" className="secondary-button" onClick={onCreateAccount}>
          Create account
        </button>
      </form>
    </div>
  )
}

export default Login
