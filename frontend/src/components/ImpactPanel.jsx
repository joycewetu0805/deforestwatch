import { useEffect, useState } from 'react'
import { Cloud, Car, TreePine, Factory } from 'lucide-react'

function fetchChain(paths) {
  return paths.reduce(
    (p, url) => p.catch(() => fetch(url).then((r) => (r.ok ? r.json() : Promise.reject()))),
    Promise.reject(),
  )
}

function Metric({ icon: Icon, value, label, color }) {
  return (
    <div className="rounded-xl border border-white/10 bg-panel/60 p-4">
      <Icon size={20} style={{ color }} />
      <div className="mt-2 text-2xl font-bold text-slate-100">{value}</div>
      <div className="text-xs text-slate-400">{label}</div>
    </div>
  )
}

export default function ImpactPanel() {
  const [data, setData] = useState(null)
  useEffect(() => {
    // API (carbon + radar) sinon asset statique impact.json
    Promise.all([
      fetchChain(['/api/v1/carbon']).then((d) => d.summary).catch(() => null),
      fetchChain(['/api/v1/radar/coverage/2025']).catch(() => null),
    ]).then(([carbon, radar]) => {
      if (carbon || radar) setData({ carbon, radar })
      else fetchChain(['/demo/impact.json']).then(setData).catch(() => {})
    })
  }, [])

  if (!data?.carbon) return null
  const c = data.carbon
  const r = data.radar

  return (
    <section className="rounded-xl border border-white/10 bg-panel/50 p-5">
      <h2 className="mb-3 font-semibold text-slate-100">🌍 Impact climatique & couverture</h2>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Metric icon={Factory} color="#EF4444"
          value={`${c.total_co2_mt?.toLocaleString('fr-FR', { maximumFractionDigits: 1 })} Mt`}
          label="CO₂ émis (déforestation)" />
        <Metric icon={Car} color="#F59E0B"
          value={c.equivalents?.cars_year?.toLocaleString('fr-FR')}
          label="voitures pendant 1 an" />
        <Metric icon={TreePine} color="#10B981"
          value={`${Math.round((c.equivalents?.trees_year || 0) / 1e6).toLocaleString('fr-FR')} M`}
          label="arbres pour compenser / an" />
        {r && (
          <Metric icon={Cloud} color="#06B6D4"
            value={`+${Math.round(r.gain_pct)} %`}
            label={`radar vs optique (${Math.round(r.optical_usable_pct)}% sous nuages)`} />
        )}
      </div>
      <p className="mt-3 text-xs text-slate-500">
        Hypothèse : {Math.round(c.assumptions?.co2_t_per_ha)} t CO₂/ha (biomasse forêt
        tropicale du Bassin du Congo, IPCC). Le radar Sentinel-1 traverse les nuages.
      </p>
    </section>
  )
}
