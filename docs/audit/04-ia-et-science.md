# 04 — Intelligence artificielle, données et validation scientifique

---

## 1. Avertissement préalable

Les précisions annoncées ci-dessous sont des **ordres de grandeur issus de la littérature
sur la détection de changement forestier tropical**, pas des promesses. Elles supposent :
une vérité terrain correcte, un protocole d'évaluation honnête et une zone comparable au
Bassin du Congo.

**Trois facteurs dégraderont systématiquement vos résultats par rapport aux publications :**

1. **La couverture nuageuse.** Au Mai-Ndombe, l'optique exploitable est rare et
   saisonnièrement biaisée. C'est le premier facteur limitant, avant tout choix de modèle.
2. **Le déséquilibre de classes.** La déforestation annuelle concerne typiquement bien
   moins de 1 % des pixels. **L'accuracy est un indicateur inutile** : un modèle qui prédit
   « pas de changement » partout atteint 99 %. Seuls comptent le rappel, la précision, la
   PR-AUC et le F1 sur la classe minoritaire.
3. **La dégradation, pas la déforestation.** Le signal recherché en Afrique centrale est
   souvent partiel et progressif, donc bien plus difficile qu'une coupe rase amazonienne.

> **Le levier n° 1 de performance n'est pas le modèle, c'est la donnée d'entraînement.**
> Passer de XGBoost à un Vision Transformer sans vérité terrain vous fera perdre six mois
> pour rien. Ajouter 5 000 points de vérité terrain de qualité vous fera gagner plus que
> tout changement d'architecture. **Cet ordre de priorité est le message principal de ce
> chapitre.**

---

## 2. Comparatif des approches

Coût = développement + calcul, hors salaires fixes. Difficulté sur 5.
« Précision attendue » = F1 sur la classe *changement*, en conditions réelles.

### 2.1 Machine learning classique

| Approche | Avantages | Inconvénients | Diff. | Coût | Précision att. | Verdict |
|---|---|---|---|---|---|---|
| **Random Forest** | Robuste, peu de réglage, importance de variables native, rapide, peu de données requises, très interprétable | Ignore le contexte spatial et temporel, plafonne vite, modèle lourd en mémoire | ⭐ 1/5 | 2 k€ | 0,55–0,70 | ✅ **Garder comme référence obligatoire.** Tout modèle avancé doit la battre pour exister |
| **XGBoost** | Meilleur que RF sur tabulaire, gère le déséquilibre (`scale_pos_weight`), rapide en inférence, très éprouvé | Réglage plus délicat, sur-apprend sans validation propre, pas de spatial | ⭐⭐ 2/5 | 3 k€ | 0,60–0,75 | ✅ **Modèle de production initial.** Meilleur rapport valeur/effort du projet |
| **LightGBM** | 5–10× plus rapide qu'XGBoost sur gros volumes, faible mémoire, gère nativement le catégoriel | Sensible au surapprentissage sur petits jeux | ⭐⭐ 2/5 | 3 k€ | 0,60–0,75 | ✅ **Recommandé à l'échelle nationale** (>10⁸ pixels) |
| **CatBoost** | Excellent sur variables catégorielles (concession, province, type de sol), robuste par défaut | Entraînement plus lent, communauté plus réduite | ⭐⭐ 2/5 | 3 k€ | 0,60–0,76 | ✅ Utile quand les variables métier dominent |
| **SVM / kNN** | Simples | Ne passent pas à l'échelle géospatiale | ⭐ 1/5 | 1 k€ | 0,45–0,60 | ❌ Sans intérêt ici |

> **Recommandation :** commencer et rester longtemps sur **XGBoost/LightGBM +
> caractéristiques temporelles bien construites**. Une bonne ingénierie de variables
> temporelles (amplitude saisonnière, pente de tendance, résidu à la climatologie, écart
> au voisinage) bat un réseau profond mal nourri, pour 5 % du coût.

### 2.2 Détection de changement temporelle — **la vraie priorité**

