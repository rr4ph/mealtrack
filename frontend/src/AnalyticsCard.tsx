import { useEffect, useState } from "react"

const API = "http://localhost:8000/api"

type Metric = "calories" | "spending"
type Range = "daily" | "weekly" | "monthly"

type Stats = {
  points: { start: string; label: string; value: number; total: number }[]
  goal?: number | null
  today?: number
  average_per_day?: boolean
  limit?: number | null
  spent?: number
  remaining?: number | null
  range_limit?: number | null
}

function money(value: number) {
  return `£${value.toFixed(2)}`
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

function Chart({ stats, metric }: { stats: Stats; metric: Metric }) {
  const line = metric === "calories" ? stats.goal : stats.range_limit
  const max = Math.max(1, ...stats.points.map((p) => p.value), line ?? 0)
  const w = 600
  const h = 180
  const pad = 24
  const top = 24
  const slot = w / stats.points.length
  const barW = Math.min(48, slot * 0.6)
  const y = (v: number) => h - pad - (v / max) * (h - pad - top)

  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" role="img" aria-label={`${metric} chart`}>
      <line x1="0" x2={w} y1={h - pad} y2={h - pad} stroke="#2a2a35" />
      {line != null && line > 0 && (
        <g>
          <line x1="0" x2={w} y1={y(line)} y2={y(line)} stroke="#d43cff" strokeDasharray="4 4" />
          <text x={w - 4} y={y(line) - 4} textAnchor="end" fontSize="10" fill="#d43cff">
            {metric === "calories" ? `goal ${line}` : `limit ${money(line)}`}
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
              <title>{`${p.label}: ${metric === "calories" ? `${Math.round(p.value)} kcal` : money(p.value)}`}</title>
            </rect>
            {p.value > 0 && (
              <text x={x + barW / 2} y={y(p.value) - 4} textAnchor="middle" fontSize="10" fill="#cfcfd8">
                {metric === "calories" ? Math.round(p.value) : p.value.toFixed(0)}
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
  const [metric, setMetric] = useState<Metric>("calories")
  const [range, setRange] = useState<Range>("daily")
  const [result, setResult] = useState<{ key: string; stats: Stats | null } | null>(null)
  const key = `${metric}-${range}`
  const stats = result?.key === key ? result.stats : null
  const error = result?.key === key && result.stats === null
  const [acts, setActs] = useState<{ key: string; items: Activity[] | null } | null>(null)
  const items = acts?.key === key ? acts.items : null
  const actError = acts?.key === key && acts.items === null

  useEffect(() => {
    let active = true
    fetch(`${API}/stats/${metric}?range=${range}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d: Stats) => {
        if (active) setResult({ key, stats: { ...d, range_limit: range === "monthly" ? d.limit : null } })
      })
      .catch(() => active && setResult({ key, stats: null }))
    fetch(`${API}/activity/${metric}?range=${range}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d: Activity[]) => active && setActs({ key, items: d }))
      .catch(() => active && setActs({ key, items: null }))
    return () => {
      active = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [metric, range])

  return (
    <div className="panel analytics-card">
      <div className="analytics-tabs" style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        {(["calories", "spending"] as Metric[]).map((m) => (
          <button
            key={m}
            type="button"
            className={metric === m ? "primary-button" : "secondary-button"}
            style={{ flex: 1 }}
            onClick={() => setMetric(m)}
          >
            {m.toUpperCase()}
          </button>
        ))}
      </div>

      {error ? (
        <p className="error-message">Could not load {metric} data.</p>
      ) : !stats ? (
        <p className="muted">Loading...</p>
      ) : (
        <>
          {metric === "calories" ? (
            <p className="muted">
              <strong>{Math.round(stats.today ?? 0).toLocaleString()}</strong>
              {stats.goal ? ` / ${stats.goal.toLocaleString()}` : ""} kcal today
              {stats.goal ? "" : " – set a calorie goal in Account"}
              {stats.average_per_day && " · bars show average kcal per day"}
            </p>
          ) : (
            <p className="muted">
              <strong>{money(stats.spent ?? 0)}</strong> spent this month
              {stats.limit != null
                ? ` · ${money(stats.limit)} limit · ${(stats.remaining ?? 0) < 0 ? `${money(-(stats.remaining ?? 0))} over` : `${money(stats.remaining ?? 0)} remaining`}`
                : " – set a spending limit in Account"}
            </p>
          )}
          <Chart stats={stats} metric={metric} />
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
        <p className="eyebrow">{metric === "calories" ? "RECENT INTAKE" : "RECENT PURCHASES"}</p>
        {actError ? (
          <p className="error-message">Could not load activity.</p>
        ) : !items ? (
          <p className="muted">Loading...</p>
        ) : items.length === 0 ? (
          <p className="muted">
            {metric === "calories" ? "No meals logged in this period." : "No purchases recorded in this period."}
          </p>
        ) : (
          items.map((a) => (
            <div key={a.id} className="activity-row">
              <div>
                <p>{a.name}</p>
                <p className="muted">{a.detail ? `${a.detail} · ` : ""}{when(a.at)}</p>
              </div>
              <strong>{metric === "calories" ? `${Math.round(a.amount)} kcal` : money(a.amount)}</strong>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default AnalyticsCard
