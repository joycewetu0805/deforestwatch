# Audit stratégique & cahier des charges — DeforestWatch → plateforme de référence africaine

**Commandité par :** direction produit / fondation
**Rédigé en posture :** CTO + Product Manager (investisseur, DSI, data scientist, expert télédétection, RSSI, directeur commercial)
**Date :** juillet 2026
**Portée :** transformation du projet académique `deforestwatch` en produit SaaS B2B/B2G vendable à des gouvernements, ONG, sociétés forestières/minières, organismes internationaux.

> Méthodologie : cet audit n'est pas générique. Il s'appuie sur une lecture directe du code du dépôt `joycewetu0805/deforestwatch` (README, GUIDE.md, `config/settings.py`, `src/api/*`, `streamlit_app/*`, `frontend/src/*`, `tests/*`, CI, `requirements.txt`) à la date du 27/07/2026. Chaque constat technique cité en partie 1 renvoie à un fichier réel du dépôt.

---

## 0. Verdict exécutif

**Ce que c'est aujourd'hui :** un excellent projet de fin d'études — pipeline ML complet (RF/XGBoost/U-Net), API FastAPI propre, deux front-ends (Streamlit + React), mode démo intelligent, CI fonctionnelle, 482 lignes de tests. Niveau technique très supérieur à la moyenne des mémoires L3.

**Ce que ce n'est pas :** un produit commercialisable. En l'état, aucun DG d'ONG ni ministère de l'Environnement ne peut signer un contrat dessus, pour trois raisons non négociables :

