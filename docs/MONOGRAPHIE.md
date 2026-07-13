# Monographie — DeforestWatch-DRC

> Version Markdown lisible de la monographie. Le document Word formaté et
> paginé (page de garde, styles de titres pour table des matières automatique)
> est généré par `make monograph` → `docs/monographie_deforestwatch.docx`.
>
> Rédigée conformément au *Guide de Rédaction des Monographies des Projets et
> des Mémoires* de la Faculté des Sciences Informatiques de l'Université
> Protestante au Congo (janvier 2025). Projet de fin de cycle **L3 LMD —
> orientation Data Science** (monographie ≤ 40 pages, §10.5.2 du guide).

---

## Page de titre

**UNIVERSITÉ PROTESTANTE AU CONGO**
Faculté des Sciences Informatiques (FASI) — Licence (L3 LMD), orientation Data Science

# DEFORESTWATCH-DRC
### Surveillance et prédiction de la déforestation de la forêt équatoriale du Bassin du Congo par imagerie satellite et Machine Learning
*Étude de cas : Province du Mai-Ndombe (Inongo), RDC*

Monographie présentée en vue de l'obtention du grade de Licencié en Sciences Informatiques.

- **Présentée par :** Joyce A. WETUNGANI
- **Directeur de mémoire :** ……………………………………
- **Encadrant :** ……………………………………
- **Année académique :** 2025–2026 — Kinshasa, République Démocratique du Congo

---

## Résumé

La République Démocratique du Congo (RDC) abrite la deuxième plus grande forêt
tropicale humide du monde, au cœur du Bassin du Congo. Cet écosystème équatorial
subit une déforestation accélérée, principalement diffuse (agriculture sur
brûlis, charbon de bois, exploitation artisanale), que les plateformes globales
captent mal. Ce travail conçoit et implémente **DeforestWatch-DRC**, une
plateforme d'analyse et de prédiction de la déforestation appliquée à la province
du Mai-Ndombe.

**Objectif.** Détecter, quantifier et anticiper la perte forestière à partir de
l'imagerie satellite Sentinel-2 et de techniques de Machine Learning.
**Méthodologie.** La démarche suit le cycle de vie d'un projet de science des
données : acquisition (Google Earth Engine), prétraitement (masquage des nuages,
indices spectraux NDVI/EVI/NDWI/NBR, composites de saison sèche), modélisation
supervisée (Random Forest, XGBoost, U-Net), évaluation par validation croisée
spatiale, puis déploiement (API FastAPI, tableaux de bord Streamlit et React).
**Résultats.** Sur le jeu de démonstration (données synthétiques réalistes
validant la chaîne de bout en bout), les trois modèles atteignent une exactitude
de 0,89 à 0,91 et un F1-macro de 0,86 à 0,89 ; un modèle de risque prédit les
fronts de déforestation avec une AUC de 0,83. La perte forestière cumulée simulée
sur 2015–2025 est traduite en émissions de CO₂ pour relier le résultat technique
au langage de la finance climat (REDD+). **Conclusion.** Le projet démontre qu'un
outil complet, prédictif et maîtrisé localement peut être conçu pour appuyer la
surveillance forestière ; ses résultats devront être confirmés sur images réelles
et vérité terrain.

**Mots-clés :** déforestation, télédétection, Sentinel-2, Machine Learning,
Random Forest, XGBoost, U-Net, NDVI, REDD+, Bassin du Congo, Mai-Ndombe, Data
Science.

### Abstract

The Democratic Republic of the Congo (DRC) holds the world's second-largest
tropical rainforest, in the heart of the Congo Basin. This equatorial ecosystem
faces accelerating, mostly diffuse deforestation that global platforms capture
poorly. This work designs and implements DeforestWatch-DRC, a deforestation
analysis and prediction platform for the Mai-Ndombe province. Using Sentinel-2
imagery and Machine Learning (Random Forest, XGBoost, U-Net), the system detects,
quantifies and anticipates forest loss, translates it into CO₂ emissions, and is
served through an API and interactive dashboards. On the demonstration dataset,
models reach 0.89–0.91 accuracy; a risk model forecasts deforestation fronts at
0.83 AUC. Results are to be confirmed on real imagery and ground truth.

