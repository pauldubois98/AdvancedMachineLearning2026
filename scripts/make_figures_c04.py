#!/usr/bin/env python3
"""Every figure of Course04 (clustering: k-means, hierarchical, DBSCAN, HDBSCAN).

One function per figure, registered under the stem the slide deck asks for.
All figures share one canvas (9 x 3.7075 in), which is exactly the content
area pandoc leaves under a slide title, so a figure never has to be resized.

    python3 scripts/make_figures_c04.py Course04/img [stem ...]
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from matplotlib.patches import (
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    Rectangle,
)

W, H, DPI = 9.0, 3.7075, 400

INK = "#1b1b1b"
MUTED = "#9aa0a6"
BLUE = "#2b6cb0"
GREEN = "#00ab0e"
RED = "#c53030"
PURPLE = "#6b46c1"
GOLD = "#b7791f"
AMBER = GOLD
LIGHT = "#edeef0"
GRID = "#cccfd2"

CYCLE = [BLUE, GREEN, RED, PURPLE, GOLD]
DENSITY_CMAP = LinearSegmentedColormap.from_list("density", [BLUE, GOLD, RED])


def _use_lato():
    for path in sorted(Path("/usr/share/fonts").rglob("Lato-*.ttf")):
        font_manager.fontManager.addfont(str(path))
    families = {f.name for f in font_manager.fontManager.ttflist}
    return "Lato" if "Lato" in families else "DejaVu Sans"


plt.rcParams.update(
    {
        "font.family": _use_lato(),
        "font.size": 12,
        "mathtext.fontset": "cm",
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "lines.linewidth": 2.2,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    }
)


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------
FIGURES = {}


def figure(name):
    def register(fn):
        FIGURES[name] = fn
        return fn

    return register


# --------------------------------------------------------------------------
# layout helpers
# --------------------------------------------------------------------------
def canvas(fig):
    """A blank axes measured in inches, for hand-laid-out figures."""
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    return ax


def panels(fig, n, titles=None, colors=None, **kw):
    """n plotting panels in a row, with the deck's coloured panel titles."""
    axes = fig.subplots(1, n, **kw)
    axes = np.atleast_1d(axes)
    for i, ax in enumerate(axes):
        if titles:
            ax.set_title(titles[i], color=(colors[i] if colors else INK), pad=10)
    return axes


def caption(ax, text, color=MUTED, size=11):
    """The grey line the example decks put under a panel."""
    ax.annotate(
        text,
        xy=(0.5, -0.26),
        xycoords="axes fraction",
        ha="center",
        va="top",
        color=color,
        fontsize=size,
    )


def box(
    ax,
    x,
    y,
    w,
    h,
    color,
    label,
    size=13,
    fill="white",
    lw=2.0,
    weight="normal",
    pad=0.06,
    va_label="center",
):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle=f"round,pad={pad},rounding_size=0.10",
            linewidth=lw,
            edgecolor=color,
            facecolor=fill,
            zorder=2,
        )
    )
    if label:
        ax.text(
            x + w / 2,
            y + h / 2,
            label,
            ha="center",
            va=va_label,
            color=color,
            fontsize=size,
            zorder=3,
            weight=weight,
        )


def arrow(ax, xy_from, xy_to, color=MUTED, lw=2.0, style="-|>", rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            xy_from,
            xy_to,
            arrowstyle=style,
            mutation_scale=14,
            linewidth=lw,
            color=color,
            shrinkA=2,
            shrinkB=2,
            zorder=1,
            connectionstyle=f"arc3,rad={rad}",
        )
    )


def column(
    ax,
    x,
    y,
    width,
    title,
    items,
    color,
    item_size=11.5,
    title_size=14,
    leading=0.30,
    bullet="—",
):
    """A titled list: coloured heading, then dashed items underneath."""
    ax.text(
        x,
        y,
        title,
        color=color,
        fontsize=title_size,
        weight="bold",
        ha="left",
        va="top",
    )
    yy = y - 0.42
    for item in items:
        ax.text(x, yy, bullet, color=color, fontsize=item_size, ha="left", va="top")
        ax.text(
            x + 0.22,
            yy,
            item,
            color=INK,
            fontsize=item_size,
            ha="left",
            va="top",
            wrap=True,
        )
        yy -= leading * (1 + item.count("\n"))
    return yy


def text_width(fig, ax, text, size):
    """Width of a piece of text, in inches — the canvas units of `canvas()`."""
    probe = ax.text(0, 0, text, fontsize=size)
    fig.canvas.draw()
    width = probe.get_window_extent(renderer=fig.canvas.get_renderer()).width
    probe.remove()
    return width / fig.dpi


def equation(ax, text, y=None, size=26, color=INK, x=None):
    ax.text(
        W / 2 if x is None else x,
        H * 0.58 if y is None else y,
        text,
        ha="center",
        va="center",
        fontsize=size,
        color=color,
    )


def note(ax, text, y=0.42, color=MUTED, size=13, x=None, ha="center"):
    ax.text(
        W / 2 if x is None else x,
        y,
        text,
        ha=ha,
        va="center",
        fontsize=size,
        color=color,
    )


def _round(v):
    """One decimal while it matters, none once the number is large."""
    return f"{v:.1f}" if v < 10 else f"{v:.0f}"


def _plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


def caption_row(fig, axes, texts, y=0.085, color=MUTED, size=11):
    """Captions pinned to the figure, so an equal-aspect panel cannot move them."""
    for ax, text in zip(np.atleast_1d(axes), texts):
        pos = ax.get_position(original=True)
        fig.text((pos.x0 + pos.x1) / 2, y, text, ha="center", va="top",
                 color=color, fontsize=size)


def despine(ax, keep=()):
    for side in ("top", "right", "left", "bottom"):
        if side not in keep:
            ax.spines[side].set_visible(False)


