import { describe, it, expect, beforeEach, vi } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import Inventory from "../src/Inventory"
import { mockFetchOnce } from "./test-utils"

describe("Inventory", () => {
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
    mockFetchOnce(/\/api\/inventory/, { items: [] })
    mockFetchOnce(/\/api\/ingredient-types/, [])
    render(<Inventory />)
    expect(screen.getByText("Loading inventory...")).toBeInTheDocument()
  })

  it("displays error message on load failure", async () => {
    mockFetchOnce(/\/api\/inventory/, { detail: "Error" }, 500)
    mockFetchOnce(/\/api\/ingredient-types/, [])

    render(<Inventory />)

    await waitFor(() => {
      expect(screen.getByText("Could not load your inventory.")).toBeInTheDocument()
    })
  })

  it("retries loading on error", async () => {
    const user = userEvent.setup()
    mockFetchOnce(/\/api\/inventory/, { detail: "Error" }, 500)
    mockFetchOnce(/\/api\/ingredient-types/, [])
    mockFetchOnce(/\/api\/inventory/, { items: [] })
    mockFetchOnce(/\/api\/ingredient-types/, [])

    render(<Inventory />)

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument()
    })

    await user.click(screen.getByRole("button", { name: "Try again" }))

    await waitFor(() => {
      expect(screen.queryByText("Could not load your inventory.")).not.toBeInTheDocument()
    })
  })
})
