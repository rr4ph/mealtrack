import { useState } from "react"

const NEW_OPTION = "__new__"
const API = "http://localhost:8000/api"

export type IngredientType = {
  ingredient_type_id: number
  name: string
}

type Props = {
  types: IngredientType[]
  value: string
  onChange: (value: string) => void
  reloadTypes: () => Promise<void>
  placeholder?: string
  disabled?: boolean
}

function IngredientTypeSelect({ types, value, onChange, reloadTypes, placeholder = "Select ingredient", disabled }: Props) {
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  async function create() {
    const trimmed = name.trim()
    if (!trimmed) return
    const existing = types.find((t) => t.name.toLowerCase() === trimmed.toLowerCase())
    if (existing) {
      onChange(String(existing.ingredient_type_id))
      setName("")
      setCreating(false)
      return
    }
    setBusy(true)
    setError("")
    try {
      const response = await fetch(`${API}/ingredient-types`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: trimmed }),
      })
      const data = await response.json().catch(() => null)
      if (!response.ok) throw new Error(data?.detail || "Could not create ingredient type.")
      await reloadTypes()
      onChange(String(data.ingredient_type_id))
      setName("")
      setCreating(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create ingredient type.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="type-select">
      <div className="type-select-row">
        <select
          value={value}
          onChange={(e) => {
            if (e.target.value === NEW_OPTION) {
              setCreating(true)
              return
            }
            onChange(e.target.value)
          }}
          disabled={disabled}
        >
          <option value="">{placeholder}</option>
          {types.map((type) => (
            <option key={type.ingredient_type_id} value={type.ingredient_type_id}>
              {type.name}
            </option>
          ))}
          <option value={NEW_OPTION}>+ Create new ingredient type</option>
        </select>
      </div>
      {creating && (
        <div className="type-select-row">
          <input
            type="text"
            placeholder="New ingredient type..."
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault()
                create()
              }
            }}
            disabled={busy}
            autoFocus
          />
          <button type="button" className="primary-button" onClick={create} disabled={busy || !name.trim()}>
            {busy ? "..." : "Add"}
          </button>
        </div>
      )}
      {error && <p className="error-message type-select-error">{error}</p>}
    </div>
  )
}

export default IngredientTypeSelect
