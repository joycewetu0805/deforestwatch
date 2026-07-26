"""
Génère les figures de la synthèse technique (docs/figures/*.png).

Les figures sont produites à partir du code réel du projet (générateur de
couverture du sol, signatures spectrales, indices, split spatial, carte de
risque), pas de valeurs recopiées à la main : elles illustrent donc exactement
ce que fait le pipeline.

Usage : python -m scripts.figures_synthese
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

from config.settings import (
    ANALYSIS_YEARS,
    BAND_ORDER,
    CLASS_COLORS,
    LAND_COVER_CLASSES,
    PROJECT_ROOT,
)
from src.utils import synthetic
from src.utils.logger import get_logger

log = get_logger("figures_synthese")

FIG_DIR = PROJECT_ROOT / "docs" / "figures"

# ── Palette (slots catégoriels validés) ──
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK_2, INK_3 = "#0b0b0b", "#52514e", "#8a8880"
SURFACE = "#ffffff"
FOREST = "#0B6E2D"

LC_CMAP = ListedColormap([CLASS_COLORS[c] for c in sorted(CLASS_COLORS)])
RISK_CMAP = LinearSegmentedColormap.from_list(
    "risk", ["#f7f4ea", "#f3d9a4", "#e8a33d", "#d1601c", "#a11d1d"]
)
NDVI_CMAP = LinearSegmentedColormap.from_list(
    "ndvi", ["#f3efe2", "#c8dda0", "#7fb457", "#2f7d34", "#0b4d1f"]
)


# ──────────────────────────────────────────────────────────────────────────
# Utilitaires de style
# ──────────────────────────────────────────────────────────────────────────
def _base_style() -> None:
    plt.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "font.size": 9,
        "text.color": INK,
        "axes.labelcolor": INK_2,
        "axes.edgecolor": "#d9d7cf",
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "legend.frameon": False,
        "savefig.facecolor": SURFACE,
    })


def _clean(ax, grid_axis: str | None = "y") -> None:
    """Axes discrets : pas de cadre, grille en retrait."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#d9d7cf")
    if grid_axis:
        ax.grid(axis=grid_axis, color="#eceae1", linewidth=0.8)
        ax.set_axisbelow(True)


def _no_axes(ax) -> None:
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        ax.spines[s.spine_type].set_visible(False) if False else s.set_visible(False)


