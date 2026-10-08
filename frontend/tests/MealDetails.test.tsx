import { describe, it, expect, beforeEach, vi } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import MealDetails from "../src/MealDetails"
import { mockFetchOnce } from "./test-utils"

describe("MealDetails", () => {
  const mockOnBack = vi.fn()
  const mockOnUpdated = vi.fn()
  const mockOnDeleted = vi.fn()

  const mockMeal = {
    meal_id: 1,
    user_id: 1,
    name: "Pasta Carbonara",
    portion: 2,
    portion_unit: "servings",
  }

  beforeEach(() => {
    mockOnBack.mockClear()
    mockOnUpdated.mockClear()
    mockOnDeleted.mockClear()
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

  it("renders meal details", async () => {
    mockFetchOnce(/\/api\/meals\/1\/ingredients/, [])
    mockFetchOnce(/\/api\/ingredient-types/, [])
    mockFetchOnce(/\/api\/calories/, {})

    render(
      <MealDetails
        meal={mockMeal}
        onBack={mockOnBack}
        onUpdated={mockOnUpdated}
        onDeleted={mockOnDeleted}
      />
    )

    await waitFor(() => {
      expect(screen.getByText("Pasta Carbonara")).toBeInTheDocument()
    })
  })

  it("shows back button and calls onBack when clicked", async () => {
    const user = userEvent.setup()
    mockFetchOnce(/\/api\/meals\/1\/ingredients/, [])
    mockFetchOnce(/\/api\/ingredient-types/, [])
    mockFetchOnce(/\/api\/calories/, {})

    render(
      <MealDetails
        meal={mockMeal}
        onBack={mockOnBack}
        onUpdated={mockOnUpdated}
        onDeleted={mockOnDeleted}
      />
    )

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /← Back/ })).toBeInTheDocument()
    })

    await user.click(screen.getByRole("button", { name: /← Back/ }))
    expect(mockOnBack).toHaveBeenCalled()
  })

  it("displays error message on load failure", async () => {
    mockFetchOnce(/\/api\/meals\/1\/ingredients/, { detail: "Error" }, 500)
    mockFetchOnce(/\/api\/ingredient-types/, [])
    mockFetchOnce(/\/api\/calories/, {})

    render(
      <MealDetails
        meal={mockMeal}
        onBack={mockOnBack}
        onUpdated={mockOnUpdated}
        onDeleted={mockOnDeleted}
      />
    )

    await waitFor(() => {
      expect(screen.getByText("Could not load meal details.")).toBeInTheDocument()
    })
  })
})
