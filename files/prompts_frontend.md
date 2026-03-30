# 🎨 PROMPTS FRONTEND — CongoForest Watch
## Surveillance de la Déforestation au Congo par Satellite & IA

> **Contexte pour chaque prompt** : Le projet est une plateforme Data Science de surveillance
> de la déforestation en RDC par imagerie satellite (Sentinel-2, Landsat) avec des modèles
> ML (Random Forest, CNN/U-Net). Stack : Python, Streamlit, FastAPI, PostgreSQL/Supabase,
> Google Earth Engine. Le frontend doit être de niveau professionnel, inspiré de Global Forest
> Watch (Vizzuality), des dashboards satellites Palantir, et du design géospatial moderne.

---

## PROMPT 1 — Landing Page / Page d'accueil

```
Crée une landing page React (JSX unique, Tailwind CSS) pour "CongoForest Watch" — une
plateforme de surveillance de la déforestation en République Démocratique du Congo par
imagerie satellite et intelligence artificielle.

DESIGN DIRECTION :
- Style : Dark mode dominant (#0A0F1C fond principal), accents vert émeraude (#10B981)
  et cyan satellite (#06B6D4). Inspiration : mélange entre Global Forest Watch et
  l'esthétique Palantir/mission control
- Hero section : fond avec une vraie texture de canopy forestière vue du ciel (simulée
  en CSS avec des gradients organiques verts sur fond sombre), titre "CongoForest Watch"
  en fonte sans-serif bold avec un effet de glow vert subtil
- Sous-titre : "Surveillance en temps réel de la déforestation au Bassin du Congo par
  imagerie satellite et intelligence artificielle"
- 4 KPI cards animées en dessous (glass morphism, backdrop-blur) :
  • "2.4M ha" — Surface surveillée
  • "47,230 ha" — Perte forestière détectée (2024)
  • "12" — Alertes actives cette semaine
  • "94.7%" — Précision du modèle CNN
- Les chiffres doivent avoir un effet de compteur animé (count-up) au scroll
- Section "Comment ça marche" : 3 étapes visuelles avec icônes (Lucide) —
  1. Acquisition satellite (icône satellite)
  2. Analyse IA (icône brain/cpu)
  3. Alertes & Décisions (icône bell/alert)
- Chaque étape reliée par une ligne animée style "data flow" (pointillés qui se déplacent)
- CTA button "Explorer la carte" avec effet hover glow vert
- Footer minimaliste avec crédits : Sentinel-2/ESA, Landsat/NASA, UPC/FASI

TECHNIQUE :
- React fonctionnel avec hooks (useState, useEffect, useRef)
- Tailwind uniquement pour le styling, pas de CSS externe
- Animations via CSS transitions et keyframes inline
- Responsive : mobile-first
- Aucune dépendance externe sauf lucide-react
- Le composant doit être exporté par défaut
```

---

## PROMPT 2 — Dashboard principal (carte interactive)

