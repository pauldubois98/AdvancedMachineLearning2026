#!/usr/bin/env python3
"""Every figure of Course06 (mixture models and the EM algorithm).

One function per figure, registered under the stem the slide deck asks for.
All figures share one canvas (9 x 3.7075 in), which is exactly the content
area pandoc leaves under a slide title, so a figure never has to be resized.

    python3 scripts/make_figures_c06.py Course06/img [stem ...]
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
# one colour per mixture component, used by every slide that draws one:
# component 1 is blue, component 2 gold, component 3 green, and so on
COMP = [BLUE, GOLD, GREEN, PURPLE, RED]
MIX = INK                 # the mixture density itself is always drawn in ink
# a responsibility matrix is always drawn with the same ramp: white is zero
G_CMAP = LinearSegmentedColormap.from_list("gm", ["#ffffff", "#cfe0f1", BLUE])
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



def ellipse(ax, mu, S, color, nsig=(1.0, 2.0), lw=1.8, ls="-", alpha=1.0,
            zorder=4):
    """The level sets of a 2-D Gaussian, at one and two standard deviations."""
    vals, vecs = np.linalg.eigh(S)
    order = np.argsort(-vals)
    vals, vecs = vals[order], vecs[:, order]
    angle = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
    for k in nsig:
        ax.add_patch(
            Ellipse(xy=mu, width=2 * k * np.sqrt(max(vals[0], 1e-12)),
                    height=2 * k * np.sqrt(max(vals[1], 1e-12)), angle=angle,
                    facecolor="none", edgecolor=color, lw=lw, ls=ls,
                    alpha=alpha, zorder=zorder))


# ==========================================================================
# the algorithms, written out once: every "measured" slide runs these
# ==========================================================================
EPS = 1e-12
CACHE = Path(__file__).resolve().parent.parent / ".cache" / "datasets" / "sklearn"


def _norm_pdf(x, mu, sd):
    z = (np.asarray(x) - mu) / sd
    return np.exp(-0.5 * z ** 2) / (sd * np.sqrt(2 * np.pi))


def _mix_pdf(x, p, mu, sd):
    """The mixture density, evaluated on a grid."""
    x = np.asarray(x, float)
    return (np.asarray(p) * _norm_pdf(x[..., None], np.asarray(mu),
                                      np.asarray(sd))).sum(-1)


def _resp1d(x, p, mu, sd):
    """gamma[i, k] = P(Z_i = k | x_i, theta): one row per point, one column
    per component, each row summing to one."""
    num = np.asarray(p) * _norm_pdf(np.asarray(x)[:, None], np.asarray(mu),
                                    np.asarray(sd))
    return num / np.maximum(num.sum(1, keepdims=True), EPS)


def _loglik1d(x, p, mu, sd):
    return float(np.log(np.maximum(_mix_pdf(x, p, mu, sd), EPS)).sum())


def _em1d(x, K=2, iters=60, seed=0, p=None, mu=None, sd=None, trace=False,
          floor=1e-2):
    """EM for a one-dimensional Gaussian mixture.  With trace=True it returns
    the whole history, so a slide can draw any iterate it likes."""
    x = np.asarray(x, float)
    if mu is None:
        rng = np.random.default_rng(seed)
        p = np.full(K, 1.0 / K)
        mu = np.sort(rng.choice(x, K, replace=False)).astype(float)
        sd = np.full(K, float(x.std()))
    p, mu, sd = (np.array(v, float) for v in (p, mu, sd))
    hist = [(p.copy(), mu.copy(), sd.copy(), _loglik1d(x, p, mu, sd))]
    for _ in range(iters):
        g = _resp1d(x, p, mu, sd)                       # E-step
        nk = g.sum(0)                                   # M-step
        p = nk / len(x)
        mu = (g * x[:, None]).sum(0) / np.maximum(nk, EPS)
        var = (g * (x[:, None] - mu) ** 2).sum(0) / np.maximum(nk, EPS)
        sd = np.maximum(np.sqrt(var), floor)
        hist.append((p.copy(), mu.copy(), sd.copy(), _loglik1d(x, p, mu, sd)))
    return (p, mu, sd, hist) if trace else (p, mu, sd)


def _mvn_pdf(X, mu, S):
    d = X.shape[1]
    L = np.linalg.cholesky(S)
    sol = np.linalg.solve(L, (X - mu).T)
    logdet = 2.0 * np.log(np.diag(L)).sum()
    return np.exp(-0.5 * ((sol ** 2).sum(0) + logdet + d * np.log(2 * np.pi)))


def _resp2d(X, p, mus, Ss):
    num = np.stack([pk * _mvn_pdf(X, mk, Sk)
                    for pk, mk, Sk in zip(p, mus, Ss)], 1)
    return num / np.maximum(num.sum(1, keepdims=True), EPS)


def _loglik2d(X, p, mus, Ss):
    tot = sum(pk * _mvn_pdf(X, mk, Sk) for pk, mk, Sk in zip(p, mus, Ss))
    return float(np.log(np.maximum(tot, EPS)).sum())


def _em2d(X, K=2, iters=40, seed=0, start=None, trace=False, reg=1e-4,
          cov="full"):
    """EM for a Gaussian mixture in the plane, with the covariance families
    the deck compares: full, diagonal, spherical, or tied across components."""
    X = np.asarray(X, float)
    n, d = X.shape
    if start is None:
        rng = np.random.default_rng(seed)
        p = np.full(K, 1.0 / K)
        mus = X[rng.choice(n, K, replace=False)].copy()
        S0 = np.cov(X.T) * 0.6 + reg * np.eye(d)
        Ss = np.array([S0 for _ in range(K)])
    else:
        p, mus, Ss = (np.array(v, float) for v in start)
    hist = [(p.copy(), mus.copy(), Ss.copy(), _loglik2d(X, p, mus, Ss))]
    for _ in range(iters):
        g = _resp2d(X, p, mus, Ss)                      # E-step
        nk = np.maximum(g.sum(0), EPS)                  # M-step
        p = nk / n
        mus = (g.T @ X) / nk[:, None]
        Ss = []
        for k in range(K):
            dX = X - mus[k]
            Sk = (g[:, k, None] * dX).T @ dX / nk[k] + reg * np.eye(d)
            Ss.append(Sk)
        Ss = np.array(Ss)
        if cov == "diag":
            Ss = np.array([np.diag(np.diag(S)) for S in Ss])
        elif cov == "spherical":
            Ss = np.array([np.eye(d) * np.trace(S) / d for S in Ss])
        elif cov == "tied":
            St = np.tensordot(p, Ss, axes=1)
            Ss = np.array([St for _ in range(K)])
        hist.append((p.copy(), mus.copy(), Ss.copy(), _loglik2d(X, p, mus, Ss)))
    return (p, mus, Ss, hist) if trace else (p, mus, Ss)


def _sem1d(x, K=2, iters=60, seed=0, p=None, mu=None, sd=None, trace=False,
           hard=False, floor=1e-2, N=1):
    """Stochastic EM: draw a label for every point instead of weighting by its
    responsibility.  hard=True draws the arg max instead, which is k-means.
    N > 1 is N-SEM: N labels per point, each class weighted by its share of
    the draws, which tends to EM as N grows."""
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    p, mu, sd = (np.array(v, float) for v in (p, mu, sd))
    hist = [(p.copy(), mu.copy(), sd.copy(), None,
             _loglik1d(x, p, mu, sd))]
    for _ in range(iters):
        g = _resp1d(x, p, mu, sd)
        if hard:
            Z = g.argmax(1)[:, None]
        else:
            u = rng.random((len(x), N))
            Z = (np.cumsum(g, 1)[:, None, :] < u[:, :, None]).sum(2)
            Z = Z.clip(0, K - 1)
        z = Z[:, 0]
        for k in range(K):
            w = (Z == k).mean(1)                # share of the draws in class k
            if w.sum() < 2:                     # an empty class: restart it
                w = np.zeros(len(x))
                w[rng.choice(len(x), 2, replace=False)] = 1.0
            p[k] = w.mean()
            mu[k] = (w * x).sum() / w.sum()
            sd[k] = max(np.sqrt((w * (x - mu[k]) ** 2).sum() / w.sum()),
                        floor)
        p = p / p.sum()
        hist.append((p.copy(), mu.copy(), sd.copy(), z.copy(),
                     _loglik1d(x, p, mu, sd)))
    return (p, mu, sd, hist) if trace else (p, mu, sd)


# --------------------------------------------------------------------------
# the data every slide runs on
# --------------------------------------------------------------------------
def _animals():
    """The table of the 2023 lecture: lengths of small animals collected in
    two regions, and how many animals had each length."""
    length = np.array([82, 83, 84, 85, 86, 87, 88, 89,
                       90, 91, 92, 93, 94, 95, 96, 98], float)
    count = np.array([5, 3, 12, 36, 55, 45, 21, 13,
                      15, 34, 59, 48, 16, 12, 6, 1])
    return length, count


def _animal_sample():
    """The same table, as one number per animal."""
    length, count = _animals()
    return np.repeat(length, count)


def _two_blobs(seed=3, n=260):
    """Two elongated, overlapping Gaussian clusters in the plane: the shape
    EM separates and k-means cannot."""
    rng = np.random.default_rng(seed)
    mus = np.array([[-1.05, -0.35], [1.15, 0.55]])
    Ss = [np.array([[0.95, 0.52], [0.52, 0.40]]),
          np.array([[0.70, -0.46], [-0.46, 0.52]])]
    p = (0.55, 0.45)
    z = rng.choice(2, n, p=p)
    X = np.zeros((n, 2))
    for k in range(2):
        m = z == k
        X[m] = rng.multivariate_normal(mus[k], Ss[k], int(m.sum()))
    return X, z


def _three_blobs(seed=5, n=330):
    rng = np.random.default_rng(seed)
    mus = np.array([[-1.5, 0.9], [1.5, 1.0], [0.1, -1.3]])
    Ss = [np.array([[0.55, 0.30], [0.30, 0.30]]),
          np.array([[0.40, -0.26], [-0.26, 0.55]]),
          np.array([[0.90, 0.05], [0.05, 0.22]])]
    z = rng.choice(3, n, p=(0.38, 0.32, 0.30))
    X = np.zeros((n, 2))
    for k in range(3):
        m = z == k
        X[m] = rng.multivariate_normal(mus[k], Ss[k], int(m.sum()))
    return X, z


def _five_blobs(seed=2, n=420):
    """Five clusters, two of them close together: hard enough that a random
    start sometimes merges a pair and splits another."""
    rng = np.random.default_rng(seed)
    mus = np.array([[-2.2, 1.2], [-1.9, -1.0], [0.4, 1.6],
                    [1.9, -0.6], [2.4, 1.4]])
    Ss = [np.array([[0.35, 0.20], [0.20, 0.25]]),
          np.array([[0.50, -0.30], [-0.30, 0.40]]),
          np.array([[0.25, 0.00], [0.00, 0.50]]),
          np.array([[0.60, 0.25], [0.25, 0.30]]),
          np.array([[0.20, 0.00], [0.00, 0.20]])]
    z = rng.choice(5, n, p=(0.30, 0.20, 0.20, 0.20, 0.10))
    X = np.zeros((n, 2))
    for k in range(5):
        m = z == k
        X[m] = rng.multivariate_normal(mus[k], Ss[k], int(m.sum()))
    return X, z


def _iris():
    from sklearn.datasets import load_iris
    d = load_iris()
    return d.data, d.target, list(d.target_names), list(d.feature_names)


# ==========================================================================
# 1. a mixture of populations
# ==========================================================================
@figure("mixture_idea")
def mixture_idea(fig):
    length, count = _animals()
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Lengths of small animals, collected in two regions",
            ha="center", va="center", color=MUTED, fontsize=12.5)

    # the table, exactly as the lecture gives it
    half = len(length) // 2
    for row in range(2):
        sl = slice(row * half, (row + 1) * half)
        y = 3.04 - row * 0.56
        ax.text(1.02, y, "length", ha="right", va="center", color=MUTED,
                fontsize=10)
        ax.text(1.02, y - 0.24, "count", ha="right", va="center", color=MUTED,
                fontsize=10)
        for j, (l, c) in enumerate(zip(length[sl], count[sl])):
            x = 1.32 + j * 0.44
            ax.text(x, y, f"{l:.0f}", ha="center", va="center", color=INK,
                    fontsize=10.5)
            ax.text(x, y - 0.24, f"{c:d}", ha="center", va="center",
                    color=INK, fontsize=10.5)
    ax.plot([0.55, 4.60], [2.08, 2.08], color=LIGHT, lw=1.0)

    bx = fig.add_axes([0.085, 0.17, 0.44, 0.37])
    bx.bar(length, count, width=0.86, color=LIGHT, edgecolor=GRID, lw=0.8)
    bx.set_xlabel("length (mm)")
    bx.set_ylabel("animals")
    despine(bx, keep=("left", "bottom"))
    bx.annotate("", xy=(86.3, 62), xytext=(86.3, 74),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.8))
    bx.annotate("", xy=(92.3, 66), xytext=(92.3, 78),
                arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=1.8))
    bx.set_ylim(0, 88)
    bx.set_yticks([0, 40, 80])

    column(ax, 5.35, 2.06, 3.2, "In the same sample:", [
        "Two peaks",
        "No group label",
    ], INK, leading=0.34, item_size=11.5)
    ax.text(5.35, 0.22, "Model the sample as a mixture of two populations",
            color=MUTED, fontsize=11.5, ha="left", va="center")


@figure("one_gaussian_fails")
def one_gaussian_fails(fig):
    x = _animal_sample()
    grid = np.linspace(79, 101, 500)
    p, mu, sd = _em1d(x, 2, 200, seed=1)
    ll1 = float(np.log(_norm_pdf(x, x.mean(), x.std())).sum())
    ll2 = _loglik1d(x, p, mu, sd)

    axes = panels(fig, 2, titles=["One Gaussian", "Two Gaussians mixed"],
                  colors=[RED, GREEN],
                  gridspec_kw=dict(left=0.07, right=0.98, top=0.78,
                                   bottom=0.27, wspace=0.18))
    for ax in axes:
        ax.hist(x, bins=np.arange(81.5, 99.5, 1.0), density=True,
                color=LIGHT, edgecolor=GRID, lw=0.8)
        ax.set_xlabel("length (mm)")
        despine(ax, keep=("left", "bottom"))
        ax.set_ylim(0, 0.22)
    axes[0].plot(grid, _norm_pdf(grid, x.mean(), x.std()), color=RED, lw=2.6)
    axes[0].set_ylabel("density")
    for k in range(2):
        axes[1].plot(grid, p[k] * _norm_pdf(grid, mu[k], sd[k]),
                     color=COMP[k], lw=1.8, ls="--")
    axes[1].plot(grid, _mix_pdf(grid, p, mu, sd), color=GREEN, lw=2.6)

    caption_row(fig, axes, [
        f"one mean, one width — log-likelihood {ll1:,.0f}",
        f"two of each, plus a weight — log-likelihood {ll2:,.0f}"], y=0.1)
    fig.text(0.5, 0.955, "No bell can fit the sample.",
             ha="center", va="center", color=MUTED, fontsize=12.5)


@figure("mixture_apps")
def mixture_apps(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "One sample with several populations",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    cards = [
        (0.30, BLUE, "Populations", "multiple group origins,\n"
         "male\nand female",
         "Task: predict the label"),
        (2.52, GOLD, "Images", "sky, road\nand building\nin one photograph",
         "Task: segmentation"),
        (4.74, GREEN, "Signals", "speakers, phonemes,\ninstruments",
         "Task: speech GMM"),
        (6.96, PURPLE, "Density", "Odd shapes:\nskewed, heavy, multi-modal",
         ""),
    ]
    for x, color, head, body, out in cards:
        box(ax, x, 0.98, 1.74, 1.96, color, "", fill="white")
        ax.text(x + 0.87, 2.70, head, ha="center", va="center", color=color,
                fontsize=13, weight="bold")
        ax.text(x + 0.87, 2.08, body, ha="center", va="center", color=INK,
                fontsize=10, linespacing=1.5)
        ax.text(x + 0.87, 1.29, out, ha="center", va="center", color=MUTED,
                fontsize=9.5, linespacing=1.5)
    note(ax, "The group label exists, but is never recorded (it is \"latent\")", y=0.52)


@figure("eq_mixture")
def eq_mixture(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "A weighted average of densities",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 2.92, r"$f(x) \;=\; \sum_k p_k \, f_k(x)"
                         r"\;=\; p_1 f_1(x) + \cdots + p_K f_K(x)$",
            ha="center", va="center", color=INK, fontsize=20)
    ax.annotate("", xy=(3.14, 2.66), xytext=(2.70, 2.30),
                arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=1.6))
    ax.text(2.64, 2.24, "weights", ha="right", va="center", color=PURPLE,
            fontsize=11.5)
    ax.annotate("", xy=(3.62, 2.66), xytext=(4.10, 2.30),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6))
    ax.text(4.16, 2.24, r"the density of class $k$", ha="left", va="center",
            color=BLUE, fontsize=11.5)
    column(ax, 0.55, 1.78, 3.9, "What the pieces are", [
        r"$K$ classes, $p_k$ the chance of landing in class $k$",
        r"$p_k \geq 0$ and $p_1 + \cdots + p_K = 1$",
        r"$f_k$ the density inside class $k$",
    ], INK, leading=0.32, item_size=11.5)
    note(ax, r"Gaussian mixture: every $f_k$ is a normal density", y=0.18,
         size=11.5)


@figure("latent_idea")
def latent_idea(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Where a point comes from: first the class, then "
                         "the value", ha="center", va="center", color=MUTED,
            fontsize=12.5)
    box(ax, 0.45, 1.80, 1.75, 0.85, PURPLE, r"draw  $Z$", size=14)
    ax.text(1.325, 1.60, r"$P(Z = k) = p_k$", ha="center", va="center",
            color=PURPLE, fontsize=11)
    box(ax, 3.30, 2.45, 2.05, 0.72, BLUE, r"$X \sim f_1$", size=14)
    box(ax, 3.30, 1.25, 2.05, 0.72, GOLD, r"$X \sim f_2$", size=14)
    arrow(ax, (2.35, 2.30), (3.20, 2.86), color=PURPLE)
    arrow(ax, (2.35, 2.15), (3.20, 1.66), color=PURPLE)
    ax.text(2.72, 2.78, r"$Z = 1$", color=PURPLE, fontsize=10.5,
            ha="center", va="bottom")
    ax.text(2.72, 1.52, r"$Z = 2$", color=PURPLE, fontsize=10.5,
            ha="center", va="top")
    box(ax, 6.40, 1.80, 1.55, 0.85, INK, r"keep  $x$", size=14)
    arrow(ax, (5.50, 2.81), (6.30, 2.38), color=MUTED)
    arrow(ax, (5.50, 1.61), (6.30, 2.08), color=MUTED)
    ax.text(7.175, 1.60, "throw $z$ away", ha="center", va="center",
            color=RED, fontsize=11)

    ax.text(0.45, 1.08, "Complete data", color=GREEN, fontsize=12.5,
            weight="bold", va="center")
    ax.text(2.10, 1.08, r"$T = (X, Z)$ — what the generator produced",
            color=INK, fontsize=11.5, va="center")
    ax.text(0.45, 0.68, "Observed data", color=BLUE, fontsize=12.5,
            weight="bold", va="center")
    ax.text(2.10, 0.68, r"$X$ alone — what the experiment recorded",
            color=INK, fontsize=11.5, va="center")
    note(ax, r"$Z$ is latent: it exists in the model, it is missing from the data.", y=0.22, size=11.5)


@figure("generative_sim")
def generative_sim(fig):
    rng = np.random.default_rng(4)
    p, mu, sd = np.array([0.45, 0.55]), np.array([86.0, 92.2]), \
        np.array([1.5, 1.6])
    n = 300
    z = rng.choice(2, n, p=p)
    x = rng.normal(mu[z], sd[z])
    grid = np.linspace(79, 100, 500)

    fig.text(0.5, 0.955, "Coin flip, then a bell",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    ax1 = fig.add_axes([0.065, 0.26, 0.26, 0.52])
    for k in range(2):
        ax1.bar(k, p[k], width=0.55, color=COMP[k], alpha=0.85)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels([r"$Z = 1$", r"$Z = 2$"])
    ax1.set_ylim(0, 0.75)
    ax1.set_ylabel(r"$p_k$")
    ax1.set_title(r"1. draw the class", color=PURPLE, fontsize=12, pad=8)
    despine(ax1, keep=("left", "bottom"))

    ax2 = fig.add_axes([0.395, 0.26, 0.26, 0.52])
    for k in range(2):
        ax2.plot(grid, _norm_pdf(grid, mu[k], sd[k]), color=COMP[k], lw=2.2)
    ax2.set_title("2. draw from correspnding bell", color=BLUE, fontsize=12, pad=8)
    ax2.set_xlabel("length (mm)")
    ax2.set_yticks([])
    despine(ax2, keep=("bottom",))

    ax3 = fig.add_axes([0.725, 0.26, 0.26, 0.52])
    bins = np.arange(79, 100.5, 1.0)
    ax3.hist([x[z == 0], x[z == 1]], bins=bins, stacked=True, density=True,
             color=[COMP[0], COMP[1]], alpha=0.75)
    ax3.plot(grid, _mix_pdf(grid, p, mu, sd), color=INK, lw=2.4)
    ax3.set_title("3. repeat", color=INK, fontsize=12, pad=8)
    ax3.set_xlabel("length (mm)")
    ax3.set_yticks([])
    despine(ax3, keep=("bottom",))

    fig.text(0.5, 0.095, "The colours are what the generator knows; the "
                         "experiment hands the grey histogram (with colours removed).",
             ha="center", va="center", color=MUTED, fontsize=11)


@figure("eq_two_component")
def eq_two_component(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"$Y_1 \sim \mathcal{N}(\mu_1, \sigma_1^2), \qquad "
         r"Y_2 \sim \mathcal{N}(\mu_2, \sigma_2^2), \qquad "
         r"Z \sim \mathcal{B}(1, p)$",
         "two bells and one coin, drawn independently"),
        (r"$X \;=\; Z\, Y_1 + (1 - Z)\, Y_2$",
         r"the coin picks which bell is read: $P(Z = 1) = p$"),
        (r"$f_X(x) \;=\; \sum_k P(Z = k)\, f(x \mid Z = k)"
         r"\;=\; p\, \varphi_{\theta_1}(x) + (1 - p)\, \varphi_{\theta_2}(x)$",
         r"marginalising: sum the joint $P(z, x) = P(z) f(x \mid z)$ over $z$"),
        (r"$\ell(\theta; x) \;=\; \sum_i "
         r"\log\!\left( p\, \varphi_{\theta_1}(x_i) "
         r"+ (1 - p)\, \varphi_{\theta_2}(x_i) \right)$",
         r"the log-likelihood of $n$ i.i.d. observations", BLUE),
    ], top=3.52, gap=0.67, x=0.45, eq_size=13, why_off=0.28)
    box(ax, 0.80, 0.1, 7.40, 0.40, GOLD, "", fill="#fdf8ef")
    ax.text(W / 2, 0.3, r"Five unknowns:  $\theta = (p, \mu_1, \sigma_1, "
                         r"\mu_2, \sigma_2)$.  How do we estimate them?",
            ha="center", va="center", color=GOLD, fontsize=13)


@figure("density_vs_clustering")
def density_vs_clustering(fig):
    x = _animal_sample()
    grid = np.linspace(79, 101, 500)
    p, mu, sd = _em1d(x, 2, 200, seed=1)
    g = _resp1d(grid, p, mu, sd)

    ax1 = fig.add_axes([0.075, 0.27, 0.38, 0.52])
    ax1.hist(x, bins=np.arange(81.5, 99.5, 1.0), density=True, color=LIGHT,
             edgecolor=GRID, lw=0.8)
    ax1.plot(grid, _mix_pdf(grid, p, mu, sd), color=INK, lw=2.6)
    ax1.set_title("a density", color=INK, fontsize=12.5, pad=8)
    ax1.set_xlabel("length (mm)")
    ax1.set_ylabel("density")
    despine(ax1, keep=("left", "bottom"))

    ax2 = fig.add_axes([0.575, 0.27, 0.38, 0.52])
    for k in range(2):
        ax2.plot(grid, g[:, k], color=COMP[k], lw=2.6)
    ax2.axhline(0.5, color=GRID, lw=1.0, ls=":")
    ax2.set_title("a label", color=PURPLE, fontsize=12.5, pad=8)
    ax2.set_xlabel("length (mm)")
    ax2.set_ylabel(r"$P(Z = k \mid x)$")
    ax2.set_ylim(-0.04, 1.04)
    despine(ax2, keep=("left", "bottom"))

    caption_row(fig, [ax1, ax2], [
        "density estimation",
        "soft clustering (probabilities)"], y=0.1)


@figure("key_questions")
def key_questions(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.56, "Fitting a mixture to a sample", ha="center",
            va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 3.08, r"$f(x) = \sum_k p_k f_k(x)$", ha="center",
            va="center", color=INK, fontsize=18)
    cards = [
        (0.35, BLUE, "1.  What family are\nthe components?",
         "Gaussian, Poisson, Student,\nexponential, …",
         "→  Assume Gaussian"),
        (3.20, PURPLE, "2.  How many are\nthere?",
         r"$K$ known, guessed,"
         "\nor estimated from the data",
         "→  Assume known"),
        (6.05, GREEN, "3.  How do we find\n" r"$\theta = (p_k, \mu_k, "
         r"\sigma_k)_k$?",
         "likelihood has no\nclosed-form maximiser",
         "→  Expectation Maximization"),
    ]
    for x, color, head, body, out in cards:
        box(ax, x+0.1, 0.8, 2.5, 1.75, color, "", fill="white")
        ax.text(x + 1.30, 2.22, head, ha="center", va="center", color=color,
                fontsize=12.5, weight="bold", linespacing=1.4)
        ax.text(x + 1.30, 1.60, body, ha="center", va="center", color=INK,
                fontsize=10.5, linespacing=1.5)
        ax.text(x + 1.30, 1.02, out, ha="center", va="center", color=color,
                fontsize=11.5)


# ==========================================================================
# 2. what a Gaussian mixture can model
# ==========================================================================
def _mw_densities():
    """The six mixtures the 2023 lecture shows, as (title, p, mu, sd)."""
    k = np.arange(8)
    b = (np.full(8, 1 / 8), 3 * ((2 / 3) ** k - 1), (2 / 3) ** k)
    j = np.arange(-2, 3)
    f = (np.r_[0.5, 2.0 ** (1 - j) / 31],
         np.r_[0.0, j + 0.5],
         np.r_[1.0, 2.0 ** (-j) / 10])
    return [
        ("asymmetric unimodal",
         np.array([1 / 5, 1 / 5, 3 / 5]), np.array([0, 1 / 2, 13 / 15]),
         np.array([1.0, 2 / 3, 5 / 9])),
        ("strongly asymmetric unimodal", *b),
        ("bimodal", np.array([0.5, 0.5]), np.array([-1.0, 1.0]),
         np.array([2 / 3, 2 / 3])),
        ("asymmetric bimodal", np.array([3 / 4, 1 / 4]),
         np.array([0.0, 1.5]), np.array([1.0, 1 / 3])),
        ("tri-modal", np.array([9 / 20, 9 / 20, 1 / 10]),
         np.array([-6 / 5, 6 / 5, 0.0]), np.array([3 / 5, 3 / 5, 1 / 4])),
        ("more complex", *f),
    ]


@figure("eq_gmm")
def eq_gmm(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Every component is a normal density", ha="center",
            va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 2.84, r"$f(x) \;=\; \sum_k p_k \,"
                         r"\frac{1}{\sqrt{2 \pi \sigma_k^2}}\,"
                         r"\exp\!\left( -\frac{(x - \mu_k)^2}"
                         r"{2 \sigma_k^2} \right)$",
            ha="center", va="center", color=INK, fontsize=21)
    column(ax, 0.55, 1.90, 3.9, "The constraints", [
        r"$p_k \geq 0$ and $p_1 + \cdots + p_K = 1$",
        r"$\mu_k \in \mathbb{R}$, no constraint at all",
        r"$\sigma_k > 0$ (zero is not allowed)",
    ], PURPLE, leading=0.32, item_size=11.5)
    column(ax, 4.90, 1.90, 3.9, "The unknowns", [
        r"$\theta = (p_k, \mu_k, \sigma_k)_{k = 1, \ldots, K}$",
        r"$3K - 1$ free numbers (since $\sum_k p_k = 1$)",
        r"$K$ if umknown",
    ], GOLD, leading=0.32, item_size=11.5)
    ax.plot([4.65, 4.65], [0.60, 1.96], color=GRID, lw=1.2)
    note(ax, "With enough components, Gaussian mixture can reach almost any density",
         y=0.24, size=11.5)


@figure("gmm_zoo")
def gmm_zoo(fig):
    dens = _mw_densities()
    fig.text(0.5, 0.955, "Six mixtures of normals",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    letters = "abcdef"
    for i, (title, p, mu, sd) in enumerate(dens):
        row, col = divmod(i, 3)
        a = fig.add_axes([0.065 + col * 0.325, 0.56 - row * 0.40, 0.255, 0.26])
        lo = float((mu - 3.5 * sd).min())
        hi = float((mu + 3.5 * sd).max())
        g = np.linspace(lo, hi, 700)
        a.fill_between(g, _mix_pdf(g, p, mu, sd), color=LIGHT, zorder=1)
        a.plot(g, _mix_pdf(g, p, mu, sd), color=INK, lw=2.0, zorder=3)
        a.set_title(f"({letters[i]})  {title}", color=COMP[i % 3],
                    fontsize=10.5, pad=5)
        a.set_xticks([])
        a.set_yticks([])
        despine(a)
    fig.text(0.5, 0.055, "Asymmetric, heavy-shouldered, multi-modal, spiky...",
             ha="center", va="center", color=MUTED, fontsize=11)


@figure("gmm_flexible")
def gmm_flexible(fig):
    rng = np.random.default_rng(11)
    n = 1500
    # a skewed, heavy-tailed target no single Gaussian can reach
    x = np.r_[rng.gamma(2.0, 0.9, int(0.7 * n)),
              rng.normal(7.5, 0.55, n - int(0.7 * n))]
    grid = np.linspace(-0.5, 10.5, 600)
    ks = (1, 2, 4, 8)
    axes = panels(fig, 4, gridspec_kw=dict(left=0.055, right=0.985, top=0.76,
                                           bottom=0.25, wspace=0.18))
    for ax, K in zip(axes, ks):
        p, mu, sd = _em1d(x, K, 300, seed=2)
        ax.hist(x, bins=60, density=True, color=LIGHT, edgecolor="none")
        for k in range(K):
            ax.plot(grid, p[k] * _norm_pdf(grid, mu[k], sd[k]),
                    color=MUTED, lw=1.0, ls="--", zorder=2)
        ax.plot(grid, _mix_pdf(grid, p, mu, sd), color=BLUE, lw=2.4, zorder=3)
        ax.set_title(f"$K = {K}$", color=BLUE, fontsize=12.5, pad=8)
        ax.set_ylim(0, 0.42)
        ax.set_yticks([])
        ax.set_xticks([0, 5, 10])
        despine(ax, keep=("bottom",))
    caption_row(fig, axes, [f"log-lik {_loglik1d(x, *_em1d(x, K, 300, seed=2)):,.0f}"
                            for K in ks], y=0.175)
    fig.text(0.5, 0.955, "More components always give a better fit.", ha="center", va="center", color=MUTED,
             fontsize=12.5)
    fig.text(0.5, 0.055, "Choosing $K$ needs another criterion than likelihood.",
             ha="center", va="center", color=MUTED, fontsize=11)


@figure("eq_gmm_multivariate")
def eq_gmm_multivariate(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"In $d$ dimensions: the same formula, with a "
                         r"covariance matrix", ha="center", va="center",
            color=MUTED, fontsize=12.5)
    ax.text(W / 2, 2.80, r"$f(x) = \sum_k p_k \, \frac{1}"
                         r"{(2\pi)^{d/2} |\Sigma_k|^{1/2}} \,"
                         r"\exp\!\left( -\frac{1}{2}"
                         r"(x - \mu_k)^{\top} \Sigma_k^{-1}"
                         r"(x - \mu_k) \right)$",
            ha="center", va="center", color=INK, fontsize=19)
    column(ax, 0.55, 1.95, 3.9, "Multi-dimension:", [
        r"$\mu_k \in \mathbb{R}^d$ are centres",
        r"$\Sigma_k$ is $d \times d$, symmetric, positive definite",
        "Level sets are ellipsoids",
    ], BLUE, leading=0.32, item_size=11.5)
    column(ax, 4.90, 1.95, 3.9, "Unchanged:", [
        "Latent class $Z$",
        "Weights $p_k$ (summing to $1$)",
    ], GREEN, leading=0.32, item_size=11.5)
    ax.plot([4.65, 4.65], [0.62, 2.01], color=GRID, lw=1.2)
    note(ax, r"$\Sigma_k$ carries $d(d+1)/2$ numbers, so the parameter count "
             r"grows like $d^2$",
         y=0.26, size=11.5)


@figure("covariance_shapes")
def covariance_shapes(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Four families of covariance, from rigid to free",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    fams = [
        ("spherical", BLUE, r"$\Sigma_k = \sigma_k^2 I$", "$K$",
         [np.diag([0.30, 0.30]), np.diag([0.62, 0.62]), np.diag([0.16, 0.16])]),
        ("diagonal", GOLD, r"$\Sigma_k = \mathrm{diag}(\sigma_{k1}^2, \ldots)$",
         "$Kd$",
         [np.diag([0.62, 0.18]), np.diag([0.16, 0.55]), np.diag([0.40, 0.30])]),
        ("tied", GREEN, r"$\Sigma_k = \Sigma$ for all $k$", r"$d(d+1)/2$",
         [np.array([[0.46, 0.26], [0.26, 0.26]])] * 3),
        ("full", PURPLE, r"$\Sigma_k$ free", r"$K d(d+1)/2$",
         [np.array([[0.52, 0.30], [0.30, 0.26]]),
          np.array([[0.30, -0.22], [-0.22, 0.42]]),
          np.array([[0.55, 0.02], [0.02, 0.12]])]),
    ]
    centres = np.array([[-0.85, 0.55], [0.85, 0.50], [0.05, -0.80]])
    for i, (name, color, form, cost, Ss) in enumerate(fams):
        a = fig.add_axes([0.055 + i * 0.245, 0.30, 0.185, 0.44])
        for c, S, cc in zip(centres, Ss, COMP):
            ellipse(a, c, S, cc, nsig=(1.0, 2.0), lw=1.6)
            a.plot(*c, "o", color=cc, ms=4)
        a.set_xlim(-2.5, 2.5)
        a.set_ylim(-2.5, 2.2)
        a.set_aspect("equal")
        _bare(a)
        a.set_title(name, color=color, fontsize=12.5, pad=6)
        ax.text(0.50 + i * 2.21 + 0.83, 0.86, form, ha="center", va="center",
                color=INK, fontsize=11)
        ax.text(0.50 + i * 2.21 + 0.83, 0.50, cost + " numbers", ha="center",
                va="center", color=MUTED, fontsize=10.5)
    note(ax, "Fewer parameters give stabler fit on little data.", y=0.14,
         size=11.5)


@figure("gmm_params")
def gmm_params(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "How many numbers a Gaussian mixture costs",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    rows = [
        ("weights", PURPLE, r"$p_1, \ldots, p_K$", r"$K - 1$",
         "one is fixed by the others"),
        ("centres", BLUE, r"$\mu_1, \ldots, \mu_K$", r"$K d$",
         "one vector per component"),
        ("spread, spherical", GREEN, r"$\sigma_k^2 I$", r"$K$",
         "one width per component"),
        ("spread, diagonal", GREEN, r"$\mathrm{diag}(\Sigma_k)$", r"$K d$",
         "one width per axis, per component"),
        ("spread, full", GOLD, r"$\Sigma_k$", r"$K d (d+1) / 2$",
         "every covariance"),
    ]
    x = (0.50, 3.05, 4.70, 6.30)
    for xi, head in zip(x, ("Piece", "Symbol", "Count", "Why")):
        ax.text(xi, 3.10, head, color=MUTED, fontsize=11.5, va="center")
    ax.plot([0.42, 8.58], [2.92, 2.92], color=GRID, lw=1.2)
    for i, (name, color, sym, cnt, why) in enumerate(rows):
        y = 2.64 - i * 0.44
        ax.text(x[0], y, name, color=color, fontsize=12, weight="bold",
                va="center")
        ax.text(x[1], y, sym, color=INK, fontsize=12, va="center")
        ax.text(x[2], y, cnt, color=INK, fontsize=12, va="center")
        ax.text(x[3], y, why, color=MUTED, fontsize=11, va="center")
        if i:
            ax.plot([0.42, 8.58], [y + 0.22, y + 0.22], color=LIGHT, lw=1.0)
    box(ax, 0.55, 0.14, 3.70, 0.42, INK, "", fill="white", lw=1.4)
    ax.text(2.40, 0.35, r"In 1-D:  $3K - 1$", ha="center", va="center",
            color=INK, fontsize=12.5)
    box(ax, 4.75, 0.14, 3.70, 0.42, GOLD, "", fill="#fdf8ef", lw=1.4)
    ax.text(6.60, 0.35, r"In $d$-D:  $K(d+1)(d+2)/2 - 1$", ha="center",
            va="center", color=GOLD, fontsize=12.5)


@figure("identifiability")
def identifiability(fig):
    p = np.array([0.35, 0.65])
    mu = np.array([-1.4, 1.1])
    sd = np.array([0.75, 0.95])
    grid = np.linspace(-4.5, 4.5, 600)

    order = [(0, 1), (1, 0)]
    axes = []
    for i, perm in enumerate(order):
        a = fig.add_axes([0.07 + i * 0.30, 0.28, 0.25, 0.48])
        for slot, k in enumerate(perm):
            a.plot(grid, p[k] * _norm_pdf(grid, mu[k], sd[k]),
                   color=COMP[slot], lw=2.0, ls="--")
        a.plot(grid, _mix_pdf(grid, p, mu, sd), color=INK, lw=2.4)
        a.set_ylim(0, 0.30)
        a.set_yticks([])
        a.set_xticks([])
        despine(a, keep=("bottom",))
        axes.append(a)
    axes[0].set_title(r"Component 1 is the left one", color=INK,
                      fontsize=11.5, pad=7)
    axes[1].set_title(r"Component 1 is the right one", color=INK,
                      fontsize=11.5, pad=7)
    caption_row(fig, axes, [r"$\theta = (p_1, \theta_1, p_2, \theta_2)$",
                            r"$\theta' = (p_2, \theta_2, p_1, \theta_1)$"],
                y=0.20)

    ax = canvas(fig)
    ax.plot([5.85, 5.85], [0.60, 3.05], color=GRID, lw=1.2)
    column(ax, 6.10, 3.00, 2.6, "Label switching", [
        "$K!$ parameter vectors give\nexactly the same density",
        "Likelihood has $K!$\nidentical maxima",
        "Components can not be interpreted",
    ], RED, leading=0.30, item_size=10.5)
    ax.text(6.10, 0.7, "Can be fixed by sorting thecomponents\n(by $\\mu_k$, or by $p_k$)", 
            color=MUTED, fontsize=10.5, va="center", linespacing=1.5)
    fig.text(0.33, 0.055, "The two pictures are the same curve: only the "
                          "colours moved.", ha="center", va="center",
             color=MUTED, fontsize=11)


@figure("eq_simulation")
def eq_simulation(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"$Z \sim \mathcal{M}(p_1, \ldots, p_K)$ on "
         r"$\{1, \ldots, K\}$,$\quad$ i.e. $P(Z = k) = p_k$",
         r"one multinomial draw, with $p_1 + \cdots + p_K = 1$"),
        (r"$\mathcal{L}(x \mid Z = k) = f_k(x)$",
         "given the class, the point is an ordinary draw from one component"),
        (r"$T = (X, Z)$",
         "the complete data: the pair the generator actually produced", GREEN),
        (r"$X$ alone",
         r"the observed data: $Z$ is dropped out, $f(x) = \sum_k p_k f_k(x)$",
         BLUE),
    ], top=3.50, gap=0.67, x=0.45, eq_size=13, why_off=0.28)
    box(ax, 0.80, 0.1, 7.40, 0.40, PURPLE, "", fill="#f6f3fd")
    ax.text(W / 2, 0.3, "Simulation is much easier than estimation ($Z$ missing makes it hard).",
            ha="center", va="center", color=PURPLE, fontsize=12.5)


# ==========================================================================
# 3. fitting by maximum likelihood
# ==========================================================================
@figure("eq_loglik")
def eq_loglik(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Maximum likelihood, as usual", ha="center",
            va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 2.82, r"$\ell_{\mathrm{obs}}(x_1, \ldots, x_n; \theta)"
                         r"\;=\; \sum_i \log\!\left( \sum_k p_k \, "
                         r"f_k(x_i) \right)$",
            ha="center", va="center", color=INK, fontsize=21)
    ax.annotate("", xy=(5.58, 2.44), xytext=(5.10, 1.98),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.6))
    ax.text(5.04, 1.90, "a sum inside a log", ha="right", va="center",
            color=RED, fontsize=11.5)
    column(ax, 0.55, 1.58, 3.9, "Classic setting:", [
        "Set the gradient to zero",
        "Solve the closed-form",
    ], GREEN, leading=0.30, item_size=11.5)
    column(ax, 4.90, 1.58, 3.9, "Model mixture:", [
        "Log does not split over the components",
        "Derivative mixe all $\\theta$",
        "No closed form",
    ], RED, leading=0.30, item_size=11.5)
    ax.plot([4.65, 4.65], [0.46, 1.64], color=GRID, lw=1.2)
    note(ax, r"Maximising $\ell_{\mathrm{obs}}$ directly is hard. Expectation-Maximization avoids the problem.", y=0.20, size=11.5)


@figure("why_hard")
def why_hard(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"$\ell_{\mathrm{obs}}(\theta) = \sum_i \log"
         r"\left( p\, \varphi_{\theta_1}(x_i) "
         r"+ (1-p)\, \varphi_{\theta_2}(x_i) \right)$",
         r"$K = 2$ already has five unknowns"),
        (r"$\frac{\partial \ell_{\mathrm{obs}}}{\partial \mu_1}"
         r"= \sum_i \frac{p\, \varphi_{\theta_1}(x_i)}"
         r"{p\, \varphi_{\theta_1}(x_i) + (1-p)\, \varphi_{\theta_2}(x_i)}"
         r"\cdot \frac{x_i - \mu_1}{\sigma_1^2}$",
         r"the fraction depends on every parameter", RED),
        (r"$\Rightarrow$  no parameter separates from the others",
         r"while Gaussian alone gives $\hat{\mu} = \bar{x}$"),
    ], top=3.00, gap=0.80, x=0.45, eq_size=20, why_off=0.31)
    # box(ax, 0.55, 0.14, 3.70, 0.46, RED, "", fill="white", lw=1.5)
    # ax.text(2.40, 0.37, "unseparable, as written", ha="center", va="center",
    #         color=RED, fontsize=12.5)
    # box(ax, 4.75, 0.14, 3.70, 0.46, GREEN, "", fill="white", lw=1.5)
    # ax.text(6.60, 0.37, r"separable, if $z$ were known", ha="center",
    #         va="center", color=GREEN, fontsize=12.5)


@figure("loglik_landscape")
def loglik_landscape(fig):
    x = _animal_sample()
    sd = np.array([1.5, 1.6])
    g1 = np.linspace(83.5, 95.0, 160)
    g2 = np.linspace(83.5, 95.0, 160)
    M1, M2 = np.meshgrid(g1, g2)
    L = np.empty_like(M1)
    for i in range(M1.shape[0]):
        for j in range(M1.shape[1]):
            L[i, j] = _loglik1d(x, np.array([0.5, 0.5]),
                                np.array([M1[i, j], M2[i, j]]), sd)

    fig.text(0.5, 0.955, r"Observed log-likelihood over $(\mu_1, \mu_2)$, "
                         r"with the rest held fixed", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.085, 0.20, 0.40, 0.62])
    lv = np.linspace(np.percentile(L, 55), L.max(), 18)
    ax.contourf(M1, M2, L, levels=lv, cmap="Blues")
    ax.contour(M1, M2, L, levels=lv, colors="white", linewidths=0.5)
    p, mu, _ = _em1d(x, 2, 300, seed=1)
    ax.plot(mu[0], mu[1], "*", color=RED, ms=16, zorder=5)
    ax.plot(mu[1], mu[0], "*", color=RED, ms=16, zorder=5)
    ax.plot([83.5, 95.0], [83.5, 95.0], color=MUTED, lw=1.2, ls=":")
    ax.set_xlabel(r"$\mu_1$")
    ax.set_ylabel(r"$\mu_2$")
    ax.set_aspect("equal")
    despine(ax, keep=("left", "bottom"))

    axc = canvas(fig)
    axc.plot([5.00, 5.00], [0.55, 3.05], color=GRID, lw=1.2)
    column(axc, 5.25, 3.02, 3.4, "Interpretation:", [
        "Two maxima (red stars), mirror\nimages of one another",
        "Dotted diagonal $\\mu_1 = \\mu_2$ is a\nridge of saddle points",
        # "flat plateaus where one component\nexplains everything",
    ], BLUE, leading=0.30, item_size=11)
    axc.text(5.25, 0.84, "only two of the five parameters", color=MUTED,
             fontsize=10.5, va="center", linespacing=1.5)
    fig.text(0.29, 0.055, "Non-concave, with as many maxima as "
                          "relabellings.", ha="center", va="center",
             color=MUTED, fontsize=11)


@figure("degeneracy")
def degeneracy(fig):
    rng = np.random.default_rng(7)
    x = np.r_[rng.normal(-1.6, 0.7, 60), rng.normal(1.7, 0.8, 60)]
    grid = np.linspace(-4.5, 4.5, 2000)
    spike = float(x.max())
    sds = (0.30, 0.04, 0.002)
    pk, mu = np.array([0.95, 0.05]), np.array([float(x.mean()), spike])

    fig.text(0.5, 0.955, "Put one component on a single point and the "
                         "likelihood climbs without end", ha="center",
             va="center", color=MUTED, fontsize=12.5)
    axes = panels(fig, 3, gridspec_kw=dict(left=0.065, right=0.60, top=0.74,
                                           bottom=0.30, wspace=0.16))
    lls = []
    for ax, sg in zip(axes, sds):
        sd = np.array([1.7, sg])
        lls.append(_loglik1d(x, pk, mu, sd))
        d = _mix_pdf(grid, pk, mu, sd)
        ax.plot(grid, np.minimum(d, 0.32), color=INK, lw=2.0)
        ax.plot(x, np.full_like(x, -0.025), "|", color=MUTED, ms=7)
        ax.set_ylim(-0.05, 0.40)
        ax.set_yticks([])
        ax.set_xticks([])
        despine(ax, keep=("bottom",))
        ax.set_title(rf"$\sigma_2 = {sg:g}$", color=RED, fontsize=11.5, pad=6)
    assert lls[0] < lls[1] < lls[2]
    caption_row(fig, axes, [f"$\\ell = {v:,.0f}$" for v in lls], y=0.225)

    ax = canvas(fig)
    ax.plot([5.70, 5.70], [0.50, 3.05], color=GRID, lw=1.2)
    column(ax, 5.95, 3.02, 2.8, "Growing likelihood unbounded", [
        r"set $\mu_k = x_i$, let $\sigma_k \to 0$",
        r"$\ell_{\mathrm{obs}}$ then grows like $\log(1/\sigma_k)$,"
        "\nwithout any bound",
        "the global maximum is a useless\nspike sitting on one point",
        # "what we want is a good local\nmaximum, not the global one",
    ], RED, leading=0.30, item_size=11)
    # ax.text(5.95, 0.64, "in practice: floor the variance, or add\n"
    #                     r"a small ridge to $\Sigma_k$ (sklearn's"
    #                     "\n$\\mathtt{reg\\_covar}$)", color=MUTED,
    #         fontsize=10.5, va="center", linespacing=1.5)


@figure("complete_data_idea")
def complete_data_idea(fig):
    x = _animal_sample()
    p, mu, sd = _em1d(x, 2, 300, seed=1)
    g = _resp1d(x, p, mu, sd)
    z = g.argmax(1)
    bins = np.arange(81.5, 99.5, 1.0)

    fig.text(0.5, 0.955, "Suppose, for a moment, that the labels were "
                         "known", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    axes = panels(fig, 2, titles=["Data", "Wish data"],
                  colors=[INK, GREEN],
                  gridspec_kw=dict(left=0.065, right=0.60, top=0.78, bottom=0.26, wspace=0.20))
    axes[0].hist(x, bins=bins, color=LIGHT, edgecolor=GRID, lw=0.8)
    axes[1].hist([x[z == 0], x[z == 1]], bins=bins, stacked=True,
                 color=[COMP[0], COMP[1]], alpha=0.8)
    for ax in axes:
        ax.set_xlabel("length (mm)")
        ax.set_yticks([])
        despine(ax, keep=("bottom",))
    caption_row(fig, axes, [r"$(x_i)_i$", r"$(x_i, z_i)_i$"], y=0.105)

    ax = canvas(fig)
    ax.plot([5.70, 5.70], [0.55, 3.05], color=GRID, lw=1.2)
    column(ax, 5.95, 3.02, 2.8, "With the labels", [
        "each class is a plain Gaussian\nsample",
        "mean and variance, class by class",
        r"$p_k$ is just the share of the class",
        "the estimation is a one-liner",
    ], GREEN, leading=0.28, item_size=11)
    ax.text(5.95, 0.82, "The labels are exactly the information\nthe generator threw away.",
            color=MUTED, fontsize=10.5, va="center", linespacing=1.5)


@figure("eq_complete_loglik")
def eq_complete_loglik(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"$\ell(\theta; x, z) = \sum_i \log\!\left( p_{z_i} "
         r"f_{z_i}(x_i) \right)"
         r"= \sum_i \sum_k \mathbb{1}_{z_i = k} \log( p_k f_k(x_i) )$",
         "with $z$ known, the point belongs to one component and only one"),
        (r"$K = 2$:$\quad \ell(\theta; x, z) = \sum_i \left( z_i "
         r"\log \varphi_{\theta_1}(x_i) + (1 - z_i) "
         r"\log \varphi_{\theta_2}(x_i) \right)$", ""),
        (r"$\qquad\qquad\qquad\quad\; + \sum_i \left( z_i \log p "
         r"+ (1 - z_i) \log(1 - p) \right)$",
         "the lecture's two lines: one per component, plus the weights",
         BLUE),
        (r"$\Rightarrow$  the log sits on a single density, not on a sum",
         r"$\theta_1$, $\theta_2$ and $p$ appear in separate terms"),
    ], top=3.52, gap=0.66, x=0.45, eq_size=13, why_off=0.27)
    box(ax, 0.80, 0.1, 7.40, 0.40, GREEN, "", fill="#f1faf1")
    ax.text(W / 2, 0.3, "Separable — three independent maximisations "
                         "instead of one hard one",
            ha="center", va="center", color=GREEN, fontsize=12.5)


@figure("eq_complete_mle")
def eq_complete_mle(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Maximising it: count, average, average again",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    rows = [
        (PURPLE, r"$\hat{p}_k \;=\; \frac{1}{n} \sum_i "
         r"\mathbb{1}_{z_i = k}$",
         r"the share of the sample that carries label $k$"),
        (BLUE, r"$\hat{\mu}_k \;=\; \frac{1}{n \hat{p}_k} "
         r"\sum_{i \,:\, z_i = k} x_i$",
         r"the mean of the points of class $k$"),
        (GOLD, r"$\hat{\sigma}_k^2 \;=\; \frac{1}{n \hat{p}_k} "
         r"\sum_{i \,:\, z_i = k} (x_i - \hat{\mu}_k)^2$",
         "their spread around that mean"),
    ]
    for i, (color, eq, why) in enumerate(rows):
        y = 2.82 - i * 0.92
        ax.text(0.60, y, eq, color=color, fontsize=15, va="center")
        ax.text(0.60, y - 0.42, why, color=MUTED, fontsize=10.5, va="center")

    # the same three numbers, read off a labelled sample
    x = _animal_sample()
    pk, mu, sd = _em1d(x, 2, 300, seed=1)
    z = _resp1d(x, pk, mu, sd).argmax(1)
    bx = fig.add_axes([0.605, 0.24, 0.355, 0.50])
    bins = np.arange(81.5, 99.5, 1.0)
    bx.hist([x[z == 0], x[z == 1]], bins=bins, stacked=True,
            color=[COMP[0], COMP[1]], alpha=0.8)
    for k in range(2):
        xs = x[z == k]
        bx.axvline(xs.mean(), color=COMP[k], lw=2.0, ls="--")
        bx.annotate("", xy=(xs.mean() - xs.std(), 66),
                    xytext=(xs.mean() + xs.std(), 66),
                    arrowprops=dict(arrowstyle="<|-|>", color=COMP[k], lw=1.4))
        bx.text(xs.mean() + 1.9, 70,
                rf"$\hat{{p}}_{k+1} = {(z == k).mean():.2f}$",
                ha="center", va="bottom", color=COMP[k], fontsize=10.5)
    bx.set_ylim(0, 92)
    bx.set_xlabel("length (mm)")
    bx.set_yticks([])
    despine(bx, keep=("bottom",))
    fig.text(0.785, 0.055, r"dashed line: $\hat{\mu}_k$,"
                           r"$\;$ arrow: $\pm \hat{\sigma}_k$",
             ha="center", va="center", color=MUTED, fontsize=10.5)

    note(ax, "Single-Gaussian formulas applied inside each class.",
         y=0.075, size=11.5)


def _animal_fit():
    """The two-component fit of the animal lengths, used by the slides that
    read class probabilities off a fitted density."""
    x = _animal_sample()
    p, mu, sd = _em1d(x, 2, 300, seed=1)
    return x, p, mu, sd


@figure("posterior_pointwise")
def posterior_pointwise(fig):
    x, p, mu, sd = _animal_fit()
    x0 = 89.0
    a = p * _norm_pdf(x0, mu, sd)
    post = a / a.sum()
    grid = np.linspace(80, 99, 700)

    fig.text(0.5, 0.955, "Once the mixture is known, every point gets "
                         "class probabilities", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    bx = fig.add_axes([0.06, 0.22, 0.42, 0.60])
    for k in range(2):
        bx.plot(grid, p[k] * _norm_pdf(grid, mu[k], sd[k]), color=COMP[k],
                lw=2.0, ls="--", label=rf"$p_{k+1} f_{k+1}(x)$")
    bx.plot(grid, _mix_pdf(grid, p, mu, sd), color=MIX, lw=2.2,
            label=r"$f(x)$")
    # the two heights at x0, stacked: together they make f(x0)
    bx.plot([x0, x0], [0, a[0]], color=COMP[0], lw=5, solid_capstyle="butt")
    bx.plot([x0, x0], [a[0], a.sum()], color=COMP[1], lw=5,
            solid_capstyle="butt")
    bx.plot([x0], [a.sum()], "o", color=MIX, ms=5)
    top = _mix_pdf(grid, p, mu, sd).max()
    for k, (yl, yb) in enumerate([(0.40, a[0] / 2), (0.26, a[0] + a[1] / 2)]):
        bx.annotate(rf"$p_{k+1} f_{k+1}(x_0)$", xy=(x0 + 0.15, yb),
                    xytext=(95.2, yl * top), color=COMP[k], fontsize=11,
                    va="center",
                    arrowprops=dict(arrowstyle="-|>", color=COMP[k], lw=1.2,
                                    shrinkA=3, shrinkB=2))
    bx.set_xticks([82, 86, x0, 92, 96])
    bx.set_xticklabels(["82", "86", r"$x_0 = 89$", "92", "96"])
    bx.set_yticks([])
    bx.set_xlabel("length (mm)")
    bx.set_ylim(0, 1.32 * top)
    bx.legend(loc="upper center", ncol=3, fontsize=10, handlelength=1.6)
    despine(bx, keep=("bottom",))

    ax = canvas(fig)
    ax.plot([4.70, 4.70], [0.55, 3.10], color=GRID, lw=1.2)
    steps(ax, [
        (r"$P(Z = k \mid X = x) = \frac{P(Z = k)\, f(x \mid Z = k)}"
         r"{f(x)}$", "Bayes' rule"),
        (r"$P(Z = k \mid X = x) = \frac{p_k\, f_k(x)}{\sum_l p_l\, f_l(x)}$",
         "prior times density, over the mixture (total probability)"),
        # (rf"$x_0 = 89$:$\quad {post[0]:.2f}$ for class 1, "
        #  rf"${post[1]:.2f}$ for class 2",
        #  "the blue share and the gold share of the bar"),
    ], top=3.00, gap=1.1, x=4.95, eq_size=16, why_off=0.40)
    note(ax, "No label is needed: only the fitted $p_k$, $\\mu_k$, $\\sigma_k$.",
         y=0.22, size=11.5)


@figure("posterior_curve")
def posterior_curve(fig):
    x, p, mu, sd = _animal_fit()
    grid = np.linspace(80, 99, 700)
    g = _resp1d(grid, p, mu, sd)
    cut = grid[np.argmin(np.abs(g[:, 0] - 0.5))]
    z = _resp1d(x, p, mu, sd).argmax(1)
    bins = np.arange(81.5, 99.5, 1.0)

    fig.text(0.5, 0.955, "The same computation at every point of the axis",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    ax1 = fig.add_axes([0.07, 0.53, 0.55, 0.30])
    ax1.hist([x[z == 0], x[z == 1]], bins=bins, stacked=True,
             color=[COMP[0], COMP[1]], alpha=0.8)
    ax1.set_xlim(80, 99)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_ylabel("most likely\nclass", color=MUTED, fontsize=10.5)
    despine(ax1)

    ax2 = fig.add_axes([0.07, 0.20, 0.55, 0.28])
    ax2.plot(grid, g[:, 0], color=COMP[0], lw=2.2,
             label=r"$P(Z = 1 \mid x)$")
    ax2.plot(grid, g[:, 1], color=COMP[1], lw=2.2,
             label=r"$P(Z = 2 \mid x)$")
    ax2.axhline(0.5, color=GRID, lw=1.0, ls=":")
    ax2.set_xlim(80, 99)
    ax2.set_ylim(0, 1.02)
    ax2.set_yticks([0, 0.5, 1])
    ax2.set_xlabel("length (mm)")
    ax2.legend(loc="center right", fontsize=9.5, handlelength=1.4)
    despine(ax2, keep=("left", "bottom"))
    for a in (ax1, ax2):
        a.axvline(cut, color=MUTED, lw=1.2, ls="--")
    ax2.text(cut - 0.45, 0.22, f"boundary {cut:.1f} mm", color=MUTED,
             fontsize=10, va="center", ha="right")

    ax = canvas(fig)
    ax.plot([6.05, 6.05], [0.50, 3.05], color=GRID, lw=1.2)
    column(ax, 6.30, 3.02, 2.6, "Pointwise", [
        "each $x$ gets its own\nprobabilities, summing to 1",
        "classify: pick the larger one",
        "boundary: where they are equal",
    ], BLUE, leading=0.30, item_size=11)
    ax.text(6.30, 0.62, "Needs the parameters...", color=MUTED, fontsize=10.5, va="center", linespacing=1.5)


@figure("chicken_egg")
def chicken_egg(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Each half is easy",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    box(ax, 0.85, 2.00, 3.00, 0.92, GREEN,
        r"know $z$  $\Rightarrow$  get $\theta$", size=14)
    ax.text(2.35, 1.78, "count and average", ha="center", va="center",
            color=GREEN, fontsize=11)
    box(ax, 5.15, 2.00, 3.00, 0.92, BLUE,
        r"know $\theta$  $\Rightarrow$  get $z$", size=14)
    ax.text(6.65, 1.78, "Bayes' rule, point by point", ha="center",
            va="center", color=BLUE, fontsize=11)
    arrow(ax, (3.95, 2.70), (5.05, 2.70), color=MUTED, rad=-0.35)
    arrow(ax, (5.05, 2.22), (3.95, 2.22), color=MUTED, rad=-0.35)
    column(ax, 0.85, 1.42, 3.4, "Problem:", [
        "Neither is known",
        "Likelihood couples $z$ and $\\theta$",
    ], RED, leading=0.30, item_size=11.5)
    column(ax, 5.15, 1.42, 3.4, "Solution:", [
        "Alternate guessing $\\theta$ & deducing $z$",
        # "This is EM",
    ], GREEN, leading=0.30, item_size=11.5)
    note(ax, "Keep probability of each label, and weight by it.", y=0.26, size=11.5)


# ==========================================================================
# 4. responsibilities
# ==========================================================================
@figure("bayes_reminder")
def bayes_reminder(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Three lines of probability, and nothing else",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    rows = [
        (BLUE, "conditioning", r"$P(A \mid B) = \frac{P(A \cap B)}{P(B)}$",
         "renormalise inside $B$"),
        (PURPLE, "Bayes' rule",
         r"$P(B \mid A) = \frac{P(A \mid B)\, P(B)}{P(A)}$",
         "turn the conditioning around"),
        (GOLD, "total probability",
         r"$P(A) = \sum_i P(A \cap B_i)$",
         r"for a partition $B_1, \ldots, B_n$ of $\Omega$"),
    ]
    for i, (color, name, eq, why) in enumerate(rows):
        y = 2.88 - i * 0.82
        ax.text(2.35, y, name, ha="right", va="center", color=color,
                fontsize=12.5, weight="bold")
        ax.text(2.60, y, eq, ha="left", va="center", color=INK, fontsize=16)
        ax.text(6.00, y, why, ha="left", va="center", color=MUTED,
                fontsize=11)
        if i:
            ax.plot([0.45, 8.55], [y + 0.42, y + 0.42], color=LIGHT, lw=1.0)
    box(ax, 0.80, 0.14, 7.40, 0.46, GREEN, "", fill="#f1faf1")
    ax.text(W / 2, 0.37, r"Put $B_k = \{Z = k\}$ and $A = \{X = x\}$: "
                         r"the three lines give the responsibility",
            ha="center", va="center", color=GREEN, fontsize=12.5)


@figure("eq_responsibility")
def eq_responsibility(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "The posterior probability of the label, given the "
                         "point", ha="center", va="center", color=MUTED,
            fontsize=12.5)
    eq = ax.text(0.80, 2.78, r"$\gamma_{ik}(\theta) \;=\; P(Z_i = k \mid "
                 r"X_i = x_i, \theta) \;=\; \frac{p_k \, f_k(x_i)}"
                 r"{\sum_l p_l \, f_l(x_i)}$",
                 ha="left", va="center", color=INK, fontsize=20)
    # aim at the fraction itself: it is the right end of the equation
    bb = eq.get_window_extent(fig.canvas.get_renderer())
    right, top, bottom = bb.x1 / DPI, bb.y1 / DPI, bb.y0 / DPI
    ax.annotate("", xy=(right + 0.06, top - 0.16), xytext=(right + 0.55, top - 0.02),
                arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=1.6))
    ax.text(right + 0.62, top - 0.02, "prior times likelihood", ha="left",
            va="center", color=PURPLE, fontsize=11)
    ax.annotate("", xy=(right + 0.06, bottom + 0.20), xytext=(right + 0.55, bottom + 0.02),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6))
    ax.text(right + 0.62, bottom + 0.02, "the mixture density at $x_i$",
            ha="left", va="center", color=BLUE, fontsize=11)
    column(ax, 0.55, 1.80, 3.9, "Interpret as", [
        r"$\gamma_{ik} \geq 0$ and $\gamma_{i1} + \cdots + "
        r"\gamma_{iK} = 1$",
        r"it is the expected label: $\gamma_{ik} = E[\mathbb{1}_{Z_i = k} "
        r"\mid x_i, \theta]$",
        r"$K = 2$: $\;\gamma_{i1} = E[Z_i \mid x_i, \theta]$",
    ], GOLD, leading=0.32, item_size=11)
    column(ax, 4.90, 1.80, 3.9, "Benefits", [
        "Computable the moment $\\theta$ is known",
        "Soft label: no decision is taken",
    ], GREEN, leading=0.32, item_size=11)
    ax.plot([4.65, 4.65], [0.50, 1.86], color=GRID, lw=1.2)
    note(ax, "$\\gamma_{ik}$ is the responsibility of component $k$ for point $i$.",
         y=0.18, size=15)


@figure("responsibility_picture")
def responsibility_picture(fig):
    p = np.array([0.45, 0.55])
    mu = np.array([86.0, 92.2])
    sd = np.array([1.5, 1.9])
    grid = np.linspace(80, 99, 700)
    g = _resp1d(grid, p, mu, sd)
    marks = np.array([84.5, 88.6, 89.4, 94.5])
    gm = _resp1d(marks, p, mu, sd)

    fig.text(0.5, 0.955, "Where a point sits decides how it is shared",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    ax1 = fig.add_axes([0.075, 0.50, 0.55, 0.32])
    for k in range(2):
        ax1.plot(grid, p[k] * _norm_pdf(grid, mu[k], sd[k]), color=COMP[k],
                 lw=2.0, ls="--")
    ax1.plot(grid, _mix_pdf(grid, p, mu, sd), color=INK, lw=2.2)
    ax1.set_xticks([])
    ax1.set_yticks([])
    despine(ax1)
    ax1.set_ylabel("the fit", color=MUTED, fontsize=10.5)

    ax2 = fig.add_axes([0.075, 0.20, 0.55, 0.26])
    ax2.fill_between(grid, 0, g[:, 0], color=COMP[0], alpha=0.75)
    ax2.fill_between(grid, g[:, 0], 1, color=COMP[1], alpha=0.75)
    ax2.set_ylim(0, 1)
    ax2.set_yticks([0, 1])
    ax2.set_xlabel("length (mm)")
    ax2.set_ylabel(r"$\gamma_{ik}$", fontsize=11)
    despine(ax2, keep=("left", "bottom"))
    for xm in marks:
        ax1.axvline(xm, color=MUTED, lw=1.0, ls=":")
        ax2.axvline(xm, color="white", lw=1.4)

    ax = canvas(fig)
    ax.plot([6.15, 6.15], [0.50, 3.05], color=GRID, lw=1.2)
    ax.text(6.40, 3.02, "Four points", color=INK, fontsize=14,
            weight="bold", va="top")
    for i, xm in enumerate(marks):
        y = 2.30 - i * 0.46
        ax.text(6.40, y, f"$x = {xm}$", color=INK, fontsize=11.5,
                va="center")
        ax.text(7.45, y, f"{gm[i, 0]:.2f}", color=COMP[0], fontsize=11.5,
                va="center", ha="right")
        ax.text(8.10, y, f"{gm[i, 1]:.2f}", color=COMP[1], fontsize=11.5,
                va="center", ha="right")
    ax.text(7.45, 2.66, r"$\gamma_{i1}$", color=COMP[0], fontsize=11,
            va="center", ha="right")
    ax.text(8.10, 2.66, r"$\gamma_{i2}$", color=COMP[1], fontsize=11,
            va="center", ha="right")
    ax.text(6.40, 0.36, "On extremes, the split is certain;\nIn the middle, less so",
            color=MUTED, fontsize=10.5, va="center", linespacing=1.5)


@figure("responsibility_matrix")
def responsibility_matrix(fig):
    x = _animal_sample()
    p, mu, sd = _em1d(x, 2, 300, seed=1)
    rng = np.random.default_rng(0)
    idx = np.sort(rng.choice(len(x), 16, replace=False))
    xs = x[idx]
    g = _resp1d(xs, p, mu, sd)

    ax = canvas(fig)
    ax.text(W / 2, 3.52, "One row per point, one column per component",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    _matrix(ax, 1.30, 0.80, 0.95, 2.10, BLUE, G_CMAP, M=g,
            shape=r"$n \times K$", vmax=1.0)
    ax.text(1.775, 3.26, r"$\gamma$", ha="center", va="center", color=BLUE,
            fontsize=14)
    for k in range(2):
        ax.text(1.30 + 0.95 * (k + 0.5) / 2, 2.98, f"$k = {k+1}$",
                ha="center", va="center", color=COMP[k], fontsize=10.5)
    ax.text(1.18, 1.85, "points", ha="right", va="center", color=MUTED,
            fontsize=11, rotation=90)

    # the same numbers, spelled out for four rows
    xcol = (3.15, 4.45, 5.45, 6.45)
    heads = (r"$x_i$", r"$\gamma_{i1}$", r"$\gamma_{i2}$", "")
    hcols = (MUTED, COMP[0], COMP[1], MUTED)
    for xi, head, hc in zip(xcol, heads, hcols):
        ax.text(xi, 3.00, head, color=hc, fontsize=11.5, va="center")
    ax.plot([3.05, 7.30], [2.80, 2.80], color=GRID, lw=1.1)
    rows = [0, 5, 9, 15]
    for i, r in enumerate(rows):
        y = 2.52 - i * 0.52
        ax.text(xcol[0], y, f"${xs[r]:.0f}$", color=INK, fontsize=12,
                va="center")
        ax.text(xcol[1], y, f"{g[r, 0]:.3f}", color=COMP[0], fontsize=12,
                va="center")
        ax.text(xcol[2], y, f"{g[r, 1]:.3f}", color=COMP[1], fontsize=12,
                va="center")
        ax.text(xcol[3], y, f"sum {g[r].sum():.0f}", color=MUTED,
                fontsize=11, va="center")
        if i:
            ax.plot([3.05, 7.30], [y + 0.26, y + 0.26], color=LIGHT, lw=1.0)

    column(ax, 7.55, 3.02, 1.3, "Properties", [
        "rows sum to one",
        "column sums are\nthe soft class\nsizes $n_k$",
    ], GOLD, leading=0.28, item_size=10.5, title_size=13)
    note(ax, r"$n_k = \gamma_{1k} + \cdots + \gamma_{nk}$ is soft class count",
         y=0.22, size=11.5)


@figure("soft_vs_hard")
def soft_vs_hard(fig):
    rng = np.random.default_rng(12)
    n = 260
    mus = np.array([[-0.75, -0.25], [0.80, 0.40]])
    Ss = [np.array([[0.95, 0.52], [0.52, 0.40]]),
          np.array([[0.70, -0.40], [-0.40, 0.48]])]
    z = rng.choice(2, n, p=(0.55, 0.45))
    X = np.zeros((n, 2))
    for k in range(2):
        m = z == k
        X[m] = rng.multivariate_normal(mus[k], Ss[k], int(m.sum()))
    p, mu_f, S_f = _em2d(X, 2, 80, seed=2)
    g = _resp2d(X, p, mu_f, S_f)

    fig.text(0.5, 0.955, "Soft assignment keeps the doubt; hard assignment "
                         "throws it away", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    axes = panels(fig, 2, titles=["soft: a weight per component",
                                  "hard: one label"],
                  colors=[GOLD, RED],
                  gridspec_kw=dict(left=0.06, right=0.60, top=0.80,
                                   bottom=0.22, wspace=0.14))
    mix = LinearSegmentedColormap.from_list(
        "mix", [COMP[1], "#efe6d2", "#e8eef5", COMP[0]])
    axes[0].scatter(X[:, 0], X[:, 1], c=g[:, 0], cmap=mix, s=26,
                    vmin=0, vmax=1, edgecolors="white", linewidths=0.4)
    axes[1].scatter(X[:, 0], X[:, 1], c=[COMP[k] for k in g.argmax(1)], s=26,
                    edgecolors="white", linewidths=0.4)
    for ax in axes:
        for k in range(2):
            ellipse(ax, mu_f[k], S_f[k], COMP[k], nsig=(1.0, 2.0), lw=1.4)
        ax.set_aspect("equal")
        _bare(ax)

    # the colour key: gamma running from one component to the other
    key = fig.add_axes([0.10, 0.145, 0.18, 0.035])
    key.imshow(np.linspace(0, 1, 256)[None, :], cmap=mix, aspect="auto")
    _bare(key)
    fig.text(0.095, 0.162, r"$\gamma_{i1} = 0$", ha="right", va="center",
             color=COMP[1], fontsize=9.5)
    fig.text(0.285, 0.162, r"$1$", ha="left", va="center", color=COMP[0],
             fontsize=9.5)

    ax = canvas(fig)
    ax.plot([5.75, 5.75], [0.45, 3.05], color=GRID, lw=1.2)
    column(ax, 6.00, 3.02, 2.8, "Soft benefits", [
        "Points between the clusters are\nuncertain",
        "Gaussian estimation step weights\ninstead of mis-assigning",
        "Stays differentiable in $\\theta$",
    ], GOLD, leading=0.30, item_size=10.5)
    n_mid = int((g.max(1) < 0.9).sum())
    ax.text(6.00, 0.70, f"{n_mid} of these {n} points have no\n"
                        f"component above 0.9: the pale ones.",
            color=MUTED, fontsize=10.5, va="center", linespacing=1.5)


# ==========================================================================
# 5. the EM algorithm
# ==========================================================================
@figure("em_idea")
def em_idea(fig):
    ax = canvas(fig)
    box(ax, 0.90, 1.95, 2.95, 0.95, BLUE, "", fill="white")
    ax.text(2.375, 2.60, "E-step", ha="center", va="center", color=BLUE,
            fontsize=14, weight="bold")
    ax.text(2.375, 2.22, r"$\theta$ fixed $\;\to\;$ compute $\gamma_{ik}$",
            ha="center", va="center", color=INK, fontsize=12)
    box(ax, 5.15, 1.95, 2.95, 0.95, GREEN, "", fill="white")
    ax.text(6.625, 2.60, "M-step", ha="center", va="center", color=GREEN,
            fontsize=14, weight="bold")
    ax.text(6.625, 2.22, r"$\gamma$ fixed $\;\to\;$ compute $\theta$",
            ha="center", va="center", color=INK, fontsize=12)
    arrow(ax, (3.95, 2.70), (5.05, 2.70), color=MUTED, rad=-0.35)
    arrow(ax, (5.05, 2.18), (3.95, 2.18), color=MUTED, rad=-0.35)
    ax.text(4.50, 3.10, "soft labels", ha="center", va="center", color=MUTED,
            fontsize=10.5)
    ax.text(4.50, 1.74, "new parameters", ha="center", va="center",
            color=MUTED, fontsize=10.5)
    column(ax, 0.90, 1.42, 3.4, "Each half is exact", [
        "Bayes' rule, no approximation",
        "weighted means and variances",
    ], INK, leading=0.30, item_size=11.5)
    column(ax, 5.15, 1.42, 3.4, "The flaws", [
        "Local maximum",
        "Initialization to pick",
    ], RED, leading=0.30, item_size=11.5)
    note(ax, "Nothing is ever optimised jointly, yet the observed "
             "likelihood climbs at every pass.", y=0.26, size=11.5)


@figure("em_algorithm")
def em_algorithm(fig):
    ax = canvas(fig)
    lines = [
        (BLUE, "input", r"$x_1, \ldots, x_n$, and the number of "
                        r"components $K$"),
        (BLUE, "init", r"$\theta^0 = (p_k^0, \mu_k^0, \sigma_k^0)_k$, "
                       r"at random or from a clustering"),
        (INK, "repeat", r"E-step:$\;\;$ $\gamma_{ik} \leftarrow "
                        r"p_k^t f_{k,t}(x_i) \,/\, \sum_l p_l^t "
                        r"f_{l,t}(x_i)$,$\quad$ for all $i, k$"),
        (INK, "", r"M-step:$\;$ $n_k \leftarrow \sum_i \gamma_{ik}$,"
                  r"$\quad p_k^{t+1} \leftarrow n_k / n$"),
        (INK, "", r"$\qquad\qquad\; \mu_k^{t+1} \leftarrow "
                  r"(1/n_k) \sum_i \gamma_{ik}\, x_i$"),
        (INK, "", r"$\qquad\qquad\; (\sigma_k^{t+1})^2 \leftarrow "
                  r"(1/n_k) \sum_i \gamma_{ik}\,"
                  r"(x_i - \mu_k^{t+1})^2$"),
        (GOLD, "until", r"$\ell_{\mathrm{obs}}(\theta^t)$ stops "
                        r"increasing"),
        (GREEN, "output", r"$\hat{\theta}$, and the responsibilities "
                          r"$\gamma$ as soft labels"),
    ]
    box(ax, 0.50, 0.64, 8.00, 2.60, BLUE, "", fill="white", lw=1.6)
    for i, (color, key, text) in enumerate(lines):
        y = 3.00 - i * 0.325
        ax.text(1.55, y, key, ha="right", va="center", color=color,
                fontsize=12, weight="bold" if key else "normal")
        ax.text(1.72, y, text, ha="left", va="center", color=INK,
                fontsize=11.5)
    note(ax, r"cost per pass: $\mathcal{O}(nKd)$ on the line, "
             r"$\mathcal{O}(nKd^2)$ with full covariances", y=0.38,
         size=11.5)
    note(ax, "no step size, no line search — every update is a closed form",
         y=0.10, size=11.5)


@figure("em_estep")
def em_estep(fig):
    x = _animal_sample()
    p0, mu0, sd0 = np.array([0.5, 0.5]), np.array([88.0, 91.0]), \
        np.array([2.2, 2.2])
    grid = np.linspace(80, 99, 600)
    g = _resp1d(grid, p0, mu0, sd0)
    gx = _resp1d(x, p0, mu0, sd0)

    fig.text(0.5, 0.955, "E-step: with $\\theta$ frozen, every point is "
                         "split between the components", ha="center",
             va="center", color=BLUE, fontsize=12.5)
    ax1 = fig.add_axes([0.07, 0.50, 0.52, 0.30])
    ax1.hist(x, bins=np.arange(81.5, 99.5, 1.0), density=True, color=LIGHT,
             edgecolor="none")
    for k in range(2):
        ax1.plot(grid, p0[k] * _norm_pdf(grid, mu0[k], sd0[k]),
                 color=COMP[k], lw=2.2)
    ax1.set_xticks([])
    ax1.set_yticks([])
    despine(ax1)
    ax1.set_title(r"the current $\theta^t$ — deliberately a poor one",
                  color=MUTED, fontsize=11, pad=6)

    ax2 = fig.add_axes([0.07, 0.19, 0.52, 0.25])
    ax2.fill_between(grid, 0, g[:, 0], color=COMP[0], alpha=0.75)
    ax2.fill_between(grid, g[:, 0], 1, color=COMP[1], alpha=0.75)
    ax2.set_ylim(0, 1)
    ax2.set_yticks([0, 1])
    ax2.set_xlabel("length (mm)")
    ax2.set_ylabel(r"$\gamma_{ik}$")
    despine(ax2, keep=("left", "bottom"))

    ax = canvas(fig)
    ax.plot([5.55, 5.55], [0.45, 3.05], color=GRID, lw=1.2)
    ax.text(5.80, 3.02, "Computes", color=BLUE, fontsize=14, weight="bold", va="top")
    ax.text(5.80, 2.34, r"$\gamma_{ik} = \dfrac{p_k f_k(x_i)}"
                        r"{\sum_l p_l f_l(x_i)}$", color=INK, fontsize=14,
            va="center")
    ax.text(5.80, 1.70, "an $n \\times K$ table of weights,\n"
                        "each row summing to one", color=INK, fontsize=11,
            va="center", linespacing=1.5)
    nk = gx.sum(0)
    ax.text(5.80, 1.10, f"soft class sizes here:\n"
                        f"$n_1 = {nk[0]:.0f}$, $n_2 = {nk[1]:.0f}$",
            color=GOLD, fontsize=11, va="center", linespacing=1.5)
    ax.text(5.80, 0.58, "No $\\theta$ has moved yet", color=MUTED,
            fontsize=10.5, va="center", linespacing=1.5)


@figure("em_mstep")
def em_mstep(fig):
    x = _animal_sample()
    p0, mu0, sd0 = np.array([0.5, 0.5]), np.array([88.0, 91.0]), \
        np.array([2.2, 2.2])
    g = _resp1d(x, p0, mu0, sd0)
    nk = g.sum(0)
    p1 = nk / len(x)
    mu1 = (g * x[:, None]).sum(0) / nk
    sd1 = np.sqrt((g * (x[:, None] - mu1) ** 2).sum(0) / nk)
    grid = np.linspace(80, 99, 600)

    fig.text(0.5, 0.955, "M-step: with $\\gamma$ frozen, re-fit each "
                         "component to its weighted share", ha="center",
             va="center", color=GREEN, fontsize=12.5)
    axes = panels(fig, 2, titles=[r"before: $\theta^t$",
                                  r"after: $\theta^{t+1}$"],
                  colors=[MUTED, GREEN],
                  gridspec_kw=dict(left=0.065, right=0.585, top=0.78,
                                   bottom=0.30, wspace=0.16))
    for ax, (pp, mm, ss) in zip(axes, ((p0, mu0, sd0), (p1, mu1, sd1))):
        ax.hist(x, bins=np.arange(81.5, 99.5, 1.0), density=True,
                color=LIGHT, edgecolor="none")
        for k in range(2):
            ax.plot(grid, pp[k] * _norm_pdf(grid, mm[k], ss[k]),
                    color=COMP[k], lw=2.2)
        ax.set_ylim(0, 0.17)
        ax.set_yticks([])
        ax.set_xlabel("length (mm)")
        despine(ax, keep=("bottom",))
    caption_row(fig, axes,
                [f"$\\ell = {_loglik1d(x, p0, mu0, sd0):,.0f}$",
                 f"$\\ell = {_loglik1d(x, p1, mu1, sd1):,.0f}$"], y=0.115)

    ax = canvas(fig)
    ax.plot([5.95, 5.95], [0.45, 3.05], color=GRID, lw=1.2)
    rows = [
        (PURPLE, r"$p_k \leftarrow n_k / n$"),
        (BLUE, r"$\mu_k \leftarrow \frac{1}{n_k} \sum_i \gamma_{ik} x_i$"),
        (GOLD, r"$\sigma_k^2 \leftarrow \frac{1}{n_k} \sum_i \gamma_{ik}"
               r"(x_i - \mu_k)^2$"),
    ]
    for i, (color, eq) in enumerate(rows):
        ax.text(6.20, 2.42 - i * 0.62, eq, color=color, fontsize=13,
                va="center")
    ax.text(6.20, 0.60, "complete-data formulas,\nwith"
                        r"$\gamma_{ik}$ in place of $\mathbb{1}_{z_i = k}$",
            color=MUTED, fontsize=13, va="center", linespacing=1.5)


@figure("eq_em_mstep")
def eq_em_mstep(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Formulas counted softly", ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(2.55, 3.04, "labels known", ha="center", va="center", color=MUTED,
            fontsize=12)
    ax.text(6.45, 3.04, "labels unknown", ha="center", va="center",
            color=GREEN, fontsize=12)
    ax.plot([4.50, 4.50], [0.70, 3.16], color=GRID, lw=1.2)
    rows = [
        (PURPLE, r"$\hat{p}_k = \frac{1}{n} \sum_i \mathbb{1}_{z_i = k}$",
         r"$p_k^{t+1} = \frac{1}{n} \sum_i \gamma_{ik}$"),
        (BLUE, r"$\hat{\mu}_k = \frac{1}{n \hat{p}_k} "
               r"\sum_{i : z_i = k} x_i$",
         r"$\mu_k^{t+1} = \frac{1}{n_k} \sum_i \gamma_{ik}\, x_i$"),
        (GOLD, r"$\hat{\sigma}_k^2 = \frac{1}{n \hat{p}_k} "
               r"\sum_{i : z_i = k} (x_i - \hat{\mu}_k)^2$",
         r"$(\sigma_k^{t+1})^2 = \frac{1}{n_k} \sum_i \gamma_{ik}"
         r"(x_i - \mu_k^{t+1})^2$"),
    ]
    for i, (color, left, right) in enumerate(rows):
        y = 2.52 - i * 0.78
        ax.text(2.55, y, left, ha="center", va="center", color=color,
                fontsize=13)
        ax.text(6.45, y, right, ha="center", va="center", color=color,
                fontsize=13)
        arrow(ax, (4.30, y), (4.70, y), color=MUTED, lw=1.4)
    box(ax, 0.80, 0.10, 7.40, 0.44, GREEN, "", fill="#f1faf1")
    ax.text(W / 2, 0.32, r"The only change: $\mathbb{1}_{z_i = k}$ "
                         r"becomes $\gamma_{ik}$, and $n \hat{p}_k$ "
                         r"becomes $n_k = \gamma_{1k} + \cdots"
                         r"+ \gamma_{nk}$",
            ha="center", va="center", color=GREEN, fontsize=12.5)


@figure("em_run")
def em_run(fig):
    x = _animal_sample()
    p0 = np.array([0.5, 0.5])
    mu0 = np.array([87.5, 90.5])
    sd0 = np.array([3.0, 3.0])
    _, _, _, hist = _em1d(x, 2, 30, p=p0, mu=mu0, sd=sd0, trace=True)
    shown = [0, 1, 2, 4, 9, 30]
    grid = np.linspace(80, 99, 600)

    fig.text(0.5, 0.955, "Thirty passes on the animal lengths, from a "
                         "deliberately bad start", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    for i, t in enumerate(shown):
        row, col = divmod(i, 3)
        a = fig.add_axes([0.065 + col * 0.325, 0.55 - row * 0.40,
                          0.255, 0.25])
        pt, mt, st, ll = hist[t]
        a.hist(x, bins=np.arange(81.5, 99.5, 1.0), density=True, color=LIGHT,
               edgecolor="none")
        for k in range(2):
            a.plot(grid, pt[k] * _norm_pdf(grid, mt[k], st[k]),
                   color=COMP[k], lw=2.0)
        a.set_ylim(0, 0.16)
        a.set_xticks([])
        a.set_yticks([])
        despine(a)
        a.set_title(f"$t = {t}$" + r"$,\;\; \ell = $" + f"${ll:,.0f}$",
                    color=INK if t else MUTED, fontsize=11, pad=5)
    pf, mf, sf, llf = hist[-1]
    fig.text(0.5, 0.055, f"It lands on $p = ({pf[0]:.2f}, {pf[1]:.2f})$, "
                         f"$\\mu = ({mf[0]:.1f}, {mf[1]:.1f})$, "
                         f"$\\sigma = ({sf[0]:.1f}, {sf[1]:.1f})$ — the two "
                         f"regions, recovered without a single label.",
             ha="center", va="center", color=MUTED, fontsize=11)


@figure("em_run_2d")
def em_run_2d(fig):
    X, _ = _two_blobs(seed=3, n=300)
    S0 = np.eye(2) * 0.9
    start = (np.array([0.5, 0.5]),
             np.array([[-0.1, 0.9], [0.1, -0.9]]),
             np.array([S0, S0]))
    _, _, _, hist = _em2d(X, 2, 20, start=start, trace=True)
    shown = [0, 1, 4, 7, 9, 20]

    fig.text(0.5, 0.955, "Ellipses walk to the clusters", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    for i, t in enumerate(shown):
        row, col = divmod(i, 3)
        a = fig.add_axes([0.085 + col * 0.300, 0.52 - row * 0.40,
                          0.235, 0.29])
        pt, mt, St, ll = hist[t]
        g = _resp2d(X, pt, mt, St)
        a.scatter(X[:, 0], X[:, 1], c=[COMP[k] for k in g.argmax(1)], s=7,
                  edgecolors="none", alpha=0.8)
        for k in range(2):
            ellipse(a, mt[k], St[k], COMP[k], nsig=(1.0, 2.0), lw=1.5)
        a.set_xlim(-3.6, 3.6)
        a.set_ylim(-2.6, 2.8)
        a.set_aspect("equal")
        _bare(a)
        a.set_title(f"$t = {t}$" + r"$,\;\; \ell = $" + f"${ll:,.0f}$",
                    color=INK if t else MUTED, fontsize=10.5, pad=4)
    fig.text(0.5, 0.055, "Colours are the hard labels showing progress.",
             ha="center", va="center", color=MUTED, fontsize=11)


@figure("em_monotone")
def em_monotone(fig):
    x = _animal_sample()
    runs = []
    for mu0, tag, color in ((np.array([87.5, 90.5]), "a mediocre start", BLUE),
                            (np.array([84.0, 95.0]), "a good start", GOLD),
                            (np.array([89.0, 89.5]), "a symmetric start",
                             GREEN)):
        _, _, _, h = _em1d(x, 2, 40, p=np.array([0.5, 0.5]), mu=mu0.copy(),
                           sd=np.array([3.0, 3.0]), trace=True)
        runs.append((mu0, tag, color, np.array([r[3] for r in h])))

    # the best value reached, by a run long enough to settle: on a log
    # scale the distance to it shows the speed of convergence
    best = _em1d(x, 2, 400, p=np.array([0.5, 0.5]), mu=np.array([84.0, 95.0]),
                 sd=np.array([3.0, 3.0]), trace=True)[3][-1][3]

    fig.text(0.5, 0.955, "Every pass increases the observed log-likelihood",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.095, 0.21, 0.36, 0.59])
    # stop each curve where the gap reaches rounding level
    where = {"a symmetric start": (41, None), "a mediocre start": (None, 3e-9),
             "a good start": (1.5, 1e-6)}
    for mu0, tag, color, tr in runs:
        gap = best - tr
        keep = np.flatnonzero(gap > 1e-9)
        t_end = keep[-1] if len(keep) else 0
        ax.semilogy(np.arange(t_end + 1), gap[:t_end + 1], color=color, lw=2.2)
        tx, ty = where[tag]
        ax.text(t_end + 1 if tx is None else tx,
                gap[t_end] if ty is None else ty, tag, color=color,
                fontsize=10, va="center", ha="left")
    ax.set_xlim(-1, 40)
    ax.set_ylim(1e-9, 1e3)
    ax.set_yticks([1e-9, 1e-6, 1e-3, 1, 1e3])
    ax.set_xlabel("pass $t$")
    ax.set_ylabel(r"$\ell^\star - \ell_{\mathrm{obs}}(\theta^t)$")
    ax.text(17, 0.3, "$\\ell^\\star$: best value reached",
            color=MUTED, fontsize=9.5, va="center", linespacing=1.4)
    despine(ax, keep=("left", "bottom"))

    ax2 = canvas(fig)
    ax2.plot([5.45, 5.45], [0.40, 3.05], color=GRID, lw=1.2)
    column(ax2, 5.70, 3.02, 3.1, "Guaranteed", [
        r"$\ell_{\mathrm{obs}}(\theta^{t+1}) \geq "
        r"\ell_{\mathrm{obs}}(\theta^{t})$",
        "The sequence is bounded above",
        "Hence converges\nto a stationary point of $\\ell_{\\mathrm{obs}}$",
    ], GREEN, leading=0.30, item_size=11)
    column(ax2, 5.70, 1.26, 3.1, "Not guaranteed", [
        "The limit is the global maximum",
        "Can get stuck at a saddle (green run)",
    ], RED, leading=0.30, item_size=11)


@figure("em_cost")
def em_cost(fig):
    ax = canvas(fig)
    rows = [
        (BLUE, "E-step", r"$n K$ densities, then one division per entry",
         r"$\mathcal{O}(n K d^2)$", "the $d^2$ is the quadratic form"),
        (GREEN, "M-step", r"$K$ weighted means and covariances",
         r"$\mathcal{O}(n K d^2)$", "one pass over the data"),
        (GOLD, "memory", r"the $\gamma$ matrix", r"$\mathcal{O}(n K)$",
         ""),
        (PURPLE, "passes", "until the likelihood flattens",
         "usually ~tens", "fast at first, slow near the top"),
    ]
    x = (0.50, 2.00, 5.00, 6.60)
    for xi, head in zip(x, ("", "Work", "Cost", "Note")):
        ax.text(xi, 3.02, head, color=MUTED, fontsize=11.5, va="center")
    ax.plot([0.42, 8.58], [2.84, 2.84], color=GRID, lw=1.2)
    for i, (color, name, work, cost, note_) in enumerate(rows):
        y = 2.54 - i * 0.50
        ax.text(x[0], y, name, color=color, fontsize=12.5, weight="bold",
                va="center")
        ax.text(x[1], y, work, color=INK, fontsize=11.5, va="center")
        ax.text(x[2], y, cost, color=INK, fontsize=11.5, va="center")
        ax.text(x[3], y, note_, color=MUTED, fontsize=10.5, va="center")
        if i:
            ax.plot([0.42, 8.58], [y + 0.25, y + 0.25], color=LIGHT, lw=1.0)
    note(ax, "Linear in the sample size, so EM scales.", y=0.42, size=11.5)


# ==========================================================================
# 6. why it works
# ==========================================================================
def _elbo_toy():
    """A one-parameter caricature of the EM landscape: an observed
    log-likelihood L(t), and for each anchor the surrogate that touches it
    there and lies below it everywhere."""
    def L(t):
        return -0.55 * (t - 1.0) ** 2 + 0.22 * np.cos(2.1 * t) - 0.22

    def dL(t):
        return -1.10 * (t - 1.0) - 0.462 * np.sin(2.1 * t)

    c = 2.40                      # a curvature steep enough to minorize L

    def G(t, tb):
        d = t - tb
        return L(tb) + dL(tb) * d - c * d ** 2

    return L, dL, G


@figure("em_two_views")
def em_two_views(fig):
    ax = canvas(fig)
    # ax.text(W / 2, 3.55, "Two ways to see the very same algorithm",
    #         ha="center", va="center", color=MUTED, fontsize=12.5)
    box(ax, 0.45, 1.90, 3.90, 1.44, BLUE, "", fill="white")
    ax.text(2.40, 3.10, "As alternating estimation", ha="center",
            va="center", color=BLUE, fontsize=13, weight="bold")
    ax.text(2.40, 2.62, r"E: $\gamma \leftarrow$ labels, given $\theta$"
            "\n" r"M: $\theta \leftarrow$ parameters, given $\gamma$",
            ha="center", va="center", color=INK, fontsize=11.5,
            linespacing=1.8)
    ax.text(2.40, 2.10, "interpretation so far", ha="center", va="center",
            color=MUTED, fontsize=10.5)

    box(ax, 4.65, 1.90, 3.90, 1.44, GREEN, "", fill="white")
    ax.text(6.60, 3.10, "As one function, maximised twice", ha="center",
            va="center", color=GREEN, fontsize=13, weight="bold")
    ax.text(6.60, 2.62, r"$F(\theta, q) = E_q[\ell(\theta; x, z)]"
                        r" - E_q[\log q(z)]$"
            "\n" r"E: $\max_q F$. $\quad$ M: $\max_{\theta} F$",
            ha="center", va="center", color=INK, fontsize=11.5,
            linespacing=1.8)
    ax.text(6.60, 2.10, "view for the proof", ha="center", va="center",
            color=MUTED, fontsize=10.5)

    column(ax, 0.45, 1.7, 8.2, "Used for the proof:", [
        r"$q$ is any distribution over the latent labels, not just the posterior",
        r"$F(\theta, q) \leq \ell_{\mathrm{obs}}(\theta)$ always, with "
        r"equality exactly at $q(z) = P(z \mid x, \theta)$",
        r"Increasing $F$ increases $\ell_{\mathrm{obs}}$",
        r"$F$ is separable, unlike $\ell_{\mathrm{obs}}$",
    ], INK, leading=0.32, item_size=11.5)


def _derivation(ax, rows, top, gap, x=0.45, why_x=5.45, eq_size=12.5):
    """Steps of a derivation, with the reason for each step in a grey column
    on the right, level with its equation."""
    ax.plot([why_x - 0.22] * 2, [top - (len(rows) - 1) * gap - 0.25,
                                 top + 0.25], color=LIGHT, lw=1.2)
    for i, row in enumerate(rows):
        eq, why = row[0], row[1]
        color = row[2] if len(row) > 2 else INK
        y = top - i * gap
        ax.text(x, y, eq, color=color, fontsize=eq_size, va="center")
        ax.text(why_x, y, why, color=MUTED, fontsize=10.5, va="center",
                linespacing=1.35)


@figure("eq_elbo")
def eq_elbo(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "An exact identity, true for any distribution $q$ "
                         "over the labels: no inequality yet",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    _derivation(ax, [
        (r"$\ell_{\mathrm{obs}}(\theta) = \log f(x \mid \theta)$",
         "observed log-likelihood:\ndoes not depend on $z$"),
        (r"$\ell_{\mathrm{obs}}(\theta) = \log f(x, z \mid \theta) - "
         r"\log P(z \mid x, \theta)$",
         "Bayes' rule, $f(x \\mid \\theta) = f(x, z \\mid \\theta)\\,/\\,"
         "P(z \\mid x, \\theta)$"),
        (r"$\ell_{\mathrm{obs}}(\theta) = \sum_z q(z) \log f(x, z \mid \theta)"
         r"\; - \;\sum_z q(z) \log P(z \mid x, \theta)$",
         "average over $z$ with weights $q(z)$,\n"
         "$q$ sums to 1"),
        (r"$\ell_{\mathrm{obs}}(\theta) = \sum_z q(z) \log "
         r"\frac{f(x, z \mid \theta)}{q(z)}"
         r"\; + \;\sum_z q(z) \log \frac{q(z)}{P(z \mid x, \theta)}$",
         "subtract and add the average of $\\log q(z)$"),
        (r"$\ell_{\mathrm{obs}}(\theta) = F(\theta, q) \; + \;"
         r"\mathrm{KL}\!\left( q \,\|\, P(\cdot \mid x, \theta) \right)$",
         "Identify $F$ and Kullback-Leibler divergence",
         GREEN),
    ], top=3.08, gap=0.63)
    # note(ax, "$F$ is the lecture's $F$, the ELBO of the Bayesian literature.",
    #      y=0.18, size=11.5)


@figure("eq_elbo_gap")
def eq_elbo_gap(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"$\ell_{\mathrm{obs}}(\theta) = F(\theta, q) + "
                         r"\mathrm{KL}(q \,\|\, P(\cdot \mid x, \theta))$",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    _derivation(ax, [
        (r"$-\mathrm{KL} = \sum_z q(z) \log \frac{P(z \mid x, \theta)}{q(z)}"
         r"\;\leq\; \log \sum_z P(z \mid x, \theta) = 0$",
         "Jensen (log is concave),\n$q(z)$ cancel & probas sum to 1",
         BLUE),
        (r"$\mathrm{KL} \geq 0$, $\mathrm{KL} = 0$ only when "
         r"$q(z) = P(z \mid x, \theta)$",
         "$F(\\theta, q) \\leq \\ell_{\\mathrm{obs}}(\\theta)$,"
         "\nwith equality exactly at the posterior", BLUE),
        (r"$F(\theta, q) = E_q[\log f(x, z \mid \theta)] \;-\; "
         r"E_q[\log q(z)]$",
         "expected complete log-likelihood,\nplus the entropy of $q$"),
        (r"$F(\theta, q) = \sum_i \sum_k q_{ik} \left( "
         r"\log p_k f_k(x_i) - \log q_{ik} \right)$",
         "expressed as a double sum\nPreviously: $q_{ik} = \\gamma_{ik}$", GREEN),
    ], top=3.05, gap=0.68)
    box(ax, 0.80, 0.1, 7.40, 0.40, GREEN, "", fill="#f1faf1")
    ax.text(W / 2, 0.3, r"EM optimize $F$ over $q$ (E-step) & over $\theta$ (M-step)",
            ha="center", va="center", color=GREEN, fontsize=12)


@figure("jensen_step")
def jensen_step(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"$\log$ is concave:$\quad \log\!\left( \sum_z q(z)\, u(z) "
         r"\right) \;\geq\; \sum_z q(z) \log u(z)$",
         "the log of an average is at least the average of the logs"),
        (r"$\ell_{\mathrm{obs}}(\theta) = \log \sum_z q(z)\,"
         r"\frac{f(x, z \mid \theta)}{q(z)}"
         r"\;\geq\; \sum_z q(z) \log \frac{f(x, z \mid \theta)}{q(z)}$",
         r"with $u(z) = f(x, z \mid \theta) / q(z)$", GREEN),
        (r"$\ell_{\mathrm{obs}}(\theta) \;\geq\; F(\theta, q)$", 
         "With equality when $f(x, z \\mid \\theta) / q(z)$ does not depend on $z$\ni.e. when $q$ is the posterior."),
    ], top=3.50, gap=0.90, x=0.45, eq_size=15, why_off=0.30)
    box(ax, 0.80, 0.12, 7.40, 0.44, BLUE, "", fill="white", lw=1.5)
    ax.text(W / 2, 0.34, "$\\ell_{\\mathrm{obs}}(\\theta) = F(\\theta, q)$ when $q$ is the posterior",
            ha="center", va="center", color=BLUE, fontsize=12)


@figure("jensen_picture")
def jensen_picture(fig):
    u = np.linspace(0.25, 6.2, 400)
    pts = np.array([0.6, 5.4])
    w = np.array([0.55, 0.45])
    ub = float((w * pts).sum())

    fig.text(0.5, 0.955, "A concave function sits above its chords",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.085, 0.20, 0.42, 0.60])
    ax.plot(u, np.log(u), color=INK, lw=2.4, zorder=3)
    ax.plot(pts, np.log(pts), color=GOLD, lw=2.0, zorder=2)
    ax.plot(pts, np.log(pts), "o", color=GOLD, ms=6, zorder=4)
    ax.plot([ub, ub], [float((w * np.log(pts)).sum()), float(np.log(ub))],
            color=RED, lw=2.2, zorder=4)
    ax.plot(ub, np.log(ub), "o", color=GREEN, ms=7, zorder=5)
    ax.plot(ub, float((w * np.log(pts)).sum()), "o", color=RED, ms=7,
            zorder=5)
    ax.annotate(r"$\log E[u]$", xy=(ub, np.log(ub)),
                xytext=(ub + 0.25, np.log(ub) + 0.42), color=GREEN,
                fontsize=11.5,
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.3))
    ax.annotate(r"$E[\log u]$", xy=(ub, float((w * np.log(pts)).sum())),
                xytext=(ub + 0.25, float((w * np.log(pts)).sum()) - 0.55),
                color=RED, fontsize=11.5,
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.3))
    ax.set_xlabel("$u$")
    ax.set_ylabel(r"$\log u$")
    ax.set_ylim(-1.5, 2.3)
    despine(ax, keep=("left", "bottom"))

    ax2 = canvas(fig)
    ax2.plot([5.10, 5.10], [0.45, 3.05], color=GRID, lw=1.2)
    column(ax2, 5.35, 3.02, 3.4, "$\\log E[u] \\geq E[\\log u]$", [
        r"applied with $u(z) = f(x, z \mid \theta) / q(z)$",
        r"average is over $z \sim q$",
        "chord degenerates to a point\nwhen $u$ is constant in $z$",
    ], GREEN, leading=0.30, item_size=11)


@figure("elbo_estep")
def elbo_estep(fig):
    L, dL, G = _elbo_toy()
    t = np.linspace(-0.9, 3.0, 500)
    tb = -0.50

    fig.text(0.5, 0.955, r"Close the gap: with $\theta$ fixed, lift the bound "
                         r"until it touches", ha="center", va="center",
             color=BLUE, fontsize=12.5)
    ax = fig.add_axes([0.085, 0.20, 0.47, 0.60])
    ax.plot(t, L(t), color=INK, lw=2.4, zorder=4,
            label=r"$\ell_{\mathrm{obs}}(\theta)$")
    for drop, color, ls, lab in (
            (0.0, BLUE, "--", r"$F(\theta, q)$, $q = P(z \mid x, \theta^t)$:"
                              " touches at $\\theta^t$"),
            (0.70, MUTED, ":", r"$F(\theta, q)$, a worse $q$: stays below")):
        ax.plot(t, G(t, tb) - drop, color=color, lw=1.8, ls=ls, zorder=3,
                label=lab)
    ax.plot(tb, L(tb), "o", color=BLUE, ms=8, zorder=5)
    ax.annotate("", xy=(tb, L(tb) - 0.04), xytext=(tb, L(tb) - 0.70),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2.0))
    ax.legend(loc="upper right", bbox_to_anchor=(1.02, 1.04), fontsize=10,
              handlelength=2.2)
    ax.axvline(tb, color=GRID, lw=1.0, ls=":")
    ax.text(tb, -2.45, r"$\theta^t$", color=BLUE, fontsize=12, ha="center",
            va="bottom")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel(r"$\theta$")
    ax.set_ylim(-2.5, 1.55)
    despine(ax, keep=("bottom",))

    ax2 = canvas(fig)
    ax2.plot([5.45, 5.45], [0.45, 3.05], color=GRID, lw=1.2)
    column(ax2, 5.70, 3.02, 3.1, "E-step:", [
        r"moves $q$ (not $\theta$)",
        r"$\max_q F(\theta^t, q)$ is reached at the" "\n"
        r"posterior $P(z \mid x, \theta^t)$",
        r"the KL gap is zero, so" "\n"
        r"$F(\theta^t, q) = \ell_{\mathrm{obs}}(\theta^t)$",
    ], BLUE, leading=0.30, item_size=11)
    ax2.text(5.70, 1.04, "In Gaussian mixture, that posterior\nis "
                         r"the table $\gamma_{ik}$.", color=INK,
             fontsize=11, va="center", linespacing=1.5)


@figure("elbo_mstep")
def elbo_mstep(fig):
    L, dL, G = _elbo_toy()
    t = np.linspace(-0.9, 3.0, 500)
    tb = -0.50
    tn = float(t[np.argmax(G(t, tb))])

    fig.text(0.5, 0.955, r"Push the bound up: with $q$ fixed, climb the bound",
             ha="center", va="center", color=GREEN, fontsize=12.5)
    ax = fig.add_axes([0.085, 0.20, 0.47, 0.60])
    ax.plot(t, L(t), color=INK, lw=2.4, zorder=4,
            label=r"$\ell_{\mathrm{obs}}(\theta)$")
    ax.plot(t, G(t, tb), color=BLUE, lw=1.8, ls="--", zorder=3,
            label=r"bound $F(\theta, q)$")
    ax.plot(tb, L(tb), "o", color=BLUE, ms=8, zorder=5,
            label=r"start $\ell_{\mathrm{obs}}(\theta^t)$")
    ax.plot(tn, G(tn, tb), "o", color=GREEN, ms=8, zorder=5,
            label="top of the bound")
    ax.plot(tn, L(tn), "o", color=INK, ms=8, zorder=5,
            label=r"new $\ell_{\mathrm{obs}}(\theta^{t+1})$")
    ax.legend(loc="upper right", bbox_to_anchor=(1.02, 1.04), fontsize=10,
              handlelength=1.8, ncol=2, columnspacing=1.2)
    ax.annotate("", xy=(tn, G(tn, tb)), xytext=(tb, L(tb)),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.0))
    ax.annotate("", xy=(tn, L(tn) - 0.03), xytext=(tn, G(tn, tb) + 0.03),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6))
    for tt, lab, color in ((tb, r"$\theta^t$", BLUE),
                           (tn, r"$\theta^{t+1}$", GREEN)):
        ax.axvline(tt, color=GRID, lw=1.0, ls=":")
        ax.text(tt, -2.45, lab, color=color, fontsize=12, ha="center",
                va="bottom")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel(r"$\theta$")
    ax.set_ylim(-2.5, 1.55)
    despine(ax, keep=("bottom",))

    ax2 = canvas(fig)
    ax2.plot([5.45, 5.45], [0.45, 3.05], color=GRID, lw=1.2)
    column(ax2, 5.70, 3.02, 3.1, "M-step", [
        r"moves $\theta$, never $q$",
        r"$\theta^{t+1} = \arg\max_\theta F(\theta, q)$" "\n"
        r"$F$ is separable, so there is a closed form",
    ], GREEN, leading=0.30, item_size=11)
    ax2.text(5.70, 1.00, r"$E_q[\log q]$ does not involve $\theta$"
                         "\n" r"maximising $F$ is maximising "
                         r"$E_q[\ell(\theta; x, z)]$.",
             color=INK, fontsize=11, va="center", linespacing=1.5)


@figure("mm_picture")
def mm_picture(fig):
    L, dL, G = _elbo_toy()
    t = np.linspace(-0.9, 3.0, 600)

    # fig.text(0.5, 0.955, "Repeat: touch, climb, touch again — a staircase "
    #                      "that never descends", ha="center", va="center",
    #          color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.075, 0.20, 0.52, 0.60])
    ax.plot(t, L(t), color=INK, lw=2.6, zorder=4)
    ax.text(2.55, L(2.55) + 0.22, r"$\ell_{\mathrm{obs}}$", color=INK,
            fontsize=13, ha="center", va="bottom")
    tb = -0.75
    for step, color in enumerate((BLUE, GOLD, GREEN)):
        g = G(t, tb)
        assert (g <= L(t) + 1e-9).all()
        tn = float(t[np.argmax(g)])
        near = np.abs(t - tb) < 0.85
        ax.plot(t[near], g[near], color=color, lw=1.6, ls="--", zorder=3)
        ax.plot(tb, L(tb), "o", color=color, ms=7, zorder=5)
        ax.annotate("", xy=(tn, G(tn, tb)), xytext=(tb, L(tb)),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8))
        if step == 0:
            ax.text(0.45, -1.55, "each dashed curve is\n"
                                 r"$F(\cdot, q^t)$: one per pass",
                    color=color, fontsize=11, ha="left", va="top",
                    linespacing=1.5)
        tb = tn
    ax.plot(tb, L(tb), "o", color=GREEN, ms=7, zorder=5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel(r"$\theta$")
    ax.set_ylim(-2.5, 0.6)
    despine(ax, keep=("bottom",))

    ax2 = canvas(fig)
    ax2.plot([5.60, 5.60], [0.45, 3.05], color=GRID, lw=1.2)
    ax2.text(5.85, 3.02, "Minorize, then maximize", color=INK, fontsize=14,
             weight="bold", va="top")
    ax2.text(5.85, 2.52, "Minorize", color=BLUE, fontsize=12.5,
             weight="bold", va="center")
    ax2.text(5.85, 2.16, r"build $F(\theta, q^t) \leq "
                         r"\ell_{\mathrm{obs}}(\theta)$" "\n"
                         r"touching at $\theta^t$ (the E-step)",
             color=INK, fontsize=11, va="center", linespacing=1.6)
    ax2.text(5.85, 1.58, "Maximize", color=GREEN, fontsize=12.5,
             weight="bold", va="center")
    ax2.text(5.85, 1.22, r"$\theta^{t+1} = \arg\max_\theta "
                         r"F(\theta, q^t)$" "\n"
                         "then start again (the M-step)",
             color=INK, fontsize=11, va="center", linespacing=1.6)


@figure("eq_em_monotone")
def eq_em_monotone(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"$\ell_{\mathrm{obs}}(\theta^{t}) = F(\theta^{t}, q^{t})$",
         r"the E-step chose $q^t = P(z \mid x, \theta^t)$, which closes "
         r"the KL gap", BLUE),
        (r"$F(\theta^{t}, q^{t}) \;\leq\; F(\theta^{t+1}, q^{t})$",
         r"the M-step maximised $F(\cdot, q^t)$, and $\theta^t$ was one "
         r"candidate", GREEN),
        (r"$F(\theta^{t+1}, q^{t}) \;\leq\; "
         r"\ell_{\mathrm{obs}}(\theta^{t+1})$",
         r"$F$ is a lower bound for every $\theta$, touching or not",
         GOLD),
    ], top=3.30, gap=0.78, x=0.90, eq_size=15, why_off=0.33)
    box(ax, 0.80, 0.22, 7.40, 0.52, INK, "", fill="white", lw=1.6)
    ax.text(W / 2, 0.48, r"$\ell_{\mathrm{obs}}(\theta^{t}) \;\leq\; "
                         r"\ell_{\mathrm{obs}}(\theta^{t+1})$"
                         r"$\qquad \forall t$",
            ha="center", va="center", color=INK, fontsize=14)


@figure("eq_q_function")
def eq_q_function(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"The E-step, written as an expectation",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$Q(\theta, \theta^{t}) \;=\; E\!\left[ \ell(\theta; x, Z) "
         r"\mid x, \theta^{t} \right]$",
         r"average the complete-data log-likelihood over the unknown "
         r"labels"),
        (r"$Q(\theta, \theta^{t}) = \sum_i \sum_k "
         r"P(Z = k \mid x_i, \theta^{t}) \, \log( p_k f_k(x_i) )"
         r"\;=\; \sum_i \sum_k \gamma_{ik} \log( p_k f_k(x_i) )$",
         "because the complete-data log-likelihood is linear in the "
         r"indicators $\mathbb{1}_{Z_i = k}$", BLUE),
        (r"$\log(p_k f_k(x_i)) = \log p_k + \log f_k(x_i)$",
         r"so $Q$ splits: the weights on one side, each component on its "
         r"own on the other", GREEN),
    ], top=3.00, gap=0.78, x=0.45, eq_size=12.5, why_off=0.30)
    box(ax, 0.80, 0.14, 7.40, 0.46, GREEN, "", fill="#f1faf1")
    ax.text(W / 2, 0.37, "Separable — which is exactly what the "
                         "log-of-a-sum destroyed",
            ha="center", va="center", color=GREEN, fontsize=12.5)


@figure("eq_mstep_derivation")
def eq_mstep_derivation(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"Three independent problems",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$\max_{p} \; \sum_i \sum_k \gamma_{ik} \log p_k$"
         r"$\quad$ subject to $\;p_1 + \cdots + p_K = 1$",
         r"a Lagrange multiplier gives $p_k = n_k / n$ with "
         r"$n_k = \sum_i \gamma_{ik}$", PURPLE),
        (r"$\max_{\mu_k} \; -\frac{1}{2\sigma_k^2} \sum_i \gamma_{ik} "
         r"(x_i - \mu_k)^2$",
         r"a weighted least squares: $\mu_k = (1/n_k) \sum_i \gamma_{ik} "
         r"x_i$", BLUE),
        (r"$\max_{\sigma_k} \; -\sum_i \gamma_{ik} \left( \log \sigma_k"
         r"+ \frac{(x_i - \mu_k)^2}{2 \sigma_k^2} \right)$",
         r"set the derivative to zero: $\sigma_k^2 = (1/n_k) \sum_i "
         r"\gamma_{ik} (x_i - \mu_k)^2$", GOLD),
    ], top=3.00, gap=1, x=0.45, eq_size=16, why_off=0.34)
    # note(ax, "Each line is the ordinary single-Gaussian calculation, with "
    #          r"$\gamma_{ik}$ as a weight.",
    #      y=0.50, size=11.5)


@figure("em_convergence")
def em_convergence(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "What the proof does and does not promise",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    column(ax, 0.55, 3.10, 3.9, "Guaranteed", [
        r"$\ell_{\mathrm{obs}}(\theta^t)$ increases at every pass",
        "limit points are stationary points of $\\ell_{\\mathrm{obs}}$",
        "no step size, no divergence, no tuning",
    ], GREEN, leading=0.30, item_size=11)
    column(ax, 4.90, 3.10, 3.9, "Not guaranteed", [
        "global maximum (only local maximum)",
        "point of convergence depend in initialization",
        "no finite limit: $\\sigma_k \\to 0$ makes to $\\ell_{\\mathrm{obs}} \\to +\\infty$",
    ], RED, leading=0.30, item_size=11)
    ax.plot([4.65, 4.65], [0.70, 3.16], color=GRID, lw=1.2)
    note(ax, "In practice: use several random starts, keep the best $\\ell_{\\mathrm{obs}}$.", y=0.38, size=11.5)


# ==========================================================================
# 7. relatives of EM
# ==========================================================================
@figure("hard_em")
def hard_em(fig):
    ax = canvas(fig)
    # ax.text(W / 2, 3.52, "What if we committed to a label?",
    #         ha="center", va="center", color=MUTED, fontsize=12.5)
    rows = [
        (GREEN, "EM", r"keep $\gamma_{ik}$, weight by it",
         "the expectation itself", "monotone, smooth"),
        (BLUE, "Classification EM", r"$z_i = \arg\max_k \gamma_{ik}$",
         "the most likely label", "equivalent to $k$-means"),
        (GOLD, "SEM (Stochastic)", r"draw $z_i \sim \gamma_{i\cdot}$",
         "one random label", "escapes saddles, noisy"),
        (PURPLE, r"$N$-SEM", r"draw $N$ labels per point",
         r"$N$ random labels", r"EM is the limit $N \to \infty$"),
    ]
    x = (0.50, 3.00, 5.20, 6.70)
    for xi, head in zip(x, ("Variant", "What replaces $z_i$",
                            "Information kept", "Character")):
        ax.text(xi, 3.04, head, color=MUTED, fontsize=11.5, va="center")
    ax.plot([0.42, 8.58], [2.86, 2.86], color=GRID, lw=1.2)
    for i, (color, name, what, info, char) in enumerate(rows):
        y = 2.56 - i * 0.52
        ax.text(x[0], y, name, color=color, fontsize=12, weight="bold",
                va="center")
        ax.text(x[1], y, what, color=INK, fontsize=11.5, va="center")
        ax.text(x[2], y, info, color=INK, fontsize=11, va="center")
        ax.text(x[3], y, char, color=MUTED, fontsize=10.5, va="center")
        if i:
            ax.plot([0.42, 8.58], [y + 0.26, y + 0.26], color=LIGHT, lw=1.0)
    note(ax, "All four share the M-step", y=0.15, size=12)


@figure("eq_kmeans_limit")
def eq_kmeans_limit(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"assume $p_1 = \cdots = p_K = 1/K$ and $\sigma_1 = \cdots "
         r"= \sigma_K = \sigma$",
         "equal weights, equal widths"),
        (r"$\gamma_{ik} \;=\; \frac{\exp\!\left( -\|x_i - \mu_k\|^2 / "
         r"(2\sigma^2) \right)}{\sum_l \exp\!\left( -\|x_i - \mu_l\|^2 / "
         r"(2\sigma^2) \right)}$",
         "normalising constants cancel, and only distances survive",
         BLUE),
        (r"$\sigma \to 0$:$\quad \gamma_{ik} \to 1$ for the nearest "
         r"centre, $0$ for the rest",
         r"softmax at temperature $\sigma^2$ is arg min",
         GOLD),
        (r"$\arg\max_k \gamma_{ik} = \arg\min_k \|x_i - \mu_k\|^2$,"
         r"$\qquad \mu_k \leftarrow$ mean of its points",
         r"same steps as $k$-means", GREEN),
    ], top=3.5, gap=0.7, x=0.45, eq_size=13, why_off=0.28)
    box(ax, 0.80, 0.14, 7.40, 0.40, GREEN, "", fill="#f1faf1")
    ax.text(W / 2, 0.34, "$k$-means is EM with hard assignment & spherical, equal, vanishing covariances",
            ha="center", va="center", color=GREEN, fontsize=12.5)


@figure("kmeans_vs_gmm")
def kmeans_vs_gmm(fig):
    X, _ = _two_blobs(seed=3, n=280)
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=2, n_init=10, random_state=0).fit(X)
    p, mus, Ss = _em2d(X, 2, 120, seed=2)
    # name the mixture components after the nearest k-means centre, so the
    # two panels use the same colour for the same cluster
    if (np.linalg.norm(mus[0] - km.cluster_centers_[0])
            > np.linalg.norm(mus[0] - km.cluster_centers_[1])):
        p, mus, Ss = p[::-1], mus[::-1], Ss[::-1]
    zg = _resp2d(X, p, mus, Ss).argmax(1)
    zk = km.labels_
    # draw the two boundaries on the same grid
    gx, gy = np.meshgrid(np.linspace(-3.6, 3.6, 300),
                         np.linspace(-2.8, 2.8, 300))
    G = np.c_[gx.ravel(), gy.ravel()]
    bk = (((G - km.cluster_centers_[0]) ** 2).sum(1)
          - ((G - km.cluster_centers_[1]) ** 2).sum(1)).reshape(gx.shape)
    bg = (_resp2d(G, p, mus, Ss)[:, 0] - 0.5).reshape(gx.shape)
    # only draw the boundary where there is any data to separate
    dens = sum(pk * _mvn_pdf(G, mk, Sk)
               for pk, mk, Sk in zip(p, mus, Ss)).reshape(gx.shape)
    bg = np.where(dens > 0.005 * dens.max(), bg, np.nan)

    fig.text(0.5, 0.955, "Same data, same $K$", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    axes = panels(fig, 2, titles=[r"$k$-means", "Gaussian mixture"],
                  colors=[RED, GREEN],
                  gridspec_kw=dict(left=0.07, right=0.62, top=0.80,
                                   bottom=0.18, wspace=0.14))
    for ax, z, b, lv in ((axes[0], zk, bk, 0.0), (axes[1], zg, bg, 0.0)):
        ax.scatter(X[:, 0], X[:, 1], c=[COMP[k] for k in z], s=16,
                   edgecolors="none", alpha=0.85)
        ax.contour(gx, gy, b, levels=[lv], colors=[INK], linewidths=1.8)
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-2.8, 2.8)
        ax.set_aspect("equal")
        _bare(ax)
    axes[0].plot(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1], "x",
                 color=INK, ms=9, mew=2.2)
    for k in range(2):
        ellipse(axes[1], mus[k], Ss[k], COMP[k], nsig=(1.0, 2.0), lw=1.4)

    ax = canvas(fig)
    ax.plot([5.85, 5.85], [0.45, 3.05], color=GRID, lw=1.2)
    column(ax, 6.10, 3.02, 2.7, "GMM gives", [
        "a shape per cluster,\nnot just a centre",
        "a probability, not an assignment",
    ], GREEN, leading=0.30, item_size=10.5)
    agree = float((zk == zg).mean())
    agree = max(agree, 1 - agree)
    ax.text(6.10, 0.74, f"the two labellings agree on "
                        f"{100 * agree:.0f}% of the\n"
                        f"{len(X)} points.", color=MUTED, fontsize=10.5,
            va="center", linespacing=1.5)


@figure("sem_algorithm")
def sem_algorithm(fig):
    ax = canvas(fig)
    lines = [
        (BLUE, "init", r"labels $z_1, \ldots, z_n$ at random"),
        (INK, "repeat", r"M: $\hat{\theta} = \arg\max_\theta \; "
                        r"\ell\left[(x_1, z_1), \ldots, (x_n, z_n); "
                        r"\theta\right]$"),
        (INK, "", r"$\quad$ the complete-data MLE (count and average)"),
        (INK, "", r"S: for each $i$, draw $z_i \sim "
                  r"P_{\hat{\theta}}(Z \mid X_i = x_i)$"),
        (INK, "", r"$\quad$ a draw, not an arg max and not an average"),
        (GOLD, "until", "the parameters stop drifting"),
    ]
    box(ax, 0.50, 1.37, 8.00, 2.1, GOLD, "", fill="white", lw=1.6)
    for i, (color, key, text) in enumerate(lines):
        y = 3.25 - i * 0.345
        ax.text(1.45, y, key, ha="right", va="center", color=color,
                fontsize=12, weight="bold" if key else "normal")
        ax.text(1.62, y, text, ha="left", va="center", color=INK,
                fontsize=11.5)
    column(ax, 0.50, 1.00, 3.9, "Pros", [
        "can \"jump out of a bad basin\"",
        "easy to implement",
    ], GREEN, leading=0.28, item_size=11)
    column(ax, 4.75, 1.00, 3.9, "Cons", [
        "likelihood no longer climbsmonotonically",
        r"it never fully converges: $\theta^t$ wanders",
    ], RED, leading=0.28, item_size=11)


@figure("sem_run")
def sem_run(fig):
    x = _animal_sample()
    p0 = np.array([0.5, 0.5])
    mu0 = np.array([87.5, 90.5])
    sd0 = np.array([3.0, 3.0])
    _, _, _, hist = _sem1d(x, 2, 40, seed=5, p=p0.copy(), mu=mu0.copy(),
                           sd=sd0.copy(), trace=True)
    shown = [0, 1, 5, 10, 15, 40]
    grid = np.linspace(80, 99, 600)

    fig.text(0.5, 0.955, "Stochastic EM on the same data: it finds the two "
                         "modes, then keeps jittering", ha="center",
             va="center", color=MUTED, fontsize=12.5)
    for i, t in enumerate(shown):
        row, col = divmod(i, 3)
        a = fig.add_axes([0.065 + col * 0.325, 0.55 - row * 0.40,
                          0.255, 0.25])
        pt, mt, st, zt, ll = hist[t]
        if zt is None:
            a.hist(x, bins=np.arange(81.5, 99.5, 1.0), color=LIGHT,
                   edgecolor="none", density=True)
        else:
            a.hist([x[zt == 0], x[zt == 1]], bins=np.arange(81.5, 99.5, 1.0),
                   stacked=True, density=True, color=[COMP[0], COMP[1]],
                   alpha=0.6)
        for k in range(2):
            a.plot(grid, pt[k] * _norm_pdf(grid, mt[k], st[k]),
                   color=COMP[k], lw=2.0)
        a.set_ylim(0, 0.16)
        a.set_xticks([])
        a.set_yticks([])
        despine(a)
        a.set_title(f"$t = {t}$" + r"$,\;\; \ell = $" + f"${ll:,.0f}$",
                    color=INK if t else MUTED, fontsize=11, pad=5)
    lls = np.array([h[4] for h in hist[25:]])
    fig.text(0.5, 0.055, f"Colours are the drawn labels, redrawn every pass. "
                         f"Past pass 25 the log-likelihood still rattles in "
                         f"$[{lls.min():,.1f}, {lls.max():,.1f}]$ instead of "
                         f"settling.",
             ha="center", va="center", color=MUTED, fontsize=10.5)


@figure("nsem_idea")
def nsem_idea(fig):
    ax = canvas(fig)
    cards = [
        (0.45, BLUE, r"$N = 1$", "one label per point,\ndrawn at random",
         "stochastic, noisy"),
        (3.30, GOLD, r"$N$ draws", "replicate the sample $N$\ntimes, draw "
         "a label in each", "noise averages out"),
        (6.15, GREEN, r"$N \to \infty$", "the average over draws\n"
         "becomes an expectation", "original EM"),
    ]
    for xx, color, head, body, out in cards:
        box(ax, xx, 1.92, 2.40, 1.50, color, "", fill="white")
        ax.text(xx + 1.20, 3.12, head, ha="center", va="center", color=color,
                fontsize=14, weight="bold")
        ax.text(xx + 1.20, 2.62, body, ha="center", va="center", color=INK,
                fontsize=10.5, linespacing=1.5)
        ax.text(xx + 1.20, 2.16, out, ha="center", va="center", color=color,
                fontsize=11)
    arrow(ax, (2.95, 2.67), (3.20, 2.67), color=MUTED)
    arrow(ax, (5.80, 2.67), (6.05, 2.67), color=MUTED)
    ax.text(W / 2, 1.18, r"$\frac{1}{N} \sum_{j=1}^{N} \ell\left[ (x_i, "
                         r"z_i^j)_i ; \theta \right] \;\longrightarrow\; "
                         r"E\left[ \ell\left[ (x_i, Z_i)_i; \theta \right] \right]$",
            ha="center", va="center", color=INK, fontsize=15)
    note(ax, "Law of large numbers over independent draws:\n"
             "randomness disappears and expectation is reached.", y=0.40,
         size=11.5)


@figure("em_variants")
def em_variants(fig):
    x = _animal_sample()
    p0, mu0, sd0 = np.array([0.5, 0.5]), np.array([87.5, 90.5]), \
        np.array([3.0, 3.0])
    T = 60
    start = dict(p=p0, mu=mu0, sd=sd0, trace=True)
    runs = [(GREEN, "EM", [r[3] for r in _em1d(x, 2, T, **start)[3]])]
    runs.append((BLUE, r"hard ($k$-means)",
                 [r[4] for r in _sem1d(x, 2, T, seed=5, hard=True,
                                       **start)[3]]))
    for N, color in ((1, GOLD), (5, PURPLE), (25, RED)):
        name = "SEM ($N = 1$)" if N == 1 else f"$N$-SEM ($N = {N}$)"
        runs.append((color, name, [r[4] for r in _sem1d(
            x, 2, T, seed=5, N=N, **start)[3]]))

    fig.text(0.5, 0.955, "Same data, same start: more draws per point, "
                         "less noise, and $N$-SEM tends to EM",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    # distance to the best fit (EM's), on a log scale: the climb, the level
    # where each method stops and the size of its noise all show at once
    best = max(max(tr) for _, _, tr in runs)
    floor = 1e-4
    ax = fig.add_axes([0.085, 0.20, 0.66, 0.62])
    for i, (color, name, tr) in enumerate(runs):
        gap = best - np.array(tr)
        # stop a curve once it reaches the floor: EM gets there and stays
        under = np.flatnonzero(gap < floor)
        end = under[0] + 1 if len(under) else len(gap)
        gap = np.maximum(gap[:end], floor)
        ax.semilogy(np.arange(end), gap, color=color,
                    lw=2.4 if i == 0 else 1.7, label=name,
                    zorder=5 if i == 0 else 3)
    ax.set_ylim(floor * 0.7, 200)
    ax.set_xlim(-1, T)
    ax.set_xlabel("pass $t$")
    ax.set_ylabel(r"$\ell^\star - \ell_{\mathrm{obs}}(\theta^t)$")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=10.5,
              handlelength=1.8)
    despine(ax, keep=("left", "bottom"))
    fig.text(0.775, 0.30, "$\\ell^\\star$: the best fit, found by EM\n"
                          "hard: stops about 0.85 below\n"
                          "SEM keeps jumping;\n$N$-SEM less so as $N$ grows",
             color=MUTED, fontsize=10, va="center", linespacing=1.5)


# ==========================================================================
# 8. using a Gaussian mixture
# ==========================================================================
@figure("init_strategies")
def init_strategies(fig):
    ax = canvas(fig)
    # ax.text(W / 2, 3.52, "The answer you get is the answer your start led to",
    #         ha="center", va="center", color=MUTED, fontsize=12.5)
    rows = [
        (RED, "all components equal", "stuck: already a (bad) fixed point"),
        (GOLD, r"$K$ points drawn at random", "cheap honest start; keep the best"),
        (GREEN, r"$k$-means", "usual default: centroids become $\\mu_k$, clusters give $p_k$ and $\\Sigma_k$"),
        (BLUE, "previous fit", r"good 'warm start' when $K$/data changes"),
        # (PURPLE, "many random starts", r"keep the one with the highest $\ell_{\mathrm{obs}}$"),
    ]
    for i, (color, name, why) in enumerate(rows):
        y = 2.95 - i * 0.56
        ax.text(3.05, y, name, ha="right", va="center", color=color,
                fontsize=12.5, weight="bold")
        ax.text(3.25, y, why, ha="left", va="center", color=INK,
                fontsize=11)
        if i:
            ax.plot([0.45, 8.55], [y + 0.28, y + 0.28], color=LIGHT, lw=1.0)
    note(ax, "Avoid symmetric start and zero variance.",
         y=0.24, size=11.5)


@figure("init_compare")
def init_compare(fig):
    X, _ = _five_blobs()
    K = 5
    from sklearn.cluster import KMeans
    seeds = (0, 2, 3, 5, 7)
    rand = []
    for seed in seeds:
        _, _, _, h = _em2d(X, K, 60, seed=seed, trace=True)
        rand.append(np.array([r[3] for r in h]))

    km = KMeans(n_clusters=K, n_init=10, random_state=0).fit(X)
    Sk = np.array([np.cov(X[km.labels_ == k].T) + 1e-4 * np.eye(2)
                   for k in range(K)])
    start = (np.bincount(km.labels_, minlength=K) / len(X),
             km.cluster_centers_.copy(), Sk)
    _, _, _, hk = _em2d(X, K, 60, start=start, trace=True)
    tk = np.array([r[3] for r in hk])

    S0 = np.cov(X.T)
    flat = (np.full(K, 1 / K), np.tile(X.mean(0), (K, 1)) + 1e-3,
            np.array([S0] * K))
    _, _, _, hf = _em2d(X, K, 60, start=flat, trace=True)
    tf = np.array([r[3] for r in hf])

    rand_f = np.array([tr[-1] for tr in rand])
    assert rand_f.max() - rand_f.min() > 5.0      # the starts must differ

    fig.text(0.5, 0.955, f"Five random starts, a $k$-means start and a "
                         f"symmetric one: ${K}$ clusters",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    # distance to the best fit found, on a log scale, so that the symmetric
    # start (hundreds below) and the near-ties (fractions below) both show
    best = max(rand_f.max(), tk[-1], tf[-1])
    floor = 1e-3
    ax = fig.add_axes([0.095, 0.21, 0.37, 0.58])
    for tr in rand:
        ax.semilogy(np.maximum(best - tr, floor), color=GOLD, lw=1.4,
                    alpha=0.85)
    ax.semilogy(np.maximum(best - tk, floor), color=GREEN, lw=2.4)
    ax.semilogy(np.maximum(best - tf, floor), color=RED, lw=2.4)
    ax.set_ylim(floor * 0.7, 3e3)
    ax.set_xlim(-1, 60)
    ax.set_xlabel("pass $t$")
    ax.set_ylabel(r"$\ell^\star - \ell_{\mathrm{obs}}(\theta^t)$")
    ax.text(61, best - tf[-1], "  symmetric", color=RED, fontsize=10,
            va="center", ha="left")
    ax.text(61, best - tk[-1], "  $k$-means", color=GREEN, fontsize=10,
            va="center", ha="left")
    ax.text(61, best - rand_f.min(), "  random", color=GOLD, fontsize=10,
            va="center", ha="left")
    ax.text(30, 3e-3, r"$\ell^\star$: the best fit found", color=MUTED,
            fontsize=9.5, ha="center", va="center")
    despine(ax, keep=("left", "bottom"))

    ax2 = canvas(fig)
    ax2.plot([5.45, 5.45], [0.45, 3.05], color=GRID, lw=1.2)
    nbest = int((rand_f > rand_f.max() - 0.5).sum())
    rows = [
        (GREEN, r"$k$-means start", f"{tk[-1]:,.1f}",
         f"within {abs(tk[-1] - rand_f.max()):.1f} of the best, in a "
         f"handful of passes"),
        (GOLD, "random, best of 5", f"{rand_f.max():,.1f}",
         f"{nbest} of the 5 random starts get there"),
        (GOLD, "random, worst of 5", f"{rand_f.min():,.1f}",
         "a genuinely different fit: two clusters merged"),
        (RED, "all components equal", f"{tf[-1]:,.1f}",
         "stuck: one Gaussian, five times over"),
    ]
    ax2.text(5.70, 3.02, "Where each start lands", color=INK, fontsize=13.5,
             weight="bold", va="top")
    for i, (color, name, val, why) in enumerate(rows):
        y = 2.42 - i * 0.50
        ax2.text(5.70, y, name, color=color, fontsize=11.5, va="center",
                 weight="bold")
        ax2.text(8.55, y, val, color=INK, fontsize=11.5, va="center",
                 ha="right")
        ax2.text(5.70, y - 0.21, why, color=MUTED, fontsize=9.5,
                 va="center")
    ax2.text(5.70, 0.24, r"Rule of thumb: $k$-means to start, several "
                         "random\nrestarts to check, keep the best "
                         r"$\ell_{\mathrm{obs}}$.", color=GREEN,
             fontsize=10.5, va="center", linespacing=1.5)


@figure("reg_covar")
def reg_covar(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Keeping a component from collapsing onto a point",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"Symptom:$\;$ $n_k \to 1$, $|\Sigma_k| \to 0$, $\;\ell_{\mathrm{obs}} \to +\infty$",
         "likely the larger $K$ and $d$ are", RED),
        (r"Cure 1:$\;$ $\Sigma_k \leftarrow \Sigma_k + \varepsilon I$",
         r"ridge on the covariance", GREEN),
        (r"Cure 2:$\;$ restart the component when $n_k$ falls below a floor",
         "put back on a random point", GREEN),
        (r"Cure 3:$\;$ restrict $\Sigma_k$",
         "fewer free numbers give less room to collapse", GREEN),
    ], top=3.02, gap=0.67, x=0.45, eq_size=12.5, why_off=0.28)
    box(ax, 0.80, 0.1, 7.40, 0.40, INK, "", fill="white", lw=1.5)
    ax.text(W / 2, 0.3, "None of these change the algorithm",
            ha="center", va="center", color=INK, fontsize=12)


@figure("logsumexp")
def logsumexp(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "The E-step, done the way a computer can",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    steps(ax, [
        (r"$\gamma_{ik} = p_k f_k(x_i) \,/\, \sum_l p_l f_l(x_i)$",
         r"in $d = 50$ dimensions each $f_k(x_i)$ underflows to $0$, "
         r"and $0/0$ follows", RED),
        (r"$a_{ik} = \log p_k + \log f_k(x_i)$",
         "work with log-densities: the Cholesky factor of $\\Sigma_k$ "
         "gives them directly"),
        (r"$\log \sum_l e^{a_{il}} = m_i + \log \sum_l e^{a_{il} - m_i}$,"
         r"$\quad m_i = \max_l a_{il}$",
         r"the largest term becomes $e^0 = 1$: nothing overflows, "
         r"nothing vanishes", GREEN),
        (r"$\gamma_{ik} = \exp\!\left( a_{ik} - \log \sum_l e^{a_{il}} "
         r"\right)$",
         r"and $\ell_{\mathrm{obs}} = \sum_i \log \sum_l e^{a_{il}}$ "
         r"comes out of the same quantity", GREEN),
    ], top=3.02, gap=0.67, x=0.45, eq_size=12.5, why_off=0.28)
    box(ax, 0.80, 0.04, 7.40, 0.40, GREEN, "", fill="#f1faf1")
    ax.text(W / 2, 0.24, "One log-sum-exp per point gives the "
                         "responsibilities and the likelihood at once",
            ha="center", va="center", color=GREEN, fontsize=12.5)


@figure("covariance_choice")
def covariance_choice(fig):
    X, _ = _three_blobs(seed=5, n=240)
    fams = ("spherical", "diag", "tied", "full")
    names = ("spherical", "diagonal", "tied", "full")
    npar = {"spherical": 3 * 2 + 3 + 2, "diag": 3 * 2 + 3 * 2 + 2,
            "tied": 3 * 2 + 3 + 2, "full": 3 * 2 + 3 * 3 + 2}

    fig.text(0.5, 0.955, "Same data, same $K = 3$", ha="center", 
             va="center", color=MUTED, fontsize=12.5)
    axes = panels(fig, 4, gridspec_kw=dict(left=0.045, right=0.985,
                                           top=0.78, bottom=0.24,
                                           wspace=0.10))
    caps = []
    for ax, fam, name in zip(axes, fams, names):
        p, mus, Ss = _em2d(X, 3, 150, seed=4, cov=fam)
        z = _resp2d(X, p, mus, Ss).argmax(1)
        ax.scatter(X[:, 0], X[:, 1], c=[COMP[k] for k in z], s=10,
                   edgecolors="none", alpha=0.85)
        for k in range(3):
            ellipse(ax, mus[k], Ss[k], COMP[k], nsig=(1.0, 2.0), lw=1.4)
        ax.set_xlim(-3.4, 3.4)
        ax.set_ylim(-2.6, 2.6)
        ax.set_aspect("equal")
        _bare(ax)
        ax.set_title(name, color=INK, fontsize=12.5, pad=7)
        caps.append(f"$\\ell = {_loglik2d(X, p, mus, Ss):,.0f}$,"
                    f"  {npar[fam]} numbers")
    caption_row(fig, axes, caps, y=0.195)
    fig.text(0.5, 0.055, "A family that contains another always fits the "
                         "training sample at least as well, so the choice "
                         "is a model-selection question.",
             ha="center", va="center", color=MUTED, fontsize=11)


@figure("aic_bic")
def aic_bic(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Penalised likelihoods: fit minus a price per parameter",
            ha="center", va="center",
            color=MUTED, fontsize=12.5)
    ax.text(2.30, 3.02, r"$\mathrm{AIC} = -2\,\ell_{\mathrm{obs}}(\hat\theta)"
                        r" + 2\,m$", ha="center", va="center", color=GOLD,
            fontsize=17)
    ax.text(6.70, 3.02, r"$\mathrm{BIC} = -2\,\ell_{\mathrm{obs}}(\hat\theta)"
                        r" + m\,\log n$", ha="center", va="center", color=GREEN,
            fontsize=17)
    ax.text(W / 2, 2.50, r"$\hat\theta$: the fitted model, $\;n$: sample "
                         r"size, $\;m$: free parameters",
            ha="center", va="center", color=INK, fontsize=12)
    ax.plot([4.50, 4.50], [0.78, 2.12], color=GRID, lw=1.2)
    column(ax, 0.55, 2.12, 3.8, "AIC (Akaike, 1973)", [
        "estimates how well the model\nwill predict new data",
        "penalty: 2 per parameter",
        "tends to pick a $K$ a bit too large",
    ], GOLD, leading=0.28, item_size=11)
    column(ax, 4.75, 2.12, 3.8, "BIC (Schwarz, 1978)", [
        r"$\mathrm{BIC} \approx -2\log P(x \mid \mathrm{model})$",
        r"penalty: $\log n$ per parameter",
        "finds the true $K$ as $n$ grows",
    ], GREEN, leading=0.28, item_size=11)
    box(ax, 0.80, 0.1, 7.40, 0.40, INK, "", fill="white", lw=1.5)
    ax.text(W / 2, 0.3, "Fit every $K$, keep the minimum; "
            "BIC penalises more if $n \\geq 8$.",
            ha="center", va="center", color=INK, fontsize=11.5)


@figure("choosing_k")
def choosing_k(fig):
    X, ztrue = _three_blobs(seed=5, n=330)
    ks = np.arange(1, 9)
    ll, bic, aic = [], [], []
    for K in ks:
        p, mus, Ss = _em2d(X, K, 200, seed=4)
        L = _loglik2d(X, p, mus, Ss)
        m = K * (1 + 2 + 3) - 1            # weights, means, covariances
        ll.append(L)
        bic.append(-2 * L + m * np.log(len(X)))
        aic.append(-2 * L + 2 * m)
    ll, bic, aic = np.array(ll), np.array(bic), np.array(aic)

    fig.text(0.5, 0.955, "The likelihood cannot choose $K$, a penalty can",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    ax1 = fig.add_axes([0.075, 0.22, 0.26, 0.56])
    ax1.plot(ks, ll, "o-", color=BLUE, ms=5)
    ax1.set_title(r"$\ell_{\mathrm{obs}}$", color=BLUE, fontsize=12, pad=7)
    ax1.set_xlabel("$K$")
    despine(ax1, keep=("left", "bottom"))

    ax2 = fig.add_axes([0.405, 0.22, 0.26, 0.56])
    ax2.plot(ks, bic, "o-", color=GREEN, ms=5, label="BIC")
    ax2.plot(ks, aic, "o-", color=GOLD, ms=5, label="AIC")
    kb = int(ks[int(np.argmin(bic))])
    ka = int(ks[int(np.argmin(aic))])
    ax2.plot(kb, bic.min(), "o", color=RED, ms=10, mfc="none", mew=2)
    ax2.set_title("BIC and AIC: lower is better", color=INK, fontsize=12,
                  pad=7)
    ax2.set_xlabel("$K$")
    ax2.legend(fontsize=9.5)
    despine(ax2, keep=("left", "bottom"))

    ax = canvas(fig)
    ax.plot([6.15, 6.15], [0.45, 3.05], color=GRID, lw=1.2)
    column(ax, 6.40, 3.02, 2.4, "Reading it", [
        r"$\ell_{\mathrm{obs}}$ only ever rises with $K$",
        f"BIC is smallest at $K = {kb}$, the\nnumber the data was made with",
        f"AIC penalises less: past $K = {ka}$ its\ncurve stays flat, "
        f"so it never objects\nto one component more",
    ], INK, leading=0.30, item_size=10.5)


@figure("gmm_iris")
def gmm_iris(fig):
    from itertools import permutations
    from sklearn.cluster import KMeans

    Xall, y, names, feats = _iris()
    X = Xall[:, [2, 3]]

    def _match(z):
        best = max(permutations(range(3)),
                   key=lambda pm: (np.array([pm[k] for k in z]) == y).sum())
        zz = np.array([best[k] for k in z])
        return best, float((zz == y).mean()), zz

    # the deck's own advice: start from k-means
    km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(X)
    Sk = np.array([np.cov(X[km.labels_ == k].T) + 1e-4 * np.eye(2)
                   for k in range(3)])
    start = (np.bincount(km.labels_, minlength=3) / len(X),
             km.cluster_centers_.copy(), Sk)
    p, mus, Ss = _em2d(X, 3, 300, start=start, reg=1e-4)
    g = _resp2d(X, p, mus, Ss)
    best, acc, zz = _match(g.argmax(1))
    ll = _loglik2d(X, p, mus, Ss)

    # a random start finds a slightly better likelihood, and a worse match
    p2, m2, S2 = _em2d(X, 3, 300, seed=1, reg=1e-4)
    _, acc2, _ = _match(_resp2d(X, p2, m2, S2).argmax(1))
    ll2 = _loglik2d(X, p2, m2, S2)

    fig.text(0.5, 0.955, "Three flowers species.",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    axes = panels(fig, 2, titles=["the true species",
                                  "the mixture's components"],
                  colors=[MUTED, GREEN],
                  gridspec_kw=dict(left=0.07, right=0.60, top=0.80,
                                   bottom=0.22, wspace=0.16))
    axes[0].scatter(X[:, 0], X[:, 1], c=[COMP[k] for k in y], s=18,
                    edgecolors="none", alpha=0.85)
    axes[1].scatter(X[:, 0], X[:, 1], c=[COMP[k] for k in zz], s=18,
                    edgecolors="none", alpha=0.85)
    for k in range(3):
        ellipse(axes[1], mus[k], Ss[k], COMP[best[k]], nsig=(1.0, 2.0),
                lw=1.4)
    for ax in axes:
        ax.set_xlabel(feats[2].replace(" (cm)", ""))
        ax.set_ylabel(feats[3].replace(" (cm)", ""))
        despine(ax, keep=("left", "bottom"))

    ax = canvas(fig)
    ax.plot([5.70, 5.70], [0.45, 3.05], color=GRID, lw=1.2)
    unsure = int((g.max(1) < 0.9).sum())
    column(ax, 5.95, 3.02, 2.8, "Results", [
        f"{100 * acc:.0f}% of the flowers land in the\ncomponent of their "
        f"own species",
        "Two overlapping species are\nwhere the mistakes are made",
        f"{unsure} of the {len(X)} carry no component"
        "\nabove 0.9;\na botanist would hesitate too",
    ], GREEN, leading=0.30, item_size=10.5)
    _credit(fig, "data: Fisher's iris, scikit-learn")


@figure("gmm_anomaly")
def gmm_anomaly(fig):
    rng = np.random.default_rng(9)
    X, _ = _two_blobs(seed=3, n=280)
    p, mus, Ss = _em2d(X, 2, 120, seed=2)
    out = rng.uniform([-3.4, -2.6], [3.4, 2.6], (14, 2))
    dens_tr = sum(pk * _mvn_pdf(X, mk, Sk)
                  for pk, mk, Sk in zip(p, mus, Ss))
    dens_out = sum(pk * _mvn_pdf(out, mk, Sk)
                   for pk, mk, Sk in zip(p, mus, Ss))
    thr = float(np.quantile(dens_tr, 0.02))
    flagged = int((dens_out < thr).sum())

    fig.text(0.5, 0.955, "A mixture gives a score for each class.", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.075, 0.18, 0.40, 0.62])
    gx, gy = np.meshgrid(np.linspace(-3.6, 3.6, 300),
                         np.linspace(-2.8, 2.8, 300))
    G = np.c_[gx.ravel(), gy.ravel()]
    dg = sum(pk * _mvn_pdf(G, mk, Sk)
             for pk, mk, Sk in zip(p, mus, Ss)).reshape(gx.shape)
    ax.contourf(gx, gy, np.log(np.maximum(dg, 1e-12)), levels=14,
                cmap="Blues")
    ax.contour(gx, gy, dg, levels=[thr], colors=[RED], linewidths=1.8)
    ax.scatter(X[:, 0], X[:, 1], s=8, color="white", alpha=0.55,
               edgecolors="none")
    ax.scatter(out[:, 0], out[:, 1], s=46, marker="*",
               color=[RED if d < thr else GREEN for d in dens_out],
               edgecolors="white", linewidths=0.5, zorder=5)
    ax.set_xlim(-3.6, 3.6)
    ax.set_ylim(-2.8, 2.8)
    ax.set_aspect("equal")
    _bare(ax)

    ax2 = canvas(fig)
    ax2.plot([4.90, 4.90], [0.45, 3.05], color=GRID, lw=1.2)
    column(ax2, 5.15, 3.02, 3.6, "Novelty detection, for free", [
        r"score a new point by its density"
        "\n" r"$f(x) = p_1 f_1(x) + \cdots + p_K f_K(x)$",
        "the red line is the 2% contour of the\ntraining density",
        f"{flagged} of the {len(out)} new stars fall outside it",
    ], BLUE, leading=0.30, item_size=11)


@figure("beyond_gaussian")
def beyond_gaussian(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "same two steps with a different component density",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    rows = [
        (BLUE, "Student mixture", r"$f_k$ a multivariate $t$",
         "heavy tails (outliers stop dragging the centres)"),
        (GREEN, "Bernoulli mixture", r"$f_k$ a product of Bernoullis",
         "binary data"),
        (GOLD, "Poisson mixture", r"$f_k$ a Poisson law",
         "counts"),
        (PURPLE, "mixture of regressions", r"$f_k$ a law for $y \mid x$", ""),
        (RED, "hidden Markov model", r"$Z$ a Markov chain, not i.i.d.", ""),
    ]
    for i, (color, name, what, why) in enumerate(rows):
        y = 2.92 - i * 0.54
        ax.text(2.80, y, name, ha="right", va="center", color=color,
                fontsize=12, weight="bold")
        ax.text(3.00, y, what, ha="left", va="center", color=INK,
                fontsize=11)
        ax.text(5.20, y, why, ha="left", va="center", color=MUTED,
                fontsize=10.5)
        if i:
            ax.plot([0.45, 8.55], [y + 0.27, y + 0.27], color=LIGHT, lw=1.0)
    note(ax, "EM used latent label and complete-data likelihood, so it can be adapted.",
         y=0.32, size=11.5)


@figure("gmm_props")
def gmm_props(fig):
    ax = canvas(fig)
    column(ax, 0.55, 3.25, 3.9, "Pros", [
        "density & soft clustering in one fit",
        "clusters with shape",
        "no step size to tune",
        "transfers to other latent-variable models",
    ], GREEN, leading=0.30, item_size=11.5)
    column(ax, 4.90, 3.25, 3.9, "Cons", [
        "local maximum",
        "dependence on initialization",
        "likelihood is unbounded,\nneeds guarding",
        r"$K$ needs tuning",
    ], RED, leading=0.30, item_size=11.5)
    ax.plot([4.65, 4.65], [0.70, 3.35], color=GRID, lw=1.2)


# ==========================================================================
def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course06/img")
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
