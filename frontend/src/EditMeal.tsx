import { getUserId } from "./auth"
import { useEffect, useState } from "react"
import IngredientTypeSelect from "./IngredientTypeSelect"

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

type IngredientDraft = {
  ingredient_id?: number
  ingredient_type_id: string
  quantity: string
  quantity_unit: string
}

type EditMealProps = {
  meal: Meal
  onClose: () => void
  onUpdated: (meal: Meal) => void
}

function EditMeal({ meal, onClose, onUpdated }: EditMealProps) {
  const [name, setName] = useState(meal.name)
  const [portion, setPortion] = useState(String(meal.portion))
  const [portionUnit, setPortionUnit] = useState(meal.portion_unit)
  const [ingredientTypes, setIngredientTypes] = useState<IngredientType[]>([])
  const [ingredients, setIngredients] = useState<IngredientDraft[]>([])
  const [originalIngredients, setOriginalIngredients] = useState<Ingredient[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")

  async function loadIngredientTypes() {
    const response = await fetch("http://localhost:8000/api/ingredient-types")
    if (!response.ok) throw new Error("Could not reload ingredient types.")
    setIngredientTypes(await response.json())
  }

  useEffect(() => {
    async function loadData() {
      setLoading(true)
      setError("")

      try {
        const [ingredientsResponse, typesResponse] = await Promise.all([
          fetch(`http://localhost:8000/api/meals/${meal.meal_id}/ingredients?user_id=${getUserId()}`),
          fetch("http://localhost:8000/api/ingredient-types"),
        ])

        if (!ingredientsResponse.ok || !typesResponse.ok) {
          throw new Error()
        }

        const ingredientsData: Ingredient[] = await ingredientsResponse.json()
        const typesData: IngredientType[] = await typesResponse.json()

        setOriginalIngredients(ingredientsData)
        setIngredients(
          ingredientsData.map((ingredient) => ({
            ingredient_id: ingredient.ingredient_id,
            ingredient_type_id: String(ingredient.ingredient_type_id),
            quantity: String(ingredient.quantity),
            quantity_unit: ingredient.quantity_unit,
          }))
        )
        setIngredientTypes(typesData)
      } catch {
        setError("Could not load meal ingredients.")
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [meal.meal_id])

  function addIngredient() {
    setIngredients((current) => [
      ...current,
      { ingredient_type_id: "", quantity: "", quantity_unit: "g" },
    ])
  }

  function updateIngredient(
    index: number,
    field: keyof IngredientDraft,
    value: string
  ) {
    setIngredients((current) =>
      current.map((ingredient, ingredientIndex) =>
        ingredientIndex === index ? { ...ingredient, [field]: value } : ingredient
      )
    )
  }

  async function removeIngredient(index: number) {
    const target = ingredients[index]

    if (target.ingredient_id) {
      setError("")
      setSaving(true)
      try {
        const response = await fetch(
          `http://localhost:8000/api/meals/${meal.meal_id}/ingredients/${target.ingredient_id}`,
          { method: "DELETE" }
        )
        if (!response.ok) throw new Error()
        setOriginalIngredients((current) =>
          current.filter((item) => item.ingredient_id !== target.ingredient_id)
        )
      } catch {
        setError("Could not remove ingredient.")
        setSaving(false)
        return
      }
      setSaving(false)
    }

    setIngredients((current) =>
      current.filter((_, ingredientIndex) => ingredientIndex !== index)
    )
  }

  async function saveMeal() {
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
      if (!ingredient.ingredient_type_id || !ingredient.quantity || Number(ingredient.quantity) <= 0) {
        setError("Please complete every ingredient.")
        return
      }
    }

    setSaving(true)

    try {
      const mealResponse = await fetch(`http://localhost:8000/api/meals/${meal.meal_id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: getUserId(),
          name: name.trim(),
          portion: Number(portion),
          portion_unit: portionUnit,
        }),
      })

      if (!mealResponse.ok) {
        throw new Error("Could not update meal.")
      }

      const remainingIngredientIds = new Set(
        ingredients.flatMap((ingredient) => ingredient.ingredient_id ? [ingredient.ingredient_id] : [])
      )

      for (const ingredient of originalIngredients) {
        if (!remainingIngredientIds.has(ingredient.ingredient_id)) {
          const response = await fetch(
            `http://localhost:8000/api/meals/${meal.meal_id}/ingredients/${ingredient.ingredient_id}`,
            { method: "DELETE" }
          )

          if (!response.ok) {
            throw new Error("Meal was updated, but an ingredient could not be removed.")
          }
        }
      }

      for (const ingredient of ingredients) {
        const body = JSON.stringify({
          ingredient_type_id: Number(ingredient.ingredient_type_id),
          quantity: Number(ingredient.quantity),
          quantity_unit: ingredient.quantity_unit,
        })
        const url = ingredient.ingredient_id
          ? `http://localhost:8000/api/meals/${meal.meal_id}/ingredients/${ingredient.ingredient_id}`
          : `http://localhost:8000/api/meals/${meal.meal_id}/ingredients`
        const response = await fetch(url, {
          method: ingredient.ingredient_id ? "PATCH" : "POST",
          headers: { "Content-Type": "application/json" },
          body,
        })

        if (!response.ok) {
          throw new Error("Meal was updated, but an ingredient could not be saved.")
        }
      }

      const updatedMeal: Meal = await mealResponse.json()
      onUpdated(updatedMeal)
      onClose()
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Could not update meal.")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-backdrop" onMouseDown={onClose}>
      <div className="modal" onMouseDown={(event) => event.stopPropagation()}>
        <div className="modal-header">
          <div>
            <p className="eyebrow">EDIT RECIPE</p>
            <h2>Edit meal</h2>
          </div>
          <button className="modal-close" onClick={onClose} type="button" aria-label="Close" disabled={saving}>
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="form-group">
            <label>Meal name</label>
            <input value={name} onChange={(event) => setName(event.target.value)} autoFocus />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Serves</label>
              <input type="number" min="1" value={portion} onChange={(event) => setPortion(event.target.value)} />
            </div>
            <div className="form-group">
              <label>Unit</label>
              <select value={portionUnit} onChange={(event) => setPortionUnit(event.target.value)}>
                <option value="servings">servings</option>
              </select>
            </div>
          </div>

          <div className="ingredients-heading">
            <div>
              <p className="eyebrow">RECIPE</p>
              <h3>Ingredients</h3>
            </div>
            <button className="secondary-button" onClick={addIngredient} type="button" disabled={loading || saving}>
              + Add ingredient
            </button>
          </div>

          {loading ? (
            <p className="muted">Loading ingredients...</p>
          ) : (
            <div className="ingredient-editor">
              {ingredients.map((ingredient, index) => (
                <div className="ingredient-row" key={ingredient.ingredient_id ?? `new-${index}`}>
                  <IngredientTypeSelect
                    types={ingredientTypes}
                    value={ingredient.ingredient_type_id}
                    onChange={(value) => updateIngredient(index, "ingredient_type_id", value)}
                    reloadTypes={loadIngredientTypes}
                    disabled={saving}
                  />
                  <input type="number" min="0" step="any" placeholder="Quantity" value={ingredient.quantity} onChange={(event) => updateIngredient(index, "quantity", event.target.value)} disabled={saving} />
                  <select value={ingredient.quantity_unit} onChange={(event) => updateIngredient(index, "quantity_unit", event.target.value)} disabled={saving}>
                    <option value="unit">unit</option>
                    <option value="g">g</option>
                    <option value="kg">kg</option>
                    <option value="ml">ml</option>
                    <option value="l">l</option>
                  </select>
                  <button className="ingredient-remove ingredient-remove-text" onClick={() => removeIngredient(index)} type="button" aria-label="Remove ingredient" disabled={saving}>Remove</button>
                </div>
              ))}
              {ingredients.length === 0 && <div className="ingredient-empty">No ingredients added yet.</div>}
            </div>
          )}

          {error && <div className="form-error">{error}</div>}
        </div>

        <div className="modal-footer">
          <button className="secondary-button" onClick={onClose} type="button" disabled={saving}>Cancel</button>
          <button className="primary-button" onClick={saveMeal} type="button" disabled={loading || saving}>
            {saving ? "Saving..." : "Save changes"}
          </button>
        </div>
      </div>
    </div>
  )
}

export default EditMeal
