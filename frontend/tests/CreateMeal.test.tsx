import { describe, it, expect, beforeEach, vi } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import CreateMeal from "../src/CreateMeal"
import { mockFetchOnce } from "./test-utils"

describe("CreateMeal", () => {
  const mockOnClose = vi.fn()
  const mockOnCreated = vi.fn()

  beforeEach(() => {
    mockOnClose.mockClear()
    mockOnCreated.mockClear()
    vi.clearAllMocks()
    localStorage.setItem(
      "mealtrack-session",
      JSON.stringify({
        user_id: 1,
        username: "testuser",
        postcode: null,
        token: "test-token",
      })
    )
  })

  it("loads ingredient types on mount", async () => {
    const mockIngredientTypes = [
      { ingredient_type_id: 1, name: "Pasta" },
      { ingredient_type_id: 2, name: "Tomato" },
    ]
    mockFetchOnce(/\/api\/ingredient-types/, mockIngredientTypes)

    render(<CreateMeal onClose={mockOnClose} onCreated={mockOnCreated} />)

    await waitFor(() => {
      expect(screen.getByText("Meal name")).toBeInTheDocument()
    })
  })
})
