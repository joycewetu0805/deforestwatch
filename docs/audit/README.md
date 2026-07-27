# Audit produit & cahier des charges — DeforestWatch-DRC → plateforme commerciale

> **Document de travail interne.** Audit technique, scientifique, produit, sécurité et
> commercial du logiciel existant, et cahier des charges de son évolution vers une
> plateforme de référence de surveillance des forêts d'Afrique centrale.
>
> Réalisé à partir d'une **lecture intégrale du code du dépôt** (164 fichiers, ~9 800 lignes
> Python/JSX) et de l'**exécution réelle de la suite de tests et de l'API**.
> Les constats marqués ✅ **vérifié** ont été reproduits par exécution, pas déduits.

| | |
|---|---|
| Date | 27 juillet 2026 |
| Périmètre | branche `claude/forest-monitoring-product-audit-lfeivt`, commit `438a24b` |
| Zone d'étude actuelle | Mai-Ndombe (Inongo), RDC — ~50 × 50 km |
| Verdict global | **Prototype de démonstration académique convaincant. Produit commercialisable : non. Écart estimé : 18–30 mois et 1,2–2,5 M€.** |

---

## Sommaire

| # | Document | Contenu |
|---|---|---|
| 00 | **Ce fichier** | Synthèse exécutive, verdict, 12 constats bloquants |
| 01 | [`01-audit-produit.md`](01-audit-produit.md) | Audit sévère du code réel : forces, failles, bugs, dette, UX, limites scientifiques |
| 02 | [`02-concurrence.md`](02-concurrence.md) | Benchmark des 10 plateformes, positionnement, différenciation défendable |
| 03 | [`03-fonctionnalites.md`](03-fonctionnalites.md) | Catalogue exhaustif : dashboard, cartographie, détection, alertes, rapports, collaboration, apps |
| 04 | [`04-ia-et-science.md`](04-ia-et-science.md) | Toutes les approches IA (coût/précision/difficulté), données, protocole de validation scientifique |
| 05 | [`05-architecture-securite.md`](05-architecture-securite.md) | Architecture cible, API, sécurité, conformité, souveraineté des données |
| 06 | [`06-business-roadmap.md`](06-business-roadmap.md) | Modèles économiques, pricing, go-to-market Afrique, roadmap 6 mois → 5 ans |
| 07 | [`07-priorisation.md`](07-priorisation.md) | Tableau de priorisation complet (valeur / difficulté / coût / délai / impact) |

---

## 1. Synthèse exécutive

### Ce que vous avez réellement

Un **prototype de démonstration bien construit**, propre, documenté en français, testé
(49 tests passent ✅ vérifié), conteneurisé, avec CI. Pour un projet de fin d'études L3,
c'est nettement au-dessus de la moyenne : l'architecture en couches
(`sources` → `provider` → API/dashboard) est une **vraie bonne décision d'ingénierie**,
et c'est ce qui rend la suite possible.

### Ce que vous n'avez pas

**Un produit.** Et il faut être direct sur le point qui invalide tout le reste :

> **La plateforme n'a jamais traité une seule image satellite réelle.**

Ce n'est pas une critique de style, c'est un constat mécanique. Le générateur
`src/utils/synthetic.py` produit une carte de classes à partir de trois « villages »
et d'une « route » diagonale (`np.abs(xx - yy) < 4`), puis en dérive des réflectances
par tirage gaussien autour de signatures spectrales codées en dur. **Tout** en découle :
les statistiques annuelles, les alertes, le CO₂, la carte de risque, les figures du
mémoire, les captures du frontend. Les modèles atteignent 0,80–0,92 de F1 parce que le
commentaire du code fixe explicitement le bruit pour atteindre cette plage
(`synthetic.py:98-100`). **Ces métriques ne mesurent rien d'autre que la capacité d'un
modèle à retrouver un tirage aléatoire dont il connaît la loi.**

