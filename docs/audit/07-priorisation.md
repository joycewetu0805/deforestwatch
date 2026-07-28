# 07 — Tableau de priorisation

---

## Légende

| Colonne | Échelle |
|---|---|
| **Priorité** | 🔴 Critique · 🟠 Haute · 🟡 Moyenne · ⚪ Faible |
| **Valeur client** | ⭐ à ⭐⭐⭐⭐⭐ |
| **Difficulté** | 1 (trivial) à 5 (recherche) |
| **Coût** | Développement + infrastructure, hors salaires structurels |
| **Délai** | En jours-homme (j/h), équipe compétente |
| **Impact commercial** | Effet direct sur la capacité à signer |
| **Impact scientifique** | Contribution à la crédibilité et à la publication |

---

## A. Sprint 0 — correctifs bloquants (2 semaines)

| Fonctionnalité | Prio | Valeur | Diff. | Coût | Délai | Comm. | Sci. |
|---|:--:|:--:|:--:|--:|--:|:--:|:--:|
| Bandeau « données de démonstration » + flag API | 🔴 | ⭐⭐⭐⭐⭐ | 1 | 0,5 k€ | 1 j | Vital | — |
| Corriger l'erreur d'unité ×100 (`high_risk_ha`) | 🔴 | ⭐⭐⭐⭐⭐ | 1 | 0,2 k€ | 0,5 j | Vital | Fort |
| MFA réellement enforcée (login 2 temps) | 🔴 | ⭐⭐⭐⭐ | 2 | 1,5 k€ | 3 j | Vital | — |
| Supprimer l'admin par défaut hors démo | 🔴 | ⭐⭐⭐⭐⭐ | 1 | 0,3 k€ | 0,5 j | Vital | — |
| Refus de démarrage sur secret par défaut | 🔴 | ⭐⭐⭐⭐ | 1 | 0,3 k€ | 0,5 j | Vital | — |
| CORS liste blanche + cookies HttpOnly | 🔴 | ⭐⭐⭐⭐ | 1 | 0,5 k€ | 1 j | Vital | — |
| Rate-limiting + auth sur `POST /reports` | 🔴 | ⭐⭐⭐⭐ | 2 | 1 k€ | 2 j | Fort | — |
| Supprimer les replis silencieux sur données fausses | 🔴 | ⭐⭐⭐⭐⭐ | 2 | 1,5 k€ | 3 j | Vital | Fort |
| CI durcie (ruff, bandit, pip-audit, Trivy, `|| true` retiré) | 🟠 | ⭐⭐⭐ | 2 | 1,5 k€ | 3 j | Moyen | Moyen |
| Docker non-root, multi-stage, DB non exposée | 🟠 | ⭐⭐⭐ | 2 | 1 k€ | 2 j | Moyen | — |
| Nettoyage dépôt + scan de secrets historique | 🟠 | ⭐⭐ | 1 | 0,5 k€ | 1 j | Faible | — |
| Corriger `_edt` (Manhattan → euclidien) et retirer la fabrication de positifs | 🟠 | ⭐⭐ | 2 | 1 k€ | 2 j | Faible | **Fort** |
| Retirer les allégations fausses de résolution | 🔴 | ⭐⭐⭐⭐ | 1 | 0,3 k€ | 1 j | Vital | Fort |
| `SECURITY.md`, `LICENSE`, ADR | 🟠 | ⭐⭐ | 1 | 0,5 k€ | 2 j | Moyen | — |
| **Sous-total** | | | | **≈ 12 k€** | **25 j/h** | | |

---

## B. Socle données & télédétection (mois 1-6)

