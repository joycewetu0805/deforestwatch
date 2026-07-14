"""
Export des données réelles vers data/raw/ pour DeforestWatch-DRC.

Télécharge, depuis Google Earth Engine, l'ensemble des données nécessaires à un
entraînement supervisé sur images réelles :

  - composites/{year}.tif   : 6 bandes Sentinel-2 (B2,B3,B4,B8,B11,B12), réflectance
  - landcover/{year}.tif    : vérité terrain 5 classes, dérivée de Dynamic World
  - topography.tif          : altitude, pente, aspect (SRTM)

Exemples (Windows PowerShell, sans make) :

  # 0. (test hors-ligne) écrit des GeoTIFF synthétiques au bon format
  python -m scripts.gee_export --demo-geotiff

  # 1. TOUT télécharger en une fois (composites + labels + topo), 2019→2025
  python -m scripts.gee_export --all --years 2019 2020 2021 2022 2023 2024 2025 --scale 60

  # ... ou étape par étape :
  python -m scripts.gee_export --download --years 2019 2020 2021 2022 2023 2024 2025 --scale 60
  python -m scripts.gee_export --labels   --years 2019 2020 2021 2022 2023 2024 2025 --scale 60
  python -m scripts.gee_export --topo --scale 60

  # 2. export pleine résolution 10 m vers Google Drive (composites uniquement)
  python -m scripts.gee_export --drive

Après un export : python -m scripts.check_real_data, puis
python -m scripts.switch_mode real, puis python -m scripts.train_all.

Note : Sentinel-2 Surface Reflectance et Dynamic World couvrent la zone à partir
de ~2017 ; les années antérieures sont ignorées automatiquement.
"""

from __future__ import annotations

import argparse

import numpy as np

from config.settings import ANALYSIS_YEARS, RAW_DIR, settings
from src.utils.helpers import bbox_from_center, ensure_dir
from src.utils.logger import get_logger
from src.utils import synthetic

log = get_logger("gee_export")

# Correspondance classes Dynamic World → classes DeforestWatch (0..4)
#   DW : 0 water, 1 trees, 2 grass, 3 flooded_veg, 4 crops, 5 shrub, 6 built,
#        7 bare, 8 snow
#   Nous : 0 forêt dense, 1 forêt dégradée, 2 agriculture/sol nu, 3 eau, 4 bâti
DW_FROM = [0, 1, 2, 3, 4, 5, 6, 7, 8]
DW_TO = [3, 0, 1, 3, 2, 1, 4, 2, 2]


def _aoi_bbox():
    return bbox_from_center(settings.study_area_lat, settings.study_area_lon,
                            settings.study_area_buffer_km)


def _aoi(ee):
    b = _aoi_bbox()
    return ee.Geometry.Rectangle(
        [b["min_lon"], b["min_lat"], b["max_lon"], b["max_lat"]])


# ──────────────────────────────────────────────────────────────────────────
# Sources Google Earth Engine
# ──────────────────────────────────────────────────────────────────────────
def _annual_collection(ee, aoi, year):
    """Composite médian Sentinel-2 de saison sèche, 6 bandes, réflectance 0..1."""
    def mask(img):
        scl = img.select("SCL")
        keep = scl.neq(3).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10)).And(scl.neq(11))
        return img.updateMask(keep).divide(10000)

    return (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(f"{year}-06-01", f"{year}-09-30")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
        .map(mask)
        .median()
        .select(["B2", "B3", "B4", "B8", "B11", "B12"])
    )


def _annual_labels(ee, aoi, year):
    """Vérité terrain 5 classes dérivée de Google Dynamic World (mode annuel)."""
    dw = (
        ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
        .filterBounds(aoi)
        .filterDate(f"{year}-06-01", f"{year}-09-30")
        .select("label")
    )
    mode = dw.reduce(ee.Reducer.mode()).rename("label")
    return mode.remap(DW_FROM, DW_TO, 2).rename("landcover").toInt16()