def blank(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    despine(ax)




# ==========================================================================
# shared data and drawing helpers
# ==========================================================================
CLUSTER_COLORS = (BLUE, RED, GREEN, PURPLE, GOLD, "#0f9b8e", "#b5179e")


def _blobs(rng, centres, spread=0.55, n=60):
    X = np.vstack([rng.normal(c, spread, (n, 2)) for c in centres])
    y = np.repeat(np.arange(len(centres)), n)
    return X, y


def _tree_data(seed=3, n=260, noise=40):
    """Two elongated arms and a blob, plus scattered noise: the running example."""
    rng = np.random.default_rng(seed)
    t = rng.uniform(0, 1, n // 2)
    arm1 = np.c_[-2.4 + 3.0 * t, 1.9 - 1.4 * t] + rng.normal(0, 0.18, (n // 2, 2))
    t = rng.uniform(0, 1, n // 2)
    arm2 = np.c_[-2.2 + 3.1 * t, -1.9 + 1.5 * t] + rng.normal(0, 0.18, (n // 2, 2))
    blob = rng.normal((2.6, 0.1), 0.42, (n // 3, 2))
    junk = rng.uniform(-3.6, 4.2, (noise, 2))
    junk[:, 1] = rng.uniform(-3.0, 3.0, noise)
    X = np.vstack([arm1, arm2, blob, junk])
    return X


def _shades(color, n):
    """n variations of one colour, light to dark — for sub-clusters."""
    base = np.array(to_rgb(color))
    return [tuple(base * f + (1 - f)) for f in np.linspace(0.55, 1.0, n)]


def _scatter_clusters(ax, X, labels, s=18, noise_color=MUTED):
    """Colour by cluster; label -1 (noise) stays grey and small."""
    for k in sorted(set(labels)):
        m = labels == k
        if k == -1:
            ax.scatter(X[m, 0], X[m, 1], s=s * 0.6, color=noise_color, alpha=0.55,
                       edgecolors="none", zorder=2)
        else:
            ax.scatter(X[m, 0], X[m, 1], s=s,
                       color=CLUSTER_COLORS[k % len(CLUSTER_COLORS)], alpha=0.85,
                       edgecolors="none", zorder=3)


def _bare(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


# ==========================================================================
# 1. what clustering is
# ==========================================================================
@figure("clustering_setting")
def clustering_setting(fig):
    rng = np.random.default_rng(1)
    X, y = _blobs(rng, [(-1.7, -1.0), (1.8, -0.6), (0.2, 1.9)], 0.62, 55)

    axes = panels(
        fig,
        2,
        titles=["given", "goal"],
        colors=[INK, GREEN],
        gridspec_kw=dict(left=0.05, right=0.62, top=0.84, bottom=0.18, wspace=0.14),
    )
    axes[0].scatter(X[:, 0], X[:, 1], s=16, color=INK, alpha=0.6, edgecolors="none")
    _scatter_clusters(axes[1], X, y, s=16)
    for ax in axes:
        ax.set_xlim(-4, 4)
        ax.set_ylim(-3, 3.6)
        _bare(ax)

    side = fig.add_axes([0.66, 0.16, 0.33, 0.70])
    side.axis("off")
    side.text(0.0, 0.78, "understand", color=BLUE, fontsize=12.5, va="center")
    side.text(0.0, 0.66, "biology, finance, text, web traffic", color=MUTED,
              fontsize=11, va="center", linespacing=1.6)
    side.text(0.0, 0.44, "use", color=GREEN, fontsize=12.5, va="center")
    side.text(0.0, 0.32, "the cluster becomes a feature",
              color=MUTED, fontsize=11, va="center", linespacing=1.6)


@figure("clustering_vs_dimred")
def clustering_vs_dimred(fig):
    rng = np.random.default_rng(4)
    axes = panels(
        fig,
        2,
        titles=["dimension reduction", "clustering"],
        colors=[BLUE, GREEN],
        gridspec_kw=dict(left=0.05, right=0.97, top=0.84, bottom=0.26, wspace=0.22),
    )
    ax = axes[0]
    ax.add_patch(Rectangle((0.10, 0.25), 0.26, 0.60, facecolor="#e9f0f8",
                           edgecolor=BLUE, lw=2, transform=ax.transAxes))
    ax.text(0.23, 0.90, r"$X \in \mathbb{R}^{N \times d}$", ha="center", color=BLUE,
            fontsize=13, transform=ax.transAxes)
    ax.add_patch(Rectangle((0.64, 0.25), 0.11, 0.60, facecolor="#e9f0f8",
                           edgecolor=BLUE, lw=2, transform=ax.transAxes))
    ax.text(0.70, 0.90, r"$Z \in \mathbb{R}^{N \times q}$", ha="center", color=BLUE,
            fontsize=13, transform=ax.transAxes)
    ax.annotate("", xy=(0.60, 0.55), xytext=(0.40, 0.55), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.2))
    ax.text(0.50, 0.62, r"$q < d$", ha="center", color=GREEN, fontsize=12,
            transform=ax.transAxes)
    ax.axis("off")

    ax = axes[1]
    X, y = _blobs(rng, [(-1.5, -0.9), (1.6, -0.6), (0.1, 1.6)], 0.46, 45)
    _scatter_clusters(ax, X, y, s=16)
    for k, centre in enumerate([(-1.5, -0.9), (1.6, -0.6), (0.1, 1.6)]):
        ax.text(centre[0], centre[1] + 1.05, f"$C_{k+1}$", ha="center",
                color=CLUSTER_COLORS[k], fontsize=13)
    ax.set_xlim(-3.4, 3.4)
    ax.set_ylim(-2.6, 3.2)
    _bare(ax)
    caption_row(fig, axes, ["fewer columns", "fewer rows"], y=0.16)


@figure("clustering_apps")
def clustering_apps(fig):
    ax = canvas(fig)
    rows = [
        (BLUE, "market segmentation", "purchase history", "segments to target"),
        (GREEN, "image segmentation", "pixels, voxels", "blood, muscle, tumour"),
        (PURPLE, "text mining", "e-mails, documents", "folders, themes"),
        (GOLD, "anomaly detection", "transactions, logs", "what fits nowhere"),
    ]
    ax.text(2.70, 3.45, "x", ha="left", va="center", color=MUTED, fontsize=11.5)
    ax.text(5.60, 3.45, r"$C_k$", ha="left", va="center", color=MUTED,
            fontsize=11.5)
    for i, (color, name, inputs, out) in enumerate(rows):
        y = 2.95 - i * 0.70
        ax.text(2.50, y, name, ha="right", va="center", color=color, fontsize=13,
                weight="bold")
        ax.text(2.70, y, inputs, ha="left", va="center", color=INK, fontsize=12)
        ax.text(5.10, y, "→", ha="center", va="center", color=MUTED, fontsize=12)
        ax.text(5.60, y, out, ha="left", va="center", color=INK, fontsize=12)
        if i:
            ax.plot([0.60, 8.40], [y + 0.35, y + 0.35], color=GRID, lw=0.9)
    note(ax, "the same algorithm, four very different ideas of what a group is",
         y=0.30)


@figure("cluster_types")
def cluster_types(fig):
    rng = np.random.default_rng(7)
    axes = fig.subplots(
        1, 3,
        gridspec_kw=dict(left=0.04, right=0.98, top=0.80, bottom=0.26, wspace=0.12),
    )
    X, y = _blobs(rng, [(-1.9, -1.1), (1.9, -0.9), (0.0, 1.9)], 0.42, 45)
    _scatter_clusters(axes[0], X, y, s=14)
    axes[0].set_title("well separated", color=BLUE, pad=10, fontsize=13)

    seeds = np.array([(-1.6, -0.8), (1.6, -0.6), (0.0, 1.6)])
    X, _ = _blobs(rng, seeds, 0.70, 55)
    nearest = ((X[:, None, :] - seeds[None]) ** 2).sum(-1).argmin(1)
    for k, centre in enumerate(seeds):
        members = X[nearest == k]
        colour = CLUSTER_COLORS[k]
        for px, py in members:
            axes[1].plot([centre[0], px], [centre[1], py], color=colour, lw=0.6,
                         alpha=0.30, zorder=1)
        axes[1].scatter(members[:, 0], members[:, 1], s=14, color=colour,
                        alpha=0.85, edgecolors="none", zorder=3)
        axes[1].plot(*centre, "X", color=colour, ms=15, mec="white", mew=1.6,
                     zorder=5)
    axes[1].set_title("prototype based", color=GREEN, pad=10, fontsize=13)

    from sklearn.datasets import make_moons

    Xm, ym = make_moons(220, noise=0.06, random_state=1)
    Xm = Xm * 2.2
    _scatter_clusters(axes[2], Xm, ym, s=14)
    axes[2].set_title("density based", color=PURPLE, pad=10, fontsize=13)
    for ax in axes:
        ax.set_aspect("equal")
        _bare(ax)
    caption_row(fig, axes, [
        "closer to each other than to anyone outside",
        "each point belongs to its nearest centre",
        "a dense region, whatever shape it takes",
    ], y=0.155)


def _contrast(fig, titles, colors):
    """The two-panel-plus-side-column layout of the 'A vs B' slides."""
    axes = panels(
        fig,
        2,
        titles=titles,
        colors=colors,
        gridspec_kw=dict(left=0.05, right=0.66, top=0.84, bottom=0.22, wspace=0.14),
    )
    side = fig.add_axes([0.70, 0.22, 0.28, 0.62])
    side.axis("off")
    return axes, side


def _side_pair(side, blocks, drop=0.14):
    """Two headed paragraphs in the side column, at the usual heights."""
    for (head, body, color), y in zip(blocks, (0.92, 0.52)):
        side.text(0.0, y, head, color=color, fontsize=12.5, weight="bold",
                  va="center")
        side.text(0.0, y - drop, body, color=MUTED, fontsize=11, va="center",
                  linespacing=1.6)


@figure("partitional_vs_hierarchical")
def partitional_vs_hierarchical(fig):
    rng = np.random.default_rng(2)
    groups = [((-1.7, -0.9), BLUE), ((1.8, -0.7), GREEN), ((0.1, 1.9), RED)]
    offsets = [(-0.62, -0.38), (0.62, -0.30), (0.02, 0.66)]

    axes = panels(
        fig,
        2,
        titles=["partitional", "hierarchical"],
        colors=[BLUE, GREEN],
        gridspec_kw=dict(left=0.05, right=0.66, top=0.84, bottom=0.22, wspace=0.14),
    )
    for gi, (centre, color) in enumerate(groups):
        shades = _shades(color, len(offsets))
        for si, off in enumerate(offsets):
            pts = rng.normal(np.array(centre) + np.array(off), 0.20, (26, 2))
            axes[0].scatter(pts[:, 0], pts[:, 1], s=15, color=color, alpha=0.85,
                            edgecolors="none")
            axes[1].scatter(pts[:, 0], pts[:, 1], s=15, color=shades[si],
                            edgecolors="none")
        axes[1].add_patch(Ellipse(np.array(centre) + np.array((0.02, 0.02)),
                                  2.5, 2.1, facecolor="none", edgecolor=color,
                                  lw=1.6, ls="--", alpha=0.7))
    for ax in axes:
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-2.6, 3.6)
        _bare(ax)
    caption(axes[0], "each point in exactly one subset")
    caption(axes[1], "and each subset splits again")

    side = fig.add_axes([0.70, 0.22, 0.28, 0.62])
    side.axis("off")
    side.text(0.0, 0.92, "partitional", color=BLUE, fontsize=12.5, weight="bold",
              va="center")
    side.text(0.0, 0.78, "one level, K fixed in advance", color=MUTED,
              fontsize=11, va="center", linespacing=1.6)
    side.text(0.0, 0.52, "hierarchical", color=GREEN, fontsize=12.5,
              weight="bold", va="center")
    side.text(0.0, 0.38, "nested groups",
              color=MUTED, fontsize=11, va="center", linespacing=1.6)


@figure("exclusive_vs_overlapping")
def exclusive_vs_overlapping(fig):
    rng = np.random.default_rng(11)
    centres = [(-0.95, 0.0), (0.95, 0.0)]
    X = np.vstack([rng.normal(c, 0.72, (70, 2)) for c in centres])
    d = np.array([np.linalg.norm(X - c, axis=1) for c in centres])
    hard = d.argmin(0)
    shared = np.abs(d[0] - d[1]) < 0.45

    axes, side = _contrast(fig, ["exclusive", "overlapping"], [BLUE, GREEN])
    for k in (0, 1):
        axes[0].scatter(X[hard == k, 0], X[hard == k, 1], s=16,
                        color=CLUSTER_COLORS[k], alpha=0.85, edgecolors="none")
    for k in (0, 1):
        m = (hard == k) & ~shared
        axes[1].scatter(X[m, 0], X[m, 1], s=16, color=CLUSTER_COLORS[k],
                        alpha=0.85, edgecolors="none")
    for x, y in X[shared]:
        axes[1].plot(x, y, marker="o", ms=8.5, color=CLUSTER_COLORS[0],
                     fillstyle="left", mec="none", zorder=4)
        axes[1].plot(x, y, marker="o", ms=8.5, color=CLUSTER_COLORS[1],
                     fillstyle="right", mec="none", zorder=4)
    for c in centres:
        axes[1].add_patch(Ellipse(c, 2.9, 2.4, facecolor="none", edgecolor=GRID,
                                  lw=1.6, ls="--"))
    axes[0].plot([0, 0], [-1.8, 2.0], color=GRID, lw=1.6, ls="--")
    for ax in axes:
        ax.set_xlim(-2.9, 2.9)
        ax.set_ylim(-1.9, 2.1)
        _bare(ax)
    caption(axes[0], "sharp border")
    caption(axes[1], "some points belong to both")
    _side_pair(side, [
        ("exclusive", "one point, one cluster", BLUE),
        ("overlapping", "a point may belong to\nseveral clusters", GREEN),
    ])


@figure("hard_vs_fuzzy")
def hard_vs_fuzzy(fig):
    rng = np.random.default_rng(13)
    centres = np.array([(-0.95, 0.0), (0.95, 0.0)])
    X = np.vstack([rng.normal(c, 0.72, (70, 2)) for c in centres])
    d = np.array([np.linalg.norm(X - c, axis=1) for c in centres])
    w = (1 / (d ** 2 + 1e-9))
    w = w / w.sum(0)

    axes, side = _contrast(fig, ["hard", "fuzzy"], [BLUE, GREEN])
    for k in (0, 1):
        m = d.argmin(0) == k
        axes[0].scatter(X[m, 0], X[m, 1], s=16, color=CLUSTER_COLORS[k],
                        alpha=0.85, edgecolors="none")
    mix = LinearSegmentedColormap.from_list("mix", [CLUSTER_COLORS[1],
                                                    CLUSTER_COLORS[0]])
    axes[1].scatter(X[:, 0], X[:, 1], s=16, c=w[0], cmap=mix, vmin=0, vmax=1,
                    edgecolors="none")
    pick = int(np.argmin(np.abs(w[0] - 0.62)))
    axes[1].annotate(rf"$w_1$ = {w[0, pick]:.2f},  $w_2$ = {w[1, pick]:.2f}",
                     xy=X[pick], xytext=(X[pick][0] - 0.25, 1.85), ha="center",
                     color=INK, fontsize=11,
                     arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.3))
    for ax in axes:
        ax.set_xlim(-2.9, 2.9)
        ax.set_ylim(-1.9, 2.3)
        _bare(ax)
    caption(axes[0], "single label")
    caption(axes[1], "weight per cluster (summing to one)")
    _side_pair(side, [
        ("hard", r"$x_i$ gets one label", BLUE),
        ("fuzzy", r"$x_i$ gets a weight $w_k \in [0, 1]$"
                  "\nfor every cluster,", GREEN),
    ], drop=0.18)
    side.text(0.0, 0.13, r"with $\sum_k w_k = 1$", color=MUTED, fontsize=11,
              va="center")


@figure("complete_vs_partial")
def complete_vs_partial(fig):
    rng = np.random.default_rng(17)
    X = np.vstack([rng.normal((-1.4, -0.5), 0.42, (55, 2)),
                   rng.normal((1.3, -0.3), 0.42, (55, 2)),
                   rng.normal((0.0, 1.5), 0.42, (55, 2)),
                   rng.uniform((-3.0, -2.0), (3.0, 2.8), (22, 2))])
    centres = np.array([(-1.4, -0.5), (1.3, -0.3), (0.0, 1.5)])
    d = np.array([np.linalg.norm(X - c, axis=1) for c in centres])
    full = d.argmin(0)
    partial = np.where(d.min(0) < 1.0, full, -1)

    axes, side = _contrast(fig, ["complete", "partial"], [BLUE, GREEN])
    _scatter_clusters(axes[0], X, full, s=15)
    _scatter_clusters(axes[1], X, partial, s=15)
    for ax in axes:
        ax.set_xlim(-3.4, 3.4)
        ax.set_ylim(-2.4, 3.2)
        _bare(ax)
    caption(axes[0], "every point gets a cluster")
    caption(axes[1], "some points are not assigned")
    _side_pair(side, [
        ("complete", "every point is assigned\n(whether it fits or not)", BLUE),
        ("partial", "points that fit nowhere stay\nunassigned", GREEN),
    ])


@figure("homogeneous_vs_heterogeneous")
def homogeneous_vs_heterogeneous(fig):
    rng = np.random.default_rng(19)
    same = np.vstack([rng.normal(c, 0.42, (55, 2)) for c in
                      [(-1.5, -0.6), (1.5, -0.6), (0.0, 1.6)]])
    y_same = np.repeat([0, 1, 2], 55)
    wide = rng.normal((-1.4, -0.3), 1.00, (80, 2))
    tight = rng.normal((1.7, 1.5), 0.17, (25, 2))
    long = rng.normal((0.0, 0.0), 0.28, (60, 2)) @ np.array([[2.0, 0.0],
                                                             [0.0, 0.45]])
    long = long + np.array([1.9, -1.4])
    other = np.vstack([wide, tight, long])
    y_other = np.concatenate([np.zeros(80), np.ones(25), 2 * np.ones(60)])

    axes, side = _contrast(fig, ["homogeneous", "heterogeneous"], [BLUE, GREEN])
    _scatter_clusters(axes[0], same, y_same, s=15)
    _scatter_clusters(axes[1], other, y_other.astype(int), s=15)
    for ax in axes:
        ax.set_xlim(-4.2, 4.2)
        ax.set_ylim(-2.8, 3.2)
        _bare(ax)
    caption(axes[0], "same size, same shape, same density")
    caption(axes[1], "differing size, shape, density")
    _side_pair(side, [
        ("homogeneous", "clusters that look alike", BLUE),
        ("heterogeneous", "sizes, shapes and densities\nthat differ", GREEN),
    ])


@figure("cluster_distinctions")
def cluster_distinctions(fig):
    ax = canvas(fig)
    rows = [
        (RED, "partitional", "hierarchical",
         "one level, or clusters inside clusters"),
        (BLUE, "exclusive", "overlapping",
         "one cluster per point, or several"),
        (GREEN, "hard", "fuzzy",
         r"a label, or a weight $w_k \in [0,1]$ with $\sum_k w_k = 1$"),
        (PURPLE, "complete", "partial",
         "everything is clustered, or some points are left out"),
        (GOLD, "homogeneous", "heterogeneous",
         "same size, shape and density — or not"),
    ]
    for i, (color, left, right, meaning) in enumerate(rows):
        y = 3.05 - i * 0.60
        ax.text(1.55, y, left, ha="right", va="center", color=color, fontsize=13)
        ax.text(1.75, y, "vs", ha="center", va="center", color=MUTED, fontsize=11)
        ax.text(1.95, y, right, ha="left", va="center", color=color, fontsize=13)
        ax.text(4.30, y, meaning, ha="left", va="center", color=INK, fontsize=12)
        if i:
            ax.plot([0.60, 8.50], [y + 0.30, y + 0.30], color=GRID, lw=0.9)
    # note(ax, "One particular method make assumptions on all the questions above.", y=0.25)


# ==========================================================================
# 2. distances
# ==========================================================================
@figure("eq_dissimilarity")
def eq_dissimilarity(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.50, r"$D : E \times E \to \mathbb{R}^{+}$", ha="center",
            va="center", color=MUTED, fontsize=13)
    column(ax, 0.60, 3.10, 3.8, "dissimilarity assumes", [
        r"$D(x, y) = D(y, x) \geq 0$",
        r"$D(x, x) = 0$",
    ], BLUE, item_size=13, title_size=13)
    column(ax, 4.95, 3.10, 3.9, "distance assumes", [
        r"$D(x, y) = 0 \Leftrightarrow x = y$",
        r"$D(x, y) \leq D(x, z) + D(z, y)$",
    ], GREEN, item_size=13, title_size=13)
    ax.plot([4.70, 4.70], [1.55, 3.20], color=GRID, lw=1.2)
    ax.text(W / 2, 1.25, "every clustering method reads the data through this function",
            ha="center", va="center", color=INK, fontsize=13)


@figure("distance_zoo")
def distance_zoo(fig):
    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.78, bottom=0.28, wspace=0.14),
    )
    theta = np.linspace(0, 2 * np.pi, 600)
    c, s = np.cos(theta), np.sin(theta)
    for ax, (q, name, formula, color) in zip(axes, (
        (1, "Manhattan", r"$q = 1$", GREEN),
        (2, "Euclidean", r"$q = 2$", BLUE),
        (6, "Chebyshev", r"$q \to \infty$", GOLD),
    )):
        radius = (np.abs(c) ** q + np.abs(s) ** q) ** (-1.0 / q)
        ax.plot(radius * c, radius * s, color=color, lw=2.6)
        ax.fill(radius * c, radius * s, color=color, alpha=0.10)
        ax.axhline(0, color=GRID, lw=1.0)
        ax.axvline(0, color=GRID, lw=1.0)
        ax.set_xlim(-1.6, 1.6)
        ax.set_ylim(-1.6, 1.6)
        ax.set_aspect("equal")
        _bare(ax)
        ax.set_title(f"{name}\n{formula}", color=color, pad=8, fontsize=12,
                     linespacing=1.8)
        caption(ax, "points at distance 1")

    ax = axes[3]
    rng = np.random.default_rng(3)
    cov = np.array([[1.0, 0.78], [0.78, 0.8]])
    X = rng.multivariate_normal([0, 0], cov, 200)
    ax.scatter(X[:, 0], X[:, 1], s=10, color=MUTED, alpha=0.5, edgecolors="none")
    vals, vecs = np.linalg.eigh(cov)
    angle = np.degrees(np.arctan2(*vecs[:, 1][::-1]))
    for scale in (1.0, 2.0):
        ax.add_patch(Ellipse((0, 0), *(2 * scale * np.sqrt(vals)), angle=angle,
                             facecolor="none", edgecolor=PURPLE, lw=2.2,
                             alpha=1.0 - 0.3 * (scale - 1)))
    ax.set_xlim(-3.4, 3.4)
    ax.set_ylim(-3.0, 3.0)
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title("Mahalanobis\n" r"$(x-y)^{T}\Sigma^{-1}(x-y)$", color=PURPLE,
                 pad=8, fontsize=12, linespacing=1.8)
    caption(ax, "the data sets the shape")


@figure("hamming_distance")
def hamming_distance(fig):
    ax = canvas(fig)
    a = list("GATTACAGTC")
    b = list("GACTACAGTG")
    diff = [i for i, (u, v) in enumerate(zip(a, b)) if u != v]

    x0, cell = 2.05, 0.46
    ax.text(x0 - 0.30, 2.78, r"$x$", ha="right", va="center", color=BLUE,
            fontsize=13)
    ax.text(x0 - 0.30, 2.24, r"$y$", ha="right", va="center", color=GREEN,
            fontsize=13)
    for j, (u, v) in enumerate(zip(a, b)):
        x = x0 + j * cell
        hit = j in diff
        if hit:
            ax.add_patch(Rectangle((x - cell / 2 + 0.03, 2.02), cell - 0.06, 0.98,
                                   facecolor=RED, alpha=0.10, edgecolor="none"))
        ax.text(x, 2.78, u, ha="center", va="center",
                color=RED if hit else BLUE, fontsize=14,
                weight="bold" if hit else "normal")
        ax.text(x, 2.24, v, ha="center", va="center",
                color=RED if hit else GREEN, fontsize=14,
                weight="bold" if hit else "normal")
        ax.text(x, 1.78, "1" if hit else "0", ha="center", va="center",
                color=RED if hit else MUTED, fontsize=11)
    ax.text(x0 - 0.30, 1.78, "differs?", ha="right", va="center", color=MUTED,
            fontsize=11)
    ax.text(x0 + 10 * cell + 0.25, 1.78, rf"$= {len(diff)}$", ha="left",
            va="center", color=RED, fontsize=13)

    ax.text(W / 2, 1.20, r"$d_H(x, y) = \sum_{j=1}^{d} "
                         r"\mathbb{1}\left[x_j \neq y_j\right]$",
            ha="center", va="center", color=INK, fontsize=18)
    ax.text(W / 2, 0.68, '"count the columns where two rows disagree"',
            ha="center", va="center", color=INK, fontsize=12)
    note(ax, "text, DNA, survey answers, one-hot features", y=0.28)


@figure("linkage_definitions")
def linkage_definitions(fig):
    rng = np.random.default_rng(11)
    A = rng.normal((-1.25, 0.25), 0.42, (14, 2))
    B = rng.normal((1.45, -0.25), 0.42, (14, 2))
    pairs = np.array([[np.linalg.norm(a - b) for b in B] for a in A])
    i_min, j_min = np.unravel_index(pairs.argmin(), pairs.shape)
    i_max, j_max = np.unravel_index(pairs.argmax(), pairs.shape)

    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.78, bottom=0.28, wspace=0.10),
    )
    titles = [
        (BLUE, "single / MIN", r"$\min_{x \in C_i,\, y \in C_j} D(x,y)$"),
        (RED, "complete / MAX", r"$\max_{x \in C_i,\, y \in C_j} D(x,y)$"),
        (GREEN, "average", r"$\frac{1}{n_i n_j}\sum\sum D(x,y)$"),
        (PURPLE, "centroid", r"$D(m_i,\, m_j)$"),
    ]
    for k, (ax, (color, name, formula)) in enumerate(zip(axes, titles)):
        ax.scatter(A[:, 0], A[:, 1], s=16, color=INK, alpha=0.55,
                   edgecolors="none")
        ax.scatter(B[:, 0], B[:, 1], s=16, color=INK, alpha=0.55,
                   edgecolors="none")
        if k == 0:
            ax.plot(*zip(A[i_min], B[j_min]), color=color, lw=2.4)
        elif k == 1:
            ax.plot(*zip(A[i_max], B[j_max]), color=color, lw=2.4)
        elif k == 2:
            for a in A[::3]:
                for b in B[::3]:
                    ax.plot(*zip(a, b), color=color, lw=0.6, alpha=0.35)
        else:
            ax.plot(*zip(A.mean(0), B.mean(0)), color=color, lw=2.4)
            ax.plot(*A.mean(0), "X", color=color, ms=11, mec="white", mew=1.2)
            ax.plot(*B.mean(0), "X", color=color, ms=11, mec="white", mew=1.2)
        ax.set_xlim(-2.6, 2.8)
        ax.set_ylim(-1.8, 1.8)
        ax.set_aspect("equal")
        _bare(ax)
        ax.set_title(f"{name}\n{formula}", color=color, pad=8, fontsize=11.5,
                     linespacing=2.0)
    fig.text(0.5, 0.055, "How far apart are two groups of points?",
             ha="center", color=MUTED, fontsize=12)


@figure("ward_idea")
def ward_idea(fig):
    rng = np.random.default_rng(6)
    blobs = [
        ("A", (-2.0, -0.6), 0.45, 60, BLUE, -0.75),
        ("B", (0.4, 1.3), 0.35, 25, GREEN, 0.60),
        ("C", (2.3, -0.8), 0.35, 25, GOLD, -0.75),
    ]
    pts = {name: rng.normal(c, sd, (n, 2)) for name, c, sd, n, _, _ in blobs}
    mean = {k: v.mean(0) for k, v in pts.items()}

    def cost(i, j):
        ni, nj = len(pts[i]), len(pts[j])
        return ni * nj / (ni + nj) * ((mean[i] - mean[j]) ** 2).sum()

    ax = fig.subplots(gridspec_kw=dict(left=0.04, right=0.52, top=0.90,
                                       bottom=0.10))
    for name, _, _, n, color, dy in blobs:
        P = pts[name]
        ax.scatter(P[:, 0], P[:, 1], s=14, color=color, alpha=0.8,
                   edgecolors="none")
        ax.plot(*mean[name], "X", color=color, ms=12, mec="white", mew=1.4,
                zorder=5)
        ax.text(mean[name][0], mean[name][1] + dy, f"{name}  (n = {n})",
                ha="center", va="center", color=color, fontsize=11.5)
    for (i, j), color in ((("B", "C"), GREEN), (("A", "B"), RED)):
        ax.plot([mean[i][0], mean[j][0]], [mean[i][1], mean[j][1]], color=color,
                lw=1.6, ls="--", zorder=1)
        mid = (mean[i] + mean[j]) / 2
        step = mean[j] - mean[i]
        perp = np.array([-step[1], step[0]])
        perp = perp / np.linalg.norm(perp) * 0.46
        other = mean[({"A", "B", "C"} - {i, j}).pop()]
        if np.linalg.norm(mid - perp - other) > np.linalg.norm(mid + perp - other):
            perp = -perp
        ax.text(*(mid + perp), rf"$\Delta J_w$ = {cost(i, j):.0f}",
                ha="center", va="center", color=color, fontsize=12,
                weight="bold")
    ax.set_xlim(-3.6, 3.8)
    ax.set_ylim(-2.4, 2.8)
    ax.set_aspect("equal")
    _bare(ax)

    side = fig.add_axes([0.56, 0.12, 0.42, 0.76])
    side.axis("off")
    side.text(0.0, 0.96, "Ward: merge what costs the least", color=GREEN,
              fontsize=13, weight="bold", va="center")
    side.text(0.0, 0.75, "Merging two clusters makes the \n"
                         "within-cluster inertia $J_w$ go up\n"
                         "That increase is the Ward distance.",
              color=INK, fontsize=11.5, va="center", linespacing=1.7)
    side.text(0.0, 0.07, "Here B and C are small and close, so\nthey merge first; "
                         "even though A has\npoints nearer to B than C does.",
              color=MUTED, fontsize=11, va="center", linespacing=1.7)


@figure("eq_huygens")
def eq_huygens(fig):
    rng = np.random.default_rng(14)
    P = rng.normal((0.0, 0.0), 0.55, (26, 2))
    ma = P.mean(0)
    m = np.array([2.1, 1.0])

    ax = fig.subplots(gridspec_kw=dict(left=0.05, right=0.40, top=0.86, bottom=0.22))
    ax.scatter(P[:, 0], P[:, 1], s=16, color=BLUE, alpha=0.8, edgecolors="none")
    ax.plot(*ma, "X", color=BLUE, ms=14, mec="white", mew=1.5, zorder=5)
    ax.plot(*m, "X", color=RED, ms=14, mec="white", mew=1.5, zorder=5)
    x = P[int(np.argmax(P[:, 1]))]
    ax.plot([x[0], ma[0]], [x[1], ma[1]], color=BLUE, lw=1.6)
    ax.plot([x[0], m[0]], [x[1], m[1]], color=RED, lw=1.6, ls="--")
    ax.plot([ma[0], m[0]], [ma[1], m[1]], color=GREEN, lw=1.6)
    ax.text(ma[0] - 0.15, ma[1] - 0.30, r"$m_a$", color=BLUE, fontsize=12,
            ha="right")
    ax.text(m[0] + 0.12, m[1], r"$m$", color=RED, fontsize=12, va="center")
    ax.text(x[0] - 0.12, x[1] + 0.05, r"$x$", color=INK, fontsize=12, ha="right")
    ax.set_xlim(-1.9, 2.9)
    ax.set_ylim(-1.9, 2.0)
    ax.set_aspect("equal")
    caption(ax, "Cost of moving the centroid.")
    _bare(ax)

    ax2 = canvas(fig)
    ax2.text(4.20, 3.1, r"$\sum_{x \in C_a} \|x - m\|^2 = "
                         r"\sum_{x \in C_a} \|x - m_a\|^2 "
                         r"+ n_a \|m_a - m\|^2$",
             color=INK, fontsize=16, va="center")
    ax2.text(4.20, 2.05, "because $\\;x - m = (x - m_a) + (m_a - m)$\n"
                         "expanding the square:"
                         r"$\;2\,(m_a - m) \cdot \sum_{x \in C_a} (x - m_a) = 0$", color=INK, fontsize=11.5,
             va="center")
    ax2.text(4.20, 1.26, r"$\sum_{x \in C_a} (x - m_a)$ vanishes (definition of a centroid)",
             color=GREEN, fontsize=11.5, va="center")
    caption(ax2, "Moving the reference costs exactly $n_a \\|m_a - m\\|^2$")


@figure("eq_ward_proof")
def eq_ward_proof(fig):
    ax = canvas(fig)
    steps = [
        (r"$\Delta J_w = \sum_{x \in C_a \cup C_b} \|x - m\|^2"
         r" - \sum_{x \in C_a} \|x - m_a\|^2"
         r" - \sum_{x \in C_b} \|x - m_b\|^2$",
         r"with $m = \dfrac{n_a m_a + n_b m_b}{n_a + n_b}$, the centre of the "
         r"merged cluster"),
        (r"$\Delta J_w = n_a \|m_a - m\|^2 + n_b \|m_b - m\|^2$",
         "the identity above, applied to each half: the inner sums cancel"),
        (r"$m_a - m = \dfrac{n_b}{n_a + n_b}(m_a - m_b)$, "
         r"$\quad m_b - m = \dfrac{n_a}{n_a + n_b}(m_b - m_a)$",
         "both centres sit on the segment between them"),
        (r"$\Delta J_w = \dfrac{n_a n_b^2 + n_b n_a^2}{(n_a + n_b)^2}"
         r"\,\|m_a - m_b\|^2 = \dfrac{n_a n_b}{n_a + n_b}"
         r"\,D^2(m_a, m_b)$",
         "substitute, and the squares collapse"),
    ]
    for i, (eq, why) in enumerate(steps):
        y = 3.02 - i * 0.74
        ax.text(0.55, y, eq, color=INK if i < 3 else GREEN, fontsize=12.5,
                va="center")
        ax.text(0.55, y - (0.44 if i in (0, 3) else 0.34), why, color=MUTED,
                fontsize=10.5, va="center")
    note(ax, "only need the two centroids and groups sizes", y=0.10)


@figure("eq_ward")
def eq_ward(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.42, "This defines as a distance between clusters:",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    eq = r"$D(C_i, C_j) = \sqrt{\dfrac{2\, n_i\, n_j}{n_i + n_j}}\;\; D(m_i, m_j)$"
    ax.text(W / 2, 2.55, eq, ha="center", va="center", color=INK, fontsize=22)

    ax.annotate("", xy=(4.50, 2.25), xytext=(2.60, 1.80),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6))
    ax.text(2.50, 1.74, "# points per cluster", ha="right", va="center",
            color=BLUE, fontsize=11, linespacing=1.6)
    ax.annotate("", xy=(5.75, 2.25), xytext=(6.40, 1.80),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.6))
    ax.text(6.50, 1.74, "centroids distance", ha="left",
            va="center", color=GREEN, fontsize=11, linespacing=1.6)

    ax.text(W / 2, 1.32, r"$D^2(C_i, C_j) = 2\,\Delta J_w$",
            ha="center", va="center", color=INK, fontsize=13)
    note(ax, "\"big clusters are expensive to join\"", y=0.72)
    note(ax, "Ward keeps the tree balanced", y=0.34)


@figure("linkage_update")
def linkage_update(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.56, "After a merge, distances to all other clusters need to be computed",
            ha="center", va="center", color=MUTED, fontsize=12.5)

    # who is who: the notation the update rule is written in
    box(ax, 0.45, 2.90, 0.75, 0.36, PURPLE, r"$C_a$", size=12)
    box(ax, 0.45, 2.36, 0.75, 0.36, PURPLE, r"$C_b$", size=12)
    arrow(ax, (1.30, 3.02), (2.00, 2.82), PURPLE, lw=1.5)
    arrow(ax, (1.30, 2.56), (2.00, 2.76), PURPLE, lw=1.5)
    box(ax, 2.06, 2.62, 1.95, 0.36, PURPLE, r"$C_i = C_a \cup C_b$", size=12,
        lw=2.6)
    box(ax, 6.05, 2.62, 0.75, 0.36, GOLD, r"$C_j$", size=12)
    ax.plot([4.13, 6.00], [2.80, 2.80], color=GOLD, lw=1.6)
    ax.text(5.07, 2.98, "?", ha="center", va="center", color=GOLD,
            fontsize=15, weight="bold")

    ax.text(7.95, 2.80, "and so on for\nevery other " r"$C_j$", ha="center",
            va="center", color=MUTED, fontsize=10, linespacing=1.5)

    ax.text(W / 2, 2.08, r"$D(C_i, C_j) = \alpha_a D(C_a, C_j) + "
                         r"\alpha_b D(C_b, C_j) + \beta D(C_a, C_b) + "
                         r"\gamma\,|D(C_a, C_j) - D(C_b, C_j)|$",
            ha="center", va="center", color=INK, fontsize=13)
    ax.text(W / 2, 1.74, "Terms on the right are already known (before the merge)",
            ha="center", va="center", color=GREEN, fontsize=10.5)
    ax.text(W / 2, 1.46, "linkage is a choice of four numbers",
            ha="center", va="center", color=MUTED, fontsize=10.5)

    rows = [
        ("single", BLUE, r"$\frac{1}{2}$", r"$\frac{1}{2}$", "0", r"$-\frac{1}{2}$"),
        ("complete", RED, r"$\frac{1}{2}$", r"$\frac{1}{2}$", "0", r"$+\frac{1}{2}$"),
        ("WPGMA", PURPLE, r"$\frac{1}{2}$", r"$\frac{1}{2}$", "0", "0"),
        ("UPGMA", GOLD, r"$\frac{n_a}{n_a + n_b}$",
         r"$\frac{n_b}{n_a + n_b}$", "0", "0"),
    ]
    xs = (3.45, 5.05, 5.75, 6.45, 7.15)
    heads = ("", r"$\alpha_a$", r"$\alpha_b$", r"$\beta$", r"$\gamma$")
    for x, head in zip(xs, heads):
        ax.text(x, 1.14, head, ha="center", va="center", color=MUTED,
                fontsize=11)
    for i, (name, color, aa, ab, b, g) in enumerate(rows):
        y = 0.88 - i * 0.25
        ax.text(xs[0], y, name, ha="center", va="center", color=color,
                fontsize=11)
        for x, cell in zip(xs[1:], (aa, ab, b, g)):
            ax.text(x, y, cell, ha="center", va="center", color=INK,
                    fontsize=11)


@figure("wpgma")
def wpgma(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.24, "a distance you compute from the previous step, never "
                         "from the points",
            ha="center", va="center", color=MUTED, fontsize=12)

    box(ax, 0.80, 2.35, 1.10, 0.45, PURPLE, r"$C_a$", size=13)
    box(ax, 0.80, 1.45, 1.10, 0.45, PURPLE, r"$C_b$", size=13)
    box(ax, 2.70, 1.85, 1.85, 0.45, PURPLE, r"$C_i = C_a \cup C_b$", size=12,
        lw=2.6)
    box(ax, 6.55, 1.85, 1.10, 0.45, GOLD, r"$C_j$", size=13)
    arrow(ax, (2.00, 2.52), (2.65, 2.22), PURPLE, lw=1.6)
    arrow(ax, (2.00, 1.68), (2.65, 1.98), PURPLE, lw=1.6)

    ax.plot([2.00, 6.50], [2.76, 2.42], color=PURPLE, lw=1.3, ls=":")
    ax.text(4.30, 2.82, r"$D(C_a, C_j)$  already known", ha="center",
            va="center", color=PURPLE, fontsize=11)
    ax.plot([2.00, 6.50], [1.46, 1.80], color=PURPLE, lw=1.3, ls=":")
    ax.text(4.30, 1.32, r"$D(C_b, C_j)$  already known", ha="center",
            va="center", color=PURPLE, fontsize=11)
    ax.plot([4.60, 6.50], [2.08, 2.08], color=GOLD, lw=1.8)
    ax.text(5.55, 2.24, "?", ha="center", va="center", color=GOLD, fontsize=15,
            weight="bold")

    ax.text(W / 2, 0.76, r"$D(C_i, C_j) = \dfrac{D(C_a, C_j) + "
                         r"D(C_b, C_j)}{2}$",
            ha="center", va="center", color=INK, fontsize=16)
    note(ax, "Costs one average per merge", y=0.16, size=11.5)


# ==========================================================================
# 3. what makes a clustering good
# ==========================================================================
@figure("eq_inertia")
def eq_inertia(fig):
    ax = canvas(fig)
    rows = [
        (INK, r"$m_i = \frac{1}{n_i}\sum_{x \in C_i} x$",
         r"the centre of cluster $C_i$"),
        (INK, r"$m = \frac{1}{n}\sum_{x} x$",
         "the centre of the whole dataset"),
        (BLUE, r"$J_w = \sum_i \sum_{x \in C_i} D^2(x, m_i)$",
         "within: how tight the clusters are"),
        (GREEN, r"$J_b = \sum_i n_i\, D^2(m_i, m)$",
         r"between: how far each $m_i$ sits from $m$"),
    ]
    for i, (color, formula, meaning) in enumerate(rows):
        y = 3.12 - i * 0.62
        ax.text(3.05, y, formula, ha="center", va="center", color=color,
                fontsize=15)
        ax.text(5.00, y, meaning, ha="left", va="center", color=INK, fontsize=12)
    ax.plot([0.70, 8.40], [0.92, 0.92], color=GRID, lw=1.2)
    ax.text(W / 2, 0.58, r"a good clustering makes $J_w$ small and $J_b$ large",
            ha="center", va="center", color=INK, fontsize=14)
    ax.text(W / 2, 0.16, r"$J_w$ with $K = n$ is zero",
            ha="center", va="center", color=RED, fontsize=12)


@figure("good_clustering")
def good_clustering(fig):
    rng = np.random.default_rng(5)
    X, truth = _blobs(rng, [(-1.9, -1.0), (1.9, -0.8), (0.0, 1.9)], 0.52, 50)

    def scores(labels):
        jw = jb = 0.0
        m = X.mean(0)
        for k in set(labels):
            pts = X[labels == k]
            centre = pts.mean(0)
            jw += ((pts - centre) ** 2).sum()
            jb += len(pts) * ((centre - m) ** 2).sum()
        return jw, jb

    from sklearn.cluster import KMeans

    bad = (X[:, 0] > 0).astype(int)
    many = KMeans(8, n_init=10, random_state=0).fit_predict(X)
    rand = rng.integers(0, 3, len(X))
    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.03, right=0.99, top=0.78, bottom=0.28, wspace=0.10),
    )
    for ax, labels, title, color in (
        (axes[0], truth, "looks legitimate", GREEN),
        (axes[1], bad, "too few clusters", GOLD),
        (axes[2], many, "too many clusters", GOLD),
        (axes[3], rand, "clusters at random", RED),
    ):
        _scatter_clusters(ax, X, labels, s=14)
        jw, jb = scores(labels)
        ax.set_title(title, color=color, pad=10, fontsize=12.5)
        caption(ax, rf"$J_w$ = {jw:.0f}    $J_b$ = {jb:.0f}")
        ax.set_xlim(-4, 4)
        ax.set_ylim(-3, 3.6)
        _bare(ax)


