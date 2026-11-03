#!/usr/bin/env python3
"""Every figure of Course09 (dimension reduction and data visualization).

One function per figure, registered under the stem the slide deck asks for.
All figures share one canvas (9 x 3.7075 in), which is exactly the content
area pandoc leaves under a slide title, so a figure never has to be resized.

SNE and t-SNE are written out below in numpy, so that every step can be drawn
on a 45-point toy and the two compared on the same code (on scikit-learn's
8 x 8 digits); the larger maps use scikit-learn's TSNE.  MNIST's 10 000 test
images are downloaded once into .cache/datasets/ (about 1.7 MB).

    python3 scripts/make_figures_c09.py Course09/img [stem ...]
"""


import sys
from functools import lru_cache
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap, PowerNorm
from matplotlib.patches import (
    Circle,
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
GRID = "#cccfd2"

# the convention of this deck: the original, high-dimensional space is blue,
# the low-dimensional map is gold, PCA is purple and t-SNE is green
HIGH, LOW, PCA_C, TSNE_C = BLUE, GOLD, PURPLE, GREEN
COMP = [BLUE, GOLD, GREEN, PURPLE, RED]
# the ten digit classes: matplotlib's tab10, the most distinguishable ten
DIGIT = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
         "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
G_CMAP = LinearSegmentedColormap.from_list("gm", ["#ffffff", "#cfe0f1", BLUE])
# the probability matrices: white is zero, a square-root scale so that the
# small probabilities still show
H_CMAP = LinearSegmentedColormap.from_list("hm", ["#ffffff", "#9cc0e4", BLUE, "#0b2a55"])
P_CMAP = LinearSegmentedColormap.from_list("pm", ["#ffffff", "#e2d9f5", PURPLE])


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
                va="top")
        yy -= leading * (1 + item.count("\n"))
    return yy


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


