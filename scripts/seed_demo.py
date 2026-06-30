"""
Génère les artefacts de démo : datasets synthétiques + rapport de métriques,
afin que le dashboard et l'API affichent des résultats immédiatement.

Usage : python -m scripts.seed_demo
"""

from src.data.dataset_builder import export
from src.models.trainer import train_all
from src.utils.logger import get_logger

log = get_logger("seed_demo")


def main() -> None:
    log.info("1/2 — Construction des datasets synthétiques…")
    export()
    log.info("2/2 — Entraînement rapide des modèles…")
    train_all(quick=True)
    log.info("Données de démo prêtes. Lancez `make dashboard` ou `make api`.")


if __name__ == "__main__":
    main()