# ==========================================================================
# 4. k-means
# ==========================================================================
@figure("eq_kmeans")
def eq_kmeans(fig):
    ax = canvas(fig)
    equation(
        ax,
        r"$J_w \;=\; \sum_{k=1}^{K} \sum_{x_i \in C_k} \|x_i - \mu_k\|^2$",
        y=2.85,
        size=26,
        color=GOLD,
    )
    ax.text(W / 2, 2.05, "find the K centres that make this as small as possible",
            ha="center", va="center", color=INK, fontsize=13.5)
    ax.plot([1.30, 7.70], [1.70, 1.70], color=GRID, lw=1.2)
    ax.text(W / 2, 1.35, r"$P(n, K) = \frac{1}{K!}\sum_{k=0}^{K}(-1)^{K-k}"
                         r"\binom{K}{k} k^{\,n}$   partitions to try",
            ha="center", va="center", color=INK, fontsize=13)
    ax.text(W / 2, 0.85, r"$P(100, 5) \approx 10^{68}$", ha="center", va="center",
            color=RED, fontsize=17)
    ax.text(2.55, 0.35, "the exact problem is NP-hard", ha="center", va="center",
            color=RED, fontsize=11.5)
    ax.text(6.45, 0.35, r"k-means finds a local minimum in $O(tKN)$", ha="center",
            va="center", color=GREEN, fontsize=11.5)


@figure("kmeans_algorithm")
def kmeans_algorithm(fig):
    rng = np.random.default_rng(23)
    X, _ = _blobs(rng, [(-1.8, -1.1), (1.9, -0.8), (0.1, 1.9)], 0.55, 60)
    mu = np.array([[-2.6, 1.7], [-2.1, 1.3], [-2.3, 0.8]])

    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.80, bottom=0.18, wspace=0.10),
    )
    titles = ["1.  initialise", "2.  assign", "3.  move the centres", "4.  repeat"]
    for step, (ax, title) in enumerate(zip(axes, titles)):
        labels = None
        if step:
            labels = ((X[:, None, :] - mu[None]) ** 2).sum(-1).argmin(1)
        if step >= 2:
            mu = np.array([X[labels == k].mean(0) if (labels == k).any() else mu[k]
                           for k in range(3)])
            labels = ((X[:, None, :] - mu[None]) ** 2).sum(-1).argmin(1)
        if step == 3:
            for _ in range(8):
                mu = np.array([X[labels == k].mean(0) for k in range(3)])
                labels = ((X[:, None, :] - mu[None]) ** 2).sum(-1).argmin(1)
        if labels is None:
            ax.scatter(X[:, 0], X[:, 1], s=12, color=MUTED, alpha=0.6,
                       edgecolors="none")
        else:
            _scatter_clusters(ax, X, labels, s=12)
        for k in range(3):
            ax.plot(*mu[k], "X", color=CLUSTER_COLORS[k], ms=13, mec="white",
                    mew=1.4, zorder=5)
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-3.0, 3.4)
        ax.set_aspect("equal")
        _bare(ax)
        ax.set_title(title, pad=8, fontsize=12.5)
    fig.text(0.5, 0.05, "assign to the nearest centre, move each centre to the "
                        "mean of its points, repeat",
             ha="center", color=MUTED, fontsize=12)


