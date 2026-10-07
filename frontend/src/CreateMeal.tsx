import { getUserId } from "./auth"
import { useEffect, useState } from "react"
import IngredientTypeSelect from "./IngredientTypeSelect"

type IngredientType = {
  ingredient_type_id: number
  name: string
}

type IngredientDraft = {
  ingredient_type_id: string
  quantity: string
  quantity_unit: string
}

type CreateMealProps = {
  onClose: () => void
  onCreated: () => void
}

function CreateMeal({
  onClose,
  onCreated,
}: CreateMealProps) {
  const [name, setName] = useState("")
  const [portion, setPortion] = useState("2")
  const [portionUnit, setPortionUnit] = useState("servings")

  const [ingredientTypes, setIngredientTypes] = useState<
    IngredientType[]
  >([])

  const [ingredients, setIngredients] = useState<
    IngredientDraft[]
  >([])

  const [loadingTypes, setLoadingTypes] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")

    async function loadIngredientTypes() {
      try {
        const response = await fetch(
          "http://localhost:8000/api/ingredient-types"
        )

        if (!response.ok) {
          throw new Error()
        }

        const data: IngredientType[] = await response.json()

        setIngredientTypes(data)
      } catch {
        setError("Could not load ingredient types.")
      } finally {
        setLoadingTypes(false)
      }
    }

  useEffect(() => {
    loadIngredientTypes()
  }, [])

  function addIngredient() {
    setIngredients((current) => [
      ...current,
      {
        ingredient_type_id: "",
        quantity: "",
        quantity_unit: "g",
      },
    ])
  }

  function updateIngredient(
    index: number,
    field: keyof IngredientDraft,
    value: string
  ) {
    setIngredients((current) =>
      current.map((ingredient, ingredientIndex) =>
        ingredientIndex === index
          ? {
              ...ingredient,
              [field]: value,
            }
          : ingredient
      )
    )
  }

  function removeIngredient(index: number) {
    setIngredients((current) =>
      current.filter(
        (_, ingredientIndex) => ingredientIndex !== index
      )
    )
  }

  async function createMeal() {
    setError("")

    if (!name.trim()) {
      setError("Please enter a meal name.")
      return
    }

    if (!portion || Number(portion) <= 0) {
      setError("Please enter a valid portion.")
      return
    }

    for (const ingredient of ingredients) {
      if (
        !ingredient.ingredient_type_id ||
        !ingredient.quantity ||
        Number(ingredient.quantity) <= 0
      ) {
        setError("Please complete every ingredient.")
        return
      }
    }

    setSaving(true)

    try {
      const mealResponse = await fetch(
        "http://localhost:8000/api/meals",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: getUserId(),
            name: name.trim(),
            portion: Number(portion),
            portion_unit: portionUnit,
          }),
        }
      )

      if (!mealResponse.ok) {
        throw new Error("Could not create meal.")
      }

      const meal = await mealResponse.json()

      for (const ingredient of ingredients) {
        const ingredientResponse = await fetch(
          `http://localhost:8000/api/meals/${meal.meal_id}/ingredients`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              ingredient_type_id: Number(
                ingredient.ingredient_type_id
              ),
              quantity: Number(ingredient.quantity),
              quantity_unit: ingredient.quantity_unit,
            }),
          }
        )

        if (!ingredientResponse.ok) {
          throw new Error(
            "Meal was created, but an ingredient could not be added."
          )
        }
      }

      onCreated()
      onClose()
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Could not create meal."
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      className="modal-backdrop"
      onMouseDown={onClose}
    >
      <div
        className="modal"
        onMouseDown={(event) =>
          event.stopPropagation()
        }
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">NEW RECIPE</p>

            <h2>Create meal</h2>
          </div>

          <button
            className="modal-close"
            onClick={onClose}
            type="button"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="form-group">
            <label>Meal name</label>

            <input
              value={name}
              onChange={(event) =>
                setName(event.target.value)
              }
              placeholder="e.g. Chicken & Rice"
              autoFocus
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Serves</label>

              <input
                type="number"
                min="1"
                value={portion}
                onChange={(event) =>
                  setPortion(event.target.value)
                }
              />
            </div>

            <div className="form-group">
              <label>Unit</label>

              <select
                value={portionUnit}
                onChange={(event) =>
                  setPortionUnit(event.target.value)
                }
              >
                <option value="servings">
                  servings
                </option>
              </select>
            </div>
          </div>

          <div className="ingredients-heading">
            <div>
              <p className="eyebrow">RECIPE</p>

              <h3>Ingredients</h3>
            </div>

            <button
              className="secondary-button"
              onClick={addIngredient}
              type="button"
            >
              + Add ingredient
            </button>
          </div>

          {loadingTypes ? (
            <p className="muted">
              Loading ingredients...
            </p>
          ) : ingredients.length === 0 ? (
            <div className="ingredient-empty">
              <span>
                No ingredients added yet.
              </span>

              <button
                className="text-button"
                onClick={addIngredient}
                type="button"
              >
                Add one
              </button>
            </div>
          ) : (
            <div className="ingredient-editor">
              {ingredients.map(
                (ingredient, index) => (
                  <div
                    className="ingredient-row"
                    key={index}
                  >
                    <IngredientTypeSelect
                      types={ingredientTypes}
                      value={ingredient.ingredient_type_id}
                      onChange={(value) =>
                        updateIngredient(index, "ingredient_type_id", value)
                      }
                      reloadTypes={loadIngredientTypes}
                    />

                    <input
                      type="number"
                      min="0"
                      step="any"
                      placeholder="Quantity"
                      value={ingredient.quantity}
                      onChange={(event) =>
                        updateIngredient(
                          index,
                          "quantity",
                          event.target.value
                        )
                      }
                    />

                    <select
                      value={
                        ingredient.quantity_unit
                      }
                      onChange={(event) =>
                        updateIngredient(
                          index,
                          "quantity_unit",
                          event.target.value
                        )
                      }
                    >
                      <option value="unit">unit</option>
                      <option value="g">g</option>
                      <option value="kg">kg</option>
                      <option value="ml">ml</option>
                      <option value="l">l</option>
                    </select>

                    <button
                      className="ingredient-remove"
                      onClick={() =>
                        removeIngredient(index)
                      }
                      type="button"
                      aria-label="Remove ingredient"
                    >
                      ×
                    </button>
                  </div>
                )
              )}
            </div>
          )}

          {error && (
            <div className="form-error">
              {error}
            </div>
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

          <button
            className="primary-button"
            onClick={createMeal}
            type="button"
            disabled={saving}
          >
            {saving ? "Creating..." : "Create meal"}
          </button>
        </div>
      </div>
    </div>
  )
}

export default CreateMeal