```
Crée un dashboard React (JSX unique, Tailwind CSS) pour "CongoForest Watch" —
la vue principale de monitoring avec carte interactive.

LAYOUT (inspiré de Global Forest Watch + mission control satellite) :
- Dark theme (#0B1120 fond, #1E293B panneaux, accents #10B981 vert et #EF4444 rouge alerte)
- Layout full-screen en 3 zones :

  1. SIDEBAR GAUCHE (w-80, collapsible) :
     - Logo "CFW" minimaliste en haut
     - Sélecteur de province RDC (dropdown stylisé : Équateur, Mai-Ndombe, Tshopo, etc.)
     - Slider temporel : année (2015-2024) avec labels
     - Toggle layers : "Couvert forestier", "Perte annuelle", "Alertes GLAD", "NDVI"
       (chaque toggle avec pastille de couleur correspondante)
     - Section "Filtre ML" : seuil de confiance du modèle (slider 0-100%)
     - Bouton "Lancer l'analyse" avec icône play, style néon vert

  2. ZONE CARTE CENTRALE (flex-1) :
     - Simuler une carte satellite dark (fond #1a1a2e avec des formes géométriques
       vertes représentant la canopée, des zones rouges pour la déforestation)
     - Overlay : grille hexagonale subtile style "scan satellite"
     - En haut de la carte : barre de coordonnées (lat, lon, zoom) style terminal
     - En bas : timeline scrubber horizontal (2015-2024) avec barres de perte forestière
       par année intégrées (mini bar chart dans le scrubber)
     - Marqueurs d'alerte : cercles rouges pulsants sur les zones de déforestation active

  3. PANNEAU DROIT (w-96, collapsible) :
     - Titre "Analyse en cours" avec indicateur live (point vert clignotant)
     - Mini graphique : évolution de la perte forestière (line chart simple en SVG,
       vert -> rouge gradient)
     - Card "Dernière détection" : date, coordonnées, surface estimée, confiance du modèle
     - Card "Répartition par cause" : donut chart simple (agriculture 45%, exploitation
       forestière 30%, feux 15%, autre 10%)
     - Liste "Alertes récentes" : 5 items avec pastille rouge, lieu, date, sévérité

INTERACTIONS :
- Les panneaux latéraux se collapse avec animation smooth
- Hover sur les alertes = highlight visuel
- Les sliders changent visuellement l'état (simulé)

TECHNIQUE :
- React avec hooks, Tailwind only, lucide-react pour les icônes
- Les graphiques doivent être en SVG pur (pas de lib externe)
- Responsive : sur mobile, les panneaux passent en bottom sheet
- Export default du composant
```

---

## PROMPT 3 — Page d'analyse ML / Résultats des modèles

```
Crée une page React (JSX unique, Tailwind) "Analyse & Modèles ML" pour CongoForest Watch.
Cette page présente les résultats de la comparaison des modèles de machine learning
utilisés pour détecter la déforestation.

DESIGN :
- Dark theme cohérent (#0B1120, #1E293B, accents #10B981/#06B6D4/#F59E0B)
- Header : "Performance des Modèles" + badge "Dernière évaluation : 15 Mars 2026"

SECTION 1 — Comparaison des modèles (3 colonnes) :
- 3 cards côte à côte, chacune représentant un modèle :
  • Random Forest : accuracy 89.2%, F1 0.87, icône arbres
  • XGBoost : accuracy 91.5%, F1 0.90, icône bolt/zap
  • U-Net (CNN) : accuracy 94.7%, F1 0.93, icône brain + badge "MEILLEUR"
- Chaque card : fond glass morphism, barre de progression circulaire (SVG) pour
  l'accuracy, métriques secondaires en dessous (précision, rappel, AUC)
- La card "MEILLEUR" a un border glow vert animé

SECTION 2 — Matrice de confusion interactive :
- Grille 2x2 stylisée (Forêt/Non-forêt prédits vs réels)
- Cellules avec couleurs : vrais positifs (vert), vrais négatifs (bleu foncé),
  faux positifs (orange), faux négatifs (rouge)
- Chiffres animés au scroll
- Tabs pour switcher entre les 3 modèles

SECTION 3 — Courbe d'apprentissage :
- Graphique SVG : Training loss vs Validation loss sur les epochs
- 2 lignes (vert pour train, cyan pour validation)
- Zone grisée entre les deux = overfitting zone
- Axes avec labels clairs

SECTION 4 — Importance des features :
- Bar chart horizontal SVG
- Features : NDVI, NDWI, EVI, Slope, Distance routes, Distance villages,
  Précipitations, Température, Bande B4, Bande B8
- Barres triées de la plus importante à la moins importante
- Couleur gradient vert -> gris

SECTION 5 — Échantillons visuels :
- Grille 2x3 de "cartes" simulées montrant :
  • Image satellite (carré avec texture verte/brune)
  • Masque prédit par le modèle (overlay rouge semi-transparent)
  • Label : "Vrai positif", "Faux négatif", etc.
- Style : bords arrondis, ombre subtile, label en badge

TECHNIQUE : React hooks, Tailwind, lucide-react, SVG pur pour tous les graphiques,
animations CSS, export default.
```

---

