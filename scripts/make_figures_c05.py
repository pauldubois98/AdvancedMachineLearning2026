#!/usr/bin/env python3
"""Every figure of Course05 (non-negative matrix factorization).

One function per figure, registered under the stem the slide deck asks for.
All figures share one canvas (9 x 3.7075 in), which is exactly the content
area pandoc leaves under a slide title, so a figure never has to be resized.

    python3 scripts/make_figures_c05.py Course05/img [stem ...]
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
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
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
# a non-negative matrix is always drawn with the same ramp: white is zero
NN_CMAP = LinearSegmentedColormap.from_list("nn", ["#ffffff", "#cfe0f1", BLUE])
W_CMAP = LinearSegmentedColormap.from_list("wm", ["#ffffff", "#e2d9f5", PURPLE])
H_CMAP = LinearSegmentedColormap.from_list("hm", ["#ffffff", "#f0e2c8", GOLD])


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


def caption_row(fig, axes, texts, y=0.085, color=MUTED, size=11):
    """Captions pinned to the figure, so an equal-aspect panel cannot move them."""
    for ax, text in zip(np.atleast_1d(axes), texts):
        pos = ax.get_position(original=True)
        fig.text((pos.x0 + pos.x1) / 2, y, text, ha="center", va="top",
                 color=color, fontsize=size)


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
    ax.text(x, y, title, color=color, fontsize=title_size, weight="bold",
            ha="left", va="top")
    yy = y - 0.42
    for item in items:
        ax.text(x, yy, bullet, color=color, fontsize=item_size, ha="left", va="top")
        ax.text(x + 0.22, yy, item, color=INK, fontsize=item_size, ha="left",
                va="top", wrap=True)
        yy -= leading * (1 + item.count("\n"))
    return yy


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


def steps(ax, rows, top=3.02, gap=0.74, x=0.55, eq_size=12.5, why_size=10.5,
          eq_color=None, why_off=0.36):
    """The deck's derivation layout: an equation, then the grey line that
    justifies it, repeated down the slide."""
    for i, row in enumerate(rows):
        eq, why = row[0], row[1]
        color = row[2] if len(row) > 2 else (eq_color or INK)
        y = top - i * gap
        ax.text(x, y, eq, color=color, fontsize=eq_size, va="center")
        if why:
            ax.text(x, y - why_off, why, color=MUTED, fontsize=why_size,
                    va="center")


def despine(ax, keep=()):
    for side in ("top", "right", "left", "bottom"):
        if side not in keep:
            ax.spines[side].set_visible(False)


def blank(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    despine(ax)


def _bare(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def _credit(fig, text):
    fig.text(0.985, 0.012, text, ha="right", va="bottom", color=MUTED, fontsize=8)


def _matrix(ax, x, y, w, h, color, cmap, M=None, label=None, shape=None,
            lw=2.0, label_size=13, seed=0, nrow=9, ncol=9, vmax=None):
    """A matrix drawn as a filled rectangle of cells, with its name above and
    its shape below.  Coordinates are the inches of `canvas()`."""
    if M is None:
        rng = np.random.default_rng(seed)
        M = rng.random((nrow, ncol)) ** 1.4
    ax.imshow(M, cmap=cmap, extent=(x, x + w, y, y + h), aspect="auto",
              vmin=0, vmax=vmax, zorder=2, interpolation="nearest")
    ax.add_patch(Rectangle((x, y), w, h, facecolor="none", edgecolor=color,
                           lw=lw, zorder=3))
    if label:
        ax.text(x + w / 2, y + h + 0.22, label, ha="center", va="center",
                color=color, fontsize=label_size)
    if shape:
        ax.text(x + w / 2, y - 0.22, shape, ha="center", va="center",
                color=MUTED, fontsize=10.5)


# ==========================================================================
# the algorithms, written out once: every "measured" slide runs these
# ==========================================================================
EPS = 1e-10
CACHE = Path(__file__).resolve().parent.parent / ".cache" / "datasets" / "sklearn"


def _init(X, r, seed=0, how="random"):
    """The initializations the deck discusses, as (W, H)."""
    p, n = X.shape
    if how == "nndsvd":
        U, s, Vt = np.linalg.svd(X, full_matrices=False)
        Wi, Hi = np.zeros((p, r)), np.zeros((r, n))
        Wi[:, 0] = np.sqrt(s[0]) * np.abs(U[:, 0])
        Hi[0] = np.sqrt(s[0]) * np.abs(Vt[0])
        for k in range(1, r):
            u, v = U[:, k], Vt[k]
            up, un = np.maximum(u, 0), np.maximum(-u, 0)
            vp, vn = np.maximum(v, 0), np.maximum(-v, 0)
            np_, nn_ = np.linalg.norm(up) * np.linalg.norm(vp), \
                np.linalg.norm(un) * np.linalg.norm(vn)
            if np_ >= nn_:
                Wi[:, k] = np.sqrt(s[k] * np_) * up / (np.linalg.norm(up) + EPS)
                Hi[k] = np.sqrt(s[k] * np_) * vp / (np.linalg.norm(vp) + EPS)
            else:
                Wi[:, k] = np.sqrt(s[k] * nn_) * un / (np.linalg.norm(un) + EPS)
                Hi[k] = np.sqrt(s[k] * nn_) * vn / (np.linalg.norm(vn) + EPS)
        return np.maximum(Wi, 1e-4), np.maximum(Hi, 1e-4)
    if how == "constant":
        scale = np.sqrt(max(X.mean(), EPS) / r)
        return np.full((p, r), scale), np.full((r, n), scale)
    if how == "cols":
        rng = np.random.default_rng(seed)
        idx = rng.choice(n, size=r, replace=False)
        Wi = np.maximum(X[:, idx].copy(), 1e-4)
        Hi = (0.5 + rng.random((r, n))) / r
        return Wi, Hi
    if how == "kmeans":
        from sklearn.cluster import KMeans
        km = KMeans(n_clusters=r, n_init=10, random_state=seed).fit(X.T)
        Wi = np.maximum(km.cluster_centers_.T, 1e-4)
        Hi = np.full((r, n), 1e-2)
        Hi[km.labels_, np.arange(n)] = 1.0
        return Wi, Hi
    rng = np.random.default_rng(seed)
    scale = np.sqrt(X.mean() / r) if X.mean() > 0 else 1.0
    return rng.random((p, r)) * scale + 1e-3, rng.random((r, n)) * scale + 1e-3


def _fro(X, Wm, Hm, mask=None):
    R = X - Wm @ Hm
    if mask is not None:
        R = mask * R
    return 0.5 * float((R ** 2).sum())


def _kl(X, Wm, Hm):
    Y = np.maximum(Wm @ Hm, EPS)
    Xp = np.maximum(X, EPS)
    return float((X * np.log(Xp / Y) - X + Y).sum())


def _mu(X, r=4, iters=200, seed=0, loss="fro", init="random", mask=None,
        mu=0.0, lam=0.0, nu=0.0, W0=None, H0=None, trace=False):
    """Lee and Seung's multiplicative updates, with the weighted and
    regularized variants the deck derives.  Returns (W, H) or the loss trace."""
    Wm, Hm = _init(X, r, seed, init) if W0 is None else (W0.copy(), H0.copy())
    Ir = np.eye(r)
    hist = []
    for _ in range(iters):
        if loss == "kl":
            Y = np.maximum(Wm @ Hm, EPS)
            Hm *= (Wm.T @ (X / Y)) / np.maximum(Wm.sum(0)[:, None], EPS)
            Y = np.maximum(Wm @ Hm, EPS)
            Wm *= ((X / Y) @ Hm.T) / np.maximum(Hm.sum(1)[None, :], EPS)
        elif mask is not None:
            Hm *= (Wm.T @ (mask * X)) / np.maximum(Wm.T @ (mask * (Wm @ Hm)), EPS)
            Wm *= ((mask * X) @ Hm.T) / np.maximum((mask * (Wm @ Hm)) @ Hm.T, EPS)
        else:
            num = np.maximum(Wm.T @ X - lam, 0.0)
            Hm *= num / np.maximum((Wm.T @ Wm + mu * Ir) @ Hm, EPS)
            Wm *= (X @ Hm.T) / np.maximum(Wm @ (Hm @ Hm.T + nu * Ir), EPS)
        if trace:
            hist.append(_kl(X, Wm, Hm) if loss == "kl" else _fro(X, Wm, Hm, mask))
    return (Wm, Hm, np.array(hist)) if trace else (Wm, Hm)


def _als(X, r=4, iters=200, seed=0, init="random", trace=False):
    """Unconstrained least squares, then a projection onto the orthant."""
    Wm, Hm = _init(X, r, seed, init)
    hist = []
    for _ in range(iters):
        Hm = np.maximum(np.linalg.lstsq(Wm, X, rcond=None)[0], 0.0)
        Wm = np.maximum(np.linalg.lstsq(Hm.T, X.T, rcond=None)[0].T, 0.0)
        Wm = np.maximum(Wm, EPS)
        Hm = np.maximum(Hm, EPS)
        if trace:
            hist.append(_fro(X, Wm, Hm))
    return (Wm, Hm, np.array(hist)) if trace else (Wm, Hm)


def _hals(X, r=4, iters=200, seed=0, init="random", trace=False):
    """Exact coordinate descent: one column of W, one row of H at a time."""
    Wm, Hm = _init(X, r, seed, init)
    hist = []
    for _ in range(iters):
        A, B = X @ Hm.T, Hm @ Hm.T
        for k in range(r):
            wk = Wm[:, k] + (A[:, k] - Wm @ B[:, k]) / max(B[k, k], EPS)
            Wm[:, k] = np.maximum(wk, EPS)
        C, Dm = Wm.T @ X, Wm.T @ Wm
        for k in range(r):
            hk = Hm[k] + (C[k] - Dm[k] @ Hm) / max(Dm[k, k], EPS)
            Hm[k] = np.maximum(hk, EPS)
        if trace:
            hist.append(_fro(X, Wm, Hm))
    return (Wm, Hm, np.array(hist)) if trace else (Wm, Hm)


def _order(Wm, Hm):
    """Components sorted by how much of X they explain, so a redraw is stable."""
    energy = np.linalg.norm(Wm, axis=0) * np.linalg.norm(Hm, axis=1)
    idx = np.argsort(-energy)
    return Wm[:, idx], Hm[idx]


# --------------------------------------------------------------------------
# the data the applications run on
# --------------------------------------------------------------------------
def _faces(n=300):
    from sklearn.datasets import fetch_olivetti_faces

    d = fetch_olivetti_faces(data_home=CACHE)
    return d.images[:n], d.data[:n]


def _topics(n_words=1200):
    from sklearn.datasets import fetch_20newsgroups
    from sklearn.feature_extraction.text import TfidfVectorizer

    groups = ["sci.space", "rec.sport.hockey", "comp.graphics", "talk.politics.mideast"]
    d = fetch_20newsgroups(subset="train", categories=groups, data_home=CACHE,
                           remove=("headers", "footers", "quotes"))
    tf = TfidfVectorizer(max_features=n_words, stop_words="english",
                         min_df=5, max_df=0.5)
    T = tf.fit_transform(d.data).toarray()
    return T.T, np.array(tf.get_feature_names_out()), np.array(d.target), \
        list(d.target_names)


def _spectral_toy(seed=1, size=44):
    """A tiny hyperspectral scene: three materials, each with its own spectrum,
    mixed inside every pixel.  X is (bands x pixels), non-negative by physics.
    The three spectra peak in different parts of the range and every material
    covers a region of its own, so the factorization is identifiable."""
    rng = np.random.default_rng(seed)
    bands = np.linspace(0.4, 2.4, 60)
    spectra = np.maximum(np.c_[
        0.04 + 0.75 * np.exp(-((bands - 0.75) / 0.16) ** 2),        # vegetation
        0.03 + 0.70 / (1 + np.exp(-(bands - 1.60) * 6.0)),          # roof
        np.maximum(0.70 - 0.30 * bands, 0.02)
        + 0.55 * np.exp(-((bands - 1.95) / 0.10) ** 2),             # soil
    ], 0.01)
    yy, xx = np.mgrid[0:size, 0:size] / (size - 1)
    fields = np.stack([
        np.exp(-(((xx - 0.24) / 0.22) ** 2 + ((yy - 0.70) / 0.20) ** 2)),
        np.exp(-(((xx - 0.74) / 0.16) ** 2 + ((yy - 0.26) / 0.15) ** 2)),
        0.30 + 0.0 * xx,
    ])
    maps = fields ** 5
    maps = maps / maps.sum(0, keepdims=True)
    Hm = maps.reshape(3, -1)
    X = spectra @ Hm
    X = np.maximum(X + rng.normal(0, 0.002, X.shape), 1e-4)
    return bands, spectra, maps, X, size


def _music_toy(seed=2):
    """Three notes, struck at different times: a power spectrogram is
    non-negative, and the mixture adds up in power."""
    freqs = np.linspace(0, 1, 70)
    notes = np.c_[
        np.exp(-((freqs - 0.14) / 0.015) ** 2) + 0.45 * np.exp(-((freqs - 0.28) / 0.018) ** 2)
        + 0.2 * np.exp(-((freqs - 0.42) / 0.02) ** 2),
        np.exp(-((freqs - 0.22) / 0.015) ** 2) + 0.40 * np.exp(-((freqs - 0.44) / 0.018) ** 2)
        + 0.18 * np.exp(-((freqs - 0.66) / 0.02) ** 2),
        np.exp(-((freqs - 0.33) / 0.016) ** 2) + 0.35 * np.exp(-((freqs - 0.66) / 0.02) ** 2),
    ]
    t = np.linspace(0, 1, 120)
    env = np.stack([
        np.exp(-np.maximum(t - 0.05, 0) * 11) * (t > 0.05),
        np.exp(-np.maximum(t - 0.35, 0) * 9) * (t > 0.35),
        np.exp(-np.maximum(t - 0.60, 0) * 7) * (t > 0.60)
        + np.exp(-np.maximum(t - 0.18, 0) * 12) * (t > 0.18),
    ])
    rng = np.random.default_rng(seed)
    X = notes @ env
    X = np.maximum(X * np.exp(rng.normal(0, 0.25, X.shape)), 1e-4)
    return freqs, notes, env, t, X


def _layers_fit(seed=7, p=18, n=28, r=3):
    """A small non-negative matrix built from r rank-one layers, and the HALS
    factorization of it: the pictures of the HALS slides all share these."""
    rng = np.random.default_rng(seed)
    u, v = np.linspace(0, 1, p), np.linspace(0, 1, n)
    Wt = np.stack([np.exp(-((u - c) / 0.15) ** 2)
                   for c in (0.22, 0.52, 0.80)], 1)
    Ht = np.stack([np.exp(-((v - c) / 0.12) ** 2)
                   for c in (0.25, 0.58, 0.84)])
    X = np.maximum(Wt @ Ht + rng.normal(0, 0.02, (p, n)), 1e-4)
    Wm, Hm = _order(*_hals(X, r, 400))
    return X, Wm, Hm


def _ratings_toy(seed=5, n_users=60, n_items=24, r=3, hide=0.55):
    """A user-by-item table built from r tastes, then mostly hidden."""
    rng = np.random.default_rng(seed)
    taste = rng.random((n_users, r)) ** 1.6
    profile = rng.random((r, n_items)) ** 1.3
    base = 1 + 4 * (taste @ profile) / (taste @ profile).max()
    full = np.clip(np.round(base + rng.normal(0, 0.45, base.shape)), 1, 5)
    mask = (rng.random(full.shape) > hide).astype(float)
    return full.T, mask.T


# ==========================================================================
# 1. a matrix as a product
# ==========================================================================
@figure("factorization_idea")
def factorization_idea(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "The table is big; the thing it describes may be small",
            ha="center", va="center", color=MUTED, fontsize=12.5)

    _matrix(ax, 1.65, 1.05, 1.85, 2.05, BLUE, NN_CMAP, label=r"$X$",
            shape=r"$p \times n$", seed=3, nrow=16, ncol=14)
    ax.text(2.58, 0.55, "4096 pixels × 400 faces\n= 1 638 400 numbers",
            ha="center", va="center", color=BLUE, fontsize=10.5, linespacing=1.5)

    ax.text(3.95, 2.05, "≈", ha="center", va="center", color=MUTED, fontsize=26)

    _matrix(ax, 4.40, 1.05, 0.72, 2.05, PURPLE, W_CMAP, label=r"$W$",
            shape=r"$p \times r$", seed=5, nrow=16, ncol=5)
    ax.text(5.32, 2.05, "·", ha="center", va="center", color=MUTED, fontsize=26)
    _matrix(ax, 5.55, 2.38, 1.85, 0.72, GOLD, H_CMAP, label=r"$H$",
            shape=r"$r \times n$", seed=7, nrow=5, ncol=14)
    ax.text(6.00, 1.55, r"$r = 16$" "\n" "4096 × 16  +  16 × 400\n= 71 936 numbers",
            ha="center", va="center", color=PURPLE, fontsize=10.5, linespacing=1.5)
    note(ax, r"a low-rank model: $\mathrm{rank}(WH) \leq r < \min(p, n)$", y=0.18)


@figure("eq_factorization")
def eq_factorization(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"Given $x_j \in \mathbb{R}^p$ for $1 \leq j \leq n$, and a "
                         r"target dimension $r < \min(p, n)$",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 2.92, r"find $r$ basis elements $w_k \in \mathbb{R}^p$ and "
                         r"weights $h_j \in \mathbb{R}^r$ such that",
            ha="center", va="center", color=MUTED, fontsize=12.5)

    ax.text(W / 2, 2.25, r"$x_j \approx \sum_{k=1}^{r} w_k\, h_j(k)$",
            ha="center", va="center", color=INK, fontsize=22)
    ax.text(W / 2, 1.50, "equivalently", ha="center", va="center", color=MUTED,
            fontsize=11.5)
    ax.text(W / 2, 1.08, r"$X \approx W H$", ha="center", va="center", color=INK,
            fontsize=26)

    rows = [
        (BLUE, r"$X \in \mathbb{R}^{p \times n}$", r"$X(:, j) = x_j$", "the data"),
        (PURPLE, r"$W \in \mathbb{R}^{p \times r}$", r"$W(:, k) = w_k$",
         "the dictionary"),
        (GOLD, r"$H \in \mathbb{R}^{r \times n}$", r"$H(:, j) = h_j$",
         "the codes"),
    ]
    for i, (color, shape, which, name) in enumerate(rows):
        y = 0.62 - i * 0.0
        x = 1.05 + i * 2.60
        ax.text(x, 0.52, shape, ha="left", va="center", color=color, fontsize=12)
        ax.text(x, 0.20, f"{which},   {name}", ha="left", va="center",
                color=MUTED, fontsize=10)


@figure("factorization_columns")
def factorization_columns(fig):
    rng = np.random.default_rng(11)
    atoms = np.array([
        np.exp(-((np.arange(14) - 2.5) / 1.6) ** 2),
        np.exp(-((np.arange(14) - 7.0) / 1.3) ** 2) * 0.9,
        np.exp(-((np.arange(14) - 11.5) / 2.0) ** 2) * 0.8,
    ])
    weights = np.array([0.9, 0.35, 0.6])
    col = weights @ atoms

    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Every column of the table is the same few parts, "
                         "in different amounts",
            ha="center", va="center", color=MUTED, fontsize=12.5)

    def strip(x, y, v, color, cmap, h=1.90, w=0.46):
        ax.imshow(v[:, None][::-1], cmap=cmap, extent=(x, x + w, y, y + h),
                  aspect="auto", vmin=0, vmax=1.0, interpolation="nearest")
        ax.add_patch(Rectangle((x, y), w, h, facecolor="none", edgecolor=color,
                               lw=1.8))

    strip(0.70, 1.00, col, BLUE, NN_CMAP)
    ax.text(0.93, 3.08, r"$x_j$", ha="center", va="center", color=BLUE,
            fontsize=14)
    ax.text(0.93, 0.74, "one face,\none document,\none pixel",
            ha="center", va="center", color=MUTED, fontsize=9.5, linespacing=1.4)

    ax.text(1.62, 1.95, "≈", ha="center", va="center", color=MUTED, fontsize=24)
    x = 2.15
    for k in range(3):
        ax.text(x, 1.95, f"{weights[k]:.2f}", ha="center", va="center",
                color=GOLD, fontsize=14)
        ax.text(x, 2.42, f"$h_j({k+1})$", ha="center", va="center", color=GOLD,
                fontsize=11)
        ax.text(x + 0.44, 1.95, "×", ha="center", va="center", color=MUTED,
                fontsize=15)
        strip(x + 0.66, 1.00, atoms[k], PURPLE, W_CMAP)
        ax.text(x + 0.89, 3.08, f"$w_{k+1}$", ha="center", va="center",
                color=PURPLE, fontsize=14)
        if k < 2:
            ax.text(x + 1.42, 1.95, "+", ha="center", va="center", color=MUTED,
                    fontsize=20)
        x += 1.95

    ax.text(7.40, 1.95, r"$w_k$: the same for" "\n" r"every column $j$",
            ha="left", va="center", color=PURPLE, fontsize=10.5, linespacing=1.5)
    ax.text(7.40, 1.25, r"$h_j$: $r$ numbers," "\n" "one column at a time",
            ha="left", va="center", color=GOLD, fontsize=10.5, linespacing=1.5)
    note(ax, r"$h_j$ is the new, $r$-dimensional description of $x_j$", y=0.22)


@figure("key_aspects")
def key_aspects(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Goal: a low-rank approximation", ha="center",
            va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 3.10, r"$X \approx W H$", ha="center", va="center",
            color=INK, fontsize=19)

    cards = [
        (0.35, BLUE, "1.  How good is the\napproximation?",
         "Frobenius, Kullback–Leibler,\nItakura–Saito, logistic, …",
         "→  a loss function"),
        (3.20, PURPLE, r"2.  What shape must" "\n" r"$W$ and $H$ have?",
         "orthogonality, independence,\nsparsity, normalisation, …",
         "→  non-negativity"),
        (6.05, GREEN, "3.  How do we find\nthem?",
         "the problem has no formula\nfor its solution",
         "→  an algorithm"),
    ]
    for x, color, head, body, out in cards:
        box(ax, x, 1.05, 2.60, 1.75, color, "", fill="white")
        ax.text(x + 1.30, 2.52, head, ha="center", va="center", color=color,
                fontsize=12.5, weight="bold", linespacing=1.4)
        ax.text(x + 1.30, 1.90, body, ha="center", va="center", color=INK,
                fontsize=10.5, linespacing=1.5)
        ax.text(x + 1.30, 1.32, out, ha="center", va="center", color=color,
                fontsize=11.5)

    note(ax, r"NMF:  find $(W, H)$ with $X \approx W H$, "
             r"$\;W \geq 0$, $\;H \geq 0$ — questions 1 and 2 are this "
             r"slide, question 3 is the rest of the deck",
         y=0.52, size=11.5)


@figure("why_nonneg")
def why_nonneg(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"$W \geq 0$ and $H \geq 0$ are read entry by entry",
            ha="center", va="center", color=MUTED, fontsize=12.5)

    # the picture: signed combinations can cancel, non-negative ones cannot
    x = np.linspace(0, 1, 120)
    a = np.exp(-((x - 0.3) / 0.12) ** 2)
    b = np.exp(-((x - 0.5) / 0.12) ** 2)
    ax1 = fig.add_axes([0.06, 0.30, 0.26, 0.42])
    ax1.plot(x, a, color=MUTED, lw=1.4)
    ax1.plot(x, b, color=MUTED, lw=1.4, ls="--")
    ax1.plot(x, 1.6 * a - 1.4 * b, color=RED, lw=2.4)
    ax1.axhline(0, color=GRID, lw=1.0)
    ax1.set_title("signed: parts cancel", color=RED, fontsize=11.5, pad=6)
    _bare(ax1)

    ax2 = fig.add_axes([0.37, 0.30, 0.26, 0.42])
    ax2.plot(x, a, color=MUTED, lw=1.4)
    ax2.plot(x, b, color=MUTED, lw=1.4, ls="--")
    ax2.plot(x, 0.8 * a + 0.6 * b, color=GREEN, lw=2.4)
    ax2.axhline(0, color=GRID, lw=1.0)
    ax2.set_ylim(ax1.get_ylim())
    ax2.set_title("non-negative: parts only add", color=GREEN, fontsize=11.5,
                  pad=6)
    _bare(ax2)
    caption_row(fig, [ax1, ax2],
                ["component can mean \"undo that\"",
                 "component is a piece of the whole"], y=0.26)

    ax.plot([6.05, 6.05], [0.70, 3.25], color=GRID, lw=1.2)
    column(ax, 6.30, 3.20, 2.5, "Inherent positive cases:", [
        "pixel intensities",
        "word counts",
        "spectra, power",
        "prices, ratings, durations",
    ], BLUE, leading=0.28, item_size=11)
    ax.text(6.30, 1.42, "data is already " r"$\geq 0$:", color=MUTED,
            fontsize=10.5, va="top")


@figure("nmf_vs_pca")
def nmf_vs_pca(fig):
    n_faces = 300
    imgs, Xf = _faces(n_faces)
    X = Xf.T
    r = 16
    U, sv, Vt = np.linalg.svd(X, full_matrices=False)
    Wn, Hn = _hals(X, r, 300, init="nndsvd")
    Wn, Hn = _order(Wn, Hn)
    # both are rank r, and both are scored against the same X
    err_p = float(np.linalg.norm(X - U[:, :r] * sv[:r] @ Vt[:r])
                  / np.linalg.norm(X))
    err_n = float(np.linalg.norm(X - Wn @ Hn) / np.linalg.norm(X))

    lim = float(np.abs(U[:, 1:6]).max())
    for k in range(5):
        a = fig.add_axes([0.085 + k * 0.102, 0.49, 0.093, 0.30])
        a.imshow(U[:, k + 1].reshape(64, 64), cmap="RdBu_r", vmin=-lim,
                 vmax=lim, interpolation="nearest")
        _bare(a)
        b = fig.add_axes([0.085 + k * 0.102, 0.15, 0.093, 0.30])
        b.imshow(Wn[:, k].reshape(64, 64), cmap="gray_r",
                 interpolation="nearest")
        _bare(b)
    fig.text(0.078, 0.64, "PCA", ha="right", va="center", color=BLUE,
             fontsize=13, weight="bold")
    fig.text(0.078, 0.30, "NMF", ha="right", va="center", color=GREEN,
             fontsize=13, weight="bold")
    fig.text(0.078, 0.56, "signed", ha="right", va="center", color=MUTED,
             fontsize=10)
    fig.text(0.078, 0.22, r"all $\geq 0$", ha="right", va="center",
             color=MUTED, fontsize=10)

    side = fig.add_axes([0.63, 0.12, 0.35, 0.70])
    side.axis("off")
    side.text(0, 0.9, "red adds, blue subtracts", color=BLUE, fontsize=12.5,
              weight="bold", va="top")
    side.text(0, 0.4, "nothing to subtract", color=GREEN, fontsize=12.5,
              weight="bold", va="top")
    side.text(0, 0.16, f"at the same rank $r = {r}$, the PCA\nfits better "
                       f"({100 * err_p:.1f}% against {100 * err_n:.1f}%)",
              color=MUTED, fontsize=10, va="top", linespacing=1.5)
    fig.text(0.34, 0.945, f"{n_faces} faces — five components each",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    _credit(fig, "data: Olivetti faces, AT&T Cambridge")


# ==========================================================================
# 2. what it is used for
# ==========================================================================
def _strip(ax, x, y, v, color, cmap, h=1.80, w=0.44):
    """One column of a matrix, drawn as a tall strip of cells."""
    v = np.asarray(v, float)
    v = v / (v.max() + EPS)
    ax.imshow(v[:, None][::-1], cmap=cmap, extent=(x, x + w, y, y + h),
              aspect="auto", vmin=0, vmax=1.0, interpolation="nearest",
              zorder=2)
    ax.add_patch(Rectangle((x, y), w, h, facecolor="none", edgecolor=color,
                           lw=1.8, zorder=3))


@figure("setup_faces")
def setup_faces(fig):
    imgs, Xf = _faces(400)
    Wm, _ = _mu(Xf.T, 36, 250, init="nndsvd")
    # the most localized of the parts: smallest L1/L2 ratio
    sparsity = np.abs(Wm).sum(0) / (np.linalg.norm(Wm, axis=0) + EPS)
    part = Wm[:, int(np.argmin(sparsity))].reshape(64, 64)

    ax = canvas(fig)
    ax.text(W / 2, 3.52, "What the three matrices hold, for faces",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    for x in (3.05, 6.05):
        ax.plot([x, x], [0.72, 3.15], color=LIGHT, lw=1.2)

    ax.text(1.50, 3.00, r"a column of $X$", ha="center", va="center",
            color=BLUE, fontsize=13)
    axf = fig.add_axes([0.040, 0.335, 0.115, 0.41])
    axf.imshow(imgs[6], cmap="gray", interpolation="nearest")
    _bare(axf)
    arrow(ax, (1.58, 1.95), (2.00, 1.95), color=MUTED, lw=1.5)
    ax.text(1.79, 2.22, "stack the\npixels", ha="center", va="center",
            color=MUTED, fontsize=9, linespacing=1.3)
    _strip(ax, 2.26, 1.08, Xf[6], BLUE, NN_CMAP, h=1.70)
    ax.text(2.48, 2.98, r"$x_j$", ha="center", va="center", color=BLUE,
            fontsize=12)
    ax.text(1.50, 0.82, "one face = 4096 pixel values,\nwritten as one tall column",
            ha="center", va="center", color=MUTED, fontsize=10, linespacing=1.4)
    ax.text(1.50, 0.36, r"$X$ is $4096 \times 400$: one column per face",
            ha="center", va="center", color=BLUE, fontsize=10.5)

    ax.text(4.55, 3.00, r"a column of $W$", ha="center", va="center",
            color=PURPLE, fontsize=13)
    axp = fig.add_axes([0.372, 0.335, 0.115, 0.41])
    axp.imshow(part, cmap="gray_r", interpolation="nearest")
    _bare(axp)
    arrow(ax, (4.63, 1.95), (5.05, 1.95), color=MUTED, lw=1.5)
    _strip(ax, 5.31, 1.08, part.ravel(), PURPLE, W_CMAP, h=1.70)
    ax.text(5.53, 2.98, r"$w_k$", ha="center", va="center", color=PURPLE,
            fontsize=12)
    ax.text(4.55, 0.82, "a part is 4096 numbers too, so it is an\n"
                        "image as well — but shared by all 400 faces",
            ha="center", va="center", color=MUTED, fontsize=10, linespacing=1.4)
    ax.text(4.55, 0.36, r"$W$ is $4096 \times r$: one column per part",
            ha="center", va="center", color=PURPLE, fontsize=10.5)

    ax.text(7.55, 3.00, r"a column of $H$", ha="center", va="center",
            color=GOLD, fontsize=13)
    axh = fig.add_axes([0.705, 0.315, 0.255, 0.365])
    rng = np.random.default_rng(4)
    vals = rng.random(9) ** 2.0
    axh.bar(np.arange(9), vals, color=GOLD, width=0.62)
    axh.set_xticks([])
    axh.set_yticks([])
    axh.set_ylim(0, 1.05)
    despine(axh, keep=("bottom",))
    axh.set_title(r"$h_j$", color=GOLD, fontsize=12, pad=4)
    ax.text(7.55, 0.82, "how much of each part this one face\nneeds: r numbers instead of 4096",
            ha="center", va="center", color=MUTED, fontsize=10, linespacing=1.4)
    ax.text(7.55, 0.36, r"$H$ is $r \times 400$: one column per face",
            ha="center", va="center", color=GOLD, fontsize=10.5)
    _credit(fig, "data: Olivetti faces, AT&T Cambridge")


@figure("setup_spectral")
def setup_spectral(fig):
    bands, spectra, maps, X, size = _spectral_toy()
    names = ["vegetation", "roof", "soil"]
    mats = [GREEN, BLUE, RED]
    # the most mixed pixel of the scene: largest entropy of its abundances
    ent = -(maps * np.log(maps + EPS)).sum(0)
    px = np.unravel_index(int(np.argmax(ent)), (size, size))
    j = px[0] * size + px[1]
    frac = maps[:, px[0], px[1]]

    fig.text(0.5, 0.955, "What the three matrices hold, for a hyperspectral image",
             ha="center", va="center", color=MUTED, fontsize=12.5)

    ax0 = fig.add_axes([0.030, 0.37, 0.150, 0.43])
    rgb = np.stack([maps[2], maps[0], maps[1]], -1)
    ax0.imshow(0.15 + 0.85 * rgb / rgb.max(), interpolation="nearest")
    ax0.add_patch(Rectangle((px[1] - 2.5, px[0] - 2.5), 5, 5, fill=False,
                            edgecolor=INK, lw=1.4))
    ax0.set_title("the scene", color=INK, fontsize=11.5, pad=5)
    _bare(ax0)
    fig.text(0.105, 0.295, "one pixel", ha="center", va="top", color=MUTED,
             fontsize=10)

    ax1 = fig.add_axes([0.245, 0.37, 0.180, 0.43])
    ax1.plot(bands, X[:, j], color=BLUE, lw=2.0)
    ax1.set_title(r"$x_j$: a column of $X$", color=BLUE, fontsize=11.5, pad=5)
    ax1.set_xlabel("wavelength", labelpad=2)
    ax1.set_xticks([])
    ax1.set_yticks([])
    despine(ax1, keep=("bottom",))
    fig.text(0.335, 0.285, "what that one pixel reflects,\nat each of 60 wavelengths",
             ha="center", va="top", color=MUTED, fontsize=10, linespacing=1.4)

    ax2 = fig.add_axes([0.505, 0.37, 0.180, 0.43])
    for t in range(3):
        ax2.plot(bands, spectra[:, t], color=mats[t], lw=1.8)
        ax2.text(1.03, 0.92 - t * 0.14, names[t], transform=ax2.transAxes,
                 color=mats[t], fontsize=9.5, ha="left", va="center")
    ax2.set_title(r"$w_k$: a column of $W$", color=PURPLE, fontsize=11.5, pad=5)
    ax2.set_xlabel("wavelength", labelpad=2)
    ax2.set_xticks([])
    ax2.set_yticks([])
    despine(ax2, keep=("bottom",))
    fig.text(0.595, 0.285, "the spectrum of one pure material,\nthe same all over the scene",
             ha="center", va="top", color=MUTED, fontsize=10, linespacing=1.4)

    ax3 = fig.add_axes([0.815, 0.37, 0.150, 0.43])
    ax3.bar(np.arange(3), frac, color=mats, width=0.6)
    ax3.set_xticks(np.arange(3))
    ax3.set_xticklabels(["veg.", "roof", "soil"], fontsize=9.5)
    ax3.set_yticks([])
    ax3.set_ylim(0, 1.30)
    for t in range(3):
        ax3.text(t, frac[t] + 0.04, "%.2f" % frac[t], ha="center", va="bottom",
                 color=mats[t], fontsize=9.5)
    despine(ax3, keep=("bottom",))
    ax3.set_title(r"$h_j$: a column of $H$", color=GOLD, fontsize=11.5, pad=5)
    fig.text(0.890, 0.285, "how much of each material\nsits inside that pixel",
             ha="center", va="top", color=MUTED, fontsize=10, linespacing=1.4)

    fig.text(0.5, 0.075, "The pixel reflects a blend of what it contains: light adds up, "
                         "and a fraction is never negative.",
             ha="center", va="center", color=INK, fontsize=11.5)


@figure("setup_topics")
def setup_topics(fig):
    T, vocab, target, names = _topics()
    j = int(np.argmax((T > 0).sum(0)))
    top = np.argsort(-T[:, j])[:7]

    ax = canvas(fig)
    ax.text(W / 2, 3.52, "What the three matrices hold, for a pile of text",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    for x in (3.08, 6.02):
        ax.plot([x, x], [0.78, 3.15], color=LIGHT, lw=1.2)

    ax.text(1.52, 3.00, r"a column of $X$: one post", ha="center", va="center",
            color=BLUE, fontsize=12.5)
    axb = fig.add_axes([0.095, 0.365, 0.150, 0.36])
    vals = T[top, j] / T[top, j].max()
    axb.barh(np.arange(7)[::-1], vals, color=BLUE, height=0.62)
    axb.set_yticks(np.arange(7)[::-1])
    axb.set_yticklabels([vocab[i] for i in top], fontsize=9.5)
    axb.set_xticks([])
    despine(axb)
    ax.text(1.52, 0.88, "one weight for each of the %d words in the\n"
                        "vocabulary, and zero for every word absent" % T.shape[0],
            ha="center", va="center", color=MUTED, fontsize=10, linespacing=1.4)
    ax.text(1.52, 0.42, r"$X$ is $%d \times %d$: one column per post"
            % (T.shape[0], T.shape[1]),
            ha="center", va="center", color=BLUE, fontsize=10.5)

    ax.text(4.55, 3.00, r"a column of $W$: a topic", ha="center", va="center",
            color=PURPLE, fontsize=12.5)
    axw = fig.add_axes([0.420, 0.365, 0.130, 0.36])
    rng = np.random.default_rng(3)
    v = np.sort(rng.random(7)) ** 1.6
    axw.barh(np.arange(7)[::-1], v / v.max(), color=PURPLE, height=0.62)
    axw.set_yticks(np.arange(7)[::-1])
    axw.set_yticklabels(["?"] * 7, fontsize=10, color=MUTED)
    axw.set_xticks([])
    despine(axw)
    ax.text(4.55, 0.88, "one weight per word again: which words go\n"
                        "together — this is what we are looking for",
            ha="center", va="center", color=MUTED, fontsize=10, linespacing=1.4)
    ax.text(4.55, 0.42, r"$W$ is $%d \times r$: one column per topic" % T.shape[0],
            ha="center", va="center", color=PURPLE, fontsize=10.5)

    ax.text(7.52, 3.00, r"a column of $H$: the mix", ha="center", va="center",
            color=GOLD, fontsize=12.5)
    axh = fig.add_axes([0.720, 0.365, 0.185, 0.36])
    mix = np.array([0.62, 0.05, 0.28, 0.11])
    axh.bar(np.arange(4), mix, color=GOLD, width=0.6)
    axh.set_xticks(np.arange(4))
    axh.set_xticklabels(["topic %d" % (k + 1) for k in range(4)], fontsize=8.5)
    axh.set_yticks([])
    despine(axh, keep=("bottom",))
    ax.text(7.52, 0.88, "how much of each topic this one post is\n"
                        "made of: r numbers, none of them negative",
            ha="center", va="center", color=MUTED, fontsize=10, linespacing=1.4)
    ax.text(7.52, 0.42, r"$H$ is $r \times %d$: one column per post" % T.shape[1],
            ha="center", va="center", color=GOLD, fontsize=10.5)
    _credit(fig, "data: 20 Newsgroups, headers and quotes removed")


@figure("setup_music")
def setup_music(fig):
    freqs, notes, env, t, X = _music_toy()
    j = int(0.62 * X.shape[1])

    fig.text(0.5, 0.955, "What the three matrices hold, for a recording",
             ha="center", va="center", color=MUTED, fontsize=12.5)

    tt = np.linspace(0, 1, 2600)
    wave = np.zeros_like(tt)
    for s, f in enumerate((42.0, 58.0, 73.0)):
        wave += np.interp(tt, t, env[s]) * np.sin(2 * np.pi * f * tt + s)
    ax0 = fig.add_axes([0.030, 0.38, 0.205, 0.40])
    ax0.plot(tt, wave, color=MUTED, lw=0.7)
    ax0.axvspan(t[j] - 0.025, t[j] + 0.025, color=BLUE, alpha=0.25, lw=0)
    ax0.set_title("the sound", color=INK, fontsize=11.5, pad=5)
    ax0.set_xlabel("time", labelpad=2)
    ax0.set_xticks([])
    ax0.set_yticks([])
    despine(ax0, keep=("bottom",))
    fig.text(0.132, 0.295, "cut into short frames", ha="center", va="top",
             color=MUTED, fontsize=10)

    ax1 = fig.add_axes([0.300, 0.38, 0.160, 0.40])
    ax1.plot(freqs, X[:, j], color=BLUE, lw=1.8)
    ax1.set_title(r"$x_j$: a column of $X$", color=BLUE, fontsize=11.5, pad=5)
    ax1.set_xlabel("frequency", labelpad=2)
    ax1.set_xticks([])
    ax1.set_yticks([])
    despine(ax1, keep=("bottom",))
    fig.text(0.380, 0.295, "the power in that one frame,\nat each frequency",
             ha="center", va="top", color=MUTED, fontsize=10, linespacing=1.4)

    ax2 = fig.add_axes([0.525, 0.38, 0.160, 0.40])
    ax2.plot(freqs, notes[:, 1], color=PURPLE, lw=1.8)
    ax2.set_title(r"$w_k$: a column of $W$", color=PURPLE, fontsize=11.5, pad=5)
    ax2.set_xlabel("frequency", labelpad=2)
    ax2.set_xticks([])
    ax2.set_yticks([])
    despine(ax2, keep=("bottom",))
    fig.text(0.605, 0.295, "one note: its pitch and its\nharmonics, the same at every frame",
             ha="center", va="top", color=MUTED, fontsize=10, linespacing=1.4)

    ax3 = fig.add_axes([0.760, 0.38, 0.205, 0.40])
    for s in range(3):
        ax3.plot(t, env[s] / env[s].max() + s * 1.15, color=CYCLE[s], lw=1.5)
    ax3.axvline(t[j], color=INK, lw=1.0, ls=(0, (2, 2)))
    ax3.set_title(r"rows of $H$: loudness in time", color=GOLD,
                  fontsize=11.5, pad=5)
    ax3.set_xlabel("time", labelpad=2)
    ax3.set_xticks([])
    ax3.set_yticks([])
    despine(ax3, keep=("bottom",))
    fig.text(0.862, 0.295, "when each note is struck, and\nhow loud it is at every frame",
             ha="center", va="top", color=MUTED, fontsize=10, linespacing=1.4)

    fig.text(0.5, 0.075, "A frame is the sum of the notes sounding in it, each scaled "
                         "by how loud it is right then.",
             ha="center", va="center", color=INK, fontsize=11.5)


@figure("setup_cube")
def setup_cube(fig):
    bands, spectra, maps, X, size = _spectral_toy()
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "The scene is a cube; the matrix is that cube, "
                         "unfolded",
            ha="center", va="center", color=MUTED, fontsize=12.5)

    # --- the cube: a stack of band images, drawn with a slight offset -----
    picks = [50, 38, 26, 14, 2]
    for s, b in enumerate(picks):
        x0 = 0.60 + s * 0.15
        y0 = 1.20 + s * 0.15
        img = (spectra[b] @ maps.reshape(3, -1)).reshape(size, size)
        ax.imshow(img / img.max(), cmap=NN_CMAP, vmin=0, vmax=1,
                  extent=(x0, x0 + 1.30, y0, y0 + 1.30), aspect="auto",
                  interpolation="nearest", zorder=2 + s)
        ax.add_patch(Rectangle((x0, y0), 1.30, 1.30, facecolor="none",
                               edgecolor=BLUE, lw=1.2, zorder=2 + s + 0.5))
    ax.text(1.55, 3.30, "the data cube", ha="center", va="center", color=BLUE,
            fontsize=12.5)
    ax.text(1.55, 0.92, r"44 pixels $\times$ 44 pixels $\times$ 60 wavelengths",
            ha="center", va="center", color=MUTED, fontsize=10.5)
    ax.text(1.55, 0.57, "one image per wavelength,\nstacked front to back",
            ha="center", va="center", color=MUTED, fontsize=10,
            linespacing=1.4)

    # --- one pixel, read through the stack --------------------------------
    arrow(ax, (3.35, 2.05), (4.05, 2.05), color=MUTED, lw=1.6)
    ax.text(3.70, 2.62, "take one pixel\nand read it\nthrough the stack",
            ha="center", va="center", color=MUTED, fontsize=10,
            linespacing=1.4)

    # --- the matrix -------------------------------------------------------
    _matrix(ax, 4.60, 1.35, 3.60, 1.55, BLUE, NN_CMAP, seed=3, nrow=12,
            ncol=26, label=r"$X$")
    ax.add_patch(Rectangle((5.72, 1.35), 0.138, 1.55, facecolor="none",
                           edgecolor=INK, lw=1.6, zorder=5))
    ax.text(5.79, 3.10, r"$x_j$", ha="center", va="center", color=INK,
            fontsize=12)
    ax.text(4.45, 2.12, "60 wavelengths", ha="right", va="center",
            color=MUTED, fontsize=10, rotation=90)
    ax.text(6.40, 0.92, r"$1936 = 44 \times 44$ pixels, laid out in a row",
            ha="center", va="center", color=MUTED, fontsize=10.5)
    ax.text(6.40, 0.57, r"$X$ is $60 \times 1936$: one column per pixel",
            ha="center", va="center", color=BLUE, fontsize=10.5)

    note(ax, "The factorization never sees the geometry: which pixel sits "
             "next to which is only used to draw the result.", y=0.20, size=11)


@figure("eq_frobenius")
def eq_frobenius(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "The Frobenius norm, and the one identity that "
                         "makes it differentiable by hand",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$\|A\|_F^2 \;=\; \sum_{i}\sum_{j} A_{ij}^2 \;=\; "
         r"\mathrm{tr}\!\left( A^\top A \right)$",
         r"the sum of the squares of every entry, written without indices: "
         r"$[A^\top A]_{jj} = \sum_i A_{ij}^2$"),
        (r"$\mathrm{tr}(AB) = \mathrm{tr}(BA)$, $\qquad$ "
         r"$\mathrm{tr}(A^\top) = \mathrm{tr}(A)$, $\qquad$ "
         r"$\mathrm{tr}$ is linear",
         "the only three facts about the trace used anywhere in this deck"),
        (r"$F(W, H) = \dfrac{1}{2}\|X - WH\|_F^2 = \dfrac{1}{2}\,"
         r"\mathrm{tr}\!\left[ (X - WH)^\top (X - WH) \right]$",
         "expand the product inside, then use the two facts above"),
        (r"$\phantom{F(W, H)} = \dfrac{1}{2}\,\mathrm{tr}(X^\top X) \;-\; "
         r"\mathrm{tr}(H^\top W^\top X) \;+\; \dfrac{1}{2}\,"
         r"\mathrm{tr}(H^\top W^\top W H)$",
         r"constant in $H$   |   linear in $H$   |   quadratic in $H$ — "
         r"a convex quadratic, so the gradient is all we need", GREEN),
    ], top=3.00, gap=0.80, x=0.35, eq_size=13.5, why_size=10.5, why_off=0.33)


@figure("mu_split_why")
def mu_split_why(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Why bother splitting the gradient in two?",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 3.04, r"$\eta_{kj} = H_{kj} / [W^\top W H]_{kj}$ was "
                         r"invented for one loss. Must we redo that algebra "
                         r"for every other one?",
            ha="center", va="center", color=INK, fontsize=12.5)

    box(ax, 0.45, 1.95, 8.10, 0.70, GREEN, "", fill="#f2fbf2")
    ax.text(W / 2, 2.52, r"No: write $\nabla = \nabla^{+} - \nabla^{-}$ with "
                         r"both parts $\geq 0$, take $\eta = H / \nabla^{+}$",
            ha="center", va="center", color=GREEN, fontsize=13)
    ax.text(W / 2, 2.15, r"$H - \eta \odot \nabla "
                         r"= H - \dfrac{H}{\nabla^{+}} \odot "
                         r"(\nabla^{+} - \nabla^{-}) "
                         r"= H \odot \dfrac{\nabla^{-}}{\nabla^{+}}$",
            ha="center", va="center", color=INK, fontsize=14)

    items = [
        ("stays non-negative", BLUE,
         "a ratio of two non-negative\nnumbers, times a non-negative\n"
         "entry — nothing can go below 0"),
        ("stops only where it should", PURPLE,
         r"a fixed point needs $\nabla^{+} = \nabla^{-}$" "\n"
         r"or $H_{kj} = 0$ — exactly the optimality" "\n"
         r"condition for a constrained $H \geq 0$"),
        ("one recipe, every loss", GOLD,
         "no step size to tune, and a\nnew loss only needs its gradient\n"
         "read in two pieces"),
    ]
    for i, (head, color, body) in enumerate(items):
        x = 1.60 + i * 2.95
        ax.text(x, 1.52, head, ha="center", va="center", color=color,
                fontsize=12.5, weight="bold")
        ax.text(x, 0.98, body, ha="center", va="center", color=MUTED,
                fontsize=10.5, linespacing=1.5)
    note(ax, "the split is never unique — any valid one gives a working rule",
         y=0.26, size=11)


@figure("jensen_what")
def jensen_what(fig):
    z = np.linspace(0.15, 3.5, 400)
    phi = (z - 1.0) ** 2 * 0.55 + 0.35 / z
    z1, z2, lam = 0.45, 3.15, 0.55
    p1 = (z1 - 1.0) ** 2 * 0.55 + 0.35 / z1
    p2 = (z2 - 1.0) ** 2 * 0.55 + 0.35 / z2
    zb = lam * z1 + (1 - lam) * z2
    pb = (zb - 1.0) ** 2 * 0.55 + 0.35 / zb
    pm = lam * p1 + (1 - lam) * p2

    ax = fig.add_axes([0.065, 0.24, 0.42, 0.56])
    ax.plot(z, phi, color=INK, lw=2.3, zorder=3)
    ax.plot([z1, z2], [p1, p2], color=GRID, lw=1.6, zorder=2)
    for zi, pi, name, color in ((z1, p1, r"$z_1$", BLUE),
                                (z2, p2, r"$z_2$", PURPLE)):
        ax.plot(zi, pi, "o", color=color, ms=7, zorder=4)
        ax.text(zi, pi + 0.22, name, color=color, fontsize=11.5, ha="center")
    ax.plot(zb, pb, "o", color=GREEN, ms=8, zorder=5)
    ax.plot(zb, pm, "o", color=RED, ms=8, zorder=5)
    ax.annotate("", xy=(zb, pm), xytext=(zb, pb),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1.6))
    ax.text(zb - 0.13, pm, r"$\sum_k \lambda_k\, \varphi(z_k)$", color=RED,
            fontsize=11.5, ha="right", va="center")
    ax.text(zb - 0.16, pb - 0.26, r"$\varphi(\bar{z})$", color=GREEN,
            fontsize=11.5, ha="right", va="center")
    ax.text(zb, -0.42, r"$\bar{z} = \lambda z_1 + (1 - \lambda) z_2$",
            color=GREEN, fontsize=11, ha="center")
    ax.set_ylim(-0.25, 3.1)
    ax.set_xticks([])
    ax.set_yticks([])
    despine(ax)
    ax.set_title(r"a convex $\varphi$: the chord never dips below the curve",
                 color=INK, fontsize=12, pad=8)

    side = fig.add_axes([0.545, 0.18, 0.43, 0.66])
    side.axis("off")
    side.text(0, 1.0, "Jensen's inequality", color=GREEN, fontsize=13.5,
              weight="bold", va="top")
    side.text(0, 0.84, r"$\varphi$ convex, $\lambda_k \geq 0$, "
                       r"$\sum_k \lambda_k = 1$:",
              color=INK, fontsize=12, va="top")
    side.text(0, 0.66, r"$\varphi\!\left( \sum_k \lambda_k z_k \right) "
                       r"\;\leq\; \sum_k \lambda_k\, \varphi(z_k)$",
              color=INK, fontsize=15, va="top")
    side.text(0, 0.42, "a convex function of an average is at most\n"
                       "the average of the values, with equality\n"
                       r"only when every $z_k$ is the same",
              color=MUTED, fontsize=10.5, va="top", linespacing=1.6)
    side.text(0, 0.12, "the right-hand side is a sum of separate terms:\n"
                       "that is what makes it useful here",
              color=GREEN, fontsize=10.5, va="top", linespacing=1.6)


@figure("mu_other_losses")
def mu_other_losses(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.05, "Minimize in closed form a majorant",
            ha="center", va="center", color=MUTED, fontsize=11)

    rows = [
        ("Frobenius", r"$\beta = 2$", BLUE,
         r"$H \leftarrow H \odot \dfrac{W^\top X}{W^\top W H}$"),
        ("Kullback–Leibler", r"$\beta = 1$", GREEN,
         r"$H \leftarrow H \odot \dfrac{W^\top (X \oslash WH)}"
         r"{W^\top \mathbf{1}}$"),
        ("Itakura–Saito", r"$\beta = 0$", GOLD,
         r"$H \leftarrow H \odot \dfrac{W^\top (X \oslash (WH)^{2})}"
         r"{W^\top (WH)^{-1}}$"),
    ]
    for i, (name, beta, color, rule) in enumerate(rows):
        y = 2.62 - i * 0.70
        ax.text(0.45, y, name, ha="left", va="center", color=color,
                fontsize=12.5)
        ax.text(2.55, y, beta, ha="left", va="center", color=MUTED,
                fontsize=11)
        ax.text(3.45, y, rule, ha="left", va="center", color=INK,
                fontsize=13.5)
        if i < 2:
            ax.plot([0.40, 8.60], [y - 0.35, y - 0.35], color=LIGHT, lw=1.0)

    box(ax, 0.45, 0.10, 8.10, 0.44, PURPLE, "", fill="white")
    ax.text(W / 2, 0.32, r"General formula: $\;H \leftarrow H \odot "
                         r"\dfrac{W^\top\!\left[(WH)^{\beta-2} \odot X\right]}"
                         r"{W^\top (WH)^{\beta-1}}\;$, from "
                         r"$\partial d_\beta / \partial y "
                         r"= y^{\beta-2}(y - x)$",
            ha="center", va="center", color=PURPLE, fontsize=12.5)


@figure("app_faces")
def app_faces(fig):
    imgs, Xf = _faces(400)
    X = Xf.T                      # pixels x faces
    r = 100
    Wm, Hm = _mu(X, r, 400, init="nndsvd")
    Wm, Hm = _order(Wm, Hm)
    j = 6
    rec = (Wm @ Hm)[:, j].reshape(64, 64)

    fig.text(0.5, 0.95, f"{X.shape[1]} faces of 64 × 64 pixels,  NMF with r = {r}",
             ha="center", va="center", color=INK, fontsize=12.5)
    gs = fig.add_gridspec(10, 10, left=0.438, right=0.742, top=0.90,
                          bottom=0.155, wspace=0.03, hspace=0.03)
    for k in range(r):
        ax = fig.add_subplot(gs[k // 10, k % 10])
        ax.imshow(Wm[:, k].reshape(64, 64), cmap="gray_r", interpolation="nearest")
        _bare(ax)
    fig.text(0.59, 0.125, r"the %d columns of $W$" % r, ha="center", va="top",
             color=PURPLE, fontsize=12)

    for i, (img, name, color) in enumerate(
            [(imgs[j], r"a face $x_j$", BLUE), (rec, r"$W h_j$", GREEN)]):
        ax = fig.add_axes([0.055 + i * 0.145, 0.30, 0.13, 0.50])
        ax.imshow(img, cmap="gray", interpolation="nearest")
        ax.set_title(name, color=color, fontsize=12.5, pad=6)
        _bare(ax)
    fig.text(0.20, 0.23, f"{r} numbers instead of 4096", ha="center", va="top",
             color=MUTED, fontsize=10.5)
    side = fig.add_axes([0.805, 0.17, 0.19, 0.68])
    side.axis("off")
    side.text(0, 1.0, "each one is", color=PURPLE, fontsize=12, va="top")
    side.text(0, 0.86, "non-negative, so it is\nsomething you add on,"
               "\nnever something you\ntake away",
              color=MUTED, fontsize=10.5, va="top", linespacing=1.5)
    side.text(0, 0.40, "a face is then a\nlist of amounts", color=INK,
              fontsize=10.5, va="top", linespacing=1.5)
    _credit(fig, "data: Olivetti faces, AT&T Cambridge")


@figure("app_spectral")
def app_spectral(fig):
    bands, spectra, maps, X, size = _spectral_toy()
    Wm, Hm = _mu(X, 3, 600, init="nndsvd")
    # name each recovered component by the true spectrum it matches
    C = np.array([[np.corrcoef(spectra[:, t], Wm[:, k])[0, 1] for k in range(3)]
                  for t in range(3)])
    order = [int(np.argmax(C[t])) for t in range(3)]
    names = ["vegetation", "roof", "soil"]
    mats = [GREEN, BLUE, RED]

    ax0 = fig.add_axes([0.035, 0.26, 0.17, 0.56])
    rgb = np.stack([maps[2], maps[0], maps[1]], -1)  # soil R, veg G, roof B
    ax0.imshow(0.15 + 0.85 * rgb / rgb.max(), interpolation="nearest")
    ax0.set_title("the scene", color=BLUE, fontsize=12, pad=6)
    _bare(ax0)
    fig.text(0.12, 0.21, "three materials,\nblended at every border",
             ha="center", va="top", color=MUTED, fontsize=9.5, linespacing=1.4)

    ax1 = fig.add_axes([0.27, 0.26, 0.24, 0.56])
    for t, k in enumerate(order):
        scale = float(spectra[:, t] @ Wm[:, k] / (Wm[:, k] @ Wm[:, k]))
        ax1.plot(bands, scale * Wm[:, k], color=mats[t], lw=2.2)
        ax1.plot(bands, spectra[:, t], color="white", lw=0.9, ls=(0, (2, 2)))
    ax1.set_xlabel("wavelength (µm)", labelpad=2)
    ax1.set_title(r"$W$: the spectra found", color=PURPLE, fontsize=12, pad=6)
    ax1.set_yticks([])
    despine(ax1, keep=("bottom",))
    fig.text(0.39, 0.125, "thick: NMF    dashed: truth", ha="center", va="top",
             color=MUTED, fontsize=9.5)

    for t, k in enumerate(order):
        ax = fig.add_axes([0.575 + t * 0.14, 0.30, 0.125, 0.48])
        hk = Hm[k].reshape(size, size)
        ax.imshow(hk / hk.max(), cmap=H_CMAP, vmin=0, vmax=1,
                  interpolation="nearest")
        for sp in ax.spines.values():
            sp.set_visible(True)
            sp.set_color(GRID)
        ax.set_title(names[t], color=mats[t], fontsize=11, pad=5)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.text(0.76, 0.855, r"$H$: how much of it, in every pixel", ha="center",
             va="center", color=GOLD, fontsize=12)
    fig.text(0.76, 0.185, "NMF never saw the three materials:\n"
                          "non-negativity is the whole prior",
             ha="center", va="top", color=MUTED, fontsize=10.5, linespacing=1.4)
    fig.text(0.5, 0.955, "Hyperspectral unmixing: 60 wavelengths × "
                         f"{size * size} pixels, r = 3",
             ha="center", va="center", color=INK, fontsize=12.5)


@figure("app_topics")
def app_topics(fig):
    T, vocab, target, names = _topics()
    Wm, Hm = _mu(T, 4, 400, init="nndsvd")
    Wm, Hm = _order(Wm, Hm)
    hard = np.argmax(Hm, 0)

    ax = canvas(fig)
    ax.text(W / 2, 3.52, f"{T.shape[1]:,} newsgroup posts × {T.shape[0]} words "
                         "(TF-IDF),  NMF with r = 4",
            ha="center", va="center", color=INK, fontsize=12.5)
    for k in range(4):
        x = 0.25 + k * 2.18
        color = CYCLE[k]
        box(ax, x, 0.62, 1.98, 2.52, color, "", lw=1.6)
        ax.text(x + 0.99, 2.92, f"topic {k + 1}", ha="center", va="center",
                color=color, fontsize=12.5, weight="bold")
        for j, word in enumerate(vocab[np.argsort(-Wm[:, k])[:8]]):
            ax.text(x + 0.99, 2.58 - j * 0.21, word, ha="center", va="center",
                    color=INK, fontsize=11.5)
        counts = np.bincount(target[hard == k], minlength=4)
        g = int(counts.argmax())
        ax.text(x + 0.99, 0.82, f"{counts[g]} of {counts.sum()} posts\n"
                                f"{names[g]}", ha="center", va="center",
                color=MUTED, fontsize=9, linespacing=1.3)
    note(ax, r"A column of $W$ is a topic: the words it is made of. "
             r"A column of $H$ is how much of each topic one post holds.",
         y=0.28, size=11)
    _credit(fig, "data: 20 Newsgroups, headers and quotes removed")


@figure("app_recsys")
def app_recsys(fig):
    full, mask = _ratings_toy()
    seen = np.where(mask > 0, full, np.nan)

    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Fill a table with holes",
            ha="center", va="center", color=MUTED, fontsize=12.5)

    ax1 = fig.add_axes([0.06, 0.22, 0.26, 0.56])
    cm = NN_CMAP.copy()
    cm.set_bad(LIGHT)
    ax1.imshow(seen, cmap=cm, vmin=1, vmax=5, aspect="auto",
               interpolation="nearest")
    ax1.set_title(r"$X$ as observed", color=BLUE, fontsize=12, pad=6)
    ax1.set_xlabel("users")
    ax1.set_ylabel("items")
    ax1.set_xticks([])
    ax1.set_yticks([])

    Wm, Hm = _mu(full, 3, 500, mask=mask, init="nndsvd")
    ax2 = fig.add_axes([0.40, 0.22, 0.26, 0.56])
    ax2.imshow(Wm @ Hm, cmap=NN_CMAP, vmin=1, vmax=5, aspect="auto",
               interpolation="nearest")
    ax2.set_title(r"$WH$, every cell filled", color=GREEN, fontsize=12, pad=6)
    ax2.set_xlabel("users")
    ax2.set_xticks([])
    ax2.set_yticks([])

    hidden = mask == 0
    err = np.abs((Wm @ Hm)[hidden] - full[hidden]).mean()
    caption_row(fig, [ax1, ax2],
                [f"{int(mask.sum())} of {mask.size} ratings given",
                 f"error on the {int(hidden.sum())} hidden ones: "
                 f"{err:.2f} stars"], y=0.165)

    side = fig.add_axes([0.70, 0.20, 0.28, 0.58])
    side.axis("off")
    side.text(0, 1.0, "Trick", color=GOLD, fontsize=12.5, weight="bold",
              va="top")
    side.text(0, 0.84, "give the missing cells\nweight 0: they cost nothing,\n"
                       "so they constrain nothing", color=INK, fontsize=10.5,
              va="top", linespacing=1.5)
    side.text(0, 0.42, "Prediction", color=GREEN, fontsize=12.5,
              weight="bold", va="top")
    side.text(0, 0.26, r"$\widehat{X}_{ij} = [WH]_{ij}$", color=INK,
              fontsize=12, va="top")
    side.text(0, 0.06, "this is weighted NMF", color=MUTED, fontsize=10.5,
              va="top")


@figure("app_music")
def app_music(fig):
    freqs, notes, env, t, X = _music_toy()
    Wm, Hm = _mu(X, 3, 800, loss="kl", init="nndsvd")
    order = [int(np.argmax([np.corrcoef(notes[:, s], Wm[:, k])[0, 1]
                            for k in range(3)])) for s in range(3)]

    ax0 = fig.add_axes([0.055, 0.24, 0.30, 0.56])
    ax0.imshow(np.log1p(X / X.max() * 400), cmap=NN_CMAP, aspect="auto",
               origin="lower", extent=(0, 1, 0, 1), interpolation="nearest")
    ax0.set_title(r"$X$: a power spectrogram", color=BLUE, fontsize=12, pad=6)
    ax0.set_xlabel("time")
    ax0.set_ylabel("frequency")
    ax0.set_xticks([])
    ax0.set_yticks([])

    ax1 = fig.add_axes([0.44, 0.24, 0.16, 0.56])
    for s, k in enumerate(order):
        ax1.plot(Wm[:, k] / Wm[:, k].max() + s * 1.25, freqs, color=CYCLE[s],
                 lw=1.6)
    ax1.set_title(r"$W$: three notes", color=PURPLE, fontsize=12, pad=6)
    ax1.set_xticks([])
    ax1.set_yticks([])
    despine(ax1)

    ax2 = fig.add_axes([0.66, 0.24, 0.32, 0.56])
    for s, k in enumerate(order):
        ax2.plot(t, Hm[k] / Hm[k].max() + s * 1.20, color=CYCLE[s], lw=1.6)
    ax2.set_title(r"$H$: when each is struck", color=GOLD, fontsize=12, pad=6)
    ax2.set_xlabel("time")
    ax2.set_xticks([])
    ax2.set_yticks([])
    despine(ax2, keep=("bottom",))

    fig.text(0.5, 0.955, "Power adds up when notes are played together, "
                         "so the spectrogram really is a product",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    fig.text(0.5, 0.115, "Itakura–Saito (or KL) is the loss of choice here: "
                         "it treats a quiet harmonic like a loud one",
             ha="center", va="top", color=MUTED, fontsize=11)


@figure("when_nmf")
def when_nmf(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.50, "NMF is the method when the data is a mixture of "
                         "things that add up",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    rows = [
        (BLUE, "images", "pixels", "parts of an object"),
        (PURPLE, "spectroscopy", "wavelengths", "pure materials"),
        (GREEN, "text", "word counts", "topics"),
        (GOLD, "audio", "power per frequency", "notes, instruments"),
        (RED, "recommendation", "ratings", "tastes"),
    ]
    ax.text(2.55, 3.05, r"a column of $X$ is", ha="left", va="center", color=MUTED,
            fontsize=11)
    ax.text(5.60, 3.05, r"a column of $W$ is", ha="left", va="center", color=MUTED,
            fontsize=11)
    for i, (color, name, inputs, out) in enumerate(rows):
        y = 2.68 - i * 0.52
        ax.text(2.40, y, name, ha="right", va="center", color=color, fontsize=13,
                weight="bold")
        ax.text(2.55, y, inputs, ha="left", va="center", color=INK, fontsize=12)
        ax.text(5.25, y, "→", ha="center", va="center", color=MUTED, fontsize=12)
        ax.text(5.60, y, out, ha="left", va="center", color=INK, fontsize=12)
        if i:
            ax.plot([0.60, 8.40], [y + 0.26, y + 0.26], color=GRID, lw=0.9)
    note(ax, "If a component means \"subtract some of that\", NMF is the wrong "
             "model", y=0.24)


# ==========================================================================
# 3. choosing a loss
# ==========================================================================
def _d_quad(x, y):
    return (x - y) ** 2


def _d_kl(x, y):
    return x * np.log(x / y) - x + y


def _d_is(x, y):
    return x / y - np.log(x / y) - 1


def _d_beta(x, y, b):
    if abs(b - 1) < 1e-9:
        return _d_kl(x, y)
    if abs(b) < 1e-9:
        return _d_is(x, y)
    return (x ** b + (b - 1) * y ** b - b * x * y ** (b - 1)) / (b * (b - 1))


@figure("eq_loss")
def eq_loss(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.50, r"Measure $X \approx WH$ with a divergence between $X$ "
                         r"and $WH$",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 2.72, r"$D(X, WH) = \sum_{i=1}^{p} \sum_{j=1}^{n} "
                         r"d([X]_{ij},\, [WH]_{ij})$",
            ha="center", va="center", color=INK, fontsize=22)

    ax.annotate("", xy=(4.95, 2.40), xytext=(3.30, 1.92),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.6))
    ax.text(3.20, 1.86, "one scalar loss", ha="right", va="center", color=MUTED,
            fontsize=11)
    ax.annotate("", xy=(5.40, 2.40), xytext=(5.40, 1.92),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6))
    ax.text(5.40, 1.76, "one entry\nof the data", ha="center", va="center",
            color=BLUE, fontsize=11, linespacing=1.5)
    ax.annotate("", xy=(6.50, 2.40), xytext=(7.55, 1.92),
                arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=1.6))
    ax.text(7.65, 1.86, "the same entry\nof the model", ha="left", va="center",
            color=PURPLE, fontsize=11, linespacing=1.5)

    box(ax, 1.15, 0.55, 6.70, 0.62, GREEN, "", fill="#f2fbf2")
    ax.text(W / 2, 0.86, "Separable: the loss of one entry never looks at "
                         "another entry",
            ha="center", va="center", color=GREEN, fontsize=12.5)
    note(ax, "this is what makes every update rule entrywise", y=0.22,
         size=11)


@figure("loss_axioms")
def loss_axioms(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.50, r"Requirements for $d$", ha="center", va="center", color=MUTED, fontsize=12.5)

    box(ax, 0.50, 1.95, 3.85, 1.25, GREEN, "", fill="white")
    ax.text(2.42, 2.98, "ask", ha="center", va="center", color=GREEN,
            fontsize=13, weight="bold")
    ax.text(2.42, 2.58, r"$d(x, x) = 0 \quad \forall x$", ha="center",
            va="center", color=INK, fontsize=14)
    ax.text(2.42, 2.20, r"$d(x, y) \geq 0 \quad \forall (x, y)$", ha="center",
            va="center", color=INK, fontsize=14)

    box(ax, 4.65, 1.95, 3.85, 1.25, RED, "", fill="white")
    ax.text(6.57, 2.98, "do not ask", ha="center", va="center", color=RED,
            fontsize=13, weight="bold")
    ax.text(6.57, 2.58, r"$d(x, y) = d(y, x)$", ha="center", va="center",
            color=INK, fontsize=14)
    ax.text(6.57, 2.20, r"$d(x, z) \leq d(x, y) + d(y, z)$", ha="center",
            va="center", color=INK, fontsize=14)

    ax.text(W / 2, 1.55, "A divergence, not a distance", ha="center",
            va="center", color=INK, fontsize=14)
    a, b = 1.0, 3.0
    ax.text(W / 2, 1.08, r"KL:  $d(1, 3) = %.2f$ "
                         r"$\quad$ but $\quad$ $d(3, 1) = %.2f$"
                         % (_d_kl(a, b), _d_kl(b, a)),
            ha="center", va="center", color=GOLD, fontsize=14)
    note(ax, "underestimating and overestimating an entry do not cost "
             "the same", y=0.52, size=11.5)
    note(ax, r"the order of the arguments is always $d(\mathrm{data},"
             r"\ \mathrm{model})$", y=0.18, size=11.5, color=MUTED)


@figure("loss_zoo")
def loss_zoo(fig):
    ax = canvas(fig)
    rows = [
        (BLUE, "Quadratic", r"$d(x, y) = (x - y)^2$",
         ["Gaussian noise", "not robust to outliers",
          r"$\ell_1$ and friends for robustness"]),
        (GREEN, "Kullback–Leibler", r"$d(x, y) = x \log \dfrac{x}{y} - x + y$",
         ["counts, Poisson noise", "text mining, photon imaging",
          "cheap to differentiate"]),
        (GOLD, "Itakura–Saito",
         r"$d(x, y) = \dfrac{x}{y} - \log \dfrac{x}{y} - 1$",
         [r"scale invariant: $d(\lambda x, \lambda y) = d(x, y)$",
          "music and audio spectra", "harder to optimise"]),
    ]
    for i, (color, name, formula, bullets) in enumerate(rows):
        y = 3.30 - i * 1.14
        ax.text(0.50, y, name, color=color, fontsize=13.5, weight="bold",
                va="center")
        ax.text(0.50, y - 0.42, formula, color=INK, fontsize=15, va="center")
        for j, b in enumerate(bullets):
            ax.text(4.60, y + 0.04 - j * 0.32, "—", color=color, fontsize=11,
                    va="center")
            ax.text(4.82, y + 0.04 - j * 0.32, b, color=INK, fontsize=11,
                    va="center")
        if i < 2:
            ax.plot([0.40, 8.60], [y - 0.72, y - 0.72], color=LIGHT, lw=1.0)


@figure("loss_shapes")
def loss_shapes(fig):
    y = np.linspace(0.06, 3.2, 400)
    axes = panels(
        fig, 2,
        titles=[r"Cost of predicting $y$ when the data is $x = 1$",
                r"Scaled by $\lambda$"],
        colors=[INK, INK],
        gridspec_kw=dict(left=0.07, right=0.97, top=0.80, bottom=0.30, wspace=0.26),
    )
    for fn, color, name, tx, ty, ha in ((_d_quad, BLUE, "quadratic", 2.35, 2.05, "left"),
                                        (_d_kl, GREEN, "KL", 3.15, 1.15, "right"),
                                        (_d_is, GOLD, "Itakura–Saito", 0.52, 1.95, "left")):
        axes[0].plot(y, fn(1.0, y), color=color, lw=2.2)
        axes[0].text(tx, ty, name, color=color, fontsize=10.5, ha=ha,
                     va="bottom")
    axes[0].axvline(1.0, color=GRID, lw=1.2, ls="--")
    axes[0].set_ylim(0, 2.6)
    axes[0].set_xlabel(r"$y = [WH]_{ij}$", labelpad=2)
    despine(axes[0], keep=("left", "bottom"))

    lam = np.linspace(0.3, 3.0, 300)
    for fn, color in ((_d_quad, BLUE), (_d_kl, GREEN), (_d_is, GOLD)):
        axes[1].plot(lam, fn(lam * 1.0, lam * 1.6) / fn(1.0, 1.6), color=color,
                     lw=2.2)
    axes[1].axhline(1.0, color=GRID, lw=1.2, ls="--")
    axes[1].set_xlabel(r"$\lambda$", labelpad=2)
    axes[1].set_ylabel(r"$d(\lambda x, \lambda y) \,/\, d(x, y)$")
    axes[1].set_ylim(0, 3.2)
    despine(axes[1], keep=("left", "bottom"))
    axes[1].text(2.25, 1.15, "Itakura–Saito", color=GOLD, fontsize=10.5)
    axes[1].text(2.25, 2.45, "quadratic", color=BLUE, fontsize=10.5)
    axes[1].text(2.25, 1.75, "KL", color=GREEN, fontsize=10.5)

    caption_row(fig, axes, ["too small costs much more than too big",
                            "only Itakura–Saito does not care about volume"],
                y=0.115)


@figure("eq_loss_from_noise")
def eq_loss_from_noise(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "A loss is a noise model in disguise", ha="center",
            va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$[X]_{ij} \sim p(\,\cdot \mid [WH]_{ij})$, independently "
         r"over $(i, j)$",
         "assume the model entry is the parameter of a distribution"),
        (r"$\max_{W, H} \; \prod_{ij} p([X]_{ij} \mid [WH]_{ij})"
         r"\;\;\Leftrightarrow\;\; \min_{W, H} \; \sum_{ij} "
         r"-\log p([X]_{ij} \mid [WH]_{ij})$",
         "maximum likelihood, written as a minimisation"),
        (r"$d(x, y) = -\log p(x \mid y) + c(x)$",
         r"add whatever depends on $x$ alone: it cannot move $W$ or $H$"),
        (r"$c(x)$ is chosen so that $d(x, x) = 0$",
         "that is the only thing the constant is for", GREEN),
    ], top=3.05, gap=0.74, x=0.45, eq_size=13, why_off=0.36)
    note(ax, "pick the distribution your data actually follows, and the loss "
             "follows from it", y=0.14, size=12)


@figure("eq_gaussian_loss")
def eq_gaussian_loss(fig):
    ax = canvas(fig)
    ax.text(0.45, 3.50, "Gaussian noise", color=BLUE, fontsize=14,
            weight="bold", va="center")
    ax.text(2.55, 3.50, r"$x \mid y \;\sim\; \mathcal{N}(y, \sigma^2)$,"
                        r"$\quad$ i.e. $x = y + \varepsilon$: the error is "
                        r"added, and its size does not depend on $y$",
            color=MUTED, fontsize=11.5, va="center")
    steps(ax, [
        (r"$p(x \mid y) = \dfrac{1}{\sqrt{2\pi\sigma^2}}\,"
         r"\exp\!\left(-\dfrac{(x - y)^2}{2\sigma^2}\right)$", ""),
        (r"$-\log p(x \mid y) = \dfrac{(x - y)^2}{2\sigma^2} "
         r"+ \frac{1}{2}\log(2\pi\sigma^2)$",
         r"the last term has no $y$ in it: drop it"),
        (r"$d(x, y) = (x - y)^2$",
         r"already zero at $x = y$, so $c(x) = 0$; the factor "
         r"$1/2\sigma^2$ only rescales the whole loss", GREEN),
    ], top=3.00, gap=0.82, x=0.45, eq_size=15, why_off=0.38)
    box(ax, 0.45, 0.20, 8.10, 0.52, BLUE, "", fill="#f0f5fb")
    ax.text(W / 2, 0.46, r"$D(X, WH) = \|X - WH\|_F^2$"
                         r"$\quad$ — the Frobenius norm, squared",
            ha="center", va="center", color=BLUE, fontsize=14)


@figure("eq_poisson_loss")
def eq_poisson_loss(fig):
    ax = canvas(fig)
    ax.text(0.45, 3.52, "Poisson counts", color=GREEN, fontsize=14,
            weight="bold", va="center")
    ax.text(2.55, 3.52, r"$x \mid y \;\sim\; \mathrm{Poisson}(y)$,"
                        r"$\quad$ how many times something happened: words, "
                        r"photons, clicks",
            color=MUTED, fontsize=11.5, va="center")
    steps(ax, [
        (r"$p(x \mid y) = \dfrac{y^{x} e^{-y}}{x!}$", ""),
        (r"$-\log p(x \mid y) = y - x \log y + \log(x!)$",
         r"again, $\log(x!)$ carries no $y$"),
        (r"$d(x, y) = y - x \log y + \;[\,x \log x - x\,]"
         r"\;=\; x \log \dfrac{x}{y} - x + y$",
         r"the bracket is $c(x)$ — not free here: it is what makes "
         r"$d(x, x) = 0$"),
        (r"check:  $d(x, x) = x \log 1 - x + x = 0$ " r"$\checkmark$", "",
         GREEN),
    ], top=2.98, gap=0.70, x=0.45, eq_size=14.5, why_off=0.34)
    box(ax, 0.45, 0.10, 8.10, 0.46, GREEN, "", fill="#f2fbf2")
    ax.text(W / 2, 0.33, r"$D(X, WH) = \mathrm{KL}(X, WH)$"
                         r"$\quad$ — the generalized Kullback–Leibler "
                         r"divergence",
            ha="center", va="center", color=GREEN, fontsize=14)


@figure("eq_is_loss")
def eq_is_loss(fig):
    ax = canvas(fig)
    ax.text(0.45, 3.52, "Multiplicative noise", color=GOLD, fontsize=14,
            weight="bold", va="center")
    ax.text(3.10, 3.52, r"$x = y \cdot \varepsilon$ with "
                        r"$\varepsilon \sim \mathrm{Exp}(1)$: the error is a "
                        r"percentage, not an amount",
            color=MUTED, fontsize=11.5, va="center")
    steps(ax, [
        (r"$p(x \mid y) = \dfrac{1}{y}\, e^{-x/y}$",
         r"the density of $y\varepsilon$; also $\mathrm{Gamma}(1, y)$, the "
         r"law of the power of a Gaussian signal"),
        (r"$-\log p(x \mid y) = \dfrac{x}{y} + \log y$", ""),
        (r"$d(x, y) = \dfrac{x}{y} + \log y "
         r"\;+\;[\,-\log x - 1\,] "
         r"\;=\; \dfrac{x}{y} - \log \dfrac{x}{y} - 1$",
         r"the bracket is $c(x)$, again fixed by $d(x, x) = 0$"),
        (r"$d(\lambda x, \lambda y) = \dfrac{x}{y} - \log \dfrac{x}{y} - 1"
         r" = d(x, y)$",
         r"the $\lambda$ cancels inside both terms: scale invariance, "
         r"for free", GOLD),
    ], top=2.98, gap=0.70, x=0.45, eq_size=14, why_off=0.34)
    note(ax, "a quiet harmonic and a loud one are then fitted with equal care "
             "— which is why audio uses it", y=0.14, size=11.5)


@figure("eq_beta_divergence")
def eq_beta_divergence(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "The three are one family", ha="center", va="center",
            color=MUTED, fontsize=12.5)
    ax.text(0.45, 3.02, r"$d_\beta(x, y) = \dfrac{1}{\beta(\beta - 1)}"
                        r"\left( x^\beta + (\beta - 1)\, y^\beta "
                        r"- \beta\, x\, y^{\beta - 1} \right)$",
            color=INK, fontsize=16, va="center")
    rows = [
        (r"$\beta = 2$", "quadratic", "Gaussian", BLUE),
        (r"$\beta = 1$", "KL", "Poisson", GREEN),
        (r"$\beta = 0$", "Itakura–Saito", "multiplicative", GOLD),
    ]
    for i, (b, name, model, color) in enumerate(rows):
        y = 2.12 - i * 0.44
        ax.text(0.60, y, b, color=color, fontsize=13, va="center")
        ax.text(1.45, y, name, color=color, fontsize=13, va="center",
                weight="bold")
        ax.text(3.30, y, model, color=MUTED, fontsize=11.5, va="center")
    ax.text(0.45, 0.48, r"$\beta = 1$ and $\beta = 0$ are limits: the formula "
                        r"is $0/0$ there, and L'Hôpital gives back KL and "
                        r"Itakura–Saito",
            color=MUTED, fontsize=11, va="center")
    ax.text(0.45, 0.16, r"$d_\beta(\lambda x, \lambda y) = \lambda^\beta\, "
                        r"d_\beta(x, y)$: only $\beta = 0$ is scale invariant",
            color=MUTED, fontsize=11, va="center")

    axp = fig.add_axes([0.60, 0.36, 0.35, 0.42])
    y = np.linspace(0.12, 3.0, 400)
    for b, color, name in ((2.0, BLUE, r"$\beta = 2$"), (1.0, GREEN, r"$\beta = 1$"),
                           (0.0, GOLD, r"$\beta = 0$"), (1.5, MUTED, r"$\beta = 1.5$")):
        axp.plot(y, _d_beta(1.0, y, b), color=color, lw=2.0 if color != MUTED else 1.2,
                 ls="-" if color != MUTED else "--", label=name)
    axp.axvline(1.0, color=GRID, lw=1.0, ls="--")
    axp.set_ylim(0, 2.0)
    axp.set_xlabel(r"$y$,  for $x = 1$")
    axp.legend(ncol=2, fontsize=9, loc="upper center")
    despine(axp, keep=("left", "bottom"))


@figure("eq_beta_gradient")
def eq_beta_gradient(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "One derivative for the whole family — and it is why "
                         "one algorithm covers them all",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$\dfrac{\partial d_\beta}{\partial y}(x, y) = "
         r"\dfrac{(\beta - 1)\beta\, y^{\beta - 1} "
         r"- \beta(\beta - 1)\, x\, y^{\beta - 2}}{\beta(\beta - 1)}$",
         r"only the last two terms of $d_\beta$ contain $y$"),
        (r"$\dfrac{\partial d_\beta}{\partial y}(x, y) = "
         r"y^{\beta - 1} - x\, y^{\beta - 2} = y^{\beta - 2}\,(y - x)$",
         "everything cancels; the same expression holds in the two limits",
         GREEN),
    ], top=2.92, gap=0.98, x=0.45, eq_size=15, why_off=0.42)
    rows = [
        (r"$\beta = 2$", r"$y - x$", BLUE),
        (r"$\beta = 1$", r"$1 - x / y$", GREEN),
        (r"$\beta = 0$", r"$(y - x) / y^2$", GOLD),
    ]
    ax.text(0.45, 1.02, "which reads", color=MUTED, fontsize=11, va="center")
    for i, (b, expr, color) in enumerate(rows):
        x = 2.05 + i * 2.25
        ax.text(x, 1.02, b, color=color, fontsize=12.5, va="center")
        ax.text(x + 0.85, 1.02, expr, color=INK, fontsize=12.5, va="center")
    box(ax, 0.80, 0.18, 7.40, 0.52, GREEN, "", fill="#f2fbf2")
    ax.text(W / 2, 0.44, "Zero exactly when the model matches the data — "
                         "whatever " r"$\beta$ is",
            ha="center", va="center", color=GREEN, fontsize=13)


@figure("loss_choice")
def loss_choice(fig):
    ax = canvas(fig)
    rows = [
        ("Quadratic", BLUE, r"$\beta = 2$", "Gaussian, additive",
         "default, anything on one scale"),
        ("KL", GREEN, r"$\beta = 1$", "Poisson, counts",
         "text, photon imaging, clicks"),
        ("Itakura–Saito", GOLD, r"$\beta = 0$", "multiplicative",
         "audio, anything spanning decades"),
        (r"$\ell_1$ / Huber", RED, "—", "heavy tails",
         "outliers you do not want to fit"),
    ]
    x = (0.50, 2.55, 3.60, 5.60)
    heads = ("Loss", r"$\beta$", "Noise it assumes", "Reach for it when")
    for xi, head in zip(x, heads):
        ax.text(xi, 3.05, head, color=MUTED, fontsize=11.5, va="center")
    ax.plot([0.42, 8.58], [2.86, 2.86], color=GRID, lw=1.2)
    for i, (name, color, b, model, use) in enumerate(rows):
        y = 2.56 - i * 0.56
        ax.text(x[0], y, name, color=color, fontsize=13, weight="bold",
                va="center")
        ax.text(x[1], y, b, color=INK, fontsize=12, va="center")
        ax.text(x[2], y, model, color=INK, fontsize=12, va="center")
        ax.text(x[3], y, use, color=INK, fontsize=12, va="center")
        if i:
            ax.plot([0.42, 8.58], [y + 0.28, y + 0.28], color=LIGHT, lw=1.0)
    note(ax, "The loss and the non-negativity constraint together are the "
             "model; change either one and you change what NMF finds", y=0.34,
         size=11.5)


# ==========================================================================
# 4. the optimization problem
# ==========================================================================
@figure("eq_problem")
def eq_problem(fig):
    ax = canvas(fig)
    ax.text(W / 2, 2.70, r"$\min_{W,\, H} \; D(X, WH)"
                         r"\qquad \mathrm{s.t.} \quad W \geq 0, \; H \geq 0$",
            ha="center", va="center", color=INK, fontsize=22)
    ax.annotate("", xy=(3.20, 2.35), xytext=(2.70, 1.90),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6))
    ax.text(2.75, 1.84, "loss", ha="right", va="center",
            color=BLUE, fontsize=11)
    ax.annotate("", xy=(6.60, 2.35), xytext=(6.95, 1.92),
                arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=1.6))
    ax.text(7.05, 1.86, "entrywise, on all\n$r(p + n)$ unknowns",
            ha="left", va="center", color=PURPLE, fontsize=11, linespacing=1.5)
    column(ax, 0.55, 1.40, 3.9, "What makes it hard", [
        "non-convex in " r"$(W, H)$ jointly",
        "the answer is never unique",
        "NP-hard in general",
    ], RED, leading=0.30, item_size=11.5)
    column(ax, 4.90, 1.40, 3.9, "What makes it workable", [
        "convex in " r"$W$ alone, and in $H$ alone",
        "the loss is separable",
        "cheap updates that never leave " r"$\geq 0$",
    ], GREEN, leading=0.30, item_size=11.5)
    ax.plot([4.65, 4.65], [0.25, 1.45], color=GRID, lw=1.2)


@figure("biconvex")
def biconvex(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Half the problem at a time is easy", ha="center",
            va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$F(W, H) = \frac{1}{2}\|X - WH\|_F^2$"
         r"$\;=\; \frac{1}{2}\sum_j \|x_j - W h_j\|_2^2$", ""),
        (r"with $W$ fixed:  $F$ is a sum of $n$ independent quadratics in "
         r"$h_j \geq 0$", "a non-negative least squares problem — convex"),
        (r"with $H$ fixed:  $F$ is a sum of $p$ independent quadratics in "
         r"the rows of $W \geq 0$", "the same problem, transposed — convex"),
        (r"in $(W, H)$ together:  $F$ contains the products "
         r"$W_{ik} H_{kj}$ — not convex",
         r"already visible at $p = n = r = 1$: $f(w, h) = (x - wh)^2$", RED),
    ], top=3.06, gap=0.68, x=0.45, eq_size=13, why_off=0.28)
    box(ax, 0.80, 0.06, 7.40, 0.44, GOLD, "", fill="#fdf8ef")
    ax.text(W / 2, 0.28, "Biconvex, so algorithms alternate",
            ha="center", va="center", color=GOLD, fontsize=13)


@figure("biconvex_picture")
def biconvex_picture(fig):
    w = np.linspace(0.05, 3.0, 300)
    h = np.linspace(0.05, 3.0, 300)
    WW, HH = np.meshgrid(w, h)
    F = 0.5 * (1.0 - WW * HH) ** 2

    axes = panels(
        fig, 2,
        titles=[r"$f(w, h) = \frac{1}{2}(x - wh)^2$ with $x = 1$",
                r"one slice: $h$ fixed"],
        colors=[INK, INK],
        gridspec_kw=dict(left=0.07, right=0.97, top=0.82, bottom=0.26,
                         wspace=0.24),
    )
    ax = axes[0]
    ax.contourf(WW, HH, np.log1p(F * 8), 24, cmap="Blues_r", alpha=0.9)
    ax.plot(w, 1.0 / w, color=RED, lw=2.2)
    ax.text(1.55, 1.55, "every point of this\ncurve is a global\nminimum",
            color=RED, fontsize=10, linespacing=1.4,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none",
                      alpha=0.85))
    # the alternating path
    pw, ph = 0.35, 2.6
    pts = [(pw, ph)]
    for _ in range(4):
        pw = 1.0 / ph
        pts.append((pw, ph))
        ph = 1.0 / pw
        pts.append((pw, ph))
    pts = np.array(pts)
    ax.plot(pts[:, 0], pts[:, 1], color=GREEN, lw=1.8, marker="o", ms=3.5)
    ax.text(0.66, 2.74, "alternating", color=GREEN, fontsize=10.5,
            va="center")
    ax.set_xlabel(r"$w$")
    ax.set_ylabel(r"$h$")
    ax.set_xlim(0.05, 3.0)
    ax.set_ylim(0.05, 3.0)
    despine(ax, keep=("left", "bottom"))

    ax = axes[1]
    for hv, color in ((0.6, BLUE), (1.2, GREEN), (2.2, PURPLE)):
        ax.plot(w, 0.5 * (1 - w * hv) ** 2, color=color, lw=2.0,
                label=f"$h = {hv}$")
        ax.plot(1 / hv, 0, "o", color=color, ms=6)
    ax.set_xlabel(r"$w$")
    ax.set_ylim(0, 1.3)
    ax.legend(fontsize=10, loc="upper right")
    despine(ax, keep=("left", "bottom"))

    caption_row(fig, axes, ["a non-convex valley, not a bowl",
                            "but each slice is a plain parabola"], y=0.125)


@figure("eq_ambiguity")
def eq_ambiguity(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"If $(W, H)$ is a solution, so is a whole family of "
                         "others",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$W H = (W \Lambda)(\Lambda^{-1} H)$ for any invertible "
         r"$\Lambda \in \mathbb{R}^{r \times r}$",
         r"legal whenever $W\Lambda \geq 0$ and $\Lambda^{-1} H \geq 0$"),
        (r"$\Lambda = \mathrm{Diag}(\lambda_1, \ldots, \lambda_r)$, "
         r"$\lambda_k > 0$:  $w_k \mapsto \lambda_k w_k$, "
         r"$\; h^{(k)} \mapsto \lambda_k^{-1} h^{(k)}$",
         "always legal — the scale of a component is pure convention"),
        (r"$\Lambda = \Pi$, a permutation:  the components come back in "
         r"another order",
         "so " + chr(34) + "component 3" + chr(34)
         + " means nothing across two runs"),
    ], top=3.02, gap=0.72, x=0.45, eq_size=13, why_off=0.33)
    column(ax, 0.55, 0.98, 3.9, "Part fix by", [
        r"normalising $\|w_k\|_2 = 1$ after each pass",
        "penalising factors",
    ], GREEN, leading=0.30, item_size=11.5)
    column(ax, 4.90, 0.98, 3.9, "Not fixable", [
        r"General $\Lambda$ (\"wider\" cone also fits the data)",
    ], RED, leading=0.30, item_size=11.5)
    ax.plot([4.65, 4.65], [0.08, 1.02], color=GRID, lw=1.2)


@figure("nmf_hardness")
def nmf_hardness(fig):
    ax = canvas(fig)
    rows = [
        (RED, "NP-hard", "exact NMF is NP-hard"),
        (RED, "ill-posed", "no unique solution"),
        (GOLD, "stationary points only", "algorithms are proven to "
         "reach a stationary point, not the minimum"),
        (GOLD, "sensitive to the start", "two initialisations give two "
         "different answers (both legitimate)"),
        # (GREEN, "in practice", "restart a few times and keep the best; "
        #  "regularize to pin the answer down"),
    ]
    for i, (color, name, why) in enumerate(rows):
        y = 2.95 - i * 0.56
        ax.text(2.95, y, name, ha="right", va="center", color=color,
                fontsize=13, weight="bold")
        ax.text(3.15, y, why, ha="left", va="center", color=INK, fontsize=11.5)
        if i:
            ax.plot([0.55, 8.45], [y + 0.28, y + 0.28], color=LIGHT, lw=1.0)
    note(ax, "\"converged\" means the updates stopped moving, not that the "
             "answer is the best", y=0.24, size=11.5)


@figure("algo_types")
def algo_types(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "All of them alternate; they differ in what they do "
                         "with one half",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    rows = [
        (BLUE, "Multiplicative", "one cheap rescaling of every entry",
         "monotone, never leaves " r"$\geq 0$, slow"),
        (PURPLE, "Alternating LS", "solve unconstrained, then clip at 0",
         "fast, may oscillate"),
        (GREEN, "Alternating NNLS", "solve the constrained problem exactly",
         "expensive, used as a refinement"),
        (GOLD, "HALS", "one column of " r"$W$ (one row of $H$) at a time",
         "closed form, simple, fast"),
    ]
    x = (0.50, 2.70, 5.85)
    for xi, head in zip(x, ("Family", "What one step does", "Costs you")):
        ax.text(xi, 3.00, head, color=MUTED, fontsize=11.5, va="center")
    ax.plot([0.42, 8.58], [2.80, 2.80], color=GRID, lw=1.2)
    for i, (color, name, what, cost) in enumerate(rows):
        y = 2.40 - i * 0.54
        ax.text(x[0], y, name, color=color, fontsize=13, weight="bold",
                va="center")
        ax.text(x[1], y, what, color=INK, fontsize=12, va="center")
        ax.text(x[2], y, cost, color=INK, fontsize=12, va="center")
        if i:
            ax.plot([0.42, 8.58], [y + 0.27, y + 0.27], color=LIGHT, lw=1.0)
    # box(ax, 1.20, 0.14, 6.60, 0.48, BLUE, "", fill="#f0f5fb")
    # ax.text(W / 2, 0.38, "We derive the multiplicative ones in full, then compare",
    #         ha="center", va="center", color=BLUE, fontsize=12.5)


# ==========================================================================
# 5. multiplicative updates
# ==========================================================================
@figure("eq_gradient")
def eq_gradient(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"Take $F(W, H) = \frac{1}{2}\|X - WH\|_F^2$ "
                         r"and differentiate",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$F = \frac{1}{2}\,\mathrm{tr}\!\left[(X - WH)^\top (X - WH)\right]$",
         "the Frobenius norm is a trace"),
        (r"$F = \frac{1}{2}\,\mathrm{tr}(X^\top X) "
         r"- \mathrm{tr}(H^\top W^\top X) "
         r"+ \frac{1}{2}\,\mathrm{tr}(H^\top W^\top W H)$",
         r"expand; the two cross terms are equal because "
         r"$\mathrm{tr}(A) = \mathrm{tr}(A^\top)$"),
        (r"$\dfrac{\partial}{\partial H}\,\mathrm{tr}(H^\top W^\top X) "
         r"= W^\top X$, $\qquad$ "
         r"$\dfrac{\partial}{\partial H}\,\mathrm{tr}(H^\top W^\top W H) "
         r"= 2\, W^\top W H$",
         r"the two standard identities, with $W^\top W$ symmetric"),
    ], top=2.95, gap=0.78, x=0.45, eq_size=13, why_off=0.32)
    box(ax, 0.80, 0.26, 7.40, 0.56, GREEN, "", fill="#f2fbf2")
    ax.text(W / 2, 0.54, r"$\nabla_H F = W^\top (WH - X)$"
                         r"$\qquad\qquad$ $\nabla_W F = (WH - X) H^\top$",
            ha="center", va="center", color=GREEN, fontsize=15)


@figure("eq_symmetry")
def eq_symmetry(fig):
    ax = canvas(fig)
    ax.text(W / 2, 2.95, r"$\|X - WH\|_F = \|X^\top - H^\top W^\top\|_F$",
            ha="center", va="center", color=INK, fontsize=20)
    ax.text(W / 2, 2.48, "same loss read with roles swapped",
            ha="center", va="center", color=MUTED, fontsize=11.5)

    ys = 2.05
    headers = ("", r"problem in $H$", r"problem in $W$")
    rows = [
        ("data", r"$X$", r"$X^\top$"),
        ("dictionary", r"$W$", r"$H^\top$"),
        ("codes", r"$H$", r"$W^\top$"),
    ]
    xs = (1.40, 4.10, 6.60)
    for x, head, color in zip(xs, headers, (MUTED, BLUE, PURPLE)):
        ax.text(x, ys, head, ha="center", va="center", color=color,
                fontsize=12.5)
    ax.plot([0.95, 8.05], [ys - 0.20, ys - 0.20], color=GRID, lw=1.2)
    for i, (name, a, b) in enumerate(rows):
        y = ys - 0.50 - i * 0.40
        ax.text(xs[0], y, name, ha="center", va="center", color=MUTED,
                fontsize=11.5)
        ax.text(xs[1], y, a, ha="center", va="center", color=BLUE, fontsize=14)
        ax.text(xs[2], y, b, ha="center", va="center", color=PURPLE,
                fontsize=14)
    box(ax, 0.80, 0.08, 7.40, 0.46, GREEN, "", fill="#f2fbf2")
    ax.text(W / 2, 0.31, "Derive every rule for $H$ only, then transpose it "
                         "to get the rule for $W$",
            ha="center", va="center", color=GREEN, fontsize=13)


@figure("gradient_negative")
def gradient_negative(fig):
    h = np.linspace(-0.6, 2.4, 300)
    f = 0.5 * 3.0 * (h - 1.2) ** 2
    h0, grad, eta = 0.25, 3.0 * (0.25 - 1.2), 0.42

    axes = panels(
        fig, 3,
        titles=["plain gradient step", "project back", "rescale"],
        colors=[RED, PURPLE, GREEN],
        gridspec_kw=dict(left=0.06, right=0.98, top=0.80, bottom=0.30,
                         wspace=0.18),
    )
    # a cost that wants h to go up is fine; make it want to go down instead
    f = 0.5 * 3.0 * (h + 0.4) ** 2
    grad = 3.0 * (h0 + 0.4)
    nexts = [h0 - eta * grad, max(h0 - eta * grad, 0.0), h0 * 0.35]
    for ax, hn, color in zip(axes, nexts, (RED, PURPLE, GREEN)):
        ax.plot(h, f, color=MUTED, lw=1.6)
        ax.axvspan(-0.6, 0, color=LIGHT, zorder=0)
        ax.axvline(0, color=GRID, lw=1.2)
        ax.plot(h0, 0.5 * 3.0 * (h0 + 0.4) ** 2, "o", color=INK, ms=7,
                zorder=4)
        ax.plot(hn, 0.5 * 3.0 * (hn + 0.4) ** 2, "o", color=color, ms=8,
                zorder=4)
        ax.annotate("", xy=(hn, 0.5 * 3.0 * (hn + 0.4) ** 2),
                    xytext=(h0, 0.5 * 3.0 * (h0 + 0.4) ** 2),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2.0))
        ax.text(-0.45, 2.6, "forbidden", color=MUTED, fontsize=9.5, rotation=90,
                va="center")
        ax.set_xlim(-0.6, 1.4)
        ax.set_ylim(-0.2, 3.4)
        ax.set_xlabel(r"$H_{kj}$")
        ax.set_xticks([0], ["0"])
        ax.set_yticks([])
        despine(ax, keep=("bottom",))
    caption_row(fig, axes, [
        "the step can cross zero",
        "cheap, but it kills the\ninformation in the step",
        "multiply by something\npositive: zero is unreachable"], y=0.175)
    fig.text(0.5, 0.955, r"The constraint $H \geq 0$ is what rules out plain "
                         "gradient descent",
             ha="center", va="center", color=MUTED, fontsize=12.5)


@figure("eq_mu_derivation")
def eq_mu_derivation(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Gradient descent with one step size per entry",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$H_{kj} \;\leftarrow\; H_{kj} - \eta_{kj}\, "
         r"[\nabla_H F]_{kj}$,$\qquad \eta_{kj} > 0$",
         r"nothing forces one single step size: $\eta$ may depend on $(k, j)$"),
        (r"choose  $\eta_{kj} = \dfrac{H_{kj}}{[W^\top W H]_{kj}}$",
         r"legal: $W, H \geq 0$, so the denominator is $\geq 0$"),
        (r"$H_{kj} \leftarrow H_{kj} - \dfrac{H_{kj}}{[W^\top W H]_{kj}}"
         r"\left( [W^\top W H]_{kj} - [W^\top X]_{kj} \right)$",
         r"substitute $\nabla_H F = W^\top W H - W^\top X$"),
        (r"$H_{kj} \;\leftarrow\; H_{kj}\,"
         r"\dfrac{[W^\top X]_{kj}}{[W^\top W H]_{kj}}$",
         r"the two $[W^\top W H]_{kj}$ cancel", GREEN),
    ], top=3.04, gap=0.68, x=0.45, eq_size=13.5, why_off=0.31)
    box(ax, 0.80, 0.06, 7.40, 0.44, GREEN, "", fill="#f2fbf2")
    ax.text(W / 2, 0.28, r"A product of non-negative numbers: $H$ can never "
                         "leave the orthant, and no projection is needed",
            ha="center", va="center", color=GREEN, fontsize=12.5)


@figure("mu_eta_why")
def mu_eta_why(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"Three questions about  "
                         r"$\eta_{kj} = H_{kj} \,/\, [W^\top W H]_{kj}$",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    cols = [
        (0.35, BLUE, "Why one per entry?", [
            r"the constraint $H_{kj} \geq 0$ is" "\n" "itself one per entry",
            "a single $\\eta$ must be small\nenough for the entry closest\n"
            "to zero — every other entry\nthen crawls",
            r"$\eta_{kj} \propto H_{kj}$: an entry near" "\n"
            "the wall shortens its own step",
        ]),
        (3.25, PURPLE, "Why this value?", [
            r"$[W^\top W H]_{kj}$ adds up $r$ non-negative"
            "\n" r"terms, one of which is $[W^\top W]_{kk} H_{kj}$",
            r"so $\eta_{kj} \leq 1 / [W^\top W]_{kk}$",
            "and that bound is the exact step for a\n"
            r"parabola of curvature $[W^\top W]_{kk}$: this is"
            "\n" r"a Newton step along $H_{kj}$, damped by"
            "\n" "the other entries",
        ]),
        (6.15, GREEN, "Just so it cancels?", [
            "the cancellation is how it was\nfound, not why it is right",
            "the next section builds an upper\n"
            "bound on $F$ and minimizes it: out\n"
            r"comes the same $\eta$, with nothing" "\n" "chosen by hand",
            "and, as a bonus, a proof that the\nloss falls at every pass",
        ]),
    ]
    for x, color, title, items in cols:
        column(ax, x, 2.96, 2.60, title, items, color, item_size=10.5,
               title_size=13, leading=0.21)
    note(ax, r"shorter than a Newton step, and never across zero: "
             r"that is the whole design of $\eta$", y=0.20, size=11.5)


@figure("eq_mu_frobenius")
def eq_mu_frobenius(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Lee and Seung, 1999 — the whole algorithm, "
                         r"assuming $X \geq 0$",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 3.12, r"Frobenius norm $\|X - WH\|_F^2$", ha="center",
            va="center", color=BLUE, fontsize=13)
    ax.text(2.95, 2.30, r"$W \;\leftarrow\; W \odot "
                        r"\dfrac{X H^\top}{W H H^\top}$",
            ha="center", va="center", color=INK, fontsize=22)
    ax.text(6.25, 2.30, r"$H \;\leftarrow\; H \odot "
                        r"\dfrac{W^\top X}{W^\top W H}$",
            ha="center", va="center", color=INK, fontsize=22)
    ax.text(W / 2, 1.42, r"$\odot$ and the fraction bar are entrywise",
            ha="center", va="center", color=MUTED, fontsize=11.5)

    rows = [
        (GREEN, "ratio > 1", "the model is too small here: grow the entry"),
        (RED, "ratio < 1", "the model is too big here: shrink it"),
        (BLUE, "ratio = 1", r"stop — this is exactly $\nabla_H F = 0$ "
         r"in direction $kj$"),
    ]
    for i, (color, when, what) in enumerate(rows):
        y = 1.02 - i * 0.30
        ax.text(2.90, y, when, ha="right", va="center", color=color,
                fontsize=11.5, weight="bold")
        ax.text(3.10, y, what, ha="left", va="center", color=INK, fontsize=11.5)
    note(ax, r"one pass costs two matrix products per factor: "
             r"$\mathcal{O}(pnr)$", y=0.14, size=11)


@figure("eq_mu_general")
def eq_mu_general(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "The same recipe works for every loss on this deck",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"split the gradient:  $\nabla_H D = \nabla^{+} - \nabla^{-}$ "
         r"with $\nabla^{+} \geq 0$ and $\nabla^{-} \geq 0$",
         "always possible, and usually obvious by inspection"),
        (r"$H \;\leftarrow\; H \odot \dfrac{\nabla^{-}}{\nabla^{+}}$",
         r"same algebra as before, with $\eta = H / \nabla^{+}$", GREEN),
    ], top=3.00, gap=0.86, x=0.45, eq_size=14, why_off=0.36)
    rows = [
        ("Frobenius", BLUE, r"$W^\top W H$", r"$W^\top X$"),
        ("KL", GREEN, r"$W^\top \mathbf{1}$",
         r"$W^\top \left( X \oslash W H \right)$"),
        ("weighted", PURPLE, r"$W^\top (\Sigma \odot WH)$",
         r"$W^\top (\Sigma \odot X)$"),
        ("regularized", GOLD, r"$(W^\top W + \mu I_r) H$",
         r"$W^\top X - \lambda \mathbf{1}$"),
    ]
    xs = (1.35, 3.80, 6.40)
    for x, head in zip(xs, ("loss", r"$\nabla^{+}$", r"$\nabla^{-}$")):
        ax.text(x, 1.35, head, ha="center", va="center", color=MUTED,
                fontsize=11.5)
    ax.plot([0.80, 8.20], [1.16, 1.16], color=GRID, lw=1.2)
    for i, (name, color, p, m) in enumerate(rows):
        y = 0.94 - i * 0.26
        ax.text(xs[0], y, name, ha="center", va="center", color=color,
                fontsize=11.5)
        ax.text(xs[1], y, p, ha="center", va="center", color=INK, fontsize=11.5)
        ax.text(xs[2], y, m, ha="center", va="center", color=INK, fontsize=11.5)


# ==========================================================================
# 6. why it works: majorize–minimize
# ==========================================================================
@figure("alternate_vs_majorize")
def alternate_vs_majorize(fig):
    ax = canvas(fig)
    box(ax, 0.35, 1.30, 3.80, 1.88, PURPLE, "", fill="#faf7ff")
    ax.text(2.25, 2.96, "outer loop: alternate", ha="center", va="center",
            color=PURPLE, fontsize=12.5, weight="bold")
    box(ax, 0.60, 2.22, 2.90, 0.48, PURPLE,
        r"$H \leftarrow$ better $H$,  $W$ frozen", size=11.5, lw=1.4)
    box(ax, 0.60, 1.50, 2.90, 0.48, PURPLE,
        r"$W \leftarrow$ better $W$,  $H$ frozen", size=11.5, lw=1.4)
    ax.add_patch(FancyArrowPatch((3.74, 2.44), (3.74, 1.76),
                                 arrowstyle="<|-|>", mutation_scale=12,
                                 linewidth=1.4, color=PURPLE, zorder=5,
                                 connectionstyle="arc3,rad=-0.85"))
    ax.text(0.35, 1.08, "each half-step minimizes over a subset of the variables,\n"
                        "and current point is one of the candidates",
            color=MUTED, fontsize=10.5, va="top", linespacing=1.55)

    arrow(ax, (4.32, 2.24), (4.86, 2.24), color=MUTED, lw=1.8)
    ax.text(4.59, 2.50, "but how?", ha="center", va="center", color=MUTED,
            fontsize=10)

    box(ax, 5.00, 1.30, 3.60, 1.88, GREEN, "", fill="#f6fdf6")
    ax.text(6.80, 2.96, "inner step: one MU update", ha="center", va="center",
            color=GREEN, fontsize=12.5, weight="bold")
    inner = [
        r"Do not solve the frozen half exactly",
        r"Build $G(H \mid \bar{H}) \geq F(H)$, touching at $\bar{H}$",
        r"Minimize $G$ instead (easier as separable)",
        r"The minimizer of $G$ is the multiplicative rule",
    ]
    for i, line in enumerate(inner):
        y = 2.64 - i * 0.33
        ax.text(5.22, y, "—", color=GREEN, fontsize=10.5, va="center")
        ax.text(5.44, y, line, color=INK, fontsize=10.5, va="center")



@figure("mm_idea")
def mm_idea(fig):
    h = np.linspace(0.95, 4.20, 600)
    fig.text(0.5, 0.955, r"$G(h \mid \bar{h})$ is a function of $h$ alone: "
                         r"the bar side is the point we sit at now, frozen",
             ha="center", va="center", color=MUTED, fontsize=12)

    def Ff(hv):
        return 0.50 * (hv - 1.40) ** 2 + 0.45 / hv

    def dF(hv):
        return 1.00 * (hv - 1.40) - 0.45 / hv ** 2

    ax = fig.add_axes([0.07, 0.20, 0.54, 0.62])
    ax.plot(h, Ff(h), color=INK, lw=2.4, zorder=3)
    ax.text(4.18, Ff(4.18) + 0.12, r"$F$", color=INK, fontsize=13,
            ha="right", va="bottom")

    # one fixed curvature that majorizes F everywhere on the plot
    c = 1.02 * float(np.max(0.5 * (1.00 + 0.90 / h ** 3)))
    hb = 3.95
    for step, color in enumerate((PURPLE, GOLD, GREEN)):
        d = h - hb
        g = Ff(hb) + dF(hb) * d + c * d ** 2
        assert (g >= Ff(h) - 1e-9).all()
        hn = hb - dF(hb) / (2 * c)
        gn = Ff(hb) + dF(hb) * (hn - hb) + c * (hn - hb) ** 2
        shown = np.abs(d) < 1.9
        ax.plot(h[shown], g[shown], color=color, lw=1.6, ls="--", zorder=2)
        ax.plot(hb, Ff(hb), "o", color=color, ms=7, zorder=4)
        ax.annotate("", xy=(hn, gn), xytext=(hb, Ff(hb)),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8))
        if step == 0:
            ax.text(1.25, 3.70, r"$G(\cdot \mid \bar{h})$: the dashed"
                    "\n" "curves, one per step",
                    color=color, fontsize=11.5, ha="left", va="top",
                    linespacing=1.5)
        hb = float(hn)
    ax.plot(hb, Ff(hb), "o", color=GREEN, ms=7, zorder=4)
    ax.set_xlabel(r"$h$")
    ax.set_xlim(0.95, 4.25)
    ax.set_ylim(0.55, 4.45)
    ax.set_yticks([])
    despine(ax, keep=("bottom",))
    ax.set_title("the surrogate touches, and lies above", color=INK,
                 fontsize=12.5, pad=8)

    side = fig.add_axes([0.65, 0.18, 0.33, 0.64])
    side.axis("off")
    side.text(0, 1.0, "Majorize", color=PURPLE, fontsize=13, weight="bold",
              va="top")
    side.text(0, 0.87, r"build $G(h \mid \bar{h}) \geq F(h)$" "\n"
                       r"with $G(\bar{h} \mid \bar{h}) = F(\bar{h})$",
              color=INK, fontsize=11.5, va="top", linespacing=1.6)
    side.text(0, 0.57, "Minimize", color=GREEN, fontsize=13, weight="bold",
              va="top")
    side.text(0, 0.44, r"$h^{+} = \arg\min_h G(h \mid \bar{h})$" "\n"
                       "then start again from " r"$h^{+}$",
              color=INK, fontsize=11.5, va="top", linespacing=1.6)
    side.text(0, 0.14, "the point: $G$ is chosen\nto be easy — separable,\n"
                       "and minimised in closed form", color=MUTED,
              fontsize=10.5, va="top", linespacing=1.5)


@figure("eq_mm_monotone")
def eq_mm_monotone(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Why majorize–minimize can never go uphill",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(0.45, 3.02, r"given  $G(h \mid \bar{h}) \geq F(h)$ for all $h$,"
                        r"$\quad$ and $\;G(\bar{h} \mid \bar{h}) "
                        r"= F(\bar{h})$,"
                        r"$\quad$ set $h^{+} = \arg\min_h G(h \mid \bar{h})$",
            color=INK, fontsize=12.5, va="center")
    rows = [
        (r"$F(h^{+}) \;\leq\; G(h^{+} \mid \bar{h})$",
         "because $G$ majorizes $F$ everywhere", BLUE),
        (r"$G(h^{+} \mid \bar{h}) \;\leq\; G(\bar{h} \mid \bar{h})$",
         r"because $h^{+}$ minimizes $G$, and $\bar{h}$ is one candidate",
         PURPLE),
        (r"$G(\bar{h} \mid \bar{h}) \;=\; F(\bar{h})$",
         "because the two touch at the current point", GOLD),
    ]
    for i, (eq, why, color) in enumerate(rows):
        y = 2.42 - i * 0.52
        ax.text(0.80, y, eq, color=color, fontsize=14, va="center")
        ax.text(4.40, y, why, color=MUTED, fontsize=11, va="center")
    ax.plot([0.70, 8.30], [0.88, 0.88], color=GRID, lw=1.2)
    ax.text(W / 2, 0.58, r"$F(h^{+}) \;\leq\; F(\bar{h})$", ha="center",
            va="center", color=GREEN, fontsize=18)
    note(ax, "no step size, no line search, and the loss decreases every "
             "single pass", y=0.18, size=11.5)


@figure("eq_jensen_split")
def eq_jensen_split(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"The trick: write $[Wh]_i$ as an average, then use "
                         "convexity",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$\lambda_{ik} = \dfrac{W_{ik}\, \bar{h}_k}{[W \bar{h}]_i}$,"
         r"$\qquad \lambda_{ik} \geq 0$, $\qquad "
         r"\sum_{k=1}^{r} \lambda_{ik} = 1$",
         r"a probability over the $r$ components, built at the current "
         r"$\bar{h}$"),
        (r"$[Wh]_i = \sum_k W_{ik} h_k "
         r"= \sum_k \lambda_{ik}\,"
         r"\dfrac{h_k}{\bar{h}_k}\,[W\bar{h}]_i$",
         r"multiply and divide by $W_{ik}\bar{h}_k$: the $i$-th model entry "
         r"is a convex combination"),
        (r"$\varphi\!\left(\sum_k \lambda_{ik} z_{ik}\right) \;\leq\; "
         r"\sum_k \lambda_{ik}\, \varphi(z_{ik})$"
         r"$\qquad$ for any convex $\varphi$",
         r"Jensen — and the right-hand side is separable in "
         r"$h_1, \ldots, h_r$", GREEN),
    ], top=2.96, gap=0.78, x=0.45, eq_size=14, why_off=0.34)
    box(ax, 0.60, 0.10, 7.80, 0.52, GREEN, "", fill="#f2fbf2")
    ax.text(W / 2, 0.36, r"$z_{ik} = \dfrac{h_k}{\bar{h}_k}\,[W\bar{h}]_i$"
                         r"$\qquad$ — one number per component, and "
                         r"$z_{ik} = [W\bar h]_i$ when $h = \bar{h}$",
            ha="center", va="center", color=GREEN, fontsize=13)


@figure("jensen_picture")
def jensen_picture(fig):
    z = np.linspace(0.1, 3.4, 300)
    phi = (1.4 - z) ** 2
    zs = np.array([0.5, 1.6, 2.9])
    lam = np.array([0.45, 0.33, 0.22])
    zbar = float(lam @ zs)
    pbar = float(lam @ (1.4 - zs) ** 2)

    ax = fig.add_axes([0.07, 0.24, 0.47, 0.58])
    ax.plot(z, phi, color=INK, lw=2.2)
    ax.plot([zs[0], zs[-1]], [(1.4 - zs[0]) ** 2, (1.4 - zs[-1]) ** 2],
            color=GRID, lw=1.2)
    for zi, li, color in zip(zs, lam, (BLUE, GREEN, PURPLE)):
        ax.plot(zi, (1.4 - zi) ** 2, "o", color=color, ms=7, zorder=4)
        ax.text(zi, (1.4 - zi) ** 2 + 0.20, r"$z_{i%d}$"
                % (int(np.where(zs == zi)[0][0]) + 1),
                color=color, fontsize=11, ha="center", va="bottom")
    ax.plot(zbar, (1.4 - zbar) ** 2, "o", color=GOLD, ms=8, zorder=5)
    ax.plot(zbar, pbar, "o", color=RED, ms=8, zorder=5)
    ax.annotate("", xy=(zbar, pbar), xytext=(zbar, (1.4 - zbar) ** 2),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1.6))
    ax.text(zbar + 0.42, (pbar + (1.4 - zbar) ** 2) / 2 + 0.42,
            "the gap\nJensen buys", color=RED, fontsize=10.5, va="center",
            linespacing=1.4)
    ax.text(zbar, -0.55, r"$[Wh]_i = \sum_k \lambda_{ik} z_{ik}$", color=GOLD,
            fontsize=11, ha="center")
    ax.set_ylim(-0.30, 2.9)
    ax.set_yticks([])
    ax.set_xticks([])
    despine(ax)
    ax.set_title(r"a convex $\varphi$, here $\varphi(u) = (x_i - u)^2$",
                 color=INK, fontsize=12, pad=8)

    # the weights, as a stacked bar
    axb = fig.add_axes([0.63, 0.34, 0.33, 0.30])
    left = 0.0
    for li, color, name in zip(lam, (BLUE, GREEN, PURPLE),
                               (r"$\lambda_{i1}$", r"$\lambda_{i2}$",
                                r"$\lambda_{i3}$")):
        axb.barh(0, li, left=left, color=color, height=0.5)
        axb.text(left + li / 2, 0, name, ha="center", va="center",
                 color="white", fontsize=11)
        left += li
    axb.set_xlim(0, 1)
    axb.set_yticks([])
    axb.set_xticks([0, 1])
    despine(axb, keep=("bottom",))
    axb.set_title(r"$\sum_k \lambda_{ik} = 1$", color=INK, fontsize=12, pad=8)
    fig.text(0.795, 0.25, r"the weights come from $\bar{h}$," "\n"
                          "so they are constants here", ha="center", va="top",
             color=MUTED, fontsize=10.5, linespacing=1.5)
    fig.text(0.5, 0.085, "Jensen replaces one hard term coupling all "
                         r"$r$ components by $r$ easy ones",
             ha="center", va="top", color=MUTED, fontsize=11.5)


@figure("eq_surrogate_frobenius")
def eq_surrogate_frobenius(fig):
    ax = canvas(fig)
    box(ax, 0.50, 2.92, 8.00, 0.52, PURPLE, "", fill="#faf7ff", lw=1.6)
    ax.text(W / 2, 3.18, r"a $\mathbf{surrogate}$ is an upper bound that "
                         r"touches:  $G(h \mid \bar{h}) \geq F(h)$  for all "
                         r"$h \geq 0$,  with equality at $h = \bar{h}$",
            ha="center", va="center", color=PURPLE, fontsize=12.5)
    steps(ax, [
        (r"$F(h) = \frac{1}{2}\|x - Wh\|_2^2 = \frac{1}{2}\sum_i "
         r"\left( x_i - \sum_k W_{ik} h_k \right)^2$",
         r"Minimize one column $h$ of $H$, with $W$ frozen — every other column independent"),
        (r"$[Wh]_i = \sum_k \lambda_{ik} z_{ik}$,$\qquad$ "
         r"$\lambda_{ik} = \dfrac{W_{ik} \bar{h}_k}{[W\bar{h}]_i}$,"
         r"$\qquad z_{ik} = \dfrac{h_k}{\bar{h}_k}\,[W\bar{h}]_i$",
         r"$\lambda_{ik} \geq 0$ and $\sum_k \lambda_{ik} = 1$: a weighted "
         r"average of the $r$ components", GREEN),
    ], top=2.30, gap=1.30, x=0.45, eq_size=13, why_size=10.5, why_off=0.46)
    ax.text(W / 2, 1.62, r"the obstacle: one square holds all $r$ entries "
                         r"of $h$ at once, so nothing is minimized entry "
                         r"by entry",
            ha="center", va="center", color=RED, fontsize=11.5)
    note(ax, r"Loss is untouched: model entry  $[Wh]_i$ is written as an average, then convexity is used.",
         y=0.16, size=11.5)


@figure("eq_surrogate_jensen")
def eq_surrogate_jensen(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"Convexity turns one coupled square into $r$ "
                         r"separate ones",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$\left( x_i - \sum_k \lambda_{ik} z_{ik} \right)^2 \;\leq\; "
         r"\sum_k \lambda_{ik} \left( x_i - z_{ik} \right)^2$",
         r"$u \mapsto (x_i - u)^2$ is convex, so the square of an average is "
         r"below the average of the squares"),
        (r"$G(h \mid \bar{h}) = \frac{1}{2} \sum_i \sum_k \lambda_{ik} "
         r"\left( x_i - \dfrac{h_k}{\bar{h}_k}[W\bar{h}]_i \right)^2 "
         r"\;\geq\; F(h)$",
         r"term $k$ holds $h_k$ and nothing else: a sum of $r$ independent "
         r"parabolas"),
        (r"$z_{ik} = [W\bar{h}]_i$ when $h = \bar{h}$,$\qquad$ so "
         r"$G(\bar{h} \mid \bar{h}) = F(\bar{h})$",
         r"the bound touches at the current point: a valid surrogate", GREEN),
    ], top=2.90, gap=1.00, x=0.45, eq_size=13, why_size=10.5, why_off=0.44)
    note(ax, r"the approximation is in the coupling, never in the loss: "
             r"$G$ is never below $F$, and the two agree at $\bar{h}$",
         y=0.16, size=11.5)


@figure("eq_surrogate_minimize")
def eq_surrogate_minimize(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Minimizing the surrogate gives back the "
                         "multiplicative rule",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$\dfrac{\partial G}{\partial h_k} = \sum_i "
         r"\dfrac{W_{ik}\bar{h}_k}{[W\bar{h}]_i} \cdot 2 "
         r"\left( x_i - \dfrac{h_k}{\bar{h}_k}[W\bar{h}]_i \right) \cdot "
         r"\left( -\dfrac{[W\bar{h}]_i}{\bar{h}_k} \right)$",
         r"chain rule; only the $k$-th parabola contains $h_k$"),
        (r"$\dfrac{\partial G}{\partial h_k} = -2 \sum_i W_{ik} "
         r"\left( x_i - \dfrac{h_k}{\bar{h}_k}[W\bar{h}]_i \right) "
         r"= -2\left( [W^\top x]_k - \dfrac{h_k}{\bar{h}_k}"
         r"[W^\top W \bar{h}]_k \right)$",
         r"the factors $[W\bar{h}]_i$ and $\bar{h}_k$ cancel"),
        (r"set to zero:  $h_k = \bar{h}_k\,"
         r"\dfrac{[W^\top x]_k}{[W^\top W \bar{h}]_k}$",
         r"and $\partial^2 G / \partial h_k^2 = 2[W^\top W\bar h]_k / "
         r"\bar{h}_k > 0$: it is the minimum", GREEN),
    ], top=2.98, gap=0.80, x=0.45, eq_size=13, why_off=0.36)
    box(ax, 0.70, 0.10, 7.60, 0.50, GREEN, "", fill="#f2fbf2")
    ax.text(W / 2, 0.35, "The same rule as before — now with a proof that "
                         "every pass lowers the loss",
            ha="center", va="center", color=GREEN, fontsize=13)


@figure("mu_eta_surrogate")
def mu_eta_surrogate(fig):
    # a small instance whose exact coordinate minimum is negative, so the
    # difference between the two steps is visible
    k, r = 0, 3
    for seed in range(400):
        rng = np.random.default_rng(seed)
        Wm = rng.random((6, r)) ** 1.3
        x = rng.random(6) ** 1.3
        hb = 0.25 + rng.random(r)
        grad = Wm.T @ (Wm @ hb - x)
        tN = hb - grad / (Wm.T @ Wm).diagonal()
        tMU = hb * (Wm.T @ x) / (Wm.T @ Wm @ hb)
        if tN[k] < -0.20 and 0.05 < tMU[k] < hb[k] - 0.10:
            break
    Wh = Wm @ hb

    def Fk(t):
        t = np.atleast_1d(np.asarray(t, dtype=float))
        hh = np.repeat(hb[:, None], t.size, 1)
        hh[k] = t
        out = 0.5 * ((Wm @ hh - x[:, None]) ** 2).sum(0)
        return out[0] if out.size == 1 else out

    def Gk(t):
        t = np.atleast_1d(np.asarray(t, dtype=float))
        tot = np.zeros(t.size)
        for l in range(r):
            hl = t if l == k else np.full(t.size, hb[l])
            tot += ((Wm[:, l] * hb[l] / Wh)[:, None]
                    * (x[:, None] - np.outer(Wh, hl / hb[l])) ** 2).sum(0)
        out = 0.5 * tot
        return out[0] if out.size == 1 else out

    t = np.linspace(min(tN[k] - 0.25, -0.35), hb[k] + 0.75, 400)
    assert (Gk(t) >= Fk(t) - 1e-9).all()
    assert abs(float(Gk(hb[k])) - float(Fk(hb[k]))) < 1e-9

    ax = fig.add_axes([0.065, 0.215, 0.50, 0.595])
    ax.axvspan(t[0], 0, color=LIGHT, zorder=0)
    ax.axvline(0, color=GRID, lw=1.2)
    ax.plot(t, Fk(t), color=INK, lw=2.4, zorder=3)
    ax.plot(t, Gk(t), color=PURPLE, lw=2.0, ls="--", zorder=3)
    ax.text(t[-1], float(Fk(t[-1])), r" $F$", color=INK, fontsize=12.5,
            va="center")
    ax.text(t[0] + 0.33, float(Gk(t[0] + 0.33)) + 0.06,
            r"$G(\cdot \mid \bar{H})$", color=PURPLE, fontsize=12.5,
            ha="left", va="bottom")
    labels = ((hb[k], INK, r"$\bar{H}_{kj}$", 0.06, "left", "top"),
              (tMU[k], GREEN, "MU step", 0.0, "center", "top"),
              (tN[k], RED, "Newton step", 0.0, "center", "bottom"))
    for tt, color, name, dx, ha, va in labels:
        ax.plot(tt, float(Fk(tt)), "o", color=color, ms=7.5, zorder=5)
        dy = 0.07 if va == "bottom" else (-0.10 if va == "top" else 0.0)
        ax.text(tt + dx, float(Fk(tt)) + dy, name, color=color, fontsize=10.5,
                ha=ha, va=va)
    ax.plot(tMU[k], float(Gk(tMU[k])), "o", color=PURPLE, ms=7.5, zorder=5)
    ax.annotate("", xy=(tMU[k], float(Gk(tMU[k]))),
                xytext=(hb[k], float(Gk(hb[k]))),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.8))
    ax.text(t[0] + 0.07, float(Gk(t).max()) * 0.90, "forbidden", color=MUTED,
            fontsize=10, rotation=90, va="top")
    ax.set_xlabel(r"one entry $H_{kj}$, the others frozen")
    ax.set_ylim(float(Fk(t).min()) - 0.26, float(Gk(t).max()) * 1.02)
    ax.set_yticks([])
    ax.set_xticks([0], ["0"])
    despine(ax, keep=("bottom",))
    ax.set_title("the surrogate is the steeper parabola", color=INK,
                 fontsize=12.5, pad=8)

    side = fig.add_axes([0.615, 0.195, 0.375, 0.615])
    side.axis("off")
    side.text(0, 1.0, "The two curvatures", color=PURPLE, fontsize=12.5,
              weight="bold", va="top")
    side.text(0, 0.86, r"$G'' = [W^\top W \bar{H}]_{kj} / \bar{H}_{kj}$"
                       r"$\;\geq\; [W^\top W]_{kk} = F''$",
              color=INK, fontsize=11.5, va="top")
    side.text(0, 0.73, "The parabola is stiffer", color=MUTED, fontsize=10.5, va="top", linespacing=1.5)
    side.text(0, 0.42, "The step is short", color=GREEN, fontsize=12.5,
              weight="bold", va="top")
    side.text(0, -0.02, "Newton on $F$ can land in the negatves,",
              color=RED, fontsize=10.5, va="top")
    fig.text(0.5, 0.055, r"$\eta$ is the step that lands on the minimum of an upper bound",
             ha="center", va="center", color=MUTED, fontsize=11.5)


@figure("mu_algorithm")
def mu_algorithm(fig):
    ax = canvas(fig)
    lines = [
        (BLUE, r"input", r"$X \geq 0$, rank $r$, a loss, a tolerance"),
        (BLUE, r"init", r"$W_0 > 0$, $H_0 > 0$  (strictly: zeros are absorbing)"),
        (INK, r"repeat", r"$H \leftarrow H \odot \nabla_H^{-} \oslash \nabla_H^{+}$"),
        (INK, "", r"$W \leftarrow W \odot \nabla_W^{-} \oslash \nabla_W^{+}$"),
        (INK, "", r"optionally rescale: $w_k \leftarrow w_k / \|w_k\|$, $\; h^{(k)} \leftarrow \|w_k\|\, h^{(k)}$"),
        (GOLD, r"until", r"$D$ stops decreasing, or the budget runs out"),
        (GREEN, r"output", r"$(W, H)$  stationary point (not always the minimum)"),
    ]
    box(ax, 0.55, 0.78, 7.90, 2.46, BLUE, "", fill="white", lw=1.6)
    for i, (color, key, text) in enumerate(lines):
        y = 2.96 - i * 0.345
        ax.text(1.75, y, key, ha="right", va="center", color=color,
                fontsize=12, weight="bold" if key else "normal")
        ax.text(1.95, y, text, ha="left", va="center", color=INK, fontsize=12)
    note(ax, r"cost per pass: a handful of $p \times n$ products, $\mathcal{O}(pnr)$", y=0.46, size=11.5)
    note(ax, "no step size to tune", y=0.16, size=11.5)


@figure("mu_convergence")
def mu_convergence(fig):
    rng = np.random.default_rng(0)
    Wt = np.abs(rng.normal(0, 1, (40, 4))) ** 1.3
    Ht = np.abs(rng.normal(0, 1, (4, 60))) ** 1.3
    X = Wt @ Ht + 0.05 * rng.random((40, 60))

    _, _, fro = _mu(X, 4, 400, seed=1, trace=True)
    _, _, kl = _mu(X, 4, 400, seed=1, loss="kl", trace=True)

    axes = panels(
        fig, 2,
        titles=[r"Frobenius, $\frac{1}{2}\|X - WH\|_F^2$",
                r"KL, $\mathrm{KL}(X, WH)$"],
        colors=[BLUE, GREEN],
        gridspec_kw=dict(left=0.09, right=0.97, top=0.80, bottom=0.26, wspace=0.26),
    )
    for ax, trace, color in zip(axes, (fro, kl), (BLUE, GREEN)):
        ax.semilogy(np.arange(1, len(trace) + 1), trace, color=color, lw=2.2)
        ax.set_xlabel("pass")
        despine(ax, keep=("left", "bottom"))
    axes[0].set_ylabel("loss")

    fig.text(0.5, 0.955, "Monotone by construction",
             ha="center", va="center", color=MUTED, fontsize=12.5)


@figure("init_strategies")
def init_strategies(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "The answer you get is the answer your start led to",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    rows = [
        (RED, "identity, constants", "degenerate: every column of "
         r"$W$ identical, and MU cannot break the tie"),
        (GOLD, "random positive", "the usual default; restart a few times and "
         "keep the best"),
        (GREEN, "SVD, then truncate", "NNDSVD: take the leading singular "
         "vectors, keep the positive part"),
        (GREEN, r"$r$ columns of $X$", "cheap, and already in the right cone"),
        (BLUE, "a clustering", r"run k-means with $K = r$: the centroids "
         r"become $W$, the assignments $H$"),
    ]
    for i, (color, name, why) in enumerate(rows):
        y = 2.95 - i * 0.56
        ax.text(2.90, y, name, ha="right", va="center", color=color,
                fontsize=12.5, weight="bold")
        ax.text(3.10, y, why, ha="left", va="center", color=INK, fontsize=11.5)
        if i:
            ax.plot([0.45, 8.55], [y + 0.28, y + 0.28], color=LIGHT, lw=1.0)
    note(ax, "never start at exactly zero, and never start symmetric", y=0.24,
         size=11.5)


@figure("init_geometry")
def init_geometry(fig):
    rng = np.random.default_rng(3)
    n = 70
    arms = np.array([[1.00, 0.30], [0.32, 1.00]]).T     # columns are the arms
    XA = np.outer(arms[:, 0], 0.25 + rng.random(n) * 1.05) \
        + rng.normal(0, 0.035, (2, n))
    XB = np.outer(arms[:, 1], 0.25 + rng.random(n) * 1.05) \
        + rng.normal(0, 0.035, (2, n))
    X = np.maximum(np.c_[XA, XB], 1e-3)

    # for "r columns of X", show a draw that lands twice on the same arm
    same = next(s for s in range(200)
                if len(set((np.random.default_rng(s)
                            .choice(2 * n, size=2, replace=False) < n)
                           .tolist())) == 1)

    strategies = [
        ("constants", RED, "constant", 0,
         "one single ray: MU can\nnever break the tie"),
        ("random", GOLD, "random", 0,
         "two arbitrary rays, with no\nrelation to the data"),
        ("NNDSVD", GREEN, "nndsvd", 0,
         "deterministic: the mean\ndirection, then the next one"),
        (r"$r$ columns of $X$", GREEN, "cols", same,
         "two real data points — here\nboth from the same arm"),
        ("k-means", BLUE, "kmeans", 0,
         "one centroid per cluster:\nthe rays land on the arms"),
    ]
    axes = panels(fig, 5, titles=[s[0] for s in strategies],
                  colors=[s[1] for s in strategies],
                  gridspec_kw=dict(left=0.040, right=0.988, top=0.775,
                                   bottom=0.335, wspace=0.17))
    lim = 1.62
    for ax, (name, color, how, seed, _) in zip(axes, strategies):
        ax.scatter(X[0], X[1], s=4.5, color=MUTED, alpha=0.5, zorder=1)
        Wi, _ = _init(X, 2, seed, how)
        for kk in range(2):
            v = Wi[:, kk] / (np.linalg.norm(Wi[:, kk]) + EPS) * lim * 0.90
            ax.annotate("", xy=(float(v[0]), float(v[1])), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=2.2),
                        zorder=4)
        ax.set_xlim(-0.13, lim)
        ax.set_ylim(-0.13, lim)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        despine(ax, keep=("left", "bottom"))
    caption_row(fig, axes, [s[4] for s in strategies], y=0.255, size=10)
    fig.text(0.5, 0.955, "Columns of $W$",
             ha="center", va="center", color=MUTED, fontsize=12.5)


@figure("init_faces")
def init_faces(fig):
    imgs, Xf = _faces(200)
    X = Xf.T
    r = 6
    rows = [
        ("constants", RED, "constant", "every column identical"),
        ("random", GOLD, "random", "pure noise"),
        ("NNDSVD", GREEN, "nndsvd", "singular vectors, positive part kept"),
        (r"$r$ columns of $X$", BLUE, "cols", "six real faces"),
        ("k-means", PURPLE, "kmeans", "six centroids"),
    ]
    fig.text(0.5, 0.95, f"The same $W_0$, built five ways.\n$r = {r}$ columns drawn as 64 × 64 images",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    size, step = 0.40, 0.44
    for i, (name, color, how, why) in enumerate(rows):
        yc = 2.86 - i * 0.515
        fig.text(1.42 / W, yc / H, name, ha="right", va="center", color=color,
                 fontsize=11.5, weight="bold")
        Wi, _ = _init(X, r, 0, how)
        for kk in range(r):
            x0 = 1.56 + kk * step
            ax = fig.add_axes([x0 / W, (yc - size / 2) / H, size / W, size / H])
            ax.imshow(Wi[:, kk].reshape(64, 64), cmap="gray_r", vmin=0,
                      interpolation="nearest")
            _bare(ax)
        fig.text(4.42 / W, yc / H, why, ha="left", va="center", color=INK,
                 fontsize=10)
    fig.text(0.5, 0.055, "five different starts, five different stationary "
                         "points: the start is part of the model",
             ha="center", va="center", color=MUTED, fontsize=11.5)
    _credit(fig, "data: Olivetti faces, AT&T Cambridge")


@figure("init_compare")
def init_compare(fig):
    n_faces = 200
    imgs, Xf = _faces(n_faces)
    X = Xf.T
    r, iters = 10, 150
    runs = [_mu(X, r, iters, seed=s, trace=True)[2] for s in range(5)]
    mean_run = np.mean(runs, 0)
    others = [
        ("constants", RED, _mu(X, r, iters, init="constant", trace=True)[2]),
        ("NNDSVD", GREEN, _mu(X, r, iters, init="nndsvd", trace=True)[2]),
        (r"$r$ columns of $X$", BLUE,
         _mu(X, r, iters, init="cols", trace=True)[2]),
        ("k-means", PURPLE, _mu(X, r, iters, init="kmeans", trace=True)[2]),
    ]

    ax = fig.add_axes([0.105, 0.215, 0.385, 0.575])
    for i, trace in enumerate(runs):
        ax.plot(trace, color=GOLD, lw=1.3, alpha=0.75,
                label="random starts" if i == 0 else None)
    for name, color, trace in others:
        ax.plot(trace, color=color, lw=2.1, label=name)
    ax.set_xlabel("pass")
    ax.set_ylabel(r"$\frac{1}{2}\|X - WH\|_F^2$")
    ax.set_yscale("log")
    ax.legend(fontsize=9.5, loc="upper right")
    despine(ax, keep=("left", "bottom"))
    ax.set_title(f"{n_faces} faces, r = {r}", color=INK, fontsize=12, pad=8)

    def head_start(trace):
        reached = np.nonzero(mean_run <= trace[0])[0]
        return int(reached[0]) + 1 if reached.size else iters

    finals = np.array([t[-1] for t in runs])
    rows = [("random, 5 starts", GOLD, f"{finals.min():.1f} to {finals.max():.1f}",
             "a spread of "
             f"{100 * (finals.max() / finals.min() - 1):.0f}% on the same data")]
    for name, color, trace in others:
        why = (f"stuck: every column of $W$ stays identical"
               if name == "constants"
               else f"starts {head_start(trace)} passes ahead of a random one")
        rows.append((name, color, f"{trace[-1]:.1f}", why))

    side = fig.add_axes([0.545, 0.175, 0.445, 0.645])
    side.axis("off")
    side.text(0, 1.0, f"loss after {iters} passes", color=INK, fontsize=12,
              weight="bold", va="top")
    for i, (name, color, val, why) in enumerate(rows):
        y = 0.90 - i * 0.172
        side.text(0, y, name, color=color, fontsize=11.5, weight="bold",
                  va="top")
        side.text(0.66, y, val, color=INK, fontsize=11.5, va="top")
        side.text(0.02, y - 0.085, why, color=MUTED, fontsize=10, va="top")
    side.text(0, 0.02, "Different stationary points are found.",
              color=MUTED, fontsize=10, va="top", linespacing=1.5)
    _credit(fig, "data: Olivetti faces, AT&T Cambridge")


# ==========================================================================
# 7. weighted NMF
# ==========================================================================
@figure("weighted_idea")
def weighted_idea(fig):
    rng = np.random.default_rng(2)
    M = (rng.random((12, 18)) > 0.45).astype(float)
    V = rng.random((12, 18)) ** 1.3

    ax = canvas(fig)
    seen = np.where(M > 0, V, np.nan)
    cm = NN_CMAP.copy()
    cm.set_bad(LIGHT)
    ax.imshow(seen, cmap=cm, extent=(0.55, 2.75, 1.45, 3.05), aspect="auto",
              vmin=0, interpolation="nearest")
    ax.add_patch(Rectangle((0.55, 1.45), 2.20, 1.60, facecolor="none",
                           edgecolor=BLUE, lw=2.0))
    ax.text(1.65, 3.25, r"$X$", ha="center", color=BLUE, fontsize=14)
    ax.text(1.65, 1.22, "grey = not observed", ha="center", color=MUTED,
            fontsize=10)

    mask_cmap = LinearSegmentedColormap.from_list("mask", [LIGHT, PURPLE])
    ax.imshow(M, cmap=mask_cmap, extent=(3.35, 5.55, 1.45, 3.05),
              aspect="auto", vmin=0, vmax=1, interpolation="nearest")
    ax.add_patch(Rectangle((3.35, 1.45), 2.20, 1.60, facecolor="none",
                           edgecolor=PURPLE, lw=2.0))
    ax.text(4.45, 3.25, r"$\Sigma$", ha="center", color=PURPLE, fontsize=14)
    ax.text(4.45, 1.22, "1 where observed, 0 elsewhere", ha="center",
            color=MUTED, fontsize=10)

    column(ax, 6.05, 3.10, 2.8, "Why weight", [
        "entries not observed",
        "entries trusted less",
        "outlier to ignore",
        "class more important",
    ], GOLD, leading=0.30, item_size=11)
    note(ax, r"$\Sigma$ does not need not be binary", y=0.55, size=11.5)
    note(ax, "Missing entries are predicted by $WH$", y=0.20,
         size=11.5)


@figure("eq_weighted_loss")
def eq_weighted_loss(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "One matrix of weights, multiplied in entry by entry",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 2.80, r"$D_\Sigma(X, WH) = \frac{1}{2}\,"
                         r"\|\Sigma \odot (X - WH)\|_F^2 "
                         r"= \frac{1}{2}\sum_{ij} \Sigma_{ij}^2\,"
                         r"\left( X_{ij} - [WH]_{ij} \right)^2$",
            ha="center", va="center", color=INK, fontsize=17)
    rows = [
        (GREEN, r"$\Sigma_{ij} = 1$", "the entry counts, exactly as before"),
        (RED, r"$\Sigma_{ij} = 0$", "the entry costs nothing, whatever the model says there"),
        (GOLD, r"$0 < \Sigma_{ij} < 1$", "the entry counts, but less"),
    ]
    for i, (color, when, what) in enumerate(rows):
        y = 2.08 - i * 0.38
        ax.text(3.25, y, when, ha="right", va="center", color=color,
                fontsize=13)
        ax.text(3.45, y, what, ha="left", va="center", color=INK, fontsize=12)
    box(ax, 0.90, 0.42, 7.20, 0.56, PURPLE, "", fill="#f6f3fd")
    ax.text(W / 2, 0.70, r"for a binary mask $\Sigma \odot \Sigma = \Sigma$, "
                         r"so $\Sigma^2$ and $\Sigma$ can be written "
                         "interchangeably",
            ha="center", va="center", color=PURPLE, fontsize=12.5)


@figure("eq_weighted_mu")
def eq_weighted_mu(fig):
    ax = canvas(fig)
    ax.text(0.45, 3.52, r"Weighted Frobenius $\|\Sigma \odot (X - WH)\|_F^2$",
            color=BLUE, fontsize=13, va="center")
    ax.text(2.60, 2.95, r"$W \leftarrow W \odot "
                        r"\dfrac{(\Sigma \odot X) H^\top}"
                        r"{(\Sigma \odot WH) H^\top}$",
            ha="center", va="center", color=INK, fontsize=17)
    ax.text(6.40, 2.95, r"$H \leftarrow H \odot "
                        r"\dfrac{W^\top (\Sigma \odot X)}"
                        r"{W^\top (\Sigma \odot WH)}$",
            ha="center", va="center", color=INK, fontsize=17)
    ax.plot([0.45, 8.55], [2.30, 2.30], color=GRID, lw=1.2)
    ax.text(0.45, 2.05, r"Weighted KL, with a weight $p_i$ per row and $q_j$ "
                        r"per column", color=GREEN, fontsize=13, va="center")
    ax.text(2.60, 1.42, r"$W_{ik} \leftarrow W_{ik}\,"
                        r"\dfrac{\sum_l H_{kl} X_{il} / (p_i [WH]_{il})}"
                        r"{\sum_l q_l H_{kl}}$",
            ha="center", va="center", color=INK, fontsize=14)
    ax.text(6.40, 1.42, r"$H_{kj} \leftarrow H_{kj}\,"
                        r"\dfrac{\sum_i W_{ik} X_{ij} / (q_j [WH]_{ij})}"
                        r"{\sum_i p_i W_{ik}}$",
            ha="center", va="center", color=INK, fontsize=14)
    ax.text(W / 2, 0.68, r"i.e. $\mathrm{KL}\!\left( X,\; "
                         r"\mathrm{Diag}(p)\, W H\, \mathrm{Diag}(q) \right)$",
            ha="center", va="center", color=MUTED, fontsize=12)
    note(ax, "the weights change the numerator and the denominator by different amounts", y=0.26, size=11.5)


@figure("completion_demo")
def completion_demo(fig):
    full, mask = _ratings_toy(hide=0.0)
    rng = np.random.default_rng(11)
    hide_levels = np.array([0.1, 0.3, 0.5, 0.65, 0.78, 0.88])
    err, base = [], []
    for hv in hide_levels:
        m = (rng.random(full.shape) > hv).astype(float)
        Wm, Hm = _mu(full, 3, 500, mask=m, init="nndsvd")
        out = m == 0
        err.append(np.abs((Wm @ Hm)[out] - full[out]).mean())
        base.append(np.abs(full[m > 0].mean() - full[out]).mean())

    ax = fig.add_axes([0.09, 0.09, 0.82, 0.82])
    ax.semilogy(100 * hide_levels, err, "o-", color=GREEN, lw=2.2, ms=6,
                label="weighted NMF, r = 3")
    ax.semilogy(100 * hide_levels, base, "o--", color=MUTED, lw=1.6, ms=5,
                label="predict the global mean")
    ax.set_xlabel("% of the table hidden")
    ax.set_ylabel("mean error on the hidden\nentries (stars)")
    ax.set_ylim(min(err) * 0.7, max(max(err), max(base)) * 2.5)
    ax.legend(fontsize=10, loc="upper left")
    despine(ax, keep=("left", "bottom"))

    fig.text(0.5, 0.955, f"{full.shape[1]} users × {full.shape[0]} items, "
                         "ratings from 1 to 5",
             ha="center", va="center", color=MUTED, fontsize=12.5)


# ==========================================================================
# 8. regularized NMF
# ==========================================================================
@figure("reg_idea")
def reg_idea(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Three different jobs for a penalty", ha="center",
            va="center", color=MUTED, fontsize=12.5)
    cards = [
        (GREEN, "sparsity", r"$\lambda \|H\|_1$",
         "few components per column;\nthe parts become nameable"),
        (BLUE, "stability", r"$\frac{\mu}{2}\|H\|_F^2$",
         "a better conditioned subproblem;\nno entry can blow up"),
        (PURPLE, "scale", r"$\frac{\nu}{2}\|W\|_F^2$",
         "penalising both factors freezes\nthe $\\Lambda$ ambiguity"),
    ]
    for i, (color, name, term, why) in enumerate(cards):
        x = 0.45 + i * 2.75
        box(ax, x, 1.30, 2.55, 1.85, color, "", fill="white")
        ax.text(x + 1.27, 2.86, name, ha="center", va="center", color=color,
                fontsize=14, weight="bold")
        ax.text(x + 1.27, 2.34, term, ha="center", va="center", color=INK,
                fontsize=17)
        ax.text(x + 1.27, 1.72, why, ha="center", va="center", color=MUTED,
                fontsize=10.5, linespacing=1.5)
    note(ax, r"since $H \geq 0$, the $\ell_1$ norm is differentiable, with gradient $\mathbf{1}$", y=0.80,
         size=11.5)
    note(ax, "Penalty fits multiplicative update without a proximal step.", y=0.40, size=11.5)


@figure("eq_reg_loss")
def eq_reg_loss(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.50, "The penalized objective", ha="center", va="center",
            color=MUTED, fontsize=12.5)
    ax.text(W / 2, 2.78, r"$\frac{1}{2}\|X - WH\|_F^2 "
                         r"+ \frac{\mu}{2}\|H\|_F^2 "
                         r"+ \lambda \|H\|_1 "
                         r"+ \frac{\nu}{2}\|W\|_F^2$",
            ha="center", va="center", color=INK, fontsize=22)
    marks = [
        (2.8, BLUE, "fit", 2.00),
        (4.4, GREEN, "keeps $H$ small", 1.72),
        (5.5, GOLD, "makes $H$ sparse", 2.00),
        (6.5, PURPLE, "keeps $W$ small", 1.72),
    ]
    for x, color, label, ty in marks:
        ax.annotate("", xy=(x, 2.42), xytext=(x, ty + 0.14),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5))
        ax.text(x, ty, label, ha="center", va="center", color=color,
                fontsize=11)
    box(ax, 0.70, 0.60, 7.60, 0.58, GREEN, "", fill="#f2fbf2")
    ax.text(W / 2, 0.89, "Penalties are separable in the entries, so derivation is unchanged.",
            ha="center", va="center", color=GREEN, fontsize=12.5)
    note(ax, r"$\lambda$, $\mu$, $\nu$ are hyperparameters to tune", y=0.22, size=11)


@figure("eq_reg_mu")
def eq_reg_mu(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "The regularized multiplicative updates", ha="center",
            va="center", color=MUTED, fontsize=12.5)
    ax.text(2.60, 2.70, r"$W \;\leftarrow\; W \odot "
                        r"\dfrac{X H^\top}{W (H H^\top + \nu I_r)}$",
            ha="center", va="center", color=INK, fontsize=18)
    ax.text(6.45, 2.70, r"$H \;\leftarrow\; H \odot "
                        r"\dfrac{\left[ W^\top X - \lambda \mathbf{1} "
                        r"\right]_{+}}{(W^\top W + \mu I_r) H}$",
            ha="center", va="center", color=INK, fontsize=18)
    ax.text(W / 2, 1.90, r"$[\,\cdot\,]_{+} = \max(\cdot, 0)$ — without it a "
                         r"large $\lambda$ would make $H$ negative",
            ha="center", va="center", color=RED, fontsize=11.5)
    rows = [
        (GOLD, r"$\lambda$ up", r"more zeros in $H$, a worse fit"),
        (GREEN, r"$\mu$ up", r"the denominator grows: $H$ shrinks, smoothly"),
        (PURPLE, r"$\nu$ up", r"$W$ shrinks and $H$ grows to compensate"),
    ]
    for i, (color, knob, what) in enumerate(rows):
        y = 1.42 - i * 0.34
        ax.text(2.70, y, knob, ha="right", va="center", color=color,
                fontsize=12.5, weight="bold")
        ax.text(2.90, y, what, ha="left", va="center", color=INK, fontsize=12)
    note(ax, "the penalties cost nothing: they only change which two matrices "
             "the ratio is made of", y=0.22, size=11.5)


@figure("sparsity_demo")
def sparsity_demo(fig):
    n_faces = 200
    imgs, Xf = _faces(n_faces)
    X = Xf.T
    lams = np.array([0.0, 5.0, 20.0, 40.0, 60.0, 80.0])
    sparsity, relerr, Ws = [], [], []
    for lam in lams:
        Wm, Hm = _mu(X, 16, 250, init="nndsvd", lam=lam)
        sparsity.append(float((Hm < 1e-6 * max(Hm.max(), 1e-12)).mean()))
        relerr.append(float(np.linalg.norm(X - Wm @ Hm) / np.linalg.norm(X)))
        Ws.append(Wm)

    ax = fig.add_axes([0.08, 0.24, 0.30, 0.54])
    ax.plot(lams, 100 * np.array(sparsity), "o-", color=GOLD, lw=2.2, ms=6)
    ax.set_xlabel(r"$\lambda$")
    ax.set_ylabel(r"% of $H$ at zero", color=GOLD)
    ax.tick_params(axis="y", colors=GOLD)
    ax2 = ax.twinx()
    ax2.plot(lams, 100 * np.array(relerr), "o--", color=RED, lw=1.8, ms=5)
    ax2.set_ylabel("relative error (%)", color=RED)
    ax2.tick_params(axis="y", colors=RED)
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_color(RED)
    ax.spines["left"].set_color(GOLD)
    despine(ax, keep=("left", "bottom"))

    for col, idx in enumerate((0, 3, 5)):
        for row in range(2):
            a = fig.add_axes([0.47 + col * 0.155, 0.47 - row * 0.26, 0.13,
                              0.24])
            a.imshow(Ws[idx][:, row + 2].reshape(64, 64), cmap="gray_r",
                     interpolation="nearest")
            _bare(a)
        fig.text(0.535 + col * 0.155, 0.76, rf"$\lambda = {lams[idx]}$",
                 ha="center", va="center", color=GOLD, fontsize=11.5)
    fig.text(0.735, 0.145, r"2 of the 16 columns of $W$",
             ha="center", va="top", color=MUTED, fontsize=10.5)

    fig.text(0.5, 0.955, f"{n_faces} faces, r = 16",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    _credit(fig, "data: Olivetti faces, AT&T Cambridge")


# ==========================================================================
# 9. other algorithms
# ==========================================================================
@figure("als_idea")
def als_idea(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.54, "One half of the problem is an ordinary least "
                         "squares — so solve it, instead of nudging it",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(0.45, 3.06, "Alternating least squares", color=PURPLE,
            fontsize=13, weight="bold", va="center")
    ax.text(W / 2, 2.56, r"$H \;\leftarrow\; \left[ (W^\top W)^{-1} W^\top X "
                         r"\right]_{+}$,$\qquad$ "
                         r"$W \;\leftarrow\; \left[ X H^\top "
                         r"(H H^\top)^{-1} \right]_{+}$",
            ha="center", va="center", color=INK, fontsize=15)
    ax.text(W / 2, 2.12, r"the unconstrained optimum of the frozen half, "
                         r"then $\max(\cdot, 0)$ entry by entry",
            ha="center", va="center", color=MUTED, fontsize=11)
    box(ax, 0.55, 1.26, 7.90, 0.52, RED, "", fill="#fdf5f5", lw=1.6)
    ax.text(W / 2, 1.52, "the catch: clipping is not the solution of the "
                         "constrained problem, so the loss can go up",
            ha="center", va="center", color=RED, fontsize=12)
    ax.plot([0.40, 8.60], [1.08, 1.08], color=GRID, lw=1.2)
    ax.text(0.45, 0.84, "Alternating NNLS", color=GREEN, fontsize=12.5,
            weight="bold", va="center")
    ax.text(2.55, 0.84, r"$h_j \leftarrow \arg\min_{h \geq 0} "
                        r"\|x_j - W h\|_2^2$ for each column: exact and "
                        r"monotone,", ha="left", va="center", color=INK,
            fontsize=11.5)
    ax.text(2.55, 0.50, "but it needs an inner solver per column, and is far "
                        "too slow to run from the start",
            ha="left", va="center", color=MUTED, fontsize=11)


@figure("hals_layers")
def hals_layers(fig):
    X, Wm, Hm = _layers_fit()
    ax = canvas(fig)
    ax.text(W / 2, 3.54, r"Every factorization is a sum of $r$ rank-one "
                         r"layers:  $WH = w_1 h^{(1)} + \ldots + "
                         r"w_r h^{(r)}$",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    top = float(X.max())
    _matrix(ax, 0.65, 1.30, 1.55, 1.55, BLUE, NN_CMAP, M=X, label=r"$X$",
            vmax=top)
    ax.text(2.35, 2.07, r"$\approx$", ha="center", va="center", color=INK,
            fontsize=18)
    for k, color in enumerate((PURPLE, GOLD, GREEN)):
        x = 2.60 + k * 2.00
        layer = np.outer(Wm[:, k], Hm[k])
        _matrix(ax, x, 1.30, 1.55, 1.55, color, NN_CMAP, M=layer,
                label=r"$w_%d\, h^{(%d)}$" % (k + 1, k + 1), vmax=top)
        if k:
            ax.text(x - 0.23, 2.07, "+", ha="center", va="center", color=INK,
                    fontsize=18)
    note(ax, r"one column of $W$ times one row of $H$: a rank-one "
             r"non-negative matrix, and the whole model is their sum",
         y=0.86, size=11.5)
    note(ax, r"MU moves all $r$ layers at once. HALS moves one, exactly, "
             r"holding the other $r - 1$ fixed", y=0.42, size=12.5,
         color=GOLD)


@figure("hals_residual")
def hals_residual(fig):
    X, Wm, Hm = _layers_fit()
    k = 1
    others = Wm @ Hm - np.outer(Wm[:, k], Hm[k])
    R = X - others
    lim = float(np.abs(R).max())
    ax = canvas(fig)
    ax.text(W / 2, 3.54, r"What layer $k$ has to explain on its own: $X$, "
                         r"with every other layer taken out",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    y0, h0, w0 = 1.42, 1.50, 1.50
    top = float(X.max())
    _matrix(ax, 0.95, y0, w0, h0, BLUE, NN_CMAP, M=X, label=r"$X$", vmax=top)
    ax.text(2.60, y0 + h0 / 2, r"$-$", ha="center", va="center", color=INK,
            fontsize=18)
    _matrix(ax, 2.75, y0, w0, h0, MUTED, NN_CMAP, M=others,
            label=r"the other layers", vmax=top)
    ax.text(4.40, y0 + h0 / 2, r"$=$", ha="center", va="center", color=INK,
            fontsize=18)
    ax.imshow(R, cmap="coolwarm", extent=(4.55, 4.55 + w0, y0, y0 + h0),
              aspect="auto", vmin=-lim, vmax=lim, zorder=2,
              interpolation="nearest")
    ax.add_patch(Rectangle((4.55, y0), w0, h0, facecolor="none",
                           edgecolor=RED, lw=2.0, zorder=3))
    ax.text(4.55 + w0 / 2, y0 + h0 + 0.22, r"$R_k$", ha="center", va="center",
            color=RED, fontsize=13)
    ax.text(6.20, y0 + h0 / 2, r"$\approx$", ha="center", va="center",
            color=INK, fontsize=18)
    _matrix(ax, 6.35, y0, w0, h0, GOLD, NN_CMAP, M=np.outer(Wm[:, k], Hm[k]),
            label=r"$w_k\, h^{(k)}$", vmax=top)
    ax.text(4.55 + w0 / 2, 1.24, "red positive, blue negative", color=MUTED,
            fontsize=9.5, ha="center", va="top")
    note(ax, r"$\frac{1}{2}\|X - WH\|_F^2 = \frac{1}{2}\|R_k - w_k "
             r"h^{(k)}\|_F^2$:  with every other layer frozen, the problem "
             r"is a single rank-one fit", y=0.74, size=12)
    note(ax, r"$R_k$ has negative entries — fitting a non-negative layer to "
             r"it is exactly where the constraint bites", y=0.34, size=11.5,
         color=RED)


@figure("hals_column")
def hals_column(fig):
    X, _, _ = _layers_fit()
    # two passes in: still far from the fixed point, so some entries of the
    # column genuinely want to go negative
    Wm, Hm = _hals(X, 3, 2)
    k = 0
    R = X - Wm @ Hm + np.outer(Wm[:, k], Hm[k])
    hk = Hm[k]
    den = float(hk @ hk)
    num = R @ hk
    opt = num / den
    i_pos, i_neg = int(np.argmax(opt)), int(np.argmin(opt))
    assert opt[i_neg] < -0.15 and opt[i_pos] > 0.5

    fig.text(0.5, 0.955, r"One entry of $w_k$ at a time: a parabola, and a "
                         r"clip at zero",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    axes = panels(fig, 2, titles=[r"entry $i$ with $[R_k h^{(k)\top}]_i > 0$",
                                  r"entry $i$ with $[R_k h^{(k)\top}]_i < 0$"],
                  colors=[GREEN, RED],
                  gridspec_kw=dict(left=0.055, right=0.515, top=0.775,
                                   bottom=0.245, wspace=0.22))
    for ax, i, color in zip(axes, (i_pos, i_neg), (GREEN, RED)):
        lo = min(-0.25, opt[i] - 0.25)
        hi = max(0.35, opt[i] + 0.25)
        t = np.linspace(lo, hi, 300)
        f = 0.5 * den * t ** 2 - num[i] * t
        ax.axvspan(lo, 0, color=LIGHT, zorder=0)
        ax.axvline(0, color=GRID, lw=1.2)
        ax.plot(t, f, color=INK, lw=2.2, zorder=3)
        ax.plot(opt[i], 0.5 * den * opt[i] ** 2 - num[i] * opt[i], "o",
                color=MUTED, ms=7, zorder=4)
        best = max(opt[i], 0.0)
        fb = 0.5 * den * best ** 2 - num[i] * best
        if opt[i] < 0:
            ax.annotate("", xy=(best, fb),
                        xytext=(opt[i], 0.5 * den * opt[i] ** 2
                                - num[i] * opt[i]),
                        arrowprops=dict(arrowstyle="-|>", color=color,
                                        lw=1.8))
        ax.plot(best, fb, "o", color=color, ms=8, zorder=5)
        ax.set_xticks([0], ["0"])
        ax.set_yticks([])
        despine(ax, keep=("bottom",))
    caption_row(fig, axes, [r"the vertex of the parabola is legal:"
                            "\nkeep it",
                            r"the vertex is forbidden:"
                            "\nzero is the best legal value"],
                y=0.185, size=10.5)

    side = fig.add_axes([0.565, 0.165, 0.425, 0.645])
    side.axis("off")
    side.text(0, 1.0, "Why the clip is exact here", color=GREEN, fontsize=12.5,
              weight="bold", va="top")
    side.text(0, 0.85, r"$\frac{1}{2}\|R_k - w_k h^{(k)}\|_F^2 = "
                       r"\sum_i \left( \frac{1}{2}\|h^{(k)}\|^2 w_{ik}^2 "
                       r"- [R_k h^{(k)\top}]_i\, w_{ik} \right) + c$",
              color=INK, fontsize=11, va="top")
    side.text(0, 0.69, "the $p$ entries never meet: minimizing under\n"
                       r"$w_k \geq 0$ is $p$ separate one-dimensional"
                       "\nproblems, each solved by its own clip",
              color=MUTED, fontsize=10.5, va="top", linespacing=1.55)
    side.text(0, 0.37, r"$w_k \;\leftarrow\; \left[ \dfrac{R_k "
                       r"h^{(k)\top}}{\|h^{(k)}\|^2} \right]_{+}$",
              color=GOLD, fontsize=15, va="top")
    side.text(0, 0.10, "in ALS the entries are coupled by "
                       r"$(W^\top W)^{-1}$," "\nso clipping there is only a "
                       "heuristic — here it\nis the constrained optimum",
              color=RED, fontsize=10.5, va="top", linespacing=1.55)


@figure("hals_algorithm")
def hals_algorithm(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "HALS, one pass", ha="center", va="center",
            color=MUTED, fontsize=12.5)
    lines = [
        (BLUE, "precompute", r"$A = X H^\top$, $\quad B = H H^\top$"),
        (INK, r"for $k = 1 \ldots r$",
         r"$w_k \leftarrow \left[ w_k + \dfrac{A_{:k} - W B_{:k}}{B_{kk}} "
         r"\right]_{+}$"),
        (BLUE, "precompute", r"$C = W^\top X$, $\quad D = W^\top W$"),
        (INK, r"for $k = 1 \ldots r$",
         r"$h^{(k)} \leftarrow \left[ h^{(k)} + \dfrac{C_{k:} - D_{k:} H}"
         r"{D_{kk}} \right]_{+}$"),
    ]
    box(ax, 0.55, 1.05, 7.90, 2.05, GOLD, "", fill="white", lw=1.6)
    for i, (color, key, text) in enumerate(lines):
        y = 2.80 - i * 0.50
        ax.text(2.55, y, key, ha="right", va="center", color=color,
                fontsize=12, weight="bold" if color is BLUE else "normal")
        ax.text(2.75, y, text, ha="left", va="center", color=INK, fontsize=13)
    note(ax, r"same $\mathcal{O}(pnr)$ cost as one MU pass — the two matrix "
             r"products are computed once, outside the loop", y=0.70, size=11.5)
    note(ax, r"and a floor of $\varepsilon$ instead of 0 keeps a column from "
             "dying", y=0.30, size=11.5)


@figure("algo_compare")
def algo_compare(fig):
    import time

    imgs, Xf = _faces(300)
    X = Xf.T
    r, iters = 12, 120
    curves = []
    for name, fn, color in (("MU", _mu, BLUE), ("ALS", _als, PURPLE),
                            ("HALS", _hals, GOLD)):
        t0 = time.perf_counter()
        *_, trace = fn(X, r, iters, init="nndsvd", trace=True)
        dt = time.perf_counter() - t0
        curves.append((name, color, trace, np.linspace(0, dt, len(trace))))

    axes = panels(fig, 2, titles=["per pass", "per second of work"],
                  colors=[INK, INK],
                  gridspec_kw=dict(left=0.09, right=0.73, top=0.80,
                                   bottom=0.26, wspace=0.26))
    for name, color, trace, secs in curves:
        axes[0].semilogy(np.arange(1, len(trace) + 1), trace, color=color,
                         lw=2.2, label=name)
        axes[1].semilogy(secs, trace, color=color, lw=2.2)
    axes[0].set_xlabel("pass")
    axes[0].set_ylabel(r"$\frac{1}{2}\|X - WH\|_F^2$")
    axes[1].set_xlabel("seconds")
    axes[0].legend(fontsize=10)
    for ax in axes:
        despine(ax, keep=("left", "bottom"))

    side = fig.add_axes([0.77, 0.20, 0.22, 0.60])
    side.axis("off")
    best = min(curves, key=lambda c: c[2][-1])
    side.text(0, 1.0, "after %d passes" % iters, color=INK, fontsize=12,
              weight="bold", va="top")
    for i, (name, color, trace, secs) in enumerate(curves):
        side.text(0, 0.84 - i * 0.14, f"{name}:  {trace[-1]:.0f}", color=color,
                  fontsize=11.5, va="top")
    als = next(c for c in curves if c[0] == "ALS")
    ups = int((np.diff(als[2]) > 1e-9).sum())
    side.text(0, 0.40, f"{best[0]} wins, and ALS is\nnot monotone: it rises "
                       f"on\n{ups} of its {iters - 1} steps",
              color=MUTED, fontsize=10.5, va="top", linespacing=1.5)
    fig.text(0.5, 0.955, f"{X.shape[1]} faces, r = {r}, same NNDSVD start for "
                         "all three",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    _credit(fig, "data: Olivetti faces, AT&T Cambridge")


@figure("choosing_r")
def choosing_r(fig):
    imgs, Xf = _faces(300)
    X = Xf.T
    rs = np.array([2, 4, 8, 12, 16, 24, 32, 48])
    err = []
    for r in rs:
        Wm, Hm = _hals(X, int(r), 150, init="nndsvd")
        err.append(float(np.linalg.norm(X - Wm @ Hm) / np.linalg.norm(X)))
    err = np.array(err)

    ax = fig.add_axes([0.09, 0.22, 0.40, 0.56])
    ax.plot(rs, 100 * err, "o-", color=BLUE, lw=2.2, ms=6)
    ax.set_xlabel(r"$r$")
    ax.set_ylabel("relative error (%)")
    ax.set_ylim(0, 100 * err.max() * 1.15)
    despine(ax, keep=("left", "bottom"))
    ax.set_title(f"{X.shape[1]} faces", color=INK, fontsize=12, pad=8)

    side = fig.add_axes([0.56, 0.18, 0.42, 0.62])
    side.axis("off")
    side.text(0, 1.0, "Larger $r$ always fits better", color=RED, fontsize=12.5,
              weight="bold", va="top")
    side.text(0, 0.62, "Choose $r$ with:", color=GREEN, fontsize=12.5,
              weight="bold", va="top")
    for i, item in enumerate([
            "Elbow (if there is one)",
            "Stability (unstable components can be discarded)",
            "Domain knowledge (e.g. 3 notes/materials)",
    ]):
        side.text(0, 0.48 - i * 0.12, "—", color=GREEN, fontsize=11, va="top")
        side.text(0.035, 0.48 - i * 0.12, item, color=INK, fontsize=11,
                  va="top")
    fig.text(0.5, 0.955, r"Choosing $r$ is the one parameter NMF cannot "
                         "choose for itself",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    _credit(fig, "data: Olivetti faces, AT&T Cambridge")


@figure("nmf_props")
def nmf_props(fig):
    ax = canvas(fig)
    column(ax, 0.55, 3.25, 3.9, "Pros", [
        "dimension reduction for\nnon-negative data",
        "components that add up:\nreadable, nameable",
        "weighted and regularized\nvariants come almost free",
        "cheap updates, easy to implement",
    ], GREEN, leading=0.30, item_size=11.5)
    column(ax, 4.90, 3.25, 3.9, "Cons", [
        "non-convex: the start decides\nwhere you land",
        "no unique answer",
        "MU converges slowly, and\nstalls at small values",
        r"$r$ has to come from somewhere",
    ], RED, leading=0.30, item_size=11.5)
    ax.plot([4.65, 4.65], [0.70, 3.35], color=GRID, lw=1.2)
    note(ax, "Use NMF when the parts have to mean something; use PCA when you "
             "only want the best rank-$r$ fit.", y=0.38)


@figure("nmf_map")
def nmf_map(fig):
    ax = canvas(fig)
    rows = [
        ("Frobenius MU", BLUE, r"$\beta = 2$", "additive noise",
         "the default"),
        ("KL MU", GREEN, r"$\beta = 1$", "counts", "text, photons"),
        ("Itakura–Saito MU", GOLD, r"$\beta = 0$", "multiplicative noise",
         "audio"),
        ("Weighted NMF", PURPLE, r"$\Sigma \odot$", "missing or unequal data",
         "completion"),
        ("Regularized NMF", RED, r"$\lambda, \mu, \nu$", "ambiguity, noise",
         "sparse, stable parts"),
        ("HALS / ANLS", INK, "—", "when MU is too slow",
         "same model, better solver"),
    ]
    x = (0.50, 2.90, 4.10, 6.60)
    headers = ("Method", "Knob", "Reach for it when", "Gives")
    for xi, head in zip(x, headers):
        ax.text(xi, 3.32, head, color=MUTED, fontsize=11.5, va="center")
    ax.plot([0.42, 8.58], [3.12, 3.12], color=GRID, lw=1.2)
    for i, (name, color, knob, when, why) in enumerate(rows):
        y = 2.86 - i * 0.47
        ax.text(x[0], y, name, color=color, fontsize=12.5, weight="bold",
                va="center")
        ax.text(x[1], y, knob, color=INK, fontsize=12, va="center")
        ax.text(x[2], y, when, color=INK, fontsize=12, va="center")
        ax.text(x[3], y, why, color=INK, fontsize=12, va="center")
        if i:
            ax.plot([0.42, 8.58], [y + 0.235, y + 0.235], color=LIGHT, lw=1.0)
    note(ax, r"all of them are the same two lines: $\;\cdot \odot "
             r"\nabla^{-} \oslash \nabla^{+}$", y=0.16, size=12)


# ==========================================================================
def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course05/img")
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