---

## Sigles et abréviations

| Sigle | Signification |
|---|---|
| AGB | Above-Ground Biomass (biomasse aérienne) |
| API | Application Programming Interface |
| AUC | Area Under the ROC Curve |
| CAFI | Central African Forest Initiative |
| CNN | Convolutional Neural Network |
| EVI | Enhanced Vegetation Index |
| GEE | Google Earth Engine |
| GFC | Global Forest Change (Hansen) |
| ICCN | Institut Congolais pour la Conservation de la Nature |
| IoU | Intersection over Union |
| JWT | JSON Web Token |
| ML | Machine Learning |
| MRV | Measurement, Reporting and Verification |
| NBR | Normalized Burn Ratio |
| NDVI | Normalized Difference Vegetation Index |
| NDWI | Normalized Difference Water Index |
| NIR | Near Infrared (proche infrarouge) |
| RDC | République Démocratique du Congo |
| REDD+ | Reducing Emissions from Deforestation and forest Degradation |
| RF | Random Forest |
| SCL | Scene Classification Layer (Sentinel-2) |
| SRTM | Shuttle Radar Topography Mission |
| SWIR | Short-Wave Infrared |
| U-Net | Réseau de segmentation en U |
| 2FA | Two-Factor Authentication |

## Liste des figures et des tableaux

**Figures :** (1) localisation de la zone d'étude ; (2) architecture technique ;
(3) cycle de vie du projet de Data Science ; (4) évolution du couvert forestier
2015–2025 ; (5) cartes de classification ; (6) matrice de confusion ; (7) carte
de risque.

**Tableaux :** (1) sources de données ; (2) bandes et indices ; (3) classes de
couverture ; (4) jeu de features ; (5) dynamique annuelle du couvert ;
(6) comparaison des modèles ; (7) traduction en CO₂.

---

## Introduction générale

La surveillance des forêts tropicales est devenue un enjeu scientifique,
environnemental et géopolitique majeur. Le Bassin du Congo, dont la République
Démocratique du Congo constitue le cœur, forme le deuxième massif forestier
tropical de la planète et joue un rôle déterminant dans la régulation du climat
mondial, le stockage du carbone et la préservation de la biodiversité. Or ce
patrimoine s'érode : la perte de couvert progresse d'année en année, portée par
des dynamiques locales spécifiques.

Ce document est une monographie de projet de fin de cycle (Licence L3 LMD,
orientation Data Science). Il rend compte de la conception et de la réalisation
d'une plateforme, **DeforestWatch-DRC**, qui applique la télédétection et
l'apprentissage automatique à la surveillance de la déforestation dans la
province du Mai-Ndombe. Conformément au guide de rédaction de la FASI/UPC, il
s'organise en trois chapitres : (I) mise en contexte et revue de la littérature ;
(II) modélisation et méthodes de travail ; (III) résultats, discussion et
conclusion, suivis de la bibliographie et des annexes.

L'ambition du travail est double. Sur le plan technique, il s'agit de démontrer
qu'une chaîne complète — de la collecte des images satellites au déploiement d'un
outil d'aide à la décision — peut être construite, testée et maîtrisée. Sur le
plan de l'impact, il s'agit de montrer en quoi un tel outil, adapté au contexte
congolais et prédictif plutôt que seulement rétrospectif, apporte une plus-value
réelle aux acteurs de la conservation.

---

## Chapitre I — Mise en contexte et revue de la littérature

### 1.1. Introduction et mise en contexte

#### 1.1.1. Présentation du domaine et du sujet

Le sujet se situe à l'intersection de trois domaines : la télédétection
(observation de la Terre par satellite), la science des données et
l'environnement. Il porte sur la détection et la prédiction de la déforestation
dans la **forêt tropicale humide équatoriale du Bassin du Congo (Mai-Ndombe,
RDC)**. La télédétection optique, popularisée par les programmes Landsat
(NASA/USGS) puis Copernicus/Sentinel (ESA), fournit aujourd'hui des images
multispectrales gratuites et régulières permettant de cartographier le couvert
végétal à grande échelle. Couplée à l'apprentissage automatique, elle ouvre la
voie à des systèmes de surveillance fine et automatisée.

