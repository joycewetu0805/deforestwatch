# 05 — Architecture cible et sécurité

---

## 1. Principe directeur

> **Ne construisez pas cette architecture maintenant.**

Le schéma ci-dessous est la cible à 24-36 mois, pour 5 000 utilisateurs et plusieurs pays.
Le déployer aujourd'hui, avec un client et zéro donnée réelle, serait la meilleure façon
de brûler la trésorerie : Kubernetes et Kafka pour dix utilisateurs coûtent un
ingénieur plateforme à plein temps et ralentissent tout.

**Séquence recommandée :**

| Étape | Quand | Architecture |
|---|---|---|
| **1. Monolithe modulaire** | 0-12 mois | FastAPI + PostgreSQL/PostGIS + Redis + workers Celery + S3, sur 2-3 VM. **C'est ce qu'il faut faire maintenant.** |
| **2. Extraction ciblée** | 12-24 mois | Sortir uniquement le traitement d'imagerie et le service de tuiles. Kubernetes managé. |
| **3. Microservices** | 24 mois+ | Le schéma complet, **quand la douleur le justifie** — jamais avant. |

Le point crucial est de **structurer le code en modules à frontières nettes dès
maintenant** (ce que vous faites déjà correctement), pour que l'extraction future soit
mécanique. La modularité est une discipline de code ; les microservices sont un choix de
déploiement. Ne confondez pas les deux.

---

## 2. Architecture cible

```
                          ┌──────────────────────────────┐
                          │   CDN + WAF + DDoS           │
                          └──────────────┬───────────────┘
                                         │
                    ┌────────────────────▼────────────────────┐
                    │   API Gateway (Kong / Traefik)          │
                    │   AuthN/Z · rate-limit · quotas · logs  │
                    └────┬──────────┬──────────┬──────────┬───┘
                         │          │          │          │
   ┌─────────────────────▼──┐ ┌─────▼──────┐ ┌─▼────────┐ ┌▼──────────────┐
   │ svc-identity           │ │ svc-aoi    │ │ svc-     │ │ svc-tiles     │
   │ users, orgs, RBAC,     │ │ zones,     │ │ alerts   │ │ TiTiler,      │
   │ MFA, SSO, clés API     │ │ concess.,  │ │ règles,  │ │ COG, WMTS,    │
   └────────────────────────┘ │ PostGIS    │ │ workflow │ │ vector tiles  │
                              └────────────┘ └──────────┘ └───────────────┘
   ┌────────────────────────┐ ┌────────────┐ ┌──────────┐ ┌───────────────┐
   │ svc-ingest             │ │ svc-       │ │ svc-     │ │ svc-notify    │
   │ STAC, S1/S2/Landsat,   │ │ inference  │ │ reports  │ │ SMS/WhatsApp/ │
   │ catalogue, téléchargt. │ │ modèles,   │ │ PDF,     │ │ mail/push/    │
   └────────────────────────┘ │ GPU, files │ │ DOCX,XLS │ │ webhook       │
   ┌────────────────────────┐ └────────────┘ └──────────┘ └───────────────┘
   │ svc-process            │ ┌────────────┐ ┌──────────────────────────┐
   │ nuages, indices,       │ │ svc-audit  │ │ svc-billing              │
   │ mosaïques, Dask        │ │ journal    │ │ plans, quotas, factures  │
   └────────────────────────┘ │ immuable   │ └──────────────────────────┘
                              └────────────┘
   ═══════════════════════════════ BUS ═══════════════════════════════════
              Kafka / Redpanda  ·  événements : image.ready, change.detected,
                                   alert.raised, alert.verified, model.deployed
   ═══════════════════════════════════════════════════════════════════════
   ┌──────────────┬──────────────┬──────────────┬──────────────┬─────────┐
   │ PostgreSQL   │ Redis        │ S3 / MinIO   │ TimescaleDB  │ Vault   │
   │ + PostGIS    │ cache,       │ COG, tuiles, │ séries       │ secrets │
   │ (métier)     │ files, verrous│ modèles,PDF │ temporelles  │         │
   └──────────────┴──────────────┴──────────────┴──────────────┴─────────┘
   ┌───────────────────────────────────────────────────────────────────────┐
   │ Orchestration : Dagster / Airflow — DAG quotidiens et à la demande     │
   │ Calcul distribué : Dask / Ray sur Kubernetes, autoscaling, spot        │
   └───────────────────────────────────────────────────────────────────────┘
   ┌───────────────────────────────────────────────────────────────────────┐
   │ Observabilité : OpenTelemetry · Prometheus · Grafana · Loki · Sentry   │
   │ CI/CD : GitHub Actions → ArgoCD (GitOps) · Terraform · déploiement     │
   │         progressif (canary) · retour arrière automatique               │
   └───────────────────────────────────────────────────────────────────────┘
```

