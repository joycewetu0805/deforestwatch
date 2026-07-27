# 03 — Catalogue fonctionnel

> Toutes les fonctionnalités demandées dans le brief, plus celles qui manquaient.
> Priorités : **P0 Critique** (sans quoi rien ne se vend) · **P1 Haute** (nécessaire au
> premier contrat) · **P2 Moyenne** (différenciation) · **P3 Faible** (ambition long terme).
>
> Statut : ✅ fait · 🟡 partiel/factice · ❌ absent

---

## 1. Socle — les fondations sans lesquelles rien n'est vendable

| Réf | Fonctionnalité | Prio | Statut | Note |
|---|---|---|---|---|
| S-01 | **Traitement de vraies images Sentinel-2** de bout en bout | **P0** | ❌ | Le point de non-retour du projet |
| S-02 | **Traitement Sentinel-1 (radar)** réel | **P0** | 🟡 factice | Verrou technique n° 1 en zone équatoriale |
| S-03 | Gestion CRS, reprojection, alignement, nodata, rééchantillonnage | **P0** | ❌ | Prérequis SIG absolu |
| S-04 | Pipeline de tuilage COG + pyramides + serveur de tuiles | **P0** | ❌ | Condition de toute carte interactive |
| S-05 | Zone d'intérêt (AOI) définissable par l'utilisateur | **P0** | ❌ | Sans cela, ce n'est pas un produit de surveillance |
| S-06 | Multi-tenant (organisations isolées) | **P0** | ❌ | Refonte, pas une option |
| S-07 | Masquage nuages/ombres réel (s2cloudless, Cloud Score+) | **P0** | 🟡 aléatoire | |
| S-08 | Vérité terrain : collecte, stockage, versionnage | **P0** | ❌ | ⭐ Barrière à l'entrée |
| S-09 | Catalogue STAC des données | P1 | ❌ | |
| S-10 | Orchestration des traitements (Airflow/Dagster/Prefect) | P1 | ❌ | |
| S-11 | Registre de modèles + versionnage (MLflow) | P1 | ❌ | `ModelRegistry` existe en base, jamais écrit |
| S-12 | Ingestion multi-capteurs pluggable | P1 | 🟡 | L'abstraction existe, la substance non |
| S-13 | Harmonisation Landsat ↔ Sentinel-2 | P2 | ❌ | Nécessaire pour remonter avant 2015 |
| S-14 | Séries temporelles longues (2000→) via Landsat | P2 | ❌ | Indispensable pour les baselines carbone |

---

## 2. Tableau de bord

### 2.1 KPIs (bandeau supérieur)

| Réf | KPI | Prio |
|---|---|---|
| K-01 | Surface forestière actuelle (ha) + variation vs N-1 | P0 |
| K-02 | Perte sur la période sélectionnée (ha) + tendance | P0 |
| K-03 | Taux de déforestation annualisé (%) | P0 |
| K-04 | Alertes actives par sévérité | P0 |
| K-05 | Alertes non traitées / en retard de traitement (SLA) | P0 |
| K-06 | Délai médian détection → vérification → clôture | P1 |
| K-07 | Taux de confirmation terrain (précision réelle mesurée) | P1 |
| K-08 | CO₂ émis estimé ± incertitude | P1 |
| K-09 | Surface à risque élevé (prévision 12 mois) | P1 |
| K-10 | Fragmentation : nombre de patchs, taille moyenne, indice de forme | P2 |
| K-11 | Couverture d'observation : % de la zone observée sans nuage | P1 |
| K-12 | Surface sous surveillance active (ha) | P1 |
| K-13 | Coût d'imagerie consommé vs quota | P2 |
| K-14 | Comparaison au benchmark national / provincial | P2 |

