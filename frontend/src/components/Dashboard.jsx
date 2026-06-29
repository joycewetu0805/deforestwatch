import { useEffect, useMemo, useState } from 'react'
import { ArrowLeft, Layers, TriangleAlert, TreePine, Activity } from 'lucide-react'

// Données de repli si l'API FastAPI n'est pas joignable (mode statique)
const FALLBACK_STATS = Array.from({ length: 11 }, (_, i) => {
  const year = 2015 + i
  const forest = 240000 - i * 6800 - i * i * 220
  return { year, total_forest_ha: forest, forest_loss_ha: i === 0 ? 0 : 6800 + i * 440 }
})

function StatCard({ icon: Icon, label, value, accent }) {
  return (
    <div className="rounded-xl border border-white/10 bg-panel/70 p-5">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-400">{label}</span>
        <Icon size={18} className={accent} />
      </div>
      <div className="mt-2 text-2xl font-bold text-slate-100">{value}</div>
    </div>
  )
}

// Mini-graphe en courbe (SVG pur, sans dépendance)
function LineChart({ data }) {
  const w = 600, h = 200, pad = 30
  const xs = data.map((d) => d.year)
  const ys = data.map((d) => d.total_forest_ha)
  const minY = Math.min(...ys), maxY = Math.max(...ys)
  const px = (i) => pad + (i / (data.length - 1)) * (w - 2 * pad)
  const py = (v) => h - pad - ((v - minY) / (maxY - minY || 1)) * (h - 2 * pad)
  const path = ys.map((v, i) => `${i ? 'L' : 'M'}${px(i)},${py(v)}`).join(' ')
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full">
      <path d={`${path} L${px(data.length - 1)},${h - pad} L${px(0)},${h - pad} Z`}
        fill="rgba(16,185,129,0.12)" />
      <path d={path} fill="none" stroke="#10B981" strokeWidth="2.5" />
      {ys.map((v, i) => <circle key={i} cx={px(i)} cy={py(v)} r="3" fill="#06B6D4" />)}
      {xs.filter((_, i) => i % 2 === 0).map((yr, i) => (
        <text key={yr} x={px(i * 2)} y={h - 8} fill="#64748B" fontSize="11" textAnchor="middle">{yr}</text>
      ))}
    </svg>
  )
}

// Grille de risque simulée (heatmap simple)
function RiskGrid() {
  const cells = useMemo(() => Array.from({ length: 144 }, (_, i) => {
    const r = Math.random()
    return r
  }), [])
  const color = (r) => r > 0.75 ? '#EF4444' : r > 0.5 ? '#F59E0B' : r > 0.25 ? '#84CC16' : '#10B981'
  return (
    <div className="grid grid-cols-12 gap-1">
      {cells.map((r, i) => (
        <div key={i} className="aspect-square rounded-sm" style={{ backgroundColor: color(r), opacity: 0.85 }} />
      ))}
    </div>
  )
}

export default function Dashboard({ onBack }) {
  const [stats, setStats] = useState(FALLBACK_STATS)
  const [live, setLive] = useState(false)

  useEffect(() => {
    fetch('/api/v1/statistics')
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((d) => { if (d.statistics?.length) { setStats(d.statistics); setLive(true) } })
      .catch(() => {})
  }, [])

  const last = stats[stats.length - 1]
  const totalLoss = stats.reduce((a, s) => a + (s.forest_loss_ha || 0), 0)

  return (
    <div className="min-h-screen bg-base text-slate-200">
      <header className="flex items-center justify-between border-b border-white/10 px-6 py-4">
        <button onClick={onBack} className="inline-flex items-center gap-2 text-slate-400 hover:text-emerald-glow">
          <ArrowLeft size={18} /> Retour
        </button>
        <h1 className="text-lg font-bold text-emerald-glow">CongoForest Watch — Monitoring</h1>
        <span className={`rounded-full px-3 py-1 text-xs ${live ? 'bg-emerald-glow/20 text-emerald-glow' : 'bg-slate-700 text-slate-400'}`}>
          {live ? '● API connectée' : '○ Mode statique'}
        </span>
      </header>

      <main className="mx-auto max-w-6xl space-y-6 p-6">
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatCard icon={TreePine} label="Forêt actuelle" accent="text-emerald-glow"
            value={`${Math.round(last.total_forest_ha).toLocaleString('fr-FR')} ha`} />
          <StatCard icon={Activity} label="Perte cumulée" accent="text-alert"
            value={`${Math.round(totalLoss).toLocaleString('fr-FR')} ha`} />
          <StatCard icon={TriangleAlert} label="Alertes actives" accent="text-amber-400" value="12" />
          <StatCard icon={Layers} label="Période" accent="text-satellite" value="2015–2025" />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-xl border border-white/10 bg-panel/50 p-5">
            <h2 className="mb-3 font-semibold text-slate-100">Évolution de la couverture forestière</h2>
            <LineChart data={stats} />
          </section>
          <section className="rounded-xl border border-white/10 bg-panel/50 p-5">
            <h2 className="mb-3 font-semibold text-slate-100">Carte de risque de déforestation</h2>
            <RiskGrid />
            <div className="mt-3 flex items-center gap-4 text-xs text-slate-400">
              <span className="flex items-center gap-1"><i className="inline-block h-3 w-3 rounded-sm" style={{ background: '#10B981' }} /> Faible</span>
              <span className="flex items-center gap-1"><i className="inline-block h-3 w-3 rounded-sm" style={{ background: '#F59E0B' }} /> Modéré</span>
              <span className="flex items-center gap-1"><i className="inline-block h-3 w-3 rounded-sm" style={{ background: '#EF4444' }} /> Élevé</span>
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}