| Fonctionnalité | Prio | Valeur | Diff. | Coût | Délai | Comm. | Sci. |
|---|:--:|:--:|:--:|--:|--:|:--:|:--:|
| **Pipeline Sentinel-2 réel de bout en bout** | 🔴 | ⭐⭐⭐⭐⭐ | 4 | 45 k€ | 90 j | **Vital** | **Vital** |
| **Pipeline Sentinel-1 radar réel** | 🔴 | ⭐⭐⭐⭐⭐ | 4 | 40 k€ | 75 j | **Vital** | **Vital** |
| Masquage nuages réel (s2cloudless / Cloud Score+) | 🔴 | ⭐⭐⭐⭐ | 3 | 15 k€ | 30 j | Fort | **Vital** |
| CRS, reprojection, alignement, nodata | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 20 k€ | 35 j | **Vital** | **Vital** |
| Tuilage COG + pyramides + STAC | 🔴 | ⭐⭐⭐⭐ | 3 | 25 k€ | 45 j | Fort | Moyen |
| Serveur de tuiles (TiTiler) | 🔴 | ⭐⭐⭐⭐ | 3 | 15 k€ | 25 j | Fort | Faible |
| PostGIS + modèle de données spatial | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 20 k€ | 35 j | **Vital** | Fort |
| **AOI définissable par l'utilisateur** | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 18 k€ | 30 j | **Vital** | Faible |
| Couches métier (concessions, aires protégées, OSM, miniers) | 🔴 | ⭐⭐⭐⭐⭐ | 2 | 15 k€ | 30 j | **Vital** | Fort |
| Orchestration Dagster | 🟠 | ⭐⭐⭐ | 3 | 18 k€ | 30 j | Moyen | Moyen |
| Migration Spark → Dask | 🟠 | ⭐⭐⭐ | 3 | 15 k€ | 25 j | Faible | Moyen |
| Harmonisation Landsat (historique 2000→) | 🟡 | ⭐⭐⭐ | 4 | 25 k€ | 45 j | Moyen | Fort |
| **Sous-total** | | | | **≈ 271 k€** | **495 j/h** | | |

---

## C. Vérité terrain & science (mois 1-12) — ⭐ le plus fort levier

| Fonctionnalité | Prio | Valeur | Diff. | Coût | Délai | Comm. | Sci. |
|---|:--:|:--:|:--:|--:|--:|:--:|:--:|
| **Protocole d'échantillonnage + outil d'annotation** | 🔴 | ⭐⭐⭐⭐⭐ | 2 | 15 k€ | 25 j | Fort | **Vital** |
| **2 000 points photo-interprétés** | 🔴 | ⭐⭐⭐⭐⭐ | 2 | 25 k€ | 50 j | **Vital** | **Vital** |
| **200 points GPS terrain (campagne)** | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 35 k€ | 30 j | **Vital** | **Vital** |
| Estimation de surface non biaisée + IC 95 % | 🔴 | ⭐⭐⭐⭐ | 3 | 12 k€ | 20 j | Fort | **Vital** |
| **Validation prospective (2015-20 → 2021-23)** | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 15 k€ | 25 j | **Vital** | **Vital** |
| **Comparaison Hansen / GLAD / RADD / TMF** | 🔴 | ⭐⭐⭐⭐⭐ | 2 | 12 k€ | 20 j | **Vital** | **Vital** |
| **Boucle terrain → étiquette → modèle** | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 25 k€ | 40 j | **Vital** | **Vital** |
| Apprentissage actif | 🟠 | ⭐⭐⭐⭐ | 3 | 12 k€ | 20 j | Moyen | Fort |
| Estimation d'incertitude (conformal prediction) | 🟠 | ⭐⭐⭐⭐ | 4 | 15 k€ | 25 j | Fort | **Vital** |
| Préprint + article | 🟠 | ⭐⭐⭐⭐ | 3 | 10 k€ | 30 j | Fort | **Vital** |
| **Sous-total** | | | | **≈ 176 k€** | **285 j/h** | | |

---

## D. Modèles

