# CongoForest Watch — Frontend React

Interface web professionnelle (dark mode, esthétique mission-control / Global
Forest Watch) pour la plateforme DeforestWatch-DRC.

## Stack
- **React 18** + **Vite**
- **Tailwind CSS** (thème sombre : `#0A0F1C`, vert émeraude `#10B981`, cyan `#06B6D4`)
- **lucide-react** pour les icônes

## Pages
- **LandingPage** — hero avec glow vert, 4 KPI animés (count-up au scroll),
  section « Comment ça marche » avec lignes de data-flow animées, CTA.
- **Dashboard** — KPIs, courbe d'évolution forestière (SVG), grille de risque.
  Récupère les données via `GET /api/v1/statistics` (proxy Vite vers FastAPI) ;
  bascule sur des données statiques si l'API n'est pas joignable.

## Développement
```bash
npm install
npm run dev      # http://localhost:5173 (proxy /api → http://localhost:8000)
npm run build    # build de production dans dist/
```

Pour des données live, lancez le backend en parallèle : `make api` à la racine.
