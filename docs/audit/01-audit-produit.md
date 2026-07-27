# 01 — Audit du produit actuel

> Audit sévère, fondé sur la lecture intégrale du code et l'exécution du système.
> Chaque reproche est référencé à un fichier et une ligne.

---

## 1. Points forts

| # | Force | Pourquoi ça compte commercialement |
|---|---|---|
| F1 | **Abstraction de source de données** (`src/data/sources.py`, `src/data/provider.py`) | Le basculement démo → réel ne demande pas de réécriture. C'est *l'*actif technique du projet. |
| F2 | **Split spatial par blocs** (`dataset_builder.py:26-40`) | Évite la fuite par autocorrélation spatiale. Marqueur de rigueur que 80 % des concurrents académiques n'ont pas. |
| F3 | **Séparation en couches propre** | `data` / `preprocessing` / `models` / `analysis` / `api` / `visualization`. Refactorable vers des microservices sans démolition. |
| F4 | **49 tests qui passent, CI GitHub Actions, Docker, docker-compose** ✅ vérifié | Rare à ce stade. Base saine pour industrialiser. |
| F5 | **Trois cibles d'interface** (Streamlit, React, API) | Permet de tester plusieurs segments avant de figer l'UX. |
| F6 | **Documentation dense en français** | Différenciant réel sur les appels d'offres francophones (RDC, Cameroun, Gabon, Congo, RCA). |
| F7 | **Repli systématique** | Le produit démarre partout, toujours. Excellent en démonstration terrain sans réseau. |
| F8 | **Modèle carbone explicite** (`carbon.py`) | Les hypothèses (AGB, fraction carbone IPCC, ratio 44/12) sont exposées dans la réponse API. C'est la bonne pratique — la plupart des concurrents cachent leurs facteurs. |

---

## 2. Points faibles — techniques

### 2.1 Le cœur : il n'y a pas de télédétection dans ce logiciel de télédétection

C'est le constat central. Détail de la chaîne réelle :

```
generate_landcover_series()          ← 3 villages + 1 route diagonale (xx-yy<4) + bruit gaussien
        │
        ▼
landcover_to_bands()                 ← 5 signatures spectrales codées en dur + N(0, 0.045)
        │
        ├──► compute_indices_array() ← NDVI/EVI/NDWI/NBR sur des bandes inventées
        ├──► yearly_statistics()     ← statistiques de déforestation « officielles »
        ├──► alerts.detect_alerts()  ← alertes géolocalisées
        ├──► carbon.yearly_carbon()  ← tonnes de CO₂ annoncées
        ├──► synthetic.risk_map()    ← carte de « prédiction »
        └──► frontend/public/demo/*  ← captures du produit vendu
```

Le commentaire `synthetic.py:98-100` est explicite :

```python
# bruit spectral marqué => classes partiellement chevauchantes
# (rend la comparaison de modèles réaliste, métriques ~0.80-0.92)
```

**Le niveau de bruit a été réglé pour produire les métriques attendues.** En contexte
académique, c'est un artifice de démonstration assumé. En contexte commercial, présenter
ces chiffres comme des performances produit serait une déclaration trompeuse — avec un
risque réputationnel et, sur un marché carbone, un risque juridique.

**Conséquence directe :** les scores 0,80–0,92 mesurent la séparabilité de gaussiennes
dont les paramètres sont connus. Sur du Sentinel-2 réel au Mai-Ndombe, avec 60–80 % de
couverture nuageuse annuelle, une confusion forêt dense / forêt secondaire / jachère
arbustive massive et aucune vérité terrain, **attendez-vous à 0,55–0,70 de F1 macro au
premier essai.** Ce n'est pas un échec — c'est le vrai point de départ.

### 2.2 Résolution et géométrie : une incohérence structurelle

| Élément | Annoncé | Réel dans le code |
|---|---|---|
| Résolution | Sentinel-2, 10 m | `GRID_SIZE = 256` pour 50 km → **195,3 m/pixel** |
| Surface pixel | — | `PIXEL_AREA_HA = 3,8147` ha |
| Détection min. théorique | « exploitation illégale » | ~3,8 ha pour 1 pixel ; ~34 ha pour un objet robuste (3×3) |