Un investisseur, un directeur technique de la CAFI ou un acheteur chez Rainforest
Alliance identifiera cela en une réunion. Il faut donc traiter cette question **en
premier**, avant toute nouvelle fonctionnalité.

### Le verdict en une phrase

Vous avez construit **le squelette applicatif d'un produit qui n'existe pas encore** —
et c'est, paradoxalement, l'ordre le plus difficile à corriger, parce que le squelette
donne l'illusion que le produit est presque fini.

---

## 2. Les 12 constats bloquants

Classés par gravité. Les « ✅ vérifié » ont été reproduits en exécutant le code.

| # | Constat | Gravité | Preuve |
|---|---|---|---|
| **B1** | **Le 2FA est entièrement contournable.** `POST /auth/login` renvoie un JWT admin valide sans jamais vérifier l'OTP. `/auth/verify-otp` existe mais n'émet aucun jeton et n'est requis nulle part. | 🔴 Critique | ✅ vérifié — `admin/users` → **200** avec un token obtenu sans OTP |
| **B2** | **Compte admin par défaut créé automatiquement en production.** `_seed_admin()` (`src/api/main.py:38-58`) n'est **pas** conditionné à `demo_mode`. Tout déploiement expose `admin@deforestwatch.cd` / `admin123`, identifiants publiés dans le README, le dashboard et l'écran de login. | 🔴 Critique | ✅ vérifié — login réussi |
| **B3** | **Aucun modèle entraîné n'est utilisé à l'inférence.** `RiskPredictor` est entraîné puis sauvegardé par `trainer.py` — et **jamais rechargé**. L'API sert `synthetic.risk_map()`, une décroissance exponentielle `100·exp(−d/12)` sur la distance à la zone déforestée. La « prédiction par Machine Learning » du titre du projet n'a pas de modèle derrière elle au runtime. | 🔴 Critique | ✅ vérifié — aucun `joblib.load` de `risk_predictor.joblib` dans tout le dépôt |
| **B4** | **Erreur d'unité d'un facteur 100 sur les surfaces à risque.** `routes.py:155` code en dur `high * 0.038` ha/pixel alors que `PIXEL_AREA_HA = 3,8147`. L'API annonce **267,9 ha** là où sa propre convention donne **26 890 ha**. | 🔴 Critique | ✅ vérifié — `PIXEL_AREA_HA/0,038 = 100,4` |
| **B5** | **La résolution annoncée est fausse d'un facteur ~20.** Le README vend du Sentinel-2 à 10 m ; la grille est de 256 px pour 50 km, soit **195 m/pixel**. À 195 m, une coupe artisanale d'un hectare est invisible : c'est 0,026 pixel. Le produit ne peut structurellement pas détecter ce qu'il prétend détecter. | 🔴 Critique | `settings.py:137-138` |
| **B6** | **La fonctionnalité radar Sentinel-1 est un décor.** `RadarCollector.annual_composite()` construit la collection GEE, l'assigne à `self._last`… puis **retourne des données synthétiques**, y compris en mode réel (`radar.py:93-96`). `cloud_penetration_demo()` code en dur `radar_usable_pct = 100.0`. | 🔴 Critique | `src/data/radar.py` |
| **B7** | **CORS `allow_origins=["*"]` avec `allow_credentials=True`.** Configuration rejetée par la spec CORS et par tout audit de sécurité. Combinée à B1/B2, elle rend l'admin exploitable depuis n'importe quel site. | 🔴 Critique | `main.py:29-35` |
| **B8** | **`POST /api/v1/reports` est ouvert sans authentification ni rate-limit.** N'importe qui peut injecter un volume illimité de faux signalements géolocalisés. Sur un produit dont la valeur est la **preuve**, c'est un vecteur d'empoisonnement de la donnée autant qu'un déni de service. | 🟠 Élevé | ✅ vérifié — **200** sans token |
| **B9** | **Secret JWT par défaut fonctionnel.** `jwt_secret_key` a une valeur par défaut utilisable ; aucun garde-fou n'empêche de démarrer en production avec. Quiconque lit le dépôt public peut forger un token admin. | 🔴 Critique | `settings.py:34` |
| **B10** | **Pas de géométrie, pas de SIG.** Aucun CRS, aucune projection, aucun `GeoDataFrame`, pas de PostGIS. Les coordonnées d'alerte sont interpolées linéairement dans une bbox lat/lon (`alerts.py:53-64`) — approximation plan carré, sans reprojection. Un produit SIG vendu à des États ne peut pas ignorer la géodésie. | 🔴 Critique | `alerts.py`, absence de PostGIS |
| **B11** | **La chaîne « réelle » n'a jamais été exécutée sur du réel.** `RasterSource` lit des GeoTIFF mais ignore le géoréférencement, ne gère ni le CRS, ni le nodata, ni le rééchantillonnage, ni l'alignement inter-années. Et si les vraies images n'ont pas d'étiquettes, `provider.landcover_series()` **retombe silencieusement sur le synthétique** (`provider.py:66-68`) : l'utilisateur croit voir ses données, il voit la simulation. | 🔴 Critique | `provider.py:62-68`, `sources.py:130-140` |
| **B12** | **La CI ne teste pas ce que le produit prétend faire.** `requirements-ci.txt` exclut TensorFlow, XGBoost, rasterio, GDAL, PySpark. Les tests s'exécutent donc systématiquement sur les **chemins de repli** (U-Net → centroïdes spectraux, Spark → pandas). Le lint est neutralisé par `|| true`. La CI verte ne prouve rien sur le cœur métier. | 🟠 Élevé | `.github/workflows/ci.yml:26-29` |

