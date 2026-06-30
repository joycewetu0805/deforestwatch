"""
Bascule persistante entre données de démonstration et données réelles.

Met à jour `DEMO_MODE` dans le fichier .env (créé depuis .env.example si absent),
ce qui pilote l'API et tout démarrage ultérieur. Pour un basculement à chaud
dans le dashboard, utilisez plutôt le toggle de la barre latérale.

Usage :
  python -m scripts.switch_mode demo    # DEMO_MODE=true  (données synthétiques)
  python -m scripts.switch_mode real    # DEMO_MODE=false (data/raw/)
  python -m scripts.switch_mode status  # affiche l'état courant
"""

from __future__ import annotations

import sys
from pathlib import Path

from config.settings import PROJECT_ROOT
from src.data.sources import RasterSource
from src.utils.logger import get_logger

log = get_logger("switch_mode")

ENV_PATH = PROJECT_ROOT / ".env"
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"


def _read_env() -> list[str]:
    if ENV_PATH.exists():
        return ENV_PATH.read_text(encoding="utf-8").splitlines()
    if ENV_EXAMPLE.exists():
        log.info(".env absent → créé depuis .env.example.")
        return ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
    return []


def _write_demo_mode(value: bool) -> None:
    lines = _read_env()
    target = f"DEMO_MODE={'true' if value else 'false'}"
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith("DEMO_MODE="):
            lines[i] = target
            found = True
            break
    if not found:
        lines.append(target)
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _status() -> None:
    current = "?"
    for line in _read_env():
        if line.strip().startswith("DEMO_MODE="):
            current = line.split("=", 1)[1].strip()
    has = RasterSource.has_data()
    mode = "démo (synthétique)" if current.lower() == "true" else "réel (data/raw/)"
    log.info(f"DEMO_MODE={current} → mode {mode}")
    log.info(f"Données réelles présentes : {'oui (' + str(len(RasterSource().years())) + ' années)' if has else 'non'}")


def main() -> None:
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else "status"

    if arg == "demo":
        _write_demo_mode(True)
        log.info("✅ Basculé en mode DÉMO (données synthétiques). Redémarrez l'API/dashboard.")
    elif arg == "real":
        if not RasterSource.has_data():
            log.warning("⚠️ Aucune image dans data/raw/composites/. L'application "
                        "fera un repli sur la démo. Lancez `make export-demo` ou "
                        "`python -m scripts.gee_export --drive` d'abord.")
        _write_demo_mode(False)
        log.info("✅ Basculé en mode RÉEL (data/raw/). Redémarrez l'API/dashboard.")
    elif arg == "status":
        _status()
    else:
        log.error("Argument attendu : demo | real | status")
        sys.exit(1)


if __name__ == "__main__":
    main()
