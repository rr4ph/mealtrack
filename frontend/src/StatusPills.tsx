import { useEffect, useState } from "react"

import { API_URL } from "./config"
const API = `${API_URL}/api`

export const DATA_CHANGED_EVENT = "mealtrack:data-changed"

type CaloriePill = { eaten: number; goal: number | null }

function StatusPills({ refreshKey }: { refreshKey: string }) {
  const [calories, setCalories] = useState<CaloriePill | null>(null)

  useEffect(() => {
    let active = true
    function load() {
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