Une coupe artisanale au Mai-Ndombe fait typiquement 0,5 à 2 ha. **Elle est
structurellement indétectable** dans la configuration actuelle. Un client
« lutte contre l'exploitation illégale » le découvrira à la première mission de terrain.

Passer à 10 m sur la même emprise, c'est 5 000 × 5 000 = **25 millions de pixels par
année**, soit 380 fois le volume actuel. Rien dans le code ne tient à cette échelle :
tout est en `numpy` en mémoire, sans tuilage, sans dask, sans COG, sans pyramide.

### 2.3 Absence totale de couche SIG

Pour un produit dont le « G » de SIG est dans la promesse :

- ❌ Aucun CRS, aucune reprojection, aucun `pyproj` utilisé (bien qu'en dépendance)
- ❌ Aucun `GeoDataFrame`, aucun vecteur, aucun shapefile/GeoPackage
- ❌ PostGIS absent — `database.py` n'a que des colonnes `Float` lat/lon
- ❌ Pas de gestion du nodata, ni du rééchantillonnage, ni de l'alignement inter-dates
- ❌ `_sector_center_latlon()` (`alerts.py:53-64`) interpole linéairement dans une bbox :
  approximation plan carré, acceptable à ±2° de l'équateur, **fausse partout ailleurs**,
  et non documentée comme approximation
- ❌ `bbox_from_center(lat, lon, km)` : conversion km → degrés sans tenir compte de la
  latitude pour la longitude au-delà de l'équateur

Un acheteur SIG (cadastre forestier, ICCN, ministère) écartera le produit à la
première question sur le système de coordonnées.

### 2.4 Sécurité — détail des failles

| Réf. | Faille | Fichier | Gravité | Correctif |
|---|---|---|---|---|
| S1 | 2FA jamais enforcée : `/auth/login` émet le JWT sans OTP ✅ vérifié | `routes.py:60-68` | 🔴 | Login en 2 temps : `login` → `pending_token` (5 min, scope `otp`) → `verify-otp` → JWT final |
| S2 | Admin `admin123` seedé même hors démo ✅ vérifié | `main.py:44-58` | 🔴 | Conditionner à `demo_mode`, forcer un mot de passe au 1er démarrage |
| S3 | Secret JWT par défaut exploitable | `settings.py:34` | 🔴 | Refuser le démarrage si `app_env != development` et secret par défaut |
| S4 | `CORS: *` + `allow_credentials=True` | `main.py:29-35` | 🔴 | Liste blanche d'origines par environnement |
| S5 | Aucun rate-limiting nulle part | global | 🔴 | `slowapi` / WAF ; 5 tentatives login / 15 min / IP |
| S6 | `POST /reports` ouvert et non limité ✅ vérifié | `routes.py:201-209` | 🟠 | Auth ou captcha + quota + modération |
| S7 | `refresh_token` passé en **query param** → journalisé par tous les proxys et logs d'accès | `routes.py:79-90` | 🟠 | Body JSON ou cookie `HttpOnly` `SameSite=Strict` |
| S8 | Aucune révocation de token, aucune liste noire, refresh 7 j non rotatif | `auth.py:63-64` | 🟠 | Rotation + `jti` + table de révocation Redis |
| S9 | Token en `localStorage` → vol par XSS | `Login.jsx:52-53` | 🟠 | Cookie `HttpOnly` + CSRF token |
| S10 | 2FA côté React purement cosmétique : `/^\d{6}$/` puis appel API qui ignore l'OTP | `Login.jsx:31-51` | 🔴 | Supprimer le repli démo des builds de production |
| S11 | Identifiants de démo affichés en clair dans l'UI, le README et le code | partout | 🟠 | Variables d'environnement, jamais en dur |
| S12 | Aucune politique de mot de passe (`secret1` accepté dans les tests) | `schemas.py` | 🟠 | Longueur ≥ 12, vérification HIBP, blocage progressif |
| S13 | Middleware de log : session DB **synchrone** dans un middleware `async`, une transaction par requête, sur `except: pass` | `main.py:61-76` | 🟠 | Journalisation asynchrone en file (Redis/Kafka), table partitionnée + rétention |
| S14 | `ApiLog` sans purge → croissance illimitée, pas d'index sur `timestamp` | `database.py:70-77` | 🟡 | Partitionnement mensuel + TTL |
| S15 | Handler d'exception global masque toutes les erreurs sans corrélation ID | `main.py:79-82` | 🟡 | `X-Request-ID`, Sentry, pas de fuite de stack |
| S16 | Aucun audit trail immuable (qui a vu/modifié/validé quoi) | absent | 🔴 pour le marché visé | Journal append-only signé |
| S17 | Aucun chiffrement au repos, aucune gestion de secrets (Vault/KMS) | absent | 🟠 | Vault + chiffrement colonne pour PII |
| S18 | `docker-compose` : port PostgreSQL 5432 exposé sur l'hôte, mot de passe par défaut | `docker-compose.yml` | 🟠 | Réseau interne uniquement |
| S19 | Conteneur exécuté en `root`, image non multi-stage, pas de scan de vulnérabilités | `Dockerfile` | 🟠 | User non-privilégié, distroless, Trivy en CI |
| S20 | Aucun `SECURITY.md`, aucune procédure de divulgation | absent | 🟡 | Prérequis appel d'offres |

> **À retenir :** l'authentification à deux facteurs, mise en avant dans le README,
> le mémoire et la page de connexion, **n'existe pas**. C'est de la sécurité théâtrale.
> Sur un produit destiné à des administrations, c'est le type de constat qui met fin
> à une procédure d'achat.

### 2.5 Dette technique et bugs

| Réf. | Problème | Fichier |
|---|---|---|
| D1 | **Erreur d'unité ×100** sur `high_risk_ha` ✅ vérifié | `routes.py:155` |
| D2 | `RadarCollector.annual_composite()` construit la requête GEE puis retourne du synthétique | `radar.py:93-96` |
| D3 | `cloud_penetration_demo()` : `radar_usable_pct = 100.0` codé en dur — physiquement faux (ombres de relief, layover, speckle) | `radar.py:111` |
| D4 | `_edt()` : « distance euclidienne » calculée par dilatation 4-connexe → c'est une **distance de Manhattan**, erreur jusqu'à 41 % en diagonale. Nom trompeur, features de risque biaisées | `risk_predictor.py:59-74` |
| D5 | `RiskPredictor` ignore la source active : appelle `synthetic.generate_landcover_series()` en dur, avec des villages et une route codés en dur. **Inutilisable sur données réelles.** | `risk_predictor.py:31-50` |
| D6 | `train()` force artificiellement des positifs si `y.sum() == 0` — le modèle apprend du bruit fabriqué plutôt que d'échouer proprement | `risk_predictor.py:104-105` |
| D7 | `train_accuracy` reporté **sur le train set** ; aucune validation, aucun AUC/PR, sur données massivement déséquilibrées | `risk_predictor.py:107` |
| D8 | `provider.landcover_series()` retombe **silencieusement** sur le synthétique si les vraies images n'ont pas d'étiquettes | `provider.py:66-68` |
| D9 | `build_pixel_splits()` n'utilise qu'**une seule année** — aucune dimension temporelle dans le modèle de classification | `dataset_builder.py:50-51` |
| D10 | `build_tile_splits()` : split **aléatoire** des tuiles alors que `_real_tiles` génère un recouvrement de 32 px → fuite train/test garantie sur données réelles | `dataset_builder.py:84-92` |
| D11 | Cache de source global mutable (`_cached_source`, `_forced_mode`) : non thread-safe, incompatible avec plusieurs workers uvicorn — le toggle admin n'affecte qu'un worker | `sources.py:170-176` |
| D12 | `datetime.utcnow()` déprécié (Python 3.12+), naïf, sans fuseau | `auth.py:54`, `database.py` |
| D13 | `@app.on_event("startup")` déprécié depuis FastAPI 0.93 | `main.py:38` |
| D14 | Aucune migration Alembic malgré la dépendance déclarée ; `create_all()` en production | `database.py:111-113` |
| D15 | Le pipeline PySpark tourne sur **un dataset en mémoire converti en DataFrame** — aucun bénéfice Big Data, coût d'exploitation pur. Justification académique, pas technique | `spark_pipeline.py:24-31` |
| D16 | Aucun versionnage de modèle actif : `ModelRegistry` existe en base et **n'est jamais écrit** | `database.py:80-89` |
| D17 | `requirements.txt` : `GDAL==3.8.3` en pip échoue sans libgdal identique — installation non reproductible hors Docker | `requirements.txt` |
| D18 | TensorFlow 2.15 + Keras 2.15 + numpy 1.26 : pile figée fin 2023, déjà 2 ans de retard sur les correctifs de sécurité | `requirements.txt` |
| D19 | `files/` versionné : `.zip`, `.docx`, `.DS_Store`, un `settings.py` dupliqué, un `Dockerfile` dupliqué | `files/` |
| D20 | `.DS_Store` commité à la racine malgré le `.gitignore` | racine |
| D21 | ~3 200 lignes de scripts de génération de documents (`generate_synthese_technique.py` : 1 292 lignes) — soit **33 % du code du dépôt** consacré au livrable académique, pas au produit | `scripts/` |
| D22 | Trois frontends à maintenir (Streamlit, React, `public/demo/*.json` figés) sans source de vérité unique | global |
| D23 | Le frontend React embarque des JSON de démo générés — le « produit » vendu sur Vercel n'appelle aucune API | `frontend/public/demo/` |

### 2.6 Ce qui manque totalement à l'infrastructure

Aucune trace, dans tout le dépôt, de : orchestration de traitements (Airflow/Prefect/
Dagster) · file de messages · cache · stockage objet · tuilage raster / COG / serveur de
tuiles · monitoring (Prometheus/Grafana) · logs centralisés · traces distribuées ·
sauvegardes · plan de reprise · IaC (Terraform) · Kubernetes · gestion de secrets ·
tests de charge · tests E2E · feature flags · gestion multi-tenant · facturation ·
quotas · versionnage d'API.

Le `docker-compose` à deux services (app + postgres) est un environnement de
développement, pas une architecture de production.

---

## 3. Points faibles — UX / produit

| # | Problème | Impact |
|---|---|---|
| U1 | **Trois interfaces concurrentes** sans hiérarchie : Streamlit (complet), React (vitrine), et un frontend statique. Le client ne sait pas quel est le produit. | 🔴 |
| U2 | **Aucune carte réellement interactive.** Les cartes sont des **PNG servis par l'API** (`_png()`, `routes.py:30-37`). Pas de zoom, pas de pan, pas de clic, pas de couche, pas de fond de plan, pas d'échelle, pas de légende dynamique, pas de coordonnées au survol. C'est une image, pas un SIG. | 🔴 |
| U3 | `Image.NEAREST` upscale 256 → 512 px : la carte est **visiblement pixelisée**. Premier signal de qualité perçue, et il est mauvais. | 🟠 |
| U4 | Aucun onboarding, aucun tutoriel, aucune aide contextuelle, aucun état vide travaillé. | 🟠 |
| U5 | Aucune gestion d'erreur côté utilisateur : une API en échec produit un écran cassé ou un repli silencieux sur des données fausses. | 🔴 |
| U6 | Aucune accessibilité : contrastes non vérifiés, pas de navigation clavier, pas d'ARIA, palette verte/rouge inaccessible aux daltoniens (8 % des hommes) — sur un produit dont **tout** le code couleur est vert/rouge. | 🟠 |
| U7 | Interface uniquement en français. Ni anglais (bailleurs, ONG internationales), ni lingala/swahili (agents de terrain). | 🟠 |
| U8 | Aucun responsive mobile sérieux, aucune app native, aucun mode hors-ligne — alors que **la cible primaire est un agent forestier en zone sans réseau**. | 🔴 |
| U9 | Aucun export : ni PDF, ni Excel, ni GeoJSON, ni shapefile, ni KML. Un utilisateur institutionnel ne peut rien sortir du produit. | 🔴 |
| U10 | Aucune notion de temps réel : la donnée la plus récente est une **agrégation annuelle**. Pour l'usage « intervention », c'est 364 jours de retard dans le pire cas. | 🔴 |
| U11 | Aucune personnalisation : pas de zone d'intérêt définissable par l'utilisateur, seuils codés en dur (`DEFAULT_THRESHOLD_HA = 400`). Un client ne peut pas surveiller *sa* concession. | 🔴 |
| U12 | Le mot « démo » est visible partout dans l'interface vendue. | 🟠 |
| U13 | Pas de design system, pas de composants réutilisables, styles inline dans le Streamlit. | 🟡 |

> **U11 mérite d'être souligné :** un produit de surveillance où l'utilisateur ne peut
> pas définir la zone qu'il surveille n'est pas un produit de surveillance. C'est une
> visualisation d'une zone choisie par l'éditeur.

---

## 4. Limites scientifiques

| # | Limite | Sévérité |
|---|---|---|
| Sc1 | **Aucune vérité terrain.** Ni relevés GPS, ni photo-interprétation, ni points de contrôle, ni protocole d'échantillonnage. Impossible de calculer une précision au sens Olofsson et al. (2014), qui est **la** référence méthodologique du domaine. | 🔴 |
| Sc2 | **Aucune quantification d'incertitude.** Ni intervalles de confiance, ni calibration des probabilités, ni propagation d'erreur vers les surfaces et le carbone. Un chiffre de CO₂ sans barre d'erreur n'est pas recevable pour Verra, ART-TREES ou un auditeur. | 🔴 |
| Sc3 | **Aucune validation croisée temporelle.** Le modèle de risque est entraîné et évalué sur la même série. Aucun test « entraîner sur 2015-2020, prédire 2021-2023, comparer au réel ». C'est le seul test qui prouverait la valeur de la prédiction. | 🔴 |
| Sc4 | **Aucune comparaison à une référence externe.** Pas de confrontation à Hansen/GFC, GLAD, RADD, DETER, TMF (JRC), ESA WorldCover, Dynamic World. Impossible de démontrer un apport. | 🔴 |
| Sc5 | **Aucune correction atmosphérique réelle, aucune normalisation BRDF, aucune harmonisation inter-capteurs.** Les composites annuels médians masquent la saisonnalité (saison sèche vs humide) qui domine le signal NDVI en zone équatoriale. | 🟠 |
| Sc6 | **Traitement des nuages fictif.** `synthetic_scl()` génère un masque aléatoire. Au Mai-Ndombe, la couverture nuageuse réelle est persistante, spatialement structurée et corrélée à la saison — pas un tirage uniforme. La disponibilité optique est **le** verrou du Bassin du Congo, et il est simulé. | 🔴 |
| Sc7 | **Modèle carbone rudimentaire.** `AGB = 310 t/ha` uniforme, sans biomasse souterraine (racines, ~+24 %), sans carbone du sol, sans bois mort, sans litière, sans carte de biomasse spatialisée (GEDI, ESA CCI Biomass, Baccini, Avitabile), sans distinction dégradation/déforestation, sans intervalle. **Non conforme aux méthodologies VM0048 / ART-TREES / GIEC.** Le module est honnête sur ses hypothèses, mais les hypothèses sont trop grossières pour le marché carbone. | 🔴 |
| Sc8 | **Les 5 classes de couverture sont insuffisantes.** Manquent : forêt marécageuse (or les tourbières de la Cuvette centrale — dont le Mai-Ndombe est proche — sont le plus grand stock de carbone tropical du monde), savane, mosaïque agriculture-forêt, plantation, sol nu minier, forêt secondaire par âge. La distinction **dégradation vs déforestation** — celle qui compte pour le carbone — n'est pas opérationnalisée. | 🔴 |
| Sc9 | **Pas de détection de changement à proprement parler.** L'approche est « classifier chaque année puis différencier », qui accumule les erreurs des deux classifications (une erreur de 5 % par an → ~10 % sur le changement). Les méthodes de référence sont temporelles : LandTrendr, CCDC, BFAST, CuSum. | 🔴 |
| Sc10 | **Le modèle de risque est un modèle de distance déguisé.** 3 des 6 features sont des distances, et la cible (« forêt déforestée l'an prochain ») est générée par un processus de distance. Le modèle apprend l'identité. Toute performance mesurée est circulaire. | 🔴 |
| Sc11 | Aucun facteur socio-économique dans le risque : démographie, prix des commodités, routes réelles (OSM), concessions, titres miniers, conflits, déplacements de population, accessibilité fluviale. Or ces facteurs dominent la littérature. | 🟠 |
| Sc12 | Aucune reproductibilité : pas de DVC, pas de MLflow, pas de hash de dataset, pas de model card, pas de graine gérée globalement. | 🟠 |
| Sc13 | Aucune publication, aucun préprint, aucun jeu de données ouvert. Zéro capital scientifique opposable. | 🟠 |

---

## 5. Limites commerciales

| # | Limite |
|---|---|
| C1 | **Aucun client, aucun pilote, aucune LOI, aucune preuve d'usage.** |
| C2 | **Aucun modèle économique implémenté** : pas de plans, pas de facturation, pas de quotas, pas de multi-tenant. L'architecture actuelle est mono-organisation — le multi-tenant est une refonte, pas une option. |
| C3 | **Aucune personne morale, aucune PI formalisée** (dépôt de marque, cession de droits, licence). Un projet universitaire peut relever d'un règlement de propriété intellectuelle de l'établissement : **à vérifier avant toute levée**. |
| C4 | **Aucune conformité** : ni RGPD (registre, DPO, DPA, base légale, politique de conservation), ni ISO 27001, ni SOC 2. Bloquant pour la Banque mondiale, l'UE, la FAO, le GIZ. |
| C5 | **Aucun SLA, aucun support, aucune astreinte, aucun statut de service.** |
| C6 | **Positionnement flou** : le brief vise gouvernements + ONG + forestiers + miniers + organismes internationaux + chercheurs. Six segments aux besoins contradictoires. Un produit qui parle à tout le monde ne convainc personne. |
| C7 | **Concurrence gratuite et supérieure** sur la fonction principale (GFW). Il faut une raison de payer qui ne soit pas « la carte ». |
| C8 | **Marché à cycle de vente long** : 9 à 18 mois en institutionnel africain, paiements différés, risque de change, exigences de présence locale. Besoin de 24 mois de trésorerie. |
| C9 | **Coût d'imagerie non modélisé.** Sentinel/Landsat sont gratuits, mais Planet, Airbus, Maxar coûtent de 1 à 20 $/km². Sans modèle de coût, la marge est inconnue et le pricing arbitraire. |
| C10 | **Dépendance à Google Earth Engine.** Gratuit en usage non commercial, **payant et sous conditions en usage commercial**. Un produit commercial adossé à GEE a un risque fournisseur majeur et une structure de coût non maîtrisée. À arbitrer tôt. |
| C11 | **Aucune stratégie de données propriétaires.** Sans jeu de vérité terrain exclusif, il n'y a pas de barrière à l'entrée : n'importe qui peut reproduire le produit avec les mêmes données publiques. **C'est le point le plus important de tout cet audit sur le plan de la valorisation.** |
| C12 | Aucun canal d'acquisition, aucune présence institutionnelle (COMIFAC, OFAC, OSFAC, CAFI, ICCN, ministère de l'Environnement RDC), aucune référence. |

---

## 6. Risques

| Réf. | Risque | Prob. | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **Un client découvre que les données sont synthétiques** | Élevée | Fatal | Sprint 0 : bannière « MODE DÉMONSTRATION » non masquable ; jamais de démo sans mention explicite |
| R2 | Fuite de données via B1/B2/B9 sur un déploiement public | **Très élevée** | Grave | Sprint 0 |
| R3 | Une alerte fausse déclenche une intervention injustifiée (saisie, poursuite) | Moyenne | Grave — juridique et humain | Validation humaine obligatoire avant tout usage coercitif ; CGU limitant la responsabilité ; niveaux de confiance explicites |
| R4 | **Un chiffre carbone erroné utilisé dans une transaction** | Moyenne | Fatal | Ne pas commercialiser le module carbone avant conformité méthodologique et audit tiers |
| R5 | GFW ou MapBiomas lance une déclinaison Bassin du Congo | Moyenne | Grave | Se spécialiser sur l'opérationnel/juridique, là où une ONG ne va pas |
| R6 | Google modifie sa politique GEE ou sa tarification | Moyenne | Grave | Chaîne de secours Copernicus Data Space / openEO / AWS Open Data |
| R7 | Instabilité politique, coup d'arrêt budgétaire d'un ministère | Élevée en RDC | Moyen | Diversifier : privé RDUE + carbone + multi-pays |
| R8 | Départ de la personne clé (projet mono-développeur) | **Élevée** | Fatal | Documenter, recruter, formaliser |
| R9 | Litige de propriété intellectuelle avec l'université | Moyenne | Grave | Clarifier par écrit **avant** toute levée |
| R10 | Le RDUE est encore reporté ou assoupli | Moyenne | Moyen | Ne pas fonder plus de 40 % du plan sur le RDUE |
| R11 | Réduction des financements d'aide au développement (contexte 2025-2026) | Élevée | Grave | Privilégier les payeurs privés et les recettes propres des États |
| R12 | Dépendance à un partenaire local sur les appels d'offres publics | Moyenne | Moyen | Plusieurs partenaires, statut local propre |

---

## 7. Plan de remédiation immédiat (Sprint 0)

**Objectif : rendre le produit démontrable sans risque juridique ni réputationnel.
2 semaines, ~25 j/h, ~12 k€.** Aucune fonctionnalité nouvelle.

| Jour | Action | Réf. |
|---|---|---|
| 1 | Bandeau permanent « DONNÉES DE DÉMONSTRATION — NON OPÉRATIONNELLES » sur toute UI dès que `is_real() == False`. Champ `is_synthetic: true` sur **chaque** réponse API. | R1 |
| 1 | Corriger `high_risk_ha` : utiliser `PIXEL_AREA_HA`, supprimer le `0.038`. | B4/D1 |
| 2-3 | Login en deux temps avec OTP réellement enforcé (jeton intermédiaire de 5 min, scope `otp`). | B1/S1 |
| 3 | `_seed_admin()` conditionné à `demo_mode` ; refus de démarrage si secret JWT par défaut hors développement. | B2/B9 |
| 4 | CORS en liste blanche ; `refresh_token` en body ; cookies `HttpOnly`. | B7/S7/S9 |
| 4 | Rate-limiting (`slowapi`) sur `/auth/*` et `/reports`. Auth requise sur `POST /reports`. | S5/S6/B8 |
| 5 | Purger `files/`, `.DS_Store`, dédupliquer `settings.py`/`Dockerfile`. Scan de secrets (`gitleaks`) sur tout l'historique. | D19/D20 |
| 6-7 | Supprimer le repli silencieux : si `real` est demandé sans données, **erreur explicite**. Idem pour les étiquettes manquantes. | B11/D8 |
| 8 | CI : retirer `|| true`, ajouter `ruff` + `bandit` + `pip-audit` + Trivy. Un job « full deps » hebdomadaire avec TensorFlow/rasterio. | B12 |
| 9 | Dockerfile multi-stage, utilisateur non-root, PostgreSQL non exposé. | S18/S19 |
| 10 | Retirer la mention « Sentinel-2 10 m » partout où c'est faux ; documenter 195 m comme limitation connue. | B5 |
| 11-12 | Renommer `_edt` en `_manhattan_distance` ou implémenter la vraie EDT (`scipy.ndimage.distance_transform_edt`). Supprimer la fabrication de positifs. | D4/D6 |
| 13-14 | `SECURITY.md`, `CONTRIBUTING.md`, `LICENSE`, ADR n° 1 (« pourquoi une abstraction de source »). Rapport de fin de Sprint 0. | S20 |

**Critère de sortie :** un audit de sécurité externe ne trouve aucun 🔴, et aucune capture
d'écran du produit ne peut être prise pour de la donnée réelle.

---

*Suite : [`02-concurrence.md`](02-concurrence.md)*