@figure("inertia_defined")
def inertia_defined(fig):
    rng = np.random.default_rng(8)
    X = rng.normal((0.0, 0.0), 0.62, (32, 2))
    centre = X.mean(0)
    inertia = ((X - centre) ** 2).sum()

    ax = fig.subplots(gridspec_kw=dict(left=0.05, right=0.44, top=0.86,
                                       bottom=0.24))
    for px, py in X:
        ax.plot([centre[0], px], [centre[1], py], color=BLUE, lw=0.8, alpha=0.45,
                zorder=1)
    ax.scatter(X[:, 0], X[:, 1], s=20, color=BLUE, alpha=0.9, edgecolors="none",
               zorder=3)
    ax.plot(*centre, "X", color=RED, ms=15, mec="white", mew=1.6, zorder=5)
    far = X[int(np.argmax(((X - centre) ** 2).sum(1)))]
    ax.annotate(r"$\|x_i - \mu_k\|$", xy=(far + centre) / 2,
                xytext=((far + centre) / 2 + np.array([0.15, 0.42])),
                ha="center", color=INK, fontsize=11,
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.2))
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title("Distance to cluster center", pad=10, fontsize=13)
    caption_row(fig, [ax], ["add the squared distances"], y=0.165)

    ax2 = canvas(fig)
    ax2.text(4.75, 2.9, r"$J_w = \sum_{k=1}^{K} \;\; "
                         r"\sum_{x_i \in C_k} \|x_i - \mu_k\|^2$",
             ha="left", va="center", color=INK, fontsize=17)
    ax2.text(4.75, 1.9, "Inertia is what k-means minimises",
             ha="left", va="center", color=GREEN, fontsize=11.5)
    ax2.text(4.75, 1.2, "Inertia falls as $K$ grows",
             ha="left", va="center", color=MUTED, fontsize=11.5)
    ax2.text(4.75, 0.5, "Do not compare inertia values for different $K$.",
             ha="left", va="center", color=AMBER, fontsize=11.5)


@figure("kmeans_init")
def kmeans_init(fig):
    from sklearn.cluster import KMeans

    X = _tree_data(seed=3, noise=0)
    axes = fig.subplots(
        1, 3,
        gridspec_kw=dict(left=0.04, right=0.98, top=0.80, bottom=0.26, wspace=0.12),
    )
    runs = (
        ("k-means++", dict(init="k-means++", n_init=10, random_state=0), GREEN),
        ("one unlucky start",
         dict(init=X[np.random.default_rng(13).choice(len(X), 5, replace=False)],
              n_init=1), RED),
        ("another unlucky start",
         dict(init=X[np.random.default_rng(50).choice(len(X), 5, replace=False)],
              n_init=1), RED),
    )
    for ax, (title, kw, color) in zip(axes, runs):
        model = KMeans(5, **kw).fit(X)
        _scatter_clusters(ax, X, model.labels_, s=11)
        ax.set_title(title, color=color, pad=10, fontsize=12.5)
        caption(ax, f"inertia {model.inertia_:.0f}")
        ax.set_aspect("equal")
        _bare(ax)
    fig.text(0.5, 0.045, "Algorithm result depends on where the centres start.",
             ha="center", color=MUTED, fontsize=12)


@figure("kmeans_limits")
def kmeans_limits(fig):
    from sklearn.cluster import KMeans
    from sklearn.datasets import make_blobs, make_moons

    rng = np.random.default_rng(31)
    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.80, bottom=0.24, wspace=0.10),
    )
    Xm, _ = make_moons(260, noise=0.06, random_state=0)
    Xb, _ = make_blobs(n_samples=240, centers=[(-2.2, 0), (2.2, 0), (0, 2.4)],
                       cluster_std=[0.9, 0.3, 0.3], random_state=1)
    Xo = np.vstack([rng.normal((-1.6, 0), 0.5, (90, 2)),
                    rng.normal((1.6, 0), 0.5, (90, 2)),
                    rng.uniform(-7, 7, (6, 2))])
    Xk, _ = make_blobs(n_samples=240, centers=4, cluster_std=0.6, random_state=4)
    cases = (
        ("non-convex shapes", Xm * 2.0, 2),
        ("unequal spreads", Xb, 3),
        ("outliers", Xo, 2),
        ("wrong K", Xk, 2),
    )
    for ax, (title, data, k) in zip(axes, cases):
        labels = KMeans(k, n_init=10, random_state=0).fit_predict(data)
        _scatter_clusters(ax, data, labels, s=10)
        ax.set_title(title, color=RED, pad=8, fontsize=12)
        ax.set_aspect("equal")
        _bare(ax)


@figure("kmeans_alternatives")
def kmeans_alternatives(fig):
    ax = canvas(fig)
    rows = [
        (GREEN, "k-means++", "spread the initial centres out",
         "default"),
        (BLUE, "k-medoids", "centres are actual data points",
         "robust to outliers"),
        (PURPLE, "kernel k-means", "cluster in a feature space",
         "non-convex shapes"),
        (GOLD, "mini-batch k-means", "update on samples of rows",
         "for large n datasets"),
    ]
    for i, (color, name, what, when) in enumerate(rows):
        y = 3.05 - i * 0.72
        ax.text(2.35, y, name, ha="right", va="center", color=color, fontsize=13,
                weight="bold")
        ax.text(2.60, y, what, ha="left", va="center", color=INK, fontsize=12)
        ax.text(5.70, y, when, ha="left", va="center", color=MUTED, fontsize=11.5)
        if i:
            ax.plot([0.60, 8.50], [y + 0.36, y + 0.36], color=GRID, lw=0.9)
    note(ax, "Always need to choose K", y=0.30)


# ==========================================================================
# 4b. mountain and subtractive clustering
# ==========================================================================
MOUNTAIN_CMAP = LinearSegmentedColormap.from_list(
    "mountain", ["#ffffff", "#e8eef6", "#bed4ea", "#7ba7d1", BLUE])


def _mountain_data(seed=21):
    rng = np.random.default_rng(seed)
    return np.vstack([rng.normal((-1.8, -0.7), 0.42, (60, 2)),
                      rng.normal((1.7, -0.5), 0.34, (40, 2)),
                      rng.normal((0.1, 1.6), 0.30, (35, 2))])


def _mountain_grid(X, step=0.22, pad=0.9):
    lo, hi = X.min(0) - pad, X.max(0) + pad
    gx = np.arange(lo[0], hi[0] + step, step)
    gy = np.arange(lo[1], hi[1] + step, step)
    GX, GY = np.meshgrid(gx, gy)
    return GX, GY, np.stack([GX.ravel(), GY.ravel()], 1)


def _mountain(V, X, sigma):
    d2 = ((V[:, None, :] - X[None]) ** 2).sum(-1)
    return np.exp(-d2 / (2 * sigma ** 2)).sum(1)


def _mountain_peaks(V, M, k, beta):
    """k rounds of 'take the peak, then subtract it'."""
    M = M.copy()
    peaks, surfaces = [], [M.copy()]
    for _ in range(k):
        i = int(np.argmax(M))
        peaks.append(V[i])
        M = M - M[i] * np.exp(-((V - V[i]) ** 2).sum(-1) / (2 * beta ** 2))
        surfaces.append(M.copy())
    return peaks, surfaces


def _subtractive(X, ra, ratio=0.5, kmax=6):
    """Chiu's subtractive clustering: peaks of the potential, then assign."""
    rb = 1.5 * ra
    d2 = ((X[:, None, :] - X[None]) ** 2).sum(-1)
    P = np.exp(-4 * d2 / ra ** 2).sum(1)
    first = P.max()
    centres = []
    for _ in range(kmax):
        i = int(np.argmax(P))
        if P[i] < ratio * first:
            break
        centres.append(X[i])
        P = P - P[i] * np.exp(-4 * ((X - X[i]) ** 2).sum(-1) / rb ** 2)
    C = np.array(centres)
    labels = ((X[:, None, :] - C[None]) ** 2).sum(-1).argmin(1)
    return labels, C


@figure("wpgma_vs_upgma")
def wpgma_vs_upgma(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.56, "WPGMA — Weighted Pair Group Method with "
                         "Arithmetic mean",
            ha="center", va="center", color=PURPLE, fontsize=12.5,
            weight="bold")
    ax.text(W / 2, 3.28, "UPGMA — Unweighted Pair Group Method with "
                         "Arithmetic mean",
            ha="center", va="center", color=GOLD, fontsize=12.5, weight="bold")
    ax.text(W / 2, 2.98, "'weighted' means the two children count equally "
                         "(not that their sizes count)",
            ha="center", va="center", color=MUTED, fontsize=11.5)

    box(ax, 0.70, 2.16, 1.45, 0.50, PURPLE, "", fill="white")
    ax.text(1.42, 2.41, r"$C_{a}$:  2 points", ha="center", va="center",
            color=PURPLE, fontsize=11.5)
    box(ax, 0.70, 1.26, 1.45, 0.50, PURPLE, "", fill="white")
    ax.text(1.42, 1.51, r"$C_{b}$:  20 points", ha="center", va="center",
            color=PURPLE, fontsize=11.5)
    box(ax, 3.55, 1.71, 1.30, 0.50, GOLD, r"$C_j$", size=13)
    arrow(ax, (2.25, 2.36), (3.50, 2.06), MUTED, lw=1.4)
    arrow(ax, (2.25, 1.56), (3.50, 1.88), MUTED, lw=1.4)
    ax.text(2.88, 2.42, r"$D = 1$", ha="center", va="center", color=INK,
            fontsize=11)
    ax.text(2.88, 1.32, r"$D = 5$", ha="center", va="center", color=INK,
            fontsize=11)

    column(ax, 5.45, 2.56, 3.2, "WPGMA", [
        r"$\frac{1 + 5}{2} = 3.0$",
        "each child gets half a vote",
    ], PURPLE, leading=0.40, item_size=12, title_size=13)
    column(ax, 5.45, 1.40, 3.2, "UPGMA", [
        r"$\frac{2 \cdot 1 + 20 \cdot 5}{22} = 4.6$",
        "each point gets a vote",
    ], GOLD, leading=0.40, item_size=12, title_size=13)


@figure("mountain_idea")
def mountain_idea(fig):
    X = _mountain_data()
    GX, GY, V = _mountain_grid(X)
    M = _mountain(V, X, 0.45)

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.04, right=0.66, top=0.84, bottom=0.22, wspace=0.14),
    )
    axes[0].scatter(GX.ravel(), GY.ravel(), s=2.5, color=GRID, zorder=1)
    axes[0].scatter(X[:, 0], X[:, 1], s=14, color=INK, alpha=0.75,
                    edgecolors="none", zorder=3)
    axes[0].set_title("grid over the data", pad=10, fontsize=13)
    caption(axes[0], "every node is a candidate centre")

    axes[1].contourf(GX, GY, M.reshape(GX.shape), levels=14, cmap=MOUNTAIN_CMAP)
    axes[1].scatter(X[:, 0], X[:, 1], s=8, color=INK, alpha=0.45,
                    edgecolors="none")
    top = V[int(np.argmax(M))]
    axes[1].plot(*top, "X", color=RED, ms=13, mec="white", mew=1.4, zorder=5)
    axes[1].set_title("build mountains", color=BLUE, pad=10, fontsize=13)
    caption(axes[1], "the highest peak is the first centre")
    for ax in axes:
        ax.set_aspect("equal")
        _bare(ax)

    side = fig.add_axes([0.70, 0.22, 0.28, 0.62])
    side.axis("off")
    side.text(0.0, 0.92, "Every data point raises the\nground around it",
              color=BLUE, fontsize=11, va="center", linespacing=1.7)
    side.text(0.0, 0.56, "Where points are crowded,\nthe hills add up",
              color=INK, fontsize=11, va="center", linespacing=1.7)
    side.text(0.0, 0.18, "Take the summit, flatten it,\nrepeat",
              color=GREEN, fontsize=11, va="center", linespacing=1.7)


@figure("eq_mountain")
def eq_mountain(fig):
    ax = canvas(fig)
    ax.text(W / 2, 2.78, r"$M(v) = \sum_{i=1}^{n} "
                         r"\exp\left(-\dfrac{\|v - x_i\|^2}"
                         r"{2\sigma^2}\right)$",
            ha="center", va="center", color=INK, fontsize=19)
    ax.text(W / 2, 2.22, r"$\sigma$ : how wide one point's hill is",
            ha="center", va="center", color=BLUE, fontsize=12)
    ax.plot([1.20, 7.80], [1.92, 1.92], color=GRID, lw=1.2)
    ax.text(W / 2, 1.42, r"$M_{\mathrm{new}}(v) = M(v) - M(c_1)\,"
                         r"\exp\left(-\dfrac{\|v - c_1\|^2}"
                         r"{2\beta^2}\right)$",
            ha="center", va="center", color=INK, fontsize=19)
    ax.text(W / 2, 0.86, r"$\beta > \sigma$ : how much ground the new centre "
                         "clears, so the next peak is somewhere else",
            ha="center", va="center", color=GREEN, fontsize=12)
    note(ax, "Stop when the tallest remaining peak is a small enough", y=0.38)


@figure("mountain_steps")
def mountain_steps(fig):
    X = _mountain_data()
    GX, GY, V = _mountain_grid(X)
    M = _mountain(V, X, 0.45)
    peaks, surfaces = _mountain_peaks(V, M, 4, 0.75)

    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.03, right=0.99, top=0.80, bottom=0.26, wspace=0.10),
    )
    titles = ["no peak subtracted", "peak 1 subtracted",
              "peak 2 subtracted", "peak 3 subtracted"]
    vmax = M.max()
    for i, ax in enumerate(axes):
        surface = surfaces[i]
        ax.contourf(GX, GY, surface.reshape(GX.shape), levels=14,
                    cmap=MOUNTAIN_CMAP, vmin=0, vmax=vmax)
        ax.scatter(X[:, 0], X[:, 1], s=6, color=INK, alpha=0.40,
                   edgecolors="none")
        shown = peaks[: i + 1] if i < 3 else peaks
        for j, c in enumerate(shown):
            ax.plot(*c, "X", color=RED if j == i else GOLD, ms=11, mec="white",
                    mew=1.2, zorder=5)
        ax.set_title(titles[i], color=BLUE, pad=8,
                     fontsize=12)
        ax.set_aspect("equal")
        _bare(ax)
    caption_row(fig, axes, [
        rf"first peak: {surfaces[0].max():.1f}",
        rf"next peak: {surfaces[1].max():.1f}",
        rf"next peak: {surfaces[2].max():.1f}",
        "stop as fourth peak too low",
    ], y=0.185)
    fig.text(0.5, 0.05, "Number of clusters is automatically detected.",
             ha="center", color=MUTED, fontsize=12)


@figure("subtractive_clustering")
def subtractive_clustering(fig):
    X = _mountain_data()
    ra = 1.1
    d2 = ((X[:, None, :] - X[None]) ** 2).sum(-1)
    P0 = np.exp(-4 * d2 / ra ** 2).sum(1)
    _, centres = _subtractive(X, ra)

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.04, right=0.62, top=0.84, bottom=0.22, wspace=0.14),
    )
    axes[0].scatter(X[:, 0], X[:, 1], s=10 + 55 * P0 / P0.max(), c=P0,
                    cmap=MOUNTAIN_CMAP, edgecolors=GRID, linewidths=0.4)
    axes[0].set_title("potential at data points", color=BLUE, pad=10,
                      fontsize=13)
    axes[0].set_xlabel("")

    axes[1].scatter(X[:, 0], X[:, 1], s=12, color=INK, alpha=0.45,
                    edgecolors="none")
    for c in centres:
        axes[1].add_patch(Circle(c, ra / 2, facecolor=GREEN, alpha=0.10,
                                 edgecolor=GREEN, lw=1.4))
        axes[1].plot(*c, "X", color=GREEN, ms=12, mec="white", mew=1.4, zorder=5)
    axes[1].set_title("centres kept", color=GREEN, pad=10, fontsize=13)
    for ax in axes:
        ax.set_aspect("equal")
        _bare(ax)

    side = fig.add_axes([0.66, 0.20, 0.32, 0.64])
    side.axis("off")
    side.text(0.0, 0.95, r"$P_i = \sum_j \exp\left(-\dfrac{4\,"
                         r"\|x_i - x_j\|^2}{r_a^2}\right)$",
              color=INK, fontsize=13.5, va="center")
    side.text(0.0, 0.66, r"$r_a$: neighbourhood radius" "\n"
                         r"$r_b \approx 1.5\, r_a$: what a centre clears",
              color=MUTED, fontsize=11, va="center", linespacing=1.8)