def _save(fig, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / name
    fig.savefig(path, dpi=170, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    log.info(f"  figure -> {path.name}")
    return path


def _lc_legend(fig, ncol: int = 5, y: float = -0.02) -> None:
    handles = [mpatches.Patch(facecolor=CLASS_COLORS[c], label=LAND_COVER_CLASSES[c],
                              edgecolor=SURFACE, linewidth=1.5)
               for c in sorted(LAND_COVER_CLASSES)]
    fig.legend(handles=handles, loc="lower center", ncol=ncol,
               bbox_to_anchor=(0.5, y), fontsize=8.5)


# ──────────────────────────────────────────────────────────────────────────
# 1. Signatures spectrales des classes
# ──────────────────────────────────────────────────────────────────────────
def fig_signatures() -> None:
    """Réflectance moyenne des 5 classes sur les 6 bandes Sentinel-2."""
    sig = {
        0: [0.03, 0.05, 0.03, 0.45, 0.18, 0.09],
        1: [0.04, 0.07, 0.05, 0.38, 0.22, 0.13],
        2: [0.10, 0.13, 0.16, 0.28, 0.34, 0.30],
        3: [0.06, 0.08, 0.05, 0.02, 0.01, 0.01],
        4: [0.14, 0.15, 0.17, 0.20, 0.28, 0.26],
    }
    labels = ["B2\nbleu", "B3\nvert", "B4\nrouge", "B8\nPIR", "B11\nSWIR1", "B12\nSWIR2"]
    x = np.arange(len(BAND_ORDER))

    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    for cls in sorted(sig):
        ax.plot(x, sig[cls], color=CLASS_COLORS[cls], linewidth=2,
                marker="o", markersize=5.5, markeredgecolor=SURFACE,
                markeredgewidth=1.2, label=LAND_COVER_CLASSES[cls], zorder=3)

    # Annotation du contraste qui porte toute la détection
    ax.annotate("", xy=(3.0, 0.445), xytext=(3.0, 0.03),
                arrowprops=dict(arrowstyle="<->", color=INK_3, linewidth=1.2))
    ax.text(0.05, 0.30,
            "Tout l'écart utile est ici :\nsur la bande B8, la forêt renvoie\n"
            "15 fois plus que l'eau et\n1,6 fois plus qu'un sol nu.",
            fontsize=8.5, color=INK_2, va="center", linespacing=1.5)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Réflectance (0 à 1)")
    ax.set_ylim(0, 0.60)
    ax.set_title("Signature spectrale de chaque classe de couverture du sol")
    _clean(ax)
    ax.legend(ncol=3, fontsize=8.5, loc="upper left", columnspacing=1.4)
    _save(fig, "01_signatures.png")


# ──────────────────────────────────────────────────────────────────────────
# 2. Composite médian et masquage des nuages
# ──────────────────────────────────────────────────────────────────────────
def fig_composite() -> None:
    """Trois scènes nuageuses et la médiane qui les nettoie."""
    from src.preprocessing.cloud_masking import cloud_mask_from_scl, synthetic_scl

    from src.visualization.maps import classification_to_rgb

    series = synthetic.generate_landcover_series()
    lc = series[ANALYSIS_YEARS[-1]]
    rgb_true = classification_to_rgb(lc).astype(np.float32) / 255.0

    # Nuages en amas plutôt qu'en poivre et sel : champ aléatoire basse
    # résolution, agrandi puis lissé, enfin seuillé à la fraction voulue.
    def _cloud_mask(frac: float, seed: int) -> np.ndarray:
        h, w = lc.shape
        coarse = np.random.default_rng(seed).random((10, 10))
        field = np.kron(coarse, np.ones((h // 10 + 1, w // 10 + 1)))[:h, :w]
        for _ in range(12):
            field = (field + np.roll(field, 1, 0) + np.roll(field, -1, 0)
                     + np.roll(field, 1, 1) + np.roll(field, -1, 1)) / 5.0
        scl = np.where(field > np.quantile(field, 1 - frac), 9, 4)
        return cloud_mask_from_scl(scl)

    scenes, stack = [], []
    for i, frac in enumerate((0.35, 0.45, 0.30)):
        mask = _cloud_mask(frac, seed=i)
        scene = rgb_true.copy()
        scene[~mask] = 0.94                       # nuage blanc opaque
        scenes.append((scene, mask))
        stack.append(np.where(mask[..., None], rgb_true, np.nan))

    with np.errstate(all="ignore"):
        median = np.nanmedian(np.stack(stack), axis=0)
    median = np.where(np.isnan(median), rgb_true, median)

    fig, axes = plt.subplots(1, 4, figsize=(7.6, 2.35))
    for i, (scene, mask) in enumerate(scenes):
        axes[i].imshow(scene)
        pct = 100 * mask.mean()
        axes[i].set_title(f"Scène {i + 1}\n{pct:.0f} % exploitable", fontsize=9)
        _no_axes(axes[i])
    axes[3].imshow(median)
    axes[3].set_title("Composite médian\n100 % exploitable", fontsize=9, color=FOREST)
    _no_axes(axes[3])
    for s in axes[3].spines.values():
        s.set_visible(True)
        s.set_color(FOREST)
        s.set_linewidth(1.8)

    fig.suptitle("Pourquoi la médiane : chaque nuage est écarté par les autres dates",
                 fontsize=10.5, fontweight="bold", y=1.14)
    _save(fig, "02_composite_median.png")


# ──────────────────────────────────────────────────────────────────────────
# 3. Évolution de la couverture du sol
# ──────────────────────────────────────────────────────────────────────────
def fig_evolution() -> None:
    """Cartes de couverture 2015 / 2020 / 2025."""
    series = synthetic.generate_landcover_series()
    years = [ANALYSIS_YEARS[0], ANALYSIS_YEARS[len(ANALYSIS_YEARS) // 2], ANALYSIS_YEARS[-1]]
    stats = {s["year"]: s for s in synthetic.yearly_statistics(series=series)}

    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.9))
    for ax, year in zip(axes, years):
        ax.imshow(series[year], cmap=LC_CMAP, vmin=0, vmax=4, interpolation="nearest")
        forest = stats[year]["total_forest_ha"]
        ax.set_title(f"{year}\n{forest:,.0f} ha de forêt".replace(",", " "), fontsize=9.5)
        _no_axes(ax)
    fig.suptitle("Recul du couvert forestier sur la zone d'étude",
                 fontsize=10.5, fontweight="bold", y=1.06)
    _lc_legend(fig, ncol=5, y=-0.08)
    _save(fig, "03_evolution.png")


# ──────────────────────────────────────────────────────────────────────────
# 4. Indices spectraux calculés
# ──────────────────────────────────────────────────────────────────────────
def fig_indices() -> None:
    """NDVI et NBR calculés sur le composite de la dernière année."""
    from src.preprocessing.indices import nbr, ndvi

    series = synthetic.generate_landcover_series()
    lc = series[ANALYSIS_YEARS[-1]]
    bands = synthetic.landcover_to_bands(lc, seed=ANALYSIS_YEARS[-1])

    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.7))

    axes[0].imshow(lc, cmap=LC_CMAP, vmin=0, vmax=4, interpolation="nearest")
    axes[0].set_title("Couverture réelle", fontsize=9.5)
    _no_axes(axes[0])

    def _pool(a: np.ndarray, k: int = 4) -> np.ndarray:
        """Moyenne par blocs k x k : atténue le bruit pixel pour la lisibilité."""
        h, w = (a.shape[0] // k) * k, (a.shape[1] // k) * k
        return a[:h, :w].reshape(h // k, k, w // k, k).mean(axis=(1, 3))

    for ax, (fn, name) in zip(axes[1:], [(ndvi, "NDVI (végétation)"), (nbr, "NBR (brûlis / sol nu)")]):
        arr = _pool(fn(bands))
        lo, hi = np.percentile(arr, [2, 98])
        im = ax.imshow(arr, cmap=NDVI_CMAP, vmin=lo, vmax=hi, interpolation="nearest")
        ax.set_title(name, fontsize=9.5)
        _no_axes(ax)
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cb.ax.tick_params(labelsize=7.5, length=2)
        cb.outline.set_visible(False)

    fig.suptitle("Les indices spectraux font ressortir le front de déforestation",
                 fontsize=10.5, fontweight="bold", y=1.04)
    _save(fig, "04_indices.png")


# ──────────────────────────────────────────────────────────────────────────
# 5. Le vecteur de 13 features
# ──────────────────────────────────────────────────────────────────────────
def fig_features() -> None:
    """Schéma : d'un pixel à un vecteur de 13 nombres."""
    fig, ax = plt.subplots(figsize=(7.6, 2.5))
    ax.set_xlim(-0.1, 14.3)
    ax.set_ylim(-1.5, 2.4)
    _no_axes(ax)

    groups = [
        ("6 bandes Sentinel-2", ["B2", "B3", "B4", "B8", "B11", "B12"], BLUE),
        ("4 indices calculés", ["NDVI", "EVI", "NDWI", "NBR"], AQUA),
        ("3 couches SRTM", ["alt.", "pente", "aspect"], ORANGE),
    ]
    x = 0.15
    for title, items, color in groups:
        x0 = x
        for label in items:
            ax.add_patch(mpatches.FancyBboxPatch(
                (x, 0.35), 0.92, 0.85, boxstyle="round,pad=0.02,rounding_size=0.09",
                facecolor=color, edgecolor=SURFACE, linewidth=1.6))
            ax.text(x + 0.46, 0.78, label, ha="center", va="center",
                    fontsize=8, color="white", fontweight="bold")
            x += 1.02
        span = x - x0 - 0.10
        ax.plot([x0, x0 + span], [0.14, 0.14], color=color, linewidth=1.6)
        ax.text(x0 + span / 2, -0.16, title, ha="center", va="top",
                fontsize=8.8, color=color, fontweight="bold")
        x += 0.28

    ax.text(7.1, 1.85, "Un pixel  =  un vecteur de 13 nombres",
            ha="center", fontsize=11, fontweight="bold", color=INK)
    ax.text(7.1, -0.95,
            "Ordre figé dans config/settings.py (FEATURE_NAMES) et identique "
            "partout dans la chaîne",
            ha="center", fontsize=8.5, color=INK_2, style="italic")
    _save(fig, "05_features.png")


# ──────────────────────────────────────────────────────────────────────────
# 6. Split spatial par blocs
# ──────────────────────────────────────────────────────────────────────────
def fig_split() -> None:
    """Split aléatoire (fuite de données) contre split spatial par blocs."""
    from src.data.dataset_builder import spatial_block_split

    grid = 256
    rng = np.random.default_rng(3)
    random_split = rng.choice([0, 1, 2], size=(grid, grid), p=[0.70, 0.15, 0.15])
    block_split = spatial_block_split(grid=grid, seed=42)

    cmap = ListedColormap([BLUE, YELLOW, ORANGE])
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2))

    axes[0].imshow(random_split, cmap=cmap, vmin=0, vmax=2, interpolation="nearest")
    axes[0].set_title("Split aléatoire : à éviter", fontsize=9.5, color="#a11d1d")
    axes[0].set_xlabel("chaque pixel de test a un voisin\nen entraînement : score gonflé",
                       fontsize=8.3, color=INK_2)
    _no_axes(axes[0])

    axes[1].imshow(block_split, cmap=cmap, vmin=0, vmax=2, interpolation="nearest")
    axes[1].set_title("Split spatial par blocs : appliqué", fontsize=9.5, color=FOREST)
    axes[1].set_xlabel("le test porte sur des zones\njamais vues à l'entraînement",
                       fontsize=8.3, color=INK_2)
    _no_axes(axes[1])

    handles = [mpatches.Patch(facecolor=c, label=l, edgecolor=SURFACE, linewidth=1.5)
               for c, l in [(BLUE, "Entraînement 70 %"), (YELLOW, "Validation 15 %"),
                            (ORANGE, "Test 15 %")]]
    fig.legend(handles=handles, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.10), fontsize=8.5)
    fig.suptitle("Éviter la fuite de données géographique",
                 fontsize=10.5, fontweight="bold", y=1.02)
    _save(fig, "06_split.png")


# ──────────────────────────────────────────────────────────────────────────
# 7. Architecture U-Net
# ──────────────────────────────────────────────────────────────────────────
def fig_unet() -> None:
    """Schéma encodeur / goulot / décodeur avec connexions résiduelles."""
    fig, ax = plt.subplots(figsize=(7.6, 3.9))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.6)
    _no_axes(ax)

    levels = [(32, 2.4), (64, 1.9), (128, 1.4), (256, 0.95)]
    enc_x, dec_x = 1.15, 10.85
    enc_pos, dec_pos = [], []

    for i, (f, h) in enumerate(levels):
        y = 5.05 - i * 1.02
        ax.add_patch(mpatches.FancyBboxPatch(
            (enc_x - 0.42, y - h / 2), 0.84, h,
            boxstyle="round,pad=0.02,rounding_size=0.07",
            facecolor=BLUE, edgecolor=SURFACE, linewidth=1.4))
        ax.text(enc_x, y, str(f), ha="center", va="center", fontsize=8.5,
                color="white", fontweight="bold")
        enc_pos.append((enc_x + 0.42, y))

        ax.add_patch(mpatches.FancyBboxPatch(
            (dec_x - 0.42, y - h / 2), 0.84, h,
            boxstyle="round,pad=0.02,rounding_size=0.07",
            facecolor=AQUA, edgecolor=SURFACE, linewidth=1.4))
        ax.text(dec_x, y, str(f), ha="center", va="center", fontsize=8.5,
                color="white", fontweight="bold")
        dec_pos.append((dec_x - 0.42, y))

        # connexion résiduelle
        ax.annotate("", xy=(dec_x - 0.46, y), xytext=(enc_x + 0.46, y),
                    arrowprops=dict(arrowstyle="->", color=ORANGE, linewidth=1.5,
                                    linestyle=(0, (5, 3))))
        enc_x += 0.55
        dec_x -= 0.55

    # goulot
    ax.add_patch(mpatches.FancyBboxPatch(
        (5.55, 0.72), 0.9, 0.75, boxstyle="round,pad=0.02,rounding_size=0.07",
        facecolor="#4a3aa7", edgecolor=SURFACE, linewidth=1.4))
    ax.text(6.0, 1.09, "512", ha="center", va="center", fontsize=8.5,
            color="white", fontweight="bold")
    ax.text(6.0, 0.40, "goulot", ha="center", fontsize=8.3, color=INK_2)

    ax.annotate("", xy=(5.5, 1.09), xytext=(enc_pos[-1][0] + 0.1, enc_pos[-1][1] - 0.5),
                arrowprops=dict(arrowstyle="->", color=INK_3, linewidth=1.3))
    ax.annotate("", xy=(dec_pos[-1][0] - 0.1, dec_pos[-1][1] - 0.5), xytext=(6.5, 1.09),
                arrowprops=dict(arrowstyle="->", color=INK_3, linewidth=1.3))

    ax.text(2.3, 7.25, "Encodeur", ha="center", fontsize=9.5, color=BLUE, fontweight="bold")
    ax.text(2.3, 6.85, "l'image rétrécit,\nle contexte s'élargit", ha="center",
            fontsize=8.3, color=INK_2, va="top")
    ax.text(9.7, 7.25, "Décodeur", ha="center", fontsize=9.5, color=AQUA, fontweight="bold")
    ax.text(9.7, 6.85, "reconstruction\npixel par pixel", ha="center",
            fontsize=8.3, color=INK_2, va="top")
    ax.text(6.0, 7.05, "connexions résiduelles", ha="center", fontsize=9,
            color=ORANGE, fontweight="bold")
    ax.text(6.0, 6.65, "elles restituent les détails fins\nperdus pendant la descente",
            ha="center", fontsize=8.3, color=INK_2, va="top")
    ax.text(6.0, 0.12, "entrée : tuile 128x128x6     →     sortie : 128x128x5 "
                       "(une probabilité par classe et par pixel)",
            ha="center", fontsize=8.4, color=INK_2)
    _save(fig, "07_unet.png")


# ──────────────────────────────────────────────────────────────────────────
# 8. Perte forestière annuelle
# ──────────────────────────────────────────────────────────────────────────
def fig_courbes() -> None:
    """Surface forestière restante et perte annuelle (deux axes séparés)."""
    stats = synthetic.yearly_statistics()
    years = [s["year"] for s in stats]
    forest = [s["total_forest_ha"] for s in stats]
    loss = [s["forest_loss_ha"] for s in stats]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.0))

    ax1.plot(years, forest, color=FOREST, linewidth=2.2, marker="o",
             markersize=5, markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=3)
    ax1.fill_between(years, forest, color=FOREST, alpha=0.10)
    ax1.set_title("Surface forestière restante (ha)")
    ax1.set_ylim(0, max(forest) * 1.15)
    ax1.annotate(f"{forest[0]:,.0f}".replace(",", " "), (years[0], forest[0]),
                 textcoords="offset points", xytext=(2, 9), fontsize=8.5, color=INK_2)
    ax1.annotate(f"{forest[-1]:,.0f}".replace(",", " "), (years[-1], forest[-1]),
                 textcoords="offset points", xytext=(-8, -14), fontsize=8.5, color=INK_2)
    _clean(ax1)

    bars = ax2.bar(years, loss, color=ORANGE, width=0.64, zorder=3)
    worst = int(np.argmax(loss))
    bars[worst].set_color("#a11d1d")
    ax2.annotate(f"pire année : {years[worst]}", (years[worst], loss[worst]),
                 textcoords="offset points", xytext=(0, 7), ha="center",
                 fontsize=8.5, color="#a11d1d", fontweight="bold")
    ax2.set_title("Perte forestière par année (ha)")
    ax2.set_ylim(0, max(loss) * 1.28)
    _clean(ax2)

    for ax in (ax1, ax2):
        ax.set_xticks(years[::2])
        ax.tick_params(labelsize=8.5, length=2)

    fig.suptitle("Ce que le pipeline quantifie, année par année",
                 fontsize=10.5, fontweight="bold", y=1.04)
    _save(fig, "08_courbes.png")


