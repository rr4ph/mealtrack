import { getUserId } from "./auth"
import { useEffect, useState } from "react"
import CreateMeal from "./CreateMeal"
import MealDetails from "./MealDetails"

import { API_URL } from "./config"
type Meal = {
  meal_id: number
  user_id: number
  name: string
  portion: number
  portion_unit: string
}

function Meals() {
  const [meals, setMeals] = useState<Meal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [showCreateMeal, setShowCreateMeal] = useState(false)
  const [selectedMeal, setSelectedMeal] = useState<Meal | null>(null)
  const [detailsVersion, setDetailsVersion] = useState(0)

  async function loadMeals() {
    setLoading(true)
    setError("")

    try {
      const response = await fetch(
        `${API_URL}/api/meals?user_id=${getUserId()}`
      )

      if (!response.ok) {
        throw new Error("Could not load meals")
      }

      const data: Meal[] = await response.json()
      setMeals(data)
    } catch {
      setError("Could not load your meals.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMeals()
  }, [])

  if (loading) {
    return (
      <div className="page-content">
        <div className="empty-page">
          <span className="muted">Loading meals...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-content">
        <div className="empty-page">
          <strong>{error}</strong>

          <button
            className="secondary-button"
            onClick={loadMeals}
          >
            Try again
          </button>
        </div>
      </div>
    )
  }

  if (selectedMeal) {
    return (
        <MealDetails
          key={`${selectedMeal.meal_id}-${detailsVersion}`}
          meal={selectedMeal}
          onBack={() => setSelectedMeal(null)}
          onUpdated={(updatedMeal) => {
            setSelectedMeal(updatedMeal)
            setMeals((current) => current.map((meal) =>
              meal.meal_id === updatedMeal.meal_id ? updatedMeal : meal
            ))
            setDetailsVersion((current) => current + 1)
          }}
          onDeleted={() => {
            setSelectedMeal(null)
            loadMeals()
          }}
        />
    )
    }

  return (
    <>
      <div className="page-content">
        <section className="page-heading">
          <div>
            <p className="eyebrow">YOUR RECIPES</p>

            <h2>Meals</h2>

            <p className="muted">
              Manage your meals and their ingredients.
            </p>
          </div>

          <button
            className="primary-button"
            onClick={() => setShowCreateMeal(true)}
          >
            + Add meal
          </button>
        </section>

        {meals.length === 0 ? (
          <section className="panel empty-page">
            <div className="empty-icon">◈</div>

            <strong>No meals yet</strong>

            <span className="muted">
              Create your first meal to start tracking its ingredients.
            </span>

            <button
              className="primary-button"
              onClick={() => setShowCreateMeal(true)}
            >
              + Create your first meal
            </button>
          </section>
        ) : (
          <section className="meal-card-grid">
            {meals.map((meal) => (
              <article
                className="meal-card"
                key={meal.meal_id}
              >
                <div className="meal-card-icon">
                  ◈
                </div>

                <div className="meal-card-body">
                  <h3>{meal.name}</h3>

                  <span className="meal-card-portion">
                    {meal.portion} {meal.portion_unit}
                  </span>
                </div>

                <div className="meal-card-footer">
                  <span>
                    Meal #{meal.meal_id}
                  </span>

                  <button
                    className="text-button"
                    onClick={() => setSelectedMeal(meal)}
                    >
                    View →
                    </button>
                </div>
              </article>
            ))}
          </section>
        )}
      </div>

      {showCreateMeal && (
        <CreateMeal
          onClose={() => setShowCreateMeal(false)}
          onCreated={loadMeals}
        />
      )}
    </>
  )
}

export default Meals
