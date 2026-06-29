"""
Génère un rapport de synthèse (Markdown, convertible en PDF) avec les dernières
statistiques de déforestation et les performances des modèles.

Usage : python -m scripts.generate_report
"""

from pathlib import Path

from config.settings import PROCESSED_DIR
from src.utils import synthetic
from src.utils.helpers import load_json
from src.utils.logger import get_logger

log = get_logger("generate_report")


def main() -> None:
    stats = synthetic.yearly_statistics()
    total_loss = sum(s["forest_loss_ha"] for s in stats)
    lines = [
        "# Rapport de synthèse — DeforestWatch-DRC",
        "",
        "## Zone d'étude : Province du Mai-Ndombe (Inongo), RDC",
        "",
        f"- Surface forestière {stats[0]['year']} : **{stats[0]['total_forest_ha']:,.0f} ha**",
        f"- Surface forestière {stats[-1]['year']} : **{stats[-1]['total_forest_ha']:,.0f} ha**",
        f"- Perte totale sur la période : **{total_loss:,.0f} ha** "
        f"({100 * total_loss / stats[0]['total_forest_ha']:.1f} %)",
        "",
        "## Évolution annuelle",
        "",
        "| Année | Forêt (ha) | Perte (ha) | Taux (%) |",
        "|-------|-----------|-----------|----------|",
    ]
    for s in stats:
        lines.append(
            f"| {s['year']} | {s['total_forest_ha']:,.0f} | "
            f"{s['forest_loss_ha']:,.0f} | {s['deforestation_rate']:.2f} |"
        )

    report_path = Path(PROCESSED_DIR) / "model_metrics.json"
    if report_path.exists():
        report = load_json(report_path)
        lines += ["", "## Comparaison des modèles", "",
                  "| Modèle | F1-macro | Mean IoU | Accuracy |",
                  "|--------|----------|----------|----------|"]
        for row in report.get("comparison", []):
            lines.append(
                f"| {row['Modèle']} | {row['F1-macro']} | {row['Mean IoU']} | {row['Accuracy']} |"
            )
        lines += ["", f"**Meilleur modèle : {report.get('best_model')}**"]

    out = Path(PROCESSED_DIR) / "rapport_synthese.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"Rapport généré → {out}")
    # Conversion PDF optionnelle si reportlab/pandoc disponibles
    _try_pdf(out)


def _try_pdf(md_path: Path) -> None:
    try:
        import subprocess

        pdf = md_path.with_suffix(".pdf")
        subprocess.run(["pandoc", str(md_path), "-o", str(pdf)], check=True,
                       capture_output=True)
        log.info(f"PDF généré → {pdf}")
    except Exception:
        log.info("Pandoc indisponible : rapport laissé en Markdown.")


if __name__ == "__main__":
    main()
