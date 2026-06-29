import { useEffect, useMemo, useState } from 'react'
import {
  ArrowLeft, Layers, TriangleAlert, TreePine, Activity, RefreshCw,
} from 'lucide-react'

// Données de repli si l'API FastAPI n'est pas joignable (mode statique)
const FALLBACK_STATS = Array.from({ length: 11 }, (_, i) => {
  const year = 2015 + i
  const forest = 240000 - i * 6800 - i * i * 220
  return {
    year,
    total_forest_ha: forest,
    forest_loss_ha: i === 0 ? 0 : 6800 + i * 440,
    deforestation_rate: i === 0 ? 0 : +(2.8 + i * 0.15).toFixed(2),
  }
})

const CLASSES = [
  { name: 'Forêt dense', color: '#0B6E2D', pct: 41 },
  { name: 'Forêt dégradée', color: '#9BCC4F', pct: 17 },
  { name: 'Agriculture / Sol nu', color: '#D9A441', pct: 28 },
  { name: 'Eau', color: '#2E86C1', pct: 8 },
  { name: 'Urbain / Bâti', color: '#C0392B', pct: 6 },
]

function StatCard({ icon: Icon, label, value, sub, accent }) {
  return (
    <div className="rounded-xl border border-white/10 bg-panel/70 p-5 transition hover:border-white/20">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-400">{label}</span>
        <Icon size={18} className={accent} />
      </div>
      <div className="mt-2 text-2xl font-bold text-slate-100">{value}</div>
      {sub && <div className="mt-1 text-xs text-slate-500">{sub}</div>}
    </div>
  )
}

function Panel({ title, children, right }) {
  return (
    <section className="rounded-xl border border-white/10 bg-panel/50 p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-semibold text-slate-100">{title}</h2>
        {right}
      </div>
      {children}
    </section>
  )
}

// Courbe d'évolution (SVG)
function LineChart({ data }) {
  const w = 600, h = 200, pad = 34
  const ys = data.map((d) => d.total_forest_ha)
  const minY = Math.min(...ys), maxY = Math.max(...ys)
  const px = (i) => pad + (i / (data.length - 1)) * (w - 2 * pad)
  const py = (v) => h - pad - ((v - minY) / (maxY - minY || 1)) * (h - 2 * pad)
  const path = ys.map((v, i) => `${i ? 'L' : 'M'}${px(i)},${py(v)}`).join(' ')
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full">
      {[0.25, 0.5, 0.75].map((g) => (
        <line key={g} x1={pad} x2={w - pad} y1={pad + g * (h - 2 * pad)} y2={pad + g * (h - 2 * pad)}
          stroke="#ffffff10" />
      ))}
      <path d={`${path} L${px(data.length - 1)},${h - pad} L${px(0)},${h - pad} Z`} fill="rgba(16,185,129,0.12)" />
      <path d={path} fill="none" stroke="#10B981" strokeWidth="2.5" />
      {ys.map((v, i) => <circle key={i} cx={px(i)} cy={py(v)} r="3" fill="#06B6D4" />)}
      {data.map((d, i) => i % 2 === 0 && (
        <text key={d.year} x={px(i)} y={h - 10} fill="#64748B" fontSize="11" textAnchor="middle">{d.year}</text>
      ))}
    </svg>
  )
}

// Barres de perte annuelle (SVG)
function BarChart({ data }) {
  const w = 600, h = 200, pad = 34
  const vals = data.map((d) => d.forest_loss_ha || 0)
  const maxV = Math.max(...vals, 1)
  const bw = (w - 2 * pad) / data.length * 0.7
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full">
      {data.map((d, i) => {
        const x = pad + (i / data.length) * (w - 2 * pad)
        const bh = (vals[i] / maxV) * (h - 2 * pad)
        return (
          <g key={d.year}>
            <rect x={x} y={h - pad - bh} width={bw} height={bh} rx="2"
              fill={`rgba(239,68,68,${0.45 + 0.5 * (vals[i] / maxV)})`} />
            {i % 2 === 0 && <text x={x + bw / 2} y={h - 12} fill="#64748B" fontSize="11" textAnchor="middle">{d.year}</text>}
          </g>
        )
      })}
    </svg>
  )
}