def _bare(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


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
# the data and the two embeddings every slide runs on
# ==========================================================================
EPS = 1e-12
CACHE = Path(__file__).resolve().parent.parent / ".cache" / "datasets"


@lru_cache(None)
def _digits():
    """scikit-learn's 1797 handwritten digits: 8 x 8 images, 64 features."""
    from sklearn.datasets import load_digits
    d = load_digits()
    return d.data.astype(float), d.target


@lru_cache(None)
def _digits_subset(n=600, seed=0):
    X, y = _digits()
    idx = np.sort(np.random.default_rng(seed).choice(len(X), n, replace=False))
    return X[idx], y[idx]


def _pca(X, q=2):
    """Centre, then project on the top q eigenvectors of the covariance."""
    Xc = X - X.mean(0)
    S = Xc.T @ Xc / (len(X) - 1)
    lam, V = np.linalg.eigh(S)
    order = np.argsort(lam)[::-1]
    lam, V = lam[order], V[:, order]
    return Xc @ V[:, :q], lam, V


@lru_cache(None)
def _swiss_roll(n=1200, seed=0):
    from sklearn.datasets import make_swiss_roll
    X, t = make_swiss_roll(n_samples=n, noise=0.15, random_state=seed)
    X[:, 1] *= 1.6      # a long roll: its length is the direction of most variance
    return X, t


def _sqdist(X):
    s = (X ** 2).sum(1)
    D = s[:, None] + s[None, :] - 2 * X @ X.T
    np.fill_diagonal(D, 0.0)
    return np.maximum(D, 0.0)


def _row_p(d2, beta):
    """p_{j|i} for one row of squared distances (self excluded), and H in bits."""
    w = np.exp(-(d2 - d2.min()) * beta)
    p = w / w.sum()
    H = -(p * np.log2(np.maximum(p, EPS))).sum()
    return p, H


def _conditional_p(X, perp=30.0, tol=1e-5, D2=None, trace=None):
    """The p_{j|i}: one Gaussian per point, its width found by bisection so
    that the row has the target perplexity.  Returns P (rows sum to one) and
    the sigma_i."""
    D2 = _sqdist(X) if D2 is None else D2
    n = len(D2)
    P = np.zeros((n, n))
    sig = np.zeros(n)
    target = np.log2(perp)
    for i in range(n):
        d2 = np.delete(D2[i], i)
        lo, hi, beta = 0.0, np.inf, 1.0 / max(np.median(d2), EPS)
        for _ in range(100):
            p, H = _row_p(d2, beta)
            if trace is not None and i == trace[0]:
                trace[1].append((1 / np.sqrt(2 * beta), 2 ** H))
            if abs(H - target) < tol:
                break
            if H > target:          # too many neighbours: narrow the bell
                lo = beta
                beta = beta * 2 if hi == np.inf else (beta + hi) / 2
            else:
                hi = beta
                beta = (beta + lo) / 2
        P[i, np.arange(n) != i] = p
        sig[i] = 1 / np.sqrt(2 * beta)
    return P, sig


def _joint_p(X, perp=30.0):
    Pc, _ = _conditional_p(X, perp)
    P = (Pc + Pc.T) / (2 * len(X))
    return np.maximum(P, EPS)


def _embed(X, kind="t", perp=30.0, iters=1000, seed=0, lr=None, exag=12.0,
           exag_iters=250, history=None, dim=2, Y0=None):
    """Symmetric SNE (kind="sne", Gaussian map kernel) or t-SNE (kind="t",
    Student-t map kernel): gradient descent with momentum, the per-coordinate
    gains of van der Maaten and Hinton (2008) and early exaggeration.
    `history` maps iteration numbers to None; each is filled with the map
    *before* that iteration's move, its Q and its KL."""
    n = len(X)
    P = _joint_p(X, perp)
    rng = np.random.default_rng(seed)
    Y = rng.normal(0, 1e-4, (n, dim)) if Y0 is None else np.array(Y0, float)
    V = np.zeros_like(Y)
    gains = np.ones_like(Y)
    if lr is None:
        lr = max(n / exag / 4, 50.0) if kind == "t" else 10.0
    for it in range(iters + 1):
        Pe = P * exag if it < exag_iters else P
        D2 = _sqdist(Y)
        W = 1 / (1 + D2) if kind == "t" else np.exp(-D2)
        np.fill_diagonal(W, 0.0)
        Q = np.maximum(W / W.sum(), EPS)
        if history is not None and it in history:
            history[it] = (Y.copy(), Q.copy(), float((P * np.log(P / Q)).sum()))
        if it == iters:
            break
        M = (Pe - Q) * (W if kind == "t" else 1.0)
        G = 4 * (M.sum(1)[:, None] * Y - M @ Y)
        gains = np.where(np.sign(G) != np.sign(V), gains + 0.2, gains * 0.8)
        gains = np.maximum(gains, 0.01)
        mom = 0.5 if it < exag_iters else 0.8
        V = mom * V - lr * gains * G
        Y = Y + V
        Y -= Y.mean(0)
    return Y


# --------------------------------------------------------------------------
# the toy every SNE step is drawn on: 2-D data, a 1-D map, so both fit on a
# slide.  Three groups: a tight one, a wide one, a medium one.
# --------------------------------------------------------------------------
TOY_COL = [BLUE, GOLD, GREEN]
TOY_PERP = 8.0
TOY_ITERS = 300
TOY_SNAPS = (0, 30, 40, 50, 70, 300)
TOY_MID = 40         # the half-formed map the step-3 slides look at


@lru_cache(None)
def _toy():
    rng = np.random.default_rng(11)
    centres = np.array([[-3.0, 0.3], [1.4, 1.9], [1.9, -1.9]])
    sd = (0.35, 0.95, 0.60)
    X = np.vstack([centres[k] + rng.normal(0, sd[k], (15, 2)) for k in range(3)])
    g = np.repeat(np.arange(3), 15)
    # the point we follow: the one of the wide group nearest its centre
    i = 15 + int(np.argmin(((X[15:30] - X[15:30].mean(0)) ** 2).sum(1)))
    return X, g, i


@lru_cache(None)
def _toy_run(seed=0, init="random"):
    X, _, _ = _toy()
    Y0 = None
    if init == "pca":
        Z, _, _ = _pca(X, 1)
        Y0 = Z / Z.std() * 1e-4
    hist = {t: None for t in range(TOY_ITERS + 1)}
    _embed(X, kind="sne", perp=TOY_PERP, iters=TOY_ITERS, seed=seed, dim=1,
           exag=1.0, exag_iters=0, lr=0.3, history=hist, Y0=Y0)
    return hist


@lru_cache(None)
def _sk_tsne_fit(name, perp=30.0, seed=0):
    """scikit-learn's t-SNE from a random start: the map and its final KL."""
    from sklearn.manifold import TSNE
    X = {"roll": lambda: _swiss_roll()[0], "blobs": lambda: _blobs_hd()[0]}[name]()
    m = TSNE(n_components=2, perplexity=perp, random_state=seed,
             init="random", learning_rate="auto")
    return m.fit_transform(X), float(m.kl_divergence_)


def _sk_tsne(name, perp=30.0, seed=0):
    return _sk_tsne_fit(name, perp, seed)[0]


# MNIST's 10 000 test images, cached in .cache/datasets/ like Course01's
# datasets (about 1.7 MB, downloaded on the first build)
MNIST_URL = "https://storage.googleapis.com/cvdf-datasets/mnist/"


def _fetch(url, name):
    import urllib.request
    path = CACHE / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"    downloading {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r:
            path.write_bytes(r.read())
    return path


@lru_cache(None)
def _mnist_pca50(n=5000, seed=0):
    """A random 5000 of MNIST's test images, reduced to 50 PCA axes (the
    usual step before t-SNE), with their labels."""
    import gzip
    with gzip.open(_fetch(MNIST_URL + "t10k-images-idx3-ubyte.gz",
                          "mnist_t10k_img.gz")) as f:
        X = np.frombuffer(f.read(), np.uint8, offset=16).reshape(-1, 784)
    with gzip.open(_fetch(MNIST_URL + "t10k-labels-idx1-ubyte.gz",
                          "mnist_t10k_lbl.gz")) as f:
        y = np.frombuffer(f.read(), np.uint8, offset=8)
    idx = np.random.default_rng(seed).choice(len(X), n, replace=False)
    Z, _, _ = _pca(X[idx] / 255.0, 50)
    return Z, y[idx]


@lru_cache(None)
def _mnist_tsne():
    from sklearn.manifold import TSNE
    Z, _ = _mnist_pca50()
    return TSNE(n_components=2, perplexity=30, random_state=0, init="pca",
                learning_rate="auto").fit_transform(Z)


@lru_cache(None)
def _blobs_hd(seed=2, d=10):
    """Three clusters in 10-D: a wide one, a tight one, and a tight one far
    away, so that sizes and distances can be compared after the map."""
    rng = np.random.default_rng(seed)
    c = np.zeros((3, d))
    c[1, 0] = 15.0
    c[2, 0] = 60.0
    sd = (2.0, 0.5, 0.5)
    X = np.vstack([c[k] + rng.normal(0, sd[k], (100, d)) for k in range(3)])
    return X, np.repeat(np.arange(3), 100)


def _digit_scatter(ax, Y, y, s=7, labels=True, alpha=0.8):
    ax.scatter(Y[:, 0], Y[:, 1], c=[DIGIT[k] for k in y], s=s, alpha=alpha,
               edgecolors="none", rasterized=True)
    if labels:
        for k in range(10):
            m = np.median(Y[y == k], 0)
            ax.text(*m, str(k), ha="center", va="center", fontsize=12,
                    weight="bold", color=DIGIT[k],
                    bbox=dict(boxstyle="round,pad=0.12", fc="white",
                              ec="none", alpha=0.75))
    _bare(ax)


def _roll_scatter(ax, Y, t, s=5):
    ax.scatter(Y[:, 0], Y[:, 1], c=t, cmap="viridis", s=s, edgecolors="none",
               rasterized=True)
    _bare(ax)


def _foot(fig, text, color=MUTED, size=11.5):
    """The one or two sentences under a figure."""
    fig.text(0.5, 0.035, text, ha="center", va="bottom", color=color,
             fontsize=size, linespacing=1.55)


def _algo(ax, x, y, lines, size=11, leading=0.31, num_color=MUTED):
    """Numbered algorithm lines; a line starting with two spaces is indented."""
    k = 0
    for line in lines:
        indent = len(line) - len(line.lstrip())
        if line.strip() and not line.startswith("#"):
            k += 1 if not indent else 0
        if line.startswith("#"):
            ax.text(x, y, line[1:].strip(), color=INK, fontsize=size,
                    weight="bold", va="center")
        else:
            if not indent:
                ax.text(x, y, f"{k}.", color=num_color, fontsize=size,
                        va="center")
            ax.text(x + 0.30 + 0.25 * indent / 2, y, line.strip(), color=INK,
                    fontsize=size, va="center")
        y -= leading
    return y


# ==========================================================================
# the toy's plane, line and matrices, drawn by the SNE step figures
# ==========================================================================
TOY_LIM = (-4.4, 4.4, -3.6, 3.6)


def _toy_plane(a, X, g, i=None, sizes=None, alpha=0.9):
    s = 26 if sizes is None else sizes
    a.scatter(*X.T, s=s, c=[TOY_COL[k] for k in g], alpha=alpha,
              edgecolors="white", linewidths=0.5, zorder=3)
    if i is not None:
        a.plot(*X[i], "*", color=RED, ms=16, mec="white", zorder=5)
    a.set_xlim(TOY_LIM[:2]); a.set_ylim(TOY_LIM[2:]); a.set_aspect("equal")
    _bare(a)


def _jitter(n):
    return ((np.arange(n) * 7) % 5 - 2) * 0.07


def _strip(a, y, g, i=None, lim=None, s=26, jitter=True, alpha=0.9):
    """A 1-D map: the points on a line (a little vertical jitter so they can
    be told apart)."""
    y = np.ravel(y)
    lo, hi = (y.min(), y.max()) if lim is None else lim
    pad = 0.06 * (hi - lo + 1e-12)
    a.axhline(0, color=GRID, lw=1.2, zorder=1)
    jy = _jitter(len(y)) if jitter else np.zeros(len(y))
    a.scatter(y, jy, s=s, c=[TOY_COL[k] for k in g], alpha=alpha,
              edgecolors="white", linewidths=0.5, zorder=3)
    if i is not None:
        a.plot(y[i], jy[i], "*", color=RED, ms=15, mec="white", zorder=5)
    a.set_xlim(lo - pad, hi + pad)
    a.set_ylim(-0.5, 0.5)
    _bare(a)


def _toy_p():
    X, g, i = _toy()
    D2 = _sqdist(X)
    Pc, sig = _conditional_p(X, TOY_PERP, D2=D2)
    return X, g, i, D2, Pc, sig


def _heat(a, M, g, title, color=INK, vmax=None):
    a.imshow(M, cmap=H_CMAP, interpolation="nearest",
             norm=PowerNorm(0.5, vmin=0, vmax=vmax if vmax else M.max()))
    for b in (14.5, 29.5):
        a.axhline(b, color=GRID, lw=0.8)
        a.axvline(b, color=GRID, lw=0.8)
    for k in range(3):
        a.add_patch(Rectangle((-2.8, 15 * k - 0.5), 1.6, 15,
                              color=TOY_COL[k], clip_on=False))
        a.add_patch(Rectangle((15 * k - 0.5, -2.8), 15, 1.6,
                              color=TOY_COL[k], clip_on=False))
    a.set_xlim(-0.5, 44.5); a.set_ylim(44.5, -0.5)
    _bare(a)
    a.set_title(title, color=color, fontsize=12, pad=12)


def _q_row(Y, i):
    d2 = (np.ravel(Y) - np.ravel(Y)[i]) ** 2
    w = np.exp(-d2)
    w[i] = 0
    return w / w.sum()


# ==========================================================================
# 1. dimension reduction
# ==========================================================================
@figure("crowding")
def crowding(fig):
    a = fig.add_axes([0.08, 0.36, 0.32, 0.56])
    th = np.linspace(0, 2 * np.pi, 7)[:-1]
    a.add_patch(Circle((0, 0), 1, fill=False, ec=GRID, ls="--"))
    for k, t in enumerate(th):
        a.plot([0, np.cos(t)], [0, np.sin(t)], color=GRID, lw=1)
        a.plot(np.cos(t), np.sin(t), "o", color=COMP[k % 5], ms=10)
    a.plot(0, 0, "*", color=RED, ms=16, mec="white")
    a.set_xlim(-1.4, 1.4); a.set_ylim(-1.4, 1.4); a.set_aspect("equal")
    _bare(a)
    a.set_title("2-D: six neighbours at distance 1", fontsize=12, pad=4,
                color=HIGH)
    a2 = fig.add_axes([0.08, 0.17, 0.32, 0.10])
    a2.plot([-3.2, 3.2], [0, 0], color=GRID, lw=1)
    for k, x in enumerate([-3.0, -2.0, -1.0, 1.0, 2.0, 3.0]):
        a2.plot(x, 0, "o", color=COMP[k % 5], ms=8)
    a2.plot(0, 0, "*", color=RED, ms=14, mec="white")
    a2.set_xlim(-3.6, 3.6); a2.set_ylim(-0.5, 0.5)
    _bare(a2)
    fig.text(0.24, 0.29, "1-D: only two fit at distance 1", ha="center",
             color=LOW, fontsize=11)

    a3 = fig.add_axes([0.54, 0.34, 0.40, 0.54])
    rng = np.random.default_rng(0)
    for d, c in zip((2, 10, 50), (GREEN, GOLD, RED)):
        r = rng.random(20000) ** (1 / d)     # the radius of a uniform point
        a3.hist(r, bins=np.linspace(0, 1, 50), density=True, histtype="step",
                lw=2, color=c, label=f"$d = {d}$")
    a3.set_xlabel("distance to the centre")
    a3.set_yticks([])
    a3.legend(loc="upper left")
    a3.set_title("Unit ball points", fontsize=12, pad=6,
                 color=INK)
    despine(a3, keep=("bottom",))
    _foot(fig, "In high dimension most neighbours sit at about the same "
          "distance.\nA low-dimensional map has no room to place them all.")


@figure("dr_obstacles")
def dr_obstacles(fig):
    rng = np.random.default_rng(2)
    W_, H_ = 0.27, 0.25
    pos = [(0.04 + c * 0.33, 0.66 - r * 0.38) for r in range(2) for c in range(3)]
    titles = ["topology: a loop must be cut",
              "curvature: the straight line lies",
              "more true dimensions than the map",
              "concentration: all distances alike",
              "noise: useless features blur",
              "density: one scale does not fit all"]
    axs = []
    for (x, y), t in zip(pos, titles):
        a = fig.add_axes([x, y, W_, H_])
        _bare(a)
        a.set_title(t, fontsize=11, color=INK, pad=3)
        axs.append(a)

    # 1. a circle onto a line: neighbours across the cut end up far apart
    a = axs[0]
    th = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    cm = plt.get_cmap("viridis")
    a.scatter(np.cos(th) * 0.8 - 1.4, np.sin(th) * 0.8, c=th, cmap=cm, s=14)
    a.scatter(np.linspace(0.3, 2.6, 24), np.zeros(24) - 0.0, c=th, cmap=cm,
              s=14)
    a.annotate("", xy=(0.2, 0), xytext=(-0.45, 0),
               arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.4))
    a.plot([0.3, 2.6], [-0.35, -0.35], color=RED, lw=0)
    a.annotate("", xy=(0.3, -0.25), xytext=(2.6, -0.25),
               arrowprops=dict(arrowstyle="<->", color=RED, lw=1.2,
                               connectionstyle="arc3,rad=0.35"))
    a.set_xlim(-2.4, 2.8); a.set_ylim(-1.1, 1.1); a.set_aspect("equal")

    # 2. a spiral: two points close in the plane, far along the curve
    a = axs[1]
    t = np.linspace(0.5 * np.pi, 4.7 * np.pi, 400)
    a.plot(t * np.cos(t), t * np.sin(t), color=GRID, lw=2)
    t1, t2 = 2.5 * np.pi, 4.5 * np.pi
    p1 = np.array([t1 * np.cos(t1), t1 * np.sin(t1)])
    p2 = np.array([t2 * np.cos(t2), t2 * np.sin(t2)])
    tt = np.linspace(t1, t2, 200)
    a.plot(tt * np.cos(tt), tt * np.sin(tt), color=GREEN, lw=2)
    a.plot(*np.array([p1, p2]).T, color=RED, lw=1.8, ls="--")
    a.plot(*p1, "o", color=INK, ms=5); a.plot(*p2, "o", color=INK, ms=5)
    a.set_aspect("equal")

    # 3. a uniform cube seen from one side: the hidden axis mixes colours
    a = axs[2]
    C = rng.random((400, 3))
    a.scatter(C[:, 0], C[:, 1], c=C[:, 2], cmap="viridis", s=6)
    a.set_aspect("equal")

    # 4. distances in d = 2 against d = 1000
    a = axs[3]
    for d, c in ((2, GREEN), (1000, RED)):
        Z = rng.random((300, d))
        D = np.sqrt(_sqdist(Z)[np.triu_indices(300, 1)])
        a.hist(D / D.mean(), bins=np.linspace(0, 2.2, 50), density=True,
               histtype="step", lw=1.8, color=c)
    a.text(0.15, 0.8, "d = 2", color=GREEN, fontsize=9.5,
           transform=a.transAxes)
    a.text(0.62, 0.8, "d = 1000", color=RED, fontsize=9.5,
           transform=a.transAxes)
    a.spines["bottom"].set_visible(True)

    # 5. two groups: within- and between-group distances, with noise added
    a = axs[4]
    for noise, ls in ((0, "-"), (50, "--")):
        A = np.c_[rng.normal(0, 0.5, (150, 2)), rng.normal(0, 0.5, (150, noise))]
        B = np.c_[rng.normal(3, 0.5, (150, 2)), rng.normal(0, 0.5, (150, noise))]
        win = np.sqrt(_sqdist(A)[np.triu_indices(150, 1)])
        btw = np.sqrt(((A[:, None] - B[None]) ** 2).sum(-1)).ravel()
        bins = np.linspace(0, 9, 60)
        a.hist(win, bins=bins, density=True, histtype="step", color=BLUE,
               lw=1.6, ls=ls)
        a.hist(btw, bins=bins, density=True, histtype="step", color=GOLD,
               lw=1.6, ls=ls)
    a.set_ylim(0, a.get_ylim()[1] * 1.45)
    a.text(0.5, 0.97, "distances within / between two groups;\n"
           "dashed: 50 noise features added", color=MUTED, fontsize=8.5,
           ha="center", va="top", transform=a.transAxes)
    a.spines["bottom"].set_visible(True)

    # 6. a dense and a sparse group
    a = axs[5]
    a.scatter(*rng.normal([-1.5, 0], 0.15, (80, 2)).T, s=5, color=BLUE)
    a.scatter(*rng.normal([1.3, 0], 0.9, (80, 2)).T, s=5, color=GOLD)
    a.set_xlim(-2.4, 3.6); a.set_ylim(-2.0, 2.0); a.set_aspect("equal")

    _foot(fig, "No low-dimensional map keeps every distance: each method "
          "chooses what to preserve.\nPCA keeps the directions of largest "
          "variance; SNE and t-SNE keep the local neighbours.")


