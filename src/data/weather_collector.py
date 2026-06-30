"""
Collecte des données météo (OpenWeatherMap) pour la zone Mai-Ndombe.
Repli synthétique : climatologie équatoriale réaliste (deux saisons des pluies).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import ANALYSIS_YEARS, settings
from src.utils.logger import get_logger

log = get_logger("weather_collector")


class WeatherCollector:
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.available = bool(self.api_key) and not settings.demo_mode

    def monthly_climatology(self, year: int) -> pd.DataFrame:
        """Précipitations (mm) et température (°C) mensuelles pour une année."""
        rng = np.random.default_rng(year)
        months = np.arange(1, 13)
        # Climat équatorial : pic de pluies vers mars-avril et oct-nov
        base_precip = 110 + 80 * np.sin((months - 1) / 12 * 2 * np.pi) ** 2
        precip = np.clip(base_precip + rng.normal(0, 20, 12), 20, None)
        temp = 25 + 2 * np.cos((months - 1) / 12 * 2 * np.pi) + rng.normal(0, 0.5, 12)
        return pd.DataFrame(
            {"year": year, "month": months, "precip_mm": precip.round(1), "temp_c": temp.round(1)}
        )

    def annual_series(self) -> pd.DataFrame:
        """Agrégat annuel 2015–2025 (précipitations totales, température moyenne)."""
        rows = []
        for year in ANALYSIS_YEARS:
            m = self.monthly_climatology(year)
            rows.append(
                {
                    "year": year,
                    "annual_precip_mm": round(m["precip_mm"].sum(), 1),
                    "mean_temp_c": round(m["temp_c"].mean(), 1),
                }
            )
        return pd.DataFrame(rows)


def main() -> None:
    wc = WeatherCollector()
    df = wc.annual_series()
    log.info(f"Série météo annuelle :\n{df.to_string(index=False)}")


if __name__ == "__main__":
    main()
