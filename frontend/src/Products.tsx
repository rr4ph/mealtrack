import { useEffect, useMemo, useState } from "react"
import { type IngredientType } from "./IngredientTypeSelect"
import CreateInventoryItem from "./CreateInventoryItem"
import BuyProduct from "./BuyProduct"
import { getUserId } from "./auth"

const API = "http://localhost:8000/api"

type Product = {
  product_id: number
  name: string
  brand: string | null
  supermarket: string
  price: number
  currency: string
  pack_size: string | null
  unit_price: number | null
  unit_name: string | null
  ingredient_type_id: number | null
  ingredient_type_name?: string | null
  last_price_update_at?: string | null
}

type SortKey = "name" | "price" | "updated"

function formatMoney(value: number, currency: string) {
  try {
    return new Intl.NumberFormat("en-GB", { style: "currency", currency }).format(value)
  } catch {
    return `${currency} ${value.toFixed(2)}`
  }
}

function Products() {
  const [query, setQuery] = useState("")
  const [supermarket, setSupermarket] = useState("all")
  const [sort, setSort] = useState<SortKey>("name")
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [searched, setSearched] = useState(false)

  const [types, setTypes] = useState<IngredientType[]>([])
  const [typesError, setTypesError] = useState("")
  const [newType, setNewType] = useState("")
  const [inventoryId, setInventoryId] = useState<number | null>(null)
  const [mergingType, setMergingType] = useState<IngredientType | null>(null)
  const [mergeTargetId, setMergeTargetId] = useState("")
  const [merging, setMerging] = useState(false)
  const [mergeError, setMergeError] = useState("")
  const [typesMessage, setTypesMessage] = useState("")
  const [addingProduct, setAddingProduct] = useState<Product | null>(null)
  const [buyingProduct, setBuyingProduct] = useState<Product | null>(null)
  const [buyMessage, setBuyMessage] = useState("")

  async function loadTypes() {
    try {
      const response = await fetch(`${API}/ingredient-types`)
      if (!response.ok) throw new Error()
      setTypes(await response.json())
      setTypesError("")
    } catch {
      setTypesError("Could not load ingredient types.")
    }
  }

  useEffect(() => {
    loadTypes()
    fetch(`${API}/inventory?user_id=${getUserId()}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => setInventoryId(d.inventory_id))
      .catch(() => setInventoryId(null))
  }, [])

  async function createType() {
    const name = newType.trim()
    if (!name) return
    if (types.some((t) => t.name.toLowerCase() === name.toLowerCase())) {
      setTypesError("That ingredient type already exists.")
      return
    }
    try {
      const response = await fetch(`${API}/ingredient-types`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      })
      if (!response.ok) {
        const data = await response.json().catch(() => null)
        throw new Error(data?.detail || "Could not create ingredient type.")
      }
      setNewType("")
      await loadTypes()
    } catch (err) {
      setTypesError(err instanceof Error ? err.message : "Could not create ingredient type.")
    }
  }

  async function mergeType() {
    if (!mergingType || !mergeTargetId) return
    const keptId = Number(mergeTargetId)
    if (keptId === mergingType.ingredient_type_id) {
      setMergeError("Cannot merge a type into itself.")
      return
    }
    const target = types.find((t) => t.ingredient_type_id === keptId)
    setMerging(true)
    setMergeError("")
    try {
      const response = await fetch(`${API}/ingredient-types/merge`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kept_id: keptId, deleted_id: mergingType.ingredient_type_id }),
      })
      if (!response.ok) {
        const data = await response.json().catch(() => null)
        throw new Error(typeof data?.detail === "string" ? data.detail : "Could not merge ingredient types.")
      }
      setTypesMessage(`Merged "${mergingType.name}" into "${target?.name ?? ""}".`)
      setMergingType(null)
      setMergeTargetId("")
      await loadTypes()
      if (query.trim()) await search()
    } catch (err) {
      setMergeError(err instanceof Error ? err.message : "Could not merge ingredient types.")
    } finally {
      setMerging(false)
    }
  }

  async function search() {
    const text = query.trim()
    if (!text) return
    setLoading(true)
    setError("")

    try {
      const response = await fetch(
        `${API}/products?query=${encodeURIComponent(text)}&supermarket=${supermarket}`
      )
      if (!response.ok) {
        const data = await response.json().catch(() => null)
        throw new Error(data?.detail || "Could not search products.")
      }
      setProducts(await response.json())
      setSearched(true)
    } catch (err) {
      setProducts([])
      setError(err instanceof Error ? err.message : "Could not search products.")
    } finally {
      setLoading(false)
    }
  }

  const sorted = useMemo(() => {
    const list = [...products]
    if (sort === "name") list.sort((a, b) => a.name.localeCompare(b.name))
    else if (sort === "price") list.sort((a, b) => a.price - b.price)
    else {
      const time = (p: Product) => (p.last_price_update_at ? Date.parse(p.last_price_update_at) || 0 : 0)
      list.sort((a, b) => time(b) - time(a))
    }
    return list
  }, [products, sort])

  return (
    <div className="page-content">
      <section className="page-heading">
        <div>
          <p className="eyebrow">SUPERMARKETS</p>
          <h2>Products</h2>
          <p className="muted">Search and compare products across supermarkets.</p>
        </div>
      </section>

      <section className="panel products-toolbar">
        <div className="search-bar">
          <span className="search-icon">⌕</span>
          <input
            type="text"
            placeholder="Search for a product..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && search()}
          />
          <button type="button" onClick={search} disabled={loading || !query.trim()}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        <div className="products-filters">
          <div className="form-group">
            <label>Supermarket</label>
            <select value={supermarket} onChange={(e) => setSupermarket(e.target.value)}>
              <option value="all">All</option>
              <option value="morrisons">Morrisons</option>
              <option value="tesco">Tesco</option>
              <option value="sainsburys">Sainsbury's</option>
            </select>
          </div>
          <div className="form-group">
            <label>Sort by</label>
            <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)}>
              <option value="name">Alphabetical</option>
              <option value="price">Price</option>
              <option value="updated">Last updated</option>
            </select>
          </div>
        </div>
      </section>

      <section className="panel ingredient-types-panel">
        <div>
          <p className="eyebrow">CLASSIFICATION</p>
          <h3>Ingredient types</h3>
          <p className="muted">Products are matched to these types when saved.</p>
        </div>
        <div className="ingredient-type-list">
          {types.length === 0 ? (
            <span className="muted">No ingredient types yet.</span>
          ) : (
            types.map((t) => (
              <span className="ingredient-type-chip" key={t.ingredient_type_id}>
                {t.name}
                <button
                  type="button"
                  className="secondary-button chip-merge-button"
                  disabled={types.length < 2}
                  onClick={() => {
                    setMergingType(t)
                    setMergeTargetId("")
                    setMergeError("")
                    setTypesMessage("")
                  }}
                >
                  Merge
                </button>
              </span>
            ))
          )}
        </div>
        <div className="search-bar">
          <input
            type="text"
            placeholder="New ingredient type..."
            value={newType}
            onChange={(e) => setNewType(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && createType()}
          />
          <button type="button" onClick={createType} disabled={!newType.trim()}>Add</button>
        </div>
        {typesError && <p className="error-message">{typesError}</p>}
        {typesMessage && <p className="muted">{typesMessage}</p>}
      </section>

      {error && <p className="error-message">{error}</p>}
      {buyMessage && <p className="muted">{buyMessage}</p>}

      {loading ? (
        <section className="panel empty-page">
          <strong>Searching supermarkets...</strong>
        </section>
      ) : sorted.length > 0 ? (
        <section className="products-grid">
          {sorted.map((p) => (
            <article className="product-tile" key={`${p.supermarket}-${p.product_id}`}>
              <span className="product-supermarket">{p.supermarket.toUpperCase()}</span>
              <h4>{p.name}</h4>
              {p.brand && <span className="product-brand">{p.brand}</span>}
              <span className="product-type">{p.ingredient_type_name ?? "Unclassified"}</span>
              <strong className="product-tile-price">{formatMoney(p.price, p.currency)}</strong>
              <div className="product-tile-meta">
                {p.pack_size && <span>Pack: {p.pack_size}</span>}
                {p.unit_price != null && p.unit_name && (
                  <span>{formatMoney(p.unit_price, p.currency)} / {p.unit_name}</span>
                )}
                {p.last_price_update_at && (
                  <span>Updated {new Date(p.last_price_update_at).toLocaleDateString("en-GB")}</span>
                )}
              </div>
              <button
                type="button"
                className="secondary-button product-tile-action"
                disabled={inventoryId === null}
                onClick={() => setAddingProduct(p)}
              >
                Add to inventory
              </button>
              <button
                type="button"
                className="primary-button product-tile-action"
                onClick={() => setBuyingProduct(p)}
              >
                Buy
              </button>
            </article>
          ))}
        </section>
      ) : (
        !error && (
          <section className="panel empty-page">
            <div className="empty-icon">⌕</div>
            <strong>{searched ? "No products found" : "Search for a product"}</strong>
            <span className="muted">
              {searched ? "Try a different search or supermarket." : "Results will appear here."}
            </span>
          </section>
        )
      )}
      {mergingType && (
        <div className="modal-backdrop">
          <div className="modal confirmation-modal">
            <div className="modal-header">
              <h2>Merge "{mergingType.name}" into:</h2>
            </div>
            <div className="modal-body">
              <select value={mergeTargetId} onChange={(e) => setMergeTargetId(e.target.value)} disabled={merging}>
                <option value="">Select a type...</option>
                {types
                  .filter((t) => t.ingredient_type_id !== mergingType.ingredient_type_id)
                  .map((t) => (
                    <option key={t.ingredient_type_id} value={t.ingredient_type_id}>{t.name}</option>
                  ))}
              </select>
              <p className="muted">
                All meal ingredients and products using "{mergingType.name}" will move to the selected type, and "{mergingType.name}" will be removed.
              </p>
              {mergeError && <p className="error-message">{mergeError}</p>}
            </div>
            <div className="modal-footer">
              <button type="button" className="secondary-button" onClick={() => setMergingType(null)} disabled={merging}>
                Cancel
              </button>
              <button type="button" className="primary-button" onClick={mergeType} disabled={merging || !mergeTargetId}>
                {merging ? "Merging..." : "Confirm merge"}
              </button>
            </div>
          </div>
        </div>
      )}
      {buyingProduct && (
        <BuyProduct
          product={buyingProduct}
          onClose={() => setBuyingProduct(null)}
          onBought={(message) => {
            setBuyingProduct(null)
            setBuyMessage(message)
          }}
        />
      )}
      {addingProduct && inventoryId !== null && (
        <CreateInventoryItem
          inventory_id={inventoryId}
          initialProduct={addingProduct}
          onClose={() => setAddingProduct(null)}
          onCreated={() => setAddingProduct(null)}
        />
      )}
    </div>
  )
}

export default Products