**État de l'art.** Les grandes plateformes de suivi forestier — Global Forest
Watch, le Global Forest Change de Hansen et al., ou les alertes RADD fondées sur
le radar — ont démocratisé l'accès à l'information sur la perte de forêt. Elles
restent toutefois pensées à l'échelle globale et sont d'abord rétrospectives :
elles documentent ce qui a déjà eu lieu, sans nécessairement anticiper les zones
menacées, ni s'adapter aux moteurs de déforestation propres à chaque territoire.

#### 1.1.2. Justification du choix du sujet

Le choix se justifie par sa pertinence à la fois académique et pratique. Sur le
plan académique, il mobilise l'ensemble des compétences de la Data Science :
acquisition et nettoyage de données spatiales volumineuses, ingénierie de
variables, comparaison rigoureuse de modèles et déploiement. Sur le plan
pratique, il répond à un besoin national : la RDC abrite environ 60 % de la forêt
du Bassin du Congo et figure parmi les premiers pays au monde pour la perte de
forêt primaire. La déforestation y est essentiellement diffuse — agriculture sur
brûlis de subsistance, charbon de bois (makala), exploitation artisanale — donc
composée de petites coupes mal captées par les outils globaux. Une approche
locale, fine et prédictive est requise. Le Mai-Ndombe, province pilote REDD+,
ajoute une dimension économique : y prouver la réduction de la déforestation
conditionne des paiements aux résultats.

### 1.2. Problématique et objectifs de la recherche

#### 1.2.1. Problématique

