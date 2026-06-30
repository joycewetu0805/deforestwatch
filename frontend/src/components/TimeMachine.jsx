import { useEffect, useMemo, useRef, useState } from 'react'
import { Play, Pause, SkipBack, Satellite } from 'lucide-react'

const CLASSES = [
  { name: 'Forêt dense', color: '#0B6E2D' },
  { name: 'Forêt dégradée', color: '#9BCC4F' },
  { name: 'Agriculture / Sol nu', color: '#D9A441' },
  { name: 'Eau', color: '#2E86C1' },
  { name: 'Urbain / Bâti', color: '#C0392B' },
]

const img = (year) => `/api/v1/maps/landcover/${year}`

// Compteur anime (hectares)
function useTween(value, ms = 700) {
  const [v, setV] = useState(value)
  const from = useRef(value)
  useEffect(() => {
    const start = from.current
    const t0 = performance.now()
    let raf
    const tick = (now) => {
      const p = Math.min((now - t0) / ms, 1)
      setV(start + (value - start) * (1 - Math.pow(1 - p, 3)))
      if (p < 1) raf = requestAnimationFrame(tick)
      else from.current = value
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [value, ms])
  return v
}

export default function TimeMachine({ stats }) {
  const years = useMemo(() => stats.map((s) => s.year), [stats])
  const [idx, setIdx] = useState(years.length - 1)
  const [playing, setPlaying] = useState(false)
  const [swipe, setSwipe] = useState(55)
  const [ok, setOk] = useState(true)

  const year = years[idx]
  const forest = useTween(stats[idx]?.total_forest_ha ?? 0)
  const first = stats[0]
  const lossPct = first ? (1 - (stats[idx]?.total_forest_ha ?? 0) / first.total_forest_ha) * 100 : 0

  // Precharge des images
  useEffect(() => {
    years.forEach((y) => { const im = new Image(); im.src = img(y) })
  }, [years])

  // Lecture automatique
  useEffect(() => {
    if (!playing) return
    const id = setInterval(() => {
      setIdx((i) => {
        if (i >= years.length - 1) { setPlaying(false); return i }
        return i + 1
      })
    }, 900)
    return () => clearInterval(id)
  }, [playing, years.length])

  const restart = () => { setIdx(0); setPlaying(true) }

  return (
    <section className="rounded-2xl border border-white/10 bg-gradient-to-br from-panel/80 to-base p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="flex items-center gap-2 font-semibold text-slate-100">
          <Satellite size={18} className="text-satellite" />
          Machine à remonter le temps — la forêt disparaît sous vos yeux
        </h2>
        <span className="rounded-full bg-emerald-glow/15 px-3 py-1 text-xs text-emerald-glow">
          Mai-Ndombe · {years[0]}–{years[years.length - 1]}
        </span>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.4fr_1fr]">
        {/* Moniteur satellite avec comparateur avant/apres */}
        <div className="relative aspect-square overflow-hidden rounded-xl border border-white/10 bg-black">
          {ok ? (
            <>
              {/* image annee courante (dessous) */}
              <img src={img(year)} alt={`Couverture ${year}`} onError={() => setOk(false)}
                className="absolute inset-0 h-full w-full object-cover" draggable={false} />
              {/* image de reference 2015 (dessus), revelee par le curseur */}
              <img src={img(years[0])} alt={`Couverture ${years[0]}`}
                className="absolute inset-0 h-full w-full object-cover"
                style={{ clipPath: `inset(0 ${100 - swipe}% 0 0)` }} draggable={false} />
              {/* ligne de glissiere */}
              <div className="absolute inset-y-0 w-0.5 bg-emerald-glow shadow-[0_0_12px_#10B981]"
                style={{ left: `${swipe}%` }} />
              <div className="pointer-events-none absolute left-3 top-3 rounded bg-black/60 px-2 py-1 text-xs text-emerald-glow">
                {years[0]} (référence)
              </div>
              <div className="pointer-events-none absolute right-3 top-3 rounded bg-black/60 px-2 py-1 text-xs text-amber-300">
                {year}
              </div>
              {/* balayage satellite */}
              <div className="pointer-events-none absolute inset-0 animate-pulse"
                style={{ background: 'linear-gradient(180deg, transparent 60%, rgba(6,182,212,.08))' }} />
              {/* annee geante */}
              <div className="pointer-events-none absolute bottom-3 left-1/2 -translate-x-1/2 text-5xl font-extrabold tracking-tight text-white/90 drop-shadow-[0_2px_8px_rgba(0,0,0,.8)]">
                {year}
              </div>
              <input type="range" min="0" max="100" value={swipe}
                onChange={(e) => setSwipe(+e.target.value)}
                className="absolute inset-x-0 bottom-0 w-full cursor-ew-resize opacity-0" />
            </>
          ) : (
            <div className="flex h-full items-center justify-center p-6 text-center text-sm text-slate-400">
              Cartes servies par l'API (GET /api/v1/maps/landcover/&#123;year&#125;).<br />
              Lancez le backend (make api) pour l'animation.
            </div>
          )}
        </div>

        {/* Controles + stats */}
        <div className="flex flex-col justify-between">
          <div>
            <div className="text-sm text-slate-400">Surface forestière — {year}</div>
            <div className="text-4xl font-extrabold text-emerald-glow">
              {Math.round(forest).toLocaleString('fr-FR')} <span className="text-xl text-slate-400">ha</span>
            </div>
            <div className="mt-1 text-sm text-alert">▼ {lossPct.toFixed(1)} % perdus depuis {years[0]}</div>

            {/* barre de progression de la perte */}
            <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-gradient-to-r from-emerald-glow to-alert transition-all"
                style={{ width: `${lossPct}%` }} />
            </div>

            {/* legende */}
            <div className="mt-5 grid grid-cols-2 gap-1.5 text-xs text-slate-300">
              {CLASSES.map((c) => (
                <div key={c.name} className="flex items-center gap-2">
                  <span className="inline-block h-3 w-3 rounded-sm" style={{ background: c.color }} />{c.name}
                </div>
              ))}
            </div>
          </div>

          {/* transport */}
          <div className="mt-5">
            <input type="range" min="0" max={years.length - 1} value={idx}
              onChange={(e) => { setPlaying(false); setIdx(+e.target.value) }}
              className="w-full accent-emerald-400" />
            <div className="mt-1 flex justify-between text-[10px] text-slate-500">
              <span>{years[0]}</span><span>{years[years.length - 1]}</span>
            </div>
            <div className="mt-3 flex items-center gap-2">
              <button onClick={() => setPlaying((p) => !p)}
                className="inline-flex items-center gap-2 rounded-lg bg-emerald-glow px-5 py-2 font-semibold text-[#04130c] transition hover:scale-105">
                {playing ? <Pause size={16} /> : <Play size={16} />}{playing ? 'Pause' : 'Lecture'}
              </button>
              <button onClick={restart}
                className="inline-flex items-center gap-2 rounded-lg border border-white/15 px-4 py-2 text-sm text-slate-300 hover:border-emerald-glow/40">
                <SkipBack size={15} /> Rejouer
              </button>
            </div>
            <p className="mt-3 text-xs text-slate-500">
              Glissez sur l'image pour comparer {years[0]} et l'année choisie.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
