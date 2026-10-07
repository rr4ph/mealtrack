import { useEffect, useState } from "react"

const API = "http://localhost:8000/api"

type Range = "daily" | "weekly" | "monthly"

type Stats = {
  points: { start: string; label: string; value: number; total: number }[]
  goal?: number | null
  today?: number
  average_per_day?: boolean
}

type Activity = { id: number; name: string; amount: number; at: string; detail: string | null }

function when(iso: string) {
  const d = new Date(iso)
  const time = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  const day = new Date()
  if (d.toDateString() === day.toDateString()) return `Today · ${time}`
  day.setDate(day.getDate() - 1)
  if (d.toDateString() === day.toDateString()) return `Yesterday · ${time}`
  return `${d.toLocaleDateString([], { day: "numeric", month: "short" })} · ${time}`
}

function Chart({ stats }: { stats: Stats }) {
  const line = stats.goal
  const max = Math.max(1, ...stats.points.map((p) => p.value), line ?? 0)
  const w = 600
  const h = 180
  const pad = 24
  const top = 24
  const slot = w / stats.points.length
  const barW = Math.min(48, slot * 0.6)
  const y = (v: number) => h - pad - (v / max) * (h - pad - top)

  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" role="img" aria-label="calories chart">
      <line x1="0" x2={w} y1={h - pad} y2={h - pad} stroke="#2a2a35" />
      {line != null && line > 0 && (
        <g>
          <line x1="0" x2={w} y1={y(line)} y2={y(line)} stroke="#d43cff" strokeDasharray="4 4" />
          <text x={w - 4} y={y(line) - 4} textAnchor="end" fontSize="10" fill="#d43cff">
            {`goal ${line}`}
          </text>
        </g>
      )}
      {stats.points.map((p, i) => {
        const x = i * slot + (slot - barW) / 2
        const over = line != null && p.value > line
        return (
          <g key={p.start}>
            <rect
              x={x} y={y(p.value)} width={barW} height={Math.max(0, h - pad - y(p.value))} rx="3"
              fill={over ? "#ff5d8f" : "#a12ec9"}
            >
              <title>{`${p.label}: ${Math.round(p.value)} kcal`}</title>
            </rect>
            {p.value > 0 && (
              <text x={x + barW / 2} y={y(p.value) - 4} textAnchor="middle" fontSize="10" fill="#cfcfd8">
                {Math.round(p.value)}
              </text>
            )}
            <text x={x + barW / 2} y={h - 8} textAnchor="middle" fontSize="10" fill="#8a8a98">{p.label}</text>
          </g>
        )
      })}
    </svg>
  )
}

function AnalyticsCard() {
  const [range, setRange] = useState<Range>("daily")
  const [result, setResult] = useState<{ key: string; stats: Stats | null } | null>(null)
  const key = range
  const stats = result?.key === key ? result.stats : null
  const error = result?.key === key && result.stats === null
  const [acts, setActs] = useState<{ key: string; items: Activity[] | null } | null>(null)
  const items = acts?.key === key ? acts.items : null
  const actError = acts?.key === key && acts.items === null

  useEffect(() => {
    let active = true
    fetch(`${API}/stats/calories?range=${range}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d: Stats) => {
        if (active) setResult({ key, stats: d })
      })
      .catch(() => active && setResult({ key, stats: null }))
    fetch(`${API}/activity/calories?range=${range}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d: Activity[]) => active && setActs({ key, items: d }))
      .catch(() => active && setActs({ key, items: null }))
    return () => {
      active = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [range])

  return (
    <div className="panel analytics-card">
      {error ? (
        <p className="error-message">Could not load calorie data.</p>
      ) : !stats ? (
        <p className="muted">Loading...</p>
      ) : (
        <>
          <p className="muted">
            <strong>{Math.round(stats.today ?? 0).toLocaleString()}</strong>
            {stats.goal ? ` / ${stats.goal.toLocaleString()}` : ""} kcal today
            {stats.goal ? "" : " – set a calorie goal in Account"}
            {stats.average_per_day && " · bars show average kcal per day"}
          </p>
          <Chart stats={stats} />
        </>
      )}

      <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 12 }}>
        {(["daily", "weekly", "monthly"] as Range[]).map((r) => (
          <button
            key={r}
            type="button"
            className={range === r ? "primary-button compact-button" : "secondary-button compact-button"}
            onClick={() => setRange(r)}
          >
            {r[0].toUpperCase() + r.slice(1)}
          </button>
        ))}
      </div>

      <div className="activity-list">
        <p className="eyebrow">RECENT INTAKE</p>
        {actError ? (
          <p className="error-message">Could not load activity.</p>
        ) : !items ? (
          <p className="muted">Loading...</p>
        ) : items.length === 0 ? (
          <p className="muted">No meals logged in this period.</p>
        ) : (
          items.map((a) => (
            <div key={a.id} className="activity-row">
              <div>
                <p>{a.name}</p>
                <p className="muted">{a.detail ? `${a.detail} · ` : ""}{when(a.at)}</p>
              </div>
              <strong>{`${Math.round(a.amount)} kcal`}</strong>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default AnalyticsCard