# ==========================================================================
# 2. reminders on PCA
# ==========================================================================
@figure("eq_pca_model")
def eq_pca_model(fig):
    ax = canvas(fig)
    dx = 1.85
    _matrix(ax, 0.70 + dx, 1.35, 1.10, 1.90, HIGH, G_CMAP, label=r"$X$",
            shape=r"$N \times d$", seed=1, nrow=12, ncol=7)
    ax.text(2.10 + dx, 2.30, r"$\approx$", fontsize=24, ha="center",
            va="center")
    _matrix(ax, 2.45 + dx, 1.35, 0.45, 1.90, LOW,
            LinearSegmentedColormap.from_list("lm", ["#ffffff", "#f3e3c7", GOLD]),
            label=r"$Z$", shape=r"$N \times q$", seed=2, nrow=12, ncol=2)
    ax.text(3.17 + dx, 2.30, r"$\times$", fontsize=18, ha="center", va="center")
    _matrix(ax, 3.45 + dx, 2.60, 1.10, 0.55, PCA_C, P_CMAP, label=r"$P^T$",
            shape=r"$q \times d$", seed=3, nrow=2, ncol=7)
    ax.text(4.85 + dx, 2.30, r"$+$ noise", fontsize=15, ha="left", va="center",
            color=MUTED)
    _foot(fig, r"$P \in \mathbb{R}^{d \times q}$ has $q < d$ orthonormal "
          r"columns ($P^T P = I_q$) and $Z = XP$ holds the coordinates." "\n"
          "P is chosen so that the variance of the projected data is maximal.")


@figure("pca_gaussian")
def pca_gaussian(fig):
    rng = np.random.default_rng(1)
    S = np.array([[3.0, -1.9], [-1.9, 1.6]])
    X = rng.multivariate_normal([0, 0], S, 400)
    Z, lam, V = _pca(X, 2)
    lim = (-5.2, 5.2, -3.4, 3.4)
    titles = ["data and principal axes", "projection on the first axis",
              "principal components"]
    axes = [fig.add_axes([0.02 + i * 0.33, 0.12, 0.30, 0.72]) for i in range(3)]
    for a, t in zip(axes, titles):
        a.set_title(t, fontsize=12.5, pad=6, color=INK)
        a.set_xlim(lim[:2]); a.set_ylim(lim[2:]); a.set_aspect("equal")
        _bare(a)
    a = axes[0]
    a.scatter(*X.T, s=5, color=HIGH, alpha=0.5, edgecolors="none")
    for k, c in zip((0, 1), (PCA_C, GOLD)):
        v = V[:, k] * 2 * np.sqrt(lam[k])
        a.add_patch(FancyArrowPatch((0, 0), tuple(v), arrowstyle="-|>",
                                    mutation_scale=14, lw=2.4, color=c, zorder=4))
        a.text(*(v * 1.22), f"$p_{k + 1}$", color=c, fontsize=13,
               ha="center", va="center")
    a = axes[1]
    p = V[:, 0]
    proj = np.outer(X @ p, p)
    for i in range(0, 400, 6):
        a.plot([X[i, 0], proj[i, 0]], [X[i, 1], proj[i, 1]], color=GRID, lw=0.6)
    a.scatter(*X.T, s=4, color=HIGH, alpha=0.3, edgecolors="none")
    a.plot(*np.outer([-6, 6], p).T, color=PCA_C, lw=1.4)
    a.scatter(*proj.T, s=5, color=PCA_C, alpha=0.7, edgecolors="none")
    a = axes[2]
    a.scatter(Z[:, 0], Z[:, 1], s=5, color=LOW, alpha=0.6, edgecolors="none")
    a.axhline(0, color=GRID, lw=1); a.axvline(0, color=GRID, lw=1)
    a.text(4.9, 0.25, "$z_1$", color=INK, fontsize=12, ha="right")
    a.text(0.2, 3.1, "$z_2$", color=INK, fontsize=12)
    fig.text(0.5, 0.04, f"the first axis keeps {100 * lam[0] / lam.sum():.0f}% "
             "of the variance; the components are decorrelated",
             ha="center", color=MUTED, fontsize=11)


