import { describe, it, expect, beforeEach, vi } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import Meals from "../src/Meals"
import { mockFetchOnce } from "./test-utils"

describe("Meals", () => {
  beforeEach(() => {
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

  it("renders loading state initially", () => {
    mockFetchOnce(/\/api\/meals/, [])
    render(<Meals />)
    expect(screen.getByText("Loading meals...")).toBeInTheDocument()
  })

  it("renders meals returned by API", async () => {
    const mockMeals = [
      {
        meal_id: 1,
        user_id: 1,
        name: "Pasta Carbonara",
        portion: 2,
        portion_unit: "servings",
      },
      {
        meal_id: 2,
        user_id: 1,
        name: "Chicken Stir Fry",
        portion: 3,
        portion_unit: "servings",
      },
    ]
    mockFetchOnce(/\/api\/meals/, mockMeals)

    render(<Meals />)

    await waitFor(() => {
      expect(screen.getByText("Pasta Carbonara")).toBeInTheDocument()
      expect(screen.getByText("Chicken Stir Fry")).toBeInTheDocument()
    })
  })

  it("renders empty state when no meals exist", async () => {
    mockFetchOnce(/\/api\/meals/, [])

    render(<Meals />)

    await waitFor(() => {
      expect(screen.getByText("No meals yet.")).toBeInTheDocument()
    })
  })

  it("displays error message on API failure", async () => {
    mockFetchOnce(/\/api\/meals/, { detail: "Error" }, 500)

    render(<Meals />)

    await waitFor(() => {
      expect(screen.getByText("Could not load your meals.")).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument()
    })
  })
})
