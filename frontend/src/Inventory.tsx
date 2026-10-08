import { getUserId } from "./auth"
import { useEffect, useState } from "react"
import CreateInventoryItem from "./CreateInventoryItem"
import IngredientTypeSelect from "./IngredientTypeSelect"

import { API_URL } from "./config"
type InventoryItem = {
  product_id: number
  name: string
  brand: string | null
  ingredient_type_name?: string | null
  quantity: number
  quantity_unit: string
  price: number | null
  currency: string | null
}

type InventoryData = {
  inventory_id: number
  items: InventoryItem[]
}

type IngredientType = {
  ingredient_type_id: number
  name: string
}

const API = `${API_URL}/api`

function Inventory() {
  const [data, setData] = useState<InventoryData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [showCreateItem, setShowCreateItem] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editQuantity, setEditQuantity] = useState("")
  const [editUnit, setEditUnit] = useState("unit")
  const [saving, setSaving] = useState(false)
  const [ingredientTypes, setIngredientTypes] = useState<IngredientType[]>([])
  const [editingTypeId, setEditingTypeId] = useState<string>("")

  async function loadInventory() {
    setLoading(true)
    setError("")

    try {
      const [invResponse, typesResponse] = await Promise.all([
        fetch(`${API}/inventory?user_id=${getUserId()}`),
        fetch(`${API}/ingredient-types`)
      ])
      if (!invResponse.ok || !typesResponse.ok) throw new Error()
      setData(await invResponse.json())
      setIngredientTypes(await typesResponse.json())
    } catch {
      setError("Could not load your inventory.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadInventory()
  }, [])

  async function changeQuantity(item: InventoryItem, action: "increase" | "decrease") {
    if (!data) return
    setError("")

    try {
      const response = await fetch(
        `${API}/inventory/${data.inventory_id}/items/${item.product_id}/${action}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ quantity: 1 }),
        }
      )
      if (!response.ok) throw new Error()

      const delta = action === "increase" ? 1 : -1
      setData({
        ...data,
        items: data.items.map((i) =>
          i.product_id === item.product_id
            ? { ...i, quantity: Math.max(0, i.quantity + delta) }
            : i
        ),
      })
    } catch {
      setError(`Could not ${action} ${item.name}.`)
    }
  }

  function startEdit(item: InventoryItem) {
    setEditingId(item.product_id)
    setEditQuantity(String(item.quantity))
    setEditUnit(item.quantity_unit)
    // Will load ingredient type if needed
    setError("")
  }

  async function changeEditUnit(item: InventoryItem, newUnit: string) {
    const oldUnit = editUnit
    setEditUnit(newUnit)
    if (!data || newUnit === oldUnit || editQuantity.trim() === "") return
    try {
      const params = new URLSearchParams({
        quantity: editQuantity,
        from_unit: oldUnit,
        to_unit: newUnit,
      })
      const response = await fetch(
        `${API}/inventory/${data.inventory_id}/items/${item.product_id}/convert?${params}`
      )
      if (!response.ok) return
      const result = await response.json()
      if (typeof result.quantity === "number") {
        setEditQuantity(String(Number(result.quantity.toFixed(4))))
      }
    } catch {
      // keep the typed quantity if conversion is unavailable
    }
  }

  async function saveEdit(item: InventoryItem) {
    if (!data) return
    const quantity = Number(editQuantity)
    if (editQuantity.trim() === "" || !Number.isFinite(quantity) || quantity < 0) {
      setError("Enter a valid quantity.")
      return
    }
    setSaving(true)
    setError("")
    try {
      const response = await fetch(
        `${API}/inventory/${data.inventory_id}/items/${item.product_id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ quantity, quantity_unit: editUnit }),
        }
      )
      if (!response.ok) throw new Error()
      
      if (editingTypeId && editingTypeId !== String(item.ingredient_type_name)) {
        const typeResponse = await fetch(
          `${API}/products/${item.product_id}/ingredient-type`,
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ingredient_type_id: Number(editingTypeId) || null }),
          }
        )
        if (!typeResponse.ok) throw new Error()
      }
      
      setEditingId(null)
      setEditingTypeId("")
      await loadInventory()
    } catch {
      setError(`Could not update ${item.name}.`)
    } finally {
      setSaving(false)
    }
  }

  async function removeItem(item: InventoryItem) {
    if (!data) return
    setError("")

    try {
      const response = await fetch(
        `${API}/inventory/${data.inventory_id}/items/${item.product_id}`,
        { method: "DELETE" }
      )
      if (!response.ok) throw new Error()

      setData({
        ...data,
        items: data.items.filter((i) => i.product_id !== item.product_id),
      })
    } catch {
      setError(`Could not remove ${item.name}.`)
    }
  }

  if (loading) {
    return (
      <div className="page-content">
        <div className="empty-page">
          <span className="muted">Loading inventory...</span>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="page-content">
        <div className="empty-page">
          <strong>{error}</strong>
          <button className="secondary-button" onClick={loadInventory}>
            Try again
          </button>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="page-content">
        <section className="page-heading">
          <div>
            <p className="eyebrow">YOUR PANTRY</p>
            <h2>Inventory</h2>
            <p className="muted">Track what you have in stock.</p>
          </div>

          <button
            className="primary-button"
            onClick={() => setShowCreateItem(true)}
          >
            + Add item
          </button>
        </section>

        {error && <p className="muted">{error}</p>}

        {data.items.length === 0 ? (
          <section className="panel empty-page">
            <div className="empty-icon">▣</div>
            <strong>Your inventory is empty</strong>
          </section>
        ) : (
          <section className="panel">
            {data.items.map((item) => (
              <div
                key={item.product_id}
                className="inventory-item"
              >
                <div className="inventory-item-info">
                  <strong>{item.name}</strong>
                  <p className="muted">{item.ingredient_type_name ?? "Unclassified"}</p>
                  {item.brand && <p className="muted">{item.brand}</p>}
                </div>

                {editingId === item.product_id ? (
                  <div className="inventory-edit">
                    <div className="inventory-item-controls inventory-edit-controls">
                      <input
                        type="number"
                        min="0"
                        step="any"
                        value={editQuantity}
                        onChange={(e) => setEditQuantity(e.target.value)}
                        disabled={saving}
                        aria-label="Quantity"
                      />
                      <select
                        value={editUnit}
                        onChange={(e) => changeEditUnit(item, e.target.value)}
                        disabled={saving}
                        aria-label="Unit"
                      >
                        <option value="unit">unit</option>
                        <option value="g">g</option>
                        <option value="kg">kg</option>
                        <option value="ml">ml</option>
                        <option value="l">l</option>
                        <option value="pcs">pcs</option>
                      </select>
                      <button className="secondary-button" onClick={() => setEditingId(null)} disabled={saving}>
                        Cancel
                      </button>
                      <button className="primary-button" onClick={() => saveEdit(item)} disabled={saving}>
                        {saving ? "Saving..." : "Save"}
                      </button>
                    </div>
                    <div className="form-group" style={{ marginTop: 12, marginBottom: 0 }}>
                      <label>Ingredient type</label>
                      <IngredientTypeSelect
                        types={ingredientTypes}
                        value={editingTypeId}
                        onChange={setEditingTypeId}
                        reloadTypes={() => loadInventory()}
                        placeholder="No ingredient type"
                        disabled={saving}
                      />
                    </div>
                  </div>
                ) : (
                <div className="inventory-item-controls">
                  <button
                    className="secondary-button"
                    onClick={() => changeQuantity(item, "decrease")}
                    disabled={item.quantity <= 0}
                    aria-label={`Decrease ${item.name}`}
                  >
                    −
                  </button>
                  <span className="inventory-quantity">
                    {item.quantity} {item.quantity_unit}
                  </span>
                  <button
                    className="secondary-button"
                    onClick={() => changeQuantity(item, "increase")}
                    aria-label={`Increase ${item.name}`}
                  >
                    +
                  </button>
                  <div className="inventory-actions">
                    <button className="link-button" onClick={() => startEdit(item)} aria-label={`Edit ${item.name}`}>
                      Edit
                    </button>
                    <button className="link-button danger" onClick={() => removeItem(item)} aria-label={`Remove ${item.name}`}>
                      Remove
                    </button>
                  </div>
                </div>
                )}
              </div>
            ))}
          </section>
        )}
      </div>

      {showCreateItem && (
        <CreateInventoryItem
          inventory_id={data.inventory_id}
          onClose={() => setShowCreateItem(false)}
          onCreated={() => {
            setShowCreateItem(false)
            loadInventory()
          }}
        />
      )}
    </>
  )
}

export default Inventory