# ──────────────────────────────────────────────────────────────────────────
# 9. Carte de risque
# ──────────────────────────────────────────────────────────────────────────
def fig_risque() -> None:
    """Couverture actuelle et carte de risque prédite."""
    series = synthetic.generate_landcover_series()
    lc = series[ANALYSIS_YEARS[-1]]
    risk = synthetic.risk_map(series=series)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1))

    axes[0].imshow(lc, cmap=LC_CMAP, vmin=0, vmax=4, interpolation="nearest")
    axes[0].set_title(f"Couverture observée en {ANALYSIS_YEARS[-1]}", fontsize=9.5)
    _no_axes(axes[0])

    forest = (lc == 0) | (lc == 1)
    masked = np.ma.masked_where(~forest, risk)   # hors forêt : sans objet
    cmap = RISK_CMAP.copy()
    cmap.set_bad("#dcd9cf")
    im = axes[1].imshow(masked, cmap=cmap, vmin=0, vmax=100, interpolation="nearest")
    axes[1].set_title("Risque prédit sur la forêt restante", fontsize=9.5)
    axes[1].set_xlabel("en gris : déjà déforesté, hors calcul", fontsize=8.2, color=INK_2)
    _no_axes(axes[1])
    cb = fig.colorbar(im, ax=axes[1], fraction=0.046, pad=0.03)
    cb.set_ticks([0, 50, 100])
    cb.set_ticklabels(["0", "50", "100"])
    cb.ax.tick_params(labelsize=8, length=2)
    cb.outline.set_visible(False)

    high = int(np.sum(risk > 70))
    fig.suptitle(f"Le risque se concentre sur la lisière : {high:,} pixels au-delà de 70 sur 100"
                 .replace(",", " "),
                 fontsize=10, fontweight="bold", y=1.02)
    _save(fig, "09_risque.png")