> **Deux KPI qu'aucun concurrent n'affiche et qui feront votre crédibilité :**
> **K-07** (votre précision réelle mesurée sur le terrain, publiée, pas votre F1 de labo)
> et **K-11** (ce que vous n'avez pas pu observer). Assumer ses angles morts est le
> signal de sérieux le plus fort qu'on puisse envoyer à un acheteur institutionnel.

### 2.2 Graphiques et widgets

| Réf | Élément | Prio |
|---|---|---|
| G-01 | Courbe de couverture forestière 2000→aujourd'hui, avec bandes d'incertitude | P0 |
| G-02 | Barres de perte annuelle, empilées par cause présumée | P0 |
| G-03 | Heatmap de densité de déforestation (hexbin ou grille) | P0 |
| G-04 | Heatmap calendaire (jour × semaine) de l'activité | P1 |
| G-05 | Top 10 des secteurs/concessions les plus touchés | P0 |
| G-06 | Sankey : classe d'origine → classe d'arrivée (transitions) | P2 |
| G-07 | Courbe de risque prédit vs réalisé (backtesting visible) | P1 |
| G-08 | Boxplot de distribution des tailles de patchs | P2 |
| G-09 | Entonnoir : détectées → vérifiées → confirmées → sanctionnées | P1 |
| G-10 | Cumul CO₂ + équivalences | P1 |
| G-11 | Rose des vents de progression du front de déforestation | P3 |
| G-12 | Corrélations pluviométrie / saison / déforestation | P2 |
| G-13 | Petits multiples : une mini-carte par année | P2 |
| G-14 | Widgets déplaçables, tableaux de bord personnalisables et partageables | P2 |
| G-15 | Comparaison inter-zones (concession A vs B) | P1 |
| G-16 | Sparklines dans chaque cellule de tableau | P2 |
| G-17 | Export PNG/SVG/CSV de chaque graphique | P1 |

> **Règles de conception non négociables :**
> - **Jamais de vert/rouge comme seul canal d'information** (8 % des hommes sont
>   daltoniens ; votre palette actuelle est intégralement vert/rouge). Doubler par la
>   forme, la texture ou la valeur.
> - Palettes séquentielles perceptuellement uniformes (viridis, cividis), **jamais
>   jet/rainbow** — qui crée des frontières visuelles inexistantes.
> - Toute valeur estimée s'affiche avec son incertitude. Un nombre nu est une promesse
>   que vous ne pouvez pas tenir.
> - Toute donnée simulée est visuellement distincte (hachures, filigrane).

### 2.3 Tableaux de bord par rôle

| Rôle | Contenu prioritaire |
|---|---|
| Ministre / DG | 6 KPI, carte nationale, tendance, comparaison provinciale. Une page. |
| Chef de brigade | File d'alertes à traiter, carte opérationnelle, équipes sur le terrain |
| Agent de terrain | **Mobile uniquement** : mes missions du jour, itinéraire, formulaire |
| Analyste SIG | Outils complets, couches, export, requêtes spatiales |
| Responsable conformité (RDUE) | Parcelles, statut de conformité, dossiers à produire |
| Gestionnaire carbone | Baseline, additionnalité, fuites, incertitude |
| Chercheur | API, notebooks, jeux de données, méthodologie |

---

## 3. Cartographie

