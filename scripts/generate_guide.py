"""
Génère le guide complet du projet DeforestWatch-DRC : à la fois documentation
de référence et mode d'emploi.

Produit deux fichiers à partir d'une source unique :
  - GUIDE.md           (à la racine, rendu parfait sur GitHub)
  - docs/GUIDE.pdf     (version imprimable / hors-ligne)

Usage : python -m scripts.generate_guide
"""

from __future__ import annotations

from pathlib import Path

from config.settings import PROJECT_ROOT
from src.utils.logger import get_logger

log = get_logger("generate_guide")


# ──────────────────────────────────────────────────────────────────────────
# Modèle de document : liste de blocs (type, contenu)
# ──────────────────────────────────────────────────────────────────────────
def document() -> list[tuple]:
    B: list[tuple] = []
    h1 = lambda t: B.append(("h1", t))          # noqa: E731
    h2 = lambda t: B.append(("h2", t))          # noqa: E731
    h3 = lambda t: B.append(("h3", t))          # noqa: E731
    p = lambda t: B.append(("p", t))            # noqa: E731
    ul = lambda items: B.append(("ul", items))  # noqa: E731
    code = lambda t: B.append(("code", t.strip("\n")))  # noqa: E731
    table = lambda h, r: B.append(("table", (h, r)))    # noqa: E731
    hr = lambda: B.append(("hr", None))          # noqa: E731

    # ── Titre ──
    h1("DeforestWatch-DRC — Guide complet & mode d'emploi")
    p("Surveillance et prediction de la deforestation de la foret equatoriale du "
      "Bassin du Congo (province du Mai-Ndombe, RDC) par imagerie satellite et "
      "Machine Learning.")
    p("Projet de fin d'etudes — L3 Data Science, Universite Protestante au Congo (FASI). "
      "Ce document explique TOUT le projet et sert de mode d'emploi pas a pas.")
    hr()

    # ── 1. Présentation ──
    h2("1. Presentation du projet")
    p("La RDC abrite la deuxieme plus grande foret tropicale humide du monde. "
      "DeforestWatch-DRC exploite les images satellites Sentinel-2 et des modeles de "
      "Machine Learning pour detecter, quantifier et predire la deforestation, et "
      "fournit une plateforme d'aide a la decision.")
    h3("Ce que fait le projet")
    ul([
        "Detecter les zones deforestees par classification d'images (5 classes de couverture).",
        "Quantifier la perte forestiere annee par annee (2015-2025).",
        "Comparer trois modeles : Random Forest, XGBoost, U-Net (CNN).",
        "Predire les zones a risque de deforestation future.",
        "Servir une API (FastAPI) et deux interfaces (dashboard Streamlit + frontend React).",
    ])
    h3("Mode demonstration vs donnees reelles")
    p("Le projet fonctionne CLE EN MAIN grace a un mode demonstration : des donnees "
      "satellites synthetiques realistes permettent de tout faire tourner sans compte "
      "Google Earth Engine. Quand vous disposez de vraies images, vous basculez en un "
      "clic (voir section 6).")

    # ── 2. Arborescence ──
    h2("2. Architecture et arborescence")
    code(
        "deforestwatch/\n"
        "  config/            Configuration centralisee (settings.py)\n"
        "  src/\n"
        "    data/            Collecte GEE, meteo, sources (demo/reel), provider\n"
        "    preprocessing/   Indices spectraux, masquage nuages, mosaiques, PySpark\n"
        "    models/          Random Forest, XGBoost, U-Net, trainer, evaluator, risque\n"
        "    visualization/   Cartes (Folium), graphiques (Plotly)\n"
        "    api/             API FastAPI (auth 2FA/JWT, routes, base de donnees)\n"
        "    utils/           Logger, helpers, generateur synthetique\n"
        "  streamlit_app/     Dashboard (login, dashboard, analyse, predictions, admin)\n"
        "  frontend/          Frontend React (Vite + Tailwind)\n"
        "  notebooks/         01 EDA, 02 pretraitement, 03 modelisation, 04 resultats\n"
        "  scripts/           Automatisation (collecte, entrainement, export, docs)\n"
        "  tests/             Suite pytest (29 tests)\n"
        "  data/              raw/ (vraies images) - processed/ - models/\n"
        "  docs/              Memoire, slides, ce guide"
    )

    # ── 3. Stack ──
    h2("3. Stack technique")
    table(["Composant", "Technologie"], [
        ["Langage", "Python 3.11"],
        ["Collecte satellite", "Google Earth Engine, rasterio"],
        ["Big Data", "PySpark"],
        ["ML classique", "scikit-learn, XGBoost"],
        ["Deep Learning", "TensorFlow / Keras (U-Net)"],
        ["API", "FastAPI (JWT + 2FA)"],
        ["Dashboards", "Streamlit + React (Vite/Tailwind)"],
        ["Base de donnees", "PostgreSQL / Supabase (repli SQLite)"],
        ["Conteneurisation", "Docker, docker-compose"],
        ["Tests / CI", "pytest, GitHub Actions"],
    ])

    # ── 4. Installation ──
    h2("4. Installation")
    code(
        "# 1. Cloner le depot\n"
        "git clone https://github.com/joycewetu0805/deforestwatch.git\n"
        "cd deforestwatch\n\n"
        "# 2. Environnement virtuel\n"
        "python -m venv venv\n"
        "source venv/bin/activate        # Windows : venv\\Scripts\\activate\n\n"
        "# 3. Dependances\n"
        "pip install -r requirements.txt\n\n"
        "# 4. Configuration\n"
        "cp .env.example .env            # editez si besoin (DEMO_MODE=true par defaut)"
    )

    # ── 5. Démarrage rapide ──
    h2("5. Demarrage rapide (mode demo)")
    p("Aucune cle API requise. En quatre commandes :")
    code(
        "make seed        # genere les donnees de demo + entraine les modeles\n"
        "make api         # API FastAPI        -> http://localhost:8000/docs\n"
        "make dashboard   # Dashboard Streamlit -> http://localhost:8501\n"
        "make frontend    # Frontend React      -> http://localhost:5173"
    )
    h3("Comptes de demonstration (dashboard)")
    table(["Email", "Mot de passe", "Code 2FA", "Role"], [
        ["admin@deforestwatch.cd", "admin123", "123456", "admin"],
        ["user@deforestwatch.cd", "user123", "123456", "utilisateur"],
    ])

    # ── 6. Données : démo <-> réel ──
    h2("6. Donnees : basculer entre demo et reel")
    p("C'est le point central pour passer du prototype aux vraies images. "
      "Trois facons, de la plus simple a la plus permanente :")
    table(["Methode", "Action", "Portee"], [
        ["Toggle dashboard", "Barre laterale > Source de donnees (Auto/Demo/Reelle)",
         "A chaud, sans redemarrer"],
        ["API (admin)", "POST /api/v1/admin/source/{auto|demo|real}", "Process API en cours"],
        ["Persistant (.env)", "make demo / make real / make mode", "Tous les demarrages suivants"],
    ])
    p("Mode Auto : utilise les vraies images si presentes dans data/raw/, sinon la demo. "
      "Si vous demandez 'reel' sans donnees disponibles, l'application fait un repli "
      "transparent sur la demo.")

    h3("Format attendu des vraies images (data/raw/)")
    code(
        "data/raw/\n"
        "  composites/2015.tif   # 6 bandes Sentinel-2 : B2,B3,B4,B8,B11,B12 (reflectance)\n"
        "  composites/2016.tif   # une image par annee\n"
        "  landcover/2015.tif    # (optionnel) classes 0..4 = verite terrain\n"
        "  topography.tif        # 3 bandes : altitude, pente, aspect"
    )
    p("Classes de couverture : 0=Foret dense, 1=Foret degradee, 2=Agriculture/Sol nu, "
      "3=Eau, 4=Urbain/Bati. Toutes les images d'une zone doivent partager la meme grille.")
    code("make check-data   # verifie annees, bandes, alignement, etiquettes")

    # ── 7. Télécharger les données depuis GEE ──
    h2("7. Telecharger les vraies donnees depuis Google Earth Engine")
    p("C'est la fonctionnalite que vous aviez en v1 : recuperer directement les images "
      "Sentinel-2. Le script scripts/gee_export.py s'en charge.")
    h3("Etape 1 — Authentification GEE")
    p("Creez un compte Earth Engine (gratuit pour usage academique) sur "
      "https://earthengine.google.com, puis authentifiez-vous :")
    code(
        "earthengine authenticate          # ouvre le navigateur, colle le jeton\n"
        "# OU compte de service (sans interaction) : renseignez dans .env\n"
        "#   GEE_SERVICE_ACCOUNT=...@...iam.gserviceaccount.com\n"
        "#   GEE_KEY_FILE=config/gee-key.json"
    )
    h3("Etape 2 — Lancer l'export")
    code(
        "# Option A : export vers Google Drive (pleine resolution 10 m, recommande)\n"
        "python -m scripts.gee_export --drive\n"
        "#   -> cree une tache par annee ; suivez-les sur\n"
        "#      https://code.earthengine.google.com/tasks\n"
        "#   -> telechargez ensuite les GeoTIFF depuis Drive vers data/raw/composites/\n\n"
        "# Option B : telechargement direct (zone reduite / apercu rapide)\n"
        "python -m scripts.gee_export --download --scale 100\n"
        "#   -> ecrit directement data/raw/composites/{annee}.tif\n\n"
        "# Choisir les annees (par defaut 2015..2025)\n"
        "python -m scripts.gee_export --download --years 2023 2024 2025 --scale 60"
    )
    h3("Etape 3 — Tester SANS compte GEE")
    p("Pour valider toute la chaine reelle sans authentification, generez des GeoTIFF "
      "synthetiques au bon format :")
    code(
        "make export-demo        # ecrit data/raw/composites + landcover + topography\n"
        "make check-data         # verifie le jeu de donnees\n"
        "# puis dans le dashboard : toggle 'Donnees reelles' (ou make real)"
    )
    h3("Etape 4 — Basculer en mode reel")
    code(
        "make real               # DEMO_MODE=false dans .env\n"
        "make train              # re-entraine les modeles sur les vraies images\n"
        "make dashboard          # le dashboard lit desormais data/raw/"
    )

    # ── 8. Les interfaces ──
    h2("8. Les interfaces")
    h3("API FastAPI (port 8000)")
    p("Documentation interactive Swagger sur http://localhost:8000/docs. Principaux "
      "endpoints :")
    ul([
        "POST /api/v1/auth/register, /auth/login, /auth/verify-otp — authentification + 2FA",
        "GET  /api/v1/statistics — perte forestiere par annee",
        "GET  /api/v1/predictions/{year} — synthese des zones a risque",
        "GET  /api/v1/models — performances des modeles",
        "GET  /api/v1/source — source de donnees active (demo/reel)",
        "GET  /api/v1/maps/landcover/{year} — carte de couverture (PNG) d'une annee",
        "GET  /api/v1/maps/risk — carte de risque (PNG)",
        "POST /api/v1/admin/source/{mode} — bascule demo/reel (admin)",
        "GET  /api/v1/admin/users, /admin/logs — back-office (admin)",
    ])
    h3("Dashboard Streamlit (port 8501)")
    ul([
        "Connexion securisee (email + mot de passe + code 2FA).",
        "Dashboard : KPIs, carte, evolution forestiere, top secteurs touches.",
        "Analyse : classification par annee, comparaison, matrice de confusion du modele.",
        "Predictions : carte de risque, zones critiques.",
        "Admin : utilisateurs, logs, metriques, modeles (role admin uniquement).",
        "Barre laterale : toggle Source de donnees (demo / reel) a chaud.",
    ])
    h3("Frontend React (port 5173)")
    ul([
        "Landing page 'CongoForest Watch' : hero anime, KPIs, fonctionnalites, stack.",
        "Machine a remonter le temps : time-lapse animee de la deforestation 2015-2025 "
        "avec lecture automatique et comparateur avant/apres (glissiere 2015 vs annee).",
        "Dashboard de monitoring : KPIs, courbes, carte de risque (fetch /api/v1/statistics).",
        "Lancement : cd frontend && npm install && npm run dev",
    ])

    # ── 9. Modèles ──
    h2("9. Modeles de Machine Learning")
    table(["Modele", "Type", "Entree"], [
        ["Random Forest", "Pixel (baseline)", "13 features (6 bandes + 4 indices + 3 topo)"],
        ["XGBoost", "Pixel (boosting)", "13 features"],
        ["U-Net (CNN)", "Segmentation", "Tuiles 128x128x6"],
        ["Risk Predictor", "Risque binaire", "Distances routes/villages, pente, voisinage"],
    ])
    p("Entrainement : make train (rapide) ou make train avec l'option complete. "
      "Metriques : Accuracy, Precision, Recall, F1, AUC-ROC, IoU par classe, Mean IoU, "
      "matrice de confusion. Le rapport est ecrit dans data/processed/model_metrics.json.")

    # ── 10. Tests & CI ──
    h2("10. Tests et integration continue")
    code(
        "make test                       # 29 tests pytest (pretraitement, modeles, API, sources)\n"
        "pytest tests/ -v --cov=src      # avec couverture"
    )
    p("GitHub Actions (.github/workflows/ci.yml) execute les tests, le lint (pyflakes) et "
      "le build du frontend a chaque push / pull request.")

    # ── 11. Livrables académiques ──
    h2("11. Livrables academiques")
    code(
        "make memoir      # docs/memoire_deforestwatch.docx (page de garde, 4 chapitres,\n"
        "                 #   bibliographie, annexes)\n"
        "make slides      # docs/soutenance_deforestwatch.pptx (16 slides)\n"
        "make report      # data/processed/rapport_synthese.md (synthese chiffree)\n"
        "make guide       # GUIDE.md + docs/GUIDE.pdf (ce document)"
    )

    # ── 12. Déploiement ──
    h2("12. Deploiement")
    code(
        "docker-compose up --build       # API + dashboard + PostgreSQL\n"
        "#   API       -> http://localhost:8000\n"
        "#   Dashboard -> http://localhost:8501"
    )
    p("Production : renseignez les cles dans .env (GEE, Supabase, OpenWeather, JWT), "
      "mettez DEMO_MODE=false. Pistes d'hebergement gratuit : dashboard sur Streamlit "
      "Community Cloud, API sur Render, base sur Supabase.")

    # ── 13. Dépannage ──
    h2("13. Depannage (FAQ)")
    ul([
        "TensorFlow/XGBoost non installes : les modeles ont un repli automatique, "
        "tout fonctionne (le U-Net utilise des centroides spectraux, XGBoost un "
        "GradientBoosting). Installez-les pour les vraies performances.",
        "PostgreSQL indisponible : l'API bascule automatiquement sur SQLite local.",
        "Le mode 'reel' affiche la demo : aucune image dans data/raw/composites/ "
        "(lancez make export-demo ou l'export GEE).",
        "Google Earth Engine refuse l'acces : relancez earthengine authenticate ou "
        "verifiez le compte de service dans .env.",
    ])

    # ── 14. Référence rapide ──
    h2("14. Reference rapide des commandes")
    table(["Commande", "Effet"], [
        ["make seed", "Donnees de demo + entrainement"],
        ["make api", "Demarre l'API FastAPI (8000)"],
        ["make dashboard", "Demarre le dashboard Streamlit (8501)"],
        ["make frontend", "Demarre le frontend React (5173)"],
        ["make train", "Entraine les 3 modeles + risque"],
        ["make test", "Lance la suite de tests"],
        ["make export-demo", "GeoTIFF de test dans data/raw/"],
        ["python -m scripts.gee_export --drive", "Export reel Sentinel-2 vers Drive"],
        ["make check-data", "Verifie les vraies donnees"],
        ["make demo / make real", "Bascule .env demo/reel"],
        ["make mode", "Affiche le mode courant"],
        ["make memoir / make slides", "Genere memoire / soutenance"],
        ["make docker", "Build + run via docker-compose"],
    ])
    hr()
    p("Genere automatiquement par scripts/generate_guide.py — DeforestWatch-DRC, 2026.")
    return B


