"""
Génère la synthèse technique illustrée du projet : comment les images
satellites sont collectées, comment les modèles de Machine Learning
apprennent, et où chaque donnée est stockée.

Le document est complémentaire des autres livrables :
  - GUIDE.pdf    mode d'emploi (installer, lancer, utiliser)
  - mémoire      document académique complet
  - ce document  explication technique illustrée de la chaîne de traitement

Les figures viennent de scripts/figures_synthese.py et sont produites à partir
du code réel du projet.

Produit : docs/SYNTHESE_TECHNIQUE.pdf

Usage : python -m scripts.generate_synthese_technique
"""

from __future__ import annotations

from pathlib import Path

from config.settings import PROJECT_ROOT
from src.utils.logger import get_logger

log = get_logger("generate_synthese")

FIG_DIR = PROJECT_ROOT / "docs" / "figures"
OUT_PATH = PROJECT_ROOT / "docs" / "SYNTHESE_TECHNIQUE.pdf"

# Couleurs du document
GREEN = (11, 110, 45)
GREEN_LIGHT = (232, 243, 235)
INK = (24, 24, 24)
INK_SOFT = (90, 90, 90)
RULE = (205, 205, 200)
CODE_BG = (242, 244, 246)
TABLE_HEAD = (16, 120, 60)
TABLE_ALT = (245, 248, 250)


