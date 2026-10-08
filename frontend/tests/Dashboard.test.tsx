import { describe, it, expect, beforeEach, vi } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import Dashboard from "../src/Dashboard"
import { mockFetchOnce } from "./test-utils"

describe("Dashboard", () => {
  const mockOnNavigate = vi.fn()

  beforeEach(() => {
    mockOnNavigate.mockClear()
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

  it("renders dashboard welcome section", async () => {
    mockFetchOnce(/\/api\/inventory/, { items: [] })
    mockFetchOnce(/\/api\/meals/, [])
    mockFetchOnce(/\/api\/shortages/, [])
    mockFetchOnce(/\/api\/goals/, {})

    render(<Dashboard onNavigate={mockOnNavigate} />)

    await waitFor(() => {
      expect(screen.getByText("Welcome back.")).toBeInTheDocument()
    })
  })

  it("displays stat cards", async () => {
    mockFetchOnce(/\/api\/inventory/, { items: [] })
    mockFetchOnce(/\/api\/meals/, [])
    mockFetchOnce(/\/api\/shortages/, [])
    mockFetchOnce(/\/api\/goals/, {})

    render(<Dashboard onNavigate={mockOnNavigate} />)

    await waitFor(() => {
      expect(screen.getByText("items tracked")).toBeInTheDocument()
      expect(screen.getByText("meals saved")).toBeInTheDocument()
    })
  })

  it("navigates to inventory when inventory stat is clicked", async () => {
    const user = userEvent.setup()
    mockFetchOnce(/\/api\/inventory/, { items: [] })
    mockFetchOnce(/\/api\/meals/, [])
    mockFetchOnce(/\/api\/shortages/, [])
    mockFetchOnce(/\/api\/goals/, {})

    render(<Dashboard onNavigate={mockOnNavigate} />)

    await waitFor(() => {
      expect(screen.getByText("items tracked")).toBeInTheDocument()
    })

    const inventoryButton = screen.getByRole("button", { name: /items tracked/ })
    await user.click(inventoryButton)

    expect(mockOnNavigate).toHaveBeenCalledWith("Inventory")
  })

  it("navigates to meals when meals stat is clicked", async () => {
    const user = userEvent.setup()
    mockFetchOnce(/\/api\/inventory/, { items: [] })
    mockFetchOnce(/\/api\/meals/, [])
    mockFetchOnce(/\/api\/shortages/, [])
    mockFetchOnce(/\/api\/goals/, {})

    render(<Dashboard onNavigate={mockOnNavigate} />)

    await waitFor(() => {
      expect(screen.getByText("meals saved")).toBeInTheDocument()
    })

    const mealsButton = screen.getByRole("button", { name: /meals saved/ })
    await user.click(mealsButton)

    expect(mockOnNavigate).toHaveBeenCalledWith("Meals")
  })

  it("displays error when shortages fail to load", async () => {
    mockFetchOnce(/\/api\/inventory/, { items: [] })
    mockFetchOnce(/\/api\/meals/, [])
    mockFetchOnce(/\/api\/shortages/, { detail: "Error" }, 500)
    mockFetchOnce(/\/api\/goals/, {})

    render(<Dashboard onNavigate={mockOnNavigate} />)

    await waitFor(() => {
      const errorMessages = screen.getAllByText("Could not load missing products.")
      expect(errorMessages.length).toBeGreaterThan(0)
    })
  })
})