| Approche | Avantages | Inconvénients | Diff. | Coût | Précision att. | Verdict |
|---|---|---|---|---|---|---|
| **BFAST / BFAST Monitor** | Détecte ruptures et tendances, éprouvé en forêt tropicale, non supervisé (pas de vérité terrain requise), donne une **date** de changement | Coûteux en calcul par pixel, sensible aux séries lacunaires (nuages) | ⭐⭐⭐ 3/5 | 8 k€ | 0,65–0,80 | ✅ **P0 — à implémenter avant tout deep learning** |
| **CCDC** | Modélise la saisonnalité, détection continue, référence dans la communauté Landsat | Nécessite de longues séries denses, calcul lourd | ⭐⭐⭐⭐ 4/5 | 15 k€ | 0,70–0,82 | ✅ P1 |
| **LandTrendr** | Excellent en segmentation de trajectoire, capte la dégradation progressive | Conçu pour l'annuel, moins réactif | ⭐⭐⭐ 3/5 | 8 k€ | 0,65–0,78 | ✅ P1, complémentaire |
| **CuSum / probabiliste (type RADD)** | Alerte quasi temps réel, fonctionne sur radar, robuste aux nuages | Réglage des seuils délicat, faux positifs sur speckle | ⭐⭐⭐ 3/5 | 10 k€ | 0,70–0,85 | ✅ **P0 sur Sentinel-1** |
| **Analyse de mélange spectral (NDFI)** | ⭐ **Le meilleur outil pour la dégradation**, physiquement fondé, interprétable | Nécessite des spectres de référence calibrés | ⭐⭐⭐ 3/5 | 10 k€ | 0,60–0,75 (dégradation) | ✅ **P0 — différenciant Bassin du Congo** |

> **Ce bloc est le plus important du chapitre.** Votre approche actuelle (classifier
> chaque année puis soustraire) cumule les erreurs des deux classifications. Les méthodes
> ci-dessus modélisent directement la **trajectoire temporelle** du pixel. Le gain est
> supérieur à celui de n'importe quel changement d'architecture neuronale, pour un coût
> et un risque bien moindres.

### 2.3 Deep learning

| Approche | Avantages | Inconvénients | Diff. | Coût | Précision att. | Verdict |
|---|---|---|---|---|---|---|
| **U-Net (CNN)** | Contexte spatial, sorties nettes, éprouvé en télédétection, nombreuses implémentations | Nécessite des masques annotés (coûteux), pas de temporel, GPU requis | ⭐⭐⭐ 3/5 | 20 k€ + 5 k€ GPU | 0,65–0,80 | ✅ P1, **après** avoir des annotations |
| **U-Net++ / DeepLabV3+ / SegFormer** | +2 à 5 pts sur U-Net | Complexité accrue, gain marginal | ⭐⭐⭐⭐ 4/5 | 30 k€ | 0,68–0,82 | 🟡 P2 |
| **Siamese U-Net (bi-temporel)** | ⭐ Conçu pour le **changement** (2 dates en entrée), pas pour la classification | Nécessite des paires annotées | ⭐⭐⭐⭐ 4/5 | 30 k€ | 0,70–0,84 | ✅ **P1 — architecture la mieux adaptée au besoin** |
| **LSTM / GRU** | Modélise la séquence temporelle, gère les longueurs variables | Ignore le spatial, entraînement lent, supplanté par les Transformers | ⭐⭐⭐ 3/5 | 15 k€ | 0,65–0,78 | 🟡 P2 |
| **ConvLSTM** | Spatial + temporel conjoints | Très coûteux en mémoire, instable | ⭐⭐⭐⭐ 4/5 | 35 k€ | 0,70–0,82 | 🟡 P2 |
| **Vision Transformer (ViT)** | Excellent avec beaucoup de données, attention longue portée | **Gourmand en données** — inadapté sans vérité terrain massive | ⭐⭐⭐⭐ 4/5 | 40 k€ | 0,60–0,85 (très variable) | ⚠️ **P2. Le piège classique.** Sans données, il fera pire qu'XGBoost |
| **Swin Transformer / SegFormer** | ViT hiérarchique, meilleur sur la segmentation dense | Idem | ⭐⭐⭐⭐⭐ 5/5 | 45 k€ | 0,70–0,86 | 🟡 P2 |
| **Temporal Attention (type TAE/LTAE)** | ⭐ Conçu pour les séries d'images satellites, robuste aux dates manquantes — **exactement le problème des nuages** | Récent, moins d'outillage prêt à l'emploi | ⭐⭐⭐⭐ 4/5 | 35 k€ | 0,72–0,86 | ✅ **P2 — le meilleur pari deep learning pour votre contexte** |
| **Modèles de fondation géospatiaux** (Prithvi, SatMAE, Clay, DOFA…) | Pré-entraînés sur des volumes massifs, affinage possible avec peu d'étiquettes, ⭐ **c'est ce qui rend le deep learning accessible sans vérité terrain massive** | Écosystème jeune, poids et licences à vérifier, forte empreinte GPU | ⭐⭐⭐⭐ 4/5 | 25 k€ | 0,70–0,85 | ✅ **P1-P2 — à surveiller de près, potentiel de saut qualitatif** |
| **GAN / diffusion** (augmentation, dénuageage) | Comble les lacunes nuageuses | ⚠️ **Génère des données qui n'existent pas.** Sur un produit probant, inacceptable en production | ⭐⭐⭐⭐⭐ 5/5 | 40 k€ | n/a | ❌ **À proscrire dans la chaîne de preuve.** Recherche uniquement |

