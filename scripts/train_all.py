"""
Pipeline complet : prétraitement → entraînement → évaluation.

Usage : python -m scripts.train_all [--full]
"""

import sys

from src.data.dataset_builder import export
from src.models.trainer import train_all
from src.utils.logger import get_logger

log = get_logger("train_all")


def main() -> None:
    quick = "--full" not in sys.argv
    log.info(f"Construction des datasets (quick={quick})…")
    export()
    report = train_all(quick=quick)
    log.info(f"Entraînement terminé. Meilleur modèle : {report['best_model']}")


if __name__ == "__main__":
    main()