La question centrale est la suivante : **comment exploiter l'imagerie satellite
et le Machine Learning pour détecter, quantifier et anticiper la déforestation de
la forêt équatoriale du Mai-Ndombe, d'une manière adaptée au contexte
congolais ?** Elle se décline en trois sous-questions : (a) quels indices
spectraux et quels modèles permettent de discriminer fiablement les classes de
couverture du sol à partir de Sentinel-2 ? (b) parmi les familles de modèles
(ensembles d'arbres vs réseaux profonds), lesquelles offrent le meilleur
compromis performance/interprétabilité/coût ? (c) la déforestation future est-elle
spatialement prédictible à partir de variables de proximité (routes, villages,
fronts existants) ?

#### 1.2.2. Objectifs

Objectif général : concevoir et réaliser une plateforme opérationnelle de
surveillance et de prédiction de la déforestation. Objectifs spécifiques :

1. Détecter les zones déforestées par classification supervisée d'images
   Sentinel-2 en cinq classes de couverture du sol.
2. Quantifier la perte forestière année par année sur la période 2015–2025.
3. Comparer trois modèles (Random Forest, XGBoost, U-Net) et retenir le plus
   adapté.
4. Prédire les zones à risque de déforestation future (carte de risque).
5. Traduire la perte forestière en émissions de CO₂ (lien avec REDD+).
6. Livrer une plateforme d'aide à la décision : API, tableaux de bord et
   signalement citoyen.

#### 1.2.3. Hypothèses de recherche

- **H1** — Les indices spectraux dérivés de Sentinel-2 (NDVI, EVI, NBR, NDWI),
  combinés aux bandes brutes et à la topographie, permettent de discriminer les
  classes de couverture forestière avec une exactitude ≥ 0,80.
- **H2** — Un modèle d'ensemble (Random Forest / XGBoost), appliqué pixel par
  pixel, offre un compromis performance/interprétabilité au moins aussi favorable
  qu'un réseau convolutif (U-Net) sur cette zone.
- **H3** — La déforestation future est spatialement prédictible : un modèle de
  risque fondé sur des variables de proximité atteint une AUC ≥ 0,75.

### 1.3. Revue de la littérature théorique

#### 1.3.1. Télédétection et indices de végétation

La caractérisation de la végétation par satellite repose sur la réponse spectrale
des surfaces. La végétation chlorophyllienne absorbe fortement le rouge et
réfléchit fortement le proche infrarouge (NIR) : ce contraste fonde le **NDVI**
(Tucker, 1979), défini par `NDVI = (NIR − Rouge) / (NIR + Rouge)`. L'**EVI**
corrige l'influence du sol et de l'atmosphère ; le **NDWI** est sensible à l'eau
et à l'humidité ; le **NBR** met en évidence les surfaces brûlées. Ces indices
constituent des variables explicatives robustes pour distinguer forêt dense,
forêt dégradée et sol nu.

#### 1.3.2. Apprentissage automatique pour la classification d'images

Deux familles de modèles sont mobilisées. Les approches **pixel** traitent chaque
pixel comme un vecteur de variables : les forêts aléatoires (Random Forest,
Breiman 2001) agrègent de nombreux arbres décorrélés et fournissent une mesure
d'importance des variables ; le gradient boosting (XGBoost, Chen & Guestrin 2016)
construit les arbres séquentiellement pour corriger les erreurs résiduelles et
atteint souvent l'état de l'art sur données tabulaires. Les approches profondes
exploitent le contexte spatial : les réseaux de neurones convolutifs apprennent
des motifs de texture et de forme.

#### 1.3.3. Segmentation sémantique et architecture U-Net

Pour cartographier l'occupation du sol à la résolution du pixel tout en tenant
compte du voisinage, la segmentation sémantique est l'outil de référence.
L'architecture **U-Net** (Ronneberger et al., 2015), encodeur-décodeur symétrique
à connexions de saut, initialement conçue pour l'imagerie biomédicale, s'est
imposée en télédétection : elle restitue une carte de classes de même taille que
l'image d'entrée en combinant contexte global (encodeur) et localisation précise
(décodeur).

#### 1.3.4. Lacunes identifiées

Trois lacunes justifient ce travail. D'abord, la plupart des systèmes
opérationnels sont rétrospectifs et n'intègrent pas de dimension prédictive
locale. Ensuite, peu d'outils sont calibrés sur les moteurs spécifiques de la
déforestation congolaise (coupes diffuses) ni proposés en français et
appropriables localement. Enfin, la traduction directe de la perte forestière en
indicateurs de la finance climat (CO₂, crédits carbone) reste rare dans les
prototypes académiques, alors qu'elle conditionne l'usage réel en contexte REDD+.

### 1.4. Revue de la littérature empirique

Sur le plan empirique, les travaux de Hansen et al. (2013) ont produit les
premières cartes mondiales à haute résolution du changement de couvert forestier
(30 m, à partir de Landsat), établissant une référence de vérité terrain encore
largement utilisée. Le lancement de Sentinel-2 (Drusch et al., 2012) a apporté une
résolution de 10 m et une revisite de cinq jours. Google Earth Engine (Gorelick et
al., 2017) a rendu ces analyses accessibles à l'échelle planétaire sans
infrastructure locale lourde. De nombreuses études appliquées ont confirmé la
supériorité fréquente des méthodes d'ensemble et des CNN sur les classifieurs
classiques pour la cartographie forestière.

**Critique méthodologique et positionnement.** Ces travaux fournissent une base
méthodologique solide mais restent souvent génériques ou centrés sur d'autres
biomes (Amazonie, forêts boréales). Peu combinent, sur une même zone congolaise,
la classification, la prédiction du risque et la valorisation carbone au sein d'un
outil déployé. C'est le positionnement de DeforestWatch-DRC, qui se veut moins une
contribution algorithmique nouvelle qu'une **intégration cohérente et
contextualisée** de méthodes éprouvées, au service d'un besoin local.

---

## Chapitre II — Modélisation et méthodes de travail

Ce chapitre expose les choix méthodologiques et les modèles retenus. Conformément
aux attentes du guide pour les projets de Data Science, il justifie les approches,
décrit précisément les étapes pour en garantir la reproductibilité et explicite
les hypothèses et contraintes.

### 2.1. Démarche méthodologique

La méthodologie suit le cycle de vie structuré d'un projet de science des données,
inspiré de la démarche CRISP-DM :

1. **Compréhension du problème** — définition des objectifs et des classes.
2. **Acquisition** — images Sentinel-2 et variables auxiliaires via GEE.
3. **Exploration** — distributions spectrales et corrélations entre indices.
4. **Préparation** — masquage des nuages, composites, indices, extraction de
   features.
5. **Modélisation** — Random Forest, XGBoost, U-Net.
6. **Évaluation** — validation croisée spatiale et comparaison des métriques.
7. **Déploiement** — API et tableaux de bord.

### 2.2. Zone d'étude

La zone couvre environ 50 × 50 km (≈ 250 000 ha) autour d'Inongo, province du
Mai-Ndombe (−1,95° S ; 18,27° E), l'un des fronts de déforestation les plus actifs
de la forêt équatoriale congolaise. La pression provient de l'agriculture
itinérante et des concessions, avec une progression des fronts depuis les villages
et les axes de circulation.

### 2.3. Données et instruments de collecte

*Tableau 1 — Sources de données utilisées.*

| Source | Description | Résolution | Couverture |
|---|---|---|---|
| Sentinel-2 (ESA) | Images multispectrales (6 bandes) | 10 m | 2015–présent |
| Landsat 8/9 (NASA) | Images multispectrales | 30 m | 2013–présent |
| Hansen GFC | Perte forestière annuelle (vérité terrain) | 30 m | 2000–2023 |
| SRTM | Altitude, pente, aspect | 30 m | Global |
| OpenWeatherMap | Précipitations, température | — | Temps réel |

*Tableau 2 — Bandes spectrales Sentinel-2 et indices dérivés.*

| Bande / Indice | Description |
|---|---|
| B2, B3, B4 | Bleu, Vert, Rouge (visible) |
| B8 | Proche infrarouge (NIR, 842 nm) |
| B11, B12 | Infrarouge à ondes courtes (SWIR) |
| NDVI | `(NIR − Rouge)/(NIR + Rouge)` — vigueur de la végétation |
| EVI | Indice de végétation amélioré |
| NDWI | `(Vert − NIR)/(Vert + NIR)` — teneur en eau |
| NBR | `(NIR − SWIR2)/(NIR + SWIR2)` — surfaces brûlées |

### 2.4. Prétraitement et préparation des données

- Masquage des nuages et des ombres via la bande **SCL** de Sentinel-2,
  indispensable en zone équatoriale.
- Composites médians de **saison sèche** (juin–septembre) pour limiter la
  couverture nuageuse.
- Calcul vectorisé des indices NDVI, EVI, NDWI, NBR.
- Extraction de **13 variables par pixel** : 6 bandes + 4 indices + 3 variables
  topographiques.
- Découpage en tuiles 128 × 128 pour le U-Net.
- Découpage **spatial** (par blocs) train/val/test 70/15/15 % pour éviter la fuite
  géographique.

*Tableau 3 — Classes de couverture du sol.*

| Code | Classe |
|---|---|
| 0 | Forêt dense |
| 1 | Forêt dégradée |
| 2 | Agriculture / Sol nu |
| 3 | Eau |
| 4 | Zone urbaine / Bâti |

*Tableau 4 — Jeu de features par pixel (13 variables) :* 6 bandes (B2, B3, B4, B8,
B11, B12) + 4 indices (NDVI, EVI, NDWI, NBR) + 3 topographiques (altitude, pente,
aspect).

### 2.5. Modélisation

Trois modèles de classification sont comparés, complétés par un modèle de risque.

- **2.5.1. Random Forest (baseline interprétable).** Agrège *B* arbres entraînés
  sur des échantillons bootstrap et des sous-ensembles aléatoires de variables ;
  vote majoritaire. La décorrélation réduit la variance ; l'importance de Gini
  interprète les variables. Paramètres : 200 arbres, profondeur max 15.
- **2.5.2. XGBoost (gradient boosting).** Construit les arbres séquentiellement en
  minimisant une perte régularisée par descente de gradient ; capture des
  interactions fines. Paramètres : 200 arbres, profondeur 10, taux 0,1.
- **2.5.3. U-Net (segmentation).** Prend des tuiles 128 × 128 × 6 et produit une
  carte de classes de même dimension ; exploite le contexte spatial via
  l'encodeur-décodeur à connexions de saut.
- **2.5.4. Modèle de risque.** Gradient boosting binaire estimant, pour chaque
  pixel forestier, la probabilité d'être déforesté à court terme ; variables :
  distances (route, village, front), pente, altitude, taux du voisinage ; sortie
  0–100.
- **2.5.5. Protocole d'évaluation.** Accuracy, Precision, Recall, F1-macro,
  AUC-ROC, IoU par classe et Mean IoU ; matrice de confusion pour révéler les
  confusions entre classes voisines (forêt dégradée vs agriculture).

### 2.6. Développement et réalisation

La plateforme suit une architecture modulaire en Python 3.11 : collecte
(`src/data`), prétraitement (`src/preprocessing`), modélisation (`src/models`),
visualisation (`src/visualization`), analyse d'impact (`src/analysis`) et API
(`src/api`). Une couche d'abstraction des sources permet de basculer du mode
démonstration (données synthétiques) aux images réelles sans modifier le code
(déposer les GeoTIFF dans `data/raw/`, désactiver le mode démonstration).

| Composant | Technologie |
|---|---|
| Langage | Python 3.11 |
| Collecte satellite | Google Earth Engine, rasterio |
| Big Data | PySpark |
| ML classique | scikit-learn, XGBoost |
| Deep Learning | TensorFlow / Keras (U-Net) |
| API | FastAPI (JWT + 2FA) |
| Tableaux de bord | Streamlit + React (Vite / Tailwind) |
| Base de données | PostgreSQL / Supabase (repli SQLite) |
| Conteneurisation | Docker, docker-compose |
| Tests / CI | pytest, GitHub Actions |

**Sécurité et robustesse.** Hachage bcrypt des mots de passe, jetons JWT (accès +
rafraîchissement), OTP 2FA compatible Google Authenticator, contrôle d'accès par
rôle. Chaque dépendance lourde dispose d'un repli automatique (GradientBoosting si
XGBoost absent, centroïdes spectraux si TensorFlow absent, SQLite si PostgreSQL
indisponible), garantissant le fonctionnement dans tout environnement.

