import { describe, it, expect, beforeEach, vi } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import Account from "../src/Account"
import { mockFetchOnce } from "./test-utils"

describe("Account", () => {
  const mockOnLogout = vi.fn()
  const mockOnSessionChange = vi.fn()

  const mockSession = {
    user_id: 1,
    username: "testuser",
    postcode: "SW1A1AA",
    token: "test-token",
  }

  beforeEach(() => {
    mockOnLogout.mockClear()
    mockOnSessionChange.mockClear()
    vi.clearAllMocks()
    localStorage.setItem("mealtrack-session", JSON.stringify(mockSession))
  })

  it("renders account page with profile section", async () => {
    mockFetchOnce(/\/api\/goals/, {})
    render(<Account session={mockSession} onLogout={mockOnLogout} onSessionChange={mockOnSessionChange} />)

    await waitFor(() => {
      expect(screen.getByText("PROFILE")).toBeInTheDocument()
    })
  })

  it("displays current username", async () => {
    mockFetchOnce(/\/api\/goals/, {})
    render(<Account session={mockSession} onLogout={mockOnLogout} onSessionChange={mockOnSessionChange} />)

    await waitFor(() => {
      expect(screen.getByDisplayValue("testuser")).toBeInTheDocument()
    })
  })

  it("displays password change section", async () => {
    mockFetchOnce(/\/api\/goals/, {})
    render(<Account session={mockSession} onLogout={mockOnLogout} onSessionChange={mockOnSessionChange} />)

    await waitFor(() => {
      expect(screen.getByText("Current password")).toBeInTheDocument()
    })
  })

  it("calls onLogout when logout button is clicked", async () => {
    const user = userEvent.setup()
    mockFetchOnce(/\/api\/goals/, {})

    render(<Account session={mockSession} onLogout={mockOnLogout} onSessionChange={mockOnSessionChange} />)

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Log out" })).toBeInTheDocument()
    })

    await user.click(screen.getByRole("button", { name: "Log out" }))

    expect(mockOnLogout).toHaveBeenCalled()
  })
})
