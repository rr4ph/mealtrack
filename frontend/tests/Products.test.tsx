import { describe, it, expect, beforeEach, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import Products from "../src/Products"

describe("Products", () => {
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

  it("renders the products page", () => {
    render(<Products />)
    expect(screen.getByText("Products")).toBeInTheDocument()
    expect(screen.getByPlaceholderText("Search for a product...")).toBeInTheDocument()
  })
})