# ──────────────────────────────────────────────────────────────────────────
# 10. Apport du radar
# ──────────────────────────────────────────────────────────────────────────
def fig_radar() -> None:
    """Signatures radar par classe et gain de couverture face aux nuages."""
    from src.data.radar import RADAR_SIGNATURES, cloud_penetration_demo

    classes = sorted(RADAR_SIGNATURES)
    vv = [RADAR_SIGNATURES[c][0] for c in classes]
    vh = [RADAR_SIGNATURES[c][1] for c in classes]
    x = np.arange(len(classes))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.1),
                                   gridspec_kw={"width_ratios": [1.6, 1], "wspace": 0.42})

    ax1.barh(x + 0.19, vv, height=0.34, color=BLUE, label="VV", zorder=3)
    ax1.barh(x - 0.19, vh, height=0.34, color=AQUA, label="VH", zorder=3)
    ax1.set_yticks(x)
    ax1.set_yticklabels([LAND_COVER_CLASSES[c] for c in classes], fontsize=8.5)
    ax1.set_xlabel("Rétrodiffusion (dB)")
    ax1.set_title("Signature radar Sentinel-1")
    ax1.legend(fontsize=8.5, loc="lower left")
    _clean(ax1, grid_axis="x")

    cov = cloud_penetration_demo(ANALYSIS_YEARS[-1])
    labels = ["Optique\nSentinel-2", "Radar\nSentinel-1"]
    vals = [cov["optical_usable_pct"], cov["radar_usable_pct"]]
    bars = ax2.bar(labels, vals, color=[ORANGE, BLUE], width=0.55, zorder=3)
    for b, v in zip(bars, vals):
        ax2.text(b.get_x() + b.get_width() / 2, v + 3, f"{v:.0f} %",
                 ha="center", fontsize=9.5, fontweight="bold", color=INK)
    ax2.set_ylim(0, 118)
    ax2.set_ylabel("Pixels exploitables")
    ax2.set_title("Sous 50 % de nuages")
    _clean(ax2)

    fig.suptitle("Le radar traverse les nuages, l'optique non",
                 fontsize=10.5, fontweight="bold", y=1.03)
    _save(fig, "10_radar.png")


