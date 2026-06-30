"""
Lance la collecte complète des données (GEE + météo) pour toutes les années.
En mode démo, génère les composites synthétiques et la série météo.

Usage : python -m scripts.collect_data
"""

from config.settings import ANALYSIS_YEARS, PROCESSED_DIR
from src.data.gee_collector import GEECollector
from src.data.weather_collector import WeatherCollector
from src.utils.helpers import ensure_dir
from src.utils.logger import get_logger

log = get_logger("collect_data")


def main() -> None:
    ensure_dir(PROCESSED_DIR)
    gee = GEECollector()
    for year in ANALYSIS_YEARS:
        comp = gee.get_annual_composite(year)
        log.info(f"Composite {year} : {comp.shape}")
    weather = WeatherCollector().annual_series()
    weather.to_csv(PROCESSED_DIR / "weather.csv", index=False)
    log.info(f"Météo annuelle exportée → {PROCESSED_DIR / 'weather.csv'}")
    log.info("Collecte terminée.")


if __name__ == "__main__":
    main()
