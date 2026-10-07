import { useEffect, useState } from "react"

const API = "http://localhost:8000/api"

export const DATA_CHANGED_EVENT = "mealtrack:data-changed"

type SpendingPill = { limit: number | null; remaining: number | null }
type CaloriePill = { eaten: number; goal: number | null }

const money = (v: number) => `£${Number.isInteger(v) ? v : v.toFixed(2)}`

function StatusPills({ refreshKey }: { refreshKey: string }) {
  const [spending, setSpending] = useState<SpendingPill | null>(null)
  const [calories, setCalories] = useState<CaloriePill | null>(null)

  useEffect(() => {
    let active = true
    function load() {
      fetch(`${API}/stats/spending?range=monthly`)
        .then((r) => (r.ok ? r.json() : Promise.reject()))
        .then((d) => active && setSpending({ limit: d.limit, remaining: d.remaining }))
        .catch(() => active && setSpending(null))
      fetch(`${API}/stats/calories?range=daily`)
        .then((r) => (r.ok ? r.json() : Promise.reject()))
        .then((d) => active && setCalories({ eaten: d.today, goal: d.goal }))
        .catch(() => active && setCalories(null))
    }
    load()
    window.addEventListener(DATA_CHANGED_EVENT, load)
    return () => {
      active = false
      window.removeEventListener(DATA_CHANGED_EVENT, load)
    }
  }, [refreshKey])

  return (
    <>
      {!spending ? null : spending.limit !== null && spending.remaining !== null ? (
        <span
          className={`header-pill ${spending.remaining <= 0 ? "header-pill-warning" : "header-pill-spending"}`}
          title="Remaining this month / monthly spending limit"
        >
          {spending.remaining < 0 ? `${money(-spending.remaining)} over` : money(spending.remaining)} / {money(spending.limit)}
        </span>
      ) : (
        <span className="header-pill header-pill-neutral" title="Set a spending limit in Account">
          No limit
        </span>
      )}
      {!calories ? null : calories.goal !== null ? (
        <span className="header-pill header-pill-calories" title="Calories eaten today / daily goal">
          {Math.round(calories.eaten)} / {calories.goal} kcal
        </span>
      ) : (
        <span className="header-pill header-pill-neutral" title="Set a calorie goal in Account">
          {Math.round(calories.eaten)} kcal · no goal
        </span>
      )}
    </>
  )
}

export default StatusPills