@figure("eq_pca_views")
def eq_pca_views(fig):
    ax = canvas(fig)
    ax.plot([4.50, 4.50], [1.35, 3.40], color=GRID, lw=1.2)
    ax.text(0.45, 3.35, "1.  Minimise the reconstruction error", color=PCA_C,
            fontsize=13, weight="bold", va="center")
    ax.text(2.45, 2.45, r"$\min_{P \in \mathbb{R}^{d \times q}}\ \sum_{i=1}^N"
            r"\ \| x_i - P P^T x_i \|^2$", fontsize=15, ha="center",
            va="center")
    ax.text(2.45, 1.70, r"$P P^T x_i$: the projection of $x_i$", color=MUTED,
            fontsize=11, ha="center", va="center")
    ax.text(4.80, 3.35, "2.  Maximise the projected variance", color=GREEN,
            fontsize=13, weight="bold", va="center")
    ax.text(6.70, 2.45, r"$\max_{p \in \mathbb{R}^d}\ \| X p \|_2^2$"
            r"$\quad \mathrm{s.t.}\ \| p \|_2 = 1$", fontsize=15,
            ha="center", va="center")
    ax.text(6.70, 1.70, r"the $q$ largest eigenvalues of $\Sigma$",
            color=MUTED, fontsize=11, ha="center", va="center")
    box(ax, 0.70, 0.30, 7.60, 0.78, INK, "", fill="#f6f6f7", lw=1.2)
    ax.text(W / 2, 0.86, "The same answer, two classic tools", ha="center",
            va="center", color=INK, fontsize=11.5, weight="bold")
    ax.text(W / 2, 0.50, r"eigenvalues of the covariance: $\Sigma = V \Lambda "
            r"V^T$$\qquad$ singular values of the data: $X = U S V^T$",
            ha="center", va="center", color=INK, fontsize=12)


@figure("pca_algorithm")
def pca_algorithm(fig):
    ax = canvas(fig)
    _algo(ax, 0.40, 3.40, [
        r"standardise: $X_{ij} \leftarrow (X_{ij} - \mu_j) / \sigma_j$",
        r"correlation matrix: $\Sigma = \frac{1}{N - 1} X^T X$",
        r"eigen-decomposition of $\Sigma$: $\{ p_j, \lambda_j \}$",
        r"order the $\lambda_j$ by decreasing value",
        r"principal axes: $P = (p_1, \dots, p_q) \in \mathbb{R}^{d \times q}$",
        r"principal components: $Z = X P$",
    ], size=12, leading=0.47)
    ax.plot([5.30, 5.30], [0.80, 3.45], color=GRID, lw=1.2)
    code = ("Xs = (X - X.mean(0)) / X.std(0)\n"
            "S = Xs.T @ Xs / (N - 1)\n"
            "lam, V = np.linalg.eigh(S)\n"
            "order = np.argsort(lam)[::-1]\n"
            "P = V[:, order[:q]]\n"
            "Z = Xs @ P")
    ax.text(5.55, 3.30, code, family="monospace", fontsize=9.8, va="top",
            color=INK, linespacing=1.75)
    ax.text(5.55, 0.95, "sklearn.decomposition.PCA(q)", family="monospace",
            fontsize=9.8, color=PCA_C, va="center")
    note(ax, "Standardise when the features have different units",
         y=0.30, size=11)


@figure("pca_nonlinear")
def pca_nonlinear(fig):
    X, t = _swiss_roll()
    a1 = fig.add_axes([0.0, 0.10, 0.34, 0.80], projection="3d")
    a1.scatter(X[:, 0], X[:, 1], X[:, 2], c=t, cmap="viridis", s=4,
               depthshade=False)
    a1.view_init(10, -70)
    a1.set_xticks([]); a1.set_yticks([]); a1.set_zticks([])
    a1.set_title("swiss roll in 3-D", color=HIGH, fontsize=12.5, y=0.96)
    Z, _, _ = _pca(X, 2)
    a2 = fig.add_axes([0.38, 0.17, 0.27, 0.62])
    _roll_scatter(a2, Z, t)
    a2.set_title("PCA: the roll is flattened", color=PCA_C, fontsize=12.5,
                 pad=10)
    a3 = fig.add_axes([0.70, 0.17, 0.27, 0.62])
    _roll_scatter(a3, np.c_[t, X[:, 1]], t)
    a3.set_title("ideally: unrolled", color=GREEN, fontsize=12.5,
                 pad=10)
    fig.text(0.5, 0.05, "coloured by position along the roll", ha="center", color=MUTED,
             fontsize=11)


# ==========================================================================
# 3. stochastic neighbour embedding
# ==========================================================================
@figure("sne_steps")
def sne_steps(fig):
    ax = canvas(fig)
    xs = (0.35, 3.25, 6.15)
    ws = 2.50
    yb = 1.75
    heads = ["1.  in the data", "2.  start the map", "3.  in the map"]
    bodies = [r"distances $\to$ probabilities $P$",
              r"random $y_1, \dots, y_N$",
              r"measure $Q$, compare, move"]
    subs = [r"once, at the start", r"$Y^{(0)} \sim \mathcal{N}(0, 10^{-4} I)$",
            r"until $\mathrm{KL}(P \,\|\, Q)$ stops falling"]
    cols = [HIGH, LOW, GREEN]
    for x, hd, bd, sb, c in zip(xs, heads, bodies, subs, cols):
        box(ax, x, yb, ws, 1.25, c, "", fill="white")
        ax.text(x + ws / 2, yb + 0.98, hd, ha="center", va="center", color=c,
                fontsize=12.5, weight="bold")
        ax.text(x + ws / 2, yb + 0.57, bd, ha="center", va="center", color=INK,
                fontsize=12)
        ax.text(x + ws / 2, yb + 0.22, sb, ha="center", va="center",
                color=MUTED, fontsize=10.5)
    arrow(ax, (2.92, yb + 0.63), (3.18, yb + 0.63))
    arrow(ax, (5.82, yb + 0.63), (6.08, yb + 0.63))
    ax.add_patch(FancyArrowPatch((8.10, yb - 0.10), (6.75, yb - 0.10),
                                 arrowstyle="-|>", mutation_scale=14, lw=2.0,
                                 color=GREEN, connectionstyle="arc3,rad=-0.9"))
    ax.text(8.30, yb - 0.45, "repeat", ha="left", color=GREEN, fontsize=11)


@figure("sne_toy")
def sne_toy(fig):
    X, g, _ = _toy()
    a = fig.add_axes([0.05, 0.19, 0.40, 0.72])
    _toy_plane(a, X, g)
    a.set_title("data: 45 points in 2-D", color=HIGH, fontsize=12.5,
                pad=4)
    b = fig.add_axes([0.52, 0.48, 0.44, 0.16])
    b.axhline(0, color=GRID, lw=1.6)
    for x in np.linspace(-1, 1, 9):
        b.text(x, 0.05, "?", ha="center", va="bottom", color=LOW, fontsize=13)
    b.set_xlim(-1.2, 1.2); b.set_ylim(-0.3, 0.5)
    _bare(b)
    b.set_title("mapping: 45 numbers on a line", color=LOW, fontsize=12.5,
                pad=2)
    _foot(fig, "Three groups (tight, wide, medium) in 2-D, mapped onto a "
          "line so that both can be drawn.\n"
          "SNE never sees the groups.")


# ==========================================================================
# 4. step 1: distances to probabilities
# ==========================================================================
@figure("sne_distances")
def sne_distances(fig):
    X, g, i, D2, _, _ = _toy_p()
    a = fig.add_axes([0.03, 0.08, 0.40, 0.84])
    for j in range(len(X)):
        if j != i:
            a.plot(*np.array([X[i], X[j]]).T, color=GRID, lw=0.8, zorder=1)
    _toy_plane(a, X, g, i)
    a.text(*(X[i] + [0.25, 0.30]), "$x_i$", color=RED, fontsize=14, zorder=6)
    d = np.sqrt(D2[i])
    order = [j for j in np.argsort(d) if j != i]
    b = fig.add_axes([0.53, 0.22, 0.43, 0.60])
    b.bar(np.arange(len(order)), d[order], color=[TOY_COL[g[j]] for j in order],
          width=0.8)
    b.set_xticks([])
    b.set_xlabel("other 44 points, ordered nearest first")
    b.set_ylabel(r"$\| x_i - x_j \|$")
    b.set_title("distances from $x_i$", color=INK, fontsize=12.5, pad=6)
    despine(b, keep=("left", "bottom"))
    fig.text(0.745, 0.05, "a distance says how far, not who is a neighbour",
             ha="center", color=MUTED, fontsize=11)