# ──────────────────────────────────────────────────────────────────────────
# Contenu du document
# ──────────────────────────────────────────────────────────────────────────
def document() -> list[tuple]:
    B: list[tuple] = []
    h1 = lambda t: B.append(("h1", t))                     # noqa: E731
    h2 = lambda t: B.append(("h2", t))                     # noqa: E731
    h3 = lambda t: B.append(("h3", t))                     # noqa: E731
    p = lambda t: B.append(("p", t))                       # noqa: E731
    ul = lambda items: B.append(("ul", items))             # noqa: E731
    ol = lambda items: B.append(("ol", items))             # noqa: E731
    code = lambda t: B.append(("code", t.strip("\n")))     # noqa: E731
    table = lambda h, r, w=None: B.append(("table", (h, r, w)))   # noqa: E731
    fig = lambda name, cap, w=180: B.append(("img", (name, cap, w)))  # noqa: E731
    note = lambda t: B.append(("note", t))                 # noqa: E731
    hr = lambda: B.append(("hr", None))                    # noqa: E731
    page = lambda: B.append(("page", None))                # noqa: E731
    cover = lambda t, s: B.append(("cover", (t, s)))       # noqa: E731

    # ══════════════════════════════════════════════════════════════════
    # Couverture
    # ══════════════════════════════════════════════════════════════════
    cover(
        "DeforestWatch-DRC",
        "Synthèse technique illustrée : de l'image satellite au modèle prédictif",
    )
    p("Ce document explique le fonctionnement interne du projet en trois temps : "
      "la collecte des images satellites, l'apprentissage automatique appliqué à "
      "ces images, et le stockage de l'ensemble des données produites.")
    p("Zone d'étude : Inongo, province du Mai-Ndombe, République Démocratique du "
      "Congo. Forêt tropicale humide équatoriale du Bassin du Congo, sur un carré "
      "d'environ 50 kilomètres de côté, observé de 2015 à 2025.")
    p("Chaque figure de ce document est produite par le code du projet lui-même "
      "(scripts/figures_synthese.py), à partir des mêmes fonctions que celles "
      "utilisées par le pipeline.")

    hr()
    h3("Sommaire")
    ol([
        "Le projet en bref",
        "La chaîne de traitement, vue d'ensemble",
        "La collecte des images satellites",
        "Du pixel brut au vecteur de caractéristiques",
        "Le Machine Learning",
        "Le stockage des données",
        "La bascule démonstration / données réelles",
        "Questions de soutenance",
        "Aide-mémoire des commandes",
    ])

    page()

    # ══════════════════════════════════════════════════════════════════
    # 1. Le projet en bref
    # ══════════════════════════════════════════════════════════════════
    h1("1. Le projet en bref")

    p("La République Démocratique du Congo abrite la deuxième plus grande forêt "
      "tropicale humide du monde. Elle recule, et le suivi de terrain seul ne "
      "permet pas de mesurer ce recul à l'échelle d'une province. Les satellites "
      "d'observation de la Terre passent au-dessus de la même zone tous les cinq "
      "jours et fournissent gratuitement leurs images.")

    p("DeforestWatch-DRC exploite ces images pour répondre à quatre questions :")
    ol([
        "Où se trouve la forêt aujourd'hui ? C'est un problème de classification "
        "d'images.",
        "Combien en a-t-on perdu, année par année ? C'est une comparaison de "
        "classifications successives.",
        "Où va-t-elle probablement disparaître dans les deux ans ? C'est un "
        "problème de prédiction.",
        "Comment rendre tout cela consultable ? C'est le rôle de l'API, du "
        "dashboard et du frontend.",
    ])

    h3("Les cinq classes de couverture du sol")
    p("Toute la chaîne repose sur ces cinq classes. Un pixel appartient toujours "
      "à une et une seule d'entre elles.")
    table(
        ["Code", "Classe", "Ce que cela représente sur le terrain"],
        [
            ["0", "Forêt dense", "Canopée fermée, forêt primaire ou secondaire mature"],
            ["1", "Forêt dégradée", "Couvert ouvert, exploitation sélective, lisière"],
            ["2", "Agriculture / sol nu", "Champ, jachère, brûlis, sol mis à nu"],
            ["3", "Eau", "Rivière, lac, zone inondée"],
            ["4", "Zone urbaine / bâti", "Village, ville, infrastructure"],
        ],
        [16, 46, 118],
    )

    p("La distinction entre forêt dense et forêt dégradée compte : la dégradation "
      "précède presque toujours la conversion complète en terre agricole. Détecter "
      "la dégradation, c'est détecter la déforestation avec un temps d'avance.")

    note("Le projet fonctionne dans deux modes. En mode démonstration, des données "
         "synthétiques réalistes permettent de tout exécuter sans compte Google "
         "Earth Engine. En mode réel, les mêmes traitements s'appliquent à de "
         "vraies images. La section 7 explique ce mécanisme.")

    page()

    # ══════════════════════════════════════════════════════════════════
    # 2. Vue d'ensemble
    # ══════════════════════════════════════════════════════════════════
    h1("2. La chaîne de traitement, vue d'ensemble")

    p("Avant d'entrer dans le détail, voici le trajet complet d'une donnée, depuis "
      "le capteur en orbite jusqu'à l'écran de l'utilisateur. Les sections "
      "suivantes reprennent chacune de ces étapes.")

    fig("12_pipeline.png", "Figure 1. Les huit étapes de la chaîne de traitement.", 150)

    p("Deux points méritent d'être notés dès maintenant.")
    p("D'abord, les étapes 1 et 2 sont séparées. Google Earth Engine calcule sur "
      "ses propres serveurs et ne renvoie pas les pixels automatiquement : il faut "
      "lancer un export explicite. C'est ce qui évite de télécharger des téraoctets "
      "d'archives.")
    p("Ensuite, à partir de l'étape 3, tout le code ignore d'où viennent les "
      "images. Qu'elles soient réelles ou simulées, elles arrivent sous la même "
      "forme : un tableau numpy de dimensions hauteur x largeur x bandes.")

    page()

    # ══════════════════════════════════════════════════════════════════
    # 3. Collecte
    # ══════════════════════════════════════════════════════════════════
    h1("3. La collecte des images satellites")

    h2("3.1 Pourquoi Google Earth Engine")

    p("Une seule scène Sentinel-2 pèse environ 700 Mo. Sur onze années et une "
      "zone de 50 kilomètres, avec un passage tous les cinq jours, l'archive "
      "complète représente plusieurs téraoctets. La télécharger serait absurde.")

    p("Google Earth Engine (GEE) héberge cette archive et permet d'y appliquer des "
      "traitements côté serveur. On décrit le calcul voulu, Google l'exécute sur "
      "son infrastructure, et seul le résultat final est exporté. Le code de "
      "collecte se trouve dans src/data/gee_collector.py.")

    h2("3.2 Sentinel-2 : la source optique principale")

    p("Sentinel-2 est une paire de satellites européens du programme Copernicus. "
      "Ils photographient la Terre dans treize bandes spectrales, à une résolution "
      "de 10 mètres pour les principales. Un pixel de l'image correspond donc à un "
      "carré de 10 mètres de côté au sol.")

    h3("Les six bandes retenues")
    table(
        ["Bande", "Longueur d'onde", "Pourquoi elle est utilisée"],
        [
            ["B2", "490 nm, bleu", "Correction atmosphérique, entre dans le calcul de l'EVI"],
            ["B3", "560 nm, vert", "Détection des surfaces en eau"],
            ["B4", "665 nm, rouge", "Fortement absorbé par la chlorophylle"],
            ["B8", "842 nm, proche infrarouge", "Fortement réfléchi par une végétation saine"],
            ["B11", "1610 nm, SWIR 1", "Sensible à l'humidité de la végétation"],
            ["B12", "2190 nm, SWIR 2", "Sensible aux zones brûlées et au sol nu"],
        ],
        [18, 50, 112],
    )

    p("Ces six bandes ne sont pas choisies au hasard. Chaque type de surface "
      "renvoie la lumière différemment selon la longueur d'onde, et cette "
      "empreinte est ce que le modèle apprend à reconnaître.")

    fig("01_signatures.png", "Figure 2. Signature spectrale moyenne de chaque "
        "classe. C'est la matière première de la classification.", 170)

    p("La lecture de cette figure explique tout le principe de la télédétection. "
      "Une forêt dense absorbe presque tout le rouge, parce que sa chlorophylle "
      "s'en nourrit, et renvoie massivement le proche infrarouge, parce que la "
      "structure interne des feuilles le diffuse. Un sol nu ne fait ni l'un ni "
      "l'autre : sa courbe monte régulièrement. L'eau absorbe tout à partir du "
      "proche infrarouge et s'effondre à zéro.")

    p("Les courbes se croisent par endroits, notamment entre forêt dégradée et "
      "agriculture sur les bandes SWIR. C'est précisément là que le modèle a du "
      "travail, et c'est pourquoi une seule bande ne suffit pas.")

    page()

    h2("3.3 Le masquage des nuages et le composite médian")

    p("Sous les tropiques, la couverture nuageuse est le principal obstacle. Une "
      "scène individuelle est souvent inexploitable à moitié. Deux mécanismes se "
      "combinent pour résoudre le problème.")

    h3("Premier mécanisme : le masque SCL")
    p("Sentinel-2 fournit une bande supplémentaire appelée SCL (Scene "
      "Classification Layer), qui étiquette chaque pixel : végétation, sol nu, "
      "eau, nuage, ombre de nuage, neige. Le code écarte les pixels portant les "
      "codes 3 (ombre), 8, 9 et 10 (nuages de densité croissante) et 11 (neige). "
      "Ces pixels deviennent des trous dans l'image.")

    h3("Deuxième mécanisme : la médiane temporelle")
    p("On ne travaille pas sur une scène, mais sur toutes les scènes de la saison "
      "sèche, du 1er juin au 30 septembre. Pour chaque pixel, on prend la valeur "
      "médiane de toutes les dates disponibles. Un nuage résiduel présent sur une "
      "seule date produit une valeur aberrante que la médiane écarte "
      "automatiquement.")

    fig("02_composite_median.png", "Figure 3. Trois scènes partiellement "
        "nuageuses, et le composite médian qui en résulte.", 175)

    p("Le choix de la saison sèche n'est pas seulement pratique. Il garantit aussi "
      "que les images comparées d'une année sur l'autre le sont dans des "
      "conditions équivalentes : même angle solaire approximatif, même état "
      "phénologique de la végétation. Comparer une image de saison sèche à une "
      "image de saison des pluies produirait de faux changements.")

    h3("La requête effectivement exécutée")
    code(
        "ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')\n"
        "  .filterBounds(zone_etude)                       # emprise geographique\n"
        "  .filterDate(f'{annee}-06-01', f'{annee}-09-30') # saison seche\n"
        "  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40))\n"
        "  .map(masque_nuages_scl)                         # trous sur les nuages\n"
        "  .median()                                       # composite\n"
        "  .select(['B2','B3','B4','B8','B11','B12'])"
    )

    page()

    h2("3.4 Sentinel-1 : le radar qui traverse les nuages")

    p("Même avec la médiane, certaines années restent trop nuageuses. Sentinel-1 "
      "apporte une solution complémentaire : c'est un radar, il émet sa propre "
      "onde et mesure ce qui revient. Les nuages sont transparents pour lui, et il "
      "fonctionne de nuit.")

    p("Le radar ne mesure pas la couleur mais la structure. Une forêt dense "
      "renvoie beaucoup d'énergie en polarisation croisée (VH), parce que l'onde "
      "rebondit dans le volume des branches. Un sol nu en renvoie peu. Une surface "
      "d'eau agit comme un miroir et renvoie presque rien vers le capteur.")

    fig("10_radar.png", "Figure 4. À gauche, la signature radar de chaque classe. "
        "À droite, le gain de couverture sous un ciel à moitié nuageux.", 175)

    p("Le module src/data/radar.py calcule également le RVI (Radar Vegetation "
      "Index), défini comme 4 fois VH divisé par la somme VV plus VH, en puissance "
      "linéaire. Il donne un indicateur de densité de végétation indépendant de "
      "toute condition d'éclairage.")

    h2("3.5 SRTM : le relief")

    p("La mission SRTM de la NASA a cartographié l'altitude de la quasi-totalité "
      "des terres émergées. On en dérive trois couches : l'altitude, la pente et "
      "l'exposition du versant.")

    p("Ces variables comptent parce que la déforestation suit la géographie. Un "
      "terrain plat et accessible est défriché en premier ; une pente forte est "
      "difficile à cultiver et protège la forêt plus longtemps. La topographie est "
      "donc un prédicteur, pas seulement une information de contexte.")

    h2("3.6 Les données météorologiques")

    p("src/data/weather_collector.py collecte les précipitations et les "
      "températures mensuelles via OpenWeatherMap, avec un repli sur une "
      "climatologie équatoriale réaliste à deux saisons des pluies. Ces données "
      "servent à l'analyse contextuelle : une saison sèche prolongée augmente le "
      "risque de feux et facilite le défrichement.")

    page()

    h2("3.7 Du serveur de Google au disque local")

    p("Le point souvent mal compris : appeler le code de collecte ne télécharge "
      "rien. GEE construit une description du calcul, et il faut lancer un export "
      "explicite pour obtenir les fichiers. C'est le rôle de scripts/gee_export.py, "
      "qui propose trois modes.")

    table(
        ["Mode", "Commande", "Usage"],
        [
            ["Export Drive", "gee_export --drive",
             "Production. Pleine résolution 10 m, vers Google Drive, "
             "à télécharger ensuite."],
            ["Téléchargement direct", "gee_export --download --scale 100",
             "Aperçu rapide. Résolution réduite, écriture directe dans data/raw/."],
            ["GeoTIFF de test", "gee_export --demo-geotiff",
             "Valider toute la chaîne réelle sans compte GEE. Écrit des GeoTIFF "
             "géoréférencés synthétiques."],
        ],
        [34, 56, 90],
    )

    p("Le troisième mode mérite une mention particulière. Il permet de vérifier "
      "que la lecture des GeoTIFF, l'alignement des grilles et l'entraînement sur "
      "données réelles fonctionnent, avant même de disposer des vraies images. "
      "C'est un filet de sécurité utile en démonstration.")

    note("Une limite à connaître et à assumer : dans l'état actuel du code, "
         "get_annual_composite() renvoie toujours un composite synthétique, même "
         "quand GEE est connecté. La seule voie vers de vraies données passe par "
         "l'export en GeoTIFF puis la lecture par RasterSource. C'est une décision "
         "d'architecture cohérente, pas un oubli : elle sépare nettement le calcul "
         "distant du traitement local.")

    page()

    # ══════════════════════════════════════════════════════════════════
    # 4. Features
    # ══════════════════════════════════════════════════════════════════
    h1("4. Du pixel brut au vecteur de caractéristiques")

    p("Un modèle de Machine Learning ne comprend pas une image : il attend des "
      "nombres. L'étape de préparation des caractéristiques, ou features, consiste "
      "à transformer chaque pixel en une liste de valeurs qui décrivent ce qu'il "
      "est.")

    h2("4.1 Les indices spectraux")

    p("Les six bandes brutes suffisent rarement. On les combine en indices, des "
      "rapports qui isolent une propriété physique précise et qui ont l'avantage "
      "d'être normalisés, donc peu sensibles aux variations d'éclairage.")

    table(
        ["Indice", "Formule", "Ce qu'il révèle"],
        [
            ["NDVI", "(B8 - B4) / (B8 + B4)",
             "Vigueur de la végétation. Proche de 1 sur forêt dense, "
             "négatif sur l'eau."],
            ["EVI", "2.5 (B8 - B4) / (B8 + 6 B4 - 7.5 B2 + 1)",
             "Même idée, mais sature moins sur les couverts très denses."],
            ["NDWI", "(B3 - B8) / (B3 + B8)",
             "Présence d'eau libre. Sépare rivières et zones inondées."],
            ["NBR", "(B8 - B12) / (B8 + B12)",
             "Zones brûlées. Le brûlis est le mode de défrichement dominant "
             "dans la zone."],
        ],
        [22, 62, 96],
    )

    p("Le NDVI est le plus connu, mais il sature : au-delà d'une certaine densité "
      "de canopée, il ne distingue plus rien. C'est exactement le cas d'une forêt "
      "équatoriale. D'où l'EVI, qui corrige ce défaut, et le NBR, qui repère les "
      "surfaces récemment brûlées que le NDVI seul confondrait avec du sol nu "
      "ordinaire.")

    fig("04_indices.png", "Figure 5. À gauche la couverture réelle, au centre et "
        "à droite les indices calculés sur le même composite.", 175)

    p("Sur ces cartes, le front de déforestation apparaît sans qu'aucun modèle "
      "n'ait encore été entraîné. Les indices sont un calcul déterministe, pas un "
      "apprentissage. Ils fournissent au modèle une information déjà à moitié "
      "digérée, ce qui lui simplifie considérablement la tâche.")

    page()

    h2("4.2 Le vecteur de treize caractéristiques")

    fig("05_features.png", "Figure 6. La composition du vecteur de features "
        "associé à chaque pixel.", 175)

    p("L'ordre de ces treize valeurs est figé une fois pour toutes dans "
      "config/settings.py, sous le nom FEATURE_NAMES. Il est respecté partout : à "
      "la construction du dataset, à l'entraînement, à la prédiction, et à "
      "l'affichage des importances de variables.")

    p("Ce point paraît anodin et ne l'est pas. Si l'ordre changeait entre "
      "l'entraînement et la prédiction, le modèle interpréterait une altitude "
      "comme un NDVI. Il ne planterait pas : il donnerait simplement des résultats "
      "faux, silencieusement. Figer l'ordre dans la configuration est une "
      "protection contre cette classe d'erreur.")

    h3("L'ordre de grandeur")
    p("Sur une grille de 256 par 256 pixels, cela représente 65 536 pixels par "
      "année, donc autant de vecteurs de 13 nombres. Sur onze années, environ "
      "720 000 exemples. Une vraie image à 10 mètres sur la même zone de 50 "
      "kilomètres en produirait 25 millions par année.")

    h2("4.3 Le découpage en tuiles pour le réseau de neurones")

    p("Random Forest et XGBoost consomment des vecteurs de pixels indépendants. Le "
      "U-Net, lui, a besoin de voir une portion d'image. Le code "
      "(src/preprocessing/feature_extraction.py) découpe donc l'image en tuiles de "
      "128 par 128 pixels, avec un recouvrement de 32 pixels entre tuiles voisines.")

    p("Le recouvrement a une justification précise. Un réseau convolutif est moins "
      "fiable sur les bords de son champ de vision, faute de contexte. Sans "
      "recouvrement, on verrait apparaître des coutures visibles aux jonctions de "
      "tuiles. Avec recouvrement, chaque zone frontalière est prédite plusieurs "
      "fois et les prédictions sont moyennées à la reconstruction.")

    h2("4.4 Le nettoyage distribué avec PySpark")

    p("src/preprocessing/spark_pipeline.py applique un traitement distribué : "
      "suppression des valeurs manquantes, filtrage des valeurs aberrantes, "
      "statistiques par classe, normalisation par StandardScaler, puis export en "
      "Parquet partitionné par année. Si PySpark n'est pas installé, un repli "
      "pandas équivalent prend le relais.")

    p("Sur la taille actuelle du jeu de données, pandas suffirait. L'intérêt de "
      "Spark est de montrer que la chaîne tient à l'échelle : la même logique "
      "s'applique sans réécriture si la zone d'étude passe d'une province à un "
      "pays entier.")

    page()

    # ══════════════════════════════════════════════════════════════════
    # 5. Machine Learning
    # ══════════════════════════════════════════════════════════════════
    h1("5. Le Machine Learning")

    h2("5.1 Le principe de l'apprentissage supervisé")

    p("Tous les modèles du projet relèvent de l'apprentissage supervisé. Le "
      "principe tient en trois temps.")

    ol([
        "On dispose d'exemples étiquetés : des pixels dont on connaît déjà la "
        "classe, fournis par la vérité terrain.",
        "Le modèle ajuste ses paramètres internes pour réduire l'écart entre ses "
        "prédictions et les étiquettes connues. Cet écart est mesuré par une "
        "fonction de perte.",
        "On évalue le modèle sur des exemples qu'il n'a jamais vus. C'est la seule "
        "mesure honnête de sa capacité à généraliser.",
    ])

    p("Le troisième point est le plus important et le plus facile à saboter. Un "
      "modèle qui mémorise ses exemples d'entraînement obtient un score parfait "
      "dessus et s'effondre sur des données nouvelles. La section 5.7 explique la "
      "précaution particulière que demandent les données spatiales.")

    h3("D'où viennent les étiquettes")
    p("En mode réel, la vérité terrain provient de deux sources : le produit "
      "Hansen Global Forest Change, qui fournit une carte mondiale de perte "
      "forestière annuelle depuis 2000, et une annotation manuelle de zones "
      "d'échantillon. Ces étiquettes sont déposées dans data/raw/landcover/.")

    h2("5.2 Deux problèmes distincts")

    p("Il faut bien séparer les deux questions que le projet traite, car elles "
      "n'ont ni les mêmes entrées, ni les mêmes étiquettes, ni la même utilité.")

    table(
        ["", "Problème A : classification", "Problème B : prédiction du risque"],
        [
            ["Question", "Qu'y a-t-il sur ce pixel aujourd'hui ?",
             "Ce pixel de forêt sera-t-il défriché d'ici deux ans ?"],
            ["Étiquette", "Classe observée, 0 à 4",
             "Comparaison entre l'année N et l'année N+1"],
            ["Sortie", "Carte de couverture du sol",
             "Carte de risque graduée de 0 à 100"],
            ["Modèles", "Random Forest, XGBoost, U-Net",
             "XGBoost binaire (ou GradientBoosting en repli)"],
        ],
        [26, 74, 80],
    )

    page()

    h2("5.3 Random Forest, la référence de départ")

    p("Un arbre de décision pose une suite de questions simples : le NDVI "
      "dépasse-t-il 0,7 ? La bande B11 est-elle inférieure à 0,2 ? Chaque réponse "
      "mène à une nouvelle question, jusqu'à une feuille qui donne la classe.")

    p("Un arbre seul est instable : changez quelques exemples d'entraînement et "
      "sa structure change complètement. La forêt aléatoire corrige ce défaut en "
      "entraînant 200 arbres, chacun sur un tirage différent des exemples et des "
      "variables, puis en faisant voter l'ensemble. Les erreurs individuelles se "
      "compensent.")

    p("Configuration retenue (config/settings.py) : 200 arbres, profondeur "
      "maximale 15, minimum 5 exemples pour scinder un noeud. La profondeur "
      "limitée est une protection contre le surapprentissage.")

    p("Son autre atout est l'interprétabilité. Le modèle indique quelles "
      "variables ont le plus contribué à ses décisions, ce qui permet de vérifier "
      "que le résultat est physiquement crédible : si l'aspect du versant "
      "dominait le NDVI dans la détection de forêt, il y aurait un problème.")

    h2("5.4 XGBoost, l'affinage séquentiel")

    p("XGBoost construit lui aussi des arbres, mais en séquence et non en "
      "parallèle. Chaque nouvel arbre se concentre sur les exemples que les "
      "précédents ont mal classés. On corrige progressivement les erreurs "
      "résiduelles plutôt que de moyenner des avis indépendants.")

    p("Cette approche est généralement plus performante sur données tabulaires, au "
      "prix d'une sensibilité plus grande au réglage des hyperparamètres. Le taux "
      "d'apprentissage est fixé à 0,1 : chaque arbre ne corrige qu'une fraction de "
      "l'erreur, ce qui évite de sur-corriger sur du bruit.")

    p("Les deux modèles exposent volontairement la même interface (fit, predict, "
      "predict_proba, feature_importance), ce qui rend la comparaison directe et "
      "sans biais d'implémentation.")

    page()

    h2("5.5 U-Net, le réseau qui voit le contexte")

    p("Random Forest et XGBoost jugent chaque pixel isolément. Ils ne savent pas "
      "qu'un pixel entouré de forêt est probablement de la forêt. Cette "
      "information de voisinage est pourtant décisive, et c'est ce qu'apporte un "
      "réseau convolutif.")

    fig("07_unet.png", "Figure 7. L'architecture U-Net : descente, goulot, "
        "remontée, et connexions résiduelles.", 175)

    h3("La descente, ou encodeur")
    p("L'image traverse des blocs de convolution qui extraient des motifs, "
      "entrecoupés de réductions de taille. À chaque niveau, l'image rétrécit "
      "mais le nombre de canaux augmente : on perd en précision spatiale et on "
      "gagne en compréhension du contexte. Les premiers niveaux détectent des "
      "textures, les derniers reconnaissent des formes entières, comme une "
      "parcelle agricole.")

    h3("Le goulot d'étranglement")
    p("Au point le plus bas, l'image est réduite mais décrite par 512 canaux. "
      "C'est la représentation la plus abstraite, celle qui encode le sens de la "
      "scène plutôt que ses détails.")

    h3("La remontée, ou décodeur")
    p("On reconstruit ensuite progressivement la résolution d'origine, jusqu'à "
      "produire une classification pixel par pixel. Sans précaution, cette "
      "reconstruction serait floue : les détails fins ont été perdus à la descente.")

    h3("Les connexions résiduelles")
    p("C'est l'idée centrale du U-Net. À chaque niveau de la remontée, on "
      "reconcatène la carte correspondante de la descente, qui avait conservé le "
      "détail spatial. Le décodeur dispose ainsi à la fois du sens global, venu du "
      "goulot, et du détail local, venu directement de l'encodeur. C'est ce qui "
      "produit des contours de parcelles nets.")

    p("La sortie applique une fonction softmax sur cinq canaux : pour chaque "
      "pixel, le réseau fournit une probabilité par classe, dont la somme vaut 1. "
      "La classe retenue est celle de probabilité maximale, et les probabilités "
      "elles-mêmes indiquent le degré de confiance.")

    note("Si TensorFlow n'est pas installé, le code bascule sur une segmentation "
         "par centroïdes spectraux qui expose la même interface. Le pipeline reste "
         "exécutable de bout en bout, avec des performances moindres. C'est un "
         "repli assumé, tracé dans les journaux.")

    page()

    h2("5.6 Le prédicteur de risque")

    p("Ce modèle répond à la question qui intéresse réellement un décideur : où "
      "faut-il intervenir avant que la forêt ne disparaisse.")

    h3("Construction de l'étiquette")
    p("Elle est temporelle. On compare la carte de couverture de l'année N à celle "
      "de l'année N+1. Un pixel est étiqueté positif s'il était forêt en N et ne "
      "l'est plus en N+1. L'entraînement se restreint aux pixels encore "
      "forestiers ; sans cette restriction, le modèle apprendrait surtout à "
      "reconnaître ce qui est déjà détruit, ce qui n'a aucune valeur prédictive.")

    h3("Les six variables explicatives")
    table(
        ["Variable", "Justification"],
        [
            ["Distance à la route", "Le défrichement suit les axes de pénétration"],
            ["Distance au village", "La pression vient des zones habitées"],
            ["Distance à la zone déjà défrichée", "Le front avance par contiguïté"],
            ["Pente", "Une pente forte décourage la mise en culture"],
            ["Altitude", "Corrèle avec l'accessibilité et le type de sol"],
            ["Taux de déforestation du voisinage", "Mesure la pression locale immédiate"],
        ],
        [72, 108],
    )

    p("Aucune de ces variables n'est spectrale. Le modèle ne regarde pas la "
      "couleur du pixel mais sa situation géographique. La logique sous-jacente "
      "est celle du front de déforestation : on ne défriche pas au hasard, on "
      "défriche à partir de ce qui est déjà ouvert et accessible.")

    fig("09_risque.png", "Figure 8. La couverture observée et le risque prédit "
        "sur la forêt restante.", 165)

    p("Le résultat est lisible immédiatement : le risque se concentre sur les "
      "lisières et le long de la route diagonale. Le coeur des massifs encore "
      "intacts reste à faible risque. C'est ce que l'on attend d'un modèle de "
      "front, et c'est un bon test de crédibilité.")

    page()

    h2("5.7 Le découpage entraînement / test, point méthodologique central")

    p("C'est le point sur lequel un jury interrogera, et celui où beaucoup de "
      "projets de télédétection se trompent.")

    p("Deux pixels voisins sur une image satellite se ressemblent énormément : "
      "même type de sol, même éclairage, souvent la même classe. Si l'on répartit "
      "les pixels aléatoirement entre entraînement et test, presque chaque pixel "
      "de test a un voisin immédiat dans l'ensemble d'entraînement. Le modèle "
      "retrouve alors au test des choses qu'il a déjà vues. Le score obtenu est "
      "excellent et ne veut rien dire.")

    p("On appelle cela une fuite de données géographique. La parade appliquée par "
      "le projet consiste à découper la grille en 64 blocs et à affecter chaque "
      "bloc entier, et non chaque pixel, à l'entraînement, à la validation ou au "
      "test.")

    fig("06_split.png", "Figure 9. À gauche le découpage aléatoire, à éviter. "
        "À droite le découpage spatial par blocs, appliqué par le projet.", 160)

    p("Avec le découpage par blocs, le modèle est évalué sur des zones "
      "géographiques entières qu'il n'a jamais rencontrées. Le score est plus "
      "faible qu'avec un découpage aléatoire, et c'est précisément ce qui le rend "
      "crédible : il mesure une vraie capacité de généralisation.")

    p("Pour le U-Net, le même raisonnement s'applique au niveau des tuiles : ce "
      "sont des tuiles entières qui partent en test, jamais des morceaux de tuile.")

    h2("5.8 L'évaluation des modèles")

    table(
        ["Métrique", "Définition courte", "Pourquoi elle est suivie"],
        [
            ["Accuracy", "Part de pixels correctement classés",
             "Lisible, mais trompeuse ici : la forêt domine largement"],
            ["Précision", "Parmi les pixels prédits classe X, part de justes",
             "Mesure les fausses alertes"],
            ["Rappel", "Parmi les pixels réellement X, part de retrouvés",
             "Mesure les oublis"],
            ["F1-macro", "Moyenne harmonique, moyennée sans pondération",
             "Une classe rare mal prédite fait chuter le score"],
            ["Mean IoU", "Intersection sur union, moyennée",
             "Métrique de référence en segmentation d'images"],
            ["AUC-ROC", "Qualité du classement des probabilités",
             "Indépendante du seuil de décision retenu"],
        ],
        [24, 66, 90],
    )

    p("Le F1-macro et le Mean IoU sont les deux chiffres à mettre en avant. Un "
      "modèle qui prédirait bêtement forêt partout obtiendrait déjà une accuracy "
      "honorable, un F1-macro très mauvais, et serait immédiatement démasqué par "
      "la matrice de confusion.")

    p("Le rapport complet est écrit dans data/processed/model_metrics.json et "
      "servi par l'endpoint /api/v1/models.")

    page()

    h2("5.9 Ce que le pipeline produit au final")

    fig("08_courbes.png", "Figure 10. Les deux sorties quantitatives : le stock "
        "de forêt restant et le flux annuel de perte.", 175)

    p("Le graphique de gauche donne le stock, celui de droite le flux. Les deux "
      "sont nécessaires : le stock dit combien il reste, le flux dit à quelle "
      "vitesse on le perd et permet d'identifier les années de rupture.")

    p("Ces chiffres sont calculés en comptant les pixels de classe 0 et 1 et en "
      "les multipliant par la surface d'un pixel. C'est une simple conversion "
      "d'unité, mais elle transforme une carte en argument chiffré, seul langage "
      "audible par une administration ou un bailleur.")

    fig("03_evolution.png", "Figure 11. Le recul du couvert forestier sur la "
        "période étudiée.", 175)

    p("Sur ces trois cartes, on lit la dynamique décrite plus haut : l'agriculture "
      "progresse en tache d'huile depuis les villages et le long de la route "
      "diagonale, en laissant une frange de forêt dégradée à l'avant du front. "
      "C'est exactement le motif que le prédicteur de risque exploite.")

    page()

    # ══════════════════════════════════════════════════════════════════
    # 6. Stockage
    # ══════════════════════════════════════════════════════════════════
    h1("6. Le stockage des données")

    p("Le stockage est volontairement éclaté. Chaque type de donnée va là où son "
      "format est le plus efficace, plutôt que de tout entasser au même endroit.")

    fig("11_stockage.png", "Figure 12. Répartition des données entre le disque, "
        "la base relationnelle et les assets du frontend.", 175)

    h2("6.1 Les images : GeoTIFF sur le disque")

    p("Un GeoTIFF est un fichier TIFF qui embarque son géoréférencement : système "
      "de coordonnées, emprise, résolution. Chaque pixel du fichier correspond "
      "donc à une position réelle sur Terre, ce qu'un PNG ou un JPEG ne "
      "permettent pas.")

    code(
        "data/raw/\n"
        "  composites/\n"
        "    2015.tif ... 2025.tif    6 bandes, reflectance Sentinel-2\n"
        "  landcover/\n"
        "    2015.tif ... 2025.tif    1 bande, classes 0 a 4 (verite terrain)\n"
        "  topography.tif             3 bandes : altitude, pente, aspect"
    )

    p("Contrainte forte : toutes les images doivent partager exactement la même "
      "grille, c'est-à-dire les mêmes dimensions, la même emprise et la même "
      "résolution. Sans cela, le pixel numéro 1 000 d'une image ne désignerait pas "
      "le même endroit que le pixel numéro 1 000 d'une autre, et toute comparaison "
      "temporelle serait fausse.")

    p("L'alignement est vérifié au chargement du dataset, et le script "
      "scripts/check_real_data.py contrôle l'ensemble du jeu de données avant "
      "l'entraînement : années détectées, nombre de bandes, cohérence des grilles, "
      "présence d'étiquettes.")

    h2("6.2 Les datasets préparés")

    p("Une fois les features calculées et le découpage effectué, les tableaux sont "
      "écrits en NPZ compressé, le format natif de numpy. On y trouve "
      "pixel_dataset.npz pour les modèles par pixel et tile_dataset.npz pour le "
      "U-Net, accompagnés d'un dataset_metadata.json qui documente le nom des "
      "features et la taille de chaque partition.")

    p("L'intérêt est la vitesse : recharger un NPZ prend une fraction de seconde, "
      "alors que reconstruire les features depuis les GeoTIFF prend plusieurs "
      "minutes. On paie le calcul une fois.")

    p("La sortie du pipeline Spark est stockée à part, en Parquet partitionné par "
      "année. Le Parquet est un format colonne : lire uniquement la colonne NDVI "
      "de l'année 2023 ne demande pas de parcourir le reste du fichier.")

    page()

    h2("6.3 Les modèles entraînés")

    table(
        ["Fichier", "Modèle", "Format"],
        [
            ["random_forest.joblib", "Random Forest", "Sérialisation joblib"],
            ["xgboost.joblib", "XGBoost", "Sérialisation joblib"],
            ["unet.keras", "U-Net", "Format natif Keras"],
            ["unet_fallback.joblib", "Repli centroïdes", "Sérialisation joblib"],
            ["risk_predictor.joblib", "Prédicteur de risque", "Sérialisation joblib"],
        ],
        [58, 56, 66],
    )

    p("Sauvegarder un modèle entraîné évite de tout recalculer à chaque "
      "prédiction. L'API charge le fichier au démarrage et répond ensuite en "
      "quelques millisecondes.")

    h2("6.4 La base de données relationnelle")

    p("PostgreSQL, accédé via SQLAlchemy (src/api/database.py). Elle ne stocke "
      "aucune image : uniquement des résultats agrégés, des métadonnées et les "
      "données applicatives.")

    table(
        ["Table", "Colonnes principales", "Rôle"],
        [
            ["users", "email, password_hash, role, otp_secret",
             "Comptes et authentification à deux facteurs"],
            ["analysis_results", "year, total_forest_ha, forest_loss_ha, rate",
             "Résultats d'analyse par année"],
            ["predictions", "zone_lat, zone_lon, risk_score, model_version",
             "Prédictions de risque géolocalisées"],
            ["reports", "lat, lon, description, severity, status",
             "Signalements soumis par les citoyens"],
            ["api_logs", "user_id, endpoint, method, status_code",
             "Traçabilité des appels à l'API"],
            ["model_registry", "model_name, version, accuracy, f1_score",
             "Versions de modèles et performances associées"],
        ],
        [34, 76, 70],
    )

    p("Le mot de passe n'est jamais stocké en clair, seulement son empreinte "
      "cryptographique, ce qui rend la valeur inutilisable même en cas de fuite "
      "de la base. La table reports mérite d'être signalée : elle relie "
      "l'observation satellite au terrain, en permettant à un habitant de "
      "signaler une coupe que le satellite n'a pas encore vue.")

    note("Si PostgreSQL est injoignable, la couche bascule automatiquement sur un "
         "SQLite local, dans data/deforestwatch.db. L'API démarre donc partout, y "
         "compris sur un poste sans serveur de base installé.")

    page()

    h2("6.5 Pourquoi les images ne vont pas en base")

    ul([
        "Volume : une seule année d'images pèse de plusieurs centaines de "
        "mégaoctets à plusieurs gigaoctets.",
        "Mode d'accès : le traitement lit des blocs entiers de pixels, jamais des "
        "lignes filtrées par condition.",
        "Outillage : rasterio, numpy et GDAL lisent le GeoTIFF nativement, avec "
        "accès partiel à une fenêtre géographique.",
        "Coût : une base relationnelle facture cher le stockage de données "
        "binaires volumineuses, pour un bénéfice nul ici.",
    ])

    p("La règle appliquée tient en une phrase : les pixels vivent sur le disque, "
      "la base ne garde que ce qui doit être interrogé, filtré ou joint.")

    h2("6.6 Ce qui est versionné, et ce qui ne l'est pas")

    table(
        ["Dans Git", "Hors Git"],
        [
            ["Code source, configuration, tests",
             "data/raw/ : les images brutes"],
            ["Documentation, notebooks, scripts",
             "data/processed/ : les datasets dérivés"],
            ["Assets de démonstration du frontend",
             "data/models/ : les modèles entraînés"],
            ["README et fichiers .gitkeep des dossiers de données",
             "Le fichier .env et la clé de service GEE"],
        ],
        [90, 90],
    )

    p("La logique est double. D'un côté, Git n'est pas fait pour des fichiers "
      "binaires volumineux qui changent souvent. De l'autre, les secrets ne "
      "doivent jamais entrer dans l'historique d'un dépôt, car ils y resteraient "
      "consultables même après suppression.")

    p("Le dépôt reste donc léger et clonable rapidement, et tout ce qui est "
      "reconstructible se reconstruit par une commande.")

    page()

    # ══════════════════════════════════════════════════════════════════
    # 7. Démo / réel
    # ══════════════════════════════════════════════════════════════════
    h1("7. La bascule démonstration / données réelles")

    p("C'est la pièce d'architecture qui tient l'ensemble, et celle qui mérite le "
      "plus d'être défendue.")

    fig("13_provider.png", "Figure 13. L'abstraction qui rend la source de "
        "données interchangeable.", 155)

    p("src/data/sources.py définit une interface abstraite, DataSource, qui "
      "déclare quatre opérations : lister les années disponibles, fournir le "
      "composite d'une année, fournir la carte de classes, fournir la topographie. "
      "Deux classes l'implémentent.")

    table(
        ["Implémentation", "Ce qu'elle fait"],
        [
            ["SyntheticSource",
             "Simule un front agricole progressant depuis les villages et les "
             "routes, avec des signatures spectrales réalistes et du bruit."],
            ["RasterSource",
             "Lit les vrais GeoTIFF de data/raw/ avec rasterio et vérifie "
             "l'alignement des grilles."],
        ],
        [46, 134],
    )

    p("Tout le code applicatif passe par src/data/provider.py et n'appelle jamais "
      "directement l'une ou l'autre. Il ignore laquelle est active.")

    h3("La résolution automatique")
    p("À l'exécution, resolve_source() applique une règle simple : si DEMO_MODE "
      "vaut false et que des fichiers .tif sont présents dans "
      "data/raw/composites/, la source réelle est retenue. Sinon, on retombe sur "
      "la source synthétique, avec un avertissement explicite dans les journaux.")

    p("Un administrateur peut même basculer à chaud, sans redémarrer le service, "
      "via l'endpoint POST /api/v1/admin/source/{mode}, où mode vaut auto, demo ou "
      "real.")

    note("Conséquence pratique : déposer les GeoTIFF au bon format et passer "
         "DEMO_MODE à false suffit à faire passer l'ensemble du projet sur des "
         "données réelles, sans modifier une seule ligne de code. Datasets, "
         "statistiques, cartes, API et dashboard suivent automatiquement.")

    p("Deux exceptions à connaître, par honnêteté : le prédicteur de risque et le "
      "pipeline Spark appellent encore directement le générateur synthétique. Ces "
      "deux modules resteront donc en mode démonstration même avec de vraies "
      "images en place. C'est le prochain point à corriger pour que la bascule "
      "soit complète.")

    page()

    # ══════════════════════════════════════════════════════════════════
    # 8. Questions de soutenance
    # ══════════════════════════════════════════════════════════════════
    h1("8. Questions de soutenance")

    p("Les questions ci-dessous reviennent presque systématiquement sur ce type de "
      "projet. Les réponses sont là pour être reformulées avec vos mots.")

    h3("Pourquoi la médiane et pas la moyenne pour le composite ?")
    p("Parce que la moyenne est sensible aux valeurs extrêmes. Un seul nuage très "
      "réfléchissant tirerait la moyenne vers le haut et blanchirait le pixel. La "
      "médiane ignore les extrêmes par construction : tant que plus de la moitié "
      "des dates sont dégagées, elle donne la valeur du sol.")

    h3("Pourquoi trois modèles plutôt qu'un seul ?")
    p("Pour comparer deux familles d'approches sur le même problème. Random Forest "
      "et XGBoost travaillent pixel par pixel, sont rapides et interprétables. Le "
      "U-Net exploite le contexte spatial et produit des contours plus nets, au "
      "prix d'un entraînement plus lourd. La comparaison chiffrée fait partie du "
      "résultat, elle n'est pas un détour.")

    h3("Comment savez-vous que votre modèle n'a pas simplement mémorisé ?")
    p("Grâce au découpage spatial par blocs. Le test porte sur des zones "
      "géographiques entières que le modèle n'a jamais vues. Avec un découpage "
      "aléatoire classique, chaque pixel de test aurait eu un voisin en "
      "entraînement et le score aurait été artificiellement élevé.")

    h3("Que se passe-t-il si une année est entièrement nuageuse ?")
    p("Le composite optique de cette année est inexploitable. Deux solutions "
      "existent dans le projet : élargir la fenêtre temporelle au-delà de la "
      "saison sèche, ce qui dégrade la comparabilité, ou s'appuyer sur le radar "
      "Sentinel-1, qui traverse les nuages et reste disponible.")

    h3("Pourquoi ne pas stocker les images dans PostgreSQL ?")
    p("Volume, mode d'accès et coût. Le traitement lit des blocs entiers de "
      "pixels, ce qu'une base relationnelle fait mal, tandis que les "
      "bibliothèques de télédétection lisent le GeoTIFF nativement, y compris "
      "partiellement. La base garde ce qu'on interroge et joint, c'est-à-dire des "
      "agrégats et des données applicatives.")

    h3("Vos données sont synthétiques : quelle est la valeur du travail ?")
    p("La chaîne de traitement est réelle et complète : requêtes GEE, masquage "
      "SCL, composite médian, indices, découpage spatial, entraînement, "
      "évaluation, API, interfaces. Le mode démonstration ne remplace que la "
      "source d'images, derrière une interface abstraite. Déposer de vraies "
      "images bascule l'ensemble sans modification du code, ce qui est vérifiable "
      "en direct avec la commande make export-demo.")

    h3("Quelle est la précision attendue en conditions réelles ?")
    p("Sur des composites Sentinel-2 réels et une vérité terrain Hansen, la "
      "littérature situe ce type de classification autour de 0,85 à 0,92 de "
      "F1-macro sur cinq classes. Les confusions se concentrent entre forêt "
      "dégradée et agriculture, parce que ces deux classes se recouvrent "
      "physiquement : une jachère en repousse est difficile à distinguer d'une "
      "forêt dégradée, même pour un oeil humain.")

    page()

    # ══════════════════════════════════════════════════════════════════
    # 9. Commandes
    # ══════════════════════════════════════════════════════════════════
    h1("9. Aide-mémoire des commandes")

    table(
        ["Commande", "Effet"],
        [
            ["make install", "Installe les dépendances Python"],
            ["make seed", "Génère les données de démonstration"],
            ["make export-demo", "Écrit des GeoTIFF de test dans data/raw/"],
            ["make check-data", "Vérifie le jeu de données réelles"],
            ["make real", "Bascule la configuration en mode réel"],
            ["make demo", "Revient au mode démonstration"],
            ["make mode", "Affiche le mode de données courant"],
            ["make train", "Entraîne les modèles et produit les métriques"],
            ["make test", "Lance la suite de tests avec couverture"],
            ["make api", "Démarre l'API FastAPI sur le port 8000"],
            ["make dashboard", "Démarre le dashboard Streamlit sur le port 8501"],
            ["make frontend", "Démarre le frontend React sur le port 5173"],
            ["make synthese", "Régénère ce document et ses figures"],
        ],
        [52, 128],
    )

    h3("Les fichiers à connaître")
    table(
        ["Fichier", "Ce qu'il contient"],
        [
            ["config/settings.py", "Toute la configuration : zone, classes, bandes, "
                                   "hyperparamètres"],
            ["src/data/gee_collector.py", "Les requêtes Google Earth Engine"],
            ["src/data/sources.py", "L'abstraction démonstration / réel"],
            ["src/data/dataset_builder.py", "Le découpage spatial et la "
                                            "construction des datasets"],
            ["src/models/trainer.py", "Le pipeline d'entraînement unifié"],
            ["src/models/evaluator.py", "Le calcul des métriques et la comparaison"],
            ["src/api/database.py", "Le schéma de la base de données"],
            ["scripts/gee_export.py", "L'export des images vers data/raw/"],
        ],
        [62, 118],
    )

    hr()
    p("Document généré par scripts/generate_synthese_technique.py. Les figures "
      "sont produites par scripts/figures_synthese.py à partir du code du projet. "
      "Pour les régénérer après une modification : make synthese.")

    return B


