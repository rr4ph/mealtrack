import { getUserId } from "./auth"
import { useEffect, useState } from "react"
import EditMeal from "./EditMeal"

type Meal = {
  meal_id: number
  user_id: number
  name: string
  portion: number
  portion_unit: string
}

type Ingredient = {
  ingredient_id: number
  meal_id: number
  ingredient_type_id: number
  quantity: number
  quantity_unit: string
}

type IngredientType = {
  ingredient_type_id: number
  name: string
}

type MealDetailsProps = {
  meal: Meal
  onBack: () => void
  onUpdated: (meal: Meal) => void
  onDeleted: () => void
}

function MealDetails({
  meal,
  onBack,
  onUpdated,
  onDeleted,
}: MealDetailsProps) {
  const [ingredients, setIngredients] = useState<Ingredient[]>([])
  const [ingredientTypes, setIngredientTypes] = useState<
    IngredientType[]
  >([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [showEditMeal, setShowEditMeal] = useState(false)
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState("")

  useEffect(() => {
    async function loadData() {
      setLoading(true)
      setError("")

      try {
        const [ingredientsResponse, typesResponse] =
          await Promise.all([
            fetch(
              `http://localhost:8000/api/meals/${meal.meal_id}/ingredients?user_id=${getUserId()}`
            ),
            fetch(
              "http://localhost:8000/api/ingredient-types"
            ),
          ])

        if (
          !ingredientsResponse.ok ||
          !typesResponse.ok
        ) {
          throw new Error()
        }

        const ingredientsData: Ingredient[] =
          await ingredientsResponse.json()

        const typesData: IngredientType[] =
          await typesResponse.json()

        setIngredients(ingredientsData)
        setIngredientTypes(typesData)
      } catch {
        setError("Could not load meal details.")
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [meal.meal_id])

  function getIngredientName(
    ingredientTypeId: number
  ) {
    const type = ingredientTypes.find(
      (item) =>
        item.ingredient_type_id === ingredientTypeId
    )

    return type?.name ?? "Unknown ingredient"
  }

  async function deleteMeal() {
    setDeleting(true)
    setDeleteError("")

    try {
      const response = await fetch(
        `http://localhost:8000/api/meals/${meal.meal_id}?user_id=${getUserId()}`,
        { method: "DELETE" }
      )

      if (!response.ok) {
        throw new Error()
      }

      onDeleted()
    } catch {
      setDeleteError("Could not delete this meal. Please try again.")
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="page-content">
      <button
        className="back-button"
        onClick={onBack}
        type="button"
      >
        ← Back to meals
      </button>

      <section className="meal-detail-heading">
        <div>
          <p className="eyebrow">RECIPE</p>

          <h2>{meal.name}</h2>

          <p className="muted">
            Serves {meal.portion} {meal.portion_unit}
          </p>
        </div>

        <div className="meal-detail-actions">
          <button
            className="secondary-button compact-button"
            onClick={() => setShowEditMeal(true)}
            type="button"
          >
            Edit meal
          </button>

          <button
            className="danger-button compact-button"
            onClick={() => setShowDeleteConfirmation(true)}
            type="button"
          >
            Delete
          </button>
        </div>
      </section>

      <section className="panel meal-ingredients-panel">
        <div className="meal-ingredients-header">
          <div>
            <p className="eyebrow">RECIPE</p>

            <h3>Ingredients</h3>
          </div>

          <span className="muted">
            {ingredients.length}{" "}
            {ingredients.length === 1
              ? "ingredient"
              : "ingredients"}
          </span>
        </div>

        {loading ? (
          <div className="ingredient-detail-empty">
            <span className="muted">
              Loading ingredients...
            </span>
          </div>
        ) : error ? (
          <div className="ingredient-detail-empty">
            <strong>{error}</strong>
          </div>
        ) : ingredients.length === 0 ? (
          <div className="ingredient-detail-empty">
            <span className="muted">
              No ingredients added yet.
            </span>
          </div>
        ) : (
          <div className="ingredient-detail-list">
            {ingredients.map((ingredient) => (
              <div
                className="ingredient-detail-row"
                key={ingredient.ingredient_id}
              >
                <div className="ingredient-detail-name">
                  <div className="ingredient-detail-icon">
                    ◈
                  </div>

                  <span>
                    {getIngredientName(
                      ingredient.ingredient_type_id
                    )}
                  </span>
                </div>

                <span className="ingredient-detail-quantity">
                  {ingredient.quantity}{" "}
                  {ingredient.quantity_unit}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      {showEditMeal && (
        <EditMeal
          meal={meal}
          onClose={() => setShowEditMeal(false)}
          onUpdated={onUpdated}
        />
      )}

      {showDeleteConfirmation && (
        <div className="modal-backdrop" onMouseDown={() => !deleting && setShowDeleteConfirmation(false)}>
          <div className="modal confirmation-modal" onMouseDown={(event) => event.stopPropagation()}>
            <div className="modal-header">
              <div>
                <p className="eyebrow">DELETE RECIPE</p>
                <h2>Delete {meal.name}?</h2>
              </div>
              <button className="modal-close" onClick={() => setShowDeleteConfirmation(false)} type="button" aria-label="Close" disabled={deleting}>×</button>
            </div>
            <div className="modal-body">
              <p className="muted">This will permanently remove the meal and its ingredients.</p>
              {deleteError && <div className="form-error">{deleteError}</div>}
            </div>
            <div className="modal-footer">
              <button className="secondary-button" onClick={() => setShowDeleteConfirmation(false)} type="button" disabled={deleting}>Cancel</button>
              <button className="danger-button" onClick={deleteMeal} type="button" disabled={deleting}>{deleting ? "Deleting..." : "Delete meal"}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MealDetails
