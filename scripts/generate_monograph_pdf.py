"""
Génère la monographie DeforestWatch-DRC au format PDF, dans une mise en page
académique classique (police serif type Times, texte noir justifié avec alinéas,
chapitres centrés en majuscules, table des matières paginée à points de
conduite, conclusions partielles) conforme aux usages des monographies de
l'Université Protestante au Congo.

La structure suit le « Guide de Rédaction des Monographies des Projets et des
Mémoires » de la Faculté des Sciences Informatiques (janvier 2025) ; le contenu
est identique sur le fond à la version Word (scripts/generate_monograph.py),
rédigé ici en prose continue.

Usage  : python -m scripts.generate_monograph_pdf
Sortie : docs/monographie_deforestwatch.pdf
Dépendances : fpdf2, numpy (polices Liberation Serif du système).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from fpdf import FPDF

# ── Constantes du projet (miroir de config.settings) ──────────────────────
AUTHOR = "Joyce A. WETUNGANI"
YEAR = 2026
ANALYSIS_START_YEAR = 2015
ANALYSIS_END_YEAR = 2025
ANALYSIS_YEARS = list(range(ANALYSIS_START_YEAR, ANALYSIS_END_YEAR + 1))
GRID_SIZE = 256
PIXEL_AREA_HA = (50_000 / GRID_SIZE) ** 2 / 10_000
AGB_TONNES_PER_HA = 310.0
CARBON_FRACTION = 0.47
CO2_TONNES_PER_HA = AGB_TONNES_PER_HA * CARBON_FRACTION * (44.0 / 12.0)

FONT_DIR = Path("/usr/share/fonts/truetype/liberation")

MARGIN = 25          # marges généreuses, usage académique
LINE = 6.5           # interligne ~1,5 pour du 12 pt
INDENT = "        "  # alinéa en début de paragraphe


def fr(n: float, dec: int = 0) -> str:
    """Format nombre à la française : 224 945 / 5,12."""
    s = f"{n:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s


# ── Statistiques (recalcul identique à src/utils/synthetic.py) ─────────────
def yearly_statistics() -> list[dict]:
    rng = np.random.default_rng(42)
    yy, xx = np.mgrid[0:GRID_SIZE, 0:GRID_SIZE]
    river = np.abs(yy - (GRID_SIZE * 0.6 + 18 * np.sin(xx / 30.0))) < 3
    town = ((xx - int(GRID_SIZE * 0.30)) ** 2
            + (yy - int(GRID_SIZE * 0.62)) ** 2) < (GRID_SIZE * 0.04) ** 2
    sources = [(int(GRID_SIZE * 0.30), int(GRID_SIZE * 0.62)),
               (int(GRID_SIZE * 0.70), int(GRID_SIZE * 0.35)),
               (int(GRID_SIZE * 0.50), int(GRID_SIZE * 0.80))]
    road = np.abs(xx - yy) < 4
    dist = np.full((GRID_SIZE, GRID_SIZE), np.inf)
    for sx, sy in sources:
        dist = np.minimum(dist, np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2))
    dist = np.minimum(dist, np.where(road, 5.0, np.inf))
    dist_norm = dist / dist.max()

    stats, prev = [], None
    for i, year in enumerate(ANALYSIS_YEARS):
        progress = i / (len(ANALYSIS_YEARS) - 1)
        lc = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int8)
        threshold = 0.10 + 0.45 * progress
        noise = rng.normal(0, 0.05, (GRID_SIZE, GRID_SIZE))
        deforested = (dist_norm + noise) < threshold
        degraded = (dist_norm + noise < threshold + 0.08) & ~deforested
        lc[degraded] = 1
        lc[deforested] = 2
        lc[river] = 3
        lc[town] = 4
        forest_ha = round(int(np.sum((lc == 0) | (lc == 1))) * PIXEL_AREA_HA, 1)
        loss = round(prev - forest_ha, 1) if prev is not None else 0.0
        rate = round(100 * loss / prev, 2) if prev else 0.0
        stats.append({"year": year, "forest": forest_ha,
                      "loss": max(loss, 0.0), "rate": max(rate, 0.0)})
        prev = forest_ha
    return stats


MODEL_METRICS = [
    ["Random Forest", "0,89", "0,87", "0,86", "0,86", "0,94", "0,78"],
    ["XGBoost", "0,90", "0,88", "0,88", "0,88", "0,95", "0,80"],
    ["U-Net (CNN)", "0,91", "0,90", "0,89", "0,89", "0,96", "0,82"],
]


# ── Document ───────────────────────────────────────────────────────────────
class Monographie(FPDF):
    def footer(self):
        if self.page_no() == 1:      # page de titre non paginée
            return
        self.set_y(-18)
        self.set_font("Serif", "", 10)
        self.cell(0, 8, str(self.page_no()), align="C")


def make_pdf() -> FPDF:
    pdf = Monographie(format="A4")
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.set_auto_page_break(auto=True, margin=MARGIN)
    pdf.add_font("Serif", "", FONT_DIR / "LiberationSerif-Regular.ttf")
    pdf.add_font("Serif", "B", FONT_DIR / "LiberationSerif-Bold.ttf")
    pdf.add_font("Serif", "I", FONT_DIR / "LiberationSerif-Italic.ttf")
    pdf.add_font("Serif", "BI", FONT_DIR / "LiberationSerif-BoldItalic.ttf")
    pdf.set_text_color(0, 0, 0)
    pdf.set_title("Monographie - DeforestWatch-DRC")
    pdf.set_author(AUTHOR)
    pdf.set_subject("Surveillance et prédiction de la déforestation du "
                    "Bassin du Congo par imagerie satellite et Machine Learning")
    return pdf


# ── Primitives de mise en page ─────────────────────────────────────────────
def body(pdf, text, size=12, style="", align="J", indent=True, spacing=2):
    pdf.set_font("Serif", style, size)
    txt = (INDENT + text) if indent else text
    pdf.multi_cell(0, LINE, txt, align=align, new_x="LMARGIN", new_y="NEXT")
    if spacing:
        pdf.ln(spacing)


def item(pdf, text, bullet="–", size=12):
    """Élément de liste avec retrait suspendu."""
    pdf.set_font("Serif", "", size)
    x0 = pdf.l_margin + 6
    pdf.set_x(x0)
    pdf.multi_cell(pdf.epw - 6, LINE, f"{bullet}  {text}",
                   align="J", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def heading_front(pdf, title, toc=True, new_page=True):
    """Titre de partie liminaire (résumé, sigles...) : centré, majuscules."""
    if new_page:
        pdf.add_page()
    if toc:
        pdf.start_section(title.upper(), level=0)
    pdf.set_font("Serif", "B", 14)
    pdf.cell(0, 8, title.upper(), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)


def chapitre(pdf, numero, titre):
    pdf.add_page()
    pdf.start_section(f"CHAPITRE {numero} : {titre.upper()}", level=0)
    pdf.ln(10)
    pdf.set_font("Serif", "B", 14)
    pdf.cell(0, 8, f"CHAPITRE {numero}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.cell(0, 8, titre.upper(), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)


def section(pdf, num, titre):
    if pdf.get_y() > pdf.h - pdf.b_margin - 40:
        pdf.add_page()
    pdf.start_section(f"{num}. {titre}", level=1)
    pdf.ln(2)
    pdf.set_font("Serif", "B", 12)
    pdf.multi_cell(0, LINE, f"{num}. {titre}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def sous_section(pdf, num, titre):
    if pdf.get_y() > pdf.h - pdf.b_margin - 30:
        pdf.add_page()
    pdf.set_font("Serif", "BI", 12)
    pdf.multi_cell(0, LINE, f"{num}. {titre}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def tableau(pdf, caption, headers, rows, widths=None, size=10.5):
    pdf.ln(2)
    pdf.set_font("Serif", "I", 10.5)
    pdf.multi_cell(0, 5.5, caption, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)
    pdf.set_font("Serif", "", size)
    pdf.set_line_width(0.2)
    pdf.set_draw_color(0, 0, 0)
    with pdf.table(col_widths=widths, text_align="LEFT",
                   line_height=5.6, padding=1.4) as t:
        hr = t.row()
        pdf.set_font("Serif", "B", size)
        for h in headers:
            hr.cell(h)
        pdf.set_font("Serif", "", size)
        for row in rows:
            r = t.row()
            for v in row:
                r.cell(str(v))
    pdf.ln(4)


def render_toc(pdf, outline):
    pdf.set_font("Serif", "B", 14)
    pdf.cell(0, 8, "TABLE DES MATIÈRES", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    for entry in outline:
        if entry.level > 1:
            continue
        label = entry.name
        page = str(entry.page_number)
        indent_mm = 6 * entry.level
        style = "B" if entry.level == 0 else ""
        pdf.set_font("Serif", style, 11)
        avail = pdf.epw - indent_mm - pdf.get_string_width(page) - 3
        # tronque si nécessaire puis points de conduite
        while pdf.get_string_width(label) > avail - 8:
            label = label[:-1]
        dots = ""
        while pdf.get_string_width(label + dots) < avail:
            dots += "."
        pdf.set_x(pdf.l_margin + indent_mm)
        pdf.cell(pdf.epw - indent_mm - pdf.get_string_width(page) - 1, 6.5,
                 label + " " + dots)
        pdf.cell(0, 6.5, page, align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.8)


# ══════════════════════════════════════════════════════════════════════════
def build() -> FPDF:
    pdf = make_pdf()
    stats = yearly_statistics()
    f0, f1 = stats[0]["forest"], stats[-1]["forest"]
    total_loss = f0 - f1
    co2_mt = total_loss * CO2_TONNES_PER_HA / 1e6

    # ── Page de titre ──────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_line_width(0.4)
    pdf.rect(12, 12, pdf.w - 24, pdf.h - 24)
    pdf.set_y(28)
    pdf.set_font("Serif", "B", 14)
    pdf.cell(0, 7, "UNIVERSITÉ PROTESTANTE AU CONGO", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Serif", "", 12)
    pdf.cell(0, 7, "Faculté des Sciences Informatiques", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Licence (L3 LMD) – Orientation : Data Science",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font("Serif", "B", 20)
    pdf.multi_cell(0, 10, "DEFORESTWATCH-DRC", align="C",
                   new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Serif", "B", 13)
    pdf.multi_cell(0, 7.5,
                   "Surveillance et prédiction de la déforestation de la forêt "
                   "équatoriale du Bassin du Congo par imagerie satellite et "
                   "Machine Learning",
                   align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Serif", "I", 12)
    pdf.multi_cell(0, 7, "Étude de cas : province du Mai-Ndombe (Inongo), "
                         "République Démocratique du Congo",
                   align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(18)
    pdf.set_font("Serif", "", 12)
    pdf.multi_cell(0, 7, "Monographie présentée et défendue en vue de "
                         "l'obtention du grade de Licencié\n"
                         "en Sciences Informatiques",
                   align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(14)
    pdf.set_font("Serif", "", 12)
    pdf.cell(0, 7, f"Par : {AUTHOR}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Directeur : ………………………………………………", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Encadreur : ………………………………………………", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(-45)
    pdf.set_font("Serif", "B", 12)
    pdf.cell(0, 7, f"Année académique {YEAR - 1}–{YEAR}", align="C",
             new_x="LMARGIN", new_y="NEXT")

    # ── Épigraphe / Remerciements ─────────────────────────────────────
    heading_front(pdf, "Remerciements")
    body(pdf, "Au terme de ce travail de fin de cycle, nous tenons à exprimer "
              "notre profonde gratitude à Dieu Tout-Puissant pour le souffle de "
              "vie, la santé et l'intelligence qu'il nous a accordés tout au "
              "long de notre formation.")
    body(pdf, "Nos remerciements s'adressent aux autorités académiques de "
              "l'Université Protestante au Congo, en particulier au corps "
              "professoral de la Faculté des Sciences Informatiques, pour la "
              "qualité de l'encadrement dont nous avons bénéficié durant notre "
              "parcours de licence.")
    body(pdf, "Nous exprimons notre reconnaissance à notre directeur "
              "……………………………… et à notre encadreur ………………………………, dont les "
              "orientations, les remarques et la disponibilité ont permis à ce "
              "travail d'aboutir.")
    body(pdf, "Enfin, nous remercions notre famille et nos camarades de "
              "promotion pour leur soutien constant. Que tous ceux qui, de près "
              "ou de loin, ont contribué à la réalisation de ce travail "
              "trouvent ici l'expression de notre gratitude.")

    # ── Résumé ────────────────────────────────────────────────────────
    heading_front(pdf, "Résumé")
    body(pdf, "La République Démocratique du Congo abrite la deuxième plus "
              "grande forêt tropicale humide du monde, au cœur du Bassin du "
              "Congo. Cet écosystème équatorial subit une déforestation "
              "accélérée, essentiellement diffuse (agriculture sur brûlis, "
              "charbon de bois, exploitation artisanale), que les plateformes "
              "mondiales de suivi captent mal. Le présent travail conçoit et "
              "réalise DeforestWatch-DRC, une plateforme d'analyse et de "
              "prédiction de la déforestation appliquée à la province du "
              "Mai-Ndombe.")
    body(pdf, "L'objectif poursuivi est de détecter, de quantifier et "
              "d'anticiper la perte forestière à partir de l'imagerie "
              "satellite Sentinel-2 et de techniques d'apprentissage "
              "automatique. La démarche suit le cycle de vie d'un projet de "
              "science des données : acquisition des images par Google Earth "
              "Engine, prétraitement (masquage des nuages, calcul des indices "
              "spectraux NDVI, EVI, NDWI et NBR, composites de saison sèche), "
              "modélisation supervisée comparant trois modèles (Random Forest, "
              "XGBoost et U-Net), évaluation par validation croisée spatiale, "
              "puis déploiement sous forme d'une API et de tableaux de bord "
              "interactifs.")
    body(pdf, "Sur le jeu de données de démonstration, qui valide la chaîne de "
              "traitement de bout en bout, les trois modèles atteignent une "
              "exactitude comprise entre 0,89 et 0,91 ; un modèle "
              "complémentaire prédit les fronts de déforestation à venir avec "
              "une aire sous la courbe ROC de 0,83. La perte forestière "
              f"simulée sur la période {ANALYSIS_START_YEAR}–"
              f"{ANALYSIS_END_YEAR} est en outre traduite en émissions de CO2, "
              "afin de relier le résultat technique au langage de la finance "
              "climat (REDD+). Ces résultats, à confirmer sur images réelles, "
              "montrent qu'un outil complet, prédictif et maîtrisé localement "
              "peut être construit pour appuyer la surveillance de la forêt "
              "congolaise.")
    pdf.ln(2)
    body(pdf, "Mots-clés : déforestation, télédétection, Sentinel-2, "
              "apprentissage automatique, Random Forest, XGBoost, U-Net, NDVI, "
              "REDD+, Bassin du Congo, Mai-Ndombe.", style="I", indent=False)

    # ── Sigles ────────────────────────────────────────────────────────
    heading_front(pdf, "Sigles et abréviations")
    tableau(pdf, "", ["Sigle", "Signification"], [
        ["AGB", "Above-Ground Biomass (biomasse aérienne)"],
        ["API", "Application Programming Interface"],
        ["AUC", "Area Under the ROC Curve"],
        ["CAFI", "Central African Forest Initiative"],
        ["CNN", "Convolutional Neural Network"],
        ["EVI", "Enhanced Vegetation Index"],
        ["GEE", "Google Earth Engine"],
        ["GFC", "Global Forest Change (Hansen)"],
        ["ICCN", "Institut Congolais pour la Conservation de la Nature"],
        ["IoU", "Intersection over Union"],
        ["JWT", "JSON Web Token"],
        ["MRV", "Measurement, Reporting and Verification"],
        ["NBR", "Normalized Burn Ratio"],
        ["NDVI", "Normalized Difference Vegetation Index"],
        ["NDWI", "Normalized Difference Water Index"],
        ["NIR", "Near Infrared (proche infrarouge)"],
        ["RDC", "République Démocratique du Congo"],
        ["REDD+", "Réduction des Émissions dues à la Déforestation et à la "
                  "Dégradation des forêts"],
        ["RF", "Random Forest"],
        ["SCL", "Scene Classification Layer (Sentinel-2)"],
        ["SRTM", "Shuttle Radar Topography Mission"],
        ["SWIR", "Short-Wave Infrared"],
        ["2FA", "Authentification à deux facteurs"],
    ], widths=(22, 78), size=11)

    # ── Liste des tableaux ────────────────────────────────────────────
    heading_front(pdf, "Liste des tableaux")
    for t in [
        "Tableau 1 – Sources de données utilisées.",
        "Tableau 2 – Bandes spectrales Sentinel-2 et indices dérivés.",
        "Tableau 3 – Classes de couverture du sol.",
        "Tableau 4 – Dynamique annuelle de la couverture forestière "
        "(2015–2025).",
        "Tableau 5 – Comparaison des performances des modèles.",
        "Tableau 6 – Traduction de la perte forestière en émissions de CO2.",
    ]:
        item(pdf, t)

    # ── Table des matières (placeholder, rendue en fin de génération) ──
    pdf.add_page()
    pdf.insert_toc_placeholder(render_toc, pages=1, allow_extra_pages=True)

    # ── Introduction générale (la page vient du placeholder de la TdM) ──
    heading_front(pdf, "Introduction générale", new_page=False)
    body(pdf, "La surveillance des forêts tropicales est devenue, au cours des "
              "deux dernières décennies, un enjeu scientifique, environnemental "
              "et géopolitique de premier plan. Le Bassin du Congo, dont la "
              "République Démocratique du Congo constitue le cœur, forme le "
              "deuxième massif forestier tropical de la planète après "
              "l'Amazonie. Il joue un rôle déterminant dans la régulation du "
              "climat mondial, le stockage du carbone et la préservation de la "
              "biodiversité. Ce patrimoine s'érode pourtant d'année en année "
              "sous l'effet de dynamiques locales bien identifiées : "
              "agriculture itinérante sur brûlis, production de charbon de "
              "bois, exploitation forestière artisanale et expansion des "
              "villages.")
    body(pdf, "Face à ce constat, les outils mondiaux de suivi du couvert "
              "forestier, aussi précieux soient-ils, montrent leurs limites "
              "dans le contexte congolais : conçus à l'échelle globale, ils "
              "peinent à capter les petites coupes diffuses qui caractérisent "
              "la déforestation en RDC et n'offrent guère de capacité "
              "d'anticipation. C'est ce qui a motivé le présent travail de fin "
              "de cycle, consacré à la conception et à la réalisation d'une "
              "plateforme de surveillance et de prédiction de la déforestation "
              "adaptée à une zone congolaise : DeforestWatch-DRC, appliquée à "
              "la province du Mai-Ndombe.")
    body(pdf, "Notre ambition est double. Sur le plan technique, il s'agit de "
              "démontrer qu'une chaîne complète de science des données, de la "
              "collecte des images satellites jusqu'au déploiement d'un outil "
              "d'aide à la décision, peut être construite, testée et maîtrisée "
              "avec des moyens accessibles. Sur le plan de l'impact, il s'agit "
              "de montrer en quoi un tel outil, prédictif plutôt que seulement "
              "rétrospectif et pensé pour le contexte local, apporte une "
              "plus-value réelle aux acteurs de la conservation forestière.")
    body(pdf, "Conformément au guide de rédaction de la Faculté des Sciences "
              "Informatiques, ce travail s'articule autour de trois chapitres. "
              "Le premier chapitre situe le sujet dans son contexte et passe en "
              "revue la littérature théorique et empirique ; il y formule la "
              "problématique, les objectifs et les hypothèses de recherche. Le "
              "deuxième chapitre expose la modélisation et les méthodes de "
              "travail : données, prétraitement, modèles retenus et protocole "
              "d'évaluation, ainsi que la réalisation logicielle. Le troisième "
              "chapitre présente les résultats obtenus, les discute au regard "
              "des hypothèses et de la littérature, puis conclut en dégageant "
              "les limites de l'étude et les perspectives de recherche.")

    # ══════════════════════════════════════════════════════════════════
    #  CHAPITRE I
    # ══════════════════════════════════════════════════════════════════
    chapitre(pdf, "I", "Mise en contexte et revue de la littérature")

    section(pdf, "I.1", "Introduction et mise en contexte")
    sous_section(pdf, "I.1.1", "Présentation du domaine et du sujet")
    body(pdf, "Notre sujet se situe à l'intersection de trois domaines : la "
              "télédétection, c'est-à-dire l'observation de la Terre par "
              "satellite, la science des données et les sciences de "
              "l'environnement. Il porte sur la détection et la prédiction de "
              "la déforestation dans la forêt tropicale humide équatoriale du "
              "Bassin du Congo, plus précisément dans la province du "
              "Mai-Ndombe. La télédétection optique, popularisée par les "
              "programmes Landsat de la NASA puis Copernicus/Sentinel de "
              "l'Agence spatiale européenne, met aujourd'hui à disposition des "
              "images multispectrales gratuites et régulières qui permettent "
              "de cartographier le couvert végétal à grande échelle. Couplée à "
              "l'apprentissage automatique, elle ouvre la voie à des systèmes "
              "de surveillance à la fois fins et automatisés.")
    body(pdf, "L'état de l'art opérationnel est dominé par de grandes "
              "plateformes de suivi forestier : Global Forest Watch, le Global "
              "Forest Change issu des travaux de Hansen et ses collaborateurs, "
              "ou encore les alertes RADD fondées sur l'imagerie radar. Ces "
              "plateformes ont démocratisé l'accès à l'information sur la "
              "perte de forêt. Elles restent toutefois pensées à l'échelle "
              "mondiale et sont d'abord rétrospectives : elles documentent ce "
              "qui a déjà eu lieu, sans nécessairement anticiper les zones "
              "menacées ni s'adapter aux moteurs de déforestation propres à "
              "chaque territoire.")
    sous_section(pdf, "I.1.2", "Justification du choix du sujet")
    body(pdf, "Le choix de ce sujet se justifie d'abord par sa pertinence "
              "académique : il mobilise l'ensemble des compétences attendues "
              "d'un data scientist, de l'acquisition et du nettoyage de "
              "données spatiales volumineuses jusqu'au déploiement d'une "
              "application, en passant par l'ingénierie de variables et la "
              "comparaison rigoureuse de modèles. Il se justifie ensuite par "
              "son intérêt pratique pour le pays. La RDC abrite environ 60 % "
              "de la forêt du Bassin du Congo et figure parmi les premiers "
              "pays au monde pour la perte de forêt primaire. Contrairement à "
              "d'autres régions où la déforestation est industrielle, elle y "
              "est essentiellement diffuse : agriculture de subsistance sur "
              "brûlis, production de charbon de bois, dit makala, et "
              "exploitation artisanale. Ces petites coupes dispersées sont "
              "précisément celles que les outils mondiaux détectent le moins "
              "bien ; une approche locale, fine et prédictive s'impose donc.")
    body(pdf, "Le choix du Mai-Ndombe ajoute enfin une dimension économique : "
              "cette province est pilote pour le mécanisme international "
              "REDD+, qui lie la RDC à des bailleurs de fonds par des accords "
              "de paiements aux résultats. Y réduire la déforestation, et "
              "surtout pouvoir le prouver par des données vérifiables, revêt "
              "une valeur financière directe pour le pays.")

    section(pdf, "I.2", "Problématique, objectifs et hypothèses")
    sous_section(pdf, "I.2.1", "Problématique")
    body(pdf, "La question centrale de ce travail peut être formulée comme "
              "suit : comment exploiter l'imagerie satellite et "
              "l'apprentissage automatique pour détecter, quantifier et "
              "anticiper la déforestation de la forêt équatoriale du "
              "Mai-Ndombe, d'une manière adaptée au contexte congolais ? "
              "Cette question se décline en trois interrogations plus "
              "précises. Premièrement, quels indices spectraux et quels "
              "modèles permettent de discriminer de façon fiable les classes "
              "de couverture du sol à partir des images Sentinel-2 ? "
              "Deuxièmement, entre les familles de modèles disponibles, "
              "ensembles d'arbres de décision d'une part et réseaux de "
              "neurones profonds d'autre part, laquelle offre le meilleur "
              "compromis entre performance, interprétabilité et coût de "
              "calcul ? Troisièmement, la déforestation future est-elle "
              "spatialement prédictible à partir de variables de proximité "
              "telles que la distance aux routes, aux villages et aux fronts "
              "de coupe existants ?")
    sous_section(pdf, "I.2.2", "Objectifs de la recherche")
    body(pdf, "L'objectif général est de concevoir et de réaliser une "
              "plateforme opérationnelle de surveillance et de prédiction de "
              "la déforestation. De cet objectif général découlent six "
              "objectifs spécifiques :")
    for i, obj in enumerate([
        "détecter les zones déforestées par classification supervisée "
        "d'images Sentinel-2 en cinq classes de couverture du sol ;",
        f"quantifier la perte forestière année par année sur la période "
        f"{ANALYSIS_START_YEAR}–{ANALYSIS_END_YEAR} ;",
        "comparer trois modèles d'apprentissage (Random Forest, XGBoost et "
        "U-Net) selon des métriques standard et retenir le plus adapté ;",
        "prédire les zones à risque de déforestation future sous la forme "
        "d'une carte de risque ;",
        "traduire la perte forestière en émissions de CO2, en lien avec le "
        "mécanisme REDD+ ;",
        "livrer une plateforme d'aide à la décision comprenant une API, des "
        "tableaux de bord et un dispositif de signalement citoyen.",
    ], start=1):
        item(pdf, obj, bullet=f"{i}.")
    sous_section(pdf, "I.2.3", "Hypothèses de recherche")
    body(pdf, "Trois hypothèses testables structurent le travail. La première "
              "(H1) avance que les indices spectraux dérivés de Sentinel-2 "
              "(NDVI, EVI, NDWI et NBR), combinés aux bandes brutes et aux "
              "variables topographiques, permettent de discriminer les classes "
              "de couverture forestière avec une exactitude au moins égale à "
              "0,80. La deuxième (H2) suppose qu'un modèle d'ensemble de type "
              "Random Forest ou XGBoost, appliqué pixel par pixel, offre un "
              "compromis performance/interprétabilité au moins aussi favorable "
              "qu'un réseau convolutif de segmentation tel que U-Net sur notre "
              "zone d'étude. La troisième (H3) pose que la déforestation "
              "future est spatialement prédictible : un modèle de risque fondé "
              "sur des variables de proximité doit atteindre une aire sous la "
              "courbe ROC au moins égale à 0,75.")

    section(pdf, "I.3", "Revue de la littérature théorique")
    sous_section(pdf, "I.3.1", "Télédétection et indices de végétation")
    body(pdf, "La caractérisation de la végétation par satellite repose sur la "
              "réponse spectrale des surfaces observées. La végétation "
              "chlorophyllienne absorbe fortement la lumière rouge et "
              "réfléchit fortement le proche infrarouge : ce contraste fonde "
              "l'indice de végétation par différence normalisée, ou NDVI, "
              "introduit par Tucker (1979) et défini comme le rapport "
              "(NIR − Rouge) / (NIR + Rouge). D'autres indices complètent "
              "cette mesure : l'EVI corrige l'influence du sol et de "
              "l'atmosphère ; le NDWI est sensible à l'eau et à l'humidité de "
              "la végétation ; le NBR, calculé à partir de l'infrarouge à "
              "ondes courtes, met en évidence les surfaces brûlées, ce qui est "
              "précieux dans un contexte d'agriculture sur brûlis. Ces indices "
              "constituent des variables explicatives robustes pour distinguer "
              "la forêt dense, la forêt dégradée et le sol nu.")
    sous_section(pdf, "I.3.2", "Apprentissage automatique et classification d'images")
    body(pdf, "Deux grandes familles de modèles sont mobilisées dans la "
              "littérature. Les approches dites « pixel » traitent chaque "
              "pixel comme un vecteur de variables indépendant de ses voisins. "
              "Parmi elles, les forêts aléatoires (Breiman, 2001) agrègent de "
              "nombreux arbres de décision entraînés sur des échantillons et "
              "des sous-ensembles de variables tirés au hasard ; la "
              "décorrélation des arbres réduit la variance du modèle, et la "
              "mesure d'importance des variables qui en découle facilite "
              "l'interprétation. Le gradient boosting, dont XGBoost (Chen et "
              "Guestrin, 2016) est l'implémentation la plus répandue, "
              "construit au contraire les arbres séquentiellement, chacun "
              "corrigeant les erreurs résiduelles des précédents ; il atteint "
              "fréquemment l'état de l'art sur données tabulaires. Les "
              "approches profondes, quant à elles, exploitent le contexte "
              "spatial : les réseaux de neurones convolutifs apprennent des "
              "motifs de texture et de forme que les modèles pixel ignorent.")
    sous_section(pdf, "I.3.3", "Segmentation sémantique et architecture U-Net")
    body(pdf, "Pour cartographier l'occupation du sol à la résolution du pixel "
              "tout en tenant compte du voisinage, l'outil de référence est la "
              "segmentation sémantique. L'architecture U-Net, proposée par "
              "Ronneberger, Fischer et Brox (2015) pour l'imagerie "
              "biomédicale, s'est imposée en télédétection. Il s'agit d'un "
              "encodeur-décodeur symétrique muni de connexions de saut : "
              "l'encodeur extrait des caractéristiques à des échelles de plus "
              "en plus grossières, tandis que le décodeur reconstruit une "
              "carte de classes de la taille de l'image d'entrée, les "
              "connexions de saut réinjectant l'information de localisation "
              "fine perdue lors de la contraction.")
    sous_section(pdf, "I.3.4", "Lacunes identifiées")
    body(pdf, "Trois lacunes ressortent de cette revue et justifient notre "
              "travail. En premier lieu, la plupart des systèmes opérationnels "
              "sont rétrospectifs et n'intègrent pas de dimension prédictive à "
              "l'échelle locale. En deuxième lieu, rares sont les outils "
              "calibrés sur les moteurs spécifiques de la déforestation "
              "congolaise, proposés en français et conçus pour être appropriés "
              "localement. En dernier lieu, la traduction directe de la perte "
              "forestière en indicateurs de la finance climat, tels que les "
              "émissions de CO2 et les crédits carbone, reste rare dans les "
              "prototypes académiques, alors qu'elle conditionne l'usage réel "
              "d'un tel outil dans une province pilote REDD+.")

    section(pdf, "I.4", "Revue de la littérature empirique")
    body(pdf, "Sur le plan empirique, les travaux de Hansen et ses "
              "collaborateurs (2013) ont produit les premières cartes "
              "mondiales à haute résolution du changement de couvert forestier "
              "à partir des archives Landsat, à 30 mètres de résolution ; "
              "elles demeurent une référence de vérité terrain largement "
              "utilisée. Le lancement de Sentinel-2 (Drusch et al., 2012) a "
              "ensuite apporté une résolution de 10 mètres et une revisite de "
              "cinq jours, améliorant sensiblement les capacités de suivi. "
              "Enfin, la plateforme Google Earth Engine (Gorelick et al., "
              "2017) a rendu ces analyses accessibles à l'échelle planétaire "
              "sans infrastructure de calcul locale. De nombreuses études "
              "appliquées, dans divers biomes, ont confirmé la supériorité "
              "fréquente des méthodes d'ensemble et des réseaux convolutifs "
              "sur les classifieurs classiques pour la cartographie "
              "forestière.")
    body(pdf, "Ces travaux appellent toutefois une lecture critique. Ils "
              "restent souvent génériques ou centrés sur d'autres régions, "
              "notamment l'Amazonie et les forêts boréales, dont les moteurs "
              "de déforestation diffèrent de ceux du Bassin du Congo. Surtout, "
              "peu d'études combinent, sur une même zone congolaise, la "
              "classification du couvert, la prédiction du risque et la "
              "valorisation carbone au sein d'un outil déployé et documenté. "
              "C'est précisément le positionnement de DeforestWatch-DRC : "
              "notre contribution se veut moins une innovation algorithmique "
              "qu'une intégration cohérente et contextualisée de méthodes "
              "éprouvées, au service d'un besoin local clairement identifié.")
    section(pdf, "I.5", "Conclusion partielle")
    body(pdf, "Ce premier chapitre a situé le sujet dans son double contexte "
              "scientifique et national, formulé la problématique et les trois "
              "hypothèses de recherche, puis établi, par la revue de la "
              "littérature, à la fois la solidité des méthodes disponibles et "
              "l'existence d'un espace de contribution : un outil local, "
              "prédictif et orienté vers l'action. Le chapitre suivant expose "
              "la démarche méthodologique adoptée pour construire cet outil.")

    # ══════════════════════════════════════════════════════════════════
    #  CHAPITRE II
    # ══════════════════════════════════════════════════════════════════
    chapitre(pdf, "II", "Modélisation et méthodes de travail")

    section(pdf, "II.1", "Démarche méthodologique")
    body(pdf, "Notre démarche suit le cycle de vie structuré d'un projet de "
              "science des données, inspiré du processus CRISP-DM. Elle "
              "enchaîne sept étapes : la compréhension du problème, au cours "
              "de laquelle les objectifs et les classes à cartographier ont "
              "été définis ; l'acquisition des données, réalisée au moyen de "
              "la plateforme Google Earth Engine ; l'exploration, consacrée à "
              "l'analyse des distributions spectrales et des corrélations "
              "entre indices ; la préparation des données ; la modélisation "
              "proprement dite ; l'évaluation comparative des modèles ; et "
              "enfin le déploiement sous forme d'une API et de tableaux de "
              "bord. Cette progression, itérative par nature, garantit la "
              "reproductibilité de l'analyse.")

    section(pdf, "II.2", "Zone d'étude")
    body(pdf, "La zone d'étude couvre un carré d'environ 50 kilomètres de "
              "côté, soit près de 250 000 hectares, autour de la ville "
              "d'Inongo, chef-lieu de la province du Mai-Ndombe (1,95° de "
              "latitude sud et 18,27° de longitude est). Il s'agit de l'un des "
              "fronts de déforestation les plus actifs de la forêt équatoriale "
              "congolaise : la pression y provient de l'agriculture itinérante "
              "et des concessions forestières, et les coupes progressent "
              "typiquement depuis les villages et le long des axes de "
              "circulation.")

    section(pdf, "II.3", "Données et instruments de collecte")
    body(pdf, "Cinq sources de données alimentent la plateforme. Les images "
              "multispectrales Sentinel-2 constituent la source principale ; "
              "elles sont complétées par les images Landsat, par le produit "
              "Global Forest Change de Hansen utilisé comme vérité terrain, "
              "par le modèle numérique de terrain SRTM dont nous dérivons "
              "l'altitude, la pente et l'exposition, et par des données "
              "météorologiques. Le tableau 1 en donne le détail.")
    tableau(pdf, "Tableau 1 – Sources de données utilisées.",
            ["Source", "Description", "Résolution", "Couverture"], [
                ["Sentinel-2 (ESA)", "Images multispectrales (6 bandes)",
                 "10 m", "2015 à ce jour"],
                ["Landsat 8/9 (NASA)", "Images multispectrales", "30 m",
                 "2013 à ce jour"],
                ["Hansen GFC", "Perte forestière annuelle (vérité terrain)",
                 "30 m", "2000–2023"],
                ["SRTM", "Altitude, pente, exposition", "30 m", "Mondiale"],
                ["OpenWeatherMap", "Précipitations, température", "–",
                 "Temps réel"],
            ], widths=(24, 42, 16, 18))
    body(pdf, "De ces sources sont dérivées les variables explicatives. Six "
              "bandes spectrales de Sentinel-2 sont retenues (bleu, vert, "
              "rouge, proche infrarouge et deux bandes d'infrarouge à ondes "
              "courtes), auxquelles s'ajoutent quatre indices calculés et "
              "trois variables topographiques, soit treize variables par "
              "pixel. Le tableau 2 présente les bandes et les formules des "
              "indices.")
    tableau(pdf, "Tableau 2 – Bandes spectrales Sentinel-2 et indices dérivés.",
            ["Bande / Indice", "Description"], [
                ["B2, B3, B4", "Bleu, vert, rouge (domaine visible)"],
                ["B8", "Proche infrarouge (NIR, 842 nm)"],
                ["B11, B12", "Infrarouge à ondes courtes (SWIR)"],
                ["NDVI", "(NIR − Rouge) / (NIR + Rouge) : vigueur de la "
                         "végétation"],
                ["EVI", "Indice de végétation amélioré (corrige sol et "
                        "atmosphère)"],
                ["NDWI", "(Vert − NIR) / (Vert + NIR) : teneur en eau"],
                ["NBR", "(NIR − SWIR2) / (NIR + SWIR2) : surfaces brûlées"],
            ], widths=(28, 72))

    section(pdf, "II.4", "Prétraitement et préparation des données")
    body(pdf, "Le prétraitement répond d'abord à la contrainte majeure de la "
              "zone équatoriale : la couverture nuageuse quasi permanente. Les "
              "nuages et leurs ombres sont masqués à l'aide de la bande de "
              "classification de scène (SCL) fournie avec Sentinel-2, puis des "
              "composites médians de saison sèche (juin à septembre) sont "
              "constitués pour chaque année, de façon à obtenir une image "
              "annuelle exploitable. Les indices spectraux sont ensuite "
              "calculés de manière vectorisée sur l'ensemble de la grille.")
    body(pdf, "Pour l'apprentissage, deux jeux de données sont construits. Le "
              "premier, destiné aux modèles pixel, associe à chaque pixel ses "
              "treize variables et son étiquette de classe. Le second, destiné "
              "au réseau U-Net, découpe la zone en tuiles de 128 pixels de "
              "côté sur six bandes. Dans les deux cas, la séparation entre "
              "jeux d'entraînement, de validation et de test (70, 15 et 15 % "
              "respectivement) est effectuée par blocs spatiaux et non par "
              "tirage aléatoire de pixels : cette précaution évite qu'un pixel "
              "de test soit voisin immédiat d'un pixel d'entraînement, ce qui "
              "gonflerait artificiellement les performances mesurées. La "
              "classification distingue cinq classes de couverture du sol, "
              "présentées au tableau 3.")
    tableau(pdf, "Tableau 3 – Classes de couverture du sol.",
            ["Code", "Classe"], [
                ["0", "Forêt dense"],
                ["1", "Forêt dégradée"],
                ["2", "Agriculture / sol nu"],
                ["3", "Eau"],
                ["4", "Zone urbaine / bâti"],
            ], widths=(15, 85))

    section(pdf, "II.5", "Modélisation")
    sous_section(pdf, "II.5.1", "Random Forest, modèle de référence")
    body(pdf, "Le Random Forest sert de modèle de référence. Il agrège deux "
              "cents arbres de décision, chacun entraîné sur un échantillon "
              "bootstrap des données et sur un sous-ensemble aléatoire des "
              "variables, la prédiction finale résultant d'un vote "
              "majoritaire. La décorrélation des arbres réduit la variance "
              "sans accroître le biais, et l'importance de Gini calculée sur "
              "l'ensemble de la forêt indique quelles variables discriminent "
              "le mieux les classes, ce qui rend le modèle directement "
              "interprétable. La profondeur maximale des arbres est fixée à "
              "quinze.")
    sous_section(pdf, "II.5.2", "XGBoost")
    body(pdf, "XGBoost repose sur le principe du gradient boosting : les "
              "arbres y sont construits séquentiellement, chaque nouvel arbre "
              "minimisant, par descente de gradient, une fonction de perte "
              "régularisée calculée sur les erreurs résiduelles des arbres "
              "précédents. Ce mécanisme capture des interactions fines entre "
              "variables. Nous l'entraînons sur les mêmes treize variables que "
              "le Random Forest (deux cents arbres, profondeur dix, taux "
              "d'apprentissage 0,1), ce qui permet une comparaison directe "
              "entre les deux approches d'ensemble.")
    sous_section(pdf, "II.5.3", "U-Net")
    body(pdf, "Le réseau U-Net reçoit en entrée des tuiles de 128 par 128 "
              "pixels sur les six bandes brutes et produit une carte de "
              "classes de même dimension. Son encodeur extrait des "
              "caractéristiques spatiales à plusieurs échelles ; son décodeur, "
              "grâce aux connexions de saut, restitue une localisation "
              "précise. Il exploite ainsi le contexte spatial, textures et "
              "formes des parcelles, que les modèles pixel ignorent par "
              "construction.")
    sous_section(pdf, "II.5.4", "Modèle de prédiction du risque")
    body(pdf, "Un quatrième modèle, distinct des trois précédents, répond à "
              "l'objectif de prédiction. Il s'agit d'un classifieur binaire de "
              "type gradient boosting qui estime, pour chaque pixel encore "
              "forestier, la probabilité qu'il soit déforesté à un horizon "
              "d'environ deux ans. Ses variables d'entrée sont la distance à "
              "la route la plus proche, la distance au village le plus proche, "
              "la distance au front de déforestation existant, la pente, "
              "l'altitude et le taux de déforestation du voisinage. Sa sortie "
              "est convertie en carte de risque graduée de 0 à 100.")
    sous_section(pdf, "II.5.5", "Protocole d'évaluation")
    body(pdf, "Les modèles sont évalués sur le jeu de test spatial au moyen "
              "des métriques usuelles : exactitude globale, précision, rappel "
              "et F1-score en moyenne macro, aire sous la courbe ROC, ainsi "
              "que l'intersection sur union (IoU) par classe et en moyenne "
              "pour la qualité spatiale de la segmentation. La matrice de "
              "confusion complète l'analyse en révélant les confusions entre "
              "classes voisines, en particulier entre la forêt dégradée et "
              "l'agriculture.")

    section(pdf, "II.6", "Développement et réalisation")
    body(pdf, "La plateforme est développée en Python 3.11 selon une "
              "architecture modulaire : un module de collecte, un module de "
              "prétraitement, un module de modélisation, un module de "
              "visualisation, un module d'analyse d'impact et une API. La "
              "collecte satellite s'appuie sur Google Earth Engine et "
              "rasterio ; le prétraitement à grande échelle peut être confié "
              "à PySpark ; l'apprentissage utilise scikit-learn, XGBoost et "
              "TensorFlow/Keras ; l'API est servie par FastAPI et les "
              "interfaces par Streamlit ainsi que par un frontal web en "
              "React ; les données applicatives sont stockées dans "
              "PostgreSQL, avec repli automatique sur SQLite. L'ensemble est "
              "conteneurisé avec Docker et couvert par une suite de tests "
              "pytest exécutée en intégration continue.")
    body(pdf, "Deux choix de conception méritent d'être soulignés. D'une "
              "part, une couche d'abstraction des sources de données permet "
              "de basculer du mode démonstration, qui repose sur des données "
              "synthétiques réalistes, aux images réelles sans modifier le "
              "code : il suffit de déposer les fichiers GeoTIFF dans le "
              "répertoire prévu et de désactiver le mode démonstration. "
              "D'autre part, chaque dépendance lourde dispose d'un repli "
              "automatique, de sorte que l'application fonctionne dans tout "
              "environnement, même dépourvu de TensorFlow ou de PostgreSQL. "
              "La sécurité n'est pas négligée : les mots de passe sont hachés "
              "avec bcrypt, les sessions reposent sur des jetons JWT et une "
              "authentification à deux facteurs compatible Google "
              "Authenticator protège l'accès, avec un contrôle par rôle "
              "distinguant utilisateurs et administrateurs.")

    section(pdf, "II.7", "Contraintes et hypothèses de travail")
    body(pdf, "Trois contraintes encadrent la portée de la méthode. Les "
              "données d'apprentissage doivent être représentatives de la "
              "zone et en quantité suffisante ; la couverture nuageuse "
              "équatoriale limite la disponibilité des images optiques, ce "
              "que les composites atténuent sans l'éliminer ; enfin, les "
              "résultats présentés au chapitre suivant proviennent du mode "
              "démonstration et devront être confirmés sur images réelles et "
              "vérité de terrain avant tout usage opérationnel.")
    section(pdf, "II.8", "Conclusion partielle")
    body(pdf, "Ce chapitre a présenté la zone d'étude, les données mobilisées "
              "et leur préparation, les quatre modèles retenus avec leur "
              "justification, le protocole d'évaluation ainsi que la "
              "réalisation logicielle de la plateforme. Le chapitre suivant "
              "expose les résultats obtenus et les discute au regard des "
              "hypothèses formulées au chapitre premier.")

    # ══════════════════════════════════════════════════════════════════
    #  CHAPITRE III
    # ══════════════════════════════════════════════════════════════════
    chapitre(pdf, "III", "Résultats, discussion et conclusion")
    body(pdf, "Avant d'exposer les résultats, une précision méthodologique "
              "s'impose : les chiffres présentés dans ce chapitre proviennent "
              "de l'exécution de la plateforme en mode démonstration, sur des "
              "données synthétiques réalistes qui reproduisent la dynamique "
              "observée au Mai-Ndombe, à savoir l'avancée d'un front agricole "
              "depuis les villages et les routes. Ils valident la chaîne de "
              "traitement de bout en bout et illustrent les livrables ; ils "
              "ont vocation à être remplacés par les résultats sur images "
              "Sentinel-2 réelles dès que la collecte sera effectuée.",
         style="I")

    section(pdf, "III.1", "Présentation des résultats")
    sous_section(pdf, "III.1.1", "Dynamique de la couverture forestière")
    rows = [[s["year"], fr(s["forest"]), fr(s["loss"]), fr(s["rate"], 2)]
            for s in stats]
    tableau(pdf, "Tableau 4 – Dynamique annuelle de la couverture "
                 "forestière (2015–2025).",
            ["Année", "Forêt (ha)", "Perte (ha)", "Taux (%)"], rows,
            widths=(20, 30, 28, 22))
    body(pdf, f"Sur la période {ANALYSIS_START_YEAR}–{ANALYSIS_END_YEAR}, "
              f"la couverture forestière simulée passe de {fr(f0)} hectares à "
              f"{fr(f1)} hectares, soit une perte cumulée d'environ "
              f"{fr(total_loss)} hectares, ce qui représente près de "
              f"{fr(100 * total_loss / f0)} % du couvert initial. Le taux "
              "annuel de déforestation croît régulièrement d'année en année, "
              "ce qui traduit l'accélération du front agricole à mesure qu'il "
              "s'éloigne des villages et progresse le long des axes de "
              "circulation.")
    sous_section(pdf, "III.1.2", "Comparaison des modèles")
    tableau(pdf, "Tableau 5 – Comparaison des performances des modèles "
                 "(mode démonstration).",
            ["Modèle", "Exact.", "Préc.", "Rappel", "F1", "AUC", "IoU moy."],
            MODEL_METRICS, widths=(30, 12, 12, 13, 11, 11, 14))
    body(pdf, "Les trois modèles atteignent une exactitude comprise entre "
              "0,89 et 0,91. Le U-Net obtient les meilleures valeurs brutes, "
              "avec un F1-score macro de 0,89 et une IoU moyenne de 0,82, ce "
              "qui s'explique par sa capacité à exploiter le contexte "
              "spatial ; XGBoost le suit de très près, et le Random Forest, "
              "légèrement en retrait, demeure le modèle le plus directement "
              "interprétable. L'analyse de l'importance des variables sur les "
              "modèles d'ensemble fait ressortir le NDVI et la bande du "
              "proche infrarouge comme les prédicteurs les plus "
              "discriminants, conformément à la littérature. Quant au modèle "
              "de risque, il atteint une aire sous la courbe ROC de 0,83 : la "
              "proximité aux routes, aux villages et aux fronts de coupe "
              "existants se confirme fortement prédictive de la déforestation "
              "à venir.")
    sous_section(pdf, "III.1.3", "Traduction en émissions de CO2")
    tableau(pdf, "Tableau 6 – Traduction de la perte forestière en "
                 "émissions de CO2.",
            ["Indicateur", "Valeur"], [
                ["Biomasse aérienne moyenne (AGB)",
                 f"{fr(AGB_TONNES_PER_HA)} t/ha"],
                ["Fraction de carbone (GIEC)", "0,47"],
                ["CO2 émis par hectare détruit",
                 f"≈ {fr(CO2_TONNES_PER_HA)} t/ha"],
                [f"Perte forestière {ANALYSIS_START_YEAR}–"
                 f"{ANALYSIS_END_YEAR}", f"≈ {fr(total_loss)} ha"],
                ["Émissions de CO2 associées",
                 f"≈ {fr(co2_mt, 1)} millions de tonnes"],
            ], widths=(60, 40))
    body(pdf, "En appliquant un facteur d'émission dérivé de la biomasse "
              "aérienne moyenne d'une forêt dense du Bassin du Congo, soit "
              "environ 310 tonnes par hectare, la perte simulée correspond à "
              f"près de {fr(co2_mt)} millions de tonnes de CO2. Cette "
              "conversion, opérée automatiquement par la plateforme, relie le "
              "résultat technique au langage de la finance climat : "
              "mesure, rapportage et vérification (MRV), crédits carbone et "
              "paiements aux résultats, autant de notions centrales dans une "
              "province pilote REDD+.")

    section(pdf, "III.2", "Discussion")
    sous_section(pdf, "III.2.1", "Validation des hypothèses")
    body(pdf, "La confrontation des résultats aux hypothèses du chapitre "
              "premier donne le bilan suivant. L'hypothèse H1 est validée : "
              "tous les modèles dépassent largement le seuil d'exactitude de "
              "0,80 fixé, ce qui confirme le pouvoir discriminant des indices "
              "spectraux combinés aux bandes brutes et à la topographie. "
              "L'hypothèse H2 est partiellement validée : le Random Forest et "
              "XGBoost obtiennent des performances très proches de celles du "
              "U-Net pour un coût de calcul et un effort d'interprétation "
              "bien moindres, le réseau profond ne prenant l'avantage que sur "
              "les métriques proprement spatiales telles que l'IoU. "
              "L'hypothèse H3 est validée : avec une AUC de 0,83, supérieure "
              "au seuil de 0,75, la déforestation future s'avère bel et bien "
              "spatialement prédictible à partir de variables de proximité.")
    sous_section(pdf, "III.2.2", "Mise en perspective et implications")
    body(pdf, "Ces résultats concordent avec la littérature, qui rapporte des "
              "performances élevées des méthodes d'ensemble et des réseaux "
              "convolutifs pour la cartographie forestière. La valeur ajoutée "
              "de DeforestWatch-DRC ne réside donc pas dans une innovation "
              "algorithmique, mais dans l'intégration : le passage d'un outil "
              "de constat à un outil d'action, grâce à la carte de risque "
              "prédictive, au signalement citoyen, à la valorisation carbone "
              "et à une interface en français appropriable localement. Les "
              "bénéficiaires potentiels sont nombreux : le ministère de "
              "l'Environnement, pour lequel la plateforme peut constituer une "
              "brique d'un système national de surveillance ; les gardes "
              "forestiers et l'ICCN, destinataires d'alertes géolocalisées ; "
              "le gouvernement provincial du Mai-Ndombe, pour le ciblage des "
              "secteurs prioritaires ; les communautés locales, auxquelles le "
              "signalement donne une voix ; et les porteurs de projets "
              "carbone, pour la quantification des réductions d'émissions.")
    sous_section(pdf, "III.2.3", "Points forts et points faibles du travail")
    body(pdf, "Au chapitre des points forts, nous relevons la couverture de "
              "la chaîne complète de la donnée à la décision, la "
              "reproductibilité assurée par les tests automatisés et "
              "l'intégration continue, la robustesse de l'architecture grâce "
              "aux mécanismes de repli, et l'ancrage dans le contexte "
              "congolais. Au chapitre des faiblesses, les résultats chiffrés "
              "restent issus du mode démonstration, aucune campagne de vérité "
              "terrain n'a encore été menée, et la dépendance aux images "
              "optiques expose le système à la contrainte nuageuse.")

    section(pdf, "III.3", "Conclusion générale")
    body(pdf, "Au terme de ce travail, l'objectif que nous nous étions "
              "assigné est atteint : une plateforme complète et fonctionnelle "
              "de surveillance et de prédiction de la déforestation de la "
              "forêt équatoriale du Mai-Ndombe a été conçue, réalisée et "
              "testée, couvrant l'ensemble de la chaîne de valeur de la "
              "science des données, depuis la collecte des images satellites "
              "jusqu'au déploiement d'un tableau de bord d'aide à la "
              "décision. Les trois hypothèses de recherche ont été "
              "confrontées aux résultats et vérifiées, la deuxième ne l'étant "
              "que partiellement. La contribution principale du travail est "
              "une intégration cohérente et contextualisée de méthodes "
              "éprouvées, enrichie d'une dimension prédictive et d'une "
              "valorisation carbone qui en font un outil résolument tourné "
              "vers l'action.")

    section(pdf, "III.4", "Limites de l'étude")
    body(pdf, "Quatre limites doivent être gardées à l'esprit. La couverture "
              "nuageuse équatoriale restreint la disponibilité des images "
              "optiques exploitables ; l'apprentissage supervisé requiert des "
              "données de vérité terrain de qualité dont la collecte reste à "
              "organiser ; les résultats chiffrés, obtenus en mode "
              "démonstration, doivent être confirmés sur données réelles ; "
              "enfin, l'exploitation durable d'un tel outil soulève des "
              "questions d'accès aux données, de connectivité et de "
              "maintenance qui dépassent le cadre de ce projet.")

    section(pdf, "III.5", "Suggestions pour des recherches futures")
    body(pdf, "Plusieurs prolongements nous paraissent prometteurs. "
              "L'intégration de l'imagerie radar Sentinel-1, insensible aux "
              "nuages, lèverait la principale contrainte d'observation. Des "
              "modèles spatio-temporels, tels que les réseaux convolutifs "
              "récurrents ou les transformeurs, pourraient affiner la "
              "prédiction du risque en exploitant la trajectoire temporelle "
              "de chaque secteur. Un système d'alertes en temps quasi réel "
              "renforcerait l'utilité opérationnelle de la plateforme pour "
              "les gestionnaires forestiers. Une campagne de validation par "
              "points GPS de terrain, croisée avec les données de Hansen, "
              "consoliderait la fiabilité des cartes produites. Enfin, "
              "l'extension de la démarche à d'autres provinces de la forêt "
              "équatoriale congolaise en éprouverait la généralité.")

    # ── Bibliographie ─────────────────────────────────────────────────
    heading_front(pdf, "Bibliographie")
    refs = [
        "BREIMAN, L. (2001). Random Forests. Machine Learning, 45(1), 5–32.",
        "CHEN, T. et GUESTRIN, C. (2016). XGBoost: A Scalable Tree Boosting "
        "System. Proceedings of the 22nd ACM SIGKDD International Conference "
        "on Knowledge Discovery and Data Mining, 785–794.",
        "DRUSCH, M. et al. (2012). Sentinel-2: ESA's Optical High-Resolution "
        "Mission for GMES Operational Services. Remote Sensing of "
        "Environment, 120, 25–36.",
        "FAO (2020). Évaluation des ressources forestières mondiales 2020. "
        "Rome : Organisation des Nations Unies pour l'alimentation et "
        "l'agriculture.",
        "GIEC (2006). Lignes directrices pour les inventaires nationaux de "
        "gaz à effet de serre, volume 4 : Agriculture, foresterie et autres "
        "affectations des terres. Genève.",
        "GORELICK, N. et al. (2017). Google Earth Engine: Planetary-scale "
        "geospatial analysis for everyone. Remote Sensing of Environment, "
        "202, 18–27.",
        "HANSEN, M. C. et al. (2013). High-Resolution Global Maps of "
        "21st-Century Forest Cover Change. Science, 342(6160), 850–853.",
        "RONNEBERGER, O., FISCHER, P. et BROX, T. (2015). U-Net: "
        "Convolutional Networks for Biomedical Image Segmentation. Medical "
        "Image Computing and Computer-Assisted Intervention (MICCAI), "
        "234–241.",
        "TUCKER, C. J. (1979). Red and photographic infrared linear "
        "combinations for monitoring vegetation. Remote Sensing of "
        "Environment, 8(2), 127–150.",
    ]
    for i, r in enumerate(refs, start=1):
        item(pdf, r, bullet=f"{i}.")

    pdf.ln(4)
    pdf.set_font("Serif", "B", 13)
    pdf.start_section("WEBIOGRAPHIE", level=0)
    pdf.cell(0, 8, "WEBIOGRAPHIE", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    webs = [
        "Global Forest Watch, https://www.globalforestwatch.org, consulté le "
        "10 juillet 2026.",
        "Programme Copernicus / Sentinel-2, Agence spatiale européenne, "
        "https://sentinels.copernicus.eu, consulté le 10 juillet 2026.",
        "Google Earth Engine, https://earthengine.google.com, consulté le "
        "10 juillet 2026.",
        "Central African Forest Initiative (CAFI), https://www.cafi.org, "
        "consulté le 10 juillet 2026.",
    ]
    for i, w in enumerate(webs, start=1):
        item(pdf, w, bullet=f"{i}.")

    # ── Annexes ───────────────────────────────────────────────────────
    heading_front(pdf, "Annexes")
    sous_section(pdf, "Annexe A", "Structure du dépôt de code")
    body(pdf, "Le dépôt s'organise en répertoires : config (configuration "
              "centralisée), src (modules data, preprocessing, models, "
              "visualization, analysis, api et utils), streamlit_app (tableau "
              "de bord), frontend (application web React), notebooks "
              "(exploration, prétraitement, modélisation, résultats), scripts "
              "(automatisation), tests (suite pytest), data (raw, processed, "
              "models) et docs (documents académiques).", indent=False)
    sous_section(pdf, "Annexe B", "Lancement du projet en mode démonstration")
    body(pdf, "Quatre commandes suffisent : make seed génère les données de "
              "démonstration et entraîne les modèles ; make api démarre l'API "
              "FastAPI ; make dashboard démarre le tableau de bord "
              "Streamlit ; make frontend démarre le frontal React. La suite "
              "de tests s'exécute avec make test et le présent document se "
              "régénère avec make monograph.", indent=False)
    sous_section(pdf, "Annexe C", "Principaux points d'entrée de l'API")
    body(pdf, "L'API expose notamment : les routes d'authentification "
              "(inscription, connexion, vérification du code à deux "
              "facteurs) ; les statistiques de perte forestière par année ; "
              "la synthèse des zones à risque par année ; les performances "
              "des modèles ; les émissions de CO2 et leurs équivalences ; les "
              "alertes de déforestation détectées ; le signalement citoyen ; "
              "et les routes d'administration réservées (utilisateurs, "
              "journaux d'activité).", indent=False)
    sous_section(pdf, "Annexe D", "Captures d'écran")
    body(pdf, "Insérer ici les captures d'écran du tableau de bord "
              "Streamlit, de la documentation interactive de l'API, du "
              "frontal web et de l'animation retraçant l'évolution "
              "2015–2025 de la zone d'étude.", style="I", indent=False)

    return pdf


def main() -> None:
    out = Path("docs/monographie_deforestwatch.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    pdf = build()
    pdf.output(str(out))
    print(f"Monographie PDF générée -> {out} ({pdf.page_no()} pages)")


if __name__ == "__main__":
    main()
