import { getUserId } from "./auth"
import { useEffect, useState } from "react"
import Shops from "./Shops"
import AnalyticsCard from "./AnalyticsCard"

import { API_URL } from "./config"
type Shortage = {
  meal_id: number
  meal_name: string
  ingredient_type_id: number
  ingredient_type_name: string
  required_quantity: number
  available_quantity: number
  missing_quantity: number
  quantity_unit: string
  incompatible_units: string[]
}

function formatQty(value: number) {
  return Number(value.toFixed(3)).toString()
}

type DashboardProps = {
  onNavigate: (page: string) => void
}

function Dashboard({ onNavigate }: DashboardProps) {
  const [inventoryCount, setInventoryCount] = useState<number | null>(null)
  const [mealCount, setMealCount] = useState<number | null>(null)
  const [shortages, setShortages] = useState<Shortage[] | null>(null)
  const [shortagesError, setShortagesError] = useState(false)

  useEffect(() => {
    fetch(`${API_URL}/api/inventory?user_id=${getUserId()}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => setInventoryCount(d.items.length))
      .catch(() => setInventoryCount(null))
    fetch(`${API_URL}/api/meals?user_id=${getUserId()}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => setMealCount(d.length))
      .catch(() => setMealCount(null))
    fetch(`${API_URL}/api/shortages?user_id=${getUserId()}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d: Shortage[]) => setShortages(d))
      .catch(() => setShortagesError(true))
  }, [])

  const mealsWithShortages = Array.from(
    (shortages ?? []).reduce((map, item) => {
      const entry = map.get(item.meal_id) ?? [item.meal_id, item.meal_name, [] as Shortage[]]
      entry[2].push(item)
      return map.set(item.meal_id, entry)
    }, new Map<number, [number, string, Shortage[]]>()).values()
  )

  return (
    <div className="page-content">
      <section className="welcome-row">
        <div>
          <p className="eyebrow">YOUR FOOD AT A GLANCE</p>
          <h2>Welcome back.</h2>
          <p className="muted">
            Keep your meals, inventory and shopping in one place.
          </p>
        </div>
      </section>

      <section className="stat-grid">
        <button className="stat-card accent-card stat-button" onClick={() => onNavigate("Inventory")}>
          <div className="stat-icon">▣</div>
          <div>
            <span className="stat-label">INVENTORY</span>
            <strong>{inventoryCount ?? "–"}</strong>
            <span className="stat-note">items tracked</span>
          </div>
        </button>

        <button className="stat-card stat-button" onClick={() => onNavigate("Meals")}>
          <div className="stat-icon">◈</div>
          <div>
            <span className="stat-label">MEALS</span>
            <strong>{mealCount ?? "–"}</strong>
            <span className="stat-note">meals saved</span>
          </div>
        </button>

      </section>

      <section className="analytics-section">
        <AnalyticsCard />
      </section>

      <section className="dashboard-grid">
        <div className="panel meal-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">MEALS</p>
              <h3>Meals with missing products</h3>
            </div>
            <button className="text-button" onClick={() => onNavigate("Meals")}>
              View all
            </button>
          </div>

          {shortagesError ? (
            <p className="error-message">Could not load missing products.</p>
          ) : shortages === null ? (
            <p className="muted">Loading...</p>
          ) : mealsWithShortages.length === 0 ? (
            <div className="empty-panel">
              <div className="empty-icon">◈</div>
              <strong>No missing products</strong>
              <span className="muted">Your inventory covers all of your meals.</span>
              <button className="secondary-button" onClick={() => onNavigate("Meals")}>
                Go to Meals
              </button>
            </div>
          ) : (
            <ul className="shortage-list">
              {mealsWithShortages.map(([mealId, name, items]) => (
                <li key={mealId}>
                  <strong>{name}</strong>
                  <span className="muted">
                    {items.length} missing ingredient{items.length === 1 ? "" : "s"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="panel shopping-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">INVENTORY</p>
              <h3>Missing products</h3>
            </div>
          </div>

          {shortagesError ? (
            <p className="error-message">Could not load missing products.</p>
          ) : shortages === null ? (
            <p className="muted">Loading...</p>
          ) : shortages.length === 0 ? (
            <div className="empty-panel compact">
              <div className="empty-icon">□</div>
              <strong>No missing products</strong>
              <span className="muted">Nothing is missing for your meals.</span>
            </div>
          ) : (
            <ul className="shortage-list">
              {shortages.map((item) => (
                <li key={`${item.meal_id}-${item.ingredient_type_id}-${item.quantity_unit}`}>
                  <strong>{item.ingredient_type_name}</strong>
                  <span className="muted">
                    {item.meal_name}: {formatQty(item.missing_quantity)} {item.quantity_unit} missing
                    {" "}(need {formatQty(item.required_quantity)}, have {formatQty(item.available_quantity)})
                    {item.incompatible_units.length > 0 &&
                      ` – stock in ${item.incompatible_units.join(", ")} can't be compared`}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <section className="shops-section">
        <Shops />
      </section>
    </div>
  )
}

export default Dashboard
