import { afterEach, beforeEach, vi } from "vitest"
import { cleanup } from "@testing-library/react"
import "@testing-library/jest-dom/vitest"
import { setupFetchMock } from "./tests/test-utils"

afterEach(() => {
  cleanup()
  localStorage.clear()
  sessionStorage.clear()
  vi.clearAllMocks()
})

beforeEach(() => {
  setupFetchMock()
})
