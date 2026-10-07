import { useEffect, useState } from "react"
import IngredientTypeSelect, { type IngredientType } from "./IngredientTypeSelect"

const API = "http://localhost:8000/api"

export type Product = {
  product_id: number
  name: string
  brand: string | null
  price: number
  currency: string
  ingredient_type_id: number | null
}

type CreateInventoryItemProps = {
  inventory_id: number
  onClose: () => void
  onCreated: () => void
  initialProduct?: Product
}

function CreateInventoryItem({ inventory_id, onClose, onCreated, initialProduct }: CreateInventoryItemProps) {
  const [query, setQuery] = useState("")
  const [supermarket, setSupermarket] = useState("all")
  const [products, setProducts] = useState<Product[]>([])
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState("")
  const [saving, setSaving] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(initialProduct ?? null)
  const [quantity, setQuantity] = useState("1")
  const [quantityUnit, setQuantityUnit] = useState("unit")
  const [types, setTypes] = useState<IngredientType[]>([])
  const [typeId, setTypeId] = useState(
    initialProduct?.ingredient_type_id != null ? String(initialProduct.ingredient_type_id) : ""
  )

  async function loadTypes() {
    try {
      const response = await fetch(`${API}/ingredient-types`)
      if (!response.ok) throw new Error()
      setTypes(await response.json())
    } catch {
      setError("Could not load ingredient types.")
    }
  }

  useEffect(() => {
    loadTypes()
  }, [])

  async function searchProducts() {
    if (!query.trim()) return
    setSearching(true)
    setError("")
    setProducts([])

    try {
      const response = await fetch(
        `${API}/products?query=${encodeURIComponent(query)}&supermarket=${supermarket}`
      )
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || "Could not search products.")
      }
      const data = await response.json()
      setProducts(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not search products.")
    } finally {
      setSearching(false)
    }
  }

  function selectProduct(product: Product) {
    setSelectedProduct(product)
    setQuantity("1")
    setQuantityUnit("unit")
    setTypeId(product.ingredient_type_id != null ? String(product.ingredient_type_id) : "")
    setError("")
  }

  async function addItem() {
    if (!selectedProduct) return
    setError("")
    setSaving(true)

    try {
      const numQuantity = Number(quantity)
      if (!numQuantity || numQuantity <= 0) {
        setError("Please enter a valid quantity.")
        setSaving(false)
        return
      }

      if (typeId && typeId !== String(selectedProduct.ingredient_type_id ?? "")) {
        const typeResponse = await fetch(
          `${API}/products/${selectedProduct.product_id}/ingredient-type`,
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ingredient_type_id: Number(typeId) }),
          }
        )
        if (!typeResponse.ok) {
          const data = await typeResponse.json().catch(() => null)
          throw new Error(data?.detail || "Could not set ingredient type.")
        }
      }

      const response = await fetch(
        `${API}/inventory/${inventory_id}/items`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            product_id: selectedProduct.product_id,
            quantity: numQuantity,
            quantity_unit: quantityUnit,
          }),
        }
      )
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || "Could not add item.")
      }
      onCreated()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add item.")
      setSaving(false)
    }
  }

  if (selectedProduct) {
    return (
      <div
        className="modal-backdrop"
        onMouseDown={onClose}
      >
        <div
          className="modal"
          onMouseDown={(event) => event.stopPropagation()}
        >
          <div className="modal-header">
            <div>
              <p className="eyebrow">ADD TO INVENTORY</p>
              <h2>Set quantity</h2>
            </div>

            <button
              className="modal-close"
              onClick={onClose}
              type="button"
              aria-label="Close"
              disabled={saving}
            >
              ×
            </button>
          </div>

          <div className="modal-body">
            <div className="form-group">
              <label>Product</label>
              <p>
                <strong>{selectedProduct.name}</strong>
              </p>
              {selectedProduct.brand && (
                <p className="muted">{selectedProduct.brand}</p>
              )}
            </div>

            <div className="form-group">
              <label>Ingredient type</label>
              <IngredientTypeSelect
                types={types}
                value={typeId}
                onChange={setTypeId}
                reloadTypes={loadTypes}
                placeholder="No ingredient type"
                disabled={saving}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Quantity</label>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  disabled={saving}
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>Unit</label>
                <select
                  value={quantityUnit}
                  onChange={(e) => setQuantityUnit(e.target.value)}
                  disabled={saving}
                >
                  <option value="unit">unit</option>
                  <option value="g">g</option>
                  <option value="kg">kg</option>
                  <option value="ml">ml</option>
                  <option value="l">l</option>
                </select>
              </div>
            </div>

            {error && <div className="form-error">{error}</div>}
          </div>

          <div className="modal-footer">
            <button
              className="secondary-button"
              onClick={() => (initialProduct ? onClose() : setSelectedProduct(null))}
              type="button"
              disabled={saving}
            >
              {initialProduct ? "Cancel" : "Back"}
            </button>

            <button
              className="primary-button"
              onClick={addItem}
              type="button"
              disabled={saving}
            >
              {saving ? "Adding..." : "Add item"}
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div
      className="modal-backdrop"
      onMouseDown={onClose}
    >
      <div
        className="modal"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">ADD TO INVENTORY</p>
            <h2>Add item</h2>
          </div>

          <button
            className="modal-close"
            onClick={onClose}
            type="button"
            aria-label="Close"
            disabled={saving}
          >
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="form-group">
            <label>Search for a product</label>
            <div className="search-row">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && searchProducts()}
                placeholder="e.g. Chicken, Milk"
                autoFocus
                disabled={searching || saving}
              />
              <button
                className="secondary-button"
                onClick={searchProducts}
                disabled={searching || saving || !query.trim()}
                type="button"
              >
                {searching ? "..." : "Search"}
              </button>
            </div>
          </div>

          <div className="form-group">
            <label>Supermarket</label>
            <select
              value={supermarket}
              onChange={(e) => setSupermarket(e.target.value)}
              disabled={searching || saving}
            >
              <option value="all">All supermarkets</option>
              <option value="morrisons">Morrisons</option>
              <option value="tesco">Tesco</option>
              <option value="sainsburys">Sainsbury's</option>
            </select>
          </div>

          {error && <div className="form-error">{error}</div>}

          {searching && <p className="muted">Searching...</p>}

          {products.length > 0 && (
            <div className="form-group" style={{ marginTop: 20 }}>
              <p className="eyebrow">Results</p>
              <div className="product-result-list">
                {products.map((product) => (
                  <button
                    key={product.product_id}
                    onClick={() => selectProduct(product)}
                    disabled={saving}
                    type="button"
                    className="product-result"
                  >
                    <div>
                      <strong>{product.name}</strong>
                      {product.brand && (
                        <p className="muted">{product.brand}</p>
                      )}
                      <p className="muted">
                        {product.currency} {product.price}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {!searching && query && products.length === 0 && !error && (
            <p className="muted">No products found.</p>
          )}
        </div>

        <div className="modal-footer">
          <button
            className="secondary-button"
            onClick={onClose}
            type="button"
            disabled={saving}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

export default CreateInventoryItem
