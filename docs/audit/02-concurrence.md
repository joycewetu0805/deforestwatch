# 02 — Analyse concurrentielle et positionnement

> ⚠️ **Note de fiabilité.** Ce chapitre s'appuie sur la connaissance publique du secteur.
> Le paysage bouge vite (rachats, fin de programmes de financement, calendrier
> réglementaire du RDUE). **Les faits datés doivent être revérifiés avant tout usage
> dans un document investisseur ou une réponse à appel d'offres.** Les points concernés
> sont signalés par ⚠️.

---

## 1. Cartographie du marché

Le marché ne se comporte pas comme un marché unique. Il faut distinguer **cinq couches**,
car les concurrents n'occupent pas les mêmes et ne se battent donc pas entre eux :

```
┌─────────────────────────────────────────────────────────────────────┐
│  5. DÉCISION & PREUVE      procédure, verbalisation, audit,         │  ← quasi vide
│                            conformité, transaction carbone          │     ★ VOTRE PLACE
├─────────────────────────────────────────────────────────────────────┤
│  4. APPLICATION MÉTIER     alertes, tâches, workflow, mobile,       │  GFW Pro, Satelligence
│                            rapports, terrain                        │  MapBiomas Alerta
├─────────────────────────────────────────────────────────────────────┤
│  3. ANALYTIQUE             classification, changement, biomasse,    │  Satelligence, Planet
│                            prédiction                               │  Descartes, Orbital
├─────────────────────────────────────────────────────────────────────┤
│  2. PLATEFORME DE CALCUL   accès, traitement distribué, API         │  GEE, CDSE, AWS, Planet
├─────────────────────────────────────────────────────────────────────┤
│  1. DONNÉE BRUTE           capteurs, constellations                 │  ESA, NASA, Planet, Airbus
└─────────────────────────────────────────────────────────────────────┘
```

**Le projet actuel se situe sur la couche 3, la plus encombrée et la moins défendable.**
La couche 5 — transformer une observation en acte opposable — est le seul étage où une
structure jeune, locale et spécialisée peut gagner. C'est aussi celui où la connaissance
du droit forestier congolais, des procédures de l'ICCN et des cahiers des charges
sociaux vaut plus qu'un budget R&D de 50 M$.

---

## 2. Benchmark détaillé

### 2.1 Global Forest Watch (WRI) — **le concurrent structurant**

