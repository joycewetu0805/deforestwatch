# 06 — Business, go-to-market et roadmap

---

## 1. Transformer le logiciel en entreprise

### 1.1 Préalables juridiques — avant toute chose

| # | Action | Urgence | Pourquoi |
|---|---|---|---|
| J1 | **Clarifier par écrit la propriété intellectuelle avec l'Université Protestante au Congo** | 🔴 **Immédiat** | Un travail réalisé dans un cadre académique peut relever du règlement de PI de l'établissement. Un investisseur exigera une cession écrite et non ambiguë. **Tant que ce point n'est pas réglé, il n'y a rien à vendre.** |
| J2 | Créer la société (SARL RDC, et/ou holding France/Belgique/Estonie) | 🔴 | La double structure facilite la levée en euros et le contrat local |
| J3 | Déposer la marque (RDC, OAPI, UE) | 🟠 | « DeforestWatch » et « CongoForest Watch » sont peu distinctifs — envisager un nom déposable |
| J4 | Licence du code : propriétaire pour le produit, ouvert pour les méthodes | 🟠 | Le modèle MapBiomas : légitimité par la méthode, revenus par le produit |
| J5 | CGU/CGV limitant la responsabilité sur l'usage des alertes | 🔴 | Protection contre R3 |
| J6 | Contrats de cession de droits pour tout contributeur | 🟠 | Due diligence |
| J7 | Assurance responsabilité civile professionnelle | 🟠 | Exigée par les contrats institutionnels |

### 1.2 Modèles économiques

| Modèle | Description | Prix indicatif | Marge | Prio |
|---|---|---|---|---|
| **SaaS par abonnement** | Par organisation, par surface surveillée et par utilisateur | Voir § 1.3 | 70-85 % | 🥇 **P0 — cœur du modèle** |
| **Licence on-premise** | Déploiement souverain sur infrastructure de l'État | 80-250 k€ + 20 %/an de maintenance | 60-70 % | 🥈 P1 — indispensable pour les ministères |
| **API à l'usage** | Facturation à l'appel ou au km² analysé | 0,02-0,20 €/km² | 60-75 % | P1 |
| **Vérification à la demande** | Achat d'imagerie THR + analyse + dossier de preuve | 150-800 €/dossier | 40-60 % | 🥉 **P0 — génère du revenu dès le premier client** |
| **Conseil / études** | Diagnostic, cartographie de référence, méthodologie | 600-1 200 €/jour | 40-55 % | **P0** — finance les 18 premiers mois |
| **Formation & certification** | Agents forestiers, géomaticiens, ONG | 400-900 €/personne/session | 60-70 % | P1 — **très forte demande, très sous-servie en RDC** |
| **Maintenance & support** | 18-22 % de la licence/an | — | 70 % | P1 |
| **Appels d'offres bailleurs** | CAFI, Banque mondiale, UE, FAO, GIZ, AFD, BAD | 200 k€ – 3 M€ | 30-50 % | 🥇 **P0 — la plus grosse poche de financement du secteur** |
| **MRV carbone** | % de la valeur des crédits vérifiés, ou forfait | 0,5-2 % ou 30-120 k€/projet | 60-75 % | P2 — après validation scientifique |
| **Données agrégées / indices** | Indice de pression forestière vendu aux financiers | 10-50 k€/an | 90 % | P3 |
| **Marque blanche** | Pour un observatoire régional (OFAC, COMIFAC) | 100-300 k€ + royalties | 55-70 % | P2 |
| **Freemium chercheurs** | Gratuit, limité, avec citation obligatoire | 0 € | — | P1 — acquisition et légitimité |

> **Séquence de revenus recommandée.** Ne commencez pas par le SaaS : le cycle est trop
> long pour votre trésorerie. Commencez par **conseil + vérification à la demande +
> formation**, qui paient dès le mois 3 et vous mettent en contact direct avec les
> décideurs. Le SaaS se construit **avec** ces clients, pas avant eux.

### 1.3 Grille tarifaire proposée