# ──────────────────────────────────────────────────────────────────────────
# Rendu Markdown
# ──────────────────────────────────────────────────────────────────────────
def to_markdown(blocks) -> str:
    out: list[str] = []
    for kind, c in blocks:
        if kind == "h1":
            out.append(f"# {c}\n")
        elif kind == "h2":
            out.append(f"\n## {c}\n")
        elif kind == "h3":
            out.append(f"\n### {c}\n")
        elif kind == "p":
            out.append(f"{c}\n")
        elif kind == "ul":
            out.extend(f"- {i}" for i in c)
            out.append("")
        elif kind == "code":
            out.append("```bash")
            out.append(c)
            out.append("```")
        elif kind == "table":
            headers, rows = c
            out.append("| " + " | ".join(headers) + " |")
            out.append("| " + " | ".join("---" for _ in headers) + " |")
            out.extend("| " + " | ".join(str(x) for x in r) + " |" for r in rows)
            out.append("")
        elif kind == "hr":
            out.append("\n---\n")
    return "\n".join(out) + "\n"


# ──────────────────────────────────────────────────────────────────────────
# Rendu PDF (fpdf2)
# ──────────────────────────────────────────────────────────────────────────
def _latin1(text: str) -> str:
    """Rend le texte compatible avec les polices coeur (latin-1)."""
    return text.encode("latin-1", "replace").decode("latin-1")


