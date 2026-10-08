import { useEffect, useState } from "react"
import Login from "./Login"
import Register from "./Register"
import Account from "./Account"
import { clearSession, getSession, type Session } from "./auth"
import Dashboard from "./Dashboard"
import "./App.css"
import Meals from "./Meals"
import Inventory from "./Inventory"
import Products from "./Products"
import StatusPills from "./StatusPills"

import { API_URL } from "./config"
type NavItem = {
  label: string
  icon: string
}

const navItems: NavItem[] = [
  { label: "Dashboard", icon: "⌂" },
  { label: "Meals", icon: "◈" },
  { label: "Inventory", icon: "▣" },
  { label: "Products", icon: "⌕" },
]

function App() {
  const [activePage, setActivePage] = useState("Dashboard")
  const [session, setSession] = useState<Session | null>(getSession())
  const [registering, setRegistering] = useState(false)
  const [notice, setNotice] = useState("")
  const [highContrast, setHighContrast] = useState(
    () => localStorage.getItem("mealtrack-high-contrast") === "true"
  )

  useEffect(() => {
    document.documentElement.classList.toggle("high-contrast", highContrast)
    localStorage.setItem("mealtrack-high-contrast", String(highContrast))
  }, [highContrast])

  useEffect(() => {
    if (!session) return
    fetch(`${API_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${session.token}` },
    })
      .then((r) => {
        if (r.status === 401) logout()
      })
      .catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function logout() {
    clearSession()
    setSession(null)
    setActivePage("Dashboard")
  }

  function navigate(page: string) {
    setActivePage(page)
  }

  if (!session) {
    return registering ? (
      <Register
        onCancel={() => setRegistering(false)}
        onRegistered={() => {
          setNotice("Account created. Log in to continue.")
          setRegistering(false)
        }}
      />
    ) : (
      <Login
        onLogin={setSession}
        onCreateAccount={() => {
          setNotice("")
          setRegistering(true)
        }}
        notice={notice}
      />
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">M</div>
          <span>Meal<span>track</span></span>
        </div>

        <nav className="navigation" aria-label="Main navigation">
          <p className="nav-label">MENU</p>

          {navItems.map((item) => (
            <button
              key={item.label}
              className={`nav-item ${activePage === item.label ? "active" : ""}`}
              onClick={() => navigate(item.label)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button className={`nav-item ${activePage === "Account" ? "active" : ""}`} onClick={() => navigate("Account")}>
            <span className="nav-icon">☺</span>
            <span>Account</span>
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">MEALTRACK</p>
            <h1>{activePage}</h1>
          </div>

          <div className="topbar-actions">
            <StatusPills refreshKey={activePage} />
            <button
              className="contrast-toggle"
              aria-pressed={highContrast}
              onClick={() => setHighContrast((v) => !v)}
            >
              <span aria-hidden="true">◐</span> High contrast: {highContrast ? "On" : "Off"}
            </button>
            <button
              className="avatar"
              aria-label="Account"
              onClick={() => navigate("Account")}
            >
              {session.username.charAt(0).toUpperCase()}
            </button>
          </div>
        </header>

        {activePage === "Dashboard" ? (
          <Dashboard onNavigate={navigate} />
        ) : activePage === "Meals" ? (
          <Meals />
        ) : activePage === "Inventory" ? (
          <Inventory />
        ) : activePage === "Products" ? (
          <Products />
        ) : activePage === "Account" ? (
          <Account session={session} onLogout={logout} onSessionChange={setSession} />
        ) : (
          <div className="page-content">
            <section className="placeholder-page panel">
              <p className="eyebrow">COMING NEXT</p>
              <h2>{activePage}</h2>
              <p className="muted">
                This page will be connected to the Mealtrack API next.
              </p>
            </section>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
