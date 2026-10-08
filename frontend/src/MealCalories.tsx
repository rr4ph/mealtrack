import { useEffect, useState } from "react"
import { DATA_CHANGED_EVENT } from "./StatusPills"

import { API_URL } from "./config"
const API = `${API_URL}/api`

function localInputValue(date: Date) {
  const pad = (n: number) => String(n).padStart(2, "0")
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

type PreviewLine = {
  ingredient_type_id: number
  ingredient_type_name: string
  product_name: string | null
  quantity_unit: string
  required: number
  available: number
  will_use: number
  remaining: number | null
  missing: number
  status: "ok" | "short" | "ambiguous"
  candidates: string[]
  products?: { product_name: string; before: number; used: number; after: number }[]
}

type Preview = { calories: number | null; sufficient: boolean; lines: PreviewLine[] }

const MAX_SERVINGS = 100
const fmt = (n: number) => String(Number(n.toFixed(2)))

function MealCalories({
  mealId,
  mealName,
}: {
  mealId: number
  mealName: string
}) {
  const [perServing, setPerServing] = useState<number | null>(null)
  const [loaded, setLoaded] = useState(false)
  const [error, setError] = useState("")
  const [editing, setEditing] = useState(false)
  const [kcal, setKcal] = useState("")
  const [saving, setSaving] = useState(false)
  const [logging, setLogging] = useState(false)
  const [servings, setServings] = useState("1")
  const [eatenAt, setEatenAt] = useState("")
  const [logError, setLogError] = useState("")
  const [message, setMessage] = useState("")
  const [preview, setPreview] = useState<Preview | null>(null)
  const [previewError, setPreviewError] = useState("")

  const servingsError = (() => {
    const n = Number(servings)
    if (servings.trim() === "" || !Number.isFinite(n)) return "Enter a valid number of servings."
    if (n <= 0) return "Servings must be greater than 0."
    if (n > MAX_SERVINGS) return `Maximum ${MAX_SERVINGS} servings per meal.`
    return ""
  })()

  useEffect(() => {
    const count = Number(servings)
    if (!logging || servingsError) {
      setPreview(null)
      return
    }
    let stale = false
    setPreviewError("")
    fetch(`${API}/meals/${mealId}/consume-preview?servings=${count}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => !stale && setPreview(d))
      .catch(() => !stale && setPreviewError("Could not load the inventory preview."))
    return () => {
      stale = true
    }
  }, [logging, servings, servingsError, mealId])

  useEffect(() => {
    fetch(`${API}/meals/${mealId}/calories`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        setPerServing(d.calories_per_serving)
        setLoaded(true)
      })
      .catch(() => setError("Could not load calories."))
  }, [mealId])

  async function save() {
    const value = Number(kcal)
    if (kcal.trim() === "" || !Number.isFinite(value) || value < 0 || value > 10000) {
      setError("Enter calories between 0 and 10,000.")
      return
    }
    setSaving(true)
    try {
      const response = await fetch(`${API}/meals/${mealId}/calories`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ calories_per_serving: value }),
      })
      if (!response.ok) throw new Error()
      setPerServing(value)
      setEditing(false)
      setError("")
    } catch {
      setError("Could not save calories.")
    } finally {
      setSaving(false)
    }
  }

  async function logMeal() {
    const count = Number(servings)
    if (servingsError) {
      setLogError(servingsError)
      return
    }
    setSaving(true)
    setLogError("")
    try {
      const response = await fetch(`${API}/meals/${mealId}/consume`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ servings: count, consumed_at: eatenAt || null }),
      })
      if (!response.ok) {
        const body = await response.json().catch(() => null)
        throw new Error(typeof body?.detail === "string" ? body.detail : "Could not log meal.")
      }
      const result = await response.json()
      setLogging(false)
      const missing = result.lines.filter((l: PreviewLine) => l.status !== "ok").length
      setMessage(
        `Logged ${mealName}: ${Math.round(result.calories)} kcal.` +
          (missing ? ` ${missing} ingredient${missing > 1 ? "s were" : " was"} missing or not deducted.` : "")
      )
      window.dispatchEvent(new Event(DATA_CHANGED_EVENT))
    } catch (err) {
      setLogError(err instanceof Error ? err.message : "Could not log meal.")
    } finally {
      setSaving(false)
    }
  }

  const logTotal = perServing !== null && !servingsError ? Math.round(perServing * Number(servings)) : 0
  const sufficient = preview?.sufficient ?? true

  return (
    <section className="panel meal-ingredients-panel meal-calories-panel">
      <div className="meal-ingredients-header">
        <div>
          <p className="eyebrow">NUTRITION</p>
          <h3>Calories</h3>
        </div>
        <button
          className="primary-button compact-button"
          type="button"
          disabled={!loaded || perServing === null}
          onClick={() => {
            setEatenAt(localInputValue(new Date()))
            setServings("1")
            setLogError("")
            setMessage("")
            setLogging(true)
          }}
        >
          Log meal
        </button>
      </div>

      <div className="meal-calories-body">
        {error && <p className="error-message">{error}</p>}
        {message && <p className="muted">{message}</p>}
        {loaded && !editing && (
          <>
            <strong>{perServing !== null ? `${Math.round(perServing)} kcal / serving` : "No calories set"}</strong>
            <div>
              <button
                type="button"
                className="secondary-button compact-button"
                onClick={() => {
                  setKcal(perServing?.toString() ?? "")
                  setError("")
                  setEditing(true)
                }}
              >
                Edit calories
              </button>
            </div>
          </>
        )}
        {loaded && editing && (
          <div className="meal-calories-edit">
            <input
              className="calorie-input" type="number" min="0" step="any" value={kcal}
              onChange={(e) => setKcal(e.target.value)} disabled={saving} aria-label="Calories per serving"
            />
            <span className="muted">kcal / serving</span>
            <button type="button" className="secondary-button compact-button" disabled={saving} onClick={() => setEditing(false)}>Cancel</button>
            <button type="button" className="primary-button compact-button" disabled={saving} onClick={save}>Save</button>
          </div>
        )}
      </div>

      {logging && (
        <div className="modal-backdrop" onMouseDown={() => !saving && setLogging(false)}>
          <div className="modal confirmation-modal" onMouseDown={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <p className="eyebrow">LOG MEAL</p>
                <h2>Log {mealName}</h2>
              </div>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Servings</label>
                <input type="number" min="0.01" max={MAX_SERVINGS} step="any" value={servings} onChange={(e) => setServings(e.target.value)} disabled={saving} />
                {servingsError && <p className="error-message">{servingsError}</p>}
              </div>
              {previewError && <p className="error-message">{previewError}</p>}
              {preview && preview.lines.length === 0 && <p className="muted">This meal has no ingredients.</p>}
              {preview && preview.lines.length > 0 && (
                <>
                  <p className="eyebrow log-section-title">INVENTORY USED</p>
                  {preview.lines.map((line) => {
                    const u = line.quantity_unit
                    return (
                      <div key={line.ingredient_type_id} className={`log-preview-line${line.status === "ok" ? "" : " log-preview-short"}`}>
                        <strong>{line.ingredient_type_name}</strong>
                        <p className="muted">Required: {fmt(line.required)} {u}</p>
                        {line.will_use > 0 && line.products ? (
                          <>
                            {line.products.map((p, i) => (
                              <div key={i} className="log-product">
                                <p>{p.product_name}</p>
                                <p className="muted">{fmt(p.before)} {u} → {fmt(p.after)} {u} remaining</p>
                                <p className="muted">Consumed: {fmt(p.used)} {u}</p>
                              </div>
                            ))}
                            {line.status !== "ok" && <p className="muted">Available in inventory: {fmt(line.available)} {u}</p>}
                          </>
                        ) : (
                          <p className="muted">None in inventory</p>
                        )}
                        {line.status !== "ok" && <p className="log-missing">Missing: {fmt(line.missing)} {u}</p>}
                      </div>
                    )
                  })}
                </>
              )}
              {preview && !preview.sufficient && (
                <div className="log-warning">
                  <strong>⚠ Some ingredients are missing</strong>
                  {preview.lines.filter((l) => l.status !== "ok").map((l) => (
                    <p key={l.ingredient_type_id} className="muted">
                      {l.ingredient_type_name} — Required: {fmt(l.required)} {l.quantity_unit} · Available: {fmt(l.available)} {l.quantity_unit} · Missing: {fmt(l.missing)} {l.quantity_unit}
                    </p>
                  ))}
                </div>
              )}
              <p className="log-calories"><span className="muted">Calories</span> <strong>{logTotal} kcal</strong></p>
              <div className="form-group">
                <label>When</label>
                <input type="datetime-local" value={eatenAt} onChange={(e) => setEatenAt(e.target.value)} disabled={saving} />
              </div>
              {logError && <p className="error-message">{logError}</p>}
            </div>
            <div className="modal-footer">
              <button type="button" className="secondary-button" onClick={() => setLogging(false)} disabled={saving}>Cancel</button>
              <button type="button" className="primary-button" onClick={logMeal} disabled={saving || !preview || !!servingsError}>
                {saving ? "Logging..." : sufficient ? "Log meal" : "Log anyway"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

export default MealCalories