## PROMPT 4 — Dashboard Admin (gestion utilisateurs + monitoring)

```
Crée un dashboard administrateur React (JSX unique, Tailwind) pour CongoForest Watch.
C'est l'interface réservée aux admins pour gérer la plateforme.

DESIGN : Dark theme professionnel (#0F172A fond, #1E293B cards, accents #10B981 vert,
#3B82F6 bleu info, #EF4444 rouge danger)

LAYOUT — Navigation tabs en haut : "Vue d'ensemble" | "Utilisateurs" | "Pipeline ML" | "Logs"

TAB 1 — Vue d'ensemble (défaut) :
- 4 KPI cards en ligne :
  • Utilisateurs actifs (icône users) : 142
  • Analyses lancées (24h) : 37
  • Alertes générées : 12
  • Uptime API : 99.8%
- Graphique "Activité des 30 derniers jours" : bar chart SVG (analyses par jour)
- Graphique "Répartition géographique" : carte simplifiée RDC avec provinces
  colorées selon le nombre d'analyses (heatmap simple)
- Section "Derniers événements système" : table stylisée avec 5 lignes
  (timestamp, type, message, statut avec badge coloré)

TAB 2 — Utilisateurs :
- Barre de recherche + bouton "Ajouter utilisateur"
- Table stylisée dark avec colonnes : Avatar(initiales), Nom, Email, Rôle
  (badge "Admin" bleu / "Chercheur" vert / "Observateur" gris), Dernière connexion,
  Actions (edit/delete icons)
- Pagination en bas
- Formulaire modal pour ajouter/modifier un utilisateur (overlay avec backdrop blur)

TAB 3 — Pipeline ML :
- Statut des pipelines : 3 cards horizontales
  • "Collecte Sentinel-2" : statut vert "Actif", dernière exécution, prochaine planifiée
  • "Prétraitement NDVI" : statut jaune "En cours", barre de progression 67%
  • "Inférence U-Net" : statut gris "En attente"
- Timeline verticale des dernières exécutions (5 items) avec icônes de statut
- Bouton "Forcer l'exécution" avec confirmation

TAB 4 — Logs :
- Terminal-style : fond #0D1117, texte monospace vert (#10B981)
- Lignes de log avec timestamps, niveaux (INFO vert, WARN jaune, ERROR rouge)
- Filtre par niveau (toggles)
- Auto-scroll avec bouton "Pause"
- 15 lignes de logs simulées réalistes (connexions API, traitements d'images, etc.)

TECHNIQUE : React hooks (useState pour les tabs), Tailwind, lucide-react, pas de lib
externe, animations de transition entre tabs, export default.
```

---

## PROMPT 5 — Page de visualisation NDVI / Time-lapse satellite

```
Crée une page React (JSX unique, Tailwind) "Visualisation Satellite" pour CongoForest Watch.
Cette page permet de visualiser l'évolution du couvert forestier dans le temps.

DESIGN DIRECTION : Inspiré des interfaces NASA Worldview et Google Earth Engine —
cinématique, immersif, data-dense mais lisible.

HERO SECTION :
- Plein écran, fond très sombre (#050A15)
- Au centre : un grand carré (500x400px) représentant une zone satellite
  simulée avec un canvas ou SVG. La zone montre une grille de pixels
  colorés (vert foncé = forêt dense, vert clair = forêt dégradée,
  brun/beige = sol nu, bleu = eau)
- Contrôles de lecture en dessous : ◀ ⏸ ▶ + slider année (2015-2024)
- Quand on clique play, les pixels changent progressivement (le vert se
  transforme en brun sur les bords = simulation de déforestation progressive)
- Vitesse de lecture : boutons x1, x2, x5
- Badge en haut à gauche de l'image : "Province : Équateur — Zone : Mbandaka"
- Badge en haut à droite : année courante en gros caractères

PANNEAU INFÉRIEUR :
- 3 métriques qui évoluent en temps réel avec l'animation :
  • Couvert forestier : "87.3%" -> diminue (barre de progression verte)
  • Surface déboisée : "12,450 ha" -> augmente (texte rouge)
  • NDVI moyen : "0.72" -> diminue (jauge circulaire SVG)
- Mini line chart SVG montrant l'évolution du NDVI sur la période

PANNEAU LATÉRAL DROIT :
- Légende des couleurs (forêt, dégradé, sol nu, eau)
- Sélecteur d'indice : NDVI | EVI | NDWI (radio buttons stylisés)
- Sélecteur de bande spectrale : "Couleur naturelle" | "Fausse couleur" |
  "Infrarouge" (chaque option change la palette de couleurs de la grille)
- Info tooltip : explication de chaque indice

EXPÉRIENCE :
- L'animation doit être fluide (requestAnimationFrame ou setInterval)
- L'effet visuel doit donner l'impression de regarder une vraie image satellite
  qui se dégrade avec le temps
- Transition douce entre les années

TECHNIQUE : React, Tailwind, lucide-react, SVG/Canvas pour la simulation,
animations JS, export default.
```