@figure("sne_gaussian")
def sne_gaussian(fig):
    X, g, i, D2, _, sig = _toy_p()
    s = sig[i]
    a = fig.add_axes([0.03, 0.08, 0.40, 0.84])
    _toy_plane(a, X, g, i)
    for k, ls in ((1, "-"), (2, "--"), (3, ":")):
        a.add_patch(Circle(X[i], k * s, fill=False, ec=RED, lw=1.3, ls=ls,
                           zorder=4))
    a.text(X[i, 0] + s * 0.75, X[i, 1] + s * 0.75 + 0.1, r"$\sigma_i$",
           color=RED, fontsize=12, zorder=6)
    d = np.sqrt(D2[i])
    b = fig.add_axes([0.53, 0.22, 0.43, 0.60])
    t = np.linspace(0, d.max() * 1.02, 300)
    b.plot(t, np.exp(-t ** 2 / (2 * s ** 2)), color=RED, lw=2)
    for j in range(len(X)):
        if j == i:
            continue
        v = np.exp(-d[j] ** 2 / (2 * s ** 2))
        b.plot([d[j], d[j]], [0, v], color=TOY_COL[g[j]], lw=0.8, alpha=0.6)
        b.plot(d[j], v, "o", color=TOY_COL[g[j]], ms=5, mec="white", mew=0.5)
    b.set_xlabel(r"distance $\| x_i - x_j \|$")
    b.set_ylabel("similarity")
    b.set_title(r"a bell centred on $x_i$: $\exp(-\| x_i - x_j \|^2 / "
                r"2 \sigma_i^2)$", color=INK, fontsize=12, pad=6)
    despine(b, keep=("left", "bottom"))
    fig.text(0.745, 0.05, "near points get a high similarity, far ones "
             "almost zero", ha="center", color=MUTED, fontsize=11)


@figure("sne_normalise")
def sne_normalise(fig):
    X, g, i, D2, Pc, _ = _toy_p()
    p = Pc[i]
    a = fig.add_axes([0.03, 0.08, 0.40, 0.84])
    _toy_plane(a, X, g, i, sizes=8 + 900 * p)
    a.text(0.02, 0.02, r"area $\propto p_{j|i}$", transform=a.transAxes,
           color=INK, fontsize=15)
    order = [j for j in np.argsort(D2[i]) if j != i]
    b = fig.add_axes([0.53, 0.22, 0.43, 0.48])
    b.bar(np.arange(len(order)), p[order], color=[TOY_COL[g[j]] for j in order],
          width=0.8)
    b.set_xticks([])
    b.set_xlabel("other 44 points, ordered nearest first")
    b.set_ylabel(r"$p_{j|i}$")
    despine(b, keep=("left", "bottom"))
    k = int(np.argmax(np.cumsum(p[order]) > 0.9)) + 1
    b.axvline(k - 0.5, color=MUTED, lw=1, ls="--")
    b.text(k, p.max() * 0.85, f"{k} points hold 90%", color=MUTED,
           fontsize=10.5)
    ax = canvas(fig)
    ax.text(6.70, 3.25, r"$p_{j|i} = \dfrac{\exp(-\| x_i - x_j \|^2 / "
            r"2 \sigma_i^2)}{\sum_{k \neq i} \exp(-\| x_i - x_k \|^2 / "
            r"2 \sigma_i^2)}$", ha="center", va="center", fontsize=12.5)
    fig.text(0.745, 0.05, r"divide by the sum: the similarities of $x_i$ "
             "become a distribution", ha="center", color=MUTED,
             fontsize=11)


@figure("sigma_effect")
def sigma_effect(fig):
    rng = np.random.default_rng(5)
    A = rng.normal([-2.0, 0.0], 0.35, (70, 2))
    B = rng.normal([2.2, 0.0], 1.30, (70, 2))
    X = np.vstack([A, B])
    D2 = _sqdist(X)
    i_dense, i_sparse = 0, 70 + int(np.argmin(((B - [2.2, 0]) ** 2).sum(1)))
    _, sig = _conditional_p(X, perp=10, D2=D2)

    def row(i, s):
        w = np.exp(-D2[i] / (2 * s ** 2))
        w[i] = 0
        return w / w.sum()

    titles = ["one width σ for every point", "a width σᵢ per point "
              "(perplexity 10)"]
    for k, title in enumerate(titles):
        a = fig.add_axes([0.03 + k * 0.50, 0.14, 0.44, 0.70])
        p = row(i_dense, 0.6) + row(i_sparse, 0.6) if k == 0 else \
            row(i_dense, sig[i_dense]) + row(i_sparse, sig[i_sparse])
        a.scatter(*X.T, s=8, color=GRID, edgecolors="none")
        a.scatter(*X.T, s=600 * p, color=HIGH, alpha=0.75, edgecolors="none")
        for i, c in ((i_dense, RED), (i_sparse, RED)):
            a.plot(*X[i], "*", color=c, ms=14, mec="white")
        for i in (i_dense, i_sparse):
            s = 0.6 if k == 0 else sig[i]
            a.add_patch(Circle(X[i], 2 * s, fill=False, ec=RED, lw=1.2,
                               ls="--"))
        a.set_xlim(-3.5, 6.2); a.set_ylim(-3.2, 3.2); a.set_aspect("equal")
        _bare(a)
        a.set_title(title, fontsize=12.5, pad=6,
                    color=RED if k == 0 else GREEN)
    fig.text(0.27, 0.05, "dense region: many neighbours;  sparse: almost none",
             ha="center", color=MUTED, fontsize=10.5)
    fig.text(0.77, 0.05, "about the same number of neighbours everywhere",
             ha="center", color=MUTED, fontsize=10.5)


@figure("eq_perplexity")
def eq_perplexity(fig):
    ax = canvas(fig)
    ax.text(2.10, 2.75, r"$\mathrm{Perp}(P_i) = 2^{H(P_i)}$", ha="center",
            va="center", fontsize=17)
    ax.text(2.10, 2.15, r"$H(P_i) = -\sum_j p_{j|i} \log_2 p_{j|i}$",
            ha="center", va="center", fontsize=13)
    ax.text(2.10, 1.70, "the Shannon entropy of the neighbours of point i",
            ha="center", va="center", color=MUTED, fontsize=11)
    ax.text(2.10, 1.25, r"uniform on $k$ points: $\mathrm{Perp} = k$",
            ha="center", va="center", color=MUTED, fontsize=11)
    X, _ = _digits_subset()
    tr = (0, [])
    _conditional_p(X, perp=30, trace=tr)
    s = np.logspace(0.3, 2, 200)
    D2 = np.delete(_sqdist(X)[0], 0)
    perp = np.array([2 ** _row_p(D2, 1 / (2 * v ** 2))[1] for v in s])
    a = fig.add_axes([0.53, 0.30, 0.43, 0.62])
    a.semilogx(s, perp, color=HIGH)
    a.axhline(30, color=GREEN, lw=1.2, ls="--")
    a.fill_between(s, 30, 620, color=RED, alpha=0.06, lw=0)
    a.fill_between(s, -20, 30, color=BLUE, alpha=0.06, lw=0)
    a.text(2.3, 330, "too many neighbours:\nshrink σᵢ", color=RED,
           fontsize=10.5, va="center")
    a.text(40, -5, "too few: widen σᵢ", color=BLUE, fontsize=10.5,
           va="bottom")
    tsig, tp = zip(*tr[1])
    a.plot(tsig, tp, "o", color=RED, ms=4.5, zorder=4)
    for j, (u, v) in enumerate(tr[1][:4]):
        a.text(u * 1.08, v + 14, str(j + 1), color=RED, fontsize=9.5)
    a.text(2.3, 40, "target 30", color=GREEN, fontsize=10.5)
    a.set_ylim(-20, 620)
    a.set_xlabel(r"$\sigma_i$ (log scale)")
    a.set_ylabel(r"$\mathrm{Perp}(P_i)$")
    despine(a, keep=("left", "bottom"))
    _foot(fig, r"$\sigma_i$ is found by bisection: try a width, compute the "
          r"perplexity of $p_{\cdot|i}$, shrink $\sigma_i$ if it is too high, "
          "widen it if too low,\nand halve the step until the target is met "
          "(red dots, for one digit). Usual targets: 5 to 50.")


@figure("eq_sne_p")
def eq_sne_p(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"$p_{j|i} = \dfrac{\exp(-\| x_i - x_j \|^2 / 2 \sigma_i^2)}"
         r"{\sum_{k \neq i} \exp(-\| x_i - x_k \|^2 / 2 \sigma_i^2)}$",
         r"chance that $x_i$ picks $x_j$ as its neighbour", BLUE),
        (r"$p_{i|i} = 0$",
         "a point is not its own neighbour", INK),
        (r"$p_{ij} = \dfrac{p_{j|i} + p_{i|j}}{2N}$",
         r"symmetrised: one distribution over all the pairs, "
         r"$\sum_{i,j} p_{ij} = 1$", GREEN),
    ], top=3.35, gap=1.0, x=2.2, eq_size=13.5, why_off=0.46)
    _foot(fig, r"By default $p_{j|i} \neq p_{i|j}$", RED)