---

## 3. Justification des choix

| Composant | Choix | Pourquoi ce choix précisément |
|---|---|---|
| **API** | FastAPI | Déjà en place, async natif, OpenAPI auto, Pydantic pour la validation, écosystème Python = même langage que la data science. Ne pas changer. |
| **Base métier** | PostgreSQL + **PostGIS** | 🔴 **Le manque le plus criant.** PostGIS apporte les index spatiaux (GiST), les jointures géométriques (« quelle concession contient cette alerte ? »), les reprojections, le raster. Sans lui, chaque requête spatiale est réimplémentée en Python — lentement et faussement. |
| **Séries temporelles** | TimescaleDB | Extension PostgreSQL : pas de base supplémentaire à exploiter. Compression et agrégats continus sur les séries NDVI et les métriques. |
| **Cache / files** | Redis | Cache de tuiles, sessions, verrous distribués, files Celery, rate-limiting. Simple, éprouvé. |
| **Stockage objet** | S3 / MinIO | Les rasters sont volumineux et immuables : c'est exactement le cas d'usage. MinIO permet un déploiement souverain **on-premise** — argument commercial décisif face aux États. |
| **Format raster** | **COG + STAC** | Le Cloud-Optimized GeoTIFF permet la lecture partielle par plage HTTP : on lit une tuile sans télécharger le fichier. C'est ce qui rend une carte interactive possible sur de grandes emprises. STAC standardise le catalogue et vous rend interopérable. **Choix structurant n° 1.** |
| **Service de tuiles** | TiTiler / pg_tileserv | Génération de tuiles à la volée depuis les COG. Remplace vos PNG statiques (U2/U3). |
| **Bus** | Kafka ou **Redpanda** | Découple détection, notification, audit et facturation. Redpanda : compatible Kafka sans JVM ni ZooKeeper, bien plus léger à exploiter pour une petite équipe. **Préférer Redpanda.** |
| **Orchestration de traitements** | **Dagster** | Meilleur qu'Airflow pour les pipelines de données : notion d'actif (asset), typage, tests, relance partielle, lignage. La relance partielle compte quand un traitement de 6 h échoue à la 5ᵉ heure. |
| **Calcul distribué** | **Dask** (pas Spark) | 🔴 **Remplacer PySpark.** Dask est natif Python, s'intègre à xarray/rioxarray/numpy, et est **conçu pour les tableaux multidimensionnels géospatiaux**. Spark est conçu pour des lignes tabulaires : c'est le mauvais modèle de données pour du raster, et il impose une JVM. Votre `spark_pipeline.py` (D15) est une justification académique, pas technique. |
| **Conteneurs** | Docker + Kubernetes managé | K8s **seulement à l'étape 2**. Managé (EKS/GKE/Scaleway) : n'exploitez jamais un plan de contrôle vous-même à cette taille. |
| **IaC** | Terraform + Terragrunt | Reproductibilité, multi-environnements, exigence d'audit. |
| **CI/CD** | GitHub Actions → ArgoCD | GitOps : l'état déployé est décrit dans Git, donc auditable et réversible. |
| **Secrets** | Vault ou SOPS + KMS | Prérequis pour S17 et pour toute certification. |
| **Observabilité** | OpenTelemetry, Prometheus, Grafana, Loki, Sentry | Standard ouvert, pas d'enfermement fournisseur. |
| **Cloud** | **Hybride** | Cloud européen (Scaleway/OVH — RGPD, souveraineté, coût) + **option de déploiement souverain on-premise** pour les États exigeants. Le mode on-premise est un argument de vente, pas une contrainte : facturez-le. |

### Sur la haute disponibilité et la reprise

| Exigence | Cible | Moyen |
|---|---|---|
| Disponibilité | 99,5 % (an 1) → 99,9 % (an 3) | Multi-AZ, réplicas, health checks |
| **RPO** (perte de données max.) | 15 min | WAL streaming PostgreSQL + snapshots |
| **RTO** (temps de reprise max.) | 4 h (an 1) → 1 h (an 3) | Runbook testé, IaC, sauvegardes vérifiées |
| Sauvegardes | Quotidiennes, 30 j + mensuelles 7 ans | 3-2-1, dont une copie hors région, **chiffrée** |
| **Test de restauration** | **Trimestriel obligatoire** | ⚠️ Une sauvegarde jamais restaurée n'est pas une sauvegarde |