@figure("mountain_props")
def mountain_props(fig):
    ax = canvas(fig)
    column(ax, 0.55, 3.25, 3.9, "Pros", [
        "No need to guesstimate the number of clusters",
        "The centres are real peaks of density",
    ], GREEN, leading=0.34)
    column(ax, 4.90, 3.25, 3.9, "Cons", [
        r"$\sigma$ (or $r_a$) is very sensible",
        "The grid grows as $m^d$, so need $d$ small",
    ], RED, leading=0.34)
    ax.plot([4.65, 4.65], [0.72, 3.35], color=GRID, lw=1.2)
    note(ax, "Can be used to initialise k-means", y=0.38)


# ==========================================================================
# 5. hierarchical clustering
# ==========================================================================
def _group_ellipse(ax, pts, color, pad=0.10, lw=2.0):
    """A dashed ellipse that fits exactly round a handful of points."""
    centre = pts.mean(0)
    _, _, axes_ = np.linalg.svd(pts - centre)
    extent = np.abs((pts - centre) @ axes_.T).max(0)
    angle = np.degrees(np.arctan2(axes_[0, 1], axes_[0, 0]))
    ax.add_patch(Ellipse(centre, 2 * (extent[0] + pad), 2 * (extent[1] + pad),
                         angle=angle, facecolor="none", edgecolor=color,
                         lw=lw, ls="--", zorder=1))


def _toy_points():
    """Six labelled points, small enough to follow a dendrogram by eye."""
    return np.array([[0.20, 0.85], [0.32, 0.72], [0.80, 0.80],
                     [0.92, 0.66], [0.55, 0.15], [0.72, 0.22]])


@figure("hierarchy_idea")
def hierarchy_idea(fig):
    from scipy.cluster.hierarchy import dendrogram, linkage

    X = _toy_points()
    Z = linkage(X, method="average")

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.05, right=0.97, top=0.82, bottom=0.30, wspace=0.22),
    )
    ax = axes[0]
    ax.scatter(X[:, 0], X[:, 1], s=70, color=INK, zorder=3)
    for i, (x, y) in enumerate(X):
        ax.text(x + 0.040, y, f"$P_{i+1}$", ha="left", va="center",
                color=INK, fontsize=11.5, zorder=4)
    for members, colour in (((0, 1), BLUE), ((2, 3), RED), ((4, 5), GREEN)):
        _group_ellipse(ax, X[list(members)], colour, pad=0.13)
    _group_ellipse(ax, X[[2, 3, 4, 5]], PURPLE, pad=0.21)
    ax.set_xlim(-0.05, 1.26)
    ax.set_ylim(-0.05, 1.10)
    _bare(ax)
    ax.set_title("nested groups", pad=10, fontsize=13)
    caption(ax, "a cluster is the union of its children")

    ax = axes[1]
    dendrogram(Z, ax=ax, labels=[f"P{i+1}" for i in range(6)],
               color_threshold=0, above_threshold_color=INK)
    ax.set_ylabel("merge distance")
    despine(ax, keep=("left",))
    ax.set_title("the dendrogram", color=GREEN, pad=10, fontsize=13)
    caption(ax, "branch height represents how far apart the two halves were")


@figure("agglomerative_steps")
def agglomerative_steps(fig):
    from scipy.cluster.hierarchy import fcluster, linkage

    X = _toy_points()
    Z = linkage(X, method="average")
    axes = fig.subplots(
        1, 6,
        gridspec_kw=dict(left=0.02, right=0.99, top=0.80, bottom=0.18, wspace=0.08),
    )
    titles = ["start: 6 clusters"] + [f"after {m} merge" + ("" if m == 1 else "s")
                                      for m in range(1, 6)]
    for ax, k, title in zip(axes, range(6, 0, -1), titles):
        raw = fcluster(Z, k, criterion="maxclust")
        labels = np.array([min(np.flatnonzero(raw == c)) for c in raw])
        _scatter_clusters(ax, X, labels, s=45)
        for i, (x, y) in enumerate(X):
            ax.text(x, y + 0.075, f"$P_{i+1}$", ha="center", color=MUTED,
                    fontsize=8.5)
        ax.set_xlim(0.02, 1.08)
        ax.set_ylim(0.0, 1.05)
        _bare(ax)
        ax.set_title(title, pad=8, fontsize=10)
    fig.text(0.5, 0.05, "agglomerative: start with one cluster per point, "
                        "merge the nearest pair, repeat",
             ha="center", color=MUTED, fontsize=12)


@figure("dendrogram_cut")
def dendrogram_cut(fig):
    from scipy.cluster.hierarchy import dendrogram, fcluster, linkage

    X = _tree_data(seed=3, noise=0)
    Z = linkage(X, method="ward")
    cut = 9.0

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.06, right=0.97, top=0.82, bottom=0.24, wspace=0.22),
    )
    ax = axes[0]
    dendrogram(Z, ax=ax, no_labels=True, color_threshold=cut,
               above_threshold_color=MUTED)
    ax.axhline(cut, color=RED, lw=2.0, ls="--")
    ax.text(ax.get_xlim()[1] * 0.99, cut + 0.5, "cut here", color=RED,
            fontsize=11.5, ha="right")
    ax.set_ylabel("merge distance")
    despine(ax, keep=("left",))
    ax.set_title("one cut, one clustering", pad=10, fontsize=13)
    caption(ax, "lower the line for more clusters, raise it for fewer")

    ax = axes[1]
    labels = fcluster(Z, cut, criterion="distance") - 1
    _scatter_clusters(ax, X, labels, s=12)
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title(f"{len(set(labels))} clusters", color=GREEN, pad=10, fontsize=13)
    caption(ax, "choice of cut replaces the choice of K")


@figure("linkage_compare")
def linkage_compare(fig):
    from scipy.cluster.hierarchy import fcluster, linkage

    X = _tree_data(seed=3, noise=25)
    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.80, bottom=0.22, wspace=0.10),
    )
    defs = [r"$\min_{x,y} D(x, y)$", r"$\max_{x,y} D(x, y)$",
            r"$\mathrm{mean}_{x,y}\, D(x, y)$",
            r"$\Delta J_w$ of the merge"]
    caps = ['"one bridge of points is enough"',
            '"far ends must be close too"',
            '"compromise of single & complete"',
            '"the smallest jump in inertia"']
    for ax, method, color, formula in zip(
            axes, ("single", "complete", "average", "ward"),
            (BLUE, RED, GREEN, PURPLE), defs):
        Z = linkage(X, method=method)
        labels = fcluster(Z, 3, criterion="maxclust") - 1
        _scatter_clusters(ax, X, labels, s=10)
        ax.set_title(f"{method}\n{formula}", color=color, pad=8, fontsize=12,
                     linespacing=1.9)
        ax.set_aspect("equal")
        _bare(ax)
    caption_row(fig, axes, caps, y=0.175, size=10)


@figure("linkage_dendrograms")
def linkage_dendrograms(fig):
    from scipy.cluster.hierarchy import dendrogram, linkage

    X = _tree_data(seed=3, noise=25)
    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.04, right=0.98, top=0.80, bottom=0.22, wspace=0.18),
    )
    defs = ["single\nnearest pair of points",
            "complete\nfarthest pair of points",
            "average\nmean over all pairs",
            "ward\ninertia added by the merge"]
    caps = ["everything joins one growing chain",
            "splits large groups",
            "balanced",
            "also (more?) balanced"]
    for ax, method, color, title in zip(
            axes, ("single", "complete", "average", "ward"),
            (BLUE, RED, GREEN, PURPLE), defs):
        Z = linkage(X, method=method)
        dendrogram(Z, ax=ax, no_labels=True, color_threshold=0,
                   above_threshold_color=color)
        ax.set_title(title, color=color, pad=8, fontsize=11.5, linespacing=1.9)
        ax.set_yticks([])
        despine(ax)
    axes[0].set_ylabel("merge distance")
    caption_row(fig, axes, caps, y=0.175, size=10)
    fig.text(0.5, 0.045, "the shape of the tree is the signature of the linkage",
             ha="center", color=MUTED, fontsize=12)


@figure("linkage_props")
def linkage_props(fig):
    ax = canvas(fig)
    rows = [
        (BLUE, "single / MIN", "follows chains of any shape",
         "one bridge of noise joins two clusters"),
        (RED, "complete / MAX", "resists outliers",
         "breaks large clusters, prefers round clusters"),
        (GREEN, "average", "does not break large clusters",
         "prefers round clusters"),
        (PURPLE, "Ward", "balanced, k-means-like clusters",
         "balanced"),
    ]
    ax.text(3.95, 3.45, "good at", ha="center", va="center", color=GREEN,
            fontsize=11.5)
    ax.text(6.75, 3.45, "bad at", ha="center", va="center", color=RED,
            fontsize=11.5)
    for i, (color, name, good, bad) in enumerate(rows):
        y = 2.95 - i * 0.72
        ax.text(2.35, y, name, ha="right", va="center", color=color, fontsize=13,
                weight="bold")
        ax.text(2.60, y, good, ha="left", va="center", color=INK, fontsize=11.5)
        ax.text(5.55, y, bad, ha="left", va="center", color=MUTED, fontsize=11.5)
        if i:
            ax.plot([0.60, 8.60], [y + 0.36, y + 0.36], color=GRID, lw=0.9)
    note(ax, "Linkage is a second modelling choice; it is as consequential as the distance.", y=0.28)


@figure("hierarchical_props")
def hierarchical_props(fig):
    ax = canvas(fig)
    column(ax, 0.55, 3.25, 3.9, "Pros", [
        "No K to choose up front",
        "Readable tree at every scale",
        "Can use any dissimilarity metric\n(not just Euclidean)",
    ], GREEN, leading=0.34)
    column(ax, 4.90, 3.25, 3.9, "Cons", [
        r"$O(N^2)$ memory, $O(N^2 \log N)$ time",
        "Still need to choose a threshhold to cut",
    ], RED, leading=0.34)
    ax.plot([4.65, 4.65], [0.70, 3.35], color=GRID, lw=1.2)


# ==========================================================================
# 6. DBSCAN
# ==========================================================================
def _dbscan_toy(seed=5):
    from sklearn.datasets import make_moons

    rng = np.random.default_rng(seed)
    X, _ = make_moons(220, noise=0.06, random_state=0)
    X = X * 2.0
    X = np.vstack([X, rng.uniform(-3.0, 4.0, (25, 2))])
    return X


@figure("dbscan_idea")
def dbscan_idea(fig):
    rng = np.random.default_rng(9)
    X = np.vstack([rng.normal((-0.6, 0.2), 0.55, (40, 2)),
                   rng.normal((2.1, 0.5), 0.30, (18, 2)),
                   rng.uniform(-2.5, 3.5, (8, 2))])
    eps = 0.55

    ax = fig.subplots(gridspec_kw=dict(left=0.04, right=0.55, top=0.92,
                                       bottom=0.08))
    ax.scatter(X[:, 0], X[:, 1], s=16, color=INK, alpha=0.55, edgecolors="none")
    for centre, color in ((X[3], GREEN), (X[-1], RED)):
        ax.add_patch(Circle(centre, eps, facecolor=color, alpha=0.12,
                            edgecolor=color, lw=1.8))
        ax.plot(*centre, "o", color=color, ms=8, zorder=4)
    ax.set_xlim(-3.0, 4.0)
    ax.set_ylim(-2.4, 2.6)
    ax.set_aspect("equal")
    _bare(ax)

    side = fig.add_axes([0.58, 0.14, 0.40, 0.74])
    side.axis("off")
    side.text(0.0, 0.78, r"$\varepsilon$: threshold for 'nearby'", color=BLUE,
              fontsize=12.5, va="center")
    side.text(0.0, 0.66, r"$N_\varepsilon(x_i) = \{z : d(x_i, z) < \varepsilon\}$",
              color=INK, fontsize=12.5, va="center")
    side.text(0.0, 0.48, r"MinPts: threshold for 'crowded' neighborhood", color=GREEN,
              fontsize=12.5, va="center")
    side.text(0.0, 0.36, r"$x_i$ is a core point if "
                         r"$|N_\varepsilon(x_i)| \geq$ MinPts",
              color=INK, fontsize=12.5, va="center")
    side.text(0.0, 0.16, "A cluster is a dense region.", color=MUTED,
              fontsize=11.5, va="center")
    side.text(0.0, -0.10, "No need to specify K", color=RED, fontsize=12.5, va="center")


@figure("dbscan_points")
def dbscan_points(fig):
    rng = np.random.default_rng(12)
    X = np.vstack([rng.normal((-0.8, 0.0), 0.55, (55, 2)),
                   rng.normal((2.0, 0.4), 0.45, (30, 2)),
                   rng.uniform(-2.6, 3.6, (10, 2))])
    eps, min_pts = 0.55, 6
    d = np.linalg.norm(X[:, None, :] - X[None], axis=-1)
    neigh = (d < eps).sum(1)
    core = neigh >= min_pts
    border = ~core & ((d < eps) & core[None, :]).any(1)
    noise = ~core & ~border

    ax = fig.subplots(gridspec_kw=dict(left=0.05, right=0.60, top=0.90, bottom=0.14))
    ax.scatter(X[noise, 0], X[noise, 1], s=26, color=RED, marker="x", lw=1.8,
               zorder=3)
    ax.scatter(X[border, 0], X[border, 1], s=26, facecolor="white",
               edgecolor=GOLD, lw=1.8, zorder=3)
    ax.scatter(X[core, 0], X[core, 1], s=26, color=GREEN, zorder=3)
    centre = X[core][0]
    ax.add_patch(Circle(centre, eps, facecolor=GREEN, alpha=0.10,
                        edgecolor=GREEN, lw=1.4))
    ax.set_xlim(-2.8, 3.8)
    ax.set_ylim(-2.4, 2.4)
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title(rf"$\varepsilon$ = {eps},   MinPts = {min_pts}", pad=10,
                 fontsize=13)

    side = fig.add_axes([0.63, 0.16, 0.35, 0.70])
    side.axis("off")
    rows = [
        (GREEN, "core", "MinPts neighbours or more", f"{core.sum()} points"),
        (GOLD, "border", "near a core point, but not one", f"{border.sum()} points"),
        (RED, "noise", "neither", f"{noise.sum()} points"),
    ]
    for i, (color, name, meaning, count) in enumerate(rows):
        y = 0.92 - i * 0.29
        side.text(0.0, y, name, color=color, fontsize=13, weight="bold",
                  va="center")
        side.text(0.0, y - 0.10, meaning, color=INK, fontsize=11, va="center")
        side.text(0.0, y - 0.19, count, color=MUTED, fontsize=10.5, va="center")


@figure("dbscan_algorithm")
def dbscan_algorithm(fig):
    ax = canvas(fig)
    box(ax, 0.55, 0.80, 4.15, 2.62, BLUE, "", fill="white")
    ax.text(2.62, 3.14, "DBSCAN", ha="center", va="center", color=BLUE,
            fontsize=14, weight="bold")
    steps = [
        r"Take an unvisited point $x_i$",
        r"Count its neighbours within $\varepsilon$",
        "Fewer than MinPts → mark it noise, move on",
        "Otherwise open a cluster and grow it:",
        "   - Core neighbours add their own neighbourhood",
        "   - Border points join without their neighbourhood",
    ]
    for i, step in enumerate(steps):
        y = 2.70 - i * 0.33
        ax.text(0.85, y, step, ha="left", va="center", color=INK, fontsize=11.5)
    column(
        ax,
        5.25,
        3.25,
        3.5,
        "Result:",
        [
            "One cluster per dense region in the data",
            "A set of noise points",
        ],
        GREEN,
        item_size=11.5,
        title_size=12.5,
        leading=0.36,
    )


@figure("dbscan_epsilon")
def dbscan_epsilon(fig):
    from sklearn.cluster import DBSCAN

    X = _dbscan_toy()
    axes = fig.subplots(
        1, 3,
        gridspec_kw=dict(left=0.04, right=0.98, top=0.78, bottom=0.26, wspace=0.12),
    )
    caps = []
    for ax, eps, color, label in zip(axes, (0.12, 0.30, 1.10),
                                     (RED, GREEN, GOLD),
                                     ("too small", "about right", "too large")):
        labels = DBSCAN(eps=eps, min_samples=6).fit_predict(X)
        _scatter_clusters(ax, X, labels, s=11)
        n_clusters = len(set(labels) - {-1})
        ax.set_title(f"{label}\n" rf"$\varepsilon$ = {eps}", color=color, pad=8,
                     fontsize=12.5, linespacing=1.8)
        caps.append(f"{_plural(n_clusters, 'cluster')}, "
                    f"{_plural((labels == -1).sum(), 'noise point')}")
        ax.set_aspect("equal")
        _bare(ax)
    caption_row(fig, axes, caps, y=0.155)