# ──────────────────────────────────────────────────────────────────────────
# Rendu PDF
# ──────────────────────────────────────────────────────────────────────────
_REPLACEMENTS = {
    "—": "-", "–": "-", "’": "'", "‘": "'",
    "“": '"', "”": '"', "…": "...", "→": "->",
    " ": " ", "₂": "2", "²": "2", "−": "-",
}


def _txt(text: str) -> str:
    """Texte compatible avec les polices coeur du PDF (latin-1)."""
    for src, dst in _REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", "replace").decode("latin-1")


class Doc:
    """Petit moteur de rendu : blocs typés vers PDF paginé."""

    def __init__(self):
        from fpdf import FPDF

        self.pdf = FPDF(format="A4")
        self.pdf.set_auto_page_break(auto=True, margin=18)
        self.pdf.set_margins(18, 16, 18)
        self.fig_no = 0
        self.first_page = True

    # ── primitives ──
    def _mc(self, text: str, h: float, fill: bool = False) -> None:
        self.pdf.set_x(self.pdf.l_margin)
        self.pdf.multi_cell(0, h, _txt(text), fill=fill, new_x="LMARGIN", new_y="NEXT")

    def _space(self, n: float) -> None:
        self.pdf.ln(n)

    def _room(self, needed: float) -> bool:
        """Vrai s'il reste `needed` mm sur la page courante."""
        return self.pdf.get_y() + needed <= self.pdf.h - self.pdf.b_margin

    # ── blocs ──
    def cover(self, title: str, subtitle: str) -> None:
        pdf = self.pdf
        pdf.add_page()
        self.first_page = False
        pdf.set_fill_color(*GREEN)
        pdf.rect(0, 0, pdf.w, 62, style="F")
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(18, 20)
        pdf.set_font("Helvetica", "B", 26)
        pdf.multi_cell(pdf.epw, 11, _txt(title), new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(18)
        pdf.set_font("Helvetica", "", 11.5)
        pdf.multi_cell(pdf.epw, 6, _txt(subtitle), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*INK)
        pdf.set_y(74)

    def h1(self, text: str) -> None:
        if not self._room(40):
            self.pdf.add_page()
        self._space(2)
        self.pdf.set_font("Helvetica", "B", 17)
        self.pdf.set_text_color(*GREEN)
        self._mc(text, 8.5)
        self.pdf.set_text_color(*INK)
        y = self.pdf.get_y() + 1
        self.pdf.set_draw_color(*GREEN)
        self.pdf.set_line_width(0.6)
        self.pdf.line(self.pdf.l_margin, y, self.pdf.l_margin + self.pdf.epw, y)
        self.pdf.set_line_width(0.2)
        self._space(4)

    def h2(self, text: str) -> None:
        if not self._room(28):
            self.pdf.add_page()
        self._space(3)
        self.pdf.set_font("Helvetica", "B", 12.5)
        self.pdf.set_text_color(*GREEN)
        self._mc(text, 6.5)
        self.pdf.set_text_color(*INK)
        self._space(1)

    def h3(self, text: str) -> None:
        if not self._room(22):
            self.pdf.add_page()
        self._space(2)
        self.pdf.set_font("Helvetica", "B", 10.5)
        self._mc(text, 5.5)

    def p(self, text: str) -> None:
        self.pdf.set_font("Helvetica", "", 10)
        self._mc(text, 5.0)
        self._space(1.6)

    def ul(self, items: list[str]) -> None:
        self.pdf.set_font("Helvetica", "", 10)
        for item in items:
            self.pdf.set_x(self.pdf.l_margin + 3)
            self.pdf.multi_cell(self.pdf.epw - 3, 5.0, _txt("-  " + item),
                                new_x="LMARGIN", new_y="NEXT")
            self._space(0.8)
        self._space(1.2)

    def ol(self, items: list[str]) -> None:
        self.pdf.set_font("Helvetica", "", 10)
        for i, item in enumerate(items, 1):
            self.pdf.set_x(self.pdf.l_margin + 3)
            self.pdf.multi_cell(self.pdf.epw - 3, 5.0, _txt(f"{i}.  {item}"),
                                new_x="LMARGIN", new_y="NEXT")
            self._space(0.8)
        self._space(1.2)

    def code(self, text: str) -> None:
        lines = text.split("\n")
        if not self._room(len(lines) * 4.4 + 6):
            self.pdf.add_page()
        self.pdf.set_font("Courier", "", 8.2)
        self.pdf.set_fill_color(*CODE_BG)
        self._space(1)
        for line in lines:
            self._mc(line or " ", 4.4, fill=True)
        self._space(3)

    def note(self, text: str) -> None:
        self.pdf.set_font("Helvetica", "I", 9.5)
        n_lines = max(1, len(text) // 95 + 1)
        if not self._room(n_lines * 5 + 10):
            self.pdf.add_page()
        self._space(2)
        y0 = self.pdf.get_y()
        self.pdf.set_fill_color(*GREEN_LIGHT)
        self.pdf.set_x(self.pdf.l_margin + 3)
        self.pdf.multi_cell(self.pdf.epw - 3, 5.0, _txt(text), fill=True,
                            new_x="LMARGIN", new_y="NEXT")
        y1 = self.pdf.get_y()
        self.pdf.set_fill_color(*GREEN)
        self.pdf.rect(self.pdf.l_margin, y0, 1.6, y1 - y0, style="F")
        self._space(3)

    def table(self, headers: list[str], rows: list[list[str]],
              widths: list[float] | None = None) -> None:
        from fpdf.fonts import FontFace

        est = 8 + len(rows) * 9
        if not self._room(min(est, 60)):
            self.pdf.add_page()
        self._space(1)
        self.pdf.set_font("Helvetica", "", 8.6)
        self.pdf.set_draw_color(*RULE)
        # fpdf remplit les lignes non alternées avec la couleur courante :
        # on la remet à blanc, sinon le vert du bloc "note" déteint sur le tableau.
        self.pdf.set_fill_color(255, 255, 255)
        kwargs = {}
        if widths:
            total = sum(widths)
            kwargs["col_widths"] = tuple(w / total * 100 for w in widths)
        with self.pdf.table(
            width=self.pdf.epw,
            text_align="LEFT",
            headings_style=FontFace(color=255, fill_color=TABLE_HEAD, emphasis="BOLD"),
            cell_fill_color=TABLE_ALT,
            cell_fill_mode="ROWS",
            line_height=4.6,
            padding=1.6,
            **kwargs,
        ) as table:
            hrow = table.row()
            for head in headers:
                hrow.cell(_txt(str(head)))
            for row in rows:
                trow = table.row()
                for cell in row:
                    trow.cell(_txt(str(cell)))
        self._space(4)

    def img(self, name: str, caption: str, width: float) -> None:
        from PIL import Image

        path = FIG_DIR / name
        if not path.exists():
            log.warning(f"Figure absente : {path}")
            return
        iw, ih = Image.open(path).size
        width = min(width, self.pdf.epw)
        height = width * ih / iw
        if not self._room(height + 10):
            self.pdf.add_page()
        self._space(2)
        x = self.pdf.l_margin + (self.pdf.epw - width) / 2
        self.pdf.image(str(path), x=x, w=width)
        self._space(1.5)
        self.fig_no += 1
        self.pdf.set_font("Helvetica", "I", 8.5)
        self.pdf.set_text_color(*INK_SOFT)
        self.pdf.set_x(self.pdf.l_margin)
        self.pdf.multi_cell(0, 4.4, _txt(caption), align="C",
                            new_x="LMARGIN", new_y="NEXT")
        self.pdf.set_text_color(*INK)
        self._space(4)

    def hr(self) -> None:
        self._space(2)
        y = self.pdf.get_y()
        self.pdf.set_draw_color(*RULE)
        self.pdf.line(self.pdf.l_margin, y, self.pdf.l_margin + self.pdf.epw, y)
        self._space(4)

    def page(self) -> None:
        """Saut de page explicite, ignoré si la page courante vient de commencer.

        Sans cette garde, une section qui a déjà débordé sur une nouvelle page
        laisserait derrière elle une page presque vide.
        """
        used = self.pdf.get_y() - self.pdf.t_margin
        if used > 0.25 * (self.pdf.h - self.pdf.t_margin - self.pdf.b_margin):
            self.pdf.add_page()

    # ── pied de page ──
    def _footer(self) -> None:
        """Numérote les pages après coup, sans déclencher de saut de page."""
        total = self.pdf.pages_count
        self.pdf.set_auto_page_break(False)
        for n in range(2, total + 1):          # la couverture reste sans pied
            self.pdf.page = n
            # L'état graphique est propre à chaque flux de page : on le réémet,
            # sinon le pied hérite de la police et de la couleur de la page.
            self.pdf.set_font("Helvetica", "B", 8)
            self.pdf.set_font("Helvetica", "", 8)
            self.pdf.set_text_color(*INK)
            self.pdf.set_text_color(*INK_SOFT)
            self.pdf.set_xy(self.pdf.l_margin, self.pdf.h - 12)
            half = self.pdf.epw / 2
            self.pdf.cell(half, 5, _txt("DeforestWatch-DRC - Synthèse technique"),
                          align="L")
            self.pdf.cell(half, 5, _txt(f"{n} / {total}"), align="R")
        self.pdf.set_text_color(*INK)
        self.pdf.set_auto_page_break(True, margin=18)

    def build(self, blocks, path: Path) -> Path:
        handlers = {
            "cover": lambda c: self.cover(*c),
            "h1": self.h1, "h2": self.h2, "h3": self.h3,
            "p": self.p, "ul": self.ul, "ol": self.ol,
            "code": self.code, "note": self.note,
            "table": lambda c: self.table(c[0], c[1], c[2]),
            "img": lambda c: self.img(c[0], c[1], c[2]),
            "hr": lambda _: self.hr(),
            "page": lambda _: self.page(),
        }
        for kind, content in blocks:
            if self.first_page and kind != "cover":
                self.pdf.add_page()
                self.first_page = False
            handlers[kind](content)
        self._footer()
        self.pdf.output(str(path))
        return path


def main() -> None:
    from scripts.figures_synthese import build_all

    build_all()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    Doc().build(document(), OUT_PATH)
    size_kb = OUT_PATH.stat().st_size / 1024
    log.info(f"Synthese technique -> {OUT_PATH} ({size_kb:.0f} Ko)")


if __name__ == "__main__":
    main()