def _srtm_topography(ee):
    """Altitude, pente, aspect depuis le MNT SRTM (3 bandes)."""
    dem = ee.Image("USGS/SRTMGL1_003")
    terrain = ee.Terrain.products(dem)  # elevation, slope, aspect, hillshade
    return (terrain.select(["elevation", "slope", "aspect"])
            .rename(["altitude", "slope", "aspect"]).toFloat())


# ──────────────────────────────────────────────────────────────────────────
# Téléchargement direct (GeoTIFF)
# ──────────────────────────────────────────────────────────────────────────
def _fetch_geotiff(img, aoi, scale, path):
    """Télécharge une ee.Image en un unique GeoTIFF multibande valide.

    Utilise filePerBand=False (sinon GEE renvoie un zip d'une bande par fichier,
    ce qui produit des composites illisibles) et vérifie l'en-tête TIFF.
    """
    import io
    import zipfile

    import requests

    url = img.getDownloadURL({
        "region": aoi, "scale": scale,
        "format": "GEO_TIFF", "filePerBand": False,
    })
    data = requests.get(url, timeout=600).content
    if data[:2] == b"PK":  # archive zip → extraire l'unique GeoTIFF
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = [n for n in zf.namelist() if n.endswith(".tif")]
            if not names:
                raise RuntimeError(f"{path.name} : aucun GeoTIFF dans l'archive GEE.")
            data = zf.read(names[0])
    if data[:4] not in (b"II*\x00", b"MM\x00*"):  # en-tête TIFF valide ?
        raise RuntimeError(
            f"{path.name} : réponse GEE invalide (souvent un dépassement de taille "
            "en téléchargement direct). Augmentez --scale, réduisez la zone, ou "
            f"utilisez --drive. Détail : {data[:300]!r}")
    path.write_bytes(data)
    log.info(f"  → {path}")


def download_composites(years, scale=100):
    import ee

    ee.Initialize()  # le projet vient de `earthengine set_project <id>`
    out = ensure_dir(RAW_DIR / "composites")
    aoi = _aoi(ee)
    for year in years:
        img = _annual_collection(ee, aoi, year)
        if img.bandNames().size().getInfo() == 0:
            log.warning(f"{year} : aucune image Sentinel-2 SR (couverture à partir "
                        "de ~2017). Année ignorée.")
            continue
        log.info(f"Composite {year} (scale={scale} m)…")
        _fetch_geotiff(img, aoi, scale, out / f"{year}.tif")


def download_labels(years, scale=100):
    import ee

    ee.Initialize()
    out = ensure_dir(RAW_DIR / "landcover")
    aoi = _aoi(ee)
    for year in years:
        dw = (ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
              .filterBounds(aoi).filterDate(f"{year}-06-01", f"{year}-09-30"))
        if dw.size().getInfo() == 0:
            log.warning(f"{year} : aucune donnée Dynamic World (couverture à partir "
                        "de ~2017). Étiquettes ignorées.")
            continue
        log.info(f"Étiquettes {year} (Dynamic World, scale={scale} m)…")
        _fetch_geotiff(_annual_labels(ee, aoi, year), aoi, scale, out / f"{year}.tif")


def download_topography(scale=100):
    import ee

    ee.Initialize()
    ensure_dir(RAW_DIR)
    aoi = _aoi(ee)
    log.info(f"Topographie SRTM (scale={scale} m)…")
    _fetch_geotiff(_srtm_topography(ee), aoi, scale, RAW_DIR / "topography.tif")