def to_pdf(blocks, path: Path) -> None:
    from fpdf import FPDF
    from fpdf.fonts import FontFace as FontStyle

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_text_color(20, 20, 20)
    W = pdf.epw  # largeur utile

    def mc(text, h, fill=False):
        """multi_cell qui revient toujours a la marge gauche (largeur garantie)."""
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, h, text, fill=fill, new_x="LMARGIN", new_y="NEXT")

    for kind, c in blocks:
        pdf.set_x(pdf.l_margin)  # garantit la largeur dispo (ex. apres un tableau)
        if kind == "h1":
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(11, 110, 45)
            mc(_latin1(c), 9)
            pdf.set_text_color(20, 20, 20)
            pdf.ln(2)
        elif kind == "h2":
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(11, 110, 45)
            mc(_latin1(c), 8)
            pdf.set_text_color(20, 20, 20)
            pdf.ln(1)
        elif kind == "h3":
            pdf.set_font("Helvetica", "B", 11.5)
            mc(_latin1(c), 7)
        elif kind == "p":
            pdf.set_font("Helvetica", "", 10.5)
            mc(_latin1(c), 5.5)
            pdf.ln(1)
        elif kind == "ul":
            pdf.set_font("Helvetica", "", 10.5)
            for item in c:
                mc(_latin1("  -  " + item), 5.5)
            pdf.ln(1)
        elif kind == "code":
            pdf.set_font("Courier", "", 9)
            pdf.set_fill_color(238, 242, 246)
            for line in c.split("\n"):
                mc(_latin1(line) or " ", 5, fill=True)
            pdf.ln(1)
        elif kind == "table":
            headers, rows = c
            pdf.set_font("Helvetica", "", 9)
            pdf.set_draw_color(210, 210, 210)
            with pdf.table(
                width=W,
                text_align="LEFT",
                headings_style=FontStyle(color=255, fill_color=(16, 185, 129), emphasis="BOLD"),
                cell_fill_color=(244, 247, 250),
                cell_fill_mode="ROWS",
            ) as table:
                hr_ = table.row()
                for h in headers:
                    hr_.cell(_latin1(str(h)))
                for row in rows:
                    tr = table.row()
                    for x in row:
                        tr.cell(_latin1(str(x)))
            pdf.ln(2)
        elif kind == "hr":
            pdf.ln(1)
            pdf.set_draw_color(200, 200, 200)
            y = pdf.get_y()
            pdf.line(pdf.l_margin, y, pdf.l_margin + W, y)
            pdf.ln(3)

    pdf.output(str(path))


def main() -> None:
    blocks = document()
    md_path = PROJECT_ROOT / "GUIDE.md"
    md_path.write_text(to_markdown(blocks), encoding="utf-8")
    log.info(f"Guide Markdown -> {md_path}")

    pdf_path = PROJECT_ROOT / "docs" / "GUIDE.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        to_pdf(blocks, pdf_path)
        log.info(f"Guide PDF -> {pdf_path}")
    except Exception as exc:  # pragma: no cover - depend de fpdf2
        log.warning(f"PDF non genere ({exc}). Installez fpdf2 : pip install fpdf2. "
                    "Le GUIDE.md reste disponible.")


if __name__ == "__main__":
    main()