@figure("p_matrix")
def p_matrix(fig):
    X, g, i, D2, Pc, _ = _toy_p()
    P = (Pc + Pc.T) / (2 * len(X))
    a1 = fig.add_axes([0.16, 0.17, 0.30, 0.66])
    _heat(a1, Pc, g, r"$p_{j|i}$: row $i$ sums to 1", HIGH)
    a2 = fig.add_axes([0.56, 0.17, 0.30, 0.66])
    _heat(a2, P, g, r"$p_{ij}$: symmetric, all sum to 1", HIGH)
    _foot(fig, "One row per point; the blocks: neighbours lie in the same "
          "group.")


# ==========================================================================
# 5. step 2: initialize the map
# ==========================================================================
@figure("init_random")
def init_random(fig):
    X, g, i = _toy()
    Y0 = _toy_run()[0][0]
    a = fig.add_axes([0.05, 0.19, 0.36, 0.72])
    _toy_plane(a, X, g)
    a.set_title("data", color=HIGH, fontsize=12.5, pad=4)
    b = fig.add_axes([0.47, 0.44, 0.50, 0.22])
    _strip(b, Y0, g)
    b.set_title(r"map at $t = 0$: $y_i \sim \mathcal{N}(0, 10^{-4})$",
                color=LOW, fontsize=12.5, pad=4)
    lo, hi = Y0.min(), Y0.max()
    b.text(lo, -0.45, f"{lo:.4f}", color=MUTED, fontsize=9.5, ha="left")
    b.text(hi, -0.45, f"{hi:.4f}", color=MUTED, fontsize=9.5, ha="right")


@figure("init_choices")
def init_choices(fig):
    X, g, _ = _toy()
    runs = [((0, "random"), "random, seed 0"), ((1, "random"), "random, seed 1"),
            ((0, "pca"), "first PCA axis")]
    ax = canvas(fig)
    ax.text(0.15, 2.95, "start", color=LOW, fontsize=12, weight="bold",
            va="center")
    ax.text(0.15, 1.45, "after\nSNE", color=GREEN, fontsize=12,
            weight="bold", va="center")
    for k, (args, title) in enumerate(runs):
        h = _toy_run(*args)
        x0 = 0.11 + k * 0.30
        a = fig.add_axes([x0, 0.70, 0.26, 0.14])
        _strip(a, h[0][0], g, s=18)
        a.set_title(title, fontsize=12, color=INK, pad=4)
        b = fig.add_axes([x0, 0.30, 0.26, 0.14])
        _strip(b, h[TOY_ITERS][0], g, s=18)
        fig.text(x0 + 0.13, 0.22, f"KL = {h[TOY_ITERS][2]:.3f}", ha="center",
                 color=MUTED, fontsize=11)
    note(ax, "Initialization decides which minimum is found; PCA initialization is deterministic",
         y=0.30, size=11)


# ==========================================================================
# 6. step 3: measure, compare, move
# ==========================================================================
@figure("eq_sne_q")
def eq_sne_q(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"$q_{j|i} = \dfrac{\exp(-\| y_i - y_j \|^2)}"
         r"{\sum_{k \neq i} \exp(-\| y_i - y_k \|^2)}$",
         r"same as $p_{j|i}$", LOW),
        (r"$q_{ij} = \dfrac{\exp(-\| y_i - y_j \|^2)}"
         r"{\sum_{k \neq l} \exp(-\| y_k - y_l \|^2)}$",
         r"symmetric SNE, like $p_{ij}$",
         LOW),
    ], top=3.15, gap=1.35, x=2.2, eq_size=13.5, why_off=0.52)
    _foot(fig, r"Fixed width $\sigma = 1/\sqrt{2}$.")


@figure("q_neighbours")
def q_neighbours(fig):
    X, g, i, D2, Pc, _ = _toy_p()
    h = _toy_run()
    late = 50
    Yl = h[late][0].ravel()
    span = Yl.max() - Yl.min()
    lim = (Yl.min() - 0.08 * span, Yl.max() + 0.08 * span)
    order = [j for j in np.argsort(D2[i]) if j != i]
    rows = ((0, "at the start, t = 0: every point is inside the bell"),
            (late, f"after {late} moves: the bell covers only the near points"))
    for k, (t, title) in enumerate(rows):
        Y = h[t][0].ravel()
        q = _q_row(Y, i)
        y0 = 0.58 if k == 0 else 0.20
        a = fig.add_axes([0.05, y0, 0.47, 0.24])
        _strip(a, Y, g, i, s=18, lim=lim)
        u = np.linspace(*lim, 400)
        a.fill_between(u, -0.02, 0.40 * np.exp(-(u - Y[i]) ** 2) - 0.02,
                       color=RED, alpha=0.10, lw=0, zorder=1)
        a.plot(u, 0.40 * np.exp(-(u - Y[i]) ** 2) - 0.02, color=RED, lw=1.4,
               zorder=2)
        a.set_ylim(-0.3, 0.45)
        a.set_title(title, fontsize=11.5, color=LOW, pad=2, loc="left")
        b = fig.add_axes([0.58, y0, 0.39, 0.24])
        xx = np.arange(len(order))
        b.bar(xx, Pc[i, order], width=0.8, color=HIGH, alpha=0.35,
              label=r"$p_{j|i}$ (data)")
        b.bar(xx, q[order], width=0.4, color=LOW, label=r"$q_{j|i}$ (map)")
        b.set_xticks([])
        b.set_yticks([])
        b.set_ylim(0, Pc[i].max() * 1.1)
        despine(b, keep=("bottom",))
        if k == 0:
            b.legend(loc="upper right", fontsize=10)
    _foot(fig, "At the start, all the projected points are in the center of the bell.")


@figure("eq_kl")
def eq_kl(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.35, r"$\mathrm{KL}(P \,\|\, Q) = \sum_{k} p_k\,"
            r"\log \dfrac{p_k}{q_k}$", ha="center", va="center", fontsize=16)
    P = np.array([0.40, 0.30, 0.15, 0.10, 0.04, 0.01])
    Q = np.array([0.15, 0.20, 0.25, 0.20, 0.12, 0.08])
    c = P * np.log(P / Q)
    k = np.arange(6)
    a = fig.add_axes([0.08, 0.27, 0.38, 0.50])
    a.bar(k - 0.19, P, 0.36, color=HIGH, label="$P$ (data)")
    a.bar(k + 0.19, Q, 0.36, color=LOW, label="$Q$ (map)")
    a.set_xticks(k, [f"{j + 1}" for j in k])
    a.set_yticks([0, 0.2, 0.4])
    a.legend(loc="upper right")
    a.set_title("two distributions over the same items", fontsize=11.5,
                color=INK, pad=4)
    despine(a, keep=("left", "bottom"))
    b = fig.add_axes([0.56, 0.27, 0.38, 0.50])
    b.bar(k, c, 0.6, color=[RED if v > 0 else BLUE for v in c])
    b.axhline(0, color=INK, lw=0.8)
    b.set_xticks(k, [f"{j + 1}" for j in k])
    b.set_title(rf"each term $p_k \log(p_k / q_k)$: total = {c.sum():.2f}",
                fontsize=11.5, color=INK, pad=4)
    despine(b, keep=("left", "bottom"))
    kl = lambda u, v: float((u * np.log(u / v)).sum())
    _foot(fig, "The big terms are where P puts weight but Q does not. "
          rf"KL $\geq 0$, zero only when $Q = P$, and not symmetric: "
          rf"here KL(Q‖P) = {kl(Q, P):.2f}." "\n"
          r"In SNE the items are the pairs $(i, j)$: KL measures how badly Q "
          "reproduces the neighbourhoods of P.")


@figure("kl_asymmetry")
def kl_asymmetry(fig):
    dx = np.linspace(0, 3, 300)
    dy = np.linspace(0, 3, 300)
    DX, DY = np.meshgrid(dx, dy)
    C = np.exp(-DX ** 2) * (DY ** 2 - DX ** 2)
    a = fig.add_axes([0.30, 0.34, 0.34, 0.62])
    vmax = np.abs(C).max()
    im = a.pcolormesh(DX, DY, C, cmap="RdBu_r", vmin=-vmax, vmax=vmax,
                      shading="auto", rasterized=True)
    a.set_xlabel("distance in the data")
    a.set_ylabel("distance in the map")
    a.plot([0, 3], [0, 3], color=INK, lw=0.8, ls="--")
    bb = dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85)
    a.plot(0.3, 2.6, "o", color=INK, ms=6)
    a.text(0.45, 2.6, "1: near in the data,\nfar in the map", fontsize=10,
           va="center", bbox=bb)
    a.plot(2.6, 0.3, "o", color=INK, ms=6)
    a.text(2.45, 0.62, "2: far in the data,\nnear in the map", fontsize=10,
           va="center", ha="right", bbox=bb)
    cb = fig.colorbar(im, ax=a, fraction=0.05, pad=0.03)
    cb.set_label(r"$p \log (p / q)$", fontsize=10)
    cb.ax.tick_params(labelsize=8)
    _foot(fig, "KL makes near points mapped far apart (1) cost much more "
          "than far points mapped close together (2).\nSo SNE keeps the "
          "local structure.")