**Sept constats critiques sont des correctifs de moins d'une journée chacun** (B1, B2, B4,
B7, B9 en particulier). Ils ne coûtent presque rien à corriger et coûteraient
extrêmement cher à laisser passer en démonstration client. Voir
[`01-audit-produit.md § 7`](01-audit-produit.md#7-plan-de-remédiation-immédiat-sprint-0).

---

## 3. Ce qui est réellement bon — et qu'il faut préserver

Il serait malhonnête de ne lister que les failles. Quatre décisions sont bonnes et
constituent l'actif réel du projet :

1. **L'abstraction de source de données** (`DataSource` → `SyntheticSource` /
   `RasterSource`, résolue par `provider`). C'est le bon pattern, appliqué au bon
   endroit. Il rend le basculement démo → réel possible sans réécrire l'application.
   *À conserver et à durcir* (cf. B11).
2. **Le split spatial par blocs** (`dataset_builder.spatial_block_split`). Beaucoup de
   travaux académiques et pas mal de produits commerciaux font un split aléatoire pixel
   à pixel et publient des scores gonflés par l'autocorrélation spatiale. Vous ne faites
   pas cette erreur. C'est un vrai marqueur de sérieux méthodologique — mettez-le en avant.
3. **La stratégie de repli systématique** (GEE → synthétique, PostgreSQL → SQLite,
   TensorFlow → centroïdes, Spark → pandas). Excellente pour la démonstrabilité.
   **Dangereuse en production** : un repli silencieux sur des données fausses est pire
   qu'une erreur. À conserver, mais rendre **bruyant et explicite** (cf. B11).
4. **La qualité éditoriale.** Docstrings en français, README, GUIDE, IMPACT, synthèse
   technique, mémoire et slides générés par script. La capacité à produire de la
   documentation est un actif commercial sous-estimé sur les marchés d'appels d'offres
   institutionnels.

---

## 4. Le repositionnement stratégique recommandé

L'erreur à ne pas commettre serait d'essayer de battre Global Forest Watch sur son
terrain. GFW est gratuit, financé par le WRI, adossé aux données de Hansen/GLAD/RADD et
dispose de dix ans d'avance. **Vous ne gagnerez jamais sur « la carte de déforestation ».**