| Plan | Cible | Surface | Fréquence | Utilisateurs | Prix/an |
|---|---|---|---|---|---|
| **Découverte** | Chercheurs, étudiants | 1 000 km² | Mensuelle | 2 | Gratuit |
| **Terrain** | ONG locale, coopérative | 10 000 km² | Hebdomadaire | 10 | 4 800 € |
| **Concession** | Exploitant forestier, RDUE | 50 000 km² | Hebdomadaire | 25 | 18 000 € |
| **Provincial** | Administration provinciale | 200 000 km² | 3 j | 100 | 55 000 € |
| **National** | Ministère, agence nationale | Illimité | Quotidien | Illimité | 150 000 – 400 000 € |
| **Souverain** | On-premise, données sous contrôle national | Illimité | Quotidien | Illimité | 250 000 € + 22 %/an |

Options facturées : vérification THR (150-800 €/dossier) · rapports certifiés
(300-1 500 €) · formation (400-900 €/pers.) · développement spécifique (700-1 000 €/j) ·
intégration SI national (30-120 k€).

> **Sur le pricing :** ne calez pas vos prix sur des logiciels européens, ni sur la
> capacité à payer perçue d'un ministère africain. Calez-les sur **le coût de l'alternative
> pour le client** : une mission de terrain de vérification coûte 2 000 à 8 000 € en
> transport fluvial, carburant, per diem et sécurité. Une vérification satellite à 400 €
> qui évite une mission inutile a un retour sur investissement immédiat et démontrable.
> **C'est votre argument de vente numéro un, et il est chiffrable devant le client.**

---

## 2. Go-to-market Afrique

### 2.1 Séquence géographique

| Phase | Pays | Pourquoi | Difficulté |
|---|---|---|---|
| **1** (0-18 m) | **RDC** | Marché domestique, réseau, langue, plus grande forêt d'Afrique, forte attention des bailleurs | Moyenne — mais l'ancrage local compense |
| **2** (18-36 m) | **Gabon, Congo-Brazzaville** | Francophones, gouvernance forestière plus structurée, budgets disponibles, forte volonté climatique affichée | **Faible — les marchés les plus accessibles** |
| **3** (24-42 m) | **Cameroun, RCA** | Marchés significatifs, mêmes institutions régionales (COMIFAC) | Moyenne à élevée (sécurité en RCA) |
| **4** (36-60 m) | **Côte d'Ivoire, Ghana, Liberia** | Enjeu cacao/RDUE très fort, bailleurs actifs | Moyenne |
| **5** (48-60 m) | **Madagascar, Mozambique, Indonésie, Amazonie** | Extension pantropicale | Élevée |

> **Contre-intuition utile :** le Gabon ou le Congo-Brazzaville seront probablement plus
> faciles à vendre que la RDC (marchés plus petits, administrations plus concentrées,
> budgets plus fiables). **Ne considérez pas la RDC comme automatiquement acquise parce
> qu'elle est votre pays.** Traitez-la comme un marché à conquérir, et servez-vous du
> Gabon comme référence si l'entrée y est plus rapide.

### 2.2 Canaux

| Canal | Effort | Délai | Recommandation |
|---|---|---|---|
| **Bailleurs** (CAFI, Banque mondiale, UE, AFD, GIZ, BAD, FAO) | Élevé | 9-18 mois | 🥇 **Le canal principal.** En Afrique centrale, c'est le bailleur qui paie, pas le ministère. Adressez le bailleur. |
| **Institutions régionales** (COMIFAC, OFAC, OSFAC, RIFFEAC) | Moyen | 6-12 mois | 🥇 Crédibilité et accès multi-pays en une relation |
| Ministères en direct | Élevé | 12-24 mois | 🥈 Long mais ancrage durable |
| **ONG internationales** (WWF, WCS, RFUK, Greenpeace) | Faible | 3-6 mois | 🥇 **Premiers clients rapides, excellentes références, apportent de la vérité terrain** |
| **Concessionnaires / exportateurs (RDUE)** | Moyen | **3-6 mois** | 🥇 **Le revenu privé le plus rapide** |
| Projets carbone (Mai-Ndombe, Wildlife Works, développeurs) | Moyen | 6-12 mois | 🥈 Forte valeur, après validation scientifique |
| Miniers | Moyen | 6-12 mois | 🥉 Marges élevées, sensibilité réputationnelle |
| Universités | Faible | 3-6 mois | Vérité terrain, stagiaires, publications, légitimité |
| Presse et publication d'indices | Faible | Continu | ⭐ Notoriété à coût quasi nul — stratégie MapBiomas |