| | |
|---|---|
| Modèle | Gratuit, financé par philanthropie et bailleurs. GFW Pro (chaînes d'approvisionnement) également gratuit. |
| Données | Hansen/UMD Global Forest Change (perte annuelle, 30 m), alertes GLAD-L/GLAD-S2, RADD (radar Sentinel-1, Wageningen), VIIRS/MODIS feux, couches de concessions, aires protégées, tourbières. |
| Outils | Interface web, Map Builder, Forest Watcher (mobile, **hors-ligne**), API ouverte, abonnements d'alertes e-mail. |

**Ce qu'ils font mieux — sans discussion possible :**
- Couverture pantropicale complète, mise à jour continue, gratuite, depuis 2014
- Alertes RADD **radar, 10 m, quasi hebdomadaires** — ce que votre B6 prétend faire et ne fait pas
- Autorité scientifique (UMD, Wageningen), méthodes publiées et évaluées par les pairs
- Forest Watcher : app mobile hors-ligne déjà déployée auprès de rangers en Afrique
- Notoriété absolue : tout ministère, ONG et bailleur du secteur connaît GFW

**Ce qu'ils font moins bien — vos ouvertures :**
- **Aucune prédiction.** GFW décrit le passé ; personne n'y anticipe.
- Aucun workflow opérationnel : pas d'attribution de tâche, pas de suivi d'intervention, pas de clôture de dossier, pas de chaîne de preuve
- Aucune personnalisation profonde par organisation (règles métier, seuils par concession, hiérarchie d'escalade)
- Pas d'intégration aux systèmes d'information nationaux (cadastre forestier, permis, redevances)
- Latence : les alertes GLAD sont rapides, mais Hansen (l'indicateur de référence) est **annuel et publié avec des mois de décalage**
- Générique : optimisé Amazonie/Indonésie, moins ajusté aux forêts marécageuses et mosaïques agricoles du Bassin du Congo
- Aucun engagement de service, aucun support, aucune responsabilité contractuelle — **un État ne peut pas fonder une procédure juridique sur un outil sans SLA ni responsable**

**À reprendre absolument :** le modèle Forest Watcher (mobile hors-ligne pour rangers) ·
l'intégration des couches de concessions · la logique d'abonnement à une zone d'intérêt ·
la publication ouverte des méthodes.

> **Erreur stratégique à éviter :** se positionner « contre » GFW. La bonne posture est
> **complémentaire** : consommer les alertes GLAD/RADD via leur API, et vendre ce que GFW
> ne fera jamais — la vérification, la procédure et la preuve. Cela réduit aussi
> massivement votre coût de R&D initial.

---

### 2.2 MapBiomas — **le meilleur modèle à copier**

| | |
|---|---|
| Origine | Brésil, réseau d'ONG, universités et entreprises technologiques. Décliné vers d'autres biomes et pays. ⚠️ Vérifier l'état d'avancement d'une déclinaison africaine. |
| Approche | Classification annuelle de l'usage des sols sur toute la série Landsat, **code entièrement ouvert**, exécuté sur Google Earth Engine. |
| MapBiomas Alerta | **La brique la plus intéressante pour vous** : chaque alerte de déforestation est **validée** avec de l'imagerie haute résolution, recoupée avec les couches foncières et administratives, et produit un **rapport standardisé exploitable par les autorités**. |

**Ce qu'ils font mieux :**
- Transparence méthodologique totale — c'est ce qui leur donne leur légitimité politique
- **La validation d'alerte comme produit** : ils ne vendent pas une détection, ils livrent un dossier
- Construction en réseau : chaque biome a ses experts locaux, ce qui évite le colonialisme méthodologique
- Ancrage institutionnel : leurs chiffres sont repris dans le débat public brésilien

**Ce qu'ils font moins bien :**
- Ce n'est pas un SaaS : pas de comptes, pas de rôles, pas de SLA, pas de facturation
- Pas de prédiction
- Dépendance forte à GEE
- Modèle non réplicable commercialement en l'état (financé par la philanthropie)

**À reprendre :** ⭐ **le workflow de validation d'alerte avec production automatique d'un
dossier standardisé.** C'est, de tout ce benchmark, l'idée la plus directement
transposable et la plus monétisable en Afrique centrale.

---

### 2.3 SERVIR (NASA / partenaires) — **partenaire potentiel, pas concurrent**

Programme de coopération scientifique avec des hubs régionaux, orienté renforcement de
capacités et co-développement d'outils avec les institutions locales.

⚠️ **Attention majeure :** le démantèlement de l'USAID en 2025 a bouleversé le
financement de nombreux programmes de coopération, dont SERVIR faisait partie. **L'état
actuel du programme doit impérativement être vérifié.** Cela crée deux effets opposés :
- **Un risque de marché** : les budgets d'assistance technique se contractent
- **Une opportunité** : un vide de service que des acteurs privés locaux peuvent occuper,
  avec des institutions africaines habituées à ces outils et soudain sans fournisseur

**Ce qu'ils font mieux :** légitimité institutionnelle, méthodologie, réseau, formation.
**Ce qu'ils font moins bien :** pas de produit continu, pas de SLA, dépendance politique
au bailleur — précisément la faiblesse qui vient de se matérialiser.

**Posture recommandée :** partenariat, pas confrontation. Un consortium avec un hub
régional est une porte d'entrée sur les appels d'offres.

---

### 2.4 Google Earth Engine — **fournisseur et risque, pas concurrent**

**Mieux :** archive planétaire pré-indexée, calcul distribué gratuit pour la recherche,
éditeur de code, écosystème énorme, Dynamic World (couverture du sol quasi temps réel).

**Moins bien :** ce n'est **pas un produit** — pas d'utilisateurs, pas de rôles, pas
d'alertes, pas de SLA, il faut savoir coder ; les Apps sont lentes et peu personnalisables ;
et surtout ⚠️ **l'usage commercial est payant et soumis à conditions**.

> **🔴 Décision d'architecture à prendre dans les 3 mois.** Tout le projet dépend
> aujourd'hui de GEE. Trois options :
> | Option | Avantages | Inconvénients |
> |---|---|---|
> | **Rester sur GEE commercial** | Rapidité, archive prête, coût de dev minimal | Coût variable non maîtrisé, dépendance totale, difficile à justifier en souveraineté |
> | **Copernicus Data Space / openEO** | Gratuit, européen, souverain, aligné RDUE, bon argument en appel d'offres UE | Sentinel uniquement, écosystème moins mature, plus de travail d'ingénierie |
> | **Pile propre** (S3 + STAC + COG + Dask/Kubernetes) | Contrôle total, coût prévisible, actif technique valorisable | 6-9 mois d'ingénierie, compétences rares |
>
> **Recommandation : GEE pour le prototypage → migration vers CDSE/openEO comme socle de
> production, avec une couche d'abstraction dès maintenant** (vous savez déjà faire :
> c'est exactement le pattern `DataSource`). Le stockage et le service de tuiles doivent
> être à vous dès le départ.

---

### 2.5 Copernicus / ESA — **votre socle de données**

**Mieux :** Sentinel-1 (radar, ~6-12 j, traverse les nuages — **décisif en zone
équatoriale**), Sentinel-2 (10-20 m, ~5 j), gratuit et ouvert, garanti sur le long terme,
politiquement neutre, aligné sur la réglementation européenne.

**Moins bien :** données brutes, aucune analytique, ergonomie d'accès perfectible,
volumétrie considérable à gérer soi-même.

**Sentinel-1 est votre meilleur atout technique inexploité.** Le Mai-Ndombe est couvert
de nuages une grande partie de l'année. RADD (GFW) a prouvé que le radar fonctionne en
détection de perte forestière tropicale. **Votre module radar actuel étant factice
(B6/D2), c'est le premier vrai développement scientifique à mener.**

---

### 2.6 Planet Labs

**Mieux :** PlanetScope quasi quotidien à 3-5 m — sans équivalent pour la **vérification**
d'une alerte ; SkySat en tasking submétrique ; basemaps mensuels sans nuages ; produits
dérivés forêt/carbone ; API mature.

⚠️ Le programme NICFI (financé par la Norvège) a longtemps donné un accès gratuit aux
mosaïques tropicales pour l'usage non commercial ; **son statut actuel doit être vérifié**
— il a connu des évolutions majeures récemment.

**Moins bien :** coût élevé et par surface (incompatible avec un abonnement à bas prix
pour un ministère africain) ; 4-8 bandes seulement (moins riche que Sentinel-2 sur le
SWIR, crucial pour la végétation) ; optique donc bloqué par les nuages ; pas d'application
métier ; pas de présence locale en Afrique centrale.

**À reprendre :** l'idée du **basemap mensuel sans nuages** comme fond de référence
visuel — c'est ce qui rend une interface crédible auprès d'un non-spécialiste.

**Usage recommandé :** ne pas acheter de couverture systématique. Acheter **à la demande,
sur les seules alertes à vérifier**. Une vérification ciblée sur 25 km² coûte quelques
dizaines d'euros et se refacture 10 à 50× dans un dossier de preuve. C'est un modèle de
marge, pas un coût.

---

### 2.7 Satelligence — **le concurrent le plus dangereux**

Société néerlandaise spécialisée dans la surveillance de la déforestation pour les
**chaînes d'approvisionnement de commodités** (huile de palme, cacao, soja, caoutchouc),
fortement positionnée sur la conformité RDUE.

**Mieux :** produit commercial mature et rentable ; combinaison radar + optique ;
positionnement RDUE clair ; clients grands comptes (négociants, agro-industrie) ;
crédibilité européenne.

**Moins bien :** ils servent **l'acheteur européen**, pas le producteur africain ; peu
d'ancrage local, pas de langue locale, pas de présence terrain ; centrés commodités
agricoles, moins sur le bois d'œuvre et le minier ; prix inaccessibles à une
administration africaine ; ne touchent ni au régalien ni au carbone juridictionnel.

> **L'asymétrie à exploiter.** Le RDUE impose la conformité à l'importateur européen,
> mais **la charge de la preuve retombe sur le producteur** : géolocalisation des
> parcelles, démonstration d'absence de déforestation après la date de référence,
> traçabilité. Un exportateur de bois ou de cacao du Bassin du Congo doit produire ce
> dossier et **personne ne le sert aujourd'hui à un prix accessible**.
> **C'est votre marché privé le plus immédiatement monétisable.**
>
> ⚠️ Le calendrier d'application du RDUE a été reporté à plusieurs reprises et fait
> l'objet de propositions de simplification. **Vérifier impérativement l'état du texte et
> les échéances en vigueur** avant d'en faire un pilier de votre discours commercial —
> et ne pas y adosser plus de 40 % du plan (R10).

---

### 2.8 Airbus OneAtlas

**Mieux :** très haute résolution (Pléiades / Pléiades Neo, jusqu'à ~30 cm), tasking
programmable, API, archive profonde, crédibilité souveraine européenne, présence
commerciale en Afrique.

**Moins bien :** très cher, orienté défense/renseignement, pas d'application forêt,
délais de tasking, pas de service analytique clé en main.

**Usage recommandé :** fournisseur ponctuel pour la **preuve juridique irréfutable**.
Une image à 30 cm datée montrant un camp d'orpaillage ou une scierie clandestine est une
pièce à conviction. C'est un poste de coût direct à refacturer.

---

### 2.9 Orbital Insight / Descartes Labs — **le contre-exemple**

⚠️ Ces deux sociétés, longtemps citées comme références de l'analytique géospatiale, ont
connu des changements de propriétaire ou de stratégie ces dernières années. **Vérifier
leur statut actuel avant de les citer.**

**Ce qu'ils font mieux :** ingénierie de très haut niveau, traitement à l'échelle
planétaire, ML sophistiqué.

**Ce qu'ils font moins bien — et c'est la leçon la plus importante de ce benchmark :**
tous deux ont bâti une **plateforme horizontale** (« l'analytique géospatiale pour
tous ») sans posséder un marché vertical. Résultat : cycles de vente longs, coûts
d'infrastructure massifs, difficulté à trouver un usage récurrent, et sorties bien en
deçà des capitaux levés.

> **Leçon à retenir :** ne construisez pas une plateforme. Construisez **une solution à
> un problème précis, pour un acheteur nommé, avec un budget identifié.** Le brief
> initial de ce projet — qui liste toutes les fonctionnalités imaginables — décrit
> exactement le chemin qui a mené ces sociétés à la difficulté.

---

## 3. Tableau comparatif de synthèse

Légende : ●●● fort · ●● moyen · ● faible · ○ absent

| Critère | **Vous (aujourd'hui)** | GFW | MapBiomas | Planet | Satelligence | Airbus | GEE |
|---|---|---|---|---|---|---|---|
| Couverture Bassin du Congo | ● (1 zone) | ●●● | ○ | ●●● | ●● | ●●● | ●●● |
| Résolution effective | ● (195 m) | ●●● (10-30 m) | ●● (30 m) | ●●● (3 m) | ●●● | ●●● (0,3 m) | ●●● |
| Fréquence | ● (annuelle) | ●●● (hebdo) | ●● | ●●● (quot.) | ●●● | ●● | ●●● |
| Radar / anti-nuages | ○ (factice) | ●●● (RADD) | ○ | ○ | ●●● | ● | ●●● |
| Prédiction | ● (heuristique) | ○ | ○ | ● | ●● | ○ | ○ |
| Workflow opérationnel | ○ | ● | ●● | ○ | ●● | ○ | ○ |
| **Chaîne de preuve juridique** | ○ | ○ | ●● | ○ | ● | ○ | ○ |
| Mobile hors-ligne | ○ | ●● | ○ | ○ | ○ | ○ | ○ |
| API / SDK | ● | ●● | ● | ●●● | ●● | ●● | ●●● |
| Multi-tenant / SaaS | ○ | ● | ○ | ●●● | ●●● | ●● | ● |
| Sécurité & conformité | ○ | ●● | ● | ●●● | ●●● | ●●● | ●●● |
| Ancrage local Afrique centrale | ●● | ● | ○ | ● | ● | ● | ○ |
| Langue française / locale | ●●● | ●● | ○ | ● | ● | ●● | ● |
| Prix accessible | ●●● | ●●● (gratuit) | ●●● | ● | ● | ● | ●● |
| Support & SLA | ○ | ● | ○ | ●●● | ●●● | ●●● | ●● |

**Lecture honnête :** vous êtes derrière sur toutes les colonnes techniques. Vous êtes
devant, ou seul, sur **trois** : ancrage local, langue, et le fait que **la colonne
« chaîne de preuve juridique » est vide pour presque tout le monde**.

Ces trois colonnes suffisent — à condition de ne pas gaspiller le budget à combler les
autres.

---

## 4. Innovations différenciantes proposées

Classées par défendabilité. Les ⭐ sont celles qui construisent une barrière à l'entrée.

| # | Innovation | Pourquoi c'est défendable |
|---|---|---|
| **I1** ⭐ | **Chaîne de preuve numérique.** Chaque alerte devient un dossier horodaté, signé cryptographiquement, versionné, ancré (hash sur registre public), avec traçabilité complète : imagerie source, méthode, version du modèle, validateur humain, décision, suite donnée. Export en pièce recevable. | Personne ne le fait. Nécessite du droit local, pas du capital. Crée un effet de verrouillage : une administration ne change pas de système d'archivage probant. |
| **I2** ⭐ | **Terrain hors-ligne bidirectionnel.** Tuiles pré-téléchargées, formulaires signés hors-ligne, GPS + photo horodatée + hash, synchronisation différée avec résolution de conflits, fonctionnement sur Android bas de gamme. | La contrainte réseau en province RDC est structurelle. Un acteur d'Amsterdam ou de Washington ne concevra jamais pour cette contrainte en priorité. |
| **I3** ⭐ | **Boucle terrain → modèle.** Chaque vérification de terrain devient une étiquette de vérité. Au bout de 2-3 ans, vous possédez **le seul jeu de vérité terrain dense du Bassin du Congo**. | 🏆 **C'est votre unique barrière à l'entrée durable.** Les images sont gratuites pour tous ; la vérité terrain congolaise ne l'est pour personne. À prioriser au-dessus de tout développement algorithmique. |
| **I4** | **Détection multi-pression, pas seulement forêt.** Orpaillage artisanal (turbidité de l'eau + bassins de décantation), routes clandestines, campements, scieries mobiles, brûlis. | Le vrai besoin des ministères RDC/Cameroun/Gabon est le contrôle du territoire, pas la statistique forestière. |
| **I5** | **Risque socio-économique explicable.** Croiser accessibilité (routes, fleuves), démographie, prix des commodités, concessions, titres miniers — avec SHAP pour expliquer chaque zone à risque. | L'explicabilité est une exigence d'achat public, pas un gadget. « Pourquoi cette zone ? » doit avoir une réponse. |
| **I6** | **Conformité RDUE côté producteur.** Génération du dossier de diligence raisonnée pour l'exportateur africain : géolocalisation parcellaire, historique de couverture, attestation datée. | Marché privé solvable, urgent, non servi (⚠️ sous réserve du calendrier). |
| **I7** | **Souveraineté des données.** Déploiement possible sur infrastructure nationale, hébergement sous contrôle de l'État, chiffrement client. | Argument décisif face à des fournisseurs américains, dans un contexte de sensibilité croissante à la souveraineté numérique. |
| **I8** | **MRV carbone auditable.** Chaîne complète et traçable, alignée sur les exigences des standards, avec incertitude propagée. | Marché à forte valeur — mais **à n'aborder qu'après validation scientifique sérieuse** (R4). |
| **I9** | **Alertes multicanal adaptées au terrain.** SMS et WhatsApp d'abord (le canal réel des agents), avec accusé de réception et escalade. | Détail d'exécution qui décide de l'adoption. Les concurrents envoient des e-mails à des gens qui n'ont pas d'e-mail au bureau. |
| **I10** | **Interfaces en langues locales** (lingala, swahili, français simplifié). | Adoption terrain, et argument politique fort. |
| **I11** | **Jumeau numérique de concession.** Chaque concession devient un objet suivi : plan d'aménagement, coupes autorisées vs observées, redevances, obligations sociales. | Passe du produit « carte » au produit « système d'information métier » — d'un budget SIG à un budget régalien, dix fois supérieur. |
| **I12** | **Indice public de pression forestière.** Publication mensuelle gratuite d'un indice par province, repris par la presse. | Acquisition et légitimité à coût quasi nul. C'est la stratégie qui a fait MapBiomas. |

---

## 5. Positionnement retenu

> **DeforestWatch n'est pas un observatoire de la déforestation.
> C'est le système d'information qui transforme une observation satellite en
> décision traçable et en preuve opposable, pour les acteurs du Bassin du Congo.**

**Formulation commerciale courte :**
*« De l'alerte satellite au procès-verbal — en 72 heures. »*

**Segment prioritaire n° 1 (à choisir maintenant, cf. README § 6) :**

| Segment | Budget | Cycle | Payeur | Recommandation |
|---|---|---|---|---|
| Administration forestière (ministère, ICCN) | Élevé | 12-18 mois | Bailleur puis État | 🥈 Cible de valeur, mais lente. À amorcer via un bailleur. |
| **Concessionnaire / exportateur RDUE** | Moyen | **3-6 mois** | Privé, immédiat | 🥇 **Cible n° 1.** Solvable, urgent, contractualisable vite. Finance le reste. |
| Projet carbone / REDD+ | Élevé | 6-12 mois | Privé | 🥉 À aborder après validation scientifique (R4). |
| ONG / conservation | Faible | 6-12 mois | Subvention | Utile en référence et en vérité terrain, peu en revenus. |
| Minier | Moyen-élevé | 6-12 mois | Privé | Opportuniste, marges élevées. |
| Recherche | Nul | — | — | Freemium, pour la légitimité uniquement. |

---

*Suite : [`03-fonctionnalites.md`](03-fonctionnalites.md)*
