"""
Génère la monographie académique DeforestWatch-DRC au format Word (.docx).

Document conforme au canevas des monographies de projets de la Faculté des
Sciences Informatiques de l'UPC (résumé, trois chapitres, bibliographie et
webiographie, annexes). Le contenu est rédigé à partir du projet réellement
implémenté ; les résultats chiffrés proviennent de l'exécution de référence en
mode démonstration (data/processed/model_metrics.json) et sont à confirmer sur
données réelles Sentinel-2.

Usage  : python -m scripts.generate_monograph   (ou make monograph)
Sortie : docs/UPC_DeforestWatch_Monographie.docx
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

from src.utils.logger import get_logger

log = get_logger("generate_monograph")

AUTHOR = "Joyce A. WETUNGANI"
ACADEMIC_YEAR = "2025-2026"
OUT_PATH = Path("docs/UPC_DeforestWatch_Monographie.docx")

GREEN = RGBColor(0x0B, 0x6E, 0x2D)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
GRAY = RGBColor(0x77, 0x77, 0x77)

# ── Valeurs de l'exécution de référence (mode démo, graine 42) ────────────
# Remplacées par le contenu de data/processed/model_metrics.json s'il existe.
REFERENCE_METRICS = {
    "best_model": "XGBoost",
    "comparison": [
        {"Modèle": "XGBoost", "Accuracy": 0.9761, "Precision": 0.8802,
         "Recall": 0.9178, "F1-macro": 0.8940, "Mean IoU": 0.8218},
        {"Modèle": "RandomForest", "Accuracy": 0.9746, "Precision": 0.8748,
         "Recall": 0.9153, "F1-macro": 0.8889, "Mean IoU": 0.8144},
        {"Modèle": "U-Net", "Accuracy": 0.9014, "Precision": 0.7198,
         "Recall": 0.9001, "F1-macro": 0.7384, "Mean IoU": 0.6631},
    ],
    "risk_predictor": {"train_accuracy": 0.8699, "n_positive": 4648},
}


def _load_metrics() -> dict:
    from src.utils.helpers import load_json

    path = Path("data/processed/model_metrics.json")
    if path.exists():
        try:
            report = load_json(path)
            if report.get("comparison"):
                return report
        except Exception as exc:  # pragma: no cover
            log.warning(f"model_metrics.json illisible ({exc}) → valeurs de référence.")
    return REFERENCE_METRICS


def fr(x, nd=4) -> str:
    """Format numérique français : virgule décimale."""
    if isinstance(x, float):
        return f"{x:.{nd}f}".replace(".", ",")
    return str(x)


def fr_int(x) -> str:
    """Milliers séparés par des espaces (usage français)."""
    return f"{int(round(x)):,}".replace(",", " ")


# ── Helpers de mise en forme ──────────────────────────────────────────────
def _base_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    for name, size in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 11.5)):
        st = doc.styles[name]
        st.font.name = "Calibri"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = GREEN if name != "Heading 3" else DARK


def h1(doc, text):
    return doc.add_heading(text, level=1)


def h2(doc, text):
    return doc.add_heading(text, level=2)


def h3(doc, text):
    return doc.add_heading(text, level=3)


def para(doc, text, justify=True, center=False, italic=False, bold=False,
         size=11, color=None):
    p = doc.add_paragraph()
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.italic = italic
    run.bold = bold
    run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = color
    return p


def formula(doc, text):
    return para(doc, text, center=True, italic=True, size=11.5)


def figure_placeholder(doc, caption, hint):
    para(doc, f"[Insérer ici : {hint}]", center=True, italic=True, color=GRAY)
    para(doc, caption, center=True, bold=True, size=10.5)


def table(doc, headers, rows, caption=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    for i, htxt in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = str(htxt)
        for r in cell.paragraphs[0].runs:
            r.bold = True
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = str(v)
    if caption:
        para(doc, caption, center=True, bold=True, size=10.5)
    return t


def toc_field(doc):
    """Insère un champ de table des matières Word (à actualiser dans Word)."""
    p = doc.add_paragraph()
    run = p.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-3" \\h \\z \\u'
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Table des matières — clic droit puis « Mettre à jour les champs »."
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for el in (begin, instr, sep, placeholder, end):
        run._r.append(el)


# ── Sections du document ──────────────────────────────────────────────────
def _cover(doc):
    para(doc, "UNIVERSITÉ PROTESTANTE AU CONGO", center=True, bold=True, size=14)
    para(doc, "FACULTÉ DES SCIENCES INFORMATIQUES", center=True, bold=True, size=13)
    para(doc, "Département de Data Science", center=True, size=12)
    doc.add_paragraph()
    para(doc,
         "CONCEPTION D'UNE PLATEFORME INTELLIGENTE DE SURVEILLANCE ET DE "
         "PRÉDICTION DE LA DÉFORESTATION PAR IMAGERIE SATELLITE ET "
         "APPRENTISSAGE AUTOMATIQUE",
         center=True, bold=True, size=16, color=GREEN)
    para(doc, "Cas de la forêt équatoriale du Bassin du Congo — "
              "province du Mai-Ndombe (RDC)", center=True, size=13)
    doc.add_paragraph()
    para(doc, "Projet présenté en vue de l'obtention du grade de Licencié "
              "en Data Science", center=True, size=12)
    doc.add_paragraph()
    para(doc, f"Par {AUTHOR}", center=True, bold=True, size=12)
    para(doc, "Étudiante en L3 Data Science", center=True, size=11)
    doc.add_paragraph()
    para(doc, "Dirigé par : [Nom de l'encadrant à compléter]", center=True, size=11)
    para(doc, f"Kinshasa, Année académique {ACADEMIC_YEAR}", center=True, size=11)


def _resume(doc, m):
    best = m["comparison"][0]
    rf = next(c for c in m["comparison"] if c["Modèle"] == "RandomForest")
    unet = next(c for c in m["comparison"] if c["Modèle"] == "U-Net")

    h1(doc, "RÉSUMÉ")
    para(doc,
         "Ce travail présente la conception et l'implémentation de DeforestWatch-DRC, "
         "une plateforme intelligente de surveillance et de prédiction de la déforestation "
         "de la forêt équatoriale du Bassin du Congo, appliquée à la province du Mai-Ndombe "
         "en République Démocratique du Congo. Le projet répond à une problématique "
         "environnementale majeure : la RDC abrite la deuxième plus grande forêt tropicale "
         "humide du monde et figure parmi les premiers pays au monde pour la perte de forêt "
         "primaire, sous l'effet d'une déforestation essentiellement diffuse — agriculture "
         "sur brûlis, production de charbon de bois, exploitation artisanale — que les "
         "outils de surveillance globaux existants captent mal et pour laquelle aucune "
         "analyse prédictive locale adaptée au contexte congolais n'est disponible.")
    para(doc,
         "La solution développée couvre l'intégralité de la chaîne de valeur de la Data "
         "Science appliquée à la télédétection. Elle associe une couche de collecte de "
         "données satellitaires (Google Earth Engine, composites annuels Sentinel-2, "
         "référentiel Hansen Global Forest Change, topographie SRTM), une couche de "
         "prétraitement (masquage des nuages par la bande SCL, composites médians de "
         "saison sèche, calcul des indices spectraux NDVI, EVI, NDWI et NBR, extraction "
         "de treize variables par pixel), une couche de modélisation comparant trois "
         "modèles de classification de la couverture du sol (Random Forest, XGBoost et "
         "U-Net) complétés d'un modèle de prédiction du risque de déforestation future, "
         "et une couche de restitution comprenant une API REST sécurisée construite avec "
         "FastAPI (authentification JWT à deux facteurs), une base de données PostgreSQL, "
         "un tableau de bord Streamlit et un frontend web React. Des modules d'analyse "
         "traduisent les résultats en indicateurs actionnables : alertes géolocalisées "
         "par secteur, conversion de la perte forestière en émissions de CO2 et apport "
         "du radar Sentinel-1 pour la surveillance sous couverture nuageuse.")
    para(doc,
         "L'évaluation des modèles, conduite selon un protocole identique sur un jeu de "
         "données à découpage spatial par blocs afin d'éviter la fuite d'information "
         f"géographique, désigne le modèle {best['Modèle']} comme le plus performant, "
         f"avec une exactitude de {fr(best['Accuracy'])}, un F1-macro de "
         f"{fr(best['F1-macro'])} et un IoU moyen de {fr(best['Mean IoU'])}, devant la "
         f"forêt aléatoire (F1-macro de {fr(rf['F1-macro'])}) et l'implémentation de "
         f"repli du U-Net (F1-macro de {fr(unet['F1-macro'])}). Ces résultats proviennent "
         "de l'exécution de référence en mode démonstration, sur des données synthétiques "
         "réalistes reproduisant la dynamique d'un front de déforestation agricole, et "
         "valident la chaîne de traitement de bout en bout.")
    para(doc,
         "Les résultats obtenus démontrent la faisabilité d'une plateforme de surveillance "
         "forestière pilotée par les données, conçue et maîtrisée localement, dans le "
         "contexte spécifique de la RDC et de la province pilote REDD+ du Mai-Ndombe. Ils "
         "mettent également en évidence des limites assumées : la confirmation des "
         "performances sur images satellitaires réelles reste à conduire, certaines "
         "classes rares sont absentes de l'ensemble de test spatial, et plusieurs points "
         "de sécurisation doivent être renforcés avant un déploiement en production.")
    para(doc,
         "Mots-clés : déforestation, télédétection, Sentinel-2, apprentissage automatique, "
         "Random Forest, XGBoost, U-Net, Bassin du Congo, Mai-Ndombe, REDD+, FastAPI.",
         italic=True)


def _front_matter(doc):
    h1(doc, "TABLE DES MATIÈRES")
    para(doc, "(Champ automatique — clic droit puis « Mettre à jour les champs » "
              "dans Word pour actualiser la pagination.)", size=10, color=GRAY)
    toc_field(doc)
    doc.add_page_break()

    h1(doc, "LISTE DES ABRÉVIATIONS ET ACRONYMES")
    table(doc, ["Abréviation", "Signification"], [
        ["2FA", "Two-Factor Authentication (authentification à deux facteurs)"],
        ["AGB", "Above-Ground Biomass (biomasse aérienne)"],
        ["API", "Application Programming Interface (interface de programmation applicative)"],
        ["CNN", "Convolutional Neural Network (réseau de neurones convolutif)"],
        ["CORS", "Cross-Origin Resource Sharing"],
        ["EVI", "Enhanced Vegetation Index (indice de végétation amélioré)"],
        ["GEE", "Google Earth Engine"],
        ["GFW", "Global Forest Watch"],
        ["IoU", "Intersection over Union (indice de Jaccard)"],
        ["JSON", "JavaScript Object Notation"],
        ["JWT", "JSON Web Token"],
        ["ML", "Machine Learning (apprentissage automatique)"],
        ["MRV", "Mesure, Rapportage et Vérification"],
        ["NBR", "Normalized Burn Ratio (indice normalisé de brûlis)"],
        ["NDVI", "Normalized Difference Vegetation Index"],
        ["NDWI", "Normalized Difference Water Index"],
        ["OTP", "One-Time Password (mot de passe à usage unique)"],
        ["RDC", "République Démocratique du Congo"],
        ["REDD+", "Réduction des Émissions dues à la Déforestation et à la Dégradation"],
        ["REST", "Representational State Transfer"],
        ["SAR", "Synthetic Aperture Radar (radar à synthèse d'ouverture)"],
        ["SCL", "Scene Classification Layer (bande de classification de scène Sentinel-2)"],
        ["SRTM", "Shuttle Radar Topography Mission"],
        ["UML", "Unified Modeling Language"],
        ["UPC", "Université Protestante au Congo"],
    ])
    doc.add_page_break()

    h1(doc, "LISTE DES FIGURES ET TABLEAUX")
    h2(doc, "Liste des figures")
    for f in [
        "Figure 1 — Architecture générale de DeforestWatch-DRC",
        "Figure 2 — Diagramme de cas d'utilisation",
        "Figure 3 — Diagramme de classes",
        "Figure 4 — Diagramme de séquence du processus d'authentification à deux facteurs",
        "Figure 5 — Diagramme d'activité de la chaîne de traitement et de prédiction",
    ]:
        para(doc, f, justify=False)
    h2(doc, "Liste des tableaux")
    for t in [
        "Tableau 1 — Sources de données satellitaires et auxiliaires",
        "Tableau 2 — Tables relationnelles de la base de données et rôle",
        "Tableau 3 — Comparaison des modèles de classification (protocole identique, mêmes données)",
        "Tableau 4 — Évolution simulée de la couverture forestière (2015-2025, mode démonstration)",
        "Tableau 5 — Table synthétique des routes de l'API DeforestWatch-DRC",
    ]:
        para(doc, t, justify=False)


def _chapter1(doc):
    h1(doc, "1. MISE EN CONTEXTE ET REVUE DE LA LITTÉRATURE")

    h2(doc, "1.1 Introduction et mise en contexte")
    para(doc,
         "La République Démocratique du Congo abrite la deuxième plus grande forêt "
         "tropicale humide du monde, au cœur du Bassin du Congo dont elle concentre "
         "environ soixante pour cent de la superficie forestière. Cet écosystème "
         "équatorial joue un rôle climatique planétaire majeur : puits de carbone, "
         "régulation du cycle hydrologique régional et réservoir de biodiversité, "
         "auxquels s'ajoutent les tourbières de la Cuvette centrale, qui stockent "
         "d'immenses quantités de carbone. Ce patrimoine subit toutefois une "
         "déforestation accélérée qui place la RDC parmi les premiers pays au monde "
         "pour la perte de forêt primaire. À la différence du front de déforestation "
         "amazonien, largement industriel, la déforestation congolaise est "
         "essentiellement diffuse : agriculture itinérante sur brûlis de subsistance, "
         "production de charbon de bois (makala), exploitation forestière artisanale "
         "et expansion des villages produisent une multitude de petites coupes "
         "dispersées, difficiles à détecter et à anticiper.")
    para(doc,
         "Les outils de surveillance existants, tels que Global Forest Watch ou les "
         "alertes RADD, fournissent des données précieuses mais présentent des limites "
         "structurelles dans le contexte congolais : ils sont globaux et peu calibrés "
         "sur les moteurs locaux de la déforestation, essentiellement rétrospectifs, "
         "proposés dans des interfaces techniques anglophones, et n'offrent ni "
         "remontée d'information de terrain ni traduction des pertes en indicateurs "
         "directement exploitables par les acteurs nationaux. Or la province du "
         "Mai-Ndombe, retenue comme zone d'étude, est une province pilote du mécanisme "
         "REDD+ : un accord de paiements aux réductions d'émissions y lie la RDC à des "
         "bailleurs internationaux, de sorte que mesurer, réduire et prouver la "
         "déforestation y possède une valeur financière directe.")
    para(doc,
         "Ce constat a motivé la conception de DeforestWatch-DRC, une plateforme de "
         "surveillance et de prédiction de la déforestation pensée spécifiquement pour "
         "ce contexte. Ce travail s'inscrit dans le domaine de la Data Science appliquée "
         "à la télédétection : il combine développement logiciel, traitement d'images "
         "satellitaires, apprentissage automatique supervisé et restitution "
         "décisionnelle, dans une démarche qui vise à transformer des images brutes "
         "Sentinel-2 en indicateurs actionnables — cartes de couverture du sol, alertes "
         "géolocalisées, cartes de risque et estimations d'émissions de CO2 — au "
         "service des gestionnaires forestiers, de l'administration et des communautés "
         "locales.")

    h2(doc, "1.2 Problématique et objectifs de la recherche")
    h3(doc, "1.2.1 Problématique")
    para(doc,
         "La problématique centrale de ce travail peut être formulée ainsi : comment "
         "concevoir une plateforme capable, à partir d'images satellitaires "
         "multispectrales et de données auxiliaires librement accessibles, de détecter "
         "et de quantifier la perte forestière annuelle sur une zone cible de la forêt "
         "équatoriale du Mai-Ndombe, d'anticiper les zones exposées à une déforestation "
         "future, et de restituer ces informations sous une forme directement "
         "exploitable par les acteurs congolais de la protection forestière ?")
    para(doc,
         "Cette problématique se décline en plusieurs enjeux pratiques. Le premier tient "
         "à la nature diffuse de la déforestation congolaise, faite de petites coupes "
         "dispersées qu'un suivi à maille grossière ne révèle pas, et qui impose une "
         "analyse locale à résolution fine. Le deuxième tient à la couverture nuageuse "
         "quasi permanente de la zone équatoriale, qui limite sévèrement la "
         "disponibilité d'images optiques exploitables et impose des stratégies de "
         "composition temporelle, voire le recours à l'imagerie radar. Le troisième "
         "tient à la rareté des données de vérité terrain dans la région, qui "
         "contraint l'apprentissage supervisé et impose une grande rigueur dans "
         "l'évaluation des modèles. Le dernier enjeu concerne l'appropriation locale : "
         "l'outil doit être en français, fonctionner avec des moyens modestes et rester "
         "maîtrisable par des équipes congolaises, dans une logique de souveraineté "
         "des données environnementales.")
    h3(doc, "1.2.2 Objectifs de la recherche")
    para(doc,
         "L'objectif général de ce travail est de concevoir et d'implémenter une "
         "plateforme intelligente de surveillance de la déforestation de la forêt "
         "équatoriale du Bassin du Congo, intégrant un module de Data Science capable "
         "de classifier la couverture du sol, de quantifier la perte forestière et de "
         "prédire les zones à risque, sur le cas de la province du Mai-Ndombe.")
    para(doc,
         "Plus spécifiquement, ce travail vise à modéliser et développer une "
         "architecture logicielle complète associant une couche de collecte de données "
         "satellitaires, une chaîne de prétraitement, une API de restitution et deux "
         "interfaces utilisateur ; à constituer des jeux de données d'apprentissage "
         "pixel et tuiles à partir des composites annuels de la zone d'étude, selon un "
         "découpage spatial rigoureux ; à entraîner, évaluer et comparer trois modèles "
         "de classification de la couverture du sol (Random Forest, XGBoost, U-Net) "
         "selon un protocole identique ; à construire un modèle de prédiction du risque "
         "de déforestation future fondé sur des variables d'accessibilité et de "
         "topographie ; et à traduire les résultats techniques en indicateurs d'aide à "
         "la décision — alertes géolocalisées par secteur, estimation des émissions de "
         "CO2 associées à la perte forestière et signalement citoyen — au sein d'une "
         "plateforme sécurisée par une authentification à deux facteurs.")
    h3(doc, "1.2.3 Hypothèses")
    para(doc,
         "Deux hypothèses principales structurent ce travail. La première pose que les "
         "signatures spectrales des composites annuels Sentinel-2, enrichies des "
         "indices de végétation dérivés et de variables topographiques, contiennent une "
         "information suffisante pour classifier la couverture du sol de la zone "
         "d'étude en cinq classes avec un niveau de performance académiquement "
         "acceptable, au moyen de modèles d'apprentissage supervisé. La seconde pose "
         "que la déforestation future est en grande partie prédictible à partir de "
         "variables d'accessibilité — distance aux routes, aux villages et au front de "
         "déforestation existant — et de variables topographiques, conformément au "
         "caractère essentiellement anthropique et progressif du front agricole "
         "observé dans la région.")

    h2(doc, "1.3 Revue de la littérature théorique")
    para(doc,
         "La télédétection optique constitue depuis plusieurs décennies l'instrument "
         "privilégié du suivi des couverts végétaux. Les capteurs multispectraux "
         "embarqués sur les missions Landsat puis Sentinel-2 mesurent la réflectance "
         "de la surface terrestre dans des bandes allant du visible à l'infrarouge "
         "moyen, à partir desquelles sont dérivés des indices synthétiques dont le plus "
         "établi est le NDVI, proposé par Tucker (1979), qui exploite le contraste "
         "entre l'absorption du rouge par la chlorophylle et la forte réflexion du "
         "proche infrarouge par les tissus végétaux. Des indices complémentaires — EVI, "
         "moins saturé sur les couverts denses, NDWI pour les surfaces en eau et NBR "
         "pour les surfaces brûlées — affinent la caractérisation des états de "
         "surface. En zone équatoriale, la couverture nuageuse persistante impose en "
         "outre des stratégies de composition temporelle, typiquement des composites "
         "médians calculés sur la saison sèche après masquage des pixels nuageux.")
    para(doc,
         "Pour la classification supervisée de la couverture du sol, les méthodes "
         "d'ensemble à base d'arbres de décision occupent une place de référence dans "
         "la littérature de télédétection. La forêt aléatoire (Breiman, 2001) agrège "
         "par vote majoritaire un ensemble d'arbres entraînés sur des échantillons "
         "bootstrap et des sous-ensembles aléatoires de variables, ce qui réduit la "
         "variance du classifieur et le rend robuste au bruit et aux variables "
         "corrélées, sans hypothèse sur la forme de la relation entre spectre et "
         "classe. Le gradient boosting, dont XGBoost (Chen et Guestrin, 2016) est "
         "l'implémentation la plus répandue, construit au contraire les arbres "
         "séquentiellement, chaque arbre corrigeant les erreurs résiduelles de "
         "l'ensemble courant, et atteint fréquemment des performances supérieures sur "
         "données tabulaires au prix d'un réglage plus délicat.")
    para(doc,
         "Les approches profondes de segmentation sémantique complètent ce panorama. "
         "L'architecture U-Net (Ronneberger et al., 2015), initialement conçue pour "
         "l'imagerie biomédicale, associe un encodeur convolutif qui contracte "
         "l'information spatiale et un décodeur qui la restitue à pleine résolution, "
         "des connexions de saut transférant les détails fins de l'encodeur vers le "
         "décodeur. À la différence des approches pixel à pixel, elle exploite le "
         "contexte spatial — texture, formes, voisinage — et s'est imposée comme un "
         "standard de la segmentation d'images de télédétection. Sa contrepartie est "
         "un besoin en données annotées sensiblement supérieur à celui des méthodes "
         "d'ensemble. La qualité d'une segmentation s'évalue notamment par l'indice de "
         "Jaccard ou IoU, rapport de l'intersection à l'union entre la classe prédite "
         "et la classe de référence.")
    para(doc,
         "Sur le plan architectural, les plateformes modernes d'observation et d'aide "
         "à la décision adoptent une architecture découplée séparant une couche de "
         "services exposée sous forme d'API REST, une couche de persistance "
         "relationnelle et des interfaces clientes spécialisées. L'accès aux archives "
         "satellitaires massives s'appuie quant à lui sur des infrastructures "
         "d'analyse planétaire telles que Google Earth Engine (Gorelick et al., 2017), "
         "qui mutualisent le stockage et le calcul et rendent l'imagerie Sentinel-2 et "
         "les produits dérivés accessibles sans téléchargement préalable massif.")

    h2(doc, "1.4 Revue de la littérature empirique")
    para(doc,
         "Le suivi global du couvert forestier dispose depuis Hansen et al. (2013) "
         "d'un référentiel empirique majeur : les cartes mondiales annuelles de perte "
         "et de gain forestiers à trente mètres de résolution, dérivées des archives "
         "Landsat, qui alimentent la plateforme Global Forest Watch. Ces produits "
         "démontrent la faisabilité d'un suivi systématique par télédétection, mais "
         "leur vocation globale limite leur finesse d'interprétation locale : la "
         "définition binaire de la perte de couvert y capture mal la dégradation "
         "progressive, pourtant caractéristique des dynamiques congolaises.")
    para(doc,
         "Concernant spécifiquement le Bassin du Congo, Tyukavina et al. (2018) "
         "établissent empiriquement que la perte forestière y est dominée par le "
         "défrichement de petite échelle lié à l'agriculture de subsistance, en "
         "expansion continue, ce qui confirme le caractère diffus et anthropique des "
         "moteurs locaux et justifie une approche de prédiction fondée sur "
         "l'accessibilité — proximité des routes, des villages et des fronts de "
         "défrichement existants. Par ailleurs, Reiche et al. (2021) démontrent avec "
         "les alertes RADD l'apport décisif de l'imagerie radar Sentinel-1 pour la "
         "détection des perturbations forestières en zone équatoriale, la rétrodiffusion "
         "radar traversant la couverture nuageuse qui rend l'optique inexploitable une "
         "grande partie de l'année. Ces deux constats empiriques ont directement "
         "orienté la conception du module de risque et du module radar du présent "
         "travail.")
    para(doc,
         "Enfin, la littérature méthodologique en apprentissage automatique appliqué à "
         "la télédétection converge sur deux mises en garde reprises dans ce travail. "
         "La première concerne l'autocorrélation spatiale : un découpage aléatoire "
         "des pixels entre apprentissage et test surestime systématiquement les "
         "performances, des pixels voisins quasi identiques se retrouvant de part et "
         "d'autre de la séparation ; un découpage spatial par blocs s'impose. La "
         "seconde concerne la rareté de la vérité terrain dans les régions peu "
         "instrumentées : lorsque les données réelles annotées manquent au moment du "
         "développement, la validation de la chaîne de traitement sur des données "
         "synthétiques réalistes, clairement identifiées comme telles, constitue une "
         "étape intermédiaire légitime, à condition que les conclusions soient "
         "explicitement conditionnées à une confirmation ultérieure sur données "
         "réelles. C'est la démarche adoptée ici.")


def _chapter2(doc, m):
    h1(doc, "2. MODÉLISATION ET MÉTHODES DE TRAVAIL")

    h2(doc, "2.1 Méthodologie adoptée")
    para(doc,
         "Le développement de DeforestWatch-DRC a suivi une démarche itérative "
         "combinant deux volets complémentaires. Le premier volet, relevant du génie "
         "logiciel, a consisté à concevoir une architecture en couches découplées et à "
         "l'implémenter progressivement : collecte et abstraction des sources de "
         "données, prétraitement, modèles, API sécurisée, puis interfaces de "
         "restitution. Le second volet, relevant de la Data Science, a suivi la "
         "démarche classique en six étapes : compréhension du problème, acquisition et "
         "préparation des données, exploration, modélisation, évaluation comparée, "
         "puis intégration des résultats dans l'application.")
    para(doc,
         "Un choix méthodologique structurant mérite d'être explicité d'emblée : le "
         "projet fonctionne selon deux modes de données interchangeables. Une couche "
         "d'abstraction des sources expose une interface unique derrière laquelle "
         "coexistent une source synthétique — qui génère des données satellitaires "
         "simulées mais réalistes, reproduisant l'avancée d'un front agricole depuis "
         "les villages et les routes de la zone d'étude — et une source réelle, qui lit "
         "des images GeoTIFF déposées dans le répertoire de données brutes. La source "
         "active est résolue automatiquement et peut être basculée à chaud, sans "
         "modification de code. Ce dispositif a permis de développer, tester et valider "
         "la chaîne complète de bout en bout en mode démonstration, tout en préparant "
         "le passage aux images réelles Sentinel-2, dont un script d'export dédié "
         "automatise la collecte depuis Google Earth Engine.")

    h2(doc, "2.2 Architecture générale du système")
    para(doc,
         "DeforestWatch-DRC repose sur une architecture en quatre couches. La couche "
         "cliente comprend un tableau de bord analytique développé avec Streamlit "
         "(connexion sécurisée, indicateurs, cartes, alertes, back-office "
         "administrateur) et un frontend web grand public développé avec React, qui "
         "présente le projet et anime un time-lapse de la déforestation 2015-2025. La "
         "couche applicative est constituée d'une API REST développée avec FastAPI, "
         "organisée en modules de routes par domaine fonctionnel : authentification, "
         "statistiques, cartes, prédictions, alertes, impact carbone, radar et "
         "administration. La couche de persistance repose sur PostgreSQL, interrogée "
         "via l'ORM SQLAlchemy, avec un repli automatique sur SQLite garantissant le "
         "démarrage de l'application en toute circonstance. Enfin, la couche Data "
         "Science regroupe les modules de collecte, de prétraitement, les modèles "
         "d'apprentissage automatique sérialisés au format joblib et les moteurs "
         "d'analyse dérivés (alertes, carbone, radar).")
    figure_placeholder(doc, "Figure 1 — Architecture générale de DeforestWatch-DRC",
                       "schéma des quatre couches : clientes (Streamlit, React), API "
                       "FastAPI, persistance PostgreSQL/SQLite, module Data Science")
    para(doc,
         "Ce choix architectural sépare clairement les responsabilités : le tableau de "
         "bord consomme directement la couche de données pour la visualisation "
         "interactive, tout en s'appuyant sur l'API pour l'authentification et "
         "l'administration ; le frontend public ne consomme que les routes ouvertes de "
         "l'API ; et la couche Data Science reste indépendante des interfaces, ce qui "
         "permet de ré-entraîner ou de remplacer les modèles sans toucher au reste du "
         "système.")

    h2(doc, "2.3 Modélisation UML")
    para(doc,
         "La modélisation du système a suivi une logique orientée objets et composants "
         "logiciels, adaptée à une application web moderne structurée autour d'une API "
         "REST. Quatre diagrammes ont été retenus pour représenter respectivement les "
         "acteurs et fonctionnalités du système, la structure des données persistées, "
         "la dynamique du scénario de sécurité le plus critique, et le déroulement de "
         "la chaîne de traitement analytique.")
    h3(doc, "2.3.1 Diagramme de cas d'utilisation")
    para(doc,
         "Le système met en relation trois acteurs principaux. Le visiteur ou citoyen "
         "consulte librement les statistiques publiques de déforestation, les cartes de "
         "couverture et de risque, et peut signaler une déforestation suspectée par un "
         "formulaire géolocalisé, sans création de compte. L'analyste authentifié — "
         "gestionnaire forestier, agent provincial ou chercheur — accède après une "
         "connexion à deux facteurs au tableau de bord complet : indicateurs annuels, "
         "analyse par année, comparaisons, matrice de confusion des modèles, carte de "
         "risque et alertes par secteur. L'administrateur dispose en outre de la "
         "gestion des comptes utilisateurs, de la consultation des journaux d'activité "
         "de l'API, de la bascule de la source de données et de l'envoi du digest "
         "d'alertes par courrier électronique. Le module de prédiction par "
         "apprentissage automatique constitue un cas d'utilisation transversal qui "
         "alimente à la fois les cartes consultées par les utilisateurs et les alertes "
         "notifiées par l'administrateur.")
    figure_placeholder(doc, "Figure 2 — Diagramme de cas d'utilisation",
                       "diagramme UML : acteurs visiteur/citoyen, analyste authentifié, "
                       "administrateur ; module IA transversal")
    h3(doc, "2.3.2 Diagramme de classes")
    para(doc,
         "Le modèle de données persistées repose sur six entités principales, "
         "correspondant chacune à une table relationnelle. L'entité Utilisateur "
         "centralise l'identification (adresse électronique unique), le mot de passe "
         "haché, le secret de l'authentification à deux facteurs et le rôle, "
         "administrateur ou utilisateur, distingué par un attribut plutôt que par une "
         "hiérarchie de classes. L'entité Signalement enregistre les déclarations "
         "citoyennes de déforestation, géolocalisées et dotées d'un statut de "
         "traitement. L'entité Résultat d'analyse historise les statistiques annuelles "
         "calculées, l'entité Prédiction les scores de risque géolocalisés, et "
         "l'entité Registre de modèles les versions des modèles entraînés. Enfin, "
         "l'entité Journal API trace de manière transversale chaque requête traitée "
         "par le serveur, à des fins d'audit. Les artefacts volumineux — modèles "
         "sérialisés, jeux de données, rapport de métriques — sont quant à eux stockés "
         "sur le système de fichiers, en dehors de la base.")
    figure_placeholder(doc, "Figure 3 — Diagramme de classes",
                       "diagramme UML des entités : Utilisateur, Signalement, Résultat "
                       "d'analyse, Prédiction, Registre de modèles, Journal API")
    h3(doc, "2.3.3 Diagramme de séquence — authentification à deux facteurs")
    para(doc,
         "Le diagramme de séquence retenu illustre le scénario de sécurité le plus "
         "critique du système : l'inscription puis la connexion avec second facteur. À "
         "l'inscription, l'API vérifie l'unicité de l'adresse électronique, hache le "
         "mot de passe avec bcrypt, génère un secret TOTP et retourne l'URI de "
         "provisionnement que l'utilisateur enregistre dans une application "
         "d'authentification compatible. À la connexion, l'API vérifie le mot de passe "
         "par comparaison de hachés puis émet deux jetons JWT signés : un jeton "
         "d'accès de courte durée et un jeton de rafraîchissement de sept jours. La "
         "vérification du code à usage unique, calculé par l'application "
         "d'authentification et validé côté serveur avec une fenêtre de tolérance, "
         "complète le second facteur. Toute route protégée vérifie enfin, par une "
         "dépendance dédiée, la validité du jeton d'accès, l'existence et l'activité "
         "du compte, et le cas échéant le rôle administrateur requis.")
    figure_placeholder(doc, "Figure 4 — Diagramme de séquence du processus "
                            "d'authentification à deux facteurs",
                       "séquence UML : inscription (bcrypt + secret TOTP), connexion "
                       "(JWT access + refresh), vérification OTP, accès à une route protégée")
    h3(doc, "2.3.4 Diagramme d'activité — chaîne de traitement et prédiction")
    para(doc,
         "Le diagramme d'activité décrit le déroulement de la chaîne analytique "
         "complète. Le système résout d'abord la source de données active : si des "
         "images réelles sont présentes et que le mode réel est demandé, elles sont "
         "utilisées ; dans le cas contraire, un repli transparent sur la source "
         "synthétique garantit la continuité de service. Les composites annuels sont "
         "ensuite soumis au masquage des nuages, au calcul des indices spectraux et à "
         "l'extraction des variables, puis classifiés pixel par pixel. De la série de "
         "cartes de couverture ainsi obtenue découlent les statistiques annuelles de "
         "perte forestière, la détection d'alertes par secteur, l'estimation des "
         "émissions de CO2 et la carte de risque de déforestation future, restituées "
         "aux interfaces sous forme d'images et de flux JSON.")
    figure_placeholder(doc, "Figure 5 — Diagramme d'activité de la chaîne de "
                            "traitement et de prédiction",
                       "activité UML : résolution de la source (réelle/démo), masquage, "
                       "indices, classification, statistiques, alertes, carbone, risque")

    h2(doc, "2.4 Zone d'étude, données et base de données")
    para(doc,
         "La zone d'étude couvre un carré d'environ cinquante kilomètres de côté "
         "centré sur la ville d'Inongo (1,95° de latitude sud, 18,27° de longitude "
         "est), chef-lieu de la province du Mai-Ndombe, soit une superficie de l'ordre "
         "de 250 000 hectares sur l'un des fronts de déforestation les plus actifs de "
         "la forêt équatoriale congolaise. La zone est discrétisée en une grille de "
         "256 par 256 cellules, chaque cellule représentant environ 3,8 hectares, et "
         "la période d'analyse s'étend de 2015 à 2025, à raison d'un composite par "
         "année. Cinq classes de couverture du sol sont distinguées : forêt dense, "
         "forêt dégradée, agriculture et sol nu, eau, et zone urbaine ou bâtie.")
    table(doc,
          ["Source", "Description", "Résolution", "Couverture"],
          [
              ["Sentinel-2 (ESA)", "Images multispectrales, 6 bandes retenues "
               "(B2, B3, B4, B8, B11, B12)", "10 m", "2015-présent"],
              ["Sentinel-1 (ESA)", "Radar SAR, rétrodiffusion VV/VH, pénètre les nuages",
               "10 m", "2015-présent"],
              ["Landsat 8/9 (NASA/USGS)", "Images multispectrales complémentaires",
               "30 m", "2013-présent"],
              ["Hansen Global Forest Change", "Perte forestière annuelle (référence "
               "d'étiquetage)", "30 m", "2000-2023"],
              ["SRTM (NASA)", "Modèle numérique de terrain : altitude, pente, exposition",
               "30 m", "Globale"],
              ["OpenWeatherMap", "Précipitations et températures", "—", "Temps réel"],
          ],
          caption="Tableau 1 — Sources de données satellitaires et auxiliaires")
    para(doc,
         "Le choix d'une base de données relationnelle répond aux besoins de la couche "
         "applicative : intégrité des comptes utilisateurs, traçabilité des "
         "signalements et des journaux, et historisation des résultats. Six tables "
         "structurent la base ; l'ORM SQLAlchemy en abstrait l'accès et permet le "
         "repli transparent de PostgreSQL vers SQLite en environnement de "
         "démonstration ou d'intégration continue.")
    table(doc,
          ["Table", "Rôle"],
          [
              ["users", "Comptes utilisateurs : email unique, mot de passe haché "
               "(bcrypt), secret TOTP 2FA, rôle (admin/user), état d'activité."],
              ["reports", "Signalements citoyens de déforestation : latitude, "
               "longitude, description, auteur facultatif, sévérité et statut."],
              ["analysis_results", "Historisation des statistiques annuelles : forêt "
               "totale, perte, taux, modèle utilisé."],
              ["predictions", "Scores de risque géolocalisés produits par le module "
               "de prédiction."],
              ["model_registry", "Registre des versions de modèles entraînés."],
              ["api_logs", "Journal transversal des requêtes API : route, méthode, "
               "code de statut, horodatage."],
          ],
          caption="Tableau 2 — Tables relationnelles de la base de données et rôle")

    h2(doc, "2.5 Prétraitement et constitution des jeux de données")
    para(doc,
         "Le prétraitement des images suit la chaîne standard de la télédétection "
         "optique en zone équatoriale. Les pixels invalides — nuages, ombres, neige et "
         "absences de données — sont d'abord masqués à partir de la bande de "
         "classification de scène (SCL) de Sentinel-2, et les images dont moins de "
         "trente pour cent des pixels sont exploitables sont écartées. Les images "
         "restantes d'une même année sont ensuite composées en une mosaïque médiane "
         "calculée sur la saison sèche (juin à septembre), période de moindre "
         "nébulosité, ce qui produit un composite annuel à six bandes par pixel. "
         "Quatre indices spectraux sont alors calculés de manière vectorisée :")
    formula(doc, "NDVI = (NIR − Rouge) / (NIR + Rouge)")
    formula(doc, "EVI = 2,5 × (NIR − Rouge) / (NIR + 6×Rouge − 7,5×Bleu + 1)")
    formula(doc, "NDWI = (Vert − NIR) / (Vert + NIR)")
    formula(doc, "NBR = (NIR − SWIR2) / (NIR + SWIR2)")
    para(doc,
         "Chaque pixel est finalement décrit par treize variables : les six bandes "
         "spectrales, les quatre indices et trois variables topographiques dérivées du "
         "modèle numérique de terrain SRTM (altitude, pente, exposition). Un pipeline "
         "PySpark assure le nettoyage et la mise à l'échelle de ces variables en "
         "environnement distribué, avec un repli pandas équivalent lorsque Spark n'est "
         "pas disponible, ce qui prépare le passage à des zones d'étude plus vastes.")
    para(doc,
         "Deux jeux de données d'apprentissage sont construits à partir de la source "
         "active. Le jeu pixel, destiné aux modèles Random Forest et XGBoost, associe "
         "à chacun des 65 536 pixels de la grille son vecteur de treize variables et "
         "sa classe de couverture. Le jeu tuiles, destiné au U-Net, découpe la zone en "
         "96 tuiles de 128 par 128 pixels à six bandes normalisées, accompagnées de "
         "leurs masques de classes. La division entre apprentissage, validation et "
         "test vise des proportions de 70, 15 et 15 pour cent ; pour le jeu pixel, "
         "elle est réalisée par blocs spatiaux — la grille est découpée en 64 blocs "
         "dont chacun est affecté en entier à l'un des trois ensembles — afin d'éviter "
         "la fuite d'information géographique induite par l'autocorrélation spatiale "
         "des pixels voisins. L'affectation aléatoire des blocs, contrôlée par une "
         "graine fixe garantissant la reproductibilité, a produit dans l'exécution de "
         "référence 43 008 pixels d'apprentissage, 16 384 de validation et 6 144 de "
         "test. Aucune normalisation des variables n'est appliquée pour les modèles à "
         "base d'arbres, dont les divisions par seuils sont insensibles à l'échelle ; "
         "les bandes sont en revanche normalisées pour le réseau de neurones.")

    h2(doc, "2.6 Modélisation de la classification de la couverture du sol")
    h3(doc, "2.6.1 Formulation du problème")
    para(doc,
         "La détection de la déforestation est formulée comme un problème de "
         "classification supervisée multi-classes : à chaque pixel est associée l'une "
         "des cinq classes de couverture du sol, et la perte forestière annuelle se "
         "déduit de la comparaison des cartes classifiées successives, les classes "
         "forêt dense et forêt dégradée étant comptabilisées comme couvert forestier. "
         "Deux formulations complémentaires sont mises en œuvre : une classification "
         "pixel à pixel opérant sur les vecteurs de treize variables, et une "
         "segmentation sémantique opérant sur les tuiles d'images, qui exploite le "
         "contexte spatial. Un troisième problème, binaire, est traité séparément : la "
         "prédiction du risque qu'un pixel encore forestier soit déforesté à l'horizon "
         "suivant (section 2.7).")
    h3(doc, "2.6.2 Fondement mathématique de la forêt aléatoire")
    para(doc,
         "Une forêt aléatoire de classification construit un ensemble de B arbres de "
         "décision, chacun entraîné sur un échantillon obtenu par tirage aléatoire "
         "avec remise (bootstrap) à partir du jeu d'apprentissage, en ne considérant à "
         "chaque division qu'un sous-ensemble aléatoire des variables explicatives. La "
         "prédiction finale pour une observation x est la classe majoritaire parmi les "
         "prédictions individuelles des arbres :")
    formula(doc, "f̂(x) = mode{ T1(x), T2(x), …, TB(x) }")
    para(doc,
         "où Tb(x) désigne la classe prédite par l'arbre b. Ce mécanisme d'agrégation "
         "réduit la variance du modèle par rapport à un arbre unique, sujet au "
         "surapprentissage. L'implémentation retenue utilise B = 200 arbres d'une "
         "profondeur maximale de 15, avec une graine aléatoire fixe garantissant la "
         "reproductibilité. L'importance de chaque variable peut être estimée par la "
         "réduction moyenne d'impureté qu'elle procure sur l'ensemble des divisions où "
         "elle intervient, ce qui fournit une lecture interprétable de la contribution "
         "des bandes, des indices et de la topographie à la décision.")
    h3(doc, "2.6.3 Fondement mathématique du gradient boosting (XGBoost)")
    para(doc,
         "Le gradient boosting construit le classifieur de manière additive et "
         "séquentielle : à chaque itération m, un nouvel arbre hm est ajusté sur le "
         "gradient de la fonction de perte évaluée sur les prédictions courantes, puis "
         "ajouté au modèle avec un taux d'apprentissage η qui contrôle la vitesse de "
         "convergence :")
    formula(doc, "Fm(x) = Fm−1(x) + η × hm(x)")
    para(doc,
         "L'implémentation XGBoost y ajoute une régularisation explicite de la "
         "complexité des arbres et des optimisations de calcul. La configuration "
         "retenue utilise 200 arbres de profondeur maximale 10, un taux "
         "d'apprentissage de 0,1 et un sous-échantillonnage de 80 pour cent des "
         "observations et des variables à chaque arbre, qui limite le "
         "surapprentissage. En l'absence de la bibliothèque XGBoost, le système se "
         "replie automatiquement sur l'implémentation de gradient boosting de "
         "scikit-learn, au prix de performances moindres mais sans rupture de service.")
    h3(doc, "2.6.4 Architecture U-Net pour la segmentation sémantique")
    para(doc,
         "Le U-Net implémenté prend en entrée des tuiles de 128 par 128 pixels à six "
         "bandes et produit en sortie une carte de probabilités par classe à la même "
         "résolution. L'encodeur enchaîne quatre niveaux de double convolution "
         "(32, 64, 128 puis 256 filtres) séparés par des sous-échantillonnages, "
         "jusqu'à un goulot de 512 filtres ; le décodeur remonte symétriquement par "
         "convolutions transposées, chaque niveau étant concaténé à la sortie "
         "correspondante de l'encodeur par une connexion de saut. L'entraînement "
         "minimise l'entropie croisée catégorielle avec l'optimiseur Adam. Un choix "
         "d'ingénierie important a été fait pour la robustesse du système : lorsque "
         "TensorFlow n'est pas disponible dans l'environnement d'exécution, une "
         "implémentation de repli fondée sur l'affectation au centroïde spectral le "
         "plus proche offre la même interface d'entraînement et de prédiction, ce qui "
         "garantit que la chaîne complète et les interfaces restent fonctionnelles.")
    h3(doc, "2.6.5 Comparaison de modèles et justification du choix")
    best = m["comparison"][0]
    rows = []
    for c in m["comparison"]:
        name = c["Modèle"]
        if name == m.get("best_model"):
            name += " (retenu)"
        if c["Modèle"] == "U-Net":
            name = "U-Net (repli centroïdes)"
        rows.append([name, fr(c["Accuracy"]), fr(c["Precision"]),
                     fr(c["Recall"]), fr(c["F1-macro"]), fr(c["Mean IoU"])])
    para(doc,
         "Conformément à l'exigence de comparaison et de justification méthodologique "
         "attendue pour un projet de Data Science, les trois modèles ont été entraînés "
         "et évalués selon un protocole strictement identique : mêmes jeux de données, "
         "même découpage spatial, mêmes métriques — exactitude, précision et rappel "
         "macro, F1-macro, et IoU moyen défini comme la moyenne par classe du rapport "
         "de l'intersection à l'union entre prédiction et référence. Les résultats "
         "détaillés sont présentés et discutés au chapitre 3 ; le tableau ci-dessous "
         "en donne la synthèse pour l'exécution de référence.")
    table(doc,
          ["Modèle", "Exactitude", "Précision macro", "Rappel macro", "F1-macro",
           "IoU moyen"],
          rows,
          caption="Tableau 3 — Comparaison des modèles de classification "
                  "(protocole identique, mêmes données)")
    para(doc,
         f"Le modèle {best['Modèle']} a été retenu comme modèle de production : il "
         "domine la comparaison sur l'ensemble des métriques tout en conservant un "
         "coût d'entraînement et d'inférence modéré, compatible avec un "
         "ré-entraînement régulier sur des données nouvelles. La forêt aléatoire, aux "
         "performances très proches, est conservée comme modèle de référence "
         "interprétable. La position du U-Net dans ce classement doit être lue avec "
         "précaution : dans l'exécution de référence, TensorFlow n'étant pas installé, "
         "c'est l'implémentation de repli par centroïdes spectraux qui a été évaluée "
         "sous ce nom, et non le réseau complet ; ce point est discuté avec "
         "transparence au chapitre 3.")

    h2(doc, "2.7 Prédiction du risque et modules d'analyse dérivés")
    risk = m.get("risk_predictor") or REFERENCE_METRICS["risk_predictor"]
    para(doc,
         "Le module de prédiction du risque formule un problème binaire : pour chaque "
         "pixel encore forestier, prédire s'il sera déforesté à l'horizon temporel "
         "suivant. Conformément au constat empirique d'une déforestation pilotée par "
         "l'accessibilité, six variables explicatives sont retenues : la distance à la "
         "route la plus proche, la distance au village le plus proche, la distance au "
         "front de déforestation existant, la pente, l'altitude et le taux de "
         "déforestation du voisinage immédiat. Un classifieur de gradient boosting est "
         "entraîné sur les pixels forestiers de l'avant-dernière année, étiquetés "
         "selon leur devenir l'année suivante ; dans l'exécution de référence, il "
         f"atteint une exactitude d'apprentissage de {fr(risk['train_accuracy'])} avec "
         f"{fr_int(risk['n_positive'])} pixels positifs. La probabilité prédite, "
         "ramenée sur une échelle de 0 à 100, produit la carte de risque exposée aux "
         "interfaces. Il convient de préciser que la carte servie en l'état par l'API "
         "repose sur une heuristique de distance au front calculée sur la série "
         "active, le modèle binaire entraîné étant sérialisé séparément ; leur "
         "unification est identifiée comme un axe d'amélioration.")
    para(doc,
         "Trois modules d'analyse traduisent ensuite les cartes en indicateurs "
         "actionnables. Le moteur d'alertes découpe la zone en 64 secteurs et compare, "
         "d'une année à l'autre, la surface forestière de chaque secteur : toute perte "
         "supérieure à un seuil de 400 hectares déclenche une alerte géolocalisée au "
         "centre du secteur, classée modérée, élevée ou critique selon que la perte "
         "dépasse une fois, une fois et demie ou trois fois le seuil ; un digest peut "
         "être expédié par courrier électronique aux gestionnaires. Le module carbone "
         "convertit la perte forestière en émissions selon la relation :")
    formula(doc, "E(CO2) = S × AGB × CF × (44 / 12)")
    para(doc,
         "où S est la surface déforestée en hectares, AGB la biomasse aérienne moyenne "
         "d'une forêt tropicale humide du Bassin du Congo, fixée à 310 tonnes par "
         "hectare selon la valeur médiane de la littérature, CF la fraction de carbone "
         "de la biomasse (0,47 selon les lignes directrices du GIEC) et 44/12 le "
         "rapport des masses molaires du CO2 et du carbone, soit environ 534 tonnes de "
         "CO2 par hectare détruit. Des équivalences parlantes (voitures, arbres) "
         "accompagnent la restitution, afin de parler le langage de la finance climat. "
         "Enfin, le module radar exploite les bandes de rétrodiffusion VV et VH de "
         "Sentinel-1, insensibles à la nébulosité, pour quantifier la part de la zone "
         "observable au radar lorsque l'optique est aveuglée par les nuages, atout "
         "décisif en zone équatoriale.")

    h2(doc, "2.8 Sécurité et authentification")
    para(doc,
         "L'authentification des utilisateurs repose sur trois mécanismes "
         "complémentaires. Les mots de passe ne sont jamais stockés en clair : ils "
         "sont hachés au moyen de la bibliothèque bcrypt avant insertion en base, la "
         "vérification s'effectuant par comparaison de hachés. Les sessions reposent "
         "sur des jetons JWT signés selon l'algorithme HS256 : un jeton d'accès d'une "
         "durée de vie de soixante minutes et un jeton de rafraîchissement de sept "
         "jours, ce dernier permettant de renouveler l'accès sans ressaisie du mot de "
         "passe. Un second facteur d'authentification est implémenté selon le "
         "standard TOTP au moyen de la bibliothèque PyOTP : un secret est généré à "
         "l'inscription et restitué sous forme d'URI de provisionnement compatible "
         "avec les applications d'authentification usuelles, et le code à usage "
         "unique est vérifié côté serveur avec une fenêtre de tolérance d'un "
         "intervalle. L'accès aux ressources sensibles — gestion des utilisateurs, "
         "journaux, bascule de source, notifications — est restreint au rôle "
         "administrateur par une dépendance dédiée, et chaque requête est journalisée "
         "en base à des fins d'audit.")
    para(doc,
         "Cette implémentation constitue une base de sécurité solide pour un projet "
         "académique, mais présente des limites qu'il convient de mentionner avec "
         "transparence. La politique CORS de l'API autorise en l'état toutes les "
         "origines, configuration commode en développement mais à restreindre par "
         "liste blanche avant toute mise en production. Le secret de signature des "
         "jetons JWT est défini par une valeur par défaut explicite dans la "
         "configuration d'exemple, à remplacer impérativement par un secret robuste "
         "en production. Enfin, le mode démonstration provisionne un compte "
         "administrateur par défaut et le tableau de bord accepte, dans ce mode, un "
         "code à usage unique fixe ; ces facilités de démonstration doivent être "
         "désactivées hors de ce cadre. Ces éléments sont repris dans la section "
         "consacrée aux limites de l'étude.")

    h2(doc, "2.9 Outils et techniques")
    para(doc,
         "Le développement s'appuie sur le langage Python 3.11. Le backend utilise le "
         "framework FastAPI, retenu pour ses performances asynchrones, sa "
         "documentation interactive générée automatiquement et la validation de "
         "données par Pydantic ; la persistance repose sur PostgreSQL via l'ORM "
         "SQLAlchemy, avec repli SQLite. La modélisation utilise scikit-learn "
         "(RandomForestClassifier, métriques), XGBoost et TensorFlow/Keras pour le "
         "U-Net, les modèles étant sérialisés avec joblib ; le prétraitement "
         "distribué s'appuie sur PySpark et la manipulation d'images satellitaires "
         "sur rasterio et l'API Python de Google Earth Engine. Les interfaces "
         "utilisent Streamlit et Plotly pour le tableau de bord analytique, et React "
         "avec Vite et Tailwind CSS pour le frontend public. La sécurité repose sur "
         "bcrypt, PyJWT et PyOTP. L'ensemble est conteneurisé avec Docker et "
         "docker-compose, versionné avec Git, et couvert par une suite d'environ "
         "cinquante tests pytest répartis en six modules (prétraitement, modèles, "
         "API, alertes, impact, sources de données), exécutée à chaque modification "
         "par une chaîne d'intégration continue GitHub Actions qui y ajoute une "
         "analyse statique et la construction du frontend.")


def _chapter3(doc, m, yearly, alerts_summary, carbon_summary):
    h1(doc, "3. RÉSULTATS, DISCUSSION ET CONCLUSION")

    h2(doc, "3.1 Présentation des résultats")
    para(doc,
         "Cette section présente les résultats obtenus à l'issue de l'exécution de "
         "référence de la chaîne complète — génération des données, entraînement et "
         "évaluation des modèles décrits au chapitre précédent. Une précision "
         "méthodologique s'impose d'emblée : cette exécution a été conduite en mode "
         "démonstration, sur des données synthétiques réalistes reproduisant la "
         "dynamique d'un front de déforestation agricole progressant depuis les "
         "villages et les routes de la zone d'étude. Les chiffres présentés valident "
         "donc la chaîne de traitement de bout en bout et la cohérence méthodologique "
         "du dispositif, mais ne décrivent pas l'état réel de la forêt du Mai-Ndombe ; "
         "leur confirmation sur images Sentinel-2 réelles constitue la première "
         "perspective de ce travail.")

    h3(doc, "3.1.1 Dynamique de la couverture forestière simulée")
    first, last = yearly[0], yearly[-1]
    total_loss = sum(s["forest_loss_ha"] for s in yearly)
    para(doc,
         "Le scénario simulé fait passer le couvert forestier de la zone d'étude de "
         f"{fr_int(first['total_forest_ha'])} hectares en {first['year']} à "
         f"{fr_int(last['total_forest_ha'])} hectares en {last['year']}, soit une "
         f"perte cumulée d'environ {fr_int(total_loss)} hectares. Ce scénario, "
         "volontairement accéléré par rapport aux taux observés dans la région, joue "
         "le rôle d'un test de charge : il garantit que chaque maillon — "
         "classification, statistiques, alertes, carbone, risque — réagit correctement "
         "à une dynamique marquée et produit des indicateurs cohérents entre eux.")
    table(doc,
          ["Année", "Forêt totale (ha)", "Perte annuelle (ha)", "Taux de perte (%)"],
          [[s["year"], fr_int(s["total_forest_ha"]), fr_int(s["forest_loss_ha"]),
            fr(s["deforestation_rate"], 2)] for s in yearly],
          caption="Tableau 4 — Évolution simulée de la couverture forestière "
                  "(2015-2025, mode démonstration)")

    h3(doc, "3.1.2 Performance des modèles de classification")
    best = m["comparison"][0]
    rf = next(c for c in m["comparison"] if c["Modèle"] == "RandomForest")
    unet = next(c for c in m["comparison"] if c["Modèle"] == "U-Net")
    per_model = m.get("per_model", {})
    xgb_pc = (per_model.get("XGBoost", {}) or {}).get("f1_per_class",
              {"Forêt dense": 0.9151, "Forêt dégradée": 0.7670,
               "Agriculture / Sol nu": 0.9999})
    para(doc,
         f"Le modèle {best['Modèle']} obtient les meilleures performances sur "
         f"l'ensemble de test spatialement isolé : exactitude de {fr(best['Accuracy'])}, "
         f"F1-macro de {fr(best['F1-macro'])} et IoU moyen de {fr(best['Mean IoU'])}. "
         f"La forêt aléatoire le suit de très près (F1-macro de {fr(rf['F1-macro'])}, "
         f"IoU moyen de {fr(rf['Mean IoU'])}), l'écart entre les deux méthodes "
         "d'ensemble restant inférieur à un point de F1. L'analyse par classe est "
         "instructive : la classe agriculture et sol nu est presque parfaitement "
         f"reconnue (F1 de {fr(xgb_pc.get('Agriculture / Sol nu', 0.9999))}), la forêt "
         f"dense l'est très bien (F1 de {fr(xgb_pc.get('Forêt dense', 0.9151))}), "
         "tandis que la forêt dégradée, classe de transition spectralement "
         f"intermédiaire, reste la plus difficile (F1 de "
         f"{fr(xgb_pc.get('Forêt dégradée', 0.7670))}). Cette hiérarchie est conforme "
         "à l'intuition physique : c'est précisément la frontière entre forêt intacte "
         "et forêt dégradée qui concentre l'ambiguïté spectrale.")
    para(doc,
         "Deux observations méthodologiques doivent accompagner ces chiffres. "
         "Premièrement, le découpage spatial par blocs, retenu pour éviter la "
         "surestimation des performances par autocorrélation spatiale, a eu pour effet "
         "collatéral qu'aucun pixel des classes rares eau et zone bâtie n'est présent "
         "dans l'ensemble de test de l'exécution de référence ; les métriques macro "
         "sont donc calculées sur les trois classes observées, et la performance sur "
         "les classes rares reste à établir. Deuxièmement, la ligne U-Net du "
         "comparatif correspond, dans cette exécution, à l'implémentation de repli par "
         f"centroïdes spectraux (F1-macro de {fr(unet['F1-macro'])}), TensorFlow "
         "n'étant pas installé dans l'environnement de référence ; elle fournit un "
         "plancher de performance honnête pour une méthode purement spectrale sans "
         "apprentissage de contexte, mais ne saurait être interprétée comme "
         "l'évaluation du réseau complet décrit en 2.6.4.")
    risk = m.get("risk_predictor") or REFERENCE_METRICS["risk_predictor"]
    para(doc,
         "Le modèle de risque binaire atteint pour sa part une exactitude "
         f"d'apprentissage de {fr(risk['train_accuracy'])} sur "
         f"{fr_int(risk['n_positive'])} pixels positifs, valeur mesurée en "
         "apprentissage et non sur un ensemble de test isolé, ce qui est signalé "
         "comme une limite au titre de la rigueur d'évaluation.")

    h3(doc, "3.1.3 Alertes, impact carbone et apport du radar")
    sev = alerts_summary.get("by_severity", {})
    para(doc,
         "Sur la série simulée, le moteur d'alertes détecte "
         f"{fr_int(alerts_summary.get('total_alerts', 215))} dépassements de seuil "
         f"sectoriels sur la période, dont {fr_int(sev.get('modérée', 62))} de "
         f"sévérité modérée, {fr_int(sev.get('élevée', 152))} de sévérité élevée et "
         f"{fr_int(sev.get('critique', 1))} de sévérité critique, l'année la plus "
         f"touchée étant {alerts_summary.get('worst_year', 2019)}. Chaque alerte est "
         "géolocalisée au centre de son secteur et exploitable directement par une "
         "équipe de terrain. Le module carbone évalue les émissions associées au "
         f"scénario simulé à environ {fr(carbon_summary.get('total_co2_mt', 95.577), 1)} "
         "mégatonnes de CO2 cumulées sur la période, chiffre dont l'ordre de grandeur "
         "illustre l'enjeu financier des paiements aux résultats dans une province "
         "pilote REDD+. Le module radar, enfin, quantifie la part de la zone restant "
         "observable par Sentinel-1 lorsque la couverture nuageuse aveugle l'optique, "
         "et confirme l'intérêt d'une fusion optique-radar pour la surveillance "
         "opérationnelle en zone équatoriale.")

    h2(doc, "3.2 Discussion des résultats")
    h3(doc, "3.2.1 Mise en perspective par rapport à la littérature")
    para(doc,
         "La hiérarchie observée entre les modèles est cohérente avec la littérature "
         "de télédétection : à volume de données annotées modéré, les méthodes "
         "d'ensemble à base d'arbres opérant sur des variables spectrales et "
         "topographiques bien construites atteignent des performances de premier plan, "
         "l'avantage des approches profondes ne se matérialisant qu'avec des volumes "
         "d'annotation nettement supérieurs. Le niveau élevé des métriques obtenues "
         "doit néanmoins être rapporté à la nature synthétique des données de "
         "l'exécution de référence : les classes y sont spectralement plus séparables "
         "que dans des images réelles, où les mélanges de pixels, les variations "
         "atmosphériques résiduelles et la continuité réelle du gradient de "
         "dégradation forestière réduiront mécaniquement les scores. La littérature "
         "empirique sur le Bassin du Congo laisse en particulier attendre une "
         "difficulté accrue sur la classe forêt dégradée, déjà identifiée ici comme "
         "la plus fragile.")
    h3(doc, "3.2.2 Implications pratiques")
    para(doc,
         "Sur le plan pratique, l'architecture d'alertes sectorielles fournit un "
         "format directement actionnable pour des gardes forestiers ou des agents "
         "provinciaux : une liste courte de secteurs géolocalisés, hiérarchisés par "
         "sévérité, plutôt qu'une carte continue difficile à traduire en tournées de "
         "terrain. Le choix de variables d'accessibilité pour le modèle de risque, "
         "validé par son exactitude d'apprentissage élevée, confirme opérationnellement "
         "que la surveillance doit se concentrer sur les lisières proches des routes "
         "et des villages, conformément au constat de Tyukavina et al. (2018) sur la "
         "prédominance du défrichement de petite échelle. Enfin, la traduction "
         "systématique des pertes en tonnes de CO2 met les résultats techniques au "
         "format attendu par les mécanismes de financement climatique, ce qui "
         "constitue l'une des plus-values distinctives de la plateforme par rapport "
         "aux outils de constat existants.")
    h3(doc, "3.2.3 Points forts et faiblesses du travail")
    para(doc,
         "Ce travail présente plusieurs points forts. La chaîne est complète et "
         "fonctionnelle de bout en bout, de la collecte satellitaire à la restitution "
         "décisionnelle, ce qui est rarement atteint dans un projet académique. La "
         "couche d'abstraction des sources de données permet de basculer des données "
         "de démonstration aux images réelles sans modification de code, et chaque "
         "composant critique dispose d'un repli garantissant la continuité de service. "
         "La démarche d'évaluation est rigoureuse — protocole identique, découpage "
         "spatial anti-fuite, métriques multiples — et la sécurité dépasse le standard "
         "habituel des prototypes, avec une authentification à deux facteurs "
         "effectivement implémentée. Enfin, le projet est testé, intégré en continu et "
         "entièrement reproductible par une seule commande.")
    para(doc,
         "Ce travail présente également des faiblesses qu'il convient de reconnaître "
         "avec la même rigueur. Les résultats chiffrés reposent sur des données "
         "synthétiques, et aucune évaluation sur images réelles n'a encore été "
         "conduite. L'ensemble de test spatial ne contient aucun pixel des classes "
         "rares, ce qui laisse leur reconnaissance non validée. Le U-Net complet n'a "
         "pas été entraîné dans l'exécution de référence, si bien que la comparaison "
         "avec les approches profondes reste à faire dans des conditions équitables. "
         "Enfin, le modèle de risque n'est évalué qu'en apprentissage, et la carte de "
         "risque servie par l'API repose encore sur une heuristique plutôt que sur le "
         "modèle entraîné.")

    h2(doc, "3.3 Limites de l'étude")
    para(doc,
         "Plusieurs limites méthodologiques et techniques doivent être explicitement "
         "mentionnées. Premièrement, les données de l'exécution de référence sont "
         "synthétiques : elles reproduisent une dynamique réaliste mais simplifiée, et "
         "l'ensemble des performances rapportées doit être confirmé sur composites "
         "Sentinel-2 réels avec une vérité terrain indépendante, le référentiel Hansen "
         "présentant lui-même des limites connues pour la dégradation forestière. "
         "Deuxièmement, le découpage spatial par blocs a exclu les classes eau et "
         "zone bâtie de l'ensemble de test, limite qui appelle une stratification "
         "spatiale tenant compte des classes rares. Troisièmement, l'évaluation du "
         "U-Net rapportée correspond à son implémentation de repli, non au réseau "
         "complet. Quatrièmement, le modèle de risque ne fait pas encore l'objet "
         "d'une validation sur ensemble isolé ni d'une calibration de ses "
         "probabilités, et n'est pas encore branché sur la carte de risque exposée. "
         "Cinquièmement, plusieurs points de sécurité doivent être durcis avant toute "
         "mise en production : restriction de la politique CORS, remplacement du "
         "secret JWT par défaut, désactivation des comptes et du code de "
         "démonstration. Enfin, la couverture nuageuse équatoriale, contournée ici "
         "par des composites de saison sèche et un module radar de démonstration, "
         "demeure la contrainte physique majeure de toute surveillance optique "
         "opérationnelle dans la région.")

    h2(doc, "3.4 Perspectives futures")
    para(doc,
         "Plusieurs axes de poursuite se dégagent de ce travail. Sur le plan des "
         "données, la priorité est la collecte des composites Sentinel-2 réels de la "
         "zone d'étude — le script d'export Google Earth Engine est déjà opérationnel "
         "— accompagnée d'une campagne de vérité terrain par points GPS, afin de "
         "ré-entraîner les modèles et de confirmer les performances en conditions "
         "réelles. Sur le plan de la modélisation, l'entraînement complet du U-Net "
         "sur tuiles réelles, la validation du modèle de risque sur ensemble isolé et "
         "son branchement sur la carte exposée, puis l'exploration de modèles "
         "spatio-temporels et de la fusion optique-radar constituent la suite "
         "naturelle. Sur le plan de la sécurité, le durcissement des points identifiés "
         "conditionne tout déploiement. Sur le plan opérationnel, enfin, l'ambition "
         "est un déploiement pilote auprès d'acteurs provinciaux du Mai-Ndombe, "
         "l'intégration du signalement citoyen dans un circuit de vérification, et "
         "l'extension progressive à d'autres provinces forestières, dans la "
         "perspective d'une contribution congolaise au système national de "
         "surveillance des forêts.")

    h2(doc, "3.5 Conclusion générale")
    para(doc,
         "Ce travail a présenté la conception et l'implémentation de "
         "DeforestWatch-DRC, une plateforme intelligente de surveillance et de "
         "prédiction de la déforestation de la forêt équatoriale du Bassin du Congo, "
         "appliquée à la province du Mai-Ndombe. L'architecture développée couvre "
         "l'intégralité de la chaîne : collecte satellitaire, prétraitement, "
         "classification de la couverture du sol, quantification annuelle de la perte "
         "forestière, prédiction du risque, alertes géolocalisées, estimation de "
         "l'impact carbone et restitution au travers d'une API sécurisée et de deux "
         "interfaces, le tout reproductible et couvert par des tests automatisés.")
    para(doc,
         "Sur le plan de la Data Science, la comparaison rigoureuse de trois modèles "
         "de classification selon un protocole identique, avec découpage spatial "
         "anti-fuite, a permis de retenir un modèle de gradient boosting atteignant "
         "un F1-macro de 0,894 sur l'exécution de référence, tout en documentant avec "
         "transparence les conditions de cette évaluation — données synthétiques, "
         "classes rares absentes du test, réseau profond évalué en repli. Cette "
         "honnêteté méthodologique, plutôt que l'affichage de scores flatteurs "
         "décontextualisés, constitue l'un des apports formateurs de ce projet.")
    para(doc,
         "Les objectifs fixés en introduction peuvent être considérés comme atteints "
         "au stade de la preuve de concept : une architecture complète a été conçue et "
         "implémentée, des modèles ont été entraînés, comparés et intégrés, et les "
         "résultats techniques sont traduits en indicateurs directement utiles aux "
         "acteurs congolais de la protection forestière. Les limites identifiées — "
         "au premier rang desquelles la confirmation sur données réelles — tracent des "
         "perspectives claires pour la poursuite de ce travail au-delà du cadre "
         "académique, au service de la souveraineté environnementale de la RDC et de "
         "sa participation à la finance climatique mondiale.")


def _bibliography(doc):
    h1(doc, "4. BIBLIOGRAPHIE ET WEBIOGRAPHIE")
    h2(doc, "Ouvrages et articles scientifiques")
    for ref in [
        'BREIMAN, L. (2001). "Random Forests." Machine Learning, Vol. 45, No. 1, '
        "pp. 5-32.",
        'CHEN, T., & GUESTRIN, C. (2016). "XGBoost: A Scalable Tree Boosting System." '
        "Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge "
        "Discovery and Data Mining, pp. 785-794.",
        'DRUSCH, M., et al. (2012). "Sentinel-2: ESA\'s Optical High-Resolution '
        'Mission for GMES Operational Services." Remote Sensing of Environment, '
        "Vol. 120, pp. 25-36.",
        "FAO (2020). Global Forest Resources Assessment 2020 — Main Report. Rome.",
        'GORELICK, N., et al. (2017). "Google Earth Engine: Planetary-scale '
        'geospatial analysis for everyone." Remote Sensing of Environment, Vol. 202, '
        "pp. 18-27.",
        'HANSEN, M. C., et al. (2013). "High-Resolution Global Maps of 21st-Century '
        'Forest Cover Change." Science, Vol. 342, No. 6160, pp. 850-853.',
        "HASTIE, T., TIBSHIRANI, R., & FRIEDMAN, J. (2009). The Elements of "
        "Statistical Learning: Data Mining, Inference, and Prediction. 2nd Edition, "
        "Springer.",
        'PEDREGOSA, F., et al. (2011). "Scikit-learn: Machine Learning in Python." '
        "Journal of Machine Learning Research, Vol. 12, pp. 2825-2830.",
        'REICHE, J., et al. (2021). "Forest disturbance alerts for the Congo Basin '
        'using Sentinel-1." Environmental Research Letters, Vol. 16, No. 2, 024005.',
        'RONNEBERGER, O., FISCHER, P., & BROX, T. (2015). "U-Net: Convolutional '
        'Networks for Biomedical Image Segmentation." Medical Image Computing and '
        "Computer-Assisted Intervention (MICCAI), pp. 234-241.",
        'TUCKER, C. J. (1979). "Red and photographic infrared linear combinations '
        'for monitoring vegetation." Remote Sensing of Environment, Vol. 8, No. 2, '
        "pp. 127-150.",
        'TYUKAVINA, A., et al. (2018). "Congo Basin forest loss dominated by '
        'increasing smallholder clearing." Science Advances, Vol. 4, No. 11, '
        "eaat2993.",
    ]:
        para(doc, ref)
    h2(doc, "Webiographie")
    for ref in [
        "Copernicus / ESA — Documentation de la mission Sentinel-2. Disponible sur : "
        "https://sentinels.copernicus.eu [Consulté en juillet 2026].",
        "FastAPI — Documentation officielle. Disponible sur : "
        "https://fastapi.tiangolo.com [Consulté en juillet 2026].",
        "Global Forest Watch — Plateforme de surveillance forestière. Disponible "
        "sur : https://www.globalforestwatch.org [Consulté en juillet 2026].",
        "Google Earth Engine — Documentation officielle. Disponible sur : "
        "https://developers.google.com/earth-engine [Consulté en juillet 2026].",
        "Scikit-learn — Documentation officielle. Disponible sur : "
        "https://scikit-learn.org/stable/ [Consulté en juillet 2026].",
        "Streamlit — Documentation officielle. Disponible sur : "
        "https://docs.streamlit.io [Consulté en juillet 2026].",
        "TensorFlow / Keras — Documentation officielle. Disponible sur : "
        "https://www.tensorflow.org [Consulté en juillet 2026].",
        "XGBoost — Documentation officielle. Disponible sur : "
        "https://xgboost.readthedocs.io [Consulté en juillet 2026].",
        "Université Protestante au Congo, Faculté des Sciences Informatiques, "
        "Commission de Coordination des Projets (2025). Guide de rédaction des "
        "monographies des projets et des mémoires. Janvier 2025.",
    ]:
        para(doc, ref)


def _annexes(doc):
    h1(doc, "5. ANNEXES")
    h2(doc, "Annexe A — Table des routes de l'API")
    table(doc,
          ["Méthode", "Route", "Rôle"],
          [
              ["GET", "/", "Métadonnées de l'application (version, mode actif)"],
              ["GET", "/health", "Vérification de l'état de santé de l'API"],
              ["POST", "/api/v1/auth/register",
               "Inscription : hachage bcrypt, génération du secret TOTP et de "
               "l'URI de provisionnement 2FA"],
              ["POST", "/api/v1/auth/login",
               "Connexion : vérification du mot de passe haché, émission des jetons "
               "JWT d'accès et de rafraîchissement"],
              ["POST", "/api/v1/auth/verify-otp",
               "Vérification du code à usage unique du second facteur"],
              ["POST", "/api/v1/auth/refresh",
               "Renouvellement du jeton d'accès à partir du jeton de rafraîchissement"],
              ["GET", "/api/v1/statistics",
               "Statistiques de déforestation par année (source active)"],
              ["GET", "/api/v1/source", "Métadonnées de la source de données active"],
              ["POST", "/api/v1/admin/source/{mode}",
               "Bascule à chaud démo/réel/auto (administrateur)"],
              ["GET", "/api/v1/maps/landcover/{année}",
               "Carte de couverture du sol d'une année, au format PNG"],
              ["GET", "/api/v1/maps/risk", "Carte de risque de déforestation, PNG"],
              ["GET", "/api/v1/predictions/{année}",
               "Synthèse des zones à risque (surface et risque moyen)"],
              ["GET", "/api/v1/alerts",
               "Alertes de déforestation détectées (filtres sévérité, année)"],
              ["GET", "/api/v1/alerts/summary", "Synthèse des alertes par sévérité"],
              ["POST", "/api/v1/reports",
               "Signalement citoyen d'une déforestation (ouvert à tous)"],
              ["GET", "/api/v1/admin/reports", "Signalements reçus (administrateur)"],
              ["GET", "/api/v1/carbon",
               "Émissions de CO2 liées à la déforestation et équivalences"],
              ["GET", "/api/v1/radar/coverage/{année}",
               "Apport du radar Sentinel-1 sous couverture nuageuse"],
              ["POST", "/api/v1/admin/notify",
               "Digest des alertes par courrier électronique (administrateur)"],
              ["GET", "/api/v1/models",
               "Comparaison des performances des modèles entraînés"],
              ["GET", "/api/v1/images/{année}", "Métadonnées du composite satellite"],
              ["GET", "/api/v1/admin/users", "Liste des utilisateurs (administrateur)"],
              ["GET", "/api/v1/admin/logs",
               "Journal des requêtes de l'API (administrateur)"],
          ],
          caption="Tableau 5 — Table synthétique des routes de l'API DeforestWatch-DRC")
    h2(doc, "Annexe B — Reproduction des résultats")
    para(doc,
         "L'ensemble des résultats présentés dans cette monographie est reproductible "
         "à partir du dépôt du projet, sans clé d'accès ni compte externe, grâce au "
         "mode démonstration : la commande make seed génère les données et entraîne "
         "les modèles (rapport de métriques dans data/processed/model_metrics.json), "
         "make api et make dashboard démarrent respectivement l'API et le tableau de "
         "bord, make test exécute la suite de tests, et make monograph régénère le "
         "présent document à partir des métriques courantes. Le passage aux données "
         "réelles s'effectue en déposant les composites GeoTIFF dans data/raw/ — "
         "collectés le cas échéant via python -m scripts.gee_export — puis en "
         "basculant le mode de données (make real).")


# ── Construction du document ──────────────────────────────────────────────
def build() -> Document:
    m = _load_metrics()
    from src.utils import synthetic
    yearly = synthetic.yearly_statistics()
    try:
        from src.analysis import alerts as alerts_engine
        alerts_summary = alerts_engine.summary()
    except Exception:  # pragma: no cover
        alerts_summary = {"total_alerts": 215,
                          "by_severity": {"modérée": 62, "élevée": 152, "critique": 1},
                          "worst_year": 2019}
    try:
        from src.analysis import carbon as carbon_engine
        carbon_summary = carbon_engine.summary()
    except Exception:  # pragma: no cover
        carbon_summary = {"total_co2_mt": 95.577}

    doc = Document()
    _base_styles(doc)
    _cover(doc)
    doc.add_page_break()
    _resume(doc, m)
    doc.add_page_break()
    _front_matter(doc)
    doc.add_page_break()
    _chapter1(doc)
    doc.add_page_break()
    _chapter2(doc, m)
    doc.add_page_break()
    _chapter3(doc, m, yearly, alerts_summary, carbon_summary)
    doc.add_page_break()
    _bibliography(doc)
    doc.add_page_break()
    _annexes(doc)
    return doc


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = build()
    doc.save(OUT_PATH)
    log.info(f"Monographie générée → {OUT_PATH} ({len(doc.paragraphs)} paragraphes)")


if __name__ == "__main__":
    main()