### 2.7. Contraintes et hypothèses de travail

- Les données doivent être représentatives et suffisantes pour l'apprentissage
  supervisé.
- La couverture nuageuse équatoriale limite la disponibilité des images optiques
  (d'où les composites et, en perspective, le radar).
- Les résultats du chapitre III proviennent du mode démonstration et devront être
  confirmés sur images réelles et vérité terrain.

---

## Chapitre III — Résultats, discussion et conclusion

> **Avertissement méthodologique.** Les chiffres ci-dessous proviennent de
> l'exécution de la plateforme en **mode démonstration**, sur des données
> synthétiques réalistes reproduisant la dynamique observée au Mai-Ndombe
> (avancée d'un front agricole depuis les villages et les routes). Ils valident la
> chaîne de bout en bout et illustrent les livrables ; ils seront remplacés par
> les résultats sur images Sentinel-2 réelles une fois la collecte effectuée.

### 3.1. Résultats

#### 3.1.1. Dynamique de la couverture forestière

*Tableau 5 — Dynamique annuelle de la couverture forestière.*

| Année | Forêt (ha) | Perte (ha) | Taux (%) |
|---|---|---|---|
| 2015 | 224 945 | 0 | 0,00 |
| 2016 | 213 421 | 11 524 | 5,12 |
| 2017 | 197 990 | 15 430 | 7,23 |
| 2018 | 179 718 | 18 272 | 9,23 |
| 2019 | 158 668 | 21 050 | 11,71 |
| 2020 | 137 794 | 20 874 | 13,16 |
| 2021 | 116 100 | 21 694 | 15,74 |
| 2022 | 95 894 | 20 206 | 17,40 |
| 2023 | 76 870 | 19 024 | 19,84 |
| 2024 | 60 265 | 16 605 | 21,60 |
| 2025 | 46 040 | 14 225 | 23,60 |

Sur 2015–2025, la couverture forestière simulée passe de 224 945 ha à 46 040 ha,
soit une perte cumulée d'environ **178 906 ha (≈ 80 % du couvert initial)**. Le
taux annuel croît régulièrement, traduisant l'accélération du front agricole à
mesure qu'il s'éloigne des villages et suit les axes de circulation.

#### 3.1.2. Comparaison des modèles

*Tableau 6 — Comparaison des performances des modèles (mode démonstration).*

| Modèle | Accuracy | Precision | Recall | F1-macro | AUC-ROC | Mean IoU |
|---|---|---|---|---|---|---|
| Random Forest | 0,89 | 0,87 | 0,86 | 0,86 | 0,94 | 0,78 |
| XGBoost | 0,90 | 0,88 | 0,88 | 0,88 | 0,95 | 0,80 |
| U-Net (CNN) | 0,91 | 0,90 | 0,89 | 0,89 | 0,96 | 0,82 |

Les trois modèles atteignent une exactitude comprise entre 0,89 et 0,91. Le U-Net
obtient les meilleures métriques brutes (F1-macro 0,89 ; Mean IoU 0,82) grâce au
contexte spatial, suivi de près par XGBoost. Le Random Forest reste légèrement en
retrait mais demeure la référence la plus interprétable. Le **modèle de risque
atteint une AUC de 0,83**, confirmant que la proximité aux routes, villages et
fronts existants est fortement prédictive.

#### 3.1.3. Traduction en émissions de CO₂

*Tableau 7 — Traduction de la perte forestière en émissions de CO₂.*

| Indicateur | Valeur |
|---|---|
| Biomasse aérienne moyenne (AGB) | 310 t/ha |
| Fraction de carbone (IPCC) | 0,47 |
| CO₂ émis par hectare détruit | ≈ 534 t/ha |
| Perte forestière 2015–2025 | ≈ 178 906 ha |
| Émissions de CO₂ associées | **≈ 95,6 Mt CO₂** |

En appliquant un facteur d'émission dérivé de la biomasse aérienne moyenne d'une
forêt dense du Bassin du Congo, la perte simulée correspond à environ **96 millions
de tonnes de CO₂**. Cette conversion relie directement le résultat technique au
langage de la finance climat (MRV, crédits carbone), essentiel dans une province
pilote REDD+.

### 3.2. Discussion

#### 3.2.1. Validation des hypothèses

- **H1** (exactitude ≥ 0,80) — **validée** : tous les modèles dépassent 0,89.
- **H2** (compromis des modèles d'ensemble) — **partiellement validée** : RF et
  XGBoost sont très proches du U-Net pour un coût et une interprétabilité bien
  supérieurs ; le U-Net ne prend l'avantage que sur les métriques spatiales (IoU).
- **H3** (AUC ≥ 0,75) — **validée** : le modèle de risque atteint 0,83.

#### 3.2.2. Mise en perspective et implications

Ces résultats sont cohérents avec la littérature (performances élevées des
méthodes d'ensemble et des CNN pour la cartographie forestière). La valeur ajoutée
de DeforestWatch-DRC ne réside pas dans une innovation algorithmique mais dans
l'**intégration** : passage d'un outil de constat à un outil d'action, via la
carte de risque prédictive, la remontée d'information citoyenne, la valorisation
carbone et une interface en français appropriable localement. Bénéficiaires :
Ministère de l'Environnement (brique d'un système national MRV), gardes forestiers
(alertes géolocalisées), gouvernement provincial, communautés locales, porteurs de
projets carbone.

#### 3.2.3. Points forts et faiblesses

**Points forts :** chaîne complète et reproductible, architecture modulaire avec
replis robustes, tests automatisés et intégration continue, contextualisation
congolaise. **Faiblesses :** résultats encore issus du mode démonstration, absence
de vérité terrain GPS, dépendance à la disponibilité des images optiques.

### 3.3. Conclusion générale

Ce travail a abouti à une plateforme complète et fonctionnelle de surveillance et
de prédiction de la déforestation de la forêt équatoriale du Mai-Ndombe, couvrant
toute la chaîne de valeur de la Data Science, de la collecte satellite au
déploiement d'un tableau de bord d'aide à la décision. Les trois hypothèses sont
vérifiées sur le jeu de démonstration. La contribution principale est une
intégration cohérente et contextualisée de méthodes éprouvées, assortie d'une
dimension prédictive et d'une valorisation carbone qui en font un outil orienté
vers l'action.

### 3.4. Limites de l'étude

- Couverture nuageuse équatoriale limitant la disponibilité des images optiques.
- Besoin de données de vérité terrain de qualité pour l'apprentissage supervisé.
- Résultats de démonstration à confirmer sur données réelles.
- Enjeux d'accès aux données, de connectivité et de maintenance dans la durée.

### 3.5. Suggestions pour des recherches futures

- Intégration de l'imagerie radar **Sentinel-1** (insensible aux nuages).
- Modèles spatio-temporels (ConvLSTM, transformers) pour la prédiction du risque.
- Système d'alertes en temps quasi réel pour les gestionnaires forestiers.
- Validation sur points GPS de terrain et calibration avec Hansen GFC.
- Extension à d'autres provinces de la forêt équatoriale congolaise.

---

## Bibliographie

1. Breiman, L. (2001). *Random Forests.* Machine Learning, 45(1), 5–32.
2. Chen, T., & Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System.*
   Proceedings of the 22nd ACM SIGKDD, 785–794.
3. Drusch, M., et al. (2012). *Sentinel-2: ESA's Optical High-Resolution Mission
   for GMES Operational Services.* Remote Sensing of Environment, 120, 25–36.
4. FAO (2020). *Global Forest Resources Assessment 2020.* Rome.
5. Gorelick, N., et al. (2017). *Google Earth Engine: Planetary-scale geospatial
   analysis for everyone.* Remote Sensing of Environment, 202, 18–27.
6. Hansen, M. C., et al. (2013). *High-Resolution Global Maps of 21st-Century
   Forest Cover Change.* Science, 342(6160), 850–853.
7. IPCC (2006). *Guidelines for National Greenhouse Gas Inventories, Vol. 4.*
   Genève : GIEC.
8. Ronneberger, O., Fischer, P., & Brox, T. (2015). *U-Net: Convolutional Networks
   for Biomedical Image Segmentation.* MICCAI, 234–241.
9. Tucker, C. J. (1979). *Red and photographic infrared linear combinations for
   monitoring vegetation.* Remote Sensing of Environment, 8(2), 127–150.

## Webiographie

1. Global Forest Watch — <https://www.globalforestwatch.org> [consulté le 10 juillet 2026].
2. Copernicus / Sentinel-2 (ESA) — <https://sentinels.copernicus.eu> [consulté le 10 juillet 2026].
3. Google Earth Engine — <https://earthengine.google.com> [consulté le 10 juillet 2026].
4. Central African Forest Initiative (CAFI) — <https://www.cafi.org> [consulté le 10 juillet 2026].

---

## Annexes

**Annexe A — Structure du dépôt de code.** `config/`, `src/{data, preprocessing,
models, visualization, analysis, api, utils}`, `streamlit_app/`, `frontend/`,
`notebooks/`, `scripts/`, `tests/`, `data/{raw, processed, models}`, `docs/`.

**Annexe B — Lancement (mode démonstration).**
- `make seed` — données de démonstration + entraînement des modèles.
- `make api` — API FastAPI (http://localhost:8000/docs).
- `make dashboard` — tableau de bord Streamlit (http://localhost:8501).
- `make frontend` — frontend React (http://localhost:5173).
- `make test` — suite de tests pytest.
- `make monograph` — génère la présente monographie (.docx).

**Annexe C — Principaux points d'entrée de l'API.**
- `POST /api/v1/auth/register`, `/auth/login`, `/auth/verify-otp` — authentification + 2FA.
- `GET /api/v1/statistics` — perte forestière par année.
- `GET /api/v1/predictions/{year}` — synthèse des zones à risque.
- `GET /api/v1/models` — performances des modèles.
- `GET /api/v1/carbon` — émissions de CO₂ et équivalences.
- `GET /api/v1/alerts` — alertes de déforestation détectées.
- `POST /api/v1/reports` — signalement citoyen de déforestation.
- `GET /api/v1/admin/users`, `/admin/logs` — back-office (administrateur).

**Annexe D — Captures d'écran.** [Insérer les captures du tableau de bord
Streamlit, de la documentation Swagger de l'API, du frontend React « CongoForest
Watch » et de la machine à remonter le temps (time-lapse 2015–2025).]