| Fonctionnalité | Prio | Valeur | Diff. | Coût | Délai | Comm. | Sci. |
|---|:--:|:--:|:--:|--:|--:|:--:|:--:|
| XGBoost/LightGBM + variables temporelles | 🔴 | ⭐⭐⭐⭐ | 2 | 12 k€ | 20 j | Fort | Fort |
| **BFAST Monitor / rupture temporelle** | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 20 k€ | 35 j | **Vital** | **Vital** |
| **CuSum radar (type RADD)** | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 22 k€ | 35 j | **Vital** | **Vital** |
| **NDFI / dégradation** ⭐ différenciant | 🟠 | ⭐⭐⭐⭐⭐ | 3 | 25 k€ | 40 j | Fort | **Vital** |
| Régression logistique spatiale (référence risque) | 🔴 | ⭐⭐⭐ | 2 | 8 k€ | 12 j | Moyen | **Vital** |
| XGBoost risque + variables socio-économiques | 🟠 | ⭐⭐⭐⭐ | 3 | 18 k€ | 30 j | Fort | Fort |
| SHAP / XAI | 🟠 | ⭐⭐⭐⭐ | 2 | 10 k€ | 15 j | Fort | Fort |
| Filtrage des faux positifs (persistance, masques) | 🔴 | ⭐⭐⭐⭐⭐ | 2 | 15 k€ | 25 j | **Vital** | Fort |
| Siamese U-Net bi-temporel | 🟡 | ⭐⭐⭐⭐ | 4 | 35 k€ | 55 j | Moyen | Fort |
| Automate cellulaire (scénarios carbone) | 🟡 | ⭐⭐⭐ | 3 | 18 k€ | 30 j | Moyen | Fort |
| Temporal attention (LTAE) | 🟡 | ⭐⭐⭐⭐ | 4 | 40 k€ | 60 j | Moyen | Fort |
| Affinage de modèle de fondation | 🟡 | ⭐⭐⭐⭐ | 4 | 30 k€ | 45 j | Moyen | Fort |
| Biomasse GEDI + S1/S2 | 🟡 | ⭐⭐⭐⭐ | 4 | 35 k€ | 55 j | Fort | **Vital** |
| MLOps (MLflow, DVC, dérive, réentraînement) | 🟠 | ⭐⭐⭐ | 3 | 22 k€ | 35 j | Moyen | Fort |
| Apprentissage fédéré | ⚪ | ⭐⭐ | 5 | 50 k€ | 80 j | Faible | Moyen |
| Modèle de fondation propriétaire | ⚪ | ⭐⭐⭐ | 5 | 200 k€+ | 250 j | Moyen | **Vital** |
| **Sous-total (hors ⚪)** | | | | **≈ 310 k€** | **492 j/h** | | |

---

## E. Application & UX