| Réf | Fonctionnalité | Prio | Statut |
|---|---|---|---|
| M-01 | **Carte 2D interactive** (MapLibre GL / deck.gl), zoom, pan, rotation | **P0** | ❌ (PNG statiques) |
| M-02 | Gestionnaire de couches : ordre, opacité, visibilité, groupes | **P0** | ❌ |
| M-03 | **Curseur temporel** + lecture animée | **P0** | 🟡 (TimeMachine sur PNG figés) |
| M-04 | **Comparaison avant/après** : rideau glissant, vue synchronisée, clignotement | **P0** | ❌ |
| M-05 | Fonds de plan : OSM, Google Satellite, Bing, Esri, Sentinel-2 récent, sombre/clair | **P0** | ❌ |
| M-06 | Sélecteur de capteur : Sentinel-2, Sentinel-1, Landsat, MODIS, Planet, drone | P1 | ❌ |
| M-07 | Compositions colorées à la volée (vraies couleurs, IRC, SWIR, NDVI, NBR) | P1 | ❌ |
| M-08 | Dessin d'AOI : polygone, rectangle, cercle, import GeoJSON/KML/SHP | **P0** | ❌ |
| M-09 | Mesure de distance et de surface | P1 | ❌ |
| M-10 | Inspection au clic : valeurs, série temporelle du pixel, historique | P1 | ❌ |
| M-11 | **Graphique de série temporelle du pixel** (le « profil NDVI ») | P1 | ❌ |
| M-12 | Géocodage / recherche de lieu, saisie de coordonnées | P1 | ❌ |
| M-13 | Légende dynamique, échelle, flèche du nord, minicarte | P1 | ❌ |
| M-14 | **Carte 3D / terrain** (MNT, extrusion, survol, ombrage) | P2 | ❌ |
| M-15 | Visualisation 3D de la canopée (GEDI, LiDAR) | P3 | ❌ |
| M-16 | Effet de rideau temporel sur imagerie très haute résolution | P2 | ❌ |
| M-17 | **Cartes hors-ligne + téléchargement de tuiles (MBTiles/PMTiles)** | **P0** (mobile) | ❌ |
| M-18 | Export cartographique : PNG, PDF, GeoTIFF, GeoJSON, SHP, KML | P1 | ❌ |
| M-19 | Impression avec mise en page cartographique (titre, légende, échelle, crédits) | P2 | ❌ |
| M-20 | Annotation : points, lignes, polygones, texte, flèches, épinglage | P1 | ❌ |
| M-21 | Cartes de chaleur, clusters de points, agrégation dynamique | P2 | ❌ |
| M-22 | Comparaison multi-fenêtres synchronisées (2×2) | P2 | ❌ |
| M-23 | Couches vectorielles métier : concessions, aires protégées, titres miniers, villages, routes, cours d'eau, limites administratives | **P0** | ❌ |
| M-24 | Cartographie participative (contributions citoyennes validées) | P3 | 🟡 |
| M-25 | Flux OGC : WMS/WMTS/WFS + STAC — pour brancher QGIS et ArcGIS | P1 | ❌ |
| M-26 | Intégration drone : upload, orthomosaïque, superposition | P3 | ❌ |
| M-27 | Vue « street level » terrain : photos géolocalisées horodatées | P2 | ❌ |

> **M-25 est sous-estimé.** Tout service SIG d'un ministère africain travaille sous QGIS.
> Un flux WMS/WFS consommable dans QGIS vaut plus, commercialement, que dix widgets web :
> il vous insère dans un flux de travail existant au lieu de demander qu'on l'abandonne.

---

## 4. Détection

### 4.1 Méthodes par phénomène

