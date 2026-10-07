import { useEffect, useState, type FormEvent } from "react"
import { saveSession, type Session } from "./auth"
import { DATA_CHANGED_EVENT } from "./StatusPills"

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

  const [calorieGoal, setCalorieGoal] = useState("")
  const [spendingLimit, setSpendingLimit] = useState("")
  const [goalsMessage, setGoalsMessage] = useState("")
  const [goalsError, setGoalsError] = useState("")
  const [savingGoals, setSavingGoals] = useState(false)

  useEffect(() => {
    fetch(`${API}/goals`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        setCalorieGoal(d.daily_calorie_goal?.toString() ?? "")
        setSpendingLimit(d.spending_limit?.toString() ?? "")
      })
      .catch(() => setGoalsError("Could not load goals."))
  }, [])

  async function saveGoals(event: FormEvent) {
    event.preventDefault()
    setGoalsMessage("")
    setGoalsError("")
    const kcal = calorieGoal.trim() === "" ? null : Number(calorieGoal)
    const limit = spendingLimit.trim() === "" ? null : Number(spendingLimit)
    if (kcal !== null && (!Number.isInteger(kcal) || kcal < 500 || kcal > 10000)) {
      setGoalsError("Calorie goal must be a whole number between 500 and 10,000.")
      return
    }
    if (limit !== null && (!Number.isFinite(limit) || limit < 0 || limit > 100000)) {
      setGoalsError("Spending limit must be zero or more.")
      return
    }
    setSavingGoals(true)
    try {
      const response = await fetch(`${API}/goals`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ daily_calorie_goal: kcal, spending_limit: limit }),
      })
      if (!response.ok) throw new Error(await errorFrom(response, "Could not save goals."))
      setGoalsMessage("Goals saved.")
      window.dispatchEvent(new Event(DATA_CHANGED_EVENT))
    } catch (err) {
      setGoalsError(err instanceof Error ? err.message : "Could not save goals.")
    } finally {
      setSavingGoals(false)
    }
  }

  const [confirmReset, setConfirmReset] = useState<"limit" | "calories" | null>(null)
  const [resetting, setResetting] = useState(false)
  const [resetMessage, setResetMessage] = useState("")
  const [resetError, setResetError] = useState("")

  async function runReset() {
    if (!confirmReset) return
    setResetting(true)
    setResetMessage("")
    setResetError("")
    try {
      const isLimit = confirmReset === "limit"
      const response = await fetch(`${API}${isLimit ? "/goals/spending-limit" : "/consumptions/today"}`, { method: "DELETE" })
      if (!response.ok) throw new Error(await errorFrom(response, "Could not reset."))
      if (isLimit) setSpendingLimit("")
      setResetMessage(isLimit ? "Spending budget reset. Set a new limit to start from £0 spent." : "Today's calorie intake reset to 0.")
      window.dispatchEvent(new Event(DATA_CHANGED_EVENT))
    } catch (err) {
      setResetError(err instanceof Error ? err.message : "Could not reset.")
    } finally {
      setResetting(false)
      setConfirmReset(null)
    }
  }

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

      <form className="panel account-panel" onSubmit={saveGoals}>
        <p className="eyebrow">GOALS</p>
        <div className="form-group">
          <label>Daily calorie goal (kcal)</label>
          <input type="number" min="500" max="10000" step="1" placeholder="e.g. 2500" value={calorieGoal} onChange={(e) => setCalorieGoal(e.target.value)} disabled={savingGoals} />
        </div>
        <div className="form-group">
          <label>Spending limit (£)</label>
          <input type="number" min="0" step="0.01" placeholder="e.g. 100" value={spendingLimit} onChange={(e) => setSpendingLimit(e.target.value)} disabled={savingGoals} />
        </div>
        {goalsError && <p className="error-message">{goalsError}</p>}
        {goalsMessage && <p className="muted">{goalsMessage}</p>}
        <button type="submit" className="primary-button" disabled={savingGoals}>
          {savingGoals ? "Saving..." : "Save goals"}
        </button>
      </form>

      <section className="panel account-panel">
        <p className="eyebrow">SAFETY / RESET</p>
        <p className="muted">{spendingLimit === "" ? "No spending limit is currently configured." : `Current spending limit: £${spendingLimit}`}</p>
        {resetError && <p className="error-message">{resetError}</p>}
        {resetMessage && <p className="muted">{resetMessage}</p>}
        <div>
          <button type="button" className="danger-button" onClick={() => setConfirmReset("limit")} disabled={spendingLimit === ""}>Reset spending limit</button>{" "}
          <button type="button" className="danger-button" onClick={() => setConfirmReset("calories")}>Reset today's calorie intake</button>
        </div>
      </section>

      {confirmReset && (
        <div className="modal-backdrop" onMouseDown={() => !resetting && setConfirmReset(null)}>
          <div className="modal confirmation-modal" onMouseDown={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{confirmReset === "limit" ? "Reset spending budget?" : "Reset today's calorie intake?"}</h2>
            </div>
            <div className="modal-body">
              <p className="muted">
                {confirmReset === "limit"
                  ? "This will start a new spending budget from now. Previous purchases will remain in your history."
                  : "This will remove today's logged meals and reset today's calorie total to zero. Previous days will remain unchanged."}
              </p>
            </div>
            <div className="modal-footer">
              <button type="button" className="secondary-button" onClick={() => setConfirmReset(null)} disabled={resetting}>Cancel</button>
              <button type="button" className="danger-button" onClick={runReset} disabled={resetting}>
                {confirmReset === "limit" ? "Reset budget" : "Reset today's intake"}
              </button>
            </div>
          </div>
        </div>
      )}

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