| Fonctionnalité | Prio | Valeur | Diff. | Coût | Délai | Comm. | Sci. |
|---|:--:|:--:|:--:|--:|--:|:--:|:--:|
| **Carte 2D interactive (MapLibre/deck.gl)** | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 30 k€ | 50 j | **Vital** | Faible |
| Gestionnaire de couches + fonds de plan | 🔴 | ⭐⭐⭐⭐ | 2 | 12 k€ | 20 j | Fort | Faible |
| **Comparaison avant/après (rideau)** | 🔴 | ⭐⭐⭐⭐⭐ | 2 | 10 k€ | 15 j | **Vital** | Faible |
| **Curseur temporel + animation** | 🔴 | ⭐⭐⭐⭐ | 2 | 10 k€ | 15 j | Fort | Faible |
| Dessin d'AOI + import GeoJSON/SHP/KML | 🔴 | ⭐⭐⭐⭐⭐ | 2 | 12 k€ | 20 j | **Vital** | Faible |
| Inspection au clic + série temporelle du pixel | 🟠 | ⭐⭐⭐⭐ | 3 | 15 k€ | 25 j | Fort | Fort |
| Dashboard KPI + graphiques | 🔴 | ⭐⭐⭐⭐ | 2 | 25 k€ | 40 j | Fort | Faible |
| Unification des interfaces (abandon d'un frontend) | 🟠 | ⭐⭐⭐ | 2 | 15 k€ | 25 j | Moyen | — |
| Accessibilité (WCAG AA, palettes daltoniens) | 🟠 | ⭐⭐⭐ | 2 | 12 k€ | 20 j | Moyen | — |
| Internationalisation FR/EN + langues locales | 🟠 | ⭐⭐⭐⭐ | 2 | 15 k€ | 25 j | Fort | — |
| Carte 3D / terrain | 🟡 | ⭐⭐⭐ | 3 | 20 k€ | 30 j | Moyen | Faible |
| Design system | 🟡 | ⭐⭐ | 2 | 15 k€ | 25 j | Faible | — |
| Onboarding, aide contextuelle, états vides | 🟠 | ⭐⭐⭐ | 2 | 12 k€ | 20 j | Fort | — |
| **Sous-total** | | | | **≈ 203 k€** | **330 j/h** | | |

---

## F. Alertes, rapports, collaboration

| Fonctionnalité | Prio | Valeur | Diff. | Coût | Délai | Comm. | Sci. |
|---|:--:|:--:|:--:|--:|--:|:--:|:--:|
| Moteur d'alertes + seuils personnalisés + geofencing | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 25 k€ | 40 j | **Vital** | Moyen |
| **SMS + WhatsApp** | 🔴 | ⭐⭐⭐⭐⭐ | 2 | 15 k€ | 25 j | **Vital** | — |
| E-mail HTML + push | 🟠 | ⭐⭐⭐ | 2 | 8 k€ | 12 j | Fort | — |
| **Workflow de validation d'alerte** ⭐ | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 28 k€ | 45 j | **Vital** | Fort |
| Escalade + accusé de réception + SLA | 🟠 | ⭐⭐⭐⭐ | 2 | 15 k€ | 25 j | Fort | — |
| Agrégation anti-spam | 🔴 | ⭐⭐⭐⭐ | 2 | 10 k€ | 15 j | **Vital** | — |
| Webhooks signés | 🟠 | ⭐⭐⭐ | 2 | 8 k€ | 12 j | Moyen | — |
| Telegram / Slack / Discord | 🟡 | ⭐⭐ | 1 | 6 k€ | 10 j | Faible | — |
| **Dossier de preuve d'alerte (PDF signé)** ⭐ | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 25 k€ | 40 j | **Vital** | Fort |
| Rapports PDF/DOCX/XLSX/PPTX | 🟠 | ⭐⭐⭐⭐ | 3 | 25 k€ | 40 j | Fort | Moyen |
| Exports SIG (GeoJSON, SHP, GPKG, KML, GeoTIFF) | 🟠 | ⭐⭐⭐⭐ | 2 | 12 k€ | 20 j | Fort | Fort |
| Résumé exécutif + recommandations IA | 🟡 | ⭐⭐⭐ | 3 | 18 k€ | 28 j | Moyen | Faible |
| Rapports programmés | 🟠 | ⭐⭐⭐ | 2 | 10 k€ | 15 j | Fort | — |
| Rapport de conformité RDUE | 🟠 | ⭐⭐⭐⭐ | 3 | 20 k€ | 32 j | Fort | Moyen |
| Commentaires, annotations, mentions | 🟠 | ⭐⭐⭐ | 2 | 18 k€ | 30 j | Moyen | Faible |
| Partage sécurisé (liens expirants) | 🟠 | ⭐⭐⭐ | 2 | 10 k€ | 15 j | Fort | — |
| Portail citoyen modéré + anonymat | 🟡 | ⭐⭐⭐ | 3 | 22 k€ | 35 j | Moyen | Fort |
| **Sous-total** | | | | **≈ 275 k€** | **439 j/h** | | |

---

## G. Mobile

| Fonctionnalité | Prio | Valeur | Diff. | Coût | Délai | Comm. | Sci. |
|---|:--:|:--:|:--:|--:|--:|:--:|:--:|
| **Android hors-ligne (consultation + saisie)** ⭐ | 🔴 | ⭐⭐⭐⭐⭐ | 4 | 60 k€ | 100 j | **Vital** | Fort |
| Téléchargement de tuiles (MBTiles/PMTiles) | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 20 k€ | 32 j | **Vital** | — |
| Synchronisation différée + conflits | 🔴 | ⭐⭐⭐⭐⭐ | 4 | 25 k€ | 40 j | **Vital** | Fort |
| Formulaire de constat (photo GPS, signature, audio) | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 22 k€ | 35 j | **Vital** | **Vital** |
| Missions, itinéraires, navigation | 🟠 | ⭐⭐⭐⭐ | 3 | 18 k€ | 30 j | Fort | Moyen |
| Support Android 8+, < 100 Mo | 🔴 | ⭐⭐⭐⭐ | 3 | 12 k€ | 20 j | **Vital** | — |
| Chiffrement local + effacement à distance | 🟠 | ⭐⭐⭐⭐ | 3 | 12 k€ | 20 j | Fort | — |
| Langues locales | 🟠 | ⭐⭐⭐ | 2 | 8 k€ | 15 j | Fort | — |
| iOS / iPad | 🟡 | ⭐⭐ | 3 | 35 k€ | 55 j | Faible | — |
| **Sous-total (hors iOS)** | | | | **≈ 177 k€** | **292 j/h** | | |

---

## H. Plateforme, API, sécurité

| Fonctionnalité | Prio | Valeur | Diff. | Coût | Délai | Comm. | Sci. |
|---|:--:|:--:|:--:|--:|--:|:--:|:--:|
| **Multi-tenant + isolation testée** | 🔴 | ⭐⭐⭐⭐⭐ | 4 | 40 k€ | 65 j | **Vital** | — |
| **RBAC complet** | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 22 k€ | 35 j | **Vital** | — |
| ABAC territorial | 🟠 | ⭐⭐⭐⭐ | 3 | 15 k€ | 25 j | Fort | — |
| **Journal d'audit immuable** ⭐ | 🔴 | ⭐⭐⭐⭐⭐ | 3 | 25 k€ | 40 j | **Vital** | Fort |
| Chaînage cryptographique + ancrage | 🟡 | ⭐⭐⭐⭐ | 4 | 25 k€ | 38 j | Fort | Fort |
| Signature numérique des rapports | 🟠 | ⭐⭐⭐⭐ | 3 | 18 k€ | 28 j | Fort | Moyen |
| API v1 documentée + clés + quotas | 🔴 | ⭐⭐⭐⭐ | 3 | 25 k€ | 40 j | Fort | Fort |
| SDK Python | 🟠 | ⭐⭐⭐ | 2 | 12 k€ | 20 j | Moyen | Fort |
| SDK JavaScript | 🟡 | ⭐⭐ | 2 | 10 k€ | 16 j | Faible | Faible |
| GraphQL | 🟡 | ⭐⭐ | 3 | 18 k€ | 28 j | Faible | Faible |
| **Flux OGC (WMS/WMTS/WFS) + plugin QGIS** ⭐ | 🟠 | ⭐⭐⭐⭐ | 3 | 25 k€ | 38 j | **Fort** | Fort |
| Facturation, plans, quotas | 🟠 | ⭐⭐⭐⭐ | 3 | 28 k€ | 45 j | Fort | — |
| Observabilité complète | 🟠 | ⭐⭐⭐ | 3 | 20 k€ | 32 j | Moyen | — |
| Sauvegardes + PRA testé | 🔴 | ⭐⭐⭐⭐ | 3 | 18 k€ | 28 j | Fort | — |
| Kubernetes + IaC + GitOps | 🟡 | ⭐⭐⭐ | 4 | 45 k€ | 70 j | Moyen | — |
| SSO OIDC/SAML | 🟡 | ⭐⭐⭐ | 3 | 15 k€ | 25 j | Fort | — |
| Vault / gestion des secrets | 🟠 | ⭐⭐⭐ | 3 | 12 k€ | 20 j | Moyen | — |
| IDS/IPS + SIEM | 🟡 | ⭐⭐⭐ | 4 | 25 k€ | 38 j | Moyen | — |
| Test d'intrusion externe | 🟠 | ⭐⭐⭐⭐ | 2 | 18 k€ | 10 j | Fort | — |
| RGPD complet | 🔴 | ⭐⭐⭐⭐ | 2 | 20 k€ | 30 j | **Vital** | — |
| ISO 27001 | 🟡 | ⭐⭐⭐⭐ | 4 | 70 k€ | 120 j | Fort | — |
| Déploiement souverain on-premise | 🟡 | ⭐⭐⭐⭐ | 4 | 35 k€ | 55 j | Fort | — |
| **Sous-total** | | | | **≈ 561 k€** | **866 j/h** | | |

---

## Synthèse

| Bloc | Coût | Délai | Horizon |
|---|--:|--:|---|
| A — Sprint 0 | 12 k€ | 25 j/h | Immédiat |
| B — Socle données | 271 k€ | 495 j/h | Mois 1-6 |
| C — Vérité terrain & science ⭐ | 176 k€ | 285 j/h | Mois 1-12 |
| D — Modèles | 310 k€ | 492 j/h | Mois 3-24 |
| E — Application & UX | 203 k€ | 330 j/h | Mois 3-12 |
| F — Alertes & rapports | 275 k€ | 439 j/h | Mois 4-18 |
| G — Mobile | 177 k€ | 292 j/h | Mois 5-14 |
| H — Plateforme & sécurité | 561 k€ | 866 j/h | Mois 6-30 |
| **Total** | **≈ 1,99 M€** | **≈ 3 224 j/h** | **30 mois** |

Hors salaires structurels (produit, commercial, direction), infrastructure récurrente
(60-150 k€/an au-delà de l'an 2), imagerie THR (variable, refacturable) et coûts
juridiques et de conformité.

---

## Les 15 chantiers à lancer en premier

Si le budget est contraint, ne faites que ceux-ci. Ils représentent environ **35 % du
coût total et probablement 80 % de la capacité à signer un premier contrat.**

| # | Chantier | Coût | Pourquoi celui-là |
|--:|---|--:|---|
| 1 | Sprint 0 complet | 12 k€ | Rend le produit montrable sans risque |
| 2 | Pipeline Sentinel-2 réel | 45 k€ | Le point de non-retour du projet |
| 3 | Pipeline Sentinel-1 réel | 40 k€ | Lève le verrou nuageux — sans lui, pas de produit équatorial |
| 4 | 2 200 points de vérité terrain | 60 k€ | ⭐ La seule barrière à l'entrée durable |
| 5 | CRS + PostGIS + AOI utilisateur | 38 k€ | Transforme une démo en outil |
| 6 | Comparaison Hansen/GLAD/RADD | 12 k€ | La preuve que vous apportez quelque chose |
| 7 | Validation prospective | 15 k€ | Le seul chiffre de prédiction défendable |
| 8 | BFAST + CuSum radar | 42 k€ | La vraie détection de changement |
| 9 | Carte 2D interactive + avant/après | 40 k€ | Ce qui rend une démo convaincante en 30 secondes |
| 10 | Moteur d'alertes + SMS/WhatsApp | 40 k€ | Le canal réel du terrain |
| 11 | Workflow de validation d'alerte | 28 k€ | ⭐ Le différenciant produit |
| 12 | Dossier de preuve signé | 25 k€ | ⭐ Le différenciant commercial |
| 13 | Mobile Android hors-ligne | 100 k€ | ⭐ Ce que personne ne fera pour l'Afrique centrale |
| 14 | Multi-tenant + RBAC + audit | 87 k€ | Sans quoi on ne vend pas à deux clients |
| 15 | Filtrage des faux positifs | 15 k€ | Ce qui décide du renouvellement à l'an 2 |
| | **Total** | **≈ 599 k€** | **≈ 1 000 j/h — 12 à 14 mois** |

---

## Ce qu'il ne faut PAS faire tout de suite

Aussi important que la liste précédente. Chacun de ces chantiers est séduisant,
défendable en réunion, et destructeur de trésorerie au stade actuel.

| Chantier | Pourquoi attendre |
|---|---|
| Kubernetes, Kafka, microservices | Un ingénieur plateforme à plein temps pour dix utilisateurs |
| Vision Transformers, modèle de fondation propriétaire | Sans vérité terrain, ils feront **pire** qu'XGBoost |
| Apprentissage fédéré | Excellent argument de communication, valeur technique nulle avant d'avoir plusieurs pays clients |
| Application iOS | 85 % du parc cible est Android |
| GraphQL | Personne ne l'a demandé |
| Carte 3D, LiDAR, drones | Impressionne en démonstration, ne signe aucun contrat |
| MRV carbone commercialisé | Risque juridique majeur avant validation (R4) |
| ISO 27001 | Attendre que le premier grand compte l'exige et le finance |
| Six segments clients en parallèle | La cause d'échec la plus fréquente. Un seul segment. |
| Blockchain au-delà d'un simple ancrage de hash | Le hash horodaté suffit ; le reste est du bruit |

---

*Retour à l'index : [`README.md`](README.md)*
