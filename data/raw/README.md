# Données brutes — comment brancher de **vraies** images satellites

Ce dossier accueille les vraies données de la **forêt équatoriale du Bassin du
Congo** (zone Mai-Ndombe). Tant qu'il est vide, l'application tourne en
**mode démo** sur des données synthétiques. Dès que vous y déposez des images au
format ci-dessous **et** que vous mettez `DEMO_MODE=false` dans `.env`, toute la
chaîne (datasets ML, statistiques, dashboard, API) bascule automatiquement sur
les données réelles — aucun code à modifier.

## Arborescence attendue

```
data/raw/
├── composites/
│   ├── 2015.tif        # composite annuel saison sèche
│   ├── 2016.tif
│   └── ...             # une image par année
├── landcover/          # (optionnel mais requis pour l'entraînement supervisé)
│   ├── 2015.tif        # carte de classes (vérité terrain)
│   └── ...
└── topography.tif      # altitude, pente, aspect
```

## Format des fichiers

| Fichier | Bandes | Description |
|---|---|---|
| `composites/{année}.tif` | 6 | B2, B3, B4, B8, B11, B12 (réflectance Sentinel-2, ordre **imposé**) |
| `landcover/{année}.tif` | 1 | Classes entières `0..4` (voir ci-dessous) |
| `topography.tif` | 3 | Altitude (m), pente (°), aspect (°) — SRTM |

Toutes les images d'une même zone **doivent avoir la même grille** (même
hauteur × largeur, même emprise, même résolution). L'alignement est vérifié au
chargement.

### Résolution : n'importe laquelle, du moment qu'elle est cohérente

La grille n'a pas à faire 256 × 256. La surface d'un pixel est déduite des
dimensions de l'image lue et de l'emprise de la zone d'étude, donc un export à
10 m (5000 × 5000 sur 50 km) comme un aperçu à 100 m (500 × 500) donnent les
mêmes hectares. Ce qui compte est que **l'emprise couverte par vos images
corresponde à la zone configurée** dans `.env` :

```
STUDY_AREA_LAT=-1.95
STUDY_AREA_LON=18.27
STUDY_AREA_BUFFER_KM=25      # zone de 50 km de côté
```

Si vous exportez une autre emprise, ajustez ces trois valeurs, sinon toutes les
surfaces seront fausses d'un facteur constant.

### Classes de couverture (`landcover/`)
| Code | Classe |
|---|---|
| 0 | Forêt dense |
| 1 | Forêt dégradée |
| 2 | Agriculture / Sol nu |
| 3 | Eau |
| 4 | Zone urbaine / Bâti |

## Comment produire ces fichiers

1. **Google Earth Engine** : authentifiez-vous (`earthengine authenticate`),
   renseignez `GEE_SERVICE_ACCOUNT` / `GEE_KEY_FILE` dans `.env`, puis exportez
   les composites Sentinel-2 (le code de collecte est dans
   `src/data/gee_collector.py`). Exportez vers Google Drive/GCS puis téléchargez
   les GeoTIFF ici.
2. **Vérité terrain** : utilisez le produit *Hansen Global Forest Change* et/ou
   une annotation manuelle pour générer les cartes de classes `landcover/`.
3. **Topographie** : exportez le DEM SRTM et dérivez pente/aspect.

## Vérifier votre jeu de données

```bash
python -m scripts.check_real_data
```

Le script liste les années détectées, contrôle le nombre de bandes et
l'alignement des grilles, et indique si l'entraînement supervisé est possible.

## Vérifier que l'application lit bien vos images

```bash
python -c "from src.data import provider; print(provider.info())"
```

`"source": "raster"` et `"is_real": true` confirment que les vraies données
sont servies. Si vous voyez `"synthetic"` alors que vos fichiers sont en place,
vérifiez que `DEMO_MODE=false` figure bien dans `.env`.

> Astuce : vous pouvez commencer avec **une seule année** de composite pour
> valider la chaîne, puis enrichir au fil du temps.
