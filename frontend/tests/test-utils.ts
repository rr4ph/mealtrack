import type { ReactElement } from "react"
import type { RenderOptions } from "@testing-library/react"
import { render } from "@testing-library/react"
import { vi } from "vitest"

/* eslint-disable @typescript-eslint/no-explicit-any */

let fetchQueue: Array<(input: any) => Promise<Response>> = []

export function setupFetchMock() {
  fetchQueue = []
  global.fetch = vi.fn(async (input: any) => {
    if (fetchQueue.length === 0) {
      return new Response(JSON.stringify({ detail: "No mock configured" }), {
        status: 404,
      })
    }
    const handler = fetchQueue.shift()
    return handler?.(input) ?? new Response("", { status: 500 })
  })
}

export function mockFetchOnce(url: string | RegExp, response: any, status = 200) {
  fetchQueue.push(async (input: any) => {
    const inputUrl = typeof input === "string" ? input : input?.url
    const matches = url instanceof RegExp ? url.test(inputUrl) : inputUrl?.includes(url)
    if (!matches) {
      return new Response(JSON.stringify({ detail: "Not mocked" }), { status: 404 })
    }
    return new Response(JSON.stringify(response), {
      status,
      headers: { "Content-Type": "application/json" },
    })
  })
}

export function renderWithAuth(ui: ReactElement, options?: Omit<RenderOptions, "wrapper">) {
  return render(ui, options)
}