@figure("dbscan_minpts")
def dbscan_minpts(fig):
    from sklearn.cluster import DBSCAN

    X = _dbscan_toy()
    eps = 0.35
    axes = fig.subplots(
        1, 3,
        gridspec_kw=dict(left=0.04, right=0.98, top=0.78, bottom=0.26, wspace=0.12),
    )
    caps = []
    for ax, mp, color, label in zip(axes, (2, 6, 18), (RED, GREEN, GOLD),
                                    ("too small", "about right", "too large")):
        labels = DBSCAN(eps=eps, min_samples=mp).fit_predict(X)
        _scatter_clusters(ax, X, labels, s=11)
        n_clusters = len(set(labels) - {-1})
        ax.set_title(f"{label}\nMinPts = {mp}", color=color, pad=8,
                     fontsize=12.5, linespacing=1.8)
        caps.append(f"{_plural(n_clusters, 'cluster')}, "
                    f"{_plural((labels == -1).sum(), 'noise point')}")
        ax.set_aspect("equal")
        _bare(ax)
    caption_row(fig, axes, caps, y=0.155)
    fig.text(0.5, 0.045, rf"$\varepsilon$ = {eps} throughout: MinPts decides "
                         "how much of the data is called noise",
             ha="center", color=MUTED, fontsize=12)


@figure("dbscan_knn_elbow")
def dbscan_knn_elbow(fig):
    from sklearn.cluster import DBSCAN
    from sklearn.neighbors import NearestNeighbors

    X = _dbscan_toy()
    k = 6
    d, _ = NearestNeighbors(n_neighbors=k).fit(X).kneighbors(X)
    kth = np.sort(d[:, -1])
    knee = 0.30

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.08, right=0.97, top=0.82, bottom=0.24, wspace=0.26),
    )
    ax = axes[0]
    ax.plot(np.arange(len(kth)), kth, color=BLUE, lw=2.6)
    ax.axhline(knee, color=RED, lw=1.8, ls="--")
    ax.set_xlabel("points, sorted")
    ax.set_ylabel(rf"distance to the {k}th neighbour")
    despine(ax, keep=("bottom", "left"))
    ax.set_title("Fix MinPts & guesstimate ε", pad=10, fontsize=13)
    caption(ax, "below the knee: ordinary points:  above the knee: the sparse tail")

    ax = axes[1]
    labels = DBSCAN(eps=knee, min_samples=k).fit_predict(X)
    _scatter_clusters(ax, X, labels, s=11)
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title(rf"$\varepsilon$ = {knee},  MinPts = {k}", color=GREEN, pad=10,
                 fontsize=13)


@figure("dbscan_vs_kmeans")
def dbscan_vs_kmeans(fig):
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.datasets import make_blobs, make_circles, make_moons

    rng = np.random.default_rng(2)
    moons, _ = make_moons(260, noise=0.06, random_state=0)
    circles, _ = make_circles(260, noise=0.05, factor=0.45, random_state=0)
    blobs, _ = make_blobs(n_samples=260, centers=[(-2.0, 0), (2.0, 0.4), (0, 2.4)],
                          cluster_std=[0.9, 0.3, 0.3], random_state=1)
    datasets = (
        ("two moons", moons * 2.0, 2, 0.32),
        ("rings", circles * 2.4, 2, 0.55),
        ("unequal spreads", blobs, 3, 0.55),
    )
    axes = fig.subplots(
        2, 3,
        gridspec_kw=dict(left=0.08, right=0.98, top=0.86, bottom=0.08,
                         wspace=0.10, hspace=0.22),
    )
    for col, (title, X, k, eps) in enumerate(datasets):
        km = KMeans(k, n_init=10, random_state=0).fit_predict(X)
        db = DBSCAN(eps=eps, min_samples=6).fit_predict(X)
        _scatter_clusters(axes[0, col], X, km, s=9)
        _scatter_clusters(axes[1, col], X, db, s=9)
        axes[0, col].set_title(title, pad=8, fontsize=12.5)
        for ax in (axes[0, col], axes[1, col]):
            ax.set_aspect("equal")
            _bare(ax)
    axes[0, 0].set_ylabel("k-means", color=BLUE, fontsize=12.5)
    axes[1, 0].set_ylabel("DBSCAN", color=GREEN, fontsize=12.5)


@figure("dbscan_props")
def dbscan_props(fig):
    ax = canvas(fig)
    column(ax, 0.55, 3.25, 3.9, "Pros", [
        "Clusters of any shape",
        "Noise is labelled",
        "No guesstimate needed for K",
    ], GREEN, leading=0.34)
    column(ax, 4.90, 3.25, 3.9, "Cons", [
        "MinPts & $\\varepsilon$ hard to choose",
        "Same density assumed for the whole dataset",
    ], RED, leading=0.34)
    ax.plot([4.65, 4.65], [0.80, 3.35], color=GRID, lw=1.2)
    note(ax, "HDBSCAN tackles the uniform density assumption.", y=0.42)


# ==========================================================================
# 7. HDBSCAN
# ==========================================================================
def _density_data(seed=4, n_dense=70, n_sparse=45, n_noise=18):
    """Clusters of three different densities, plus noise."""
    rng = np.random.default_rng(seed)
    X = np.vstack([
        rng.normal((-1.9, -0.6), 0.26, (n_dense, 2)),
        rng.normal((0.6, 1.5), 0.17, (n_dense, 2)),
        rng.normal((2.2, -0.9), 0.80, (n_sparse, 2)),
        rng.uniform((-3.4, -2.6), (4.0, 3.2), (n_noise, 2)),
    ])
    return X


def _core_distances(X, k):
    d = np.linalg.norm(X[:, None, :] - X[None], axis=-1)
    return np.sort(d, axis=1)[:, k], d


def _mutual_reachability(X, k):
    core, d = _core_distances(X, k)
    return np.maximum(np.maximum(core[:, None], core[None, :]), d)


@figure("hdbscan_idea")
def hdbscan_idea(fig):
    ax = canvas(fig)
    box(ax, 0.6, 2.55, 7.8, 0.95, BLUE, "", fill="white")
    ax.text(4.5, 3.26, "General idea", ha="center", va="center", color=BLUE,
            fontsize=13.5, weight="bold")
    ax.text(4.5, 2.92, "Running DBSCAN for every value of " r"$\varepsilon$ at once,"
            " and keep the clusters that last",
            ha="center", va="center", color=INK, fontsize=13)
    column(ax, 0.6, 2.15, 3.9, "Benefits", [
        r"no $\varepsilon$ to choose",
        "clusters of different densities,\nside by side in one dataset",
        "a hierarchy",
    ], GREEN, leading=0.32)
    column(ax, 4.9, 2.15, 3.9, "Need to choose", [
        r"MinPts: the scale of the density",
        r"$C_{\min}$: size of the smallest cluster",
    ], GOLD, leading=0.32)
    note(ax, "hierarchical DBSCAN: density-based, but over all scales", y=0.35)


@figure("hdbscan_steps")
def hdbscan_steps(fig):
    ax = canvas(fig)
    steps = [
        (r"1. compute $\mathrm{core}_k$", "measure the\nlocal density", BLUE),
        ("2. transform\nthe space", r"use $d_{\mathrm{mreach}}$" "\n"
         r"instead of $d$", BLUE),
        ("3. spanning\ntree", "connect every\npoint, cheaply", GREEN),
        ("4. cluster\nhierarchy", "cut the edges\nheaviest first", GREEN),
        ("5. condense\nthe hierarchy", "collapse branches\n"
         r"under $C_{\min}$", GOLD),
        ("6. extract\nstable clusters", "keep what\nsurvives longest", RED),
    ]
    w, gap = 1.30, 0.14
    x = 0.33
    for title, sub, color in steps:
        box(ax, x, 1.55, w, 1.40, color, "", fill="white")
        ax.text(x + w / 2, 2.62, title, ha="center", va="center", color=color,
                fontsize=10, weight="bold", linespacing=1.5)
        ax.text(x + w / 2, 2.00, sub, ha="center", va="center", color=INK,
                fontsize=9, linespacing=1.5)
        if x > 0.5:
            arrow(ax, (x - gap + 0.02, 2.25), (x - 0.02, 2.25), MUTED, lw=1.5)
        x += w + gap
    note(ax, r"MinPts enters at step 1; $C_{\min}$ at step 5", y=0.65,
         color=MUTED, size=12)


@figure("core_distance")
def core_distance(fig):
    X = _density_data()
    k = 5
    core, _ = _core_distances(X, k)

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.05, right=0.97, top=0.82, bottom=0.22, wspace=0.14),
    )
    ax = axes[0]
    ax.scatter(X[:, 0], X[:, 1], s=12, color=INK, alpha=0.5, edgecolors="none")
    dense_i = int(np.argsort(core)[3])
    sparse_i = int(np.argsort(core)[int(0.93 * len(core))])
    for i, color, label in ((dense_i, GREEN, "dense"), (sparse_i, RED, "sparse")):
        ax.add_patch(Circle(X[i], core[i], facecolor=color, alpha=0.12,
                            edgecolor=color, lw=1.8))
        ax.plot(*X[i], "o", color=color, ms=7, zorder=4)
        ax.annotate(rf"{label}: $\mathrm{{core}}_{{{k}}}$ = {core[i]:.2f}",
                    xy=X[i], xytext=(X[i][0], X[i][1] - core[i] - 0.45),
                    ha="center", va="top", color=color, fontsize=11)
    ax.set_xlim(-4.2, 4.6)
    ax.set_ylim(-4.0, 3.6)
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title(rf"$\mathrm{{core}}_k(x_i)$ = distance to the {k}th neighbour",
                 pad=10, fontsize=13)
    caption(ax, "cheapest density estimate")

    ax = axes[1]
    order = np.argsort(core)
    ax.scatter(X[order, 0], X[order, 1], s=24, c=core[order], cmap=DENSITY_CMAP,
               edgecolors="none")
    ax.set_xlim(-4.2, 4.6)
    ax.set_ylim(-4.0, 3.6)
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title("low density → large core distance", pad=10, fontsize=13)
    caption(ax, "blue = crowded, red = out at sea")


@figure("eq_mutual_reachability")
def eq_mutual_reachability(fig):
    ax = canvas(fig)
    eq = (r"$d_{\mathrm{mreach}-k}(x_i, x_j) = "
          r"\max\left(\mathrm{core}_k(x_i),\ \mathrm{core}_k(x_j),\ "
          r"d(x_i, x_j)\right)$")
    ax.text(W / 2, 2.72, eq, ha="center", va="center", fontsize=21, color=INK)
    column(ax, 0.9, 2.05, 3.6, "Two points are close only if", [
        "they are close in space",
        "they both sit in a dense region",
    ], BLUE, leading=0.32)
    column(ax, 4.9, 2.05, 3.6, "Sparse points", [
        "are pushed away from everything\n(including each other)",
        "single linkage stops chaining through them",
    ], GREEN, leading=0.32)
    note(ax, "Islands-and-sea picture: sea is widen, lands do not move", y=0.22)


def _mreach_toy():
    """Six points: a tight crowd, plus two stragglers — the worked example."""
    X = np.array([
        [0.00, 0.00], [0.42, 0.22], [0.18, 0.50], [0.58, -0.26],
        [1.85, 0.80], [2.55, 1.35],
    ])
    names = ["$A$", "$B$", "$C$", "$D$", "$P$", "$Q$"]
    return X, names


@figure("mreach_example")
def mreach_example(fig):
    X, names = _mreach_toy()
    k = 2
    core, d = _core_distances(X, k)

    ax = fig.add_axes([0.03, 0.14, 0.42, 0.66])
    for i, color in ((0, BLUE), (4, RED), (5, RED)):
        ax.add_patch(Circle(X[i], core[i], facecolor=color, alpha=0.09,
                            edgecolor=color, lw=1.4, ls="--"))
    ax.scatter(X[:, 0], X[:, 1], s=40, color=INK, zorder=4, edgecolors="none")
    for (x, y), name in zip(X, names):
        ax.text(x + 0.10, y + 0.12, name, color=INK, fontsize=11.5, zorder=5)
    ax.set_xlim(-1.3, 3.5)
    ax.set_ylim(-1.3, 2.6)
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title(r"Dashed circles are $\mathrm{core}_2$",
                 pad=8, fontsize=12.5)
    caption_row(fig, [ax], ["$A$ sits in the crowd, $P$ and $Q$ do not"],
                y=0.135)

    cax = canvas(fig)
    pairs = [(0, 1, "both in the crowd", GREEN),
             (1, 4, "one of them alone", GOLD),
             (4, 5, "both out at sea", RED)]
    xs = (4.72, 5.56, 6.40, 7.24, 8.18)
    heads = ("pair", r"$d$", r"$\mathrm{core}_2$", r"$\mathrm{core}_2$",
             r"$d_{\mathrm{mreach}}$")
    cax.text(6.45, 3.42, r"$d_{\mathrm{mreach}}$ is the largest of the three",
             ha="center", va="center", color=MUTED, fontsize=11.5)
    for x, head in zip(xs, heads):
        cax.text(x, 2.96, head, ha="center", va="center", color=MUTED,
                 fontsize=11)
    cax.plot([4.38, 8.72], [2.76, 2.76], color=GRID, lw=1.0)
    cax.plot([7.72, 7.72], [0.70, 3.08], color=GRID, lw=1.0)
    for r, (i, j, why, color) in enumerate(pairs):
        y = 2.44 - r * 0.62
        vals = (d[i, j], core[i], core[j])
        best = int(np.argmax(vals))
        cax.text(xs[0], y, f"{names[i]}, {names[j]}", ha="center", va="center",
                 color=INK, fontsize=12)
        for c, (x, v) in enumerate(zip(xs[1:4], vals)):
            cax.text(x, y, f"{v:.2f}", ha="center", va="center",
                     color=color if c == best else MUTED,
                     fontsize=12, weight="bold" if c == best else "normal")
        cax.text(xs[4], y, f"{max(vals):.2f}", ha="center", va="center",
                 color=color, fontsize=12.5, weight="bold")
        cax.text(xs[0], y - 0.26, why, ha="center", va="center", color=MUTED,
                 fontsize=9.5)
    cax.text(6.45, 0.42, "$A$ and $B$ keep their real distance;\n"
                         "every pair that touches $P$ or $Q$ is pushed apart",
             ha="center", va="center", color=INK, fontsize=11,
             linespacing=1.6)


@figure("mreach_intuition")
def mreach_intuition(fig):
    rng = np.random.default_rng(5)
    left = rng.normal((-1.6, 0.0), 0.30, (40, 2))
    right = rng.normal((1.6, 0.0), 0.30, (40, 2))
    bridge = np.c_[np.linspace(-0.95, 0.95, 5), np.zeros(5)]
    X = np.vstack([left, right, bridge])
    k = 4
    core, d = _core_distances(X, k)

    ax = fig.add_axes([0.02, 0.22, 0.46, 0.56])
    ax.scatter(X[:80, 0], X[:80, 1], s=16, color=MUTED, alpha=0.7,
               edgecolors="none")
    for b in bridge:
        i = int(np.argmin(((X - b) ** 2).sum(1)))
        ax.add_patch(Circle(X[i], core[i], facecolor=RED, alpha=0.07,
                            edgecolor=RED, lw=1.2, ls="--"))
    ax.scatter(bridge[:, 0], bridge[:, 1], s=36, color=RED, zorder=4,
               edgecolors="none")
    for a, b in zip(bridge[:-1], bridge[1:]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=RED, lw=1.4, zorder=3)
    ax.set_xlim(-2.9, 2.9)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title("path of stray points can no longer\nbridge the two blobs", pad=6,
                 fontsize=12.5)

    cax = canvas(fig)
    blocks = [
        ("it puts a floor under every point", GREEN,
         r"nothing can be nearer to $x_i$ than $\mathrm{core}_k(x_i)$, so a"
         "\npoint in an empty region is far from everything"),
        ("it never shrinks a distance", BLUE,
         "dense pairs keep the distance they had;\nonly the sparse ones move"),
        ("it stays symmetric", PURPLE,
         r"(as $\max$ of a symmetric list)"),
    ]
    y = 3.00
    for head, color, body in blocks:
        cax.text(4.95, y, head, color=color, fontsize=11.5, weight="bold",
                 va="center")
        cax.text(4.95, y - 0.40, body, color=INK, fontsize=10.5, va="center",
                 linespacing=1.6)
        y -= 1.04


@figure("mreach_effect")
def mreach_effect(fig):
    X = _density_data(seed=7, n_dense=45, n_sparse=30, n_noise=14)
    k = 5
    d = np.linalg.norm(X[:, None, :] - X[None], axis=-1)
    mr = _mutual_reachability(X, k)
    iu = np.triu_indices(len(X), 1)

    ax = fig.subplots(
        gridspec_kw=dict(left=0.34, right=0.66, top=0.82, bottom=0.26),
    )
    ax.scatter(d[iu], mr[iu], s=5, color=BLUE, alpha=0.25, edgecolors="none")
    lim = d[iu].max() * 1.02
    ax.plot([0, lim], [0, lim], color=MUTED, lw=1.4, ls="--")
    ax.text(lim * 0.70, lim * 0.62, r"$d_{\mathrm{mreach}} = d$", color=MUTED,
            fontsize=11, rotation=38)
    ax.set_xlabel(r"$d(x_i, x_j)$")
    ax.set_ylabel(r"$d_{\mathrm{mreach}-k}(x_i, x_j)$")
    despine(ax, keep=("bottom", "left"))
    ax.set_title("New distance $\\geq$ old distances", pad=10, fontsize=13)
    caption(ax, "Distance is unchanged for pairs in dense regions, inflated elsewhere.")