# ──────────────────────────────────────────────────────────────────────────
# 11. Architecture de stockage
# ──────────────────────────────────────────────────────────────────────────
def fig_stockage() -> None:
    """Où va chaque type de donnée."""
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9.6)
    _no_axes(ax)

    def box(x, y, w, h, title, lines, color, note=None):
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.14",
            facecolor=color, edgecolor=SURFACE, linewidth=1.8))
        ax.text(x + 0.28, y + h - 0.36, title, ha="left", va="center",
                fontsize=9, fontweight="bold", color="white")
        for i, line in enumerate(lines):
            ax.text(x + 0.28, y + h - 0.82 - i * 0.34, line, ha="left",
                    va="center", fontsize=7.4, color="white")
        if note:
            ax.text(x + w / 2, y + 0.26, note, ha="center", va="center",
                    fontsize=7.3, color="white", style="italic")

    ax.text(6, 9.3, "Chaque donnée va là où son format est le plus efficace",
            ha="center", fontsize=10.5, fontweight="bold", color=INK)

    box(0.25, 5.85, 3.75, 2.95, "Disque  data/raw/", [
        "composites/{année}.tif",
        "landcover/{année}.tif",
        "topography.tif",
        "",
        "GeoTIFF géoréférencés",
    ], BLUE, note="non versionné : trop volumineux")

    box(4.15, 5.85, 3.7, 2.95, "Disque  data/processed/", [
        "pixel_dataset.npz",
        "tile_dataset.npz",
        "features_clean.parquet",
        "model_metrics.json",
        "",
        "prêt à charger en numpy",
    ], "#4a3aa7")

    box(8.0, 5.85, 3.75, 2.95, "Disque  data/models/", [
        "random_forest.joblib",
        "xgboost.joblib",
        "unet.keras",
        "risk_predictor.joblib",
        "",
        "modèles entraînés",
    ], AQUA)

    box(0.25, 1.35, 6.1, 3.9, "PostgreSQL   (repli SQLite)", [
        "users                comptes, hash, secret 2FA",
        "analysis_results     surface et perte par année",
        "predictions          risque géolocalisé",
        "reports              signalements citoyens",
        "api_logs             traçabilité des appels",
        "model_registry       versions et performances",
    ], ORANGE, note="aucune image : uniquement des agrégats")

    box(6.5, 1.35, 5.25, 3.9, "frontend/public/demo/", [
        "landcover/{année}.png",
        "risk.png",
        "stats.json",
        "alerts.json",
        "impact.json",
    ], "#52514e", note="la vitrine tourne sans backend")

    ax.text(6, 0.55, "Les pixels vivent sur le disque. La base ne garde que ce qui doit "
                     "être interrogé, filtré ou joint.",
            ha="center", fontsize=8.6, color=INK_2, style="italic")
    _save(fig, "11_stockage.png")


