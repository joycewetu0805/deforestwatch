"""
Estimation des émissions de CO₂ liées à la déforestation.

Convertit la perte forestière (hectares) en tonnes de CO₂ rejetées, à partir de
la biomasse aérienne moyenne d'une forêt tropicale humide du Bassin du Congo.
Transforme un résultat technique (ha perdus) en indicateur d'impact climatique.
"""

from __future__ import annotations

from config.settings import (
    AGB_TONNES_PER_HA,
    CARBON_FRACTION,
    CO2_PER_CARBON,
    CO2_TONNES_PER_HA,
)
from src.data import provider

# Absorption annuelle moyenne d'un arbre mature (~21 kg CO₂/an) → équivalences
CO2_PER_TREE_YEAR_T = 0.021
# Émissions annuelles moyennes d'une voiture (t CO₂/an, ordre de grandeur)
CO2_PER_CAR_YEAR_T = 4.6


def co2_from_loss(area_lost_ha: float) -> float:
    """Tonnes de CO₂ émises pour une surface déforestée (ha)."""
    return round(max(area_lost_ha, 0.0) * CO2_TONNES_PER_HA, 1)


def yearly_carbon() -> list[dict]:
    """Émissions de CO₂ par année, dérivées des statistiques de déforestation."""
    stats = provider.yearly_statistics()
    out = []
    cumulative = 0.0
    for s in stats:
        emitted = co2_from_loss(s["forest_loss_ha"])
        cumulative += emitted
        out.append({
            "year": s["year"],
            "forest_loss_ha": s["forest_loss_ha"],
            "co2_emitted_t": emitted,
            "co2_cumulative_t": round(cumulative, 1),
        })
    return out


def summary() -> dict:
    """Synthèse carbone : total émis + équivalences parlantes."""
    years = yearly_carbon()
    total = round(sum(y["co2_emitted_t"] for y in years), 1)
    return {
        "total_co2_t": total,
        "total_co2_mt": round(total / 1e6, 3),                 # mégatonnes
        "assumptions": {
            "agb_t_per_ha": AGB_TONNES_PER_HA,
            "carbon_fraction": CARBON_FRACTION,
            "co2_per_carbon": round(CO2_PER_CARBON, 3),
            "co2_t_per_ha": round(CO2_TONNES_PER_HA, 1),
        },
        "equivalents": {
            "cars_year": round(total / CO2_PER_CAR_YEAR_T),    # voitures/an équivalentes
            "trees_year": round(total / CO2_PER_TREE_YEAR_T),  # arbres pour compenser/an
        },
        "worst_year": max(years, key=lambda y: y["co2_emitted_t"])["year"] if years else None,
    }


def main() -> None:
    from src.utils.logger import get_logger

    log = get_logger("carbon")
    s = summary()
    log.info(f"CO₂ total émis : {s['total_co2_t']:,.0f} t "
             f"(≈ {s['total_co2_mt']} Mt) — équiv. {s['equivalents']['cars_year']:,} "
             f"voitures/an. Pire année : {s['worst_year']}.")


if __name__ == "__main__":
    main()
