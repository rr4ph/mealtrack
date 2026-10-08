import { API_URL } from "./config"

export type Session = {
  user_id: number
  username: string
  postcode: string | null
  token: string
}

const KEY = "mealtrack-session"

export function getSession(): Session | null {
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? (JSON.parse(raw) as Session) : null
  } catch {
    return null
  }
}

export function saveSession(session: Session) {
  localStorage.setItem(KEY, JSON.stringify(session))
}

export function clearSession() {
  localStorage.removeItem(KEY)
}

export function getUserId(): number {
  return getSession()?.user_id ?? 0
}

const nativeFetch = window.fetch.bind(window)
window.fetch = (input, init) => {
  const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url
  const token = getSession()?.token
  if (token && url.startsWith(`${API_URL}/api/`)) {
    const headers = new Headers(init?.headers)
    if (!headers.has("Authorization")) headers.set("Authorization", `Bearer ${token}`)
    return nativeFetch(input, { ...init, headers })
  }
  return nativeFetch(input, init)
}