| Réf | Phénomène | Méthode recommandée | Capteur | Difficulté | Prio |
|---|---|---|---|---|---|
| D-01 | **Perte de couverture forestière** | Détection de rupture temporelle (CCDC/BFAST) + segmentation | S2 + S1 | Moyenne | **P0** |
| D-02 | **Dégradation** (coupe sélective, écrémage) | Analyse de mélange spectral (SMA/NDFI, méthode DEGRAD/JRC) + texture radar | S2 + S1 | **Élevée** | **P0** |
| D-03 | **Brûlis** | dNBR / NBR₂, anomalies thermiques VIIRS/MODIS, cicatrices post-feu | S2 + VIIRS | Faible | P1 |
| D-04 | **Exploitation illégale du bois** | Détection de routes de débardage + parcs à grumes + trouées en arête de poisson | S2 THR + S1 | Élevée | P1 |
| D-05 | **Mines / orpaillage artisanal** | Bassins de décantation (indices eau + turbidité), sols nus, expansion en bord de rivière | S2 + S1 | Moyenne | P1 |
| D-06 | **Agriculture** | Classification cultures + rotation + suivi de jachère | S2 séries | Moyenne | P1 |
| D-07 | **Routes clandestines** | Détection linéaire (Hough, morphologie, U-Net linéaire), différentiel vs OSM | S2 THR + S1 | Élevée | P1 |
| D-08 | **Expansion urbaine** | Indices bâti (NDBI), double-rebond radar, croissance de nuit (VIIRS DNB) | S2 + S1 + VIIRS | Faible | P2 |
| D-09 | **Détection de constructions** | Détection d'objets (YOLO/DETR) sur THR | Planet/Airbus | Élevée | P2 |
| D-10 | **Campements / occupation** | Détection d'objets + persistance temporelle + accessibilité | THR | Élevée | P2 |
| D-11 | **Fragmentation** | Métriques paysagères (taille de patch, densité de lisière, connectivité, MSPA) | Dérivé | Faible | P1 |
| D-12 | **Perte de biomasse** | Régression AGB (GEDI + S1/S2) + différentiel temporel | GEDI + S1/S2 | **Élevée** | P1 |
| D-13 | **Évolution de la canopée** | Hauteur de canopée (GEDI + ML), rugosité, trouées | GEDI + S2 | Élevée | P2 |
| D-14 | Plantations (palmier, hévéa, cacao) | Texture + phénologie + géométrie de plantation | S2 | Moyenne | P2 |
| D-15 | Inondations / dynamique des zones humides | Seuillage radar + indices eau | S1 | Faible | P2 |
| D-16 | Assèchement de tourbières | Humidité radar + subsidence InSAR | S1 | Très élevée | P3 |
| D-17 | Pistes d'atterrissage clandestines | Détection linéaire THR | THR | Élevée | P3 |
| D-18 | Trafic fluvial (grumes) | Détection d'objets sur les fleuves | THR / SAR | Très élevée | P3 |
| D-19 | Stress / mortalité de végétation | Anomalies NDVI/NDWI vs climatologie | S2 | Faible | P2 |
| D-20 | Régénération / reforestation | Tendance NDVI positive persistante | S2 | Faible | P1 |
| D-21 | Détection de changement générique non supervisée | Autoencodeur, écart de représentation, CVA | S2 | Moyenne | P2 |

> **Sur D-02 (dégradation) :** c'est **le** sujet du Bassin du Congo. La déforestation
> franche y est moins dominante qu'en Amazonie ; la dégradation par coupe sélective et
> agriculture itinérante l'est bien davantage. C'est aussi ce que GFW capte le moins bien.
> **C'est la meilleure cible scientifique différenciante du projet** — et celle qui
> justifie le mieux un discours de recherche appliquée.

### 4.2 Chaîne de traitement d'une alerte

```
Acquisition ──► Prétraitement ──► Détection ──► Filtrage ──► Qualification
   (S1/S2)      (nuages, CRS,     (modèle +     (bruit,      (cause probable,
                 harmonisation)    rupture)      taille min,   sévérité,
                                                 persistance)  confiance)
                                                                    │
     ┌──────────────────────────────────────────────────────────────┘
     ▼
Enrichissement ──► Priorisation ──► Notification ──► Vérification ──► Décision
(concession,       (score, SLA,     (SMS/WhatsApp/   (THR ou          (dossier,
 propriétaire,      proximité        push, escalade)  terrain)         PV, archive
 protection,        équipe)                                            probante)
 accès)                                                                    │
                                                                           ▼
                                                            ⭐ Étiquette de vérité
                                                               → réentraînement
```

**Le retour en boucle (dernière flèche) est la fonctionnalité la plus importante de tout
ce document.** C'est elle qui transforme un produit reproductible en actif propriétaire.

