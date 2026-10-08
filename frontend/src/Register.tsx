import { useState, type FormEvent } from "react"

import { API_URL } from "./config"
type RegisterProps = {
  onRegistered: () => void
  onCancel: () => void
}

function Register({ onRegistered, onCancel }: RegisterProps) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [confirm, setConfirm] = useState("")
  const [postcode, setPostcode] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError("")
    if (password !== confirm) {
      setError("Passwords do not match.")
      return
    }
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: username.trim(),
          password,
          postcode: postcode.trim() || null,
        }),
      })
      const data = await response.json().catch(() => null)
      if (!response.ok) {
        const detail = data?.detail
        throw new Error(
          typeof detail === "string"
            ? detail
            : Array.isArray(detail)
              ? detail.map((d: { msg: string }) => d.msg).join(" ")
              : "Could not create account."
        )
      }
      onRegistered()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create account.")
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
        <p className="eyebrow">CREATE ACCOUNT</p>
        <div className="form-group">
          <label>Username</label>
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} autoFocus />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <div className="form-group">
          <label>Confirm password</label>
          <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} />
        </div>
        <div className="form-group">
          <label>Postcode (optional)</label>
          <input type="text" value={postcode} onChange={(e) => setPostcode(e.target.value)} />
        </div>
        {error && <p className="error-message">{error}</p>}
        <button type="submit" className="primary-button" disabled={loading || !username.trim() || !password || !confirm}>
          {loading ? "Creating..." : "Create account"}
        </button>
        <button type="button" className="secondary-button" onClick={onCancel}>Back to log in</button>
      </form>
    </div>
  )
}

export default Register