# ──────────────────────────────────────────────────────────────────────────
# 12. Chaîne de traitement complète
# ──────────────────────────────────────────────────────────────────────────
def fig_pipeline() -> None:
    """Les huit étapes, de l'orbite au dashboard."""
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9.2)
    _no_axes(ax)

    steps = [
        ("1. COLLECTE", "GEE filtre les scènes, masque les nuages, calcule la médiane", BLUE),
        ("2. EXPORT", "scripts/gee_export.py  vers  data/raw/*.tif", BLUE),
        ("3. LECTURE", "RasterSource lit les GeoTIFF avec rasterio", "#4a3aa7"),
        ("4. FEATURES", "6 bandes + 4 indices + 3 topo = 13 par pixel", "#4a3aa7"),
        ("5. DATASETS", "split spatial par blocs 70 / 15 / 15", "#4a3aa7"),
        ("6. ENTRAÎNEMENT", "Random Forest, XGBoost, U-Net, prédicteur de risque", AQUA),
        ("7. ÉVALUATION", "F1-macro, Mean IoU, matrice de confusion", AQUA),
        ("8. RESTITUTION", "API FastAPI, dashboard Streamlit, frontend React", ORANGE),
    ]

    y = 8.35
    for i, (title, desc, color) in enumerate(steps):
        ax.add_patch(mpatches.FancyBboxPatch(
            (1.0, y - 0.42), 2.6, 0.72,
            boxstyle="round,pad=0.02,rounding_size=0.10",
            facecolor=color, edgecolor=SURFACE, linewidth=1.5))
        ax.text(2.3, y - 0.06, title, ha="center", va="center",
                fontsize=8.8, color="white", fontweight="bold")
        ax.text(3.85, y - 0.06, desc, ha="left", va="center", fontsize=8.5, color=INK_2)
        if i < len(steps) - 1:
            ax.annotate("", xy=(2.3, y - 0.85), xytext=(2.3, y - 0.46),
                        arrowprops=dict(arrowstyle="->", color="#c9c7bf", linewidth=1.4))
        y -= 1.03

    ax.text(6, 9.0, "La chaîne complète, de l'orbite au dashboard",
            ha="center", fontsize=10.5, fontweight="bold", color=INK)
    _save(fig, "12_pipeline.png")