// Donut de répartition des classes (SVG)
function Donut() {
  let acc = 0
  const r = 60, c = 2 * Math.PI * r
  return (
    <div className="flex items-center gap-6">
      <svg viewBox="0 0 160 160" className="h-40 w-40 -rotate-90">
        {CLASSES.map((cl) => {
          const len = (cl.pct / 100) * c
          const seg = (
            <circle key={cl.name} cx="80" cy="80" r={r} fill="none" stroke={cl.color}
              strokeWidth="20" strokeDasharray={`${len} ${c - len}`} strokeDashoffset={-acc} />
          )
          acc += len
          return seg
        })}
      </svg>
      <div className="space-y-1.5">
        {CLASSES.map((cl) => (
          <div key={cl.name} className="flex items-center gap-2 text-sm text-slate-300">
            <span className="inline-block h-3 w-3 rounded-sm" style={{ background: cl.color }} />
            {cl.name} <span className="text-slate-500">· {cl.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// Grille de risque (heatmap)
function RiskGrid() {
  const cells = useMemo(() => Array.from({ length: 144 }, () => Math.random()), [])
  const color = (v) => v > 0.78 ? '#EF4444' : v > 0.55 ? '#F59E0B' : v > 0.3 ? '#84CC16' : '#10B981'
  return (
    <>
      <div className="grid grid-cols-12 gap-1">
        {cells.map((v, i) => (
          <div key={i} className="aspect-square rounded-sm transition hover:scale-110"
            style={{ backgroundColor: color(v), opacity: 0.85 }} title={`Risque ${(v * 100).toFixed(0)}/100`} />
        ))}
      </div>
      <div className="mt-3 flex items-center gap-4 text-xs text-slate-400">
        <span className="flex items-center gap-1"><i className="inline-block h-3 w-3 rounded-sm" style={{ background: '#10B981' }} /> Faible</span>
        <span className="flex items-center gap-1"><i className="inline-block h-3 w-3 rounded-sm" style={{ background: '#84CC16' }} /> Modéré</span>
        <span className="flex items-center gap-1"><i className="inline-block h-3 w-3 rounded-sm" style={{ background: '#F59E0B' }} /> Élevé</span>
        <span className="flex items-center gap-1"><i className="inline-block h-3 w-3 rounded-sm" style={{ background: '#EF4444' }} /> Critique</span>
      </div>
    </>
  )
}

export default function Dashboard({ onBack }) {
  const [stats, setStats] = useState(FALLBACK_STATS)
  const [live, setLive] = useState(false)
  const [loading, setLoading] = useState(false)

  const load = () => {
    setLoading(true)
    fetch('/api/v1/statistics')
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((d) => { if (d.statistics?.length) { setStats(d.statistics); setLive(true) } })
      .catch(() => setLive(false))
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  const last = stats[stats.length - 1]
  const first = stats[0]
  const totalLoss = stats.reduce((a, s) => a + (s.forest_loss_ha || 0), 0)
  const lossPct = ((totalLoss / first.total_forest_ha) * 100).toFixed(1)

  return (
    <div className="min-h-screen bg-base text-slate-200">
      <header className="sticky top-0 z-50 flex items-center justify-between border-b border-white/10 bg-base/80 px-6 py-4 backdrop-blur-md">
        <button onClick={onBack} className="inline-flex items-center gap-2 text-slate-400 hover:text-emerald-glow">
          <ArrowLeft size={18} /> Retour
        </button>
        <h1 className="text-lg font-bold text-emerald-glow">Monitoring — Mai-Ndombe</h1>
        <div className="flex items-center gap-3">
          <button onClick={load} className="text-slate-400 hover:text-emerald-glow" title="Rafraîchir">
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
          <span className={`rounded-full px-3 py-1 text-xs ${live ? 'bg-emerald-glow/20 text-emerald-glow' : 'bg-slate-700 text-slate-400'}`}>
            {live ? '● API connectée' : '○ Mode statique'}
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-6 p-6">
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatCard icon={TreePine} label="Forêt actuelle" accent="text-emerald-glow"
            value={`${Math.round(last.total_forest_ha).toLocaleString('fr-FR')} ha`} sub={`année ${last.year}`} />
          <StatCard icon={Activity} label="Perte cumulée" accent="text-alert"
            value={`${Math.round(totalLoss).toLocaleString('fr-FR')} ha`} sub={`▼ ${lossPct}% depuis ${first.year}`} />
          <StatCard icon={TriangleAlert} label="Alertes actives" accent="text-amber-400" value="12" sub="cette semaine" />
          <StatCard icon={Layers} label="Période suivie" accent="text-satellite" value={`${first.year}–${last.year}`} sub="composites annuels" />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Panel title="Évolution de la couverture forestière"><LineChart data={stats} /></Panel>
          <Panel title="Perte forestière annuelle (ha)"><BarChart data={stats} /></Panel>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Panel title="Carte de risque de déforestation"><RiskGrid /></Panel>
          <Panel title="Répartition de la couverture du sol"><Donut /></Panel>
        </div>
      </main>
    </div>
  )
}