@figure("sne_forces")
def sne_forces(fig):
    X, g, i, _, Pc, _ = _toy_p()
    P = (Pc + Pc.T) / (2 * len(X))
    Y, Q, _ = _toy_run()[TOY_MID]
    y = Y.ravel()
    f = -4 * (P[i] - Q[i]) * (y[i] - y)       # minus the gradient, per pair
    f[i] = 0
    attract = P[i] > Q[i]
    pull = [j for j in np.argsort(-np.abs(f)) if attract[j] and j != i][:4]
    push = [j for j in np.argsort(-np.abs(f)) if not attract[j] and j != i][:4]
    top = sorted(pull + push, key=lambda j: y[j])
    a = fig.add_axes([0.05, 0.22, 0.90, 0.76])
    span = y.max() - y.min()
    lim = (y.min() - 0.08 * span, y.max() + 0.08 * span)
    a.axhline(0, color=GRID, lw=1.2)
    a.scatter(y, _jitter(len(y)) * 0.6, s=22, c=[TOY_COL[k] for k in g],
              edgecolors="white", linewidths=0.5, zorder=3)
    a.plot(y[i], 0, "*", color=RED, ms=15, mec="white", zorder=5)
    scale = 0.30 * span / np.abs(f[top]).max()
    for r, j in enumerate(top):
        h = 0.55 + r * 0.21
        c = GREEN if attract[j] else RED
        a.plot([y[j]], [h], "o", color=TOY_COL[g[j]], ms=6, zorder=4)
        a.plot([y[j], y[j]], [0.08, h], color=GRID, lw=0.6, ls=":")
        a.add_patch(FancyArrowPatch((y[i], h), (y[i] + f[j] * scale, h),
                                    arrowstyle="-|>", mutation_scale=10,
                                    lw=1.8, color=c, zorder=4,
                                    shrinkA=0, shrinkB=0))
    a.axvline(y[i], color=RED, lw=0.6, ls=":", ymin=0.1)
    net = np.sign(f.sum()) * 0.18 * span
    a.add_patch(FancyArrowPatch((y[i], -0.55), (y[i] + net, -0.55),
                                arrowstyle="-|>", mutation_scale=14, lw=3,
                                color=INK, zorder=4, shrinkA=0, shrinkB=0))
    a.text(y[i] + net / 2, -0.82, "the sum of all 44 springs: the move of "
           "the star", ha="center", color=INK, fontsize=10.5)
    a.set_xlim(*lim); a.set_ylim(-0.95, 0.55 + 8 * 0.21 + 0.1)
    _bare(a)
    _foot(fig, r"One spring per pair: $p_{ij} > q_{ij}$ pulls the points "
          r"together (green), $p_{ij} < q_{ij}$ pushes them apart (red)." "\n"
          f"Shown: the star after {TOY_MID} moves, its four strongest pulls "
          "and pushes, and their sum.")


@figure("eq_sne_gradient")
def eq_sne_gradient(fig):
    ax = canvas(fig)
    ax.text(0.40, 3.20, r"$\min_{y_1, \dots, y_N}\ \mathrm{KL}(P \,\|\, Q)"
            r" = \sum_{i, j} p_{ij} \log \dfrac{p_{ij}}{q_{ij}}$", fontsize=14,
            va="center")
    ax.text(0.40, 2.30, r"$\dfrac{\partial \mathrm{KL}(P \,\|\, Q)}{\partial y_i} = 4 \sum_j "
            r"(p_{ij} - q_{ij})(y_i - y_j)$", fontsize=14, va="center",
            color=GREEN)
    ax.text(0.40, 1.65, "symmetric SNE: a spring between each pair", color=MUTED,
            fontsize=11, va="center")
    column(ax, 0.40, 1.20, 5.0, "", [
        "non-convex: no guarantee, several restarts, added noise",
        r"one move: $y_i \leftarrow y_i - \eta\, \partial \mathrm{KL}(P \,\|\, Q) / \partial y_i$, for every $i$",
    ], RED, item_size=11, leading=0.33)
    # springs
    yi = np.array([7.10, 2.30])
    a_ = np.array([6.10, 2.95])
    r_ = np.array([8.25, 1.70])
    ax.plot(*yi, "o", color=LOW, ms=11)
    ax.text(*(yi + [0.0, -0.32]), "$y_i$", ha="center", fontsize=12)
    for pt, c in ((a_, GREEN), (r_, RED)):
        ax.plot(*pt, "o", color=LOW, ms=9, alpha=0.7)
        n = 9
        t = np.linspace(0, 1, 80)
        line = yi[None] + t[:, None] * (pt - yi)[None]
        perp = np.array([-(pt - yi)[1], (pt - yi)[0]])
        perp /= np.linalg.norm(perp)
        wig = 0.07 * np.sin(2 * np.pi * n * t) * (t > 0.12) * (t < 0.88)
        ax.plot(*(line + wig[:, None] * perp).T, color=c, lw=1.4)
    ax.text(6.00, 3.30, r"$p > q$: pulled together", color=GREEN, fontsize=11,
            ha="center")
    ax.text(8.20, 1.30, r"$p < q$: pushed apart", color=RED, fontsize=11,
            ha="center")


@figure("sne_iterations")
def sne_iterations(fig):
    X, g, i = _toy()
    h = _toy_run()
    for r, t in enumerate(TOY_SNAPS):
        a = fig.add_axes([0.10, 0.83 - r * 0.145, 0.47, 0.11])
        _strip(a, h[t][0], g, s=16)
        fig.text(0.085, 0.885 - r * 0.145, f"t = {t}", ha="right",
                 va="center", color=INK, fontsize=10.5)
        w = np.ptp(h[t][0])
        fig.text(0.585, 0.885 - r * 0.145, f"width {w:.2g}", ha="left",
                 va="center", color=MUTED, fontsize=9.5)
    b = fig.add_axes([0.73, 0.22, 0.25, 0.62])
    ts = np.arange(TOY_ITERS + 1)
    b.plot(ts, [h[t][2] for t in ts], color=GREEN)
    for t in TOY_SNAPS:
        b.plot(t, h[t][2], "o", color=GREEN, ms=4)
    b.set_xlabel("move $t$")
    b.set_ylabel(r"$\mathrm{KL}(P \,\|\, Q)$")
    b.set_title("the loss", fontsize=12, color=INK, pad=6)
    despine(b, keep=("left", "bottom"))
    fig.text(0.34, 0.03, "each row is rescaled to its own width: the map "
             "grows, then the groups separate", ha="center", color=MUTED,
             fontsize=10.5)


@figure("pq_matrices")
def pq_matrices(fig):
    X, g, _, _, Pc, _ = _toy_p()
    P = (Pc + Pc.T) / (2 * len(X))
    h = _toy_run()
    mats = [(P, "P: the data", HIGH),
            (h[0][1], f"Q at t = 0,  KL = {h[0][2]:.2f}", LOW),
            (h[TOY_MID][1], f"Q at t = {TOY_MID},  KL = {h[TOY_MID][2]:.2f}",
             LOW),
            (h[TOY_ITERS][1], f"Q at t = {TOY_ITERS},  KL = "
             f"{h[TOY_ITERS][2]:.2f}", GREEN)]
    vmax = np.percentile(P[P > 1e-9], 95)
    for k, (M, title, c) in enumerate(mats):
        a = fig.add_axes([0.025 + k * 0.245, 0.17, 0.21, 0.64])
        _heat(a, M, g, title, c, vmax=vmax)
    _foot(fig, "At the start every pair is equally likely; the moves bring "
          "Q's blocks in line with P's.")


# ==========================================================================
# 7. t-SNE
# ==========================================================================
@figure("student_t")
def student_t(fig):
    d = np.linspace(0, 5, 400)
    a = fig.add_axes([0.20, 0.34, 0.62, 0.58])
    g = np.exp(-d ** 2)
    t = 1 / (1 + d ** 2)
    a.plot(d, g, color=HIGH, label=r"Gaussian $e^{-d^2}$")
    a.plot(d, t, color=TSNE_C, label=r"Student-t $(1 + d^2)^{-1}$")
    lvl = 0.1
    dg, dt = np.sqrt(-np.log(lvl)), np.sqrt(1 / lvl - 1)
    a.axhline(lvl, color=MUTED, lw=1, ls="--")
    a.plot([dg, dg], [0, lvl], color=HIGH, lw=1, ls=":")
    a.plot([dt, dt], [0, lvl], color=TSNE_C, lw=1, ls=":")
    a.annotate("", xy=(dt, lvl), xytext=(dg, lvl),
               arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.8))
    a.text(3.15, 0.36, "same similarity,\nfarther away", ha="left",
           color=RED, fontsize=10.5)
    a.set_xlabel("distance in the map")
    a.set_ylabel("similarity")
    a.legend(loc="upper right")
    despine(a, keep=("left", "bottom"))
    _foot(fig, "With a heavy-tailed q, the same similarity sits farther "
          "away: close neighbours are drawn a little closer,\nnon-neighbours "
          "are pushed away. This makes room in the map for more points.")


