import { useEffect, useMemo, useRef, useState } from 'react'
import { Map as MapIcon, Box, Square, Loader2 } from 'lucide-react'
import DeckGL from '@deck.gl/react'
import { BitmapLayer, ColumnLayer } from '@deck.gl/layers'
import { Map as MapLibre } from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'

// Fonds de carte CARTO : aucun jeton d'API nécessaire.
const BASEMAPS = {
  Sombre: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
  Clair: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
  Voyager: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
}

const LAYERS = [
  { id: 'risk', label: 'Risque' },
  { id: 'landcover', label: 'Couverture' },
  { id: 'loss', label: 'Pertes' },
]

function Toggle({ options, value, onChange }) {
  return (
    <div className="inline-flex rounded-lg border border-white/10 bg-black/30 p-0.5">
      {options.map((o) => (
        <button
          key={o.id ?? o}
          type="button"
          onClick={() => onChange(o.id ?? o)}
          className={`rounded-md px-3 py-1 text-xs font-medium transition ${
            (o.id ?? o) === value
              ? 'bg-emerald-600 text-white'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          {o.label ?? o}
        </button>
      ))}
    </div>
  )
}

function Legend({ items, prefix }) {
  if (!items?.length) return null
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
      {prefix && <span>{prefix}</span>}
      {items.map((i) => (
        <span key={i.label} className="inline-flex items-center gap-1.5">
          <span
            className="inline-block h-3 w-3 rounded-sm"
            style={{ background: i.color }}
          />
          {i.label}
        </span>
      ))}
    </div>
  )
}

export default function MapView() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(false)
  const [layer, setLayer] = useState('risk')
  const [mode, setMode] = useState('3D')
  const [basemap, setBasemap] = useState('Sombre')
  const [year, setYear] = useState(null)
  const [hover, setHover] = useState(null)
  const containerRef = useRef(null)

  useEffect(() => {
    fetch('demo/map.json')
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error('indisponible'))))
      .then((d) => {
        setData(d)
        setYear(d.years[d.years.length - 1])
      })
      .catch(() => setError(true))
  }, [])

  const viewState = useMemo(
    () => ({
      longitude: data?.center.lon ?? 18.27,
      latitude: data?.center.lat ?? -1.95,
      zoom: 9.2,
      pitch: mode === '3D' ? 48 : 0,
      bearing: 0,
    }),
    [data, mode],
  )

  const layers = useMemo(() => {
    if (!data) return []
    const b = data.bounds
    const bounds = [b.west, b.south, b.east, b.north]
    const extruded = mode === '3D'

    // Couche 2D : les composites déjà exportés en PNG, posés sur leur emprise.
    if (layer === 'landcover') {
      return [
        new BitmapLayer({
          id: `landcover-${year}`,
          image: `demo/landcover/${year}.png`,
          bounds,
          opacity: 0.85,
        }),
      ]
    }

    const cells = layer === 'risk' ? data.risk_cells : data.loss_cells
    return [
      new ColumnLayer({
        id: `${layer}-${mode}`,
        data: cells,
        diskResolution: 4, // cellules carrées : elles pavent la zone sans interstice
        angle: 45,
        radius: data.cell.radius_m,
        coverage: 1,
        extruded,
        elevationScale: extruded ? 1 : 0,
        getPosition: (d) => [d.lon, d.lat],
        getElevation: (d) => d.height,
        getFillColor: (d) => d.color,
        pickable: true,
        autoHighlight: true,
        opacity: 0.85,
        onHover: (info) => setHover(info.object ? info : null),
        transitions: { getElevation: 350 },
      }),
    ]
  }, [data, layer, mode, year])

  const legendItems = data?.legend?.[layer]
  const surface = data?.cell?.surface_ha

  if (error) {
    return (
      <div className="flex h-72 items-center justify-center rounded-xl border border-white/10 bg-panel/50 text-sm text-slate-400">
        Données cartographiques indisponibles. Lancez
        <code className="mx-1 rounded bg-black/40 px-1.5 py-0.5 text-xs">
          make export-frontend
        </code>
        pour les générer.
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <Toggle options={LAYERS} value={layer} onChange={setLayer} />
        <Toggle options={['2D', '3D']} value={mode} onChange={setMode} />
        <Toggle
          options={Object.keys(BASEMAPS)}
          value={basemap}
          onChange={setBasemap}
        />
        {layer === 'landcover' && data && (
          <label className="flex items-center gap-2 text-xs text-slate-400">
            Année
            <input
              type="range"
              min={data.years[0]}
              max={data.years[data.years.length - 1]}
              value={year ?? data.years[0]}
              onChange={(e) => setYear(Number(e.target.value))}
              className="h-1 w-36 accent-emerald-500"
            />
            <span className="w-10 font-semibold text-slate-200">{year}</span>
          </label>
        )}
      </div>

      <div
        ref={containerRef}
        className="relative h-[26rem] overflow-hidden rounded-xl border border-white/10"
      >
        {!data ? (
          <div className="flex h-full items-center justify-center gap-2 text-sm text-slate-400">
            <Loader2 size={16} className="animate-spin" />
            Chargement de la carte…
          </div>
        ) : (
          <>
            <DeckGL
              initialViewState={viewState}
              controller={{ dragRotate: true }}
              layers={layers}
              getCursor={() => 'grab'}
            >
              <MapLibre mapStyle={BASEMAPS[basemap]} reuseMaps />
            </DeckGL>

            {hover?.object && (
              <div
                className="pointer-events-none absolute z-10 rounded-lg border border-white/10 bg-slate-900/95 px-3 py-2 text-xs text-slate-100 shadow-lg"
                style={{ left: hover.x + 12, top: hover.y + 12 }}
              >
                <div className="font-semibold">
                  {layer === 'risk'
                    ? `Risque ${hover.object.value}/100`
                    : hover.object.label}
                </div>
                {layer === 'loss' && (
                  <div>{hover.object.value} ha perdus</div>
                )}
                <div className="text-slate-400">
                  Cellule de {surface} ha
                </div>
                <div className="text-slate-500">
                  {hover.object.lat}, {hover.object.lon}
                </div>
              </div>
            )}

            <div className="pointer-events-none absolute bottom-2 left-3 flex items-center gap-1.5 text-[11px] text-slate-400">
              {mode === '3D' ? <Box size={12} /> : <Square size={12} />}
              {mode === '3D'
                ? 'Ctrl + glisser pour pivoter et incliner'
                : 'Glisser pour déplacer, molette pour zoomer'}
            </div>
          </>
        )}
      </div>

      <Legend
        items={legendItems}
        prefix={layer === 'risk' ? 'Score de risque :' : null}
      />
    </div>
  )
}

export { MapIcon }