---

## 4. Sécurité — cahier des charges

### 4.1 Authentification et accès

| Réf | Exigence | Prio |
|---|---|---|
| SEC-01 | **MFA réellement enforcée** : TOTP + codes de secours + WebAuthn/Passkeys. Login en 2 temps avec jeton intermédiaire de portée limitée | **P0** 🔴 corrige B1 |
| SEC-02 | MFA obligatoire pour tout rôle admin | P0 |
| SEC-03 | Politique de mot de passe : ≥ 12 caractères, vérification contre les fuites connues (HIBP k-anonymity), blocage progressif | P0 |
| SEC-04 | Suppression de tout compte par défaut hors développement | **P0** 🔴 corrige B2 |
| SEC-05 | Refus de démarrage si secret par défaut hors développement | **P0** 🔴 corrige B9 |
| SEC-06 | JWT courts (15 min) + refresh rotatif avec `jti` et révocation | P0 |
| SEC-07 | Cookies `HttpOnly` `Secure` `SameSite=Strict` + CSRF, plutôt que localStorage | P0 |
| SEC-08 | SSO OIDC/SAML (Azure AD, Keycloak) pour les grands comptes | P1 |
| SEC-09 | Verrouillage progressif, détection de bourrage d'identifiants | P0 |
| SEC-10 | Gestion des sessions : liste, révocation, expiration d'inactivité | P1 |
| SEC-11 | Clés API à portées, rotation, expiration, révocation immédiate | P1 |

### 4.2 Autorisation

| Réf | Exigence | Prio |
|---|---|---|
| SEC-20 | **RBAC** complet : super-admin, admin org, gestionnaire, analyste, agent, lecteur, auditeur, API | P0 |
| SEC-21 | **ABAC** sur les zones : un agent ne voit que son territoire | P1 |
| SEC-22 | **Isolation multi-tenant vérifiée par des tests automatisés** — le risque de fuite inter-organisation est le plus grave d'un SaaS | **P0** |
| SEC-23 | Row-Level Security PostgreSQL comme second rempart | P1 |
| SEC-24 | Principe du moindre privilège sur les services et la base | P0 |
| SEC-25 | Séparation des devoirs : l'admin ne peut pas altérer le journal d'audit | P1 |

### 4.3 Chiffrement et données

| Réf | Exigence | Prio |
|---|---|---|
| SEC-30 | TLS 1.3 partout, HSTS, pas de version antérieure à 1.2 | P0 |
| SEC-31 | Chiffrement au repos : disques, base, objets (SSE-KMS) | P0 |
| SEC-32 | Chiffrement colonne pour les données personnelles et les identités de lanceurs d'alerte | **P1** ⚠️ enjeu de sécurité des personnes |
| SEC-33 | Vault/KMS, rotation, aucun secret dans le code ou les images | P0 |
| SEC-34 | Anonymisation des signalements : suppression EXIF, pas de journalisation IP | **P1** |
| SEC-35 | Purge des données en environnement hors production | P1 |
| SEC-36 | Classification des données (public / interne / confidentiel / sensible) | P1 |

### 4.4 Audit et traçabilité