---

## PROMPT 6 — Page Alertes & Notifications

```
Crée une page React (JSX unique, Tailwind) "Centre d'Alertes" pour CongoForest Watch.
Cette page affiche les alertes de déforestation détectées par le modèle ML.

DESIGN : Dark theme, urgence maîtrisée — inspiré des centres de commande (NASA, NORAD)
Palette : #0B1120 fond, rouge (#EF4444) pour les alertes critiques,
orange (#F59E0B) pour les warnings, vert (#10B981) pour les résolutions

HEADER :
- Titre "Centre d'Alertes" + compteur animé "12 alertes actives" avec point
  rouge pulsant
- Filtres en ligne : Sévérité (Critique/Haute/Moyenne), Province (dropdown),
  Période (7j/30j/90j), Statut (Active/Résolue/Ignorée)

SECTION PRINCIPALE — Liste d'alertes :
- Cards empilées verticalement, chaque alerte contient :
  • Bande latérale gauche colorée selon sévérité (rouge/orange/jaune)
  • Titre : "Déforestation détectée — Secteur Mbandaka Nord"
  • Sous-titre : coordonnées GPS, surface estimée, confiance du modèle
  • Mini carte : carré 80x80px avec point rouge sur fond vert foncé (simulé)
  • Timestamp : "Il y a 2 heures"
  • Tags : "Agriculture sur brûlis", "Zone protégée"
  • Actions : "Voir détails" | "Marquer résolu" | "Exporter"
  • Au hover : légère élévation + glow de la couleur de sévérité

- 8 alertes simulées avec des données réalistes (noms de lieux réels de la RDC :
  Mbandaka, Kisangani, Bumba, Lisala, Inongo, Boende, Basankusu, Gemena)

PANNEAU DROIT (sticky) :
- Graphique "Alertes par semaine" (12 semaines) : bar chart SVG vertical,
  barres empilées par sévérité
- Card "Résumé" : total alertes, % résolues, temps moyen de résolution
- Card "Zones les plus touchées" : top 5 localités avec mini barres horizontales
- Bouton "Générer rapport PDF"

DÉTAIL ALERTE (modal, s'ouvre au clic "Voir détails") :
- Overlay dark avec card centrale large
- Image satellite simulée (grand carré vert avec zone rouge)
- Avant/Après : deux carrés côte à côte (2023 = tout vert, 2024 = zone rouge)
- Métriques détaillées : surface, périmètre, cause probable, date de détection,
  date de confirmation
- Historique : mini timeline 3 points (Détecté -> Vérifié -> En attente d'action)
- Boutons : "Télécharger image" | "Envoyer au ministère" | "Fermer"

TECHNIQUE : React hooks, Tailwind, lucide-react, SVG pur, animations CSS,
modal avec portail React, export default.
```

---

## PROMPT 7 — Page de connexion / Authentification