La donnée de déforestation est devenue une commodité gratuite. **Ce qui n'est pas
gratuit, et ce qui est douloureux pour le client, c'est la chaîne qui va de l'alerte à
l'acte juridique ou financier :** vérifier, qualifier, géolocaliser sur une concession
nommée, notifier le bon agent, prouver qu'il est intervenu, et produire une pièce
opposable devant un tribunal, un auditeur carbone ou un régulateur européen.

**Positionnement recommandé :**

> **La couche opérationnelle et probante de la surveillance forestière en Afrique
> centrale.** Pas un observatoire — un système d'information métier pour les
> administrations forestières, les concessionnaires soumis au RDUE et les porteurs de
> projets carbone du Bassin du Congo.

Cinq angles de différenciation défendables face aux acteurs mondiaux, détaillés dans
[`02-concurrence.md`](02-concurrence.md) :

| Angle | Pourquoi c'est défendable |
|---|---|
| **Chaîne de preuve** | Alerte horodatée, signée, versionnée, exportable en pièce juridique. Personne ne le fait sérieusement en Afrique centrale. |
| **Hors-ligne first** | La connectivité en province RDC est le vrai facteur limitant. GFW/Planet sont pensés pour des analystes connectés à Washington ou Amsterdam. |
| **Ancrage réglementaire local** | Code forestier RDC, concessions, aires protégées ICCN, cahiers des charges sociaux. Les acteurs mondiaux ne descendront jamais à ce niveau de spécificité. |
| **Conformité RDUE côté producteur** | Satelligence sert l'acheteur européen. Le producteur africain qui doit *prouver* sa conformité n'est servi par personne. |
| **Souveraineté & langue** | Données hébergées sous contrôle national, interface française et lingala/swahili. Argument décisif en appel d'offres public. |

---

## 5. Chiffrage et calendrier de synthèse

| Horizon | Objectif | Effort | Budget | Jalon de sortie |
|---|---|---|---|---|
| **Sprint 0** (2 sem.) | Correctifs bloquants B1–B12 | 25 j/h | ~12 k€ | Démo montrable sans risque |
| **6 mois** | Première vraie image traitée, MVP vendable, 1 client pilote | 900 j/h | 280–380 k€ | Contrat pilote signé |
| **12 mois** | Production, SLA, mobile hors-ligne, 5 clients | 2 100 j/h | 750 k€–1,0 M€ | 250–400 k€ ARR |
| **3 ans** | 4 pays, IA propriétaire validée, référence régionale | — | 3,5–5 M€ cumulés | 2,5–4 M€ ARR |
| **5 ans** | Standard du Bassin du Congo, extension pantropicale | — | 8–12 M€ cumulés | 8–15 M€ ARR |

Détail dans [`06-business-roadmap.md`](06-business-roadmap.md).

---

## 6. Les trois décisions à prendre maintenant

Tout le reste en découle.

1. **Traiter une vraie image, sur une vraie zone, avec une vraie vérité terrain, avant
   d'écrire une ligne de fonctionnalité nouvelle.** Tant que ce n'est pas fait, chaque
   feature ajoutée est de la dette construite sur du sable. C'est le point de non-retour
   du projet.
2. **Choisir le client n° 1 et n'écrire que pour lui.** Administration forestière,
   concessionnaire RDUE ou projet carbone : les trois ont des besoins incompatibles en
   termes de résolution, de fréquence et de format de preuve. Vouloir servir les six
   segments listés dans le brief garantit de n'en convaincre aucun.
3. **Décider si la prédiction reste dans le produit.** C'est le cœur académique du
   projet, mais c'est aussi ce qui est le plus difficile à valider et le plus facile à
   attaquer commercialement (« sur quoi repose votre 78 % ? »). Recommandation :
   **la conserver, mais la reléguer au second plan derrière la détection**, et ne la
   commercialiser qu'après validation rétrospective publiée (cf.
   [`04-ia-et-science.md § 6`](04-ia-et-science.md)).

---

*Documents suivants : commencer par [`01-audit-produit.md`](01-audit-produit.md).*
