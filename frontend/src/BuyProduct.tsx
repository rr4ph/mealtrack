import { useEffect, useState } from "react"
import { DATA_CHANGED_EVENT } from "./StatusPills"

const API = "http://localhost:8000/api"

type BuyProductProps = {
  product: { product_id: number; name: string; price: number; currency: string }
  onClose: () => void
  onBought: (message: string) => void
}

function BuyProduct({ product, onClose, onBought }: BuyProductProps) {
  const [quantity, setQuantity] = useState("1")
  const [price, setPrice] = useState(product.price.toFixed(2))
  const [priceEdited, setPriceEdited] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  const [remaining, setRemaining] = useState<number | null>(null)

  useEffect(() => {
    fetch(`${API}/stats/spending?range=monthly`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => setRemaining(d.remaining ?? null))
      .catch(() => setRemaining(null))
  }, [])

  const total = Number(price)
  const overBy = remaining !== null && price.trim() !== "" && Number.isFinite(total) ? total - remaining : 0
  const overLimit = overBy > 0.005

  function changeQuantity(value: string) {
    setQuantity(value)
    const n = Number(value)
    if (!priceEdited && n > 0) setPrice((n * product.price).toFixed(2))
  }

  async function buy() {
    const q = Number(quantity)
    const p = Number(price)
    if (!Number.isFinite(q) || q <= 0) return setError("Quantity must be greater than zero.")
    if (price.trim() === "" || !Number.isFinite(p) || p < 0) return setError("Price must be zero or more.")
    setSaving(true)
    setError("")
    try {
      const response = await fetch(`${API}/purchases`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: product.product_id, quantity: q, price_paid: p }),
      })
      if (!response.ok) {
        const data = await response.json().catch(() => null)
        throw new Error(typeof data?.detail === "string" ? data.detail : "Could not record purchase.")
      }
      window.dispatchEvent(new Event(DATA_CHANGED_EVENT))
      onBought(`Bought ${q} × ${product.name} for £${p.toFixed(2)}.`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not record purchase.")
      setSaving(false)
    }
  }

  return (
    <div className="modal-backdrop" onMouseDown={() => !saving && onClose()}>
      <div className="modal confirmation-modal" onMouseDown={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <p className="eyebrow">BUY</p>
            <h2>{product.name}</h2>
          </div>
        </div>
        <div className="modal-body">
          <div className="form-group">
            <label>Quantity (packs)</label>
            <input type="number" min="1" step="1" value={quantity} onChange={(e) => changeQuantity(e.target.value)} disabled={saving} />
          </div>
          <div className="form-group">
            <label>Total price paid (£)</label>
            <input
              type="number" min="0" step="0.01" value={price}
              onChange={(e) => { setPrice(e.target.value); setPriceEdited(true) }} disabled={saving}
            />
          </div>
          <p className="muted">Records the purchase and adds the packs to your inventory.</p>
          {remaining !== null && (
            <p className="muted">
              Remaining budget: £{Math.abs(remaining).toFixed(2)}
              {remaining < 0 && " over"}
            </p>
          )}
          {overLimit && <p className="error-message">⚠ This purchase will put you £{overBy.toFixed(2)} over your spending limit.</p>}
          {error && <p className="error-message">{error}</p>}
        </div>
        <div className="modal-footer">
          <button type="button" className="secondary-button" onClick={onClose} disabled={saving}>Cancel</button>
          <button type="button" className="primary-button" onClick={buy} disabled={saving}>
            {saving ? "Buying..." : overLimit ? "Buy anyway" : "Confirm purchase"}
          </button>
        </div>
      </div>
    </div>
  )
}

export default BuyProduct
