import { describe, it, expect, beforeEach, vi } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import Register from "../src/Register"
import { mockFetchOnce } from "./test-utils"

describe("Register", () => {
  const mockOnRegistered = vi.fn()
  const mockOnCancel = vi.fn()

  beforeEach(() => {
    mockOnRegistered.mockClear()
    mockOnCancel.mockClear()
    vi.clearAllMocks()
  })

  it("renders the registration form", () => {
    render(<Register onRegistered={mockOnRegistered} onCancel={mockOnCancel} />)
    expect(screen.getByText("CREATE ACCOUNT")).toBeInTheDocument()
    expect(screen.getByText("Username")).toBeInTheDocument()
    expect(screen.getByText("Password")).toBeInTheDocument()
    expect(screen.getByText("Confirm password")).toBeInTheDocument()
    expect(screen.getByText("Postcode (optional)")).toBeInTheDocument()
  })

  it("disables submit button when required fields are empty", () => {
    render(<Register onRegistered={mockOnRegistered} onCancel={mockOnCancel} />)
    const submitButton = screen.getByRole("button", { name: "Create account" })
    expect(submitButton).toBeDisabled()
  })

  it("enables submit when all required fields are filled", async () => {
    const user = userEvent.setup()
    render(<Register onRegistered={mockOnRegistered} onCancel={mockOnCancel} />)
    const inputs = document.querySelectorAll("input")
    await user.type(inputs[0], "newuser")
    await user.type(inputs[1], "password123")
    await user.type(inputs[2], "password123")
    const submitButton = screen.getByRole("button", { name: "Create account" })
    expect(submitButton).not.toBeDisabled()
  })

  it("handles successful registration", async () => {
    const user = userEvent.setup()
    mockFetchOnce(/\/api\/users/, { user_id: 2, username: "newuser" })

    render(<Register onRegistered={mockOnRegistered} onCancel={mockOnCancel} />)
    const inputs = document.querySelectorAll("input")
    await user.type(inputs[0], "newuser")
    await user.type(inputs[1], "password123")
    await user.type(inputs[2], "password123")
    await user.click(screen.getByRole("button", { name: "Create account" }))

    await waitFor(() => {
      expect(mockOnRegistered).toHaveBeenCalled()
    })
  })

  it("displays error when passwords do not match", async () => {
    const user = userEvent.setup()
    render(<Register onRegistered={mockOnRegistered} onCancel={mockOnCancel} />)
    const inputs = document.querySelectorAll("input")
    await user.type(inputs[0], "newuser")
    await user.type(inputs[1], "password123")
    await user.type(inputs[2], "password456")
    await user.click(screen.getByRole("button", { name: "Create account" }))

    await waitFor(() => {
      expect(screen.getByText("Passwords do not match.")).toBeInTheDocument()
    })
  })

  it("displays error message on registration failure", async () => {
    const user = userEvent.setup()
    mockFetchOnce(/\/api\/users/, { detail: "Username already exists" }, 400)

    render(<Register onRegistered={mockOnRegistered} onCancel={mockOnCancel} />)
    const inputs = document.querySelectorAll("input")
    await user.type(inputs[0], "existinguser")
    await user.type(inputs[1], "password123")
    await user.type(inputs[2], "password123")
    await user.click(screen.getByRole("button", { name: "Create account" }))

    await waitFor(() => {
      expect(screen.getByText("Username already exists")).toBeInTheDocument()
    })
  })

  it("accepts optional postcode", async () => {
    const user = userEvent.setup()
    mockFetchOnce(/\/api\/users/, { user_id: 2, username: "newuser" })

    render(<Register onRegistered={mockOnRegistered} onCancel={mockOnCancel} />)
    const inputs = document.querySelectorAll("input")
    await user.type(inputs[0], "newuser")
    await user.type(inputs[1], "password123")
    await user.type(inputs[2], "password123")
    await user.type(inputs[3], "SW1A1AA")
    await user.click(screen.getByRole("button", { name: "Create account" }))

    await waitFor(() => {
      expect(mockOnRegistered).toHaveBeenCalled()
    })
  })

  it("calls onCancel when back button is clicked", async () => {
    const user = userEvent.setup()
    render(<Register onRegistered={mockOnRegistered} onCancel={mockOnCancel} />)
    await user.click(screen.getByRole("button", { name: "Back to log in" }))
    expect(mockOnCancel).toHaveBeenCalled()
  })
})