1. **Zone unique, non paramétrable** — le produit surveille 50×50 km autour d'Inongo (Mai-Ndombe). Il n'existe **aucun mécanisme multi-tenant, multi-zone, multi-pays**. C'est un démonstrateur, pas une plateforme.
2. **Sécurité de théâtre** — le dashboard Streamlit (l'interface que verra un client) a sa **propre** authentification, un dictionnaire Python en dur avec mots de passe en clair (`admin123`/`user123`) et un code 2FA **fixe** (`123456`), totalement déconnectée du système JWT/bcrypt réel de l'API (`streamlit_app/components/auth.py:11-14`). Un pentest la détruit en 30 secondes.
3. **Aucun modèle économique implémenté** — pas de facturation, pas de clés API à quota, pas de plans tarifaires, pas de séparation des données par client. Le produit ne sait pas générer de revenu récurrent.

**Verdict investisseur :** le socle technique justifie un seed, pas une série A. Il faut 6 à 9 mois de "produit-isation" avant d'aller devant un comité d'investissement avec un go-to-market Afrique centrale crédible.

---

## 1. Audit du produit actuel

### 1.1 Points forts (à préserver absolument)

| Force | Preuve dans le code |
|---|---|
| Architecture logicielle propre et modulaire (data / preprocessing / models / api / visualization séparés) | `src/` |
| Trois familles de modèles comparées avec de vraies métriques (Accuracy, F1, AUC-ROC, IoU) | `src/models/evaluator.py`, `src/models/trainer.py` |
| **Mode démo/réel avec bascule à chaud sans redémarrage** — idée d'onboarding excellente, rare dans un projet académique | `src/data/provider.py`, `src/data/sources.py`, endpoint `POST /api/v1/admin/source/{mode}` |
| Repli gracieux si TensorFlow/XGBoost absents (dégradation, pas de crash) | GUIDE.md §13 |
| Conscience réelle du problème nuages tropicaux (radar Sentinel-1 en complément de l'optique) | `src/data/radar.py`, endpoint `/api/v1/radar/coverage/{year}` |
| Estimation carbone (AGB → CO₂) avec facteurs IPCC documentés | `config/settings.py:87-94`, `src/analysis/carbon.py` |
| Signalement citoyen (crowdsourcing) déjà présent, ouvert sans authentification | `POST /api/v1/reports` |
| CI GitHub Actions (tests + lint + build frontend à chaque push) | `.github/workflows/ci.yml` |
| Documentation exceptionnelle pour un projet académique (GUIDE.md, IMPACT.md, mémoire généré) | racine du dépôt |

### 1.2 Points faibles critiques

| # | Faiblesse | Preuve | Sévérité |
|---|---|---|---|
| F1 | **Authentification dashboard factice** : mots de passe en clair, code 2FA fixe `123456`, aucun lien avec la table `User`/bcrypt réelle | `streamlit_app/components/auth.py:11-51` | 🔴 Bloquant commercial |
| F2 | **Zone géographique câblée en dur** (`study_area_lat/lon` uniques dans `Settings`) — impossible de vendre à un 2ᵈ client sans forker le code | `config/settings.py:47-50` | 🔴 Bloquant scaling |
| F3 | **Pas de multi-tenant** : une seule base, un seul rôle `admin`/`user`, aucune notion d'organisation, de client, de périmètre de données | `src/api/database.py` (table `User` : `email`, `role`, sans `org_id`) | 🔴 Bloquant B2B |
| F4 | **`DEMO_MODE=true` par défaut et `JWT_SECRET_KEY` par défaut faible** committés dans `.env.example` — risque réel de déploiement en prod avec les valeurs par défaut si personne ne les changent | `.env.example:15`, `config/settings.py:34` | 🟠 Élevé |
| F5 | Base de données de repli **SQLite** en cas d'indisponibilité PostgreSQL — inacceptable pour un SaaS multi-client (verrous d'écriture, pas de scaling horizontal) | GUIDE.md §13 | 🟠 Élevé |
| F6 | **Deux interfaces qui font la même chose** (Streamlit "dashboard officiel" vs React "CongoForest Watch") sans frontière produit claire — confusion pour un acheteur qui demande "montrez-moi *le* produit" | `streamlit_app/` vs `frontend/src/` | 🟠 Élevé |
| F7 | Pas de PostGIS visible (pas de requêtes spatiales natives, pas d'index géographique) malgré usage de géodonnées | `src/api/database.py`, `requirements.txt` | 🟡 Moyen |
| F8 | Tests fins (482 lignes / 7 fichiers) : aucun test de sécurité, aucun test de charge, pas de test end-to-end multi-utilisateur | `tests/` | 🟡 Moyen |
| F9 | Dépendances datées et non scannées (FastAPI 0.109, Pydantic 2.6.0, TensorFlow 2.15 — fin 2023/2024) sans Dependabot ni SAST dans la CI | `requirements.txt`, `.github/workflows/ci.yml` | 🟡 Moyen |
| F10 | Stack lourde et monolithique (PySpark + GDAL + TensorFlow dans le même process) — coût cloud et complexité de déploiement disproportionnés pour un MVP commercial | `requirements.txt` | 🟡 Moyen |
| F11 | Pas d'i18n : tout est en français alors que la cible (Afrique centrale) est aussi anglophone (RDC frontalière), et le continent est multilingue (portugais, swahili, lingala, arabe pour l'Afrique du Nord) | UI Streamlit/React | 🟡 Moyen |
| F12 | Aucune gestion de secrets (Vault, AWS Secrets Manager, Doppler) — tout passe par `.env` en clair | `config/settings.py` | 🟡 Moyen |

### 1.3 Risques

- **Risque réputationnel** : si un ministère ou une ONG teste le produit et trouve les identifiants `admin123` dans le code source public GitHub, la crédibilité scientifique du projet est atteinte instantanément.
- **Risque juridique/souveraineté des données** : héberger les données environnementales d'un État sur Supabase (US/EU) sans clause de résidence des données peut bloquer un appel d'offres gouvernemental (RDC, Gabon, Congo-Brazzaville imposent parfois une hébergement local ou régional).
- **Risque scientifique** : le mode démo génère des données *synthétiques* mais réalistes. Sans garde-fou UX fort, un client peut confondre démo et réel — désastre si une décision opérationnelle (envoi d'écogardes) est prise sur une fausse alerte.
- **Risque de dépendance à une seule zone d'étude** : toute la logique métier (classes, échelle, résolution 256×256, buffer 25 km) est pensée pour Mai-Ndombe. Étendre à une autre concession forestière n'est pas un paramétrage, c'est une réécriture.
- **Risque de continuité** : projet actuellement porté par une seule personne (mémoire académique) — aucune redondance d'équipe, aucun plan de succession technique documenté.

### 1.4 Fonctionnalités manquantes (les plus critiques)

- Multi-tenant / multi-zone / multi-pays
- Facturation, plans tarifaires, clés API à quota
- Alertes push temps réel (email/SMS/WhatsApp) réellement opérationnelles (le code actuel a un digest email admin manuel, rien d'automatisé ni de multi-canal)
- Téléchargement de rapports PDF/Word/PPT générés à la demande pour un client
- Application mobile
- Mode hors-ligne (critique en zone forestière à connectivité faible/inexistante)
- Historique/versioning des couches cartographiques, comparaison avant/après avec curseur temporel dans l'UI
- Gestion fine des rôles (RBAC au-delà de admin/user)
- API publique documentée avec SDK

### 1.5 Problèmes UX

- Connexion "sécurisée" affichant les identifiants de démo directement sous le formulaire (`st.caption("Démo — admin@deforestwatch.cd / admin123 · 2FA : 123456")`) — acceptable en dev, dangereux si jamais exposé publiquement sans retrait.
- Deux produits (Streamlit + React) signifie deux design systems, deux courbes d'apprentissage, incohérence de marque ("DeforestWatch-DRC" vs "CongoForest Watch").
- Streamlit est un excellent outil de prototypage data-science mais structurellement limité pour un produit commercial : re-render complet à chaque interaction, pas de vraie gestion d'état, difficile à styliser à un niveau "SaaS entreprise", performances dégradées à l'échelle.
- Aucune indication visuelle permanente et non-ignorable "MODE DÉMONSTRATION — données synthétiques" sur les cartes elles-mêmes (bandeau, watermark) pour empêcher toute confusion en usage réel.

### 1.6 Limites scientifiques

- Modèles entraînés/évalués **uniquement sur données synthétiques par défaut** — aucune métrique de terrain publiée sur données réelles (le README l'assume : "résultats chiffrés à confirmer sur données réelles").
- Pas de validation croisée spatiale (spatial cross-validation) mentionnée — un risque classique en télédétection est la fuite spatiale (spatial autocorrelation) qui gonfle artificiellement l'accuracy.
- Pas d'estimation d'incertitude par pixel (pas de carte de confiance) — critique quand un client va agir légalement sur une alerte.
- Pas de fusion optique + radar réellement intégrée au pipeline de classification (le radar sert seulement à un indicateur de couverture nuageuse, pas encore à la détection elle-même).
- Résolution unique 10-30m — aucune option de finesse à l'échelle drone/très haute résolution pour la détection de petites clairières ou pistes clandestines.
- Pas de détection de changement multi-date fine (change-point detection), seulement comparaison année par année.

### 1.7 Limites commerciales

- Aucun pricing, aucun contrat type, aucune mention légale (CGU, politique de confidentialité, conformité RGPD/loi congolaise sur les données).
- Le README affiche encore une URL de clone `github.com/alviii/deforest-watch-drc.git` obsolète (incohérente avec le vrai remote `joycewetu0805/deforestwatch`) — mauvais signal de rigueur pour un audit technique externe (due diligence).
- Pas de preuve d'impact quantifiée sur du réel (aucun case study, aucun client pilote documenté).
- Positionnement "académique" partout (mémoire, soutenance, université) dans le dépôt public — à séparer strictement du narratif commercial.

---

## 2. Analyse concurrentielle

| Plateforme | Ce qu'elle fait mieux que nous | Ce qu'elle fait moins bien / angle mort | À reprendre | Innovation possible pour se différencier |
|---|---|---|---|---|
| **Global Forest Watch (WRI)** | Couverture mondiale, alertes GLAD/RADD quasi temps réel, immense historique de données, API publique mature, notoriété | Granularité locale faible, pas de prédiction propriétaire par pays, UX générique non adaptée au contexte terrain africain, pas d'accompagnement local | Le modèle d'alertes GLAD (fréquence, seuils par biome), l'ouverture des données | Prédiction *locale* fine (contexte foncier RDC : routes, concessions, migrations agricoles) que GFW n'a pas la granularité de modéliser |
| **MapBiomas (Brésil)** | Excellence sur la classification multi-usage des sols annuelle, forte adoption institutionnelle nationale, transparence méthodologique publiée | Spécifique au Brésil, pas de version Afrique centrale, pas de temps réel | Le modèle de gouvernance multi-institutions (labo + ONG + gouvernement) et la validation terrain systématique | Devenir le "MapBiomas du Bassin du Congo" : gouvernance partagée avec les États (RDC, Congo, Gabon, RCA, Cameroun) |
| **SERVIR (NASA/USAID)** | Renforcement de capacités locales, formation, ancrage régional fort en Afrique | Outils souvent en mode projet/subvention, pas de continuité produit SaaS, pas de modèle commercial | La logique de "hub régional" et le lien avec les administrations | Créer un vrai centre de services payant (au lieu d'un programme subventionné) : SLA, support, revenus récurrents |
| **Google Earth Engine Apps** | Puissance de calcul planétaire, catalogue de données massif, gratuit pour la recherche | Nécessite des compétences techniques pour créer une app, pas de produit "clé en main" pour un décideur non technicien, pas d'alertes proactives packagées | Utiliser GEE comme *backend de calcul* plutôt que réinventer le stockage/traitement satellite | Packager GEE comme moteur de calcul derrière une UX métier zéro-code pour agents forestiers |
| **Copernicus (UE)** | Données gratuites, hyper fiables, résolution et fréquence excellentes (Sentinel-1/2), infrastructure européenne robuste | Pas de couche IA/prédiction, pas de produit final, juste des données brutes | Rien à "reprendre" — c'est une source de données à consommer, pas un concurrent produit | Devenir le meilleur "dernier kilomètre" entre Copernicus et le décideur terrain africain |
| **Planet Labs** | Imagerie quotidienne très haute résolution (3-5m), fraîcheur inégalée | Coût très élevé, données commerciales fermées, pas de couche prédictive Afrique centrale | Le modèle d'abonnement à l'imagerie tuilée et le "PlanetScope daily basemap" | Offrir Planet en option premium payante dans nos abonnements (revente/partenariat) plutôt que le concurrencer sur l'acquisition |
| **Satelligence** | Produit B2B mature pour le secteur agro-industriel (huile de palme, chaînes d'approvisionnement zéro-déforestation, conformité EUDR) | Cible entreprises agro-industrielles occidentales, prix élevé, pas de couche gouvernementale/ONG | Le positionnement "conformité réglementaire" (EUDR, zéro-déforestation) — marché énorme et sous-adressé en Afrique centrale | Devenir le partenaire de conformité EUDR pour les exportateurs de bois/cacao/huile de palme du Bassin du Congo (obligation UE dès 2025-2026) |
| **Airbus OneAtlas / Orbital Insight / Descartes Labs** | Infrastructure cloud géospatiale de niveau entreprise, analytics à très grande échelle, clients gouvernementaux/défense | Prix prohibitif pour ONG et gouvernements africains à budget contraint, pas d'ancrage local, support en anglais uniquement | Les modèles de licence entreprise (contrats pluriannuels, API à quota, SLA contractuels) | Le prix et la proximité : devenir 5 à 10x moins cher, en français/local, avec support terrain — c'est un avantage concurrentiel réel et défendable |

### Synthèse concurrentielle

Le "océan bleu" n'est pas la technologie de détection (largement démocratisée par Sentinel + modèles open-source), c'est :
1. **La granularité locale et la connaissance du contexte foncier/politique congolais** (concessions, migrations agricoles, routes clandestines) — aucun concurrent global ne l'a.
2. **La conformité réglementaire EUDR** pour les exportateurs de matières premières du Bassin du Congo — marché réglementaire naissant, quasi vide de concurrents locaux.
3. **Le prix et la langue** — devenir le fournisseur crédible, francophone, abordable, que les gouvernements d'Afrique centrale peuvent réellement s'offrir et comprendre.

---

## 3. Catalogue de fonctionnalités (priorisées)

### 🔴 P0 — Critique (bloque toute vente)
- Multi-tenant réel (organisation, projet, périmètre géographique par client)
- Authentification unifiée et sécurisée (suppression du dictionnaire en dur Streamlit, SSO/OAuth2, MFA réel via TOTP standard)
- Facturation & gestion d'abonnements (Stripe/Paddle + plans)
- Zone d'étude paramétrable (dessin de polygone, upload de shapefile/GeoJSON par le client)
- Alertes multi-canal réellement automatisées (email, SMS, WhatsApp) avec seuils par client
- Export de rapports PDF/Excel à la demande
- Bandeau non-ignorable "Données démo / Données réelles" partout dans l'UI

### 🟠 P1 — Haute priorité (6-12 mois)
- API publique documentée (OpenAPI, clés API, quotas)
- RBAC complet (rôles personnalisés, permissions granulaires)
- Comparateur avant/après avec curseur temporel dans le produit final (pas seulement démo React)
- Carte 3D / terrain
- Intégration Sentinel-1 (radar) dans le pipeline de classification, pas seulement en indicateur
- Carte d'incertitude / confiance par pixel
- Historique et audit trail complet
- Mobile app (au moins Android, lecture + alertes + signalement terrain hors-ligne)
- Détection de routes/pistes clandestines (segmentation linéaire)
- Estimation carbone certifiable (méthodologie documentée, exportable pour crédits carbone)

### 🟡 P2 — Moyenne priorité (12-24 mois)
- Application iOS
- Mode hors-ligne complet avec synchronisation différée
- Apprentissage actif (active learning) pour réduire le coût d'annotation terrain
- IA explicable (cartes de saliency, importance des features par alerte)
- Webhooks et intégrations Slack/Discord/Telegram
- Rapport de conformité EUDR automatisé
- Multi-langue (FR/EN/PT/Swahili)
- Collaboration cartographique (annotations, commentaires géoréférencés)

### 🟢 P3 — Ambitieux / différenciant (24-60 mois)
- Fusion de données GEDI (LiDAR spatial NASA) pour la biomasse 3D
- Ingestion de données drones propriétaires client
- Apprentissage fédéré entre pays partenaires (partage de modèles sans partage de données souveraines)
- Marketplace de modèles/plugins tiers
- Jumeau numérique de la forêt (simulation de scénarios de gestion)
- Réentraînement automatique en continu (MLOps complet avec détection de dérive)

---

## 4. Dashboard professionnel (spécification)

**KPIs en tête de page :** surface forêt restante (ha), perte annuelle (ha et %), CO₂ émis équivalent, nombre d'alertes actives, taux de confiance moyen du modèle, zones à risque critique (top 5).

**Widgets :**
- Carte interactive principale (2D/3D, calques commutables)
- Graphique d'évolution temporelle (aires empilées par classe de couverture)
- Heatmap de risque par secteur administratif
- Classement des "hotspots" de déforestation (tableau triable)
- Fil d'alertes en temps réel avec statut (nouvelle / en cours / résolue)
- Widget météo/pluviométrie corrélé aux périodes de brûlis
- Indicateur de fraîcheur des données (dernière image satellite reçue)
- Comparateur multi-zones (si le client gère plusieurs concessions)

---

## 5. Cartographie

- Curseur temporel (slider année/mois) avec lecture automatique (time-lapse) — **déjà amorcé côté React (`TimeMachine.jsx`)**, à généraliser au produit final unique
- Comparateur avant/après en glissière (swipe) — déjà présent en démo React, à fiabiliser
- Carte 2D (Leaflet/MapLibre) et 3D (Cesium/deck.gl) pour le relief et la canopée
- Couches commutables : Sentinel-2, Landsat, MODIS, Planet (si abonnement), drones client, OpenStreetMap, imagerie Google/Bing en fond de plan
- Cartes hors-ligne téléchargeables par tuiles (MBTiles) pour usage terrain sans réseau
- Superposition de couches contextuelles : routes, concessions forestières, aires protégées, cadastre minier

---

## 6. Méthodes de détection à couvrir

| Cible | Méthode recommandée |
|---|---|
| Changement de couverture forestière | Classification multi-date + change detection (post-classification comparison) |
| Brûlis / feux | Indice NBR (déjà présent dans `config/settings.py`) + détection thermique (MODIS/VIIRS actifs feux) |
| Exploitation illégale / coupe sélective | Segmentation fine + détection de clairières sub-pixel, texture radar |
| Mines artisanales/industrielles | Classification spectrale sol nu + détection de formes géométriques anormales |
| Expansion agricole | Séries temporelles NDVI + saisonnalité |
| Routes clandestines / pistes forestières | Segmentation linéaire (U-Net orienté ligne) + détection de fronts de déforestation en "arête de poisson" (motif classique en Amazonie/Congo) |
| Expansion urbaine | Classes bâti + croissance des surfaces imperméables |
| Campements | Détection d'objets petite échelle (très haute résolution requise, Planet/drone) |
| Fragmentation forestière | Métriques de paysage (indice de fragmentation, distance au bord de forêt) |
| Dégradation (vs perte totale) | Modèles de sous-pixel / analyse spectrale de mélange (spectral unmixing) |
| Perte de biomasse | Fusion GEDI/LiDAR + modèles allométriques |
| Évolution de la canopée | Séries temporelles NDVI/EVI lissées (harmoniques, Fourier) |

---

## 7. Intelligence artificielle — comparatif des approches

| Approche | Avantages | Inconvénients | Difficulté | Coût | Précision attendue |
|---|---|---|---|---|---|
| Random Forest (déjà implémenté) | Rapide, interprétable, robuste au bruit | Ignore le contexte spatial (pixel par pixel) | Faible | Faible | 80-88% |
| XGBoost/LightGBM/CatBoost | Meilleure performance que RF sur features tabulaires, rapide à entraîner | Toujours pixel-based, sensible au déséquilibre de classes | Faible-Moyenne | Faible | 85-90% |
| CNN / U-Net (déjà implémenté) | Capture le contexte spatial, standard en segmentation sémantique satellite | Besoin de données étiquetées volumineuses, coût GPU | Moyenne | Moyenne | 88-93% |
| Vision Transformers (ViT/Swin) | État de l'art sur grandes images, bonne capture du contexte global | Très gourmand en données et en calcul, moins mature en télédétection tropicale | Élevée | Élevée | 90-95% (si données suffisantes) |
| LSTM / modèles spatio-temporels (ConvLSTM) | Modélise l'évolution temporelle, bon pour la prédiction de trajectoire de déforestation | Complexe à entraîner, séries temporelles longues nécessaires | Élevée | Moyenne-Élevée | Variable, fort potentiel prédictif |
| AutoML (H2O, AutoGluon) | Accélère l'itération, bon pour prototypage client par client | Boîte noire, coût cloud si mal maîtrisé | Faible | Moyenne | Variable |
| Détection d'anomalies (isolation forest, autoencodeurs) | Détecte l'inattendu sans étiquettes complètes | Plus de faux positifs, nécessite calibrage | Moyenne | Moyenne | Complémentaire, pas autonome |
| Estimation d'incertitude (ensembles, dropout bayésien) | Indispensable pour la confiance client et la défense légale des alertes | Coût de calcul supplémentaire | Moyenne | Moyenne | Améliore la fiabilité perçue, pas l'accuracy brute |
| IA explicable (SHAP, Grad-CAM) | Essentiel pour convaincre un juriste/décideur qu'une alerte est fondée | Ajoute de la complexité d'ingénierie | Moyenne | Faible-Moyenne | N/A (outil de confiance, pas de perf) |
| Apprentissage fédéré | Permet la collaboration inter-pays sans partager des données souveraines sensibles | Complexe à opérer, immature en écosystème géospatial | Très élevée | Élevée | Potentiel différenciant fort à 3-5 ans |
| Apprentissage actif | Réduit drastiquement le coût d'annotation terrain (le vrai goulot d'étranglement en Afrique centrale) | Nécessite une boucle humaine bien opérée | Moyenne | Moyenne | Accélère la montée en précision dans le temps |
| Réentraînement automatique (MLOps) | Maintient la précision face à la dérive (nouvelles zones, nouveaux capteurs) | Coût d'infrastructure MLOps | Élevée | Élevée | Maintient la précision dans la durée |

**Recommandation séquencée :** garder RF+XGBoost+U-Net comme socle (déjà fait, solide), ajouter l'estimation d'incertitude et l'IA explicable en priorité P1 (peu coûteux, très fort effet de confiance client/légal), puis ConvLSTM pour la prédiction spatio-temporelle en P1-P2, Vision Transformers et apprentissage fédéré en différenciation P3.

---

## 8. Alertes intelligentes

Canaux : Email, SMS (Africa's Talking/Twilio — pertinent pour l'Afrique), WhatsApp Business API, Telegram, Signal, notifications push (mobile), webhooks génériques, Slack, Discord.

Fonctions : seuils personnalisés par utilisateur/zone, alertes multi-destinataires par rôle, escalade automatique (non traité en N heures → notifie le niveau supérieur), accusé de réception obligatoire, historique complet et exportable, géorepérage (alertes uniquement dans un polygone défini par le client — concession, aire protégée).

> Le socle actuel (`src/analysis/alerts.py`, `POST /api/v1/admin/notify`) ne fait qu'un digest email manuel déclenché par un admin — à transformer en moteur d'alerte événementiel (queue + workers), pas un simple endpoint synchrone.

---

## 9. Rapports

Formats : PDF, Word, Excel, PowerPoint — générés à la demande (période, zone, destinataire).
Contenu : cartes annotées, graphiques d'évolution, statistiques clés, imagerie satellite avant/après, recommandations générées par IA (langage naturel, ex. "Le secteur X présente un risque élevé du fait de sa proximité à la nouvelle route Y"), résumé exécutif d'une page pour les décideurs non techniques.

---

## 10. Collaboration

Équipes et organisations, rôles (admin / analyste / observateur terrain / lecture seule), permissions par zone géographique, commentaires et annotations cartographiques géoréférencées, partage sécurisé de rapports (lien à expiration, accès invité), historique des modifications (qui a validé quelle alerte, quand), workflow de validation d'alerte (brouillon → vérifiée → clôturée).

---

## 11. API

REST (déjà amorcé, propre — `src/api/routes.py`) + GraphQL en option pour les intégrateurs avancés, SDK Python et JavaScript officiels, webhooks sortants, documentation OpenAPI publique (Swagger déjà généré par FastAPI, à exposer publiquement avec exemples), clés API avec quotas et rate-limiting par plan tarifaire, OAuth2 pour les intégrations tierces (en plus du JWT interne), journalisation complète des appels (la table `ApiLog` existe déjà — bonne base à étendre).

---

## 12. Applications

- **Web** : produit principal, temps réel, tous les rôles.
- **Android** : priorité mobile (parc Android dominant en Afrique centrale) — consultation carte, alertes push, signalement terrain géolocalisé, **mode hors-ligne avec synchronisation différée** (connectivité forestière faible).
- **iOS** : cible ONG internationales et bailleurs, moindre priorité initiale.
- **Tablette** : usage terrain écogardes/forestiers, gros boutons, mode plein soleil (contraste élevé), autonomie batterie optimisée.

---

## 13. Données — sources à intégrer

Sentinel-1 (radar), Sentinel-2, Landsat 8/9, MODIS, Planet (partenariat/revente), GEDI (biomasse LiDAR spatial), LiDAR aéroporté/drone (client), imagerie drone propriétaire, OpenStreetMap (routes, villages), météo (précipitations, température, humidité — déjà amorcé via OpenWeatherMap), relief (SRTM — déjà utilisé), cadastre routier, concessions forestières et minières (données gouvernementales), aires protégées (WDPA), données socio-économiques (densité de population, pauvreté, accès aux marchés — facteurs prédictifs de pression sur la forêt).

---

## 14. Architecture cible niveau entreprise

```
┌─────────────────────────────────────────────────────────────────┐
│  CLIENTS : Web (React) · Mobile (Android/iOS) · API tierces      │
└───────────────────────────┬───────────────────────────────────────┘
                            │ HTTPS / OAuth2 / JWT
┌───────────────────────────▼───────────────────────────────────────┐
│  API GATEWAY (Kong/Traefik) — rate limiting, auth, quotas par plan │
└───────────────────────────┬───────────────────────────────────────┘
          ┌──────────────────┼──────────────────┬───────────────────┐
          ▼                  ▼                  ▼                   ▼
   ┌─────────────┐   ┌──────────────┐   ┌───────────────┐  ┌───────────────┐
   │ Service Auth │   │ Service Tenant│  │ Service Alertes│  │ Service Rapports│
   │ (FastAPI)    │   │/Zones (FastAPI)│  │ (FastAPI+Kafka)│  │ (FastAPI)      │
   └──────┬───────┘   └──────┬───────┘   └───────┬───────┘  └───────┬───────┘
          │                  │                    │                  │
          ▼                  ▼                    ▼                  ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │        PostgreSQL/PostGIS (multi-tenant, row-level security)      │
   └─────────────────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────────┐
   │  PIPELINE ML ASYNCHRONE                                           │
   │  Kafka (ingestion événements satellite) → Workers PySpark/GPU     │
   │  → Object Storage (S3/MinIO, GeoTIFF/COG) → Inférence (RF/U-Net/  │
   │    ConvLSTM) → Résultats écrits en PostGIS + Redis (cache tuiles) │
   └─────────────────────────────────────────────────────────────────┘

   Orchestration : Kubernetes (autoscaling GPU pour l'inférence)
   CI/CD : GitHub Actions → build Docker → déploiement K8s (staging/prod)
   Observabilité : Prometheus + Grafana + Sentry
   Sauvegardes : snapshots PostgreSQL quotidiens + réplication cross-région
   Reprise après sinistre : RTO < 4h, RPO < 1h, région secondaire (ex. Afrique du Sud/Europe selon contraintes de souveraineté)
   Cloud hybride : option d'hébergement on-premise pour clients gouvernementaux exigeant la souveraineté des données
```

**Justification des choix :**
- **Microservices + Kubernetes** : permet de scaler indépendamment le calcul ML (GPU, coûteux) et l'API (CPU, léger) — critique car le monolithe actuel mélange PySpark/TensorFlow/GDAL dans le même process.
- **PostGIS** : requêtes spatiales natives (intersections polygones, distances) indispensables et absentes aujourd'hui.
- **Kafka** : découple l'ingestion satellite (par nature asynchrone, en rafale) du service API synchrone.
- **Row-level security PostgreSQL** : c'est le mécanisme le plus simple et le plus sûr pour garantir l'isolation des données entre clients (multi-tenant) sans dupliquer les bases.
- **Cloud hybride** : argument de vente déterminant pour les gouvernements qui refusent l'hébergement 100% étranger.

---

## 15. Sécurité

Constats actuels à corriger en priorité absolue :
1. Supprimer le dictionnaire d'identifiants en dur du dashboard Streamlit (`streamlit_app/components/auth.py`) et faire consommer le vrai flux JWT/OTP de l'API par **toutes** les interfaces.
2. Remplacer le secret JWT par défaut par une valeur générée et injectée via un gestionnaire de secrets (jamais en clair dans `.env`/`settings.py`).
3. Interdire tout déploiement avec `DEMO_MODE=true` ou `APP_DEBUG=true` en production (garde-fou CI/CD).

Cible entreprise :
- MFA obligatoire pour tous les rôles admin (TOTP standard, pas de code fixe).
- RBAC fin avec row-level security en base.
- Chiffrement au repos (base + object storage) et en transit (TLS partout, HSTS).
- Audit trail complet et immuable (append-only log des actions sensibles).
- Conformité RGPD (et lois locales type loi RDC sur les données) : registre de traitement, DPA avec les clients, droit à l'effacement.
- Détection d'intrusion (WAF, fail2ban sur l'API, rate-limiting par clé API).
- Sauvegardes chiffrées, testées régulièrement (exercice de restauration).
- Scan de dépendances (Dependabot/Snyk) et SAST (Bandit/Semgrep) dans la CI — absents aujourd'hui.
- Signatures numériques sur les rapports exportés (garantir l'intégrité d'une preuve utilisée devant un tribunal ou une administration).

---

## 16. Business — monétisation et stratégie

**Modèles économiques combinés :**
- **SaaS par abonnement** : plans par nombre de zones surveillées et fréquence d'alertes (ex. Starter/Pro/Enterprise).
- **Licence gouvernementale** : contrat pluriannuel avec SLA, hébergement dédié ou on-premise, pour ministères et agences nationales.
- **API payante à l'usage** : pour intégrateurs, chercheurs, plateformes tierces (facturation au volume d'appels/tuiles).
- **Consulting & intégration** : déploiement sur-mesure pour grandes concessions forestières/minières.
- **Maintenance & support** : contrats annuels (SLA, hotline, mises à jour).
- **Formation** : certification d'agents forestiers/écogardes à l'usage de la plateforme (revenu + impact + adoption).
- **Réponse aux appels d'offres** : Banque mondiale, FAO, UE (programmes FLEGT/EUDR), bailleurs bilatéraux — cibler activement les AO environnementaux Afrique centrale.
- **Partenariats** : Planet/Airbus (revente d'imagerie premium en marque blanche), ONG internationales (WWF, WRI, Rainforest Foundation) comme co-distributeurs et cautions scientifiques.

**Stratégie d'expansion Afrique centrale :** commencer par la RDC (marché domicile, déjà instrumenté), puis Congo-Brazzaville, Gabon, Cameroun, RCA — les 6 pays du Bassin du Congo (COMIFAC) comme marché adressable naturel, avant extension Afrique de l'Ouest (Côte d'Ivoire, Ghana — cacao/EUDR) et Afrique de l'Est (Tanzanie, RDC Est).

---

## 17. Roadmap

| Horizon | Priorités techniques | Priorités commerciales | Priorités scientifiques |
|---|---|---|---|
| **6 mois** | Corriger l'auth (P0), multi-tenant MVP, zone paramétrable, facturation basique, bandeau démo/réel | 1er client pilote (ONG ou concession privée), retirer le narratif académique du dépôt public, pricing v1 | Valider les modèles sur données réelles Mai-Ndombe, publier des métriques réelles |
| **1 an** | API publique + SDK, RBAC complet, mobile Android v1, alertes multi-canal automatisées, PostGIS, CI sécurité (SAST/dependabot) | 3-5 clients payants, 1 contrat institutionnel (ministère/COMIFAC), partenariat ONG de caution scientifique | Intégration radar dans la classification, cartes d'incertitude, IA explicable |
| **3 ans** | Architecture microservices/K8s complète, mode hors-ligne mobile, extension multi-pays Bassin du Congo, conformité EUDR automatisée | Leader Afrique centrale (10-30 clients institutionnels), revenus récurrents stables, levée série A | ConvLSTM prédictif opérationnel, apprentissage actif en production |
| **5 ans** | Apprentissage fédéré inter-pays, fusion GEDI/LiDAR, marketplace de modèles, cloud hybride souverain par pays | Référence panafricaine (Afrique de l'Ouest/Est), diversification revenus (carbone, EUDR, data licensing) | Jumeau numérique forestier, réentraînement continu automatisé (MLOps mature) |

---

## 18. Tableau de priorisation final

| Fonctionnalité | Priorité | Valeur client | Difficulté technique | Coût estimé | Temps de dev | Impact commercial | Impact scientifique |
|---|---|---|---|---|---|---|---|
| Corriger l'authentification (supprimer identifiants en dur) | Critique | Élevée | Faible | Faible | 1-2 sem. | Élevé (bloquant) | Nul |
| Multi-tenant + zone paramétrable | Critique | Très élevée | Élevée | Élevé | 2-3 mois | Très élevé (bloquant) | Faible |
| Facturation/abonnements | Critique | Élevée | Moyenne | Moyen | 1 mois | Très élevé | Nul |
| Bandeau démo/réel non-ignorable | Critique | Moyenne | Faible | Faible | 2-3 jours | Élevé (confiance) | Moyen |
| Alertes multi-canal automatisées | Haute | Très élevée | Moyenne | Moyen | 1-2 mois | Élevé | Faible |
| API publique + SDK | Haute | Élevée | Moyenne | Moyen | 1-2 mois | Élevé | Faible |
| RBAC complet | Haute | Élevée | Moyenne | Moyen | 1 mois | Moyen | Nul |
| PostGIS + requêtes spatiales | Haute | Moyenne | Moyenne | Faible | 3-4 sem. | Moyen | Élevé |
| Mobile Android + hors-ligne | Haute | Très élevée | Élevée | Élevé | 3-4 mois | Élevé | Faible |
| Radar intégré à la classification | Haute | Moyenne | Élevée | Moyen | 2 mois | Moyen | Très élevé |
| Cartes d'incertitude / IA explicable | Haute | Moyenne | Moyenne | Faible | 3-4 sem. | Moyen (confiance légale) | Très élevé |
| Rapports PDF/Word/Excel à la demande | Haute | Élevée | Faible | Faible | 3 sem. | Élevé | Faible |
| Conformité EUDR automatisée | Moyenne | Très élevée (marché niche) | Élevée | Élevé | 3 mois | Très élevé (nouveau marché) | Moyen |
| ConvLSTM prédictif | Moyenne | Élevée | Très élevée | Élevé | 3-4 mois | Moyen | Très élevé |
| Application iOS | Moyenne | Moyenne | Élevée | Élevé | 3 mois | Faible-Moyen | Nul |
| Apprentissage actif | Moyenne | Moyenne | Élevée | Moyen | 2 mois | Moyen | Élevé |
| Multi-langue (EN/PT/Swahili) | Moyenne | Élevée (expansion) | Faible | Faible | 3-4 sem. | Élevé (expansion) | Nul |
| Fusion GEDI/LiDAR biomasse | Faible (aujourd'hui) | Élevée (à terme) | Très élevée | Élevé | 4-6 mois | Moyen | Très élevé |
| Apprentissage fédéré inter-pays | Faible (aujourd'hui) | Élevée (à terme) | Très élevée | Très élevé | 6+ mois | Élevé (à terme) | Très élevé |
| Marketplace de modèles tiers | Faible | Faible aujourd'hui | Élevée | Élevé | 6+ mois | Faible aujourd'hui | Faible |
| Jumeau numérique forestier | Faible | Faible aujourd'hui | Très élevée | Très élevé | 6+ mois | Faible aujourd'hui | Moyen |

---

## Conclusion

Le socle technique de `deforestwatch` est réel et de bonne qualité pour un projet académique — cela mérite d'être dit sans ambiguïté. Mais entre ce socle et un produit vendable à des gouvernements ou des ONG internationales, il manque une couche entière : **multi-tenant, sécurité réelle, facturation, mobile, alertes opérationnelles, et une histoire de conformité réglementaire (EUDR) qui est aujourd'hui l'angle commercial le plus vendable et le moins disputé en Afrique centrale.**

La priorité immédiate n'est pas d'ajouter des fonctionnalités IA plus sophistiquées — le pipeline RF/XGBoost/U-Net est déjà solide — mais de corriger les trois défauts bloquants (§0) et de construire la couche produit (tenant, facturation, alertes) qui transforme un excellent projet de recherche en plateforme réellement opérable par un client payant.