@figure("eq_tsne")
def eq_tsne(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"$p_{ij} = \dfrac{p_{j|i} + p_{i|j}}{2N}$, $\quad p_{j|i}$ Gaussian "
         r"with perplexity", "in the data: unchanged", HIGH),
        (r"$q_{ij} = \dfrac{(1 + \| y_i - y_j \|^2)^{-1}}{\sum_{k \neq l}"
         r"(1 + \| y_k - y_l \|^2)^{-1}}$",
         r"in the map: Student's t with one degree of freedom", TSNE_C),
        (r"$\dfrac{\partial C}{\partial y_i} = 4 \sum_j (p_{ij} - q_{ij})"
         r"(y_i - y_j)(1 + \| y_i - y_j \|^2)^{-1}$",
         r"the same springs, weakened at long range"),
    ], top=3.25, gap=1.08, x=0.40, eq_size=13.5, why_off=0.48)
    ax.text(6.55, 1.10, "large p: map distance < data distance\n"
            "small p: map distance > data distance", color=MUTED,
            fontsize=10.5, va="center", ha="left")


@figure("tsne_algorithm")
def tsne_algorithm(fig):
    ax = canvas(fig)
    ax.text(0.40, 3.42, r"Input: data $X$, perplexity, $T$ iterations, rate "
            r"$\eta$, momentum $\alpha(t)$", fontsize=11, color=MUTED,
            va="center")
    _algo(ax, 0.40, 3.00, [
        r"$p_{j|i}$ with the target perplexity, then $p_{ij}$",
        r"draw $Y^{(0)} \sim \mathcal{N}(0, 10^{-4} I)$",
        r"for $t = 1, \dots, T$:",
        r"   compute the $q_{ij}$ and the gradient $\partial C / \partial Y$",
        r"   $Y^{(t)} = Y^{(t-1)} - \eta\, \partial C / \partial Y + "
        r"\alpha(t) (Y^{(t-1)} - Y^{(t-2)})$",
    ], size=12, leading=0.40)
    ax.plot([0.40, 8.60], [1.15, 1.15], color=GRID, lw=1)
    rows = [("early exaggeration", r"$p_{ij} \times 12$ at the start"),
            ("adaptive rates", "one gain per coordinate"),
            ("accelerated versions", r"Barnes–Hut, FFT: $O(N \log N)$ "
             r"instead of $O(N^2)$")]
    for i, (a_, b_) in enumerate(rows):
        y = 0.88 - i * 0.32
        ax.text(0.40, y, a_, color=TSNE_C, fontsize=11.5, weight="bold",
                va="center")
        ax.text(2.80, y, b_, color=INK, fontsize=11, va="center")


@figure("perplexity_effect")
def perplexity_effect(fig):
    X, y = _blobs_hd()
    perps = (2, 5, 30, 100)
    for k, pp in enumerate(perps):
        Y = _sk_tsne("blobs", pp)
        a = fig.add_axes([0.02 + k * 0.245, 0.17, 0.225, 0.64])
        a.scatter(*Y.T, c=[COMP[j] for j in y], s=5, edgecolors="none")
        a.set_aspect("equal", adjustable="datalim")
        _bare(a)
        a.set_title(f"perplexity {pp}", fontsize=12.5, pad=6, color=INK)
    fig.text(0.5, 0.92, "Three clusters in 10D: one wide, one tight, one (tight) far away",
             ha="center", color=INK, fontsize=11.5)


@figure("tsne_runs")
def tsne_runs(fig):
    X, y = _blobs_hd()
    seeds = (0, 1, 2, 3)
    for k, sd in enumerate(seeds):
        Y, kl = _sk_tsne_fit("blobs", 30, sd)
        a = fig.add_axes([0.02 + k * 0.245, 0.31, 0.225, 0.54])
        a.scatter(*Y.T, c=[COMP[j] for j in y], s=5, edgecolors="none")
        a.set_aspect("equal", adjustable="datalim")
        _bare(a)
        a.set_title(f"seed {sd}", fontsize=12.5, pad=6, color=INK)
        a.text(0.5, -0.06, f"KL = {kl:.3f}", transform=a.transAxes,
               ha="center", va="top", color=MUTED, fontsize=10.5)
    fig.text(0.5, 0.93, "(same three clusters in 10D, perplexity 30)",
             ha="center", color=INK, fontsize=11.5)
    _foot(fig, "Places and gaps change with new seeds.")


@figure("pca_vs_tsne")
def pca_vs_tsne(fig):
    ax = canvas(fig)
    ax.plot([4.50, 4.50], [0.25, 3.15], color=GRID, lw=1.2)
    for x, title, c, items in (
        (0.35, "PCA", PCA_C, [
            ("·", "finds the global structure"),
            ("·", "a linear subspace"),
            ("−", "far-away points can become\nnearest neighbours"),
            ("−", "misses curved structure"),
            ("+", "fast"),
            ("+", "the axes can be read back\nin terms of the features"),
            ("+", "projects new points"),
        ]),
        (4.80, "t-SNE", TSNE_C, [
            ("·", "keeps the local structure"),
            ("·", "for visualization"),
            ("+", "reveals hidden structure"),
            ("−", r"slow: $O(N^2)$ (or $O(N \log N)$)"),
            ("−", "the axes mean nothing"),
            ("−", "no map for a new point: it\nlearns the points, not a function"),
            ("+", "variants exist (UMAP, …)"),
        ]),
    ):
        ax.text(x, 3.40, title, color=c, fontsize=14, weight="bold",
                va="center")
        yy = 2.98
        for sym, txt in items:
            sc = {"+": GREEN, "−": RED, "·": MUTED}[sym]
            ax.text(x, yy, sym, color=sc, fontsize=13, weight="bold",
                    va="top")
            ax.text(x + 0.28, yy, txt, color=INK, fontsize=11, va="top")
            yy -= 0.38 + 0.19 * txt.count("\n")


@figure("tsne_pitfalls")
def tsne_pitfalls(fig):
    X, y = _blobs_hd()
    Z, _, _ = _pca(X, 2)
    Y = _sk_tsne("blobs", 30)
    for k, (P2, title, c) in enumerate(((Z, "PCA", PCA_C),
                                        (Y, "t-SNE", TSNE_C))):
        a = fig.add_axes([0.08 + k * 0.46, 0.21, 0.38, 0.66])
        a.scatter(*P2.T, c=[COMP[j] for j in y], s=5, edgecolors="none")
        a.set_aspect("equal", adjustable="datalim")
        _bare(a)
        a.set_title(title, color=c, fontsize=13, pad=6, weight="bold")
    fig.text(0.5, 0.93, "(same three clusters in 10D)",
             ha="center", color=INK, fontsize=11.5)
    _foot(fig, "In t-SNE map, cluster sizes are meanless.")


@figure("pca_vs_tsne_roll")
def pca_vs_tsne_roll(fig):
    X, t = _swiss_roll()
    Z, _, _ = _pca(X, 2)
    Y = _sk_tsne("roll", 30)
    for k, (P2, title, c) in enumerate(((Z, "PCA", PCA_C),
                                        (Y, "t-SNE", TSNE_C))):
        a = fig.add_axes([0.08 + k * 0.46, 0.15, 0.38, 0.70])
        _roll_scatter(a, P2, t)
        a.set_aspect("equal", adjustable="datalim")
        a.set_title(title, color=c, fontsize=13, pad=6, weight="bold")
    fig.text(0.5, 0.05, "Swiss roll", ha="center", color=INK, fontsize=16)


@figure("pca_vs_tsne_mnist")
def pca_vs_tsne_mnist(fig):
    Z50, y = _mnist_pca50()
    Zp = Z50[:, :2]
    Y = _mnist_tsne()
    for k, (P2, title, c) in enumerate(((Zp, "PCA", PCA_C),
                                        (Y, "t-SNE", TSNE_C))):
        a = fig.add_axes([0.06 + k * 0.48, 0.17, 0.40, 0.72])
        _digit_scatter(a, P2, y, s=2, alpha=0.6)
        a.set_aspect("equal", adjustable="datalim")
        a.set_title(title, color=c, fontsize=13, pad=6, weight="bold")
    _foot(fig, "5000 MNIST images (28 × 28 = 784 pixels).")


@figure("sne_vs_tsne")
def sne_vs_tsne(fig):
    X, y = _digits_subset()
    for k, (kind, title, c) in enumerate((("sne", "SNE", HIGH),
                                          ("t", "t-SNE", TSNE_C))):
        Y = _embed(X, kind=kind)
        a = fig.add_axes([0.05 + k * 0.50, 0.08, 0.40, 0.78])
        _digit_scatter(a, Y, y)
        a.set_aspect("equal", adjustable="datalim")
        a.set_title(title, color=c, fontsize=13, pad=6, weight="bold")
    fig.text(0.5, 0.03, "(same 600 digits)", ha="center", color=MUTED, fontsize=13)


# ==========================================================================
def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course09/img")
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
