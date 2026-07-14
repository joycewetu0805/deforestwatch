"""
Export des composites Sentinel-2 vers data/raw/ (vraies données).

Trois modes :

  # 1. Export réel depuis Google Earth Engine vers Google Drive (production)
  python -m scripts.gee_export --drive

  # 2. Téléchargement direct GEE en GeoTIFF (zone réduite / aperçu)
  python -m scripts.gee_export --download --scale 100

  # 3. Écrit les composites synthétiques en GeoTIFF (test de la chaîne réelle
  #    sans compte GEE) — permet de valider RasterSource immédiatement
  python -m scripts.gee_export --demo-geotiff

Après un export, lancez `make check-data` puis mettez DEMO_MODE=false.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from config.settings import ANALYSIS_YEARS, RAW_DIR, settings
from src.utils.helpers import bbox_from_center, ensure_dir
from src.utils.logger import get_logger
from src.utils import synthetic

log = get_logger("gee_export")


def _aoi_bbox():
    return bbox_from_center(settings.study_area_lat, settings.study_area_lon,
                            settings.study_area_buffer_km)


# ──────────────────────────────────────────────────────────────────────────
# Mode 1/2 : Google Earth Engine
# ──────────────────────────────────────────────────────────────────────────
def _annual_collection(ee, aoi, year):
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


def export_to_drive(years, scale=10):
    import ee

    ee.Initialize()
    b = _aoi_bbox()
    aoi = ee.Geometry.Rectangle([b["min_lon"], b["min_lat"], b["max_lon"], b["max_lat"]])
    for year in years:
        img = _annual_collection(ee, aoi, year)
        task = ee.batch.Export.image.toDrive(
            image=img, description=f"deforestwatch_{year}",
            folder="deforestwatch_exports", fileNamePrefix=str(year),
            region=aoi, scale=scale, maxPixels=1e10,
        )
        task.start()
        log.info(f"Tâche d'export Drive lancée pour {year} (suivez l'état sur "
                 "https://code.earthengine.google.com/tasks).")
    log.info("Une fois terminés, téléchargez les GeoTIFF depuis Drive vers "
             f"{RAW_DIR / 'composites'}/.")


def download_direct(years, scale=100):
    import io
    import zipfile

    import ee
    import requests

    ee.Initialize()  # le projet vient de `earthengine set_project <id>`
    out = ensure_dir(RAW_DIR / "composites")
    b = _aoi_bbox()
    aoi = ee.Geometry.Rectangle([b["min_lon"], b["min_lat"], b["max_lon"], b["max_lat"]])
    for year in years:
        img = _annual_collection(ee, aoi, year)
        # Sentinel-2 SR n'existe pas avant ~2017 → collection vide, aucune bande.
        if img.bandNames().size().getInfo() == 0:
            log.warning(f"{year} : aucune image Sentinel-2 SR disponible "
                        "(couverture à partir de ~2017). Année ignorée.")
            continue
        # filePerBand=False => un seul GeoTIFF multibande (et non un zip d'une
        # bande par fichier, cause des composites illisibles).
        url = img.getDownloadURL({
            "region": aoi, "scale": scale,
            "format": "GEO_TIFF", "filePerBand": False,
        })
        log.info(f"Téléchargement {year} (scale={scale} m)…")
        data = requests.get(url, timeout=600).content
        if data[:2] == b"PK":  # archive zip → on extrait l'unique GeoTIFF
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                names = [n for n in zf.namelist() if n.endswith(".tif")]
                if not names:
                    raise RuntimeError(f"{year} : aucun GeoTIFF dans l'archive GEE.")
                data = zf.read(names[0])
        # Un vrai GeoTIFF commence par 'II*\\x00' (little-endian) ou 'MM\\x00*'.
        if data[:4] not in (b"II*\x00", b"MM\x00*"):
            raise RuntimeError(
                f"{year} : réponse GEE invalide (souvent un dépassement de taille "
                "de téléchargement direct). Augmentez --scale ou réduisez la zone, "
                f"ou utilisez l'export Drive. Détail : {data[:300]!r}")
        (out / f"{year}.tif").write_bytes(data)
        log.info(f"  → {out / f'{year}.tif'}")


# ──────────────────────────────────────────────────────────────────────────
# Mode 3 : GeoTIFF synthétiques (test de la chaîne réelle sans GEE)
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
             "Mettez DEMO_MODE=false puis lancez `make check-data`.")


def main():
    ap = argparse.ArgumentParser(description="Export Sentinel-2 vers data/raw/")
    ap.add_argument("--drive", action="store_true", help="Export GEE vers Google Drive")
    ap.add_argument("--download", action="store_true", help="Téléchargement direct GEE (GeoTIFF)")
    ap.add_argument("--demo-geotiff", action="store_true",
                    help="Écrit des GeoTIFF synthétiques pour tester la chaîne réelle")
    ap.add_argument("--scale", type=int, default=100, help="Résolution en mètres")
    ap.add_argument("--years", type=int, nargs="*", default=ANALYSIS_YEARS)
    args = ap.parse_args()

    if args.demo_geotiff:
        write_demo_geotiffs(args.years)
    elif args.drive:
        export_to_drive(args.years, scale=args.scale)
    elif args.download:
        download_direct(args.years, scale=args.scale)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