@figure("mst_step")
def mst_step(fig):
    from scipy.sparse.csgraph import minimum_spanning_tree

    X = _density_data(seed=7, n_dense=45, n_sparse=28, n_noise=12)
    k = 5
    mr = _mutual_reachability(X, k)
    mst = minimum_spanning_tree(mr).toarray()
    rows, cols = np.nonzero(mst)
    weights = mst[rows, cols]

    ax = fig.subplots(gridspec_kw=dict(left=0.05, right=0.62, top=0.88,
                                       bottom=0.16))
    norm = plt.Normalize(weights.min(), weights.max())
    cmap = DENSITY_CMAP
    for r, c, wgt in zip(rows, cols, weights):
        ax.plot(X[[r, c], 0], X[[r, c], 1], color=cmap(norm(wgt)), lw=1.3,
                zorder=1)
    ax.scatter(X[:, 0], X[:, 1], s=14, color=INK, zorder=2, edgecolors="none")
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title("minimum spanning tree under " r"$d_{\mathrm{mreach}}$",
                 pad=10, fontsize=13)

    side = fig.add_axes([0.65, 0.16, 0.33, 0.70])
    side.axis("off")
    side.text(0.0, 0.95, f"{len(X)} points", color=INK, fontsize=12.5,
              va="center")
    side.text(0.0, 0.8, rf"$\binom{{n}}{{2}}$ = {len(X)*(len(X)-1)//2} "
                         "possible edges", color=MUTED, fontsize=12, va="center")
    side.text(0.0, 0.6, f"{len(rows)} edges kept", color=GREEN, fontsize=12.5,
              va="center")
    side.text(0.0, 0.36, '"the cheapest set of edges\nthat still connects everything"',
              color=INK, fontsize=11, va="center", linespacing=1.7)


def _mst_toy():
    """Seven labelled points, small enough to follow edge by edge."""
    X = np.array([
        [0.10, 2.20], [1.05, 2.65], [0.55, 1.35], [1.95, 1.75],
        [3.40, 2.30], [3.60, 1.15], [3.05, 0.30],
    ])
    return X, list("ABCDEFG")


def _edge_label(ax, p, q, text, color, size=10, off=0.30, avoid=None):
    """A weight written beside its edge, on whichever side is emptier."""
    mid = (p + q) / 2
    d = q - p
    n = np.array([-d[1], d[0]])
    n = n / (np.linalg.norm(n) + 1e-12)
    sides = [mid + off * n, mid - off * n]
    if avoid is not None:
        sides.sort(key=lambda c: -np.linalg.norm(avoid - c, axis=1).min())
    elif sides[0][1] < sides[1][1]:
        sides.reverse()
    ax.text(*sides[0], text, ha="center", va="center", color=color,
            fontsize=size, zorder=6)


def _prim(D):
    """Prim's algorithm: grow one tree, always adding its cheapest exit edge."""
    n = len(D)
    inside = [0]
    edges = []
    while len(inside) < n:
        outside = [j for j in range(n) if j not in inside]
        i, j = min(((i, j) for i in inside for j in outside),
                   key=lambda e: D[e])
        edges.append((i, j, D[i, j]))
        inside.append(j)
    return edges


@figure("mst_build")
def mst_build(fig):
    X, names = _mst_toy()
    D = np.linalg.norm(X[:, None, :] - X[None], axis=-1)
    edges = _prim(D)

    shown = (1, 2, 4, 6)
    titles = ("start anywhere", "add the cheapest exit edge",
              "(repeat)", "stop at " r"$n - 1$ edges")
    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.70, bottom=0.26,
                         wspace=0.08),
    )
    for ax, m, title in zip(axes, shown, titles):
        inside = {0} | {j for _, j, _ in edges[:m]}
        # every edge the tree could still take, faint
        for i in sorted(inside):
            for j in range(len(X)):
                if j not in inside:
                    ax.plot(X[[i, j], 0], X[[i, j], 1], color=GRID, lw=0.6,
                            ls=":", alpha=0.7, zorder=1)
        for i, j, w in edges[:m - 1]:
            ax.plot(X[[i, j], 0], X[[i, j], 1], color=BLUE, lw=2.0, zorder=2)
        i, j, w = edges[m - 1]
        ax.plot(X[[i, j], 0], X[[i, j], 1], color=GREEN, lw=2.6, zorder=3)
        _edge_label(ax, X[i], X[j], f"{w:.2f}", GREEN, avoid=X)
        ax.scatter(X[:, 0], X[:, 1], s=70, color="white", zorder=4,
                   edgecolors=MUTED, linewidths=1.0)
        for (x, y), name, k in zip(X, names, range(len(X))):
            ax.text(x, y, name, ha="center", va="center", zorder=5,
                    color=INK if k in inside else MUTED, fontsize=9)
        ax.set_xlim(-0.70, 4.35)
        ax.set_ylim(-0.55, 3.20)
        ax.set_aspect("equal")
        _bare(ax)
        ax.set_title(title, pad=6, fontsize=11.5, color=INK)

    fig.text(0.5, 0.90, "Prim's algorithm: add the cheapest edge",
             ha="center", color=MUTED, fontsize=12.5)
    caption_row(fig, axes, [f"{m} " + ("edge" if m == 1 else "edges")
                            for m in shown], y=0.215)
    fig.text(0.5, 0.10, "no cycle can ever appear: new endpoint is chosen outside the tree",
             ha="center", color=INK, fontsize=11.5)


@figure("mst_to_hierarchy")
def mst_to_hierarchy(fig):
    from scipy.cluster.hierarchy import dendrogram, linkage
    from scipy.spatial.distance import squareform

    X, names = _mst_toy()
    D = np.linalg.norm(X[:, None, :] - X[None], axis=-1)
    edges = sorted(_prim(D), key=lambda e: -e[2])

    axL = fig.add_axes([0.03, 0.22, 0.42, 0.56])
    for rank, (i, j, w) in enumerate(edges):
        color = (RED, GOLD)[rank] if rank < 2 else BLUE
        axL.plot(X[[i, j], 0], X[[i, j], 1], color=color,
                 lw=2.8 if rank < 2 else 1.8, zorder=2)
        _edge_label(axL, X[i], X[j], f"{w:.2f}", color, avoid=X)
    axL.scatter(X[:, 0], X[:, 1], s=90, color="white", zorder=4,
                edgecolors=MUTED, linewidths=1.1)
    for (x, y), name in zip(X, names):
        axL.text(x, y, name, ha="center", va="center", color=INK, fontsize=10,
                 zorder=5)
    axL.set_xlim(-0.65, 4.30)
    axL.set_ylim(-0.55, 3.15)
    axL.set_aspect("equal")
    _bare(axL)
    axL.set_title("A tree with its edge weights", pad=8, fontsize=12.5)
    caption_row(fig, [axL], ["cut the heaviest edge first"], y=0.145)

    Z = linkage(squareform(D, checks=False), method="single")
    axR = fig.add_axes([0.56, 0.24, 0.40, 0.55])
    with plt.rc_context({"lines.linewidth": 1.8}):
        dendrogram(Z, ax=axR, labels=names, color_threshold=0,
                   above_threshold_color=BLUE)
    for y, color in zip(sorted(e[2] for e in edges)[-2:][::-1], (RED, GOLD)):
        axR.axhline(y, color=color, lw=1.4, ls="--")
    axR.set_ylabel("height of the merge")
    despine(axR, keep=("left",))
    axR.set_title("same tree drawn as a dendrogram", pad=8, fontsize=12.5)
    caption_row(fig, [axR], ["each cut is one horizontal line"], y=0.145)

    fig.text(0.5, 0.955, "Removing the edges heaviest first is equivalent to reading "
                         "the dendrogram from the top.",
             ha="center", color=MUTED, fontsize=12.5)


def _hdbscan_tree(X=None, k=5, min_size=10):
    """The single-linkage tree of the running example, under d_mreach."""
    from scipy.cluster.hierarchy import linkage
    from scipy.spatial.distance import squareform

    if X is None:
        X = _density_data(seed=7, n_dense=45, n_sparse=28, n_noise=12)
    mr = _mutual_reachability(X, k)
    np.fill_diagonal(mr, 0.0)
    return X, linkage(squareform(mr, checks=False), method="single")


def _condensed_tree(Z, min_size):
    """HDBSCAN's condensed tree.

    Walk the single-linkage tree from the root down. A split only counts as a
    split when both sides still hold min_size points; otherwise the small side
    is a handful of points falling out of a cluster that carries on.
    """
    n = len(Z) + 1
    left, right = Z[:, 0].astype(int), Z[:, 1].astype(int)
    size = np.r_[np.ones(n, int), Z[:, 3].astype(int)]
    clusters = {0: dict(parent=None, lam_birth=0.0, falls=[], children=[],
                        size0=int(size[2 * n - 2]))}
    nxt = 0
    stack = [(2 * n - 2, 0)]
    while stack:
        node, cid = stack.pop()
        if node < n:
            continue
        a, b = left[node - n], right[node - n]
        h = Z[node - n, 2]
        lam = 1.0 / h if h > 0 else np.inf
        big_a, big_b = size[a] >= min_size, size[b] >= min_size
        if big_a and big_b:
            clusters[cid]["lam_death"] = lam
            for child in (a, b):
                nxt += 1
                clusters[nxt] = dict(parent=cid, lam_birth=lam, falls=[],
                                     children=[], size0=int(size[child]))
                clusters[cid]["children"].append(nxt)
                stack.append((child, nxt))
        elif big_a or big_b:
            keep, drop = (a, b) if big_a else (b, a)
            clusters[cid]["falls"] += [lam] * int(size[drop])
            stack.append((keep, cid))
        else:
            clusters[cid]["falls"] += [lam] * int(size[node])
            clusters[cid]["lam_death"] = lam
    for c in clusters.values():
        c["falls"].sort()
        stay = c["size0"] - len(c["falls"])
        c["stability"] = sum(l - c["lam_birth"] for l in c["falls"])
        if stay:
            c["stability"] += stay * (c["lam_death"] - c["lam_birth"])
    return clusters


def _condensed_nodes(Z, min_size):
    """node of the single-linkage tree -> the condensed cluster it lives in.

    The same walk as _condensed_tree, kept so the raw dendrogram can be
    painted in the colours of the tree it condenses to.
    """
    n = len(Z) + 1
    left, right = Z[:, 0].astype(int), Z[:, 1].astype(int)
    size = np.r_[np.ones(n, int), Z[:, 3].astype(int)]
    owner = {2 * n - 2: 0}
    nxt = 0
    stack = [(2 * n - 2, 0)]
    while stack:
        node, cid = stack.pop()
        if node < n:
            continue
        a, b = left[node - n], right[node - n]
        if size[a] >= min_size and size[b] >= min_size:
            for child in (a, b):
                nxt += 1
                owner[child] = nxt
                stack.append((child, nxt))
        elif max(size[a], size[b]) >= min_size:
            keep = a if size[a] >= min_size else b
            owner[keep] = cid
            stack.append((keep, cid))
    return owner


def _condensed_layout(clusters, cid=0, x0=0.0, x1=1.0, out=None):
    """Give every condensed cluster a horizontal slot, children inside parent."""
    out = {} if out is None else out
    out[cid] = (x0 + x1) / 2
    kids = clusters[cid]["children"]
    if kids:
        total = sum(clusters[k]["size0"] for k in kids)
        x = x0
        for k in kids:
            w = (x1 - x0) * clusters[k]["size0"] / total
            _condensed_layout(clusters, k, x, x + w, out)
            x += w
    return out


def _draw_condensed(ax, clusters, lam_max, colors=None, label=None,
                    width=0.085):
    """The HDBSCAN bar tree: bar width = points still inside, y = lambda."""
    pos = _condensed_layout(clusters)
    for cid, c in clusters.items():
        lam0 = c["lam_birth"]
        lam1 = min(c.get("lam_death", lam_max), lam_max)
        falls = [l for l in c["falls"] if l <= lam1]
        ys = [lam0] + falls + [lam1]
        remaining = c["size0"]
        xs = []
        for i in range(len(ys) - 1):
            xs.append(remaining)
            remaining -= 1 if i < len(falls) else 0
        color = (colors or {}).get(cid, MUTED)
        for y0, y1, m in zip(ys[:-1], ys[1:], xs):
            half = width * m / clusters[0]["size0"]
            ax.fill_betweenx([y0, y1], pos[cid] - half, pos[cid] + half,
                             color=color, lw=0)
        if c["children"]:
            kids = [pos[k] for k in c["children"]]
            ax.plot([min(kids), max(kids)], [lam1, lam1], color=color, lw=1.2)
        if label:
            label(ax, cid, c, pos[cid], lam0, lam1)
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(lam_max, 0)
    ax.set_xticks([])


@figure("hdbscan_hierarchy")
def hdbscan_hierarchy(fig):
    from scipy.cluster.hierarchy import dendrogram, fcluster

    min_size = 10
    X, Z = _hdbscan_tree(min_size=min_size)

    ax = fig.add_axes([0.06, 0.20, 0.58, 0.58])
    with plt.rc_context({"lines.linewidth": 1.0}):
        dendrogram(Z, ax=ax, no_labels=True, color_threshold=0,
                   above_threshold_color=MUTED)
    ax.set_ylabel(r"$d_{\mathrm{mreach}}$ at the merge")
    ax.set_xticks([])
    despine(ax, keep=("left",))
    ax.set_title("Single linkage on the transformed space", pad=8,
                 fontsize=12.5)
    caption_row(fig, [ax], ["One dendrogram gives DBSCAN for all $\\varepsilon$ at once."],
                y=0.145)

    cuts = [(1.45, RED), (1.00, GOLD), (0.55, GREEN)]
    lines = []
    for eps, color in cuts:
        ax.axhline(eps, color=color, lw=1.5, ls="--")
        labels = fcluster(Z, t=eps, criterion="distance")
        counts = np.bincount(labels)[1:]
        kept = int((counts >= min_size).sum())
        noise = int(counts[counts < min_size].sum())
        ax.text(ax.get_xlim()[1] * 0.995, eps + 0.03,
                rf"$\varepsilon$ = {eps:.2f}", ha="right", va="bottom",
                color=color, fontsize=10)
        lines.append((color, rf"$\varepsilon$ = {eps:.2f}",
                      f"{_plural(kept, 'cluster')}, {noise} left over"))

    cax = canvas(fig)
    cax.text(5.80, 3.10, "horizontal cut $\\Leftrightarrow$ DBSCAN run", color=BLUE,
             fontsize=12.5, weight="bold", va="center")
    y = 2.62
    for color, head, body in lines:
        cax.text(6.00, y, head, color=color, fontsize=11.5, va="center")
        cax.text(6.95, y, body, color=INK, fontsize=11, va="center")
        y -= 0.42
    cax.text(6.00, 1.18, "No cut is right everywhere:\n"
                         "- loose clusters need a high cut\n"
                         "- tight clusters need a low cut",
             color=INK, fontsize=10.5, va="center", linespacing=1.7)
    cax.text(6.00, 0.34, "Pick a different height per branch",
             color=GREEN, fontsize=11, va="center", linespacing=1.7)


@figure("condensed_tree")
def condensed_tree(fig):
    from scipy.cluster.hierarchy import dendrogram

    min_size = 10
    X, Z = _hdbscan_tree()
    clusters = _condensed_tree(Z, min_size)

    fig.text(0.5, 0.93, "at every split, ask whether both sides still hold "
                        rf"$C_{{\min}}$ = {min_size} points",
             ha="center", color=INK, fontsize=12.5)

    colors = {0: GRID, 1: BLUE, 2: GRID, 3: GOLD, 4: GREEN}
    owner = _condensed_nodes(Z, min_size)

    axL = fig.add_axes([0.06, 0.20, 0.38, 0.60])
    with plt.rc_context({"lines.linewidth": 0.9}):
        dendrogram(Z, ax=axL, no_labels=True,
                   link_color_func=lambda i: colors.get(owner.get(i), GRID))
    axL.set_ylabel(r"$d_{\mathrm{mreach}}$ at the merge")
    axL.set_ylim(0, Z[:, 2].max() * 1.05)
    despine(axL, keep=("left",))
    axL.set_xticks([])
    axL.set_title("Raw tree", color=MUTED, pad=8, fontsize=12.5)

    axR = fig.add_axes([0.56, 0.20, 0.38, 0.60])
    lam_max = 3.2

    def label(ax, cid, c, x, lam0, lam1):
        if cid == 0 or lam1 - lam0 < 0.05 * lam_max:
            return
        ax.text(x, (lam0 + lam1) / 2, _plural(c["size0"], "point"),
                ha="center", va="center", color=colors[cid], fontsize=10,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.6))

    _draw_condensed(axR, clusters, lam_max, colors, label)
    axR.set_ylabel(r"$\lambda = 1/\varepsilon$")
    despine(axR, keep=("left",))
    axR.set_title(rf"Condensed tree $C_{{\min}}$ = {min_size}", color=BLUE, pad=8,
                  fontsize=12.5)
    fig.text(0.5, 0.055, "Tree with noise swept out: a few thick branches",
             ha="center", color=INK, fontsize=11.5)


