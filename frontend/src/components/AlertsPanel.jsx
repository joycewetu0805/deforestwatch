import { useEffect, useState } from 'react'
import { BellRing, MapPin, TriangleAlert } from 'lucide-react'

const SEV = {
  critique: { color: '#EF4444', label: 'Critique' },
  'élevée': { color: '#F59E0B', label: 'Élevée' },
  'modérée': { color: '#84CC16', label: 'Modérée' },
}

// API d'abord, puis assets de démo statiques
function fetchChain(paths) {
  return paths.reduce(
    (p, url) => p.catch(() => fetch(url).then((r) => (r.ok ? r.json() : Promise.reject()))),
    Promise.reject(),
  )
}

export default function AlertsPanel() {
  const [alerts, setAlerts] = useState([])
  const [summary, setSummary] = useState(null)

  useEffect(() => {
    fetchChain(['/api/v1/alerts?active_only=true&limit=8', '/demo/alerts.json'])
      .then((d) => setAlerts(Array.isArray(d) ? d.slice(0, 8) : []))
      .catch(() => setAlerts([]))
    fetchChain(['/api/v1/alerts/summary', '/demo/alerts_summary.json'])
      .then(setSummary)
      .catch(() => setSummary(null))
  }, [])

  return (
    <section className="rounded-xl border border-alert/30 bg-alert/[0.06] p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="flex items-center gap-2 font-semibold text-slate-100">
          <BellRing size={18} className="text-alert" /> Alertes de déforestation
        </h2>
        {summary && (
          <span className="rounded-full bg-alert/20 px-3 py-1 text-xs font-semibold text-alert">
            {summary.active_alerts} actives · {summary.total_alerts} au total
          </span>
        )}
      </div>

      {alerts.length === 0 ? (
        <p className="text-sm text-slate-400">Aucune alerte active.</p>
      ) : (
        <div className="space-y-2">
          {alerts.map((a) => {
            const sev = SEV[a.severity] || { color: '#888', label: a.severity }
            return (
              <div key={a.id}
                className="flex items-center gap-3 rounded-lg border border-white/10 bg-panel/60 px-3 py-2">
                <TriangleAlert size={16} style={{ color: sev.color }} />
                <div className="flex-1">
                  <div className="text-sm text-slate-200">
                    Secteur <b>{a.sector}</b> · {a.year} — perte de{' '}
                    <b>{Math.round(a.area_lost_ha).toLocaleString('fr-FR')} ha</b>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-slate-500">
                    <MapPin size={11} /> {a.lat.toFixed(3)}, {a.lon.toFixed(3)}
                  </div>
                </div>
                <span className="rounded-full px-2 py-0.5 text-xs font-semibold"
                  style={{ background: `${sev.color}22`, color: sev.color }}>
                  {sev.label}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