### 2.4 Prédiction du risque (spatio-temporel)

| Approche | Avantages | Inconvénients | Diff. | Coût | Précision att. | Verdict |
|---|---|---|---|---|---|---|
| **Régression logistique spatiale** | Interprétable, référence académique, coefficients discutables avec un ministère | Linéaire, performances limitées | ⭐⭐ 2/5 | 5 k€ | AUC 0,70–0,80 | ✅ **P0 — référence obligatoire** |
| **XGBoost sur variables de risque** | Bon compromis, SHAP disponible | Ignore la structure spatiale explicite | ⭐⭐ 2/5 | 8 k€ | AUC 0,78–0,86 | ✅ **P0 — modèle de production** |
| **Automate cellulaire / Markov (type LCM/Dinamica)** | Standard du domaine, produit des scénarios spatialisés crédibles, accepté par les méthodologies carbone | Calibration lourde, peu de ML | ⭐⭐⭐ 3/5 | 15 k€ | AUC 0,75–0,85 | ✅ **P1 — attendu par les acheteurs carbone** |
| **ConvLSTM / U-Net spatio-temporel** | Capte la propagation des fronts | Gourmand, difficile à valider | ⭐⭐⭐⭐ 4/5 | 30 k€ | AUC 0,80–0,88 | 🟡 P2 |
| **Graph Neural Network** (réseau routier/fluvial) | Modélise l'accessibilité de façon naturelle | Complexe, données de réseau nécessaires | ⭐⭐⭐⭐⭐ 5/5 | 40 k€ | AUC 0,80–0,90 | 🟡 P3 |
| **Processus ponctuels / Hawkes** | Modélise la contagion spatiale de la déforestation | Peu utilisé, difficile à expliquer | ⭐⭐⭐⭐ 4/5 | 25 k€ | — | 🟡 P3 |

> **Le point dur de la prédiction n'est pas le modèle, c'est la validation.**
> Un AUC de 0,88 obtenu sur un découpage aléatoire ne vaut rien : la déforestation est
> spatialement autocorrélée et temporellement tendancielle. **Seule une validation
> prospective compte :** entraîner sur 2015-2020, prédire 2021-2023, comparer au réel
> observé. C'est le seul chiffre défendable devant un investisseur ou un auditeur.
> Vous ne l'avez pas fait (Sc3). **C'est l'expérience la plus urgente du projet.**

### 2.5 Approches transverses