### 4.3 Réduction des faux positifs — indispensable

Un système à 20 % de faux positifs qui envoie 50 alertes/jour fait perdre confiance en
deux semaines et n'est jamais réutilisé. Mesures :

| Réf | Mesure | Prio |
|---|---|---|
| FP-01 | Persistance : confirmer sur ≥ 2 acquisitions | P0 |
| FP-02 | Surface minimale paramétrable | P0 |
| FP-03 | Croisement optique + radar | P0 |
| FP-04 | Masques d'exclusion (eau permanente, savane, cultures connues, nuages) | P0 |
| FP-05 | Filtre saisonnier (jachère, défeuillaison, crue) | P1 |
| FP-06 | Seuil de confiance ajustable par l'utilisateur | P0 |
| FP-07 | Apprentissage sur les retours humains (« rejetée » = contre-exemple) | P1 |
| FP-08 | Suppression des zones de coupe autorisée déclarées | P1 |

---

## 5. Alertes intelligentes

### 5.1 Canaux

| Réf | Canal | Prio | Note |
|---|---|---|---|
| A-01 | **E-mail** (HTML + PDF joint) | P0 | 🟡 partiel (SMTP existe) |
| A-02 | **SMS** (Africa's Talking, Twilio, agrégateur local) | **P0** | Le canal qui fonctionne réellement en province |
| A-03 | **WhatsApp Business API** | **P0** | Canal dominant en RDC |
| A-04 | Push mobile (FCM / APNS) | P1 | |
| A-05 | Telegram | P2 | |
| A-06 | Signal | P3 | Peu d'API officielle, coût/bénéfice défavorable |
| A-07 | Webhook générique signé (HMAC) | P1 | |
| A-08 | Slack | P2 | Cible ONG internationales |
| A-09 | Discord | P3 | Cible communautaire |
| A-10 | Radio / IVR vocal en langue locale | P3 | Innovant, forte adhérence terrain |
| A-11 | Flux RSS/Atom, calendrier ICS | P3 | |

### 5.2 Logique

| Réf | Fonctionnalité | Prio |
|---|---|---|
| A-20 | **Seuils personnalisés** par utilisateur, zone, type, sévérité | P0 |
| A-21 | **Géorepérage** : abonnement à une AOI dessinée | P0 |
| A-22 | Alertes multi-utilisateurs, listes de diffusion, groupes | P0 |
| A-23 | **Escalade automatique** (non traité en X h → N+1 → N+2) | P1 |
| A-24 | **Accusé de réception** et prise en charge nominative | P1 |
| A-25 | **Historique complet et immuable** | P0 |
| A-26 | Validation / rejet humain avec motif | P0 |
| A-27 | Agrégation anti-spam (digest, regroupement spatial, silence) | P0 |
| A-28 | Heures de silence, fréquence configurable | P1 |
| A-29 | Priorisation par score (surface × protection × accessibilité × récidive) | P1 |
| A-30 | Affectation à une équipe, itinéraire, planification de mission | P1 |
| A-31 | Alerte prédictive (« cette zone passera à risque élevé sous 3 mois ») | P2 |
| A-32 | Détection de récidive sur une même parcelle | P2 |
| A-33 | Corrélation multi-sources (satellite + signalement citoyen + renseignement) | P2 |
| A-34 | Suivi SLA et rapport de performance par équipe | P1 |
| A-35 | Mode « crise » : diffusion massive coordonnée | P3 |

---

## 6. Rapports

| Réf | Fonctionnalité | Prio |
|---|---|---|
| R-01 | **PDF** paginé, charté, avec cartes, graphiques, tableaux | P0 |
| R-02 | **Word (.docx)** éditable | P1 |
| R-03 | **Excel (.xlsx)** avec données brutes et tableaux croisés | P1 |
| R-04 | **PowerPoint (.pptx)** de synthèse | P2 |
| R-05 | Export GeoJSON / SHP / GeoPackage / KML | P1 |
| R-06 | CSV / Parquet | P1 |
| R-07 | Modèles de rapport personnalisables (logo, charte, sections) | P1 |
| R-08 | **Résumé exécutif généré automatiquement** | P1 |
| R-09 | **Recommandations générées par IA** (LLM sur données structurées) | P2 |
| R-10 | Génération programmée (hebdo/mensuel/trimestriel) + envoi | P1 |
| R-11 | Rapport à la demande sur une AOI et une période | P0 |
| R-12 | **Dossier de preuve d'alerte** (imagerie avant/après, coordonnées, méthode, chaîne de traçabilité, signature) | **P0** ⭐ |
| R-13 | Rapport de conformité RDUE | P1 |
| R-14 | Rapport MRV carbone | P2 |
| R-15 | Rapport de performance (SLA, taux de confirmation) | P1 |
| R-16 | Rapport public anonymisé (transparence) | P2 |
| R-17 | Signature électronique et horodatage qualifié | P2 |
| R-18 | Multilingue (FR/EN/PT) | P1 |
| R-19 | Comparatif inter-périodes ou inter-zones | P2 |
| R-20 | API de génération de rapport | P2 |

> **Sur R-09 (recommandations par IA) :** un LLM ne doit **jamais** produire de chiffre.
> Il rédige un texte à partir de chiffres calculés en amont, avec un gabarit contraint et
> une relecture humaine avant diffusion. Toute autre architecture crée un risque
> d'hallucination sur un document qui peut fonder une décision juridique ou financière.

---

## 7. Collaboration

| Réf | Fonctionnalité | Prio |
|---|---|---|
| C-01 | Organisations / espaces de travail isolés (multi-tenant) | **P0** |
| C-02 | Équipes, sous-équipes, unités territoriales | P1 |
| C-03 | **RBAC** : admin, gestionnaire, analyste, agent, lecteur, invité, auditeur | **P0** |
| C-04 | Permissions granulaires par ressource (AOI, couche, rapport) | P1 |
| C-05 | Invitations, SSO, provisionnement SCIM | P2 |
| C-06 | Commentaires et fils de discussion sur alertes et zones | P1 |
| C-07 | Mentions @ et notifications | P1 |
| C-08 | **Annotations cartographiques partagées** | P1 |
| C-09 | Partage sécurisé : lien expirant, mot de passe, lecture seule, audit d'accès | P1 |
| C-10 | **Historique des modifications** (qui, quand, quoi, valeur avant/après) | **P0** |
| C-11 | **Workflow de validation d'alerte** avec états et transitions | **P0** ⭐ |
| C-12 | Attribution de tâches et suivi | P1 |
| C-13 | Double validation pour les décisions sensibles | P2 |
| C-14 | Espace public / portail citoyen | P2 |
| C-15 | Signalement citoyen avec modération et anonymat protégé | P2 |
| C-16 | Bibliothèque documentaire partagée | P3 |
| C-17 | Édition collaborative temps réel | P3 |

> **⚠️ Sur C-15 :** un citoyen qui signale une exploitation illégale peut s'exposer à des
> représailles. **L'anonymat n'est pas une option de confort, c'est une obligation de
> protection.** Cela impose : pas de métadonnées EXIF conservées, pas d'IP journalisée,
> chiffrement, possibilité de suppression, et une analyse de risque documentée. À traiter
> comme une exigence de sécurité, pas comme une fonctionnalité produit.

---

## 8. API

| Réf | Fonctionnalité | Prio | Statut |
|---|---|---|---|
| P-01 | **REST versionnée** (`/v1`), pagination, filtres, tri | P0 | 🟡 |
| P-02 | **OpenAPI 3.1** complète, exemples, codes d'erreur normalisés | P0 | 🟡 auto-généré |
| P-03 | **Clés API** avec portées (scopes) et rotation | P0 | ❌ |
| P-04 | **OAuth2 / OIDC** (client credentials + authorization code) | P1 | ❌ |
| P-05 | JWT avec rotation, révocation, `jti` | P0 | 🟡 |
| P-06 | **Quotas et rate-limiting** par plan | P0 | ❌ |
| P-07 | **Journalisation d'usage** + facturation à l'appel | P1 | 🟡 |
| P-08 | **Webhooks sortants** signés, avec rejeu et file d'échec | P1 | ❌ |
| P-09 | **SDK Python** (`pip install deforestwatch`) | P1 | ❌ |
| P-10 | **SDK JavaScript/TypeScript** | P2 | ❌ |
| P-11 | GraphQL (requêtes composites analystes) | P2 | ❌ |
| P-12 | Flux OGC : WMS, WMTS, WFS, OGC API-Features/Tiles | P1 | ❌ |
| P-13 | **API STAC** pour le catalogue d'imagerie | P1 | ❌ |
| P-14 | Portail développeur avec bac à sable et clés de test | P2 | ❌ |
| P-15 | Statut de service public + historique d'incidents | P1 | ❌ |
| P-16 | Idempotence sur les écritures | P2 | ❌ |
| P-17 | Export asynchrone de gros volumes (job + callback) | P1 | ❌ |
| P-18 | Politique de dépréciation documentée | P2 | ❌ |
| P-19 | Plugin QGIS officiel | P2 | ❌ |
| P-20 | Connecteurs Power BI / Excel / ArcGIS | P3 | ❌ |

> **P-19 (plugin QGIS) coûte quelques jours et vaut cher.** Il place votre marque dans
> l'outil quotidien de chaque géomaticien du ministère.

---

## 9. Applications

### 9.1 Web (application principale)

Toutes les fonctionnalités. Responsive à partir de 1024 px. PWA installable. Objectifs :
premier rendu < 2 s sur connexion 3G, carte fluide à 60 fps, fonctionnement dégradé
acceptable à 500 kbit/s.

### 9.2 Mobile Android — ⭐ **priorité stratégique**

**Android d'abord et très loin devant iOS** : c'est ~85 % du parc en RDC, et les agents
de terrain sont équipés d'entrée de gamme.

| Réf | Fonctionnalité | Prio |
|---|---|---|
| MB-01 | **Fonctionnement hors-ligne complet** (consultation + saisie) | **P0** |
| MB-02 | Téléchargement de zone (tuiles + données) avant mission | **P0** |
| MB-03 | Synchronisation différée avec résolution de conflits | **P0** |
| MB-04 | Mes missions du jour, navigation vers le point | **P0** |
| MB-05 | **Formulaire de constat** : photos géolocalisées horodatées, GPS, notes vocales, signature | **P0** |
| MB-06 | Boussole, altitude, précision GPS affichée | P1 |
| MB-07 | Mode économie de batterie / données | P1 |
| MB-08 | Bouton d'alerte d'urgence | P2 |
| MB-09 | Fonctionnement sur Android 8+, < 100 Mo, < 2 Go de RAM | **P0** |
| MB-10 | Langues locales | P1 |
| MB-11 | Chiffrement local et effacement à distance (vol d'appareil) | P1 |
| MB-12 | Partage par Bluetooth/Wi-Fi Direct entre agents sans réseau | P3 |

### 9.3 iOS / iPad / tablette

iOS en P2 (cadres, bailleurs, ONG internationales). Tablette Android en P1 : c'est
l'outil de terrain préféré des brigades, avec un écran exploitable pour la carte.

### 9.4 Bureau

Plugin QGIS (P2) plutôt qu'une application native. Ne développez jamais un client lourd :
c'est un puits sans fond de maintenance pour un marché qui utilise déjà QGIS.

---

*Suite : [`04-ia-et-science.md`](04-ia-et-science.md)*
