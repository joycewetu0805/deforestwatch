# 🚀 Déploiement — DeforestWatch-DRC

Trois composants, chacun sur un hébergeur gratuit. Le plus simple : tout en
**mode démo** (`DEMO_MODE=true`), aucune base de données requise.

| Composant | Hébergeur gratuit | URL type |
|---|---|---|
| Frontend React (vitrine + Time Machine) | **Vercel** | `https://congoforest-watch.vercel.app` |
| API FastAPI | **Render** | `https://deforestwatch-api.onrender.com` |
| Dashboard Streamlit | **Streamlit Community Cloud** | `https://deforestwatch.streamlit.app` |
| Base de données (optionnel) | **Supabase** | PostgreSQL |

> 💡 Le frontend est **autonome** : il embarque des cartes de démo
> (`frontend/public/demo/`) et fonctionne même sans l'API. Une fois l'API
> déployée, il l'utilise automatiquement (voir « Brancher le frontend sur l'API »).

---

## 1. Frontend → Vercel

Le dépôt contient déjà `vercel.json` (build du sous-dossier `frontend/`).

1. Sur https://vercel.com → **Add New → Project** → importez le dépôt GitHub.
2. Laissez les réglages par défaut (Vercel lit `vercel.json`). Déployez.
3. C'est en ligne. ✅

En CLI : `npm i -g vercel && vercel --prod` à la racine du dépôt.

### Brancher le frontend sur l'API (optionnel)
Pour des données live au lieu de la démo, ajoutez un *rewrite* dans `vercel.json`
qui proxifie `/api` vers votre API Render :

```json
"rewrites": [
  { "source": "/api/(.*)", "destination": "https://deforestwatch-api.onrender.com/api/$1" },
  { "source": "/((?!assets/|demo/|favicon).*)", "destination": "/index.html" }
]
```

---

## 2. API FastAPI → Render

Le dépôt contient `render.yaml` (blueprint) et `requirements-api.txt` (dépendances
légères, sans GDAL/TensorFlow).

1. Sur https://dashboard.render.com → **New → Blueprint** → sélectionnez le dépôt.
2. Render lit `render.yaml` : service web Python, plan free, `DEMO_MODE=true`,
   `JWT_SECRET_KEY` généré automatiquement.
3. Déployez. L'API sera sur `https://<nom>.onrender.com` (docs sur `/docs`).

> Le plan free s'endort après inactivité (réveil ~30 s à la 1re requête).

Variables d'environnement utiles : `DEMO_MODE`, `JWT_SECRET_KEY`,
`DATABASE_URL` (si Supabase), `OPENWEATHER_API_KEY`, `GEE_SERVICE_ACCOUNT`.

---

## 3. Dashboard Streamlit → Streamlit Community Cloud

1. Sur https://share.streamlit.io → **New app** → dépôt GitHub.
2. **Main file path** : `streamlit_app/app.py`.
3. (Avancé) Python 3.11. Les dépendances viennent de `requirements.txt`.
4. Déployez. Comptes de démo : `admin@deforestwatch.cd` / `admin123` · 2FA `123456`.

> Le thème sombre est déjà configuré dans `.streamlit/config.toml`.

---

## 4. Base de données → Supabase (optionnel)

Nécessaire seulement si vous voulez persister utilisateurs/logs (sinon SQLite).

1. Sur https://supabase.com → **New project** (notez le mot de passe DB).
2. Récupérez la chaîne `Connection string` (mode *session*, port 5432).
3. Mettez-la dans `DATABASE_URL` côté API (Render) et `DEMO_MODE=false`.
4. Les tables sont créées automatiquement au démarrage de l'API (`init_db`).

---

## Récapitulatif des variables d'environnement

| Variable | Frontend | API | Dashboard |
|---|---|---|---|
| `DEMO_MODE` | — | ✅ (true/false) | ✅ |
| `JWT_SECRET_KEY` | — | ✅ | — |
| `DATABASE_URL` | — | optionnel | optionnel |
| `OPENWEATHER_API_KEY` | — | optionnel | — |
| `GEE_SERVICE_ACCOUNT` / `GEE_KEY_FILE` | — | optionnel | optionnel |

## Checklist de mise en production
- [ ] `DEMO_MODE=false` uniquement si de vraies données sont disponibles
- [ ] `JWT_SECRET_KEY` aléatoire et secret
- [ ] CORS restreint au domaine du frontend (voir `src/api/main.py`)
- [ ] Comptes de démo désactivés / mots de passe changés