| Approche | Avantages | Inconvénients | Diff. | Coût | Verdict |
|---|---|---|---|---|---|
| **AutoML** (Optuna, AutoGluon) | Optimise sans expertise, gain rapide de 2-5 pts | Boîte noire, coût de calcul, risque de surapprentissage du jeu de validation | ⭐⭐ 2/5 | 5 k€ | ✅ P1 — utiliser Optuna pour l'optimisation d'hyperparamètres, pas AutoML de bout en bout |
| **Détection d'anomalies** (Isolation Forest, autoencodeur) | Non supervisée — **utilisable sans vérité terrain**, détecte l'inattendu | Beaucoup de faux positifs, difficile à qualifier | ⭐⭐⭐ 3/5 | 10 k€ | ✅ **P1 — pertinent tant que vous n'avez pas d'étiquettes** |
| **Estimation d'incertitude** (ensembles profonds, MC-Dropout, conformal prediction) | ⭐⭐ **Indispensable au marché carbone et juridique.** La *conformal prediction* donne des garanties statistiques sans hypothèse de distribution | Coût de calcul ×5 pour les ensembles | ⭐⭐⭐ 3/5 | 15 k€ | ✅ **P0-P1. Le vrai différenciant scientifique.** Personne n'affiche d'incertitude honnête |
| **IA explicable (SHAP, LIME, Grad-CAM, cartes d'attention)** | Exigence d'achat public, nécessaire pour la contestation d'une alerte, aide au débogage | SHAP coûteux sur gros volumes | ⭐⭐ 2/5 | 8 k€ | ✅ **P1. Obligatoire pour l'usage régalien** |
| **Apprentissage actif** | ⭐ **Réduit le coût d'annotation de 60-80 %** en ne faisant annoter que les cas informatifs | Nécessite une boucle humaine outillée | ⭐⭐⭐ 3/5 | 12 k€ | ✅ **P1. Le meilleur retour sur investissement de toute cette liste** |
| **Apprentissage semi-supervisé / pseudo-étiquetage** | Exploite les pixels non étiquetés (la quasi-totalité) | Amplifie les biais initiaux | ⭐⭐⭐ 3/5 | 12 k€ | ✅ P2 |
| **Apprentissage auto-supervisé** (SimCLR, MAE) | Pré-entraînement sans étiquettes sur votre propre archive | Coût GPU élevé | ⭐⭐⭐⭐ 4/5 | 25 k€ | 🟡 P2 |
| **Transfert de domaine** (Amazonie → Congo) | Réutilise des jeux étiquetés existants | Décalage de domaine important entre biomes | ⭐⭐⭐ 3/5 | 15 k€ | ✅ P2 |
| **Apprentissage fédéré** | Entraînement multi-pays **sans partage des données** — argument de souveraineté puissant pour un consortium COMIFAC | Complexité forte, gain réel discutable à petite échelle, sécurité délicate | ⭐⭐⭐⭐⭐ 5/5 | 50 k€ | ⚠️ **P3. Excellent argument de communication, faible valeur technique immédiate.** Ne pas le faire avant d'avoir plusieurs pays clients |
| **Réentraînement automatique (MLOps)** | Le modèle s'améliore avec les retours terrain | Risque de dérive silencieuse ; **jamais de déploiement automatique sans validation** | ⭐⭐⭐ 3/5 | 20 k€ | ✅ **P1** — avec approbation humaine obligatoire |
| **Détection de dérive** (données et concept) | Prévient la dégradation silencieuse en production | — | ⭐⭐ 2/5 | 8 k€ | ✅ P1 |
| **LLM pour la rédaction de rapports** | Gain de temps réel sur les synthèses | ⚠️ Hallucinations — **jamais de chiffre produit par le LLM** | ⭐⭐ 2/5 | 10 k€ | ✅ P2, sous contrainte stricte |

---

## 3. Trajectoire IA recommandée

```
PHASE 1 (0-6 mois) — Fondations, zéro deep learning
├── Vérité terrain : 2 000 points photo-interprétés + 200 GPS terrain   ⭐⭐⭐
├── XGBoost/LightGBM + variables temporelles                            ⭐⭐
├── BFAST Monitor + CuSum radar (Sentinel-1)                            ⭐⭐⭐
├── Régression logistique spatiale (référence de risque)                ⭐⭐
├── Validation prospective 2015-2020 → 2021-2023                        ⭐⭐⭐
└── Comparaison à Hansen / GLAD / RADD / TMF                            ⭐⭐⭐

PHASE 2 (6-18 mois) — Montée en puissance
├── NDFI / analyse de mélange (dégradation)                             ⭐⭐⭐
├── Siamese U-Net bi-temporel                                           ⭐⭐
├── Apprentissage actif sur la boucle terrain                           ⭐⭐⭐
├── Conformal prediction (incertitude garantie)                         ⭐⭐⭐
├── SHAP sur le modèle de risque                                        ⭐⭐
└── MLOps : MLflow, DVC, détection de dérive, réentraînement validé     ⭐⭐

PHASE 3 (18-36 mois) — Différenciation
├── Affinage d'un modèle de fondation géospatial                        ⭐⭐
├── Temporal attention (LTAE) robuste aux dates manquantes              ⭐⭐⭐
├── Régression de biomasse GEDI + S1/S2                                 ⭐⭐
├── Automate cellulaire pour scénarios carbone                          ⭐⭐
└── Publication scientifique évaluée par les pairs                      ⭐⭐⭐

PHASE 4 (36 mois+) — Ambition
├── Modèle de fondation propriétaire Bassin du Congo                    ⭐⭐
├── Apprentissage fédéré multi-pays COMIFAC                             ⭐
└── Jumeau numérique forestier prédictif                                ⭐
```

**Les ⭐⭐⭐ sont les actions à fort effet de levier. Cinq d'entre elles sont en phase 1
et ne relèvent d'aucune technologie avancée.**

---

## 4. Sources de données

### 4.1 Imagerie

| Source | Résolution | Fréquence | Coût | Prio | Usage |
|---|---|---|---|---|---|
| **Sentinel-2 (L2A)** | 10-20 m | ~5 j | Gratuit | **P0** | Socle optique |
| **Sentinel-1 (GRD/SLC)** | 10-20 m | 6-12 j | Gratuit | **P0** | ⭐ Anti-nuages — **verrou du Bassin du Congo** |
| **Landsat 5/7/8/9** | 30 m | 16 j | Gratuit | P1 | Historique depuis 1984 (baselines carbone) |
| **MODIS / VIIRS** | 250-500 m / 375 m | Quotidien | Gratuit | P1 | Feux actifs, alerte grossière rapide |
| **PlanetScope** | 3-5 m | Quotidien | ~payant | P1 | ⭐ **Vérification d'alerte à la demande** |
| **SkySat / Pléiades / Pléiades Neo** | 0,3-0,7 m | Tasking | Élevé | P2 | Preuve juridique |
| **GEDI** | Empreinte ~25 m | Échantillonné | Gratuit | P1 | ⭐ Hauteur de canopée et biomasse |
| **ICESat-2** | Échantillonné | — | Gratuit | P2 | Complément altimétrique |
| **PALSAR-2 / NISAR** | 25 m / variable | — | Gratuit/variable | P2 | Radar bande L : **pénètre la canopée**, excellent pour la biomasse |
| **LiDAR aéroporté** | 0,1-1 m | Campagne | Très élevé | P3 | Calibration de biomasse, référence absolue |
| **Drone** | 2-10 cm | À la demande | Faible/mission | P2 | ⭐ Preuve locale, très convaincant pour un juge |

### 4.2 Données auxiliaires

| Source | Prio | Usage |
|---|---|---|
| **SRTM / Copernicus DEM** (relief, pente, exposition) | P0 | Accessibilité, correction topographique |
| **OpenStreetMap** (routes, cours d'eau, villages, bâti) | **P0** | ⭐ Accessibilité — variable la plus prédictive de la déforestation |
| **Concessions forestières RDC** (cadastre) | **P0** | ⭐ Attribution de responsabilité — cœur de la valeur |
| **Aires protégées** (WDPA, ICCN) | **P0** | Priorisation, gravité juridique |
| **Titres et permis miniers** | P1 | Détection de l'orpaillage |
| **Hansen GFC / GLAD / RADD / TMF (JRC)** | **P0** | ⭐ Référence de comparaison — indispensable pour prouver un apport |
| **ESA WorldCover / Dynamic World / ESA CCI** | P1 | Couverture de référence |
| **Cartes de biomasse** (ESA CCI Biomass, GEDI L4B) | P1 | Carbone |
| **CHIRPS / ERA5 / OpenWeather** (pluie, température, humidité, sécheresse) | P1 | Feux, saisonnalité, risque |
| **WorldPop / GPW** (densité de population) | P1 | Pression anthropique |
| **Données socio-économiques** (pauvreté, prix des commodités, conflits ACLED) | P2 | Modèle de risque |
| **Tourbières de la Cuvette centrale** | P1 | ⭐ Enjeu carbone majeur et médiatique |
| **Limites administratives (GADM, officielles)** | P0 | Restitution par territoire |
| **Signalements citoyens & renseignement terrain** | P1 | ⭐ Données propriétaires |
| **Registres REDD+ / projets carbone** | P2 | Contexte, opportunités commerciales |

---

## 5. Protocole de validation scientifique — **non négociable**

C'est ce qui vous distinguera d'un projet étudiant. À appliquer intégralement.

### 5.1 Échantillonnage et estimation

- **Échantillonnage aléatoire stratifié** sur les strates de la carte produite
- Interprétation **à l'aveugle** par ≥ 2 interprètes, désaccords arbitrés par un tiers
- Matrice de confusion **pondérée par les surfaces réelles de chaque strate**
- **Estimation de surface non biaisée avec intervalle de confiance à 95 %**, selon la
  méthodologie de référence du domaine (Olofsson et al., 2014, *Remote Sensing of
  Environment*) — c'est la référence que citera tout auditeur
- Métriques par classe : précision utilisateur, précision producteur, F1, kappa
- **Aucune publication d'un chiffre de surface sans son intervalle de confiance**

### 5.2 Validation croisée

| Type | Objectif |
|---|---|
| **Spatiale par blocs** | Éviter la fuite par autocorrélation ✅ *déjà fait — le préserver* |
| **Temporelle prospective** | Entraîner sur le passé, prédire le futur, comparer au réel ❌ **à faire d'urgence** |
| **Géographique** | Entraîner au Mai-Ndombe, tester en Tshopo/Équateur — mesure la généralisation |
| **Inter-capteurs** | Cohérence Sentinel-2 vs Landsat |

### 5.3 Publication

| Action | Effet |
|---|---|
| Préprint sur les résultats de validation | Crédibilité immédiate, coût nul |
| Article dans une revue à comité de lecture (*Remote Sensing of Environment*, *Environmental Research Letters*, *Remote Sensing*) | ⭐ Autorité opposable en appel d'offres |
| Jeu de vérité terrain ouvert (une part) | Notoriété, réciprocité, positionnement de référence |
| Code des méthodes ouvert, produit fermé | Modèle MapBiomas : la transparence méthodologique crée la légitimité politique |
| Model cards et data sheets | Exigence croissante des bailleurs |

> **Recommandation forte :** publier **la comparaison honnête avec Hansen/GLAD/RADD**, y
> compris là où vous êtes moins bons. Un article qui dit « nous détectons mieux la
> dégradation en forêt marécageuse congolaise, moins bien la coupe rase que RADD » est
> **infiniment plus crédible et plus vendeur** qu'un communiqué annonçant 94 % de
> précision sans protocole. Les acheteurs institutionnels de ce secteur sont
> techniquement compétents et méfiants par expérience.

---

## 6. Décision sur la fonctionnalité « prédiction »

Le brief place la prédiction au centre. Analyse froide :

| Pour | Contre |
|---|---|
| Différenciation réelle : GFW, MapBiomas et Satelligence ne prédisent pas | Impossible à valider sans plusieurs années de recul |
| Valeur opérationnelle : patrouiller avant plutôt qu'après | Une prédiction fausse détruit la confiance dans **tout** le produit |
| Aligné sur l'identité académique du projet | Attaquable commercialement : « sur quoi repose ce 78 % ? » |
| Attendu par les méthodologies carbone (scénarios de référence) | Risque juridique si une prédiction motive une action coercitive |

**Recommandation :**

1. **La conserver**, c'est votre singularité.
2. **La reléguer au second rang** derrière la détection dans le discours produit et l'UI.
   On vend d'abord ce qui est vérifiable.
3. **Ne jamais l'exposer sans validation prospective publiée** et sans incertitude affichée.
4. La présenter comme une **aide à la priorisation des patrouilles** (« où regarder en
   premier »), jamais comme une prédiction d'événement (« ici sera déforesté »).
   Cette nuance de formulation change la nature du risque juridique.
5. La verrouiller derrière une mention explicite : *« indicatif — ne constitue pas un
   constat »*.

---

*Suite : [`05-architecture-securite.md`](05-architecture-securite.md)*
