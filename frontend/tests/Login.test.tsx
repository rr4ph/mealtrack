import { describe, it, expect, beforeEach, vi } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import Login from "../src/Login"
import { mockFetchOnce } from "./test-utils"

describe("Login", () => {
  const mockOnLogin = vi.fn()
  const mockOnCreateAccount = vi.fn()

  beforeEach(() => {
    mockOnLogin.mockClear()
    mockOnCreateAccount.mockClear()
    vi.clearAllMocks()
  })

  it("renders the login form", () => {
    mockFetchOnce(/\/api\/auth\/login/, {})
    render(<Login onLogin={mockOnLogin} onCreateAccount={mockOnCreateAccount} />)
    expect(screen.getByText("Mealtrack")).toBeInTheDocument()
    expect(screen.getByText("LOG IN")).toBeInTheDocument()
    expect(screen.getByLabelText("Username")).toBeInTheDocument()
    expect(screen.getByLabelText("Password")).toBeInTheDocument()
  })

  it("disables submit button when fields are empty", () => {
    mockFetchOnce(/\/api\/auth\/login/, {})
    render(<Login onLogin={mockOnLogin} onCreateAccount={mockOnCreateAccount} />)
    const submitButton = screen.getByRole("button", { name: "Log in" })
    expect(submitButton).toBeDisabled()
  })

  it("enables submit when both fields are filled", async () => {
    const user = userEvent.setup()
    mockFetchOnce(/\/api\/auth\/login/, {})
    render(<Login onLogin={mockOnLogin} onCreateAccount={mockOnCreateAccount} />)
    await user.type(screen.getByLabelText("Username"), "testuser")
    await user.type(screen.getByLabelText("Password"), "password123")
    const submitButton = screen.getByRole("button", { name: "Log in" })
    expect(submitButton).not.toBeDisabled()
  })

  it("handles successful login", async () => {
    const user = userEvent.setup()
    const mockSession = {
      user_id: 1,
      username: "testuser",
      postcode: "SW1A1AA",
      token: "test-token",
    }
    mockFetchOnce(/\/api\/auth\/login/, mockSession)

    render(<Login onLogin={mockOnLogin} onCreateAccount={mockOnCreateAccount} />)
    await user.type(screen.getByLabelText("Username"), "testuser")
    await user.type(screen.getByLabelText("Password"), "password123")
    await user.click(screen.getByRole("button", { name: "Log in" }))

    await waitFor(() => {
      expect(mockOnLogin).toHaveBeenCalledWith(mockSession)
    })
  })

  it("displays error message on failed login", async () => {
    const user = userEvent.setup()
    mockFetchOnce(/\/api\/auth\/login/, { detail: "Invalid credentials" }, 401)

    render(<Login onLogin={mockOnLogin} onCreateAccount={mockOnCreateAccount} />)
    await user.type(screen.getByLabelText("Username"), "testuser")
    await user.type(screen.getByLabelText("Password"), "wrong")
    await user.click(screen.getByRole("button", { name: "Log in" }))

    await waitFor(() => {
      expect(screen.getByText("Invalid credentials")).toBeInTheDocument()
    })
  })

  it("displays notice message if provided", () => {
    mockFetchOnce(/\/api\/auth\/login/, {})
    render(
      <Login
        onLogin={mockOnLogin}
        onCreateAccount={mockOnCreateAccount}
        notice="Account created. Log in to continue."
      />
    )
    expect(screen.getByText("Account created. Log in to continue.")).toBeInTheDocument()
  })
})