### 2.3 Partenariats prioritaires

| Partenaire | Nature | Apport |
|---|---|---|
| **OSFAC (Kinshasa)** | Technique et institutionnel | Expertise télédétection locale, légitimité, réseau |
| **Université de Kinshasa / UPC** | Recherche | Vérité terrain, publications, viviers de recrutement |
| **ICCN** | Utilisateur pilote | Cas d'usage aires protégées, références |
| **Un opérateur télécom (Vodacom, Airtel, Orange RDC)** | Distribution | ⭐ SMS/USSD à coût réduit, données mobiles subventionnées pour les agents |
| **Un fournisseur d'imagerie THR** | Fournisseur | Tarif revendeur sur la vérification |
| **Un cabinet juridique congolais** | Conseil | Valeur probante des rapports en droit congolais |
| **Un intégrateur SIG local** | Distribution | Déploiement, formation, support de proximité |

---

## 3. Roadmap

### 3.1 Six mois — « Prouver que ça marche pour de vrai »

**Objectif unique : traiter de vraies images, sur une vraie zone, et le prouver.**

| Mois | Technique | Scientifique | Commercial |
|---|---|---|---|
| **0** | Sprint 0 : correctifs B1-B12 | Protocole de validation rédigé | J1 (PI université) 🔴 · J2 (société) |
| **1** | Pipeline Sentinel-2 réel : STAC, COG, masquage nuages | 500 points de vérité terrain photo-interprétés | 20 entretiens de découverte client |
| **2** | Pipeline Sentinel-1 réel + CuSum | Comparaison à Hansen/GLAD/RADD | 3 lettres d'intention |
| **3** | PostGIS + AOI utilisateur + carte interactive (MapLibre) | BFAST Monitor opérationnel | **Premier contrat de conseil signé** |
| **4** | Alertes réelles + SMS/WhatsApp + workflow de validation | Validation prospective 2015-2020 → 2021-2023 | Réponse au premier appel d'offres |
| **5** | Application mobile Android hors-ligne (v1) | 200 points de vérité terrain GPS | Pilote terrain avec une ONG |
| **6** | Rapport PDF de preuve + audit trail | **Préprint publié** | **Premier client SaaS payant** |

**Sortie :** 1 zone réelle traitée · précision mesurée et publiée · 1 client payant ·
2-3 lettres d'intention · un préprint. **Effort ~900 j/h, 280-380 k€.**

**Équipe minimale :** 1 ingénieur télédétection · 1 développeur back · 1 développeur
front/mobile · 1 data scientist (mi-temps) · vous (produit + commercial).

### 3.2 Un an — « Devenir un produit »

| Trimestre | Technique | Scientifique | Commercial |
|---|---|---|---|
| **T3** | Multi-tenant · RBAC · MFA réelle · API v1 + clés · facturation | Modèle de dégradation (NDFI) · incertitude conformale | 3 clients payants · dossier bailleur déposé |
| **T4** | Mobile v2 · rapports Word/Excel/PPT · webhooks · SDK Python | Siamese U-Net · apprentissage actif | 5 clients · 1 contrat public · 250-400 k€ ARR |

**Sortie :** produit multi-tenant en production · SLA 99,5 % · 5 clients · mobile déployé ·
un article soumis. **Cumul ~2 100 j/h, 750 k€-1,0 M€.** Équipe 8-12 personnes.

### 3.3 Trois ans — « Devenir la référence régionale »