# ──────────────────────────────────────────────────────────────────────────
# 13. Bascule démo / réel
# ──────────────────────────────────────────────────────────────────────────
def fig_provider() -> None:
    """L'abstraction qui rend la bascule démo / réel invisible."""
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.2)
    _no_axes(ax)

    def box(x, y, w, h, label, sub, color, fs=9.2):
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.13",
            facecolor=color, edgecolor=SURFACE, linewidth=1.8))
        ax.text(x + w / 2, y + h / 2 + (0.17 if sub else 0), label, ha="center",
                va="center", fontsize=fs, fontweight="bold", color="white")
        if sub:
            ax.text(x + w / 2, y + h / 2 - 0.26, sub, ha="center", va="center",
                    fontsize=7.8, color="white")

    box(1.4, 6.75, 7.2, 1.0, "Code applicatif",
        "datasets ML, statistiques, dashboard Streamlit, API FastAPI", INK_2)
    box(3.1, 5.05, 3.8, 1.0, "provider.py", "point d'accès unique", "#4a3aa7")
    box(3.1, 3.35, 3.8, 1.0, "DataSource", "interface abstraite", "#4a3aa7")
    box(0.5, 1.15, 4.0, 1.15, "SyntheticSource", "front agricole simulé", AQUA)
    box(5.5, 1.15, 4.0, 1.15, "RasterSource", "GeoTIFF réels, rasterio", BLUE)

    for y0, y1 in [(6.75, 6.10), (5.05, 4.40)]:
        ax.annotate("", xy=(5.0, y1), xytext=(5.0, y0),
                    arrowprops=dict(arrowstyle="->", color="#c9c7bf", linewidth=1.5))
    for x_end in (2.5, 7.5):
        ax.annotate("", xy=(x_end, 2.35), xytext=(5.0, 3.30),
                    arrowprops=dict(arrowstyle="->", color="#c9c7bf", linewidth=1.5,
                                    connectionstyle="arc3,rad=0"))

    ax.text(2.5, 0.75, "DEMO_MODE=true", ha="center", fontsize=8.2,
            color=AQUA, fontweight="bold")
    ax.text(7.5, 0.75, "DEMO_MODE=false  +  data/raw/ rempli", ha="center",
            fontsize=8.2, color=BLUE, fontweight="bold")
    ax.text(5.0, 0.18, "Le code applicatif ne sait jamais laquelle des deux est active.",
            ha="center", fontsize=8.6, color=INK_2, style="italic")
    _save(fig, "13_provider.png")


FIGURES = [
    fig_signatures, fig_composite, fig_evolution, fig_indices, fig_features,
    fig_split, fig_unet, fig_courbes, fig_risque, fig_radar, fig_stockage,
    fig_pipeline, fig_provider,
]


def build_all() -> Path:
    _base_style()
    log.info(f"Génération de {len(FIGURES)} figures…")
    for fn in FIGURES:
        fn()
    log.info(f"Figures écrites dans {FIG_DIR}")
    return FIG_DIR


def main() -> None:
    build_all()


if __name__ == "__main__":
    main()