```
Crée une page de connexion React (JSX unique, Tailwind) pour CongoForest Watch.

DESIGN : Immersif, cinématique — l'écran de login doit donner l'impression
d'accéder à un centre de commandement satellite.

LAYOUT FULL SCREEN :
- Fond : gradient radial très sombre (#030712 centre -> #0A1628 bords)
- Effet de particules subtil en arrière-plan : petits points verts/cyan qui
  flottent lentement (simuler des "données satellite" qui transitent) —
  implémenté avec un canvas ou des divs positionnées avec animation CSS
- Au centre : card de login (max-w-md) en glass morphism
  (bg-white/5 backdrop-blur-xl border border-white/10)

CONTENU DE LA CARD :
- Logo : "CFW" en lettres stylisées + "CongoForest Watch" en dessous
- Tagline : "Accès sécurisé à la plateforme de surveillance"
- Champ Email : input dark avec icône mail, border qui glow en vert au focus
- Champ Mot de passe : input dark avec icône lock, toggle visibilité
- Checkbox "Se souvenir de moi"
- Bouton "Se connecter" : pleine largeur, fond gradient vert (#059669 -> #10B981),
  effet hover avec glow, effet de loading quand cliqué (spinner pendant 2sec
  puis message "Bienvenue")
- Séparateur "ou"
- Bouton secondaire "Connexion avec Google" (outline, icône Google)
- Lien "Mot de passe oublié ?"
- En bas de la card : "Accès réservé aux chercheurs et administrateurs autorisés"

DÉTAILS UX :
- Au clic sur "Se connecter" : le bouton montre un spinner, puis après 2 secondes,
  la card entière fait une animation de scale + fade out comme si on "entre"
  dans la plateforme
- Les inputs ont des labels flottants (label qui monte au focus)
- Validation visuelle : bordure rouge si email invalide
- Le fond de particules ne doit pas distraire mais donner de la profondeur

AMBIANCE : Comme si tu te connectais au système de surveillance de la NASA.
Professionnel, sécurisé, futuriste mais pas gadget.

TECHNIQUE : React hooks (useState pour form state, loading, validation),
Tailwind, lucide-react, animations CSS keyframes pour les particules et
transitions, export default.
```

---

## 📋 NOTES D'UTILISATION

### Ordre recommandé de génération :
1. **Prompt 7** — Login (première impression)
2. **Prompt 1** — Landing page (vitrine du projet)
3. **Prompt 2** — Dashboard carte (cœur de l'app)
4. **Prompt 5** — Visualisation satellite (effet wow)
5. **Prompt 3** — Analyse ML (crédibilité technique)
6. **Prompt 6** — Alertes (utilité pratique)
7. **Prompt 4** — Admin (critère UPC obligatoire)

### Design System cohérent à maintenir :
| Token | Valeur | Usage |
|-------|--------|-------|
| `bg-primary` | `#0B1120` | Fond principal |
| `bg-surface` | `#1E293B` | Cards, panneaux |
| `bg-elevated` | `#334155` | Éléments surélevés |
| `accent-green` | `#10B981` | Actions positives, forêt |
| `accent-cyan` | `#06B6D4` | Données satellite, tech |
| `accent-red` | `#EF4444` | Alertes, déforestation |
| `accent-amber` | `#F59E0B` | Warnings, attention |
| `text-primary` | `#F1F5F9` | Texte principal |
| `text-secondary` | `#94A3B8` | Texte secondaire |
| `font-heading` | `Inter / system-ui` | Titres |
| `font-mono` | `JetBrains Mono` | Données, terminal |
| `glass` | `bg-white/5 backdrop-blur-xl` | Surfaces glass |
| `border` | `border-white/10` | Bordures subtiles |
| `glow-green` | `shadow-[0_0_30px_rgba(16,185,129,0.3)]` | Effet glow |

### Références visuelles du secteur :
- **Global Forest Watch** (globalforestwatch.org) — Standard de l'industrie pour la surveillance forestière
- **NASA Worldview** (worldview.earthdata.nasa.gov) — Interface satellite de référence
- **Vizzuality** (vizzuality.com) — Studio qui a designé GFW
- **Shakuro Satellite Dashboard** (Dribbble) — Esthétique mission control
- **Palantir Gotham** — Style operationnel dark, data-dense
- **Google Earth Engine** — Référence traitement satellite