| Réf | Exigence | Prio |
|---|---|---|
| SEC-40 | **Journal d'audit immuable append-only** : qui, quoi, quand, depuis où, avant/après | **P0** ⭐ |
| SEC-41 | Chaînage cryptographique des entrées (hash de l'entrée précédente) | P1 |
| SEC-42 | Ancrage périodique du hash racine sur un registre public (horodatage opposable) | P2 ⭐ différenciant |
| SEC-43 | Rétention 7 ans (aligné sur les délais de prescription) | P1 |
| SEC-44 | Consultation par un auditeur externe, sans droit de modification | P1 |
| SEC-45 | Corrélation d'identifiant de requête de bout en bout | P1 |
| SEC-46 | **Signature numérique des rapports de preuve** (certificat qualifié) | P1 ⭐ |
| SEC-47 | Horodatage qualifié (RFC 3161) des alertes | P2 |

### 4.5 Protection applicative et infrastructure

| Réf | Exigence | Prio |
|---|---|---|
| SEC-50 | WAF + protection DDoS + bot management | P0 |
| SEC-51 | **Rate-limiting** par IP, utilisateur, clé, plan | **P0** 🔴 corrige S5 |
| SEC-52 | CORS en liste blanche stricte | **P0** 🔴 corrige B7 |
| SEC-53 | En-têtes de sécurité : CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy | P0 |
| SEC-54 | Validation stricte des entrées, ORM paramétré, jamais de SQL concaténé | P0 |
| SEC-55 | Antivirus et validation de type sur les fichiers téléversés, stockage isolé | P1 |
| SEC-56 | **SAST + DAST + SCA + scan de conteneurs + scan de secrets en CI** | **P0** 🔴 corrige B12 |
| SEC-57 | Conteneurs non-root, distroless, systèmes de fichiers en lecture seule | P0 |
| SEC-58 | Segmentation réseau, politiques réseau K8s, pas de base exposée | P0 |
| SEC-59 | **IDS/IPS** + détection de comportement anormal (Falco, GuardDuty) | P1 |
| SEC-60 | Bastion, accès just-in-time, MFA sur l'infrastructure | P1 |
| SEC-61 | **Test d'intrusion externe annuel** + après chaque changement majeur | P1 |
| SEC-62 | Programme de divulgation responsable / bug bounty | P2 |
| SEC-63 | Plan de réponse à incident + exercice de simulation annuel | P1 |
| SEC-64 | Alertes de sécurité en temps réel (SIEM) | P2 |

### 4.6 Conformité

| Réf | Exigence | Prio | Note |
|---|---|---|---|
| SEC-70 | **RGPD** : registre des traitements, base légale, DPA sous-traitants, politique de conservation, droits des personnes, notification sous 72 h | **P0** | Bloquant pour tout client européen ou bailleur UE |
| SEC-71 | DPO désigné (ou externalisé) | P1 | |
| SEC-72 | **Loi congolaise sur la protection des données et le numérique** | P0 | ⚠️ Cadre à faire vérifier par un juriste local — il évolue |
| SEC-73 | Analyse d'impact (AIPD) sur le module de signalement citoyen | **P1** | Traitement à risque pour les personnes |
| SEC-74 | ISO 27001 | P2 | 12-18 mois, 50-80 k€. Déclencheur : premier grand compte ou bailleur qui l'exige |
| SEC-75 | SOC 2 Type II | P3 | Utile surtout sur le marché nord-américain |
| SEC-76 | Résidence des données configurable par client | P1 | ⭐ Argument souveraineté |
| SEC-77 | Conditions d'utilisation limitant la responsabilité sur l'usage des alertes | **P0** | ⚠️ **Protection juridique essentielle** (R3) |
| SEC-78 | Politique d'usage acceptable interdisant les usages de surveillance des personnes | P1 | Position éthique **et** protection de la marque |

---

## 5. Une question éthique à trancher explicitement

Un système capable de détecter des campements, des constructions et des mouvements de
population dans des zones forestières est, techniquement, **un système de surveillance du
territoire — et potentiellement des personnes qui y vivent.**

Au Bassin du Congo, les forêts sont habitées : communautés locales et peuples autochtones,
dont les droits fonciers sont souvent non formalisés. Un outil qui signale une « occupation
illégale » peut servir la protection de la forêt comme l'expulsion de ses habitants.

Ce n'est pas une considération théorique : c'est un **risque commercial et réputationnel
concret**. Les bailleurs (CAFI, Banque mondiale, UE) appliquent des sauvegardes sociales
strictes, et un incident de ce type disqualifierait durablement le produit.

**À intégrer au cahier des charges, pas en annexe :**

| Mesure | Justification |
|---|---|
| Politique d'usage acceptable contractuelle | Interdit explicitement l'usage contre les communautés |
| Résolution volontairement dégradée sur les zones d'habitat communautaire | Détecter le défrichement industriel n'exige pas d'identifier des personnes |
| Consentement libre, préalable et éclairé pour toute donnée communautaire | Standard des sauvegardes des bailleurs |
| Comité d'éthique consultatif incluant des représentants de communautés | Crédibilité auprès des bailleurs et de la société civile |
| Traçabilité des usages : qui a consulté quelle zone et pourquoi | L'audit protège aussi contre le détournement interne |
| Refus documenté de certains cas d'usage | Se donner le droit de dire non a une valeur commerciale de long terme |

Traiter ce sujet en amont, publiquement, est un **avantage concurrentiel** face à des
fournisseurs américains ou européens qui ne l'aborderont pas.

---

*Suite : [`06-business-roadmap.md`](06-business-roadmap.md)*
