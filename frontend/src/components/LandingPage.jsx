import { useEffect, useRef, useState } from 'react'
import {
  Satellite, Cpu, BellRing, ArrowRight, Leaf, Github,
  ShieldCheck, Map, LineChart, Database,
} from 'lucide-react'

// Compteur animé (count-up) déclenché à l'apparition à l'écran
function useCountUp(target, duration = 1600, start = false) {
  const [value, setValue] = useState(0)
  useEffect(() => {
    if (!start) return
    let raf
    const t0 = performance.now()
    const tick = (now) => {
      const p = Math.min((now - t0) / duration, 1)
      setValue(target * (1 - Math.pow(1 - p, 3)))
      if (p < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [target, duration, start])
  return value
}

function KpiCard({ value, suffix, label, decimals = 0, visible }) {
  const v = useCountUp(value, 1600, visible)
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-md
                    transition hover:-translate-y-1 hover:border-emerald-glow/40 hover:bg-white/10">
      <div className="text-3xl font-bold text-satellite md:text-4xl">
        {v.toLocaleString('fr-FR', { maximumFractionDigits: decimals, minimumFractionDigits: decimals })}
        <span className="text-emerald-glow">{suffix}</span>
      </div>
      <div className="mt-2 text-sm text-slate-400">{label}</div>
    </div>
  )
}

const STEPS = [
  { icon: Satellite, title: 'Acquisition satellite', desc: 'Composites Sentinel-2 & Landsat du Bassin du Congo, saison sèche.' },
  { icon: Cpu, title: 'Analyse IA', desc: 'Random Forest, XGBoost et U-Net classent chaque pixel de forêt.' },
  { icon: BellRing, title: 'Alertes & Décisions', desc: 'Cartes de risque et alertes pour les acteurs de la conservation.' },
]

const FEATURES = [
  { icon: Map, title: 'Cartographie', desc: 'Couverture du sol et fronts de déforestation, année par année.' },
  { icon: LineChart, title: 'Prédiction', desc: 'Zones à risque de déforestation à court terme.' },
  { icon: ShieldCheck, title: 'Sécurisé', desc: 'API FastAPI avec authentification JWT et 2FA.' },
  { icon: Database, title: 'Données ouvertes', desc: 'Sentinel-2/ESA, Landsat/NASA, Hansen GFC, SRTM.' },
]

const TECH = ['Python', 'Google Earth Engine', 'PySpark', 'scikit-learn', 'XGBoost',
  'TensorFlow / U-Net', 'FastAPI', 'Streamlit', 'React', 'PostgreSQL', 'Docker']

function Nav({ onExplore }) {
  return (
    <nav className="sticky top-0 z-50 border-b border-white/10 bg-base/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <div className="flex items-center gap-2 font-bold text-emerald-glow">
          <Leaf size={20} /> CongoForest Watch
        </div>
        <div className="flex items-center gap-6 text-sm text-slate-300">
          <a href="#how" className="hidden hover:text-emerald-glow md:inline">Méthode</a>
          <a href="#features" className="hidden hover:text-emerald-glow md:inline">Fonctions</a>
          <button onClick={onExplore}
            className="rounded-lg bg-emerald-glow/90 px-4 py-1.5 font-semibold text-[#04130c] hover:bg-emerald-glow">
            Dashboard
          </button>
        </div>
      </div>
    </nav>
  )
}

export default function LandingPage({ onExplore }) {
  const heroRef = useRef(null)
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => e.isIntersecting && setVisible(true), { threshold: 0.3 })
    if (heroRef.current) obs.observe(heroRef.current)
    return () => obs.disconnect()
  }, [])

  return (
    <div className="min-h-screen bg-base text-slate-200">
      <Nav onExplore={onExplore} />

      {/* Hero */}
      <section className="relative overflow-hidden px-6 pb-16 pt-20 text-center">
        <div className="pointer-events-none absolute inset-0 opacity-40"
          style={{ background: 'radial-gradient(circle at 30% 20%, rgba(16,185,129,0.25), transparent 45%), radial-gradient(circle at 75% 60%, rgba(6,182,212,0.18), transparent 40%)' }} />
        <div className="relative mx-auto max-w-4xl">
          <span className="inline-flex items-center gap-2 rounded-full border border-emerald-glow/30 bg-emerald-glow/10 px-4 py-1 text-sm text-emerald-glow">
            <Leaf size={16} /> Forêt équatoriale · RDC · Bassin du Congo
          </span>
          <h1 className="glow mt-6 text-5xl font-extrabold tracking-tight text-emerald-glow md:text-7xl">
            CongoForest Watch
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-300">
            Surveillance en temps réel de la déforestation au Bassin du Congo par
            imagerie satellite et intelligence artificielle.
          </p>
          <div className="mt-10 flex items-center justify-center gap-3">
            <button onClick={onExplore}
              className="inline-flex items-center gap-2 rounded-xl bg-emerald-glow px-8 py-3
                         font-semibold text-base text-[#04130c] shadow-lg shadow-emerald-glow/30
                         transition hover:scale-105 hover:shadow-emerald-glow/50">
              Explorer la carte <ArrowRight size={18} />
            </button>
            <a href="#how"
              className="inline-flex items-center gap-2 rounded-xl border border-white/15 px-6 py-3
                         text-sm text-slate-300 transition hover:border-emerald-glow/40 hover:text-emerald-glow">
              En savoir plus
            </a>
          </div>
        </div>

        {/* KPI cards */}
        <div ref={heroRef} className="relative mx-auto mt-16 grid max-w-5xl grid-cols-2 gap-4 md:grid-cols-4">
          <KpiCard value={2.4} suffix="M ha" decimals={1} label="Surface surveillée" visible={visible} />
          <KpiCard value={47230} suffix=" ha" label="Perte forestière (2024)" visible={visible} />
          <KpiCard value={12} suffix="" label="Alertes actives cette semaine" visible={visible} />
          <KpiCard value={94.7} suffix=" %" decimals={1} label="Précision du modèle CNN" visible={visible} />
        </div>
      </section>

      {/* Comment ça marche */}
      <section id="how" className="px-6 py-16">
        <h2 className="text-center text-3xl font-bold text-slate-100">Comment ça marche</h2>
        <div className="relative mx-auto mt-12 flex max-w-5xl flex-col items-stretch justify-center gap-6 md:flex-row">
          {STEPS.map((s, i) => (
            <div key={i} className="flex-1">
              <div className="flex h-full flex-col items-center rounded-2xl border border-white/10 bg-panel/60 p-8 text-center">
                <div className="rounded-full bg-emerald-glow/15 p-4 text-emerald-glow">
                  <s.icon size={32} />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-slate-100">{s.title}</h3>
                <p className="mt-2 text-sm text-slate-400">{s.desc}</p>
              </div>
              {i < STEPS.length - 1 && (
                <svg className="mx-auto hidden h-2 w-24 md:block" viewBox="0 0 100 4">
                  <line className="dataflow" x1="0" y1="2" x2="100" y2="2" stroke="#10B981" strokeWidth="2" />
                </svg>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Fonctionnalités */}
      <section id="features" className="bg-white/[0.02] px-6 py-16">
        <h2 className="text-center text-3xl font-bold text-slate-100">Une plateforme complète</h2>
        <div className="mx-auto mt-10 grid max-w-5xl grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f, i) => (
            <div key={i} className="rounded-2xl border border-white/10 bg-panel/50 p-6 transition hover:border-satellite/40">
              <f.icon size={26} className="text-satellite" />
              <h3 className="mt-3 font-semibold text-slate-100">{f.title}</h3>
              <p className="mt-1 text-sm text-slate-400">{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Stack technique */}
        <div className="mx-auto mt-12 max-w-4xl text-center">
          <p className="text-sm uppercase tracking-widest text-slate-500">Stack technique</p>
          <div className="mt-4 flex flex-wrap justify-center gap-2">
            {TECH.map((t) => (
              <span key={t} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
                {t}
              </span>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-white/10 px-6 py-10 text-center text-sm text-slate-500">
        <div className="flex items-center justify-center gap-2 text-slate-400">
          <Github size={16} /> Projet de fin d'études — UPC / FASI · Data Science · 2026
        </div>
        <div className="mt-2">Données : Sentinel-2/ESA · Landsat/NASA · Hansen GFC · SRTM</div>
      </footer>
    </div>
  )
}