# ──────────────────────────────────────────────────────────────────────────
# Export pleine résolution vers Google Drive (composites)
# ──────────────────────────────────────────────────────────────────────────
def export_to_drive(years, scale=10):
    import ee

    ee.Initialize()
    aoi = _aoi(ee)
    for year in years:
        img = _annual_collection(ee, aoi, year)
        if img.bandNames().size().getInfo() == 0:
            log.warning(f"{year} : aucune image Sentinel-2 SR. Année ignorée.")
            continue
        task = ee.batch.Export.image.toDrive(
            image=img, description=f"deforestwatch_{year}",
            folder="deforestwatch_exports", fileNamePrefix=str(year),
            region=aoi, scale=scale, maxPixels=1e10,
        )
        task.start()
        log.info(f"Tâche d'export Drive lancée pour {year} (suivi : "
                 "https://code.earthengine.google.com/tasks).")
    log.info("Une fois terminées, téléchargez les GeoTIFF depuis Drive vers "
             f"{RAW_DIR / 'composites'}/.")


# ──────────────────────────────────────────────────────────────────────────
# Mode hors-ligne : GeoTIFF synthétiques (test de la chaîne réelle sans GEE)
# ──────────────────────────────────────────────────────────────────────────
def write_demo_geotiffs(years):
    """Écrit composites + landcover + topographie synthétiques en GeoTIFF géoréférencés."""
    import rasterio
    from rasterio.transform import from_bounds

    comp_dir = ensure_dir(RAW_DIR / "composites")
    lc_dir = ensure_dir(RAW_DIR / "landcover")
    series = synthetic.generate_landcover_series()
    b = _aoi_bbox()
    grid = series[years[-1]].shape[0]
    transform = from_bounds(b["min_lon"], b["min_lat"], b["max_lon"], b["max_lat"], grid, grid)
    crs = "EPSG:4326"

    def save(path, arr):
        arr = np.asarray(arr)
        if arr.ndim == 2:
            arr = arr[None, ...]
        else:
            arr = np.transpose(arr, (2, 0, 1))
        with rasterio.open(path, "w", driver="GTiff", height=arr.shape[1],
                           width=arr.shape[2], count=arr.shape[0], dtype=arr.dtype,
                           crs=crs, transform=transform) as ds:
            ds.write(arr)

    for year in years:
        lc = series[year]
        save(comp_dir / f"{year}.tif", synthetic.landcover_to_bands(lc, seed=year))
        save(lc_dir / f"{year}.tif", lc.astype(np.int16))
        log.info(f"  écrit {year}.tif (composite + landcover)")
    save(RAW_DIR / "topography.tif", synthetic.generate_topography(grid=grid))
    log.info(f"GeoTIFF de démonstration écrits dans {RAW_DIR}. "
             "Mettez DEMO_MODE=false puis lancez check_real_data.")


def main():
    ap = argparse.ArgumentParser(description="Export des données réelles vers data/raw/")
    ap.add_argument("--all", action="store_true",
                    help="Télécharge composites + labels + topographie (recommandé)")
    ap.add_argument("--download", action="store_true", help="Composites Sentinel-2 (direct)")
    ap.add_argument("--labels", action="store_true", help="Vérité terrain Dynamic World")
    ap.add_argument("--topo", action="store_true", help="Topographie SRTM")
    ap.add_argument("--drive", action="store_true", help="Composites pleine résolution vers Drive")
    ap.add_argument("--demo-geotiff", action="store_true",
                    help="Écrit des GeoTIFF synthétiques (test hors-ligne)")
    ap.add_argument("--scale", type=int, default=100, help="Résolution en mètres (60 conseillé)")
    ap.add_argument("--years", type=int, nargs="*", default=ANALYSIS_YEARS)
    args = ap.parse_args()

    if args.demo_geotiff:
        write_demo_geotiffs(args.years)
    elif args.drive:
        export_to_drive(args.years, scale=args.scale)
    elif args.all:
        download_composites(args.years, scale=args.scale)
        download_labels(args.years, scale=args.scale)
        download_topography(scale=args.scale)
    elif args.download:
        download_composites(args.years, scale=args.scale)
    elif args.labels:
        download_labels(args.years, scale=args.scale)
    elif args.topo:
        download_topography(scale=args.scale)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