@figure("condense_example")
def condense_example(fig):
    ax = canvas(fig)
    cmin = 5
    ax.text(W / 2, 3.52, rf"$C_{{\min}}$ = {cmin}: at every split, count the two sides",
            ha="center", va="center", color=MUTED, fontsize=12.5)

    cases = [
        (1.60, 14, 8, 6, GREEN, "real split",
         "both sides are big enough:\ntwo new clusters are born"),
        (4.50, 14, 12, 2, GOLD, "some points fall out",
         "one side is too small: it is noise,\nand the cluster carries on as 12"),
        (7.40, 6, 4, 2, RED, "cluster dies",
         "neither side survives: its last\n6 points are all noise"),
    ]
    scale = 0.055
    for x, n, a, b, color, verdict, why in cases:
        small_a, small_b = a < cmin, b < cmin
        # the parent bar
        ax.fill_betweenx([2.30, 3.05], x - n * scale / 2, x + n * scale / 2,
                         color=color if not (small_a and small_b) else RED,
                         alpha=0.85, lw=0)
        ax.text(x, 3.14, f"{n}", ha="center", va="bottom", color=INK,
                fontsize=11.5)
        # and what becomes of its two sides
        for side, m, small in ((-1, a, small_a), (+1, b, small_b)):
            xc = x + side * 0.62
            ax.plot([x, xc], [2.30, 2.18], color=MUTED, lw=1.0)
            if small:
                rng = np.random.default_rng(abs(int(x * 10)) + side)
                ax.scatter(xc + rng.uniform(-0.17, 0.17, m),
                           1.85 + rng.uniform(-0.14, 0.14, m),
                           s=20, color=MUTED, edgecolors="none")
                ax.text(xc, 1.46, f"{m} → noise", ha="center", va="center",
                        color=MUTED, fontsize=10)
            else:
                ax.fill_betweenx([1.52, 2.18], xc - m * scale / 2,
                                 xc + m * scale / 2, color=color, alpha=0.85,
                                 lw=0)
                ax.text(xc, 1.40, f"{m}", ha="center", va="center", color=INK,
                        fontsize=11)
        ax.text(x, 1.02, verdict, ha="center", va="center", color=color,
                fontsize=12, weight="bold")
        ax.text(x, 0.64, why, ha="center", va="center", color=MUTED,
                fontsize=10.5, linespacing=1.6)

    for x in (3.05, 5.95):
        ax.plot([x, x], [0.40, 3.20], color=GRID, lw=1.0)
    note(ax, "Only the first case adds a branch.\n"
             "Condensed tree has (much) fewer then $n - 1$ branches.", y=0.20, size=11.5)


@figure("stability_idea")
def stability_idea(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "A cluster is stable if it holds many points "
                         r"over a long stretch of $\varepsilon$",
            ha="center", va="center", color=MUTED, fontsize=12.5)

    axL = fig.add_axes([0.07, 0.15, 0.38, 0.62])
    axL.set_xlim(0, 10)
    axL.set_ylim(3.2, 0)
    axL.set_xticks([])
    axL.set_ylabel(r"$\lambda = 1/\varepsilon$")
    despine(axL, keep=("left",))
    for x, lam0, lam1, w, color, name in (
        (2.6, 0.45, 2.85, 1.5, GREEN, "stable"),
        (7.0, 0.45, 0.95, 3.0, RED, "unstable"),
    ):
        axL.fill_betweenx([lam0, lam1], x - w / 2, x + w / 2, color=color,
                          alpha=0.30, lw=0)
        axL.plot([x - w / 2, x - w / 2], [lam0, lam1], color=color, lw=1.6)
        axL.plot([x + w / 2, x + w / 2], [lam0, lam1], color=color, lw=1.6)
        axL.text(x, lam0 - 0.12, name, ha="center", va="bottom", color=color,
                 fontsize=12)
        # how wide the bar is: how many points it holds
        axL.annotate("", xy=(x - w / 2, lam1 + 0.20),
                     xytext=(x + w / 2, lam1 + 0.20),
                     arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.1))
        axL.text(x, lam1 + 0.30, "points", ha="center", va="top", color=MUTED,
                 fontsize=10)
        # how tall it is: how long they stay
        xv = x - w / 2 - 0.45
        axL.annotate("", xy=(xv, lam0), xytext=(xv, lam1),
                     arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.1))
        if color is GREEN:
            axL.text(xv - 0.38, (lam0 + lam1) / 2, "how long they stay",
                     ha="center", va="center", color=MUTED, fontsize=10,
                     rotation=90)
    caption_row(fig, [axL], [r"area = points $\times$ how long they stay"],
                y=0.115)
    axL.set_title('"Stability" ~ area of the bar of a branch', pad=8, fontsize=12.5)

    cax = canvas(fig)
    cax.text(4.78, 2.96, r"$\mathrm{stability}(C) = \sum_{x_i \in C} "
                         r"\left(\lambda_i - \lambda_{\mathrm{birth}}(C)"
                         r"\right)$",
             color=INK, fontsize=15, va="center")
    cax.text(4.78, 2.40, r"$\lambda_{\mathrm{birth}}$: where the bar starts"
                         "\ni.e. the " r"$\varepsilon$ at which the cluster split off",
             color=MUTED, fontsize=10.5, va="center", linespacing=1.7)
    cax.text(4.78, 1.82, r"$\lambda_i$: where point $x_i$ leaves the bar"
                         "\ni.e. either falls out as noise, or splits",
             color=MUTED, fontsize=10.5, va="center", linespacing=1.7)


@figure("stability_example")
def stability_example(fig):
    ax = canvas(fig)
    lam_birth, lam_death = 0.8, 2.6
    leaves = [1.2, 1.5, 2.0]
    stay = 3
    ax.text(W / 2, 3.52, "one cluster of 6 points, born at "
                         rf"$\lambda_{{\mathrm{{birth}}}}$ = {lam_birth}",
            ha="center", va="center", color=MUTED, fontsize=12.5)

    axL = fig.add_axes([0.07, 0.17, 0.36, 0.60])
    axL.set_xlim(0, 10)
    axL.set_ylim(3.0, 0.3)
    axL.set_xticks([])
    axL.set_ylabel(r"$\lambda = 1/\varepsilon$")
    despine(axL, keep=("left",))
    width = [6, 5, 4, 3]
    edges = [lam_birth] + leaves + [lam_death]
    for y0, y1, m in zip(edges[:-1], edges[1:], width):
        axL.fill_betweenx([y0, y1], 5 - 0.42 * m, 5 + 0.42 * m, color=BLUE,
                          alpha=0.30, lw=0)
    for i, lam in enumerate(leaves):
        axL.plot([5 - 0.42 * width[i], 5 + 0.42 * width[i]], [lam, lam],
                 color=RED, lw=1.2)
        axL.plot(5 + 0.42 * width[i] + 0.5, lam, "o", color=RED, ms=5)
        axL.text(5 + 0.42 * width[i] + 0.9, lam,
                 rf"$x_{i + 1}$ leaves, $\lambda$ = {lam}", ha="left",
                 va="center", color=RED, fontsize=9.5)
    axL.axhline(lam_birth, color=MUTED, lw=1.2, ls="--")
    axL.axhline(lam_death, color=GREEN, lw=1.2, ls="--")
    axL.text(0.3, lam_death - 0.06, "the cluster splits: the last 3 leave here",
             ha="left", va="bottom", color=GREEN, fontsize=9.5)
    axL.set_title("when each point leaves the bar", pad=8, fontsize=12.5)

    cax = canvas(fig)
    rows = [(rf"$x_{i + 1}$", lam, lam - lam_birth, RED)
            for i, lam in enumerate(leaves)]
    cax.text(4.85, 3.00, "one term per point", color=BLUE, fontsize=12.5,
             weight="bold", va="center")
    y = 2.58
    for name, lam, contrib, color in rows:
        cax.text(4.85, y, f"{name}:", color=INK, fontsize=11.5, va="center")
        cax.text(5.35, y, rf"${lam} - {lam_birth} = {contrib:.1f}$",
                 color=color, fontsize=11.5, va="center")
        y -= 0.34
    cax.text(4.85, y, r"$x_4, x_5, x_6$:", color=INK, fontsize=11.5,
             va="center")
    cax.text(6.10, y, rf"$3 \times ({lam_death} - {lam_birth}) = "
                      rf"{3 * (lam_death - lam_birth):.1f}$",
             color=GREEN, fontsize=11.5, va="center")
    total = sum(r[2] for r in rows) + stay * (lam_death - lam_birth)
    cax.plot([4.85, 8.15], [y - 0.26, y - 0.26], color=GRID, lw=1.0)
    cax.text(4.85, y - 0.60, rf"$\mathrm{{stability}} = {total:.1f}$",
             color=INK, fontsize=15, va="center")
    cax.text(4.85, 0.46, "a point that leaves early contributes almost "
                         "nothing;\nthe ones that stay to the end contribute "
                         "the most",
             color=MUTED, fontsize=10.5, va="center", linespacing=1.7)


@figure("extract_example")
def extract_example(fig):
    ax = canvas(fig)

    nodes = {
        "root": (4.50, 2.80, 10, None),
        "A":    (2.15, 1.85, 6, None),
        "B":    (6.85, 1.85, 9, None),
        "A1":   (1.05, 0.90, 2, None),
        "A2":   (3.25, 0.90, 3, None),
        "B1":   (5.75, 0.90, 5, None),
        "B2":   (7.95, 0.90, 7, None),
    }
    kept = {"A", "B1", "B2"}
    dropped = {"A1", "A2"}
    edges = [("root", "A"), ("root", "B"), ("A", "A1"), ("A", "A2"),
             ("B", "B1"), ("B", "B2")]
    for a, b in edges:
        ax.plot([nodes[a][0], nodes[b][0]], [nodes[a][1] - 0.17,
                nodes[b][1] + 0.19], color=GRID, lw=1.2, zorder=1)
    for name, (x, y, stab, _) in nodes.items():
        color = GREEN if name in kept else (GRID if name in dropped else MUTED)
        box(ax, x - 0.55, y - 0.17, 1.10, 0.36, color, "", fill="white",
            lw=2.4 if name in kept else 1.4)
        ax.text(x, y, f"{name}:  {stab}", ha="center", va="center",
                color=color if name in kept else INK, fontsize=11,
                weight="bold" if name in kept else "normal")

    ax.text(0.10, 2.52, r"$2 + 3 < 6$", color=RED, fontsize=11.5, va="center")
    ax.text(0.10, 2.24, "the children lose:\nkeep $A$, and drop\nthe two below "
                        "it", color=MUTED, fontsize=10, va="top",
            linespacing=1.6)
    ax.text(8.90, 2.52, r"$5 + 7 > 9$", color=GREEN, fontsize=11.5,
            va="center", ha="right")
    ax.text(8.90, 2.24, "the children win:\nkeep $B_1$ and $B_2$,\nand drop "
                        "$B$", color=MUTED, fontsize=10, va="top", ha="right",
            linespacing=1.6)
    ax.text(4.50, 3.22, r"$6 + 5 + 7 > 10$", color=GREEN, fontsize=11.5,
            ha="center", va="center")
    note(ax, r"$\rightarrow$ three clusters: $A$, $B_1$, $B_2$ "
             "(everything else is noise)", y=0.14, size=12, color=GREEN)


@figure("hdbscan_result")
def hdbscan_result(fig):
    from sklearn.cluster import DBSCAN, HDBSCAN

    X = _density_data(seed=4)
    axes = fig.subplots(
        1, 3,
        gridspec_kw=dict(left=0.04, right=0.98, top=0.80, bottom=0.26, wspace=0.10),
    )
    runs = [
        (DBSCAN(eps=0.18, min_samples=5).fit_predict(X),
         r"DBSCAN, $\varepsilon$ = 0.18", RED,
         "sparse cluster is gone"),
        (DBSCAN(eps=1.00, min_samples=5).fit_predict(X),
         r"DBSCAN, $\varepsilon$ = 1.00", RED,
         "sparse cluster contains noise\nand is merged with another cluster"),
        (HDBSCAN(min_cluster_size=10).fit_predict(X),
         r"HDBSCAN, $C_{\min}$ = 10", GREEN,
         "looks correct"),
    ]
    for ax, (labels, title, color, cap) in zip(axes, runs):
        _scatter_clusters(ax, X, labels, s=12)
        n = len(set(labels) - {-1})
        ax.set_title(f"{title}\n{_plural(n, 'cluster')}, "
                     f"{(labels == -1).sum()} noise",
                     color=color, pad=8, fontsize=12, linespacing=1.8)
        ax.set_aspect("equal")
        _bare(ax)
    caption_row(fig, axes, [r[3] for r in runs], y=0.155)


@figure("hdbscan_props")
def hdbscan_props(fig):
    ax = canvas(fig)
    column(ax, 0.55, 3.25, 3.9, "Pros", [
        r"two parameters, MinPts and $C_{\min}$," "\n"
        r"(easier to tune than $\varepsilon$)",
        "clusters at varying densities",
        "robust to outliers",
    ], GREEN, leading=0.32)
    column(ax, 4.90, 3.25, 3.9, "Cons", [
        "more machinery",
        "more compute",
        "suffers in high dimension",
    ], RED, leading=0.32)
    ax.plot([4.65, 4.65], [0.80, 3.35], color=GRID, lw=1.2)
    note(ax, "HDBSCAN is the default choice when density varies.",
         y=0.42)


# ==========================================================================
# 8. Putting it together
# ==========================================================================
@figure("algo_compare")
def algo_compare(fig):
    from sklearn.cluster import DBSCAN, HDBSCAN, AgglomerativeClustering, KMeans
    from sklearn.datasets import make_blobs, make_circles, make_moons
    from sklearn.preprocessing import StandardScaler

    rng = np.random.default_rng(0)
    moons, _ = make_moons(300, noise=0.06, random_state=0)
    circles, _ = make_circles(300, noise=0.05, factor=0.45, random_state=0)
    aniso_X, aniso_y = make_blobs(300, random_state=170)
    aniso = aniso_X @ np.array([[0.6, -0.6], [-0.4, 0.8]])
    varied, _ = make_blobs(300, cluster_std=[1.0, 2.5, 0.5], random_state=170)
    datasets = [("moons", moons, 2, 0.26), ("rings", circles, 2, 0.40),
                ("anisotropic", aniso, 3, 0.26), ("unequal spreads", varied, 3, 0.35)]
    methods = [("k-means", BLUE), ("Ward", PURPLE), ("DBSCAN", GOLD),
               ("HDBSCAN", GREEN), ("subtractive", RED)]

    axes = fig.subplots(
        5, 4,
        gridspec_kw=dict(left=0.14, right=0.99, top=0.86, bottom=0.02,
                         wspace=0.08, hspace=0.10),
    )
    for col, (name, X, k, eps) in enumerate(datasets):
        X = StandardScaler().fit_transform(X)
        preds = [
            KMeans(k, n_init=10, random_state=0).fit_predict(X),
            AgglomerativeClustering(k, linkage="ward").fit_predict(X),
            DBSCAN(eps=eps, min_samples=8).fit_predict(X),
            HDBSCAN(min_cluster_size=10).fit_predict(X),
            _subtractive(X, 1.2)[0],
        ]
        for row, labels in enumerate(preds):
            ax = axes[row, col]
            _scatter_clusters(ax, X, labels, s=4)
            ax.set_aspect("equal")
            _bare(ax)
        axes[0, col].set_title(name, pad=6, fontsize=11.5)
    for row, (name, color) in enumerate(methods):
        pos = axes[row, 0].get_position(original=True)
        fig.text(0.125, (pos.y0 + pos.y1) / 2, name, ha="right", va="center",
                 color=color, fontsize=10.5)
    fig.text(0.5, 0.965, "no method wins everywhere", ha="center", color=MUTED, fontsize=12)


@figure("clustering_map")
def clustering_map(fig):
    ax = canvas(fig)
    rows = [
        ("k-means", BLUE, "K", "spherical, similar size", "fast"),
        ("hierarchical", PURPLE, "cut height", "whatever the linkage favours",
         "dendrogram to read"),
        ("subtractive", RED, r"$r_a$", "one blob per peak of density",
         "Auto-detects K"),
        ("DBSCAN", GOLD, r"$\varepsilon$, MinPts", "any shape, one density",
         "noise labelled"),
        ("HDBSCAN", GREEN, r"MinPts, $C_{\min}$", "any shape, any density",
         "default when unsure"),
    ]
    x = (0.55, 2.60, 4.20, 6.55)
    headers = ("Method", "Parameters", "Good with", "Benefits")
    for xi, head in zip(x, headers):
        ax.text(xi, 3.32, head, color=MUTED, fontsize=11.5, va="center")
    ax.plot([0.45, 8.55], [3.12, 3.12], color=GRID, lw=1.2)
    for i, (name, color, param, shapes, why) in enumerate(rows):
        y = 2.88 - i * 0.56
        ax.text(x[0], y, name, color=color, fontsize=13, weight="bold",
                va="center")
        ax.text(x[1], y, param, color=INK, fontsize=12, va="center")
        ax.text(x[2], y, shapes, color=INK, fontsize=12, va="center")
        ax.text(x[3], y, why, color=INK, fontsize=12, va="center")
        if i:
            ax.plot([0.45, 8.55], [y + 0.28, y + 0.28], color=LIGHT, lw=1.0)


# ==========================================================================
def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course04/img")
    out.mkdir(parents=True, exist_ok=True)
    wanted = argv[2:] or sorted(FIGURES)
    for stem in wanted:
        if stem not in FIGURES:
            raise SystemExit(f"unknown figure: {stem}")
        fig = plt.figure(figsize=(W, H), dpi=DPI)
        FIGURES[stem](fig)
        fig.savefig(out / f"{stem}.png", dpi=DPI)
        plt.close(fig)
        print(f"  {stem}.png")


if __name__ == "__main__":
    main(sys.argv)
