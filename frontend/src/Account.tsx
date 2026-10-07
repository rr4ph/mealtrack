import { useState, type FormEvent } from "react"
import { saveSession, type Session } from "./auth"

const API = "http://localhost:8000/api"

type AccountProps = {
  session: Session
  onLogout: () => void
  onSessionChange: (session: Session) => void
}

async function errorFrom(response: Response, fallback: string) {
  const data = await response.json().catch(() => null)
  return data?.detail || fallback
}

function Account({ session, onLogout, onSessionChange }: AccountProps) {
  const [username, setUsername] = useState(session.username)
  const [postcode, setPostcode] = useState(session.postcode ?? "")
  const [profileMessage, setProfileMessage] = useState("")
  const [profileError, setProfileError] = useState("")
  const [savingProfile, setSavingProfile] = useState(false)

  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [passwordMessage, setPasswordMessage] = useState("")
  const [passwordError, setPasswordError] = useState("")
  const [savingPassword, setSavingPassword] = useState(false)

  async function saveProfile(event: FormEvent) {
    event.preventDefault()
    setProfileMessage("")
    setProfileError("")
    if (!username.trim()) {
      setProfileError("Username is required.")
      return
    }
    setSavingProfile(true)
    try {
      const response = await fetch(`${API}/auth/account`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim(), postcode: postcode.trim() || null }),
      })
      if (!response.ok) throw new Error(await errorFrom(response, "Could not update account."))
      const data = await response.json()
      const updated: Session = { ...session, username: data.username, postcode: data.postcode }
      saveSession(updated)
      onSessionChange(updated)
      setUsername(data.username)
      setPostcode(data.postcode ?? "")
      setProfileMessage("Account updated.")
    } catch (err) {
      setProfileError(err instanceof Error ? err.message : "Could not update account.")
    } finally {
      setSavingProfile(false)
    }
  }

  async function changePassword(event: FormEvent) {
    event.preventDefault()
    setPasswordMessage("")
    setPasswordError("")
    if (newPassword.length < 8) {
      setPasswordError("New password must be at least 8 characters.")
      return
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("New password and confirmation do not match.")
      return
    }
    setSavingPassword(true)
    try {
      const response = await fetch(`${API}/auth/password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      })
      if (!response.ok) throw new Error(await errorFrom(response, "Could not change password."))
      const data = await response.json()
      const updated: Session = { ...session, token: data.token }
      saveSession(updated)
      onSessionChange(updated)
      setCurrentPassword("")
      setNewPassword("")
      setConfirmPassword("")
      setPasswordMessage("Password changed.")
    } catch (err) {
      setPasswordError(err instanceof Error ? err.message : "Could not change password.")
    } finally {
      setSavingPassword(false)
    }
  }

  return (
    <div className="page-content account-page">
      <section className="page-heading">
        <div>
          <p className="eyebrow">PROFILE</p>
          <h2>Account</h2>
          <p className="muted">Manage your Mealtrack account.</p>
        </div>
      </section>

      <form className="panel account-panel" onSubmit={saveProfile}>
        <p className="eyebrow">DETAILS</p>
        <div className="form-group">
          <label>Username</label>
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} disabled={savingProfile} />
        </div>
        <div className="form-group">
          <label>Postcode</label>
          <input type="text" value={postcode} onChange={(e) => setPostcode(e.target.value)} disabled={savingProfile} />
        </div>
        {profileError && <p className="error-message">{profileError}</p>}
        {profileMessage && <p className="muted">{profileMessage}</p>}
        <button type="submit" className="primary-button" disabled={savingProfile}>
          {savingProfile ? "Saving..." : "Save changes"}
        </button>
      </form>

      <form className="panel account-panel" onSubmit={changePassword}>
        <p className="eyebrow">PASSWORD</p>
        <div className="form-group">
          <label>Current password</label>
          <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} disabled={savingPassword} />
        </div>
        <div className="form-group">
          <label>New password</label>
          <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} disabled={savingPassword} />
        </div>
        <div className="form-group">
          <label>Confirm new password</label>
          <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} disabled={savingPassword} />
        </div>
        {passwordError && <p className="error-message">{passwordError}</p>}
        {passwordMessage && <p className="muted">{passwordMessage}</p>}
        <button
          type="submit"
          className="primary-button"
          disabled={savingPassword || !currentPassword || !newPassword || !confirmPassword}
        >
          {savingPassword ? "Changing..." : "Change password"}
        </button>
      </form>

      <section className="panel account-panel">
        <p className="eyebrow">SESSION</p>
        <button type="button" className="secondary-button" onClick={onLogout}>Log out</button>
      </section>
    </div>
  )
}

export default Account