| Année | Objectifs |
|---|---|
| **An 2** | Couverture nationale RDC · Gabon et Congo ouverts · ISO 27001 · plugin QGIS · MRV carbone · 15-25 clients · 1,0-1,8 M€ ARR |
| **An 3** | 4 pays · modèle de fondation affiné · biomasse GEDI · article publié · marque blanche OFAC · 30-50 clients · **2,5-4 M€ ARR** · équipe 25-35 |

Jalons structurants : le plus grand jeu de vérité terrain d'Afrique centrale (10 000+
points) · l'indice mensuel de pression forestière repris par la presse · l'intégration au
système national de surveillance des forêts d'au moins un pays (**effet de verrouillage
majeur**).

### 3.4 Cinq ans — « Standard du Bassin du Congo »

- **6-8 pays**, extension pantropicale amorcée
- Modèle de fondation propriétaire Bassin du Congo, éventuellement partiellement ouvert
- Apprentissage fédéré COMIFAC (souveraineté préservée, modèle mutualisé)
- Reconnaissance des rapports comme **pièce recevable** par au moins une juridiction
- **8-15 M€ ARR**, 80-120 personnes, rentabilité atteinte
- Options de sortie : acquisition par un acteur de l'observation de la Terre ou du
  carbone · fonds à impact · **ou indépendance rentable** — qui est, pour une entreprise
  d'infrastructure publique en Afrique, une trajectoire parfaitement défendable

---

## 4. Financement

| Étape | Montant | Source | Contrepartie |
|---|---|---|---|
| Amorçage | 50-150 k€ | Subventions innovation, concours, incubateurs climat, business angels | Faible dilution |
| **Non dilutif** ⭐ | 200-800 k€ | **CAFI, GCF, AFD Digital Africa, UE, Fonds pour l'environnement mondial** | Aucune dilution — **à privilégier absolument dans ce secteur** |
| Pré-amorçage | 300-800 k€ | Fonds tech africains, business angels | 10-18 % |
| Amorçage | 1,5-3 M€ | VC climat/impact européens et africains | 15-25 % |
| Série A | 6-12 M€ | VC internationaux | 15-22 % |
| Revenus | Continu | Conseil, formation, appels d'offres | **La meilleure source** |

> **Point clé de financement :** ce secteur est l'un des rares où le **financement non
> dilutif est abondant** (climat, forêt, Afrique, MRV). Cherchez agressivement de la
> subvention avant de chercher du capital. Chaque euro de subvention obtenu vaut trois
> à quatre euros de capital en valeur actionnariale conservée. Et un bailleur qui vous
> finance devient souvent un prescripteur auprès de vos clients.

---

## 5. Indicateurs de pilotage

| Catégorie | Indicateur | Cible an 1 | Cible an 3 |
|---|---|---|---|
| Produit | Utilisateurs actifs mensuels | 150 | 2 500 |
| Produit | Surface sous surveillance active | 100 000 km² | 2 M km² |
| Produit | Alertes traitées / semaine | 200 | 5 000 |
| **Qualité** | **Taux de confirmation terrain** | > 70 % | > 85 % |
| **Qualité** | **Délai détection → notification** | < 7 j | < 24 h |
| Qualité | Disponibilité | 99,5 % | 99,9 % |
| Business | ARR | 250-400 k€ | 2,5-4 M€ |
| Business | Rétention nette | > 100 % | > 115 % |
| Business | Ratio LTV/CAC | > 2 | > 3,5 |
| Business | Cycle de vente médian | 6 mois | 4 mois |
| Impact | Surface protégée grâce à une intervention | mesurée | 50 000 ha |
| Impact | Agents formés | 50 | 800 |
| Science | Points de vérité terrain accumulés | 2 000 | 15 000 ⭐ |
| Science | Publications | 1 préprint | 3 articles |

> **Les deux indicateurs qui comptent vraiment** sont le **taux de confirmation terrain**
> (votre précision réelle, celle qui décide si le client renouvelle) et le **volume de
> vérité terrain accumulée** (votre actif défendable). Tous les autres sont des
> conséquences.

---

*Suite : [`07-priorisation.md`](07-priorisation.md)*
