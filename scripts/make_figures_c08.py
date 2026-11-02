#!/usr/bin/env python3
"""Every figure of Course08 (model order selection).

One function per figure, registered under the stem the slide deck asks for.
All figures share one canvas (9 x 3.7075 in), which is exactly the content
area pandoc leaves under a slide title, so a figure never has to be resized.

    python3 scripts/make_figures_c08.py Course08/img [stem ...]
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
# the convention of this deck: everything measured on data the model was
# fitted to is blue, everything measured on held-out data is red, the
# complexity being paid for is purple, and the chosen model is green
TRAIN, TEST, CHOSEN, PENALTY = BLUE, RED, GREEN, PURPLE
COMP = [BLUE, GOLD, GREEN, PURPLE, RED]
# a fold matrix is always drawn with the same ramp: white is "not used"
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
# the models and the data every slide runs on
# ==========================================================================
EPS = 1e-12
CACHE = Path(__file__).resolve().parent.parent / ".cache" / "datasets" / "sklearn"


def _sin_data(n=10, seed=6, noise=0.22):
    """Bishop's running example: n points of sin(2 pi x) plus Gaussian noise."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, n)
    t = np.sin(2 * np.pi * x) + rng.normal(0, noise, n)
    return x, t


def _design(x, M):
    """The polynomial design matrix, columns 1, x, ..., x^M."""
    return np.vander(np.asarray(x, float), M + 1, increasing=True)


def _poly_fit(x, t, M, lam=0.0):
    """Least squares on the polynomial basis, ridge-regularised if lam > 0."""
    A = _design(x, M)
    G = A.T @ A + lam * np.eye(M + 1)
    return np.linalg.solve(G, A.T @ np.asarray(t, float))


def _poly_eval(w, x):
    return _design(x, len(w) - 1) @ w


def _rms(w, x, t):
    r = _poly_eval(w, x) - np.asarray(t, float)
    return float(np.sqrt((r ** 2).mean()))


def _folds(n, K, seed=0):
    """K index sets, as the lecture's step 2: a random split into K parts."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(n)
    return [np.sort(f) for f in np.array_split(idx, K)]


def _cv_poly(x, t, M, K=10, seed=0, lam=0.0):
    """The lecture's R_CV for the polynomial of order M."""
    errs = []
    for f in _folds(len(x), K, seed):
        tr = np.setdiff1d(np.arange(len(x)), f)
        w = _poly_fit(x[tr], t[tr], M, lam)
        errs.append(float(((_poly_eval(w, x[f]) - t[f]) ** 2).mean()))
    return float(np.mean(errs)), float(np.std(errs) / np.sqrt(K))


def _gmm_blobs(seed=5, n=400):
    """Three Gaussian clusters, the data lecture 6 left us with."""
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


def _moons(n=200, noise=0.28, seed=3):
    from sklearn.datasets import make_moons
    return make_moons(n_samples=n, noise=noise, random_state=seed)


def _nmf_mu(X, r, iters=200, seed=0, mask=None):
    """Lee and Seung's updates, as in lecture 5, with an optional mask so a
    held-out set of entries can be scored."""
    rng = np.random.default_rng(seed)
    p, n = X.shape
    scale = np.sqrt(max(X.mean(), 1e-10) / r)
    Wm = rng.random((p, r)) * scale + 1e-3
    Hm = rng.random((r, n)) * scale + 1e-3
    Mk = np.ones_like(X) if mask is None else mask
    for _ in range(iters):
        Hm *= (Wm.T @ (Mk * X)) / np.maximum(Wm.T @ (Mk * (Wm @ Hm)), 1e-10)
        Wm *= ((Mk * X) @ Hm.T) / np.maximum((Mk * (Wm @ Hm)) @ Hm.T, 1e-10)
    return Wm, Hm


def _nmf_toy(seed=1, p=30, n=45, r=4, noise=0.05):
    rng = np.random.default_rng(seed)
    Wt = np.abs(rng.normal(0, 1, (p, r))) ** 1.3
    Ht = np.abs(rng.normal(0, 1, (r, n))) ** 1.3
    return np.maximum(Wt @ Ht + rng.normal(0, noise, (p, n)), 1e-4), r


# ==========================================================================
# 1. the question
# ==========================================================================
@figure("selection_setting")
def selection_setting(fig):
    ax = canvas(fig)
    box(ax, 0.50, 2.00, 2.45, 1.00, PURPLE, "", fill="white")
    ax.text(1.725, 2.72, "order", ha="center", va="center", color=PURPLE,
            fontsize=13, weight="bold")
    ax.text(1.725, 2.30, r"$M$: $K$, $r$, $\varepsilon$, $\gamma$, depth, …",
            ha="center", va="center", color=INK, fontsize=11.5)
    box(ax, 3.28, 2.00, 2.45, 1.00, BLUE, "", fill="white")
    ax.text(4.505, 2.72, "parameters", ha="center", va="center", color=BLUE,
            fontsize=13, weight="bold")
    ax.text(4.505, 2.30, r"$\theta$: $w$, $\mu_k$, $W$, $H$, …",
            ha="center", va="center", color=INK, fontsize=11.5)
    box(ax, 6.06, 2.00, 2.45, 1.00, GREEN, "", fill="white")
    ax.text(7.285, 2.72, "fitted model", ha="center", va="center", color=GREEN,
            fontsize=13, weight="bold")
    ax.text(7.285, 2.30, "model ready to use", ha="center", va="center",
            color=INK, fontsize=11.5)
    arrow(ax, (3.00, 2.50), (3.20, 2.50), color=MUTED)
    arrow(ax, (5.78, 2.50), (5.98, 2.50), color=MUTED)
    ax.text(1.725, 1.78, "the loss cannot choose it", ha="center",
            va="center", color=RED, fontsize=10.5)
    ax.text(4.505, 1.78, "fitted by minimising a loss", ha="center",
            va="center", color=MUTED, fontsize=10.5)
    note(ax, "Which model generalises best to unseen data?", y=0.14, size=11.5)


@figure("curve_fitting")
def curve_fitting(fig):
    x, t = _sin_data(10)
    g = np.linspace(0, 1, 400)

    fig.text(0.5, 0.955, "Ten points drawn from a curve",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.10, 0.20, 0.42, 0.60])
    ax.plot(g, np.sin(2 * np.pi * g), color=GREEN, lw=2.2, zorder=2)
    ax.plot(x, t, "o", color=BLUE, ms=8, mfc="white", mew=2, zorder=3)
    ax.set_xlabel("$x$")
    ax.set_ylabel("$t$")
    ax.set_ylim(-1.6, 1.6)
    ax.set_xticks([0, 0.5, 1])
    ax.set_yticks([-1, 0, 1])
    despine(ax, keep=("left", "bottom"))

    ax2 = canvas(fig)
    ax2.plot([5.35, 5.35], [0.45, 3.05], color=GRID, lw=1.2)
    column(ax2, 5.60, 3.02, 3.2, "The set-up", [
        r"the green curve is $\sin(2 \pi x)$: the truth",
        r"the circles are $t_i = \sin(2 \pi x_i) + \epsilon_i$",
    ], INK, leading=0.30, item_size=11)
    ax2.text(5.60, 1.44, "Goal", color=GREEN, fontsize=12.5, weight="bold",
             va="center")
    ax2.text(5.60, 1.02, r"predict $t$ at a new $x$", color=INK, fontsize=11,
             va="center", linespacing=1.6)


@figure("eq_poly_fit")
def eq_poly_fit(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"$f(x, w) = w_0 + w_1 x + \cdots + w_M x^M$",
         r"$M$ is the order of the polynomial; $w$ are its "
         r"coefficients (to be learnt)"),
        (r"$e(w) = \sum_i \rho\left( f(x_i, w) - t_i \right)$",
         r"the error function over the $N$ observed points"),
        (r"$\rho(u) = u^2$$\quad$ so $e$ is quadratic in $w$",
         r"a closed form for $w^\star$ exists for every value of $M$", GREEN),
        (r"$e(w^\star)$ does not help choosing $M$",
         r"$e(w^\star)$ can only go down as $M$ grows", RED),
    ], top=3.5, gap=0.67, x=0.45, eq_size=13, why_off=0.34)
    box(ax, 0.80, 0.15, 7.40, 0.40, PURPLE, "", fill="#f6f3fd")
    ax.text(W / 2, 0.375, r"Two nested problems: find $w$ given $M$ and find $M$",
            ha="center", va="center", color=PURPLE, fontsize=12.5)


@figure("poly_orders")
def poly_orders(fig):
    x, t = _sin_data(10)
    g = np.linspace(0, 1, 500)
    Ms = (1, 2, 3, 9)

    caps = []
    for i, M in enumerate(Ms):
        row, col = divmod(i, 2)
        a = fig.add_axes([0.085 + col * 0.245, 0.52 - row * 0.40,
                          0.195, 0.28])
        w = _poly_fit(x, t, M)
        a.plot(g, np.sin(2 * np.pi * g), color=GREEN, lw=1.6, zorder=2)
        a.plot(g, _poly_eval(w, g), color=RED, lw=2.2, zorder=3)
        a.plot(x, t, "o", color=BLUE, ms=5, mfc="white", mew=1.6, zorder=4)
        a.set_ylim(-1.9, 1.9)
        a.set_xticks([])
        a.set_yticks([])
        despine(a)
        a.set_title(f"$M = {M}$", color=INK, fontsize=12, pad=4)
        caps.append(_rms(w, x, t))

    ax = canvas(fig)
    ax.plot([5.40, 5.40], [0.45, 3.05], color=GRID, lw=1.2)
    column(ax, 5.65, 3.02, 3.2, "Interpretation:", [
        f"$M = 1, 2$: too rigid to bend, the fit\nmisses the shape "
        f"(underfitting)",
        f"$M = 3$: close to the green curve it has\nnever seen",
        f"$M = 9$: ten coefficients for ten points,\nso it passes through "
        f"every one",
    ], INK, leading=0.28, item_size=11)
    ax.text(5.65, 0.74, f"training error at $M = 9$: {caps[-1]:.3f}\n"
                        f"training error at $M = 3$: {caps[-2]:.3f}",
            color=BLUE, fontsize=11, va="center", linespacing=1.6)
    ax.text(5.65, 0.18, "The best training error belongs to the\n"
                        "worst model.",
            color=RED, fontsize=10.5, va="center", linespacing=1.5)


@figure("train_vs_test")
def train_vs_test(fig):
    x, t = _sin_data(10)
    xt, tt = _sin_data(200, seed=99)
    Ms = np.arange(0, 10)
    tr = np.array([_rms(_poly_fit(x, t, M), x, t) for M in Ms])
    te = np.array([_rms(_poly_fit(x, t, M), xt, tt) for M in Ms])

    ax = fig.add_axes([0.095, 0.21, 0.40, 0.58])
    ax.plot(Ms, tr, "o-", color=TRAIN, ms=5, label="training")
    ax.plot(Ms, te, "o-", color=TEST, ms=5, label="test")
    kb = int(Ms[int(np.argmin(te))])
    ax.plot(kb, te.min(), "o", color=CHOSEN, ms=13, mfc="none", mew=2.2,
            zorder=5)
    ax.set_xlabel("$M$")
    ax.set_ylabel(r"$E_{\mathrm{RMS}}$")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=10)
    despine(ax, keep=("left", "bottom"))

    ax2 = canvas(fig)
    ax2.plot([5.25, 5.25], [0.45, 3.05], color=GRID, lw=1.2)
    column(ax2, 5.50, 3.02, 3.2, "Interpretation:", [
        "the blue one never rises: more freedom\nalways fits the sample "
        "better",
        f"the red one turns up after $M = {kb}$: the fit\nstarts chasing "
        f"the noise",
        # "the gap between them is the overfitting",
    ], INK, leading=0.28, item_size=11)


@figure("coefficients_blow_up")
def coefficients_blow_up(fig):
    x, t = _sin_data(10)
    Ms = (0, 1, 3, 9)
    ws = [_poly_fit(x, t, M) for M in Ms]

    ax = canvas(fig)
    xcol = [1.90 + j * 1.55 for j in range(4)]
    for xi, M in zip(xcol, Ms):
        ax.text(xi, 3.04, f"$M = {M}$", color=INK, fontsize=12,
                ha="center", va="center", weight="bold")
    ax.plot([0.60, 8.40], [2.86, 2.86], color=GRID, lw=1.2)
    for i in range(10):
        y = 2.62 - i * 0.235
        ax.text(1.10, y, f"$w_{{{i}}}$", color=MUTED, fontsize=10.5,
                ha="right", va="center")
        for xi, w in zip(xcol, ws):
            if i < len(w):
                big = abs(w[i]) > 50
                ax.text(xi, y, f"{w[i]:,.1f}",
                        color=RED if big else INK,
                        fontsize=10.5, ha="center", va="center",
                        weight="bold" if big else "normal")
            else:
                ax.text(xi, y, "—", color=LIGHT, fontsize=10.5,
                        ha="center", va="center")
    note(ax, r"The $M = 9$ coefficients are enormous and alternate in sign: "
             r"huge terms cancelling to pass through ten points.", y=0.22,
         size=11.5)


@figure("more_data")
def more_data(fig):
    g = np.linspace(0, 1, 500)
    sizes = (10, 15, 100)

    fig.text(0.5, 0.955, "The same $M = 9$ polynomial, three sample sizes",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    axes = panels(fig, 3, gridspec_kw=dict(left=0.145, right=0.855,
                                           top=0.80, bottom=0.34,
                                           wspace=0.14))
    caps = []
    for a, n in zip(axes, sizes):
        x, t = _sin_data(n)
        w = _poly_fit(x, t, 9)
        a.plot(g, np.sin(2 * np.pi * g), color=GREEN, lw=1.6, zorder=2)
        a.plot(g, _poly_eval(w, g), color=RED, lw=2.2, zorder=3)
        a.plot(x, t, "o", color=BLUE, ms=3.5, mfc="white", mew=1.1, zorder=4)
        a.set_ylim(-1.9, 1.9)
        a.set_xticks([])
        a.set_yticks([])
        despine(a)
        a.set_title(f"$N = {n}$", color=INK, fontsize=12, pad=5)
        xt, tt = _sin_data(200, seed=99)
        caps.append(_rms(w, xt, tt))
    caption_row(fig, axes, [f"test {c:.2f}" for c in caps], y=0.33)

    ax = canvas(fig)
    note(ax, "Ten coefficients, held down by more points: the affordable\n"
             "order grows with the training set.", y=0.52, size=12.5)


@figure("svm_sigma")
def svm_sigma(fig):
    from sklearn.svm import SVC
    X, y = _moons(220, noise=0.30, seed=3)
    gammas = (0.08, 2.0, 200.0)
    names = (r"$\gamma$ too small", r"$\gamma$ about right",
             r"$\gamma$ too large")
    colors = (RED, GREEN, RED)
    gx, gy = np.meshgrid(np.linspace(-1.6, 2.6, 300),
                         np.linspace(-1.2, 1.7, 300))
    G = np.c_[gx.ravel(), gy.ravel()]

    axes = panels(fig, 3, gridspec_kw=dict(left=0.045, right=0.985,
                                           top=0.80, bottom=0.22,
                                           wspace=0.08))
    caps = []
    for a, gm, name, color in zip(axes, gammas, names, colors):
        clf = SVC(C=1.0, gamma=gm).fit(X, y)
        Z = clf.decision_function(G).reshape(gx.shape)
        a.contourf(gx, gy, Z, levels=[-9e9, 0, 9e9],
                   colors=["#faeeee", "#e8eef5"])
        a.contour(gx, gy, Z, levels=[0], colors=[INK], linewidths=1.8)
        a.scatter(X[:, 0], X[:, 1], c=[BLUE if yy else RED for yy in y],
                  s=13, edgecolors="none", alpha=0.9)
        a.set_aspect("equal")
        _bare(a)
        a.set_title(name, color=color, fontsize=13, pad=8)
        caps.append(float(clf.score(X, y)))
    caption_row(fig, axes, [f"training accuracy {c:.0%}" for c in caps],
                y=0.27, size=12)


@figure("overfit_underfit")
def overfit_underfit(fig):
    ax = canvas(fig)
    rows = [
        (RED, "underfitting", "cannot represent the pattern",
         "train high, test high", r"$M$ too small"),
        (GREEN, '"sweet spot"', "the pattern and not the noise",
         "train low, test lowest", r"$M$ about right"),
        (RED, "overfitting", "this sample, noise included",
         "train tiny, test high", r"$M$ too large"),
    ]
    x = (0.4, 2.2, 4.9, 7.2)
    for xi, head in zip(x, ("", "What happens", "What is measured", "Why")):
        ax.text(xi, 3.02, head, color=MUTED, fontsize=11.5, va="center")
    ax.plot([0.42, 8.58], [2.84, 2.84], color=GRID, lw=1.2)
    for i, (color, name, what, meas, why) in enumerate(rows):
        y = 2.52 - i * 0.56
        ax.text(x[0], y, name, color=color, fontsize=12.5, weight="bold",
                va="center")
        ax.text(x[1], y, what, color=INK, fontsize=11, va="center")
        ax.text(x[2], y, meas, color=INK, fontsize=11, va="center")
        ax.text(x[3], y, why, color=color, fontsize=11, va="center")
        if i:
            ax.plot([0.42, 8.58], [y + 0.28, y + 0.28], color=LIGHT, lw=1.0)
    # the two words of the lecture: the term in purple, its definition in ink
    defs = [
        ("generalisation",
         "how the model behaves on data drawn from the same law, "
         "but never seen"),
        ("model selection",
         r"choosing $M$ so that the generalisation is as good as it "
         r"can be"),
    ]
    for i, (term, meaning) in enumerate(defs):
        y = 0.82 - i * 0.42
        ax.text(0.42, y, term, color=PURPLE, fontsize=12.5, weight="bold",
                ha="left", va="center")
        ax.text(2.25, y, meaning, color=INK, fontsize=11.5, ha="left",
                va="center")


# ==========================================================================
# 1b. the same two failures, knob by knob (every lecture so far)
# ==========================================================================
@figure("knob_rigid_vs_flexible")
def knob_rigid_vs_flexible(fig):
    """Lecture 1: naive Bayes, LDA, QDA — capacity chosen by the covariance
    model.  Underfitting is a bias no sample size removes; overfitting is a
    variance that data cures."""
    from sklearn.discriminant_analysis import (
        LinearDiscriminantAnalysis as _LDA,
        QuadraticDiscriminantAnalysis as _QDA,
    )
    from sklearn.naive_bayes import GaussianNB

    S = np.array([[1.0, 0.75], [0.75, 1.0]])
    mu0, mu1 = np.array([-1.0, -0.6]), np.array([1.0, 0.6])
    models = (("naive Bayes", GaussianNB, RED),
              ("LDA", _LDA, GREEN),
              ("QDA", _QDA, PURPLE))

    def sample(n, seed):
        rng = np.random.default_rng(seed)
        X = np.vstack([rng.multivariate_normal(mu0, S, n),
                       rng.multivariate_normal(mu1, S, n)])
        return X, np.r_[np.zeros(n), np.ones(n)]

    Xte, yte = sample(5000, 0)
    # the best any rule can reach here: the true linear discriminant
    wstar = np.linalg.solve(S, mu1 - mu0)
    cstar = wstar @ (mu0 + mu1) / 2
    bayes = float(((Xte @ wstar > cstar).astype(float) == yte).mean())

    ns = np.array([10, 15, 20, 30, 50, 100, 200, 500])
    curves = {name: [] for name, _, _ in models}
    for n in ns:
        acc = {name: [] for name, _, _ in models}
        for rep in range(120):
            Xtr, ytr = sample(int(n), 1000 + rep)
            for name, Model, _ in models:
                acc[name].append(Model().fit(Xtr, ytr).score(Xte, yte))
        for name in acc:
            curves[name].append(float(np.mean(acc[name])))
    curves = {k: np.array(v) for k, v in curves.items()}
    assert curves["naive Bayes"][-1] < curves["LDA"][-1] - 0.02
    assert curves["QDA"][0] < curves["LDA"][0] - 0.01
    plateau = curves["naive Bayes"][-1]
    qda_gap0 = curves["LDA"][0] - curves["QDA"][0]

    Xs, ys = sample(20, 1001)
    ax = fig.add_axes([0.120, 0.38, 0.330, 0.50])
    gx, gy = np.meshgrid(np.linspace(-4.2, 4.2, 300),
                         np.linspace(-3.4, 3.4, 300))
    G = np.c_[gx.ravel(), gy.ravel()]
    # the two classes are drawn in grey, so the three colours on this
    # panel are the three decision rules and nothing else
    ax.plot(Xs[ys == 0, 0], Xs[ys == 0, 1], "o", color=MUTED, ms=5,
            mfc="white", mew=1.4, zorder=2)
    ax.plot(Xs[ys == 1, 0], Xs[ys == 1, 1], "o", color=MUTED, ms=5,
            mew=0, zorder=2)
    for (name, Model, color), ls in zip(models, (":", "-", "--")):
        Z = Model().fit(Xs, ys).predict(G).reshape(gx.shape)
        ax.contour(gx, gy, Z, levels=[0.5], colors=[color], linewidths=2.0,
                   linestyles=[ls], zorder=3)
    ax.set_xlim(-4.2, 4.2)
    ax.set_ylim(-3.4, 3.4)
    _bare(ax)
    ax.set_title("one sample of 40", color=INK, fontsize=11.5, pad=6)

    ax2 = fig.add_axes([0.550, 0.38, 0.330, 0.50])
    ax2.axhline(bayes, color=MUTED, lw=1.4, ls=":")
    for name, _, color in models:
        ax2.plot(ns, curves[name], "o-", color=color, ms=4, lw=2.0)
    ax2.set_xscale("log")
    ax2.set_xlabel("points per class")
    ax2.set_ylabel("test accuracy")
    ax2.set_xticks([10, 100, 500])
    ax2.set_xticklabels(["10", "100", "500"])
    ax2.set_title("as the sample grows", color=INK, fontsize=11.5, pad=6)
    despine(ax2, keep=("left", "bottom"))
    ax2.annotate("best possible", xy=(ns[0], bayes), xytext=(2, -4),
                 textcoords="offset points", ha="left", va="top",
                 color=MUTED, fontsize=9)

    ax3 = canvas(fig)
    lines = [
        (RED, f"naive Bayes is too rigid: it stalls at {plateau:.0%}, and more "
              f"data never fixes a bias."),
        (PURPLE, f"QDA is too free: {qda_gap0:.0%} behind at 10 points, level "
                 f"by 500."),
        (GREEN, "LDA is the shape the data really has, and wins at every size."),
    ]
    for i, (color, text) in enumerate(lines):
        ax3.text(W / 2, 0.90 - i * 0.32, text, ha="center", va="center",
                 color=color, fontsize=11.5)


@figure("knob_ridge_lambda")
def knob_ridge_lambda(fig):
    """Lecture 2: the penalty is a capacity knob that runs backwards."""
    x, t = _sin_data(10)
    xe, te = _sin_data(60, seed=11)
    g = np.linspace(0, 1, 400)
    lams = (0.0, 1.8e-5, 10.0)
    names = (r"$\lambda = 0$", r"$\lambda \approx 2 \cdot 10^{-5}$",
             r"$\lambda = 10$")
    colors = (RED, GREEN, RED)

    fits = [_poly_fit(x, t, 9, lam) for lam in lams]
    tr = [_rms(w, x, t) for w in fits]
    tev = [_rms(w, xe, te) for w in fits]
    assert tr[0] < tr[1] < tr[2] and tev[1] < tev[0] and tev[1] < tev[2]

    fig.text(0.5, 0.955, r"(order $M = 9$)", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    axes = panels(fig, 3, gridspec_kw=dict(left=0.055, right=0.985,
                                           top=0.78, bottom=0.26,
                                           wspace=0.18))
    for a, w, name, color in zip(axes, fits, names, colors):
        a.plot(g, np.sin(2 * np.pi * g), color=MUTED, lw=1.6, ls=":",
               zorder=2)
        a.plot(g, _poly_eval(w, g), color=color, lw=2.2, zorder=3)
        a.plot(x, t, "o", color=BLUE, ms=6, mfc="white", mew=1.8, zorder=4)
        a.set_ylim(-1.8, 1.8)
        a.set_xticks([0, 0.5, 1])
        a.set_yticks([-1, 0, 1])
        a.set_title(name, color=color, fontsize=13, pad=8)
        despine(a, keep=("left", "bottom"))
    caption_row(fig, axes,
                [f"train {a:.2f}  ·  test {b:.2f}" for a, b in zip(tr, tev)],
                y=0.145, size=11)
    ax = canvas(fig)
    ax.text(W / 2, 0.22, "This knob runs backwards: capacity falls as "
                         r"$\lambda$ grows, so the left panel is the "
                         "overfitted one.",
            ha="center", va="center", color=PENALTY, fontsize=11.5)


@figure("knob_svm_c")
def knob_svm_c(fig):
    """Lecture 3: the other SVM knob, at fixed gamma."""
    from sklearn.svm import SVC
    X, y = _moons(120, noise=0.30, seed=3)
    Xe, ye = _moons(3000, noise=0.30, seed=77)
    Cs = (0.01, 1.0, 1e3)
    names = ("$C$ too small", "$C$ about right", "$C$ too large")
    colors = (RED, GREEN, RED)
    gx, gy = np.meshgrid(np.linspace(-1.7, 2.7, 300),
                         np.linspace(-1.4, 1.9, 300))
    G = np.c_[gx.ravel(), gy.ravel()]

    axes = panels(fig, 3, gridspec_kw=dict(left=0.045, right=0.985,
                                           top=0.78, bottom=0.26,
                                           wspace=0.08))
    caps = []
    for a, C, name, color in zip(axes, Cs, names, colors):
        clf = SVC(C=C, gamma=2.0).fit(X, y)
        Z = clf.decision_function(G).reshape(gx.shape)
        a.contourf(gx, gy, Z, levels=[-9e9, 0, 9e9],
                   colors=["#faeeee", "#e8eef5"])
        a.contour(gx, gy, Z, levels=[0], colors=[INK], linewidths=1.8)
        a.scatter(X[:, 0], X[:, 1], c=[BLUE if v else RED for v in y],
                  s=13, edgecolors="none", alpha=0.9)
        a.set_aspect("equal")
        _bare(a)
        a.set_title(name, color=color, fontsize=13, pad=8)
        caps.append((float(clf.score(X, y)), float(clf.score(Xe, ye))))
    assert caps[1][1] > caps[0][1] and caps[1][1] > caps[2][1]
    caption_row(fig, axes,
                [f"train {a:.0%}  ·  test {b:.0%}" for a, b in caps],
                y=0.16, size=11.5)
    # ax = canvas(fig)
    # ax.text(W / 2, 0.22, f"Underfitting costs "
    #                      f"{caps[1][1] - caps[0][1]:.0%} here; overfitting "
    #                      f"costs {caps[1][1] - caps[2][1]:.0%}. "
    #                      f"The two sides are rarely symmetric.",
    #         ha="center", va="center", color=MUTED, fontsize=11.5)


@figure("knob_kmeans_k")
def knob_kmeans_k(fig):
    """Lecture 4: K in k-means, and why the objective cannot choose it."""
    from sklearn.cluster import KMeans
    X, _ = _gmm_blobs(seed=5, n=400)
    Ks = (2, 3, 8)
    names = ("$K = 2$", "$K = 3$", "$K = 8$")
    colors = (RED, GREEN, RED)

    axes = panels(fig, 3, gridspec_kw=dict(left=0.045, right=0.985,
                                           top=0.78, bottom=0.26,
                                           wspace=0.08))
    caps = []
    for a, K, name, color in zip(axes, Ks, names, colors):
        km = KMeans(K, n_init=10, random_state=0).fit(X)
        pal = [COMP[i % len(COMP)] for i in range(K)]
        a.scatter(X[:, 0], X[:, 1], c=[pal[i] for i in km.labels_], s=11,
                  edgecolors="none", alpha=0.75)
        a.plot(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1], "X",
               color=INK, ms=9, mew=0)
        a.set_aspect("equal")
        _bare(a)
        a.set_title(name, color=color, fontsize=13, pad=8)
        caps.append(float(km.inertia_))
    assert caps[0] > caps[1] > caps[2]
    caption_row(fig, axes, [f"inertia {c:.0f}" for c in caps], y=0.16,
                size=11.5)
    # ax = canvas(fig)
    # ax.text(W / 2, 0.22, "Inertia keeps falling, so the objective itself "
    #                      "always prefers the right-hand panel: "
    #                      "it cannot choose $K$.",
    #         ha="center", va="center", color=RED, fontsize=11.5)


@figure("knob_dbscan_eps")
def knob_dbscan_eps(fig):
    """Lecture 4: the density knob, whose two failures look nothing alike."""
    from sklearn.cluster import DBSCAN
    X, _ = _gmm_blobs(seed=5, n=400)
    eps = (0.18, 0.40, 0.70)
    names = (r"$\varepsilon = 0.18$", r"$\varepsilon = 0.40$",
             r"$\varepsilon = 0.70$")
    colors = (RED, GREEN, RED)

    axes = panels(fig, 3, gridspec_kw=dict(left=0.045, right=0.985,
                                           top=0.78, bottom=0.26,
                                           wspace=0.08))
    caps = []
    for a, e, name, color in zip(axes, eps, names, colors):
        lab = DBSCAN(eps=e, min_samples=8).fit(X).labels_
        nk = len(set(lab) - {-1})
        noise = float((lab == -1).mean())
        core = lab >= 0
        a.scatter(X[core, 0], X[core, 1],
                  c=[COMP[v % len(COMP)] for v in lab[core]], s=11,
                  edgecolors="none", alpha=0.8)
        a.scatter(X[~core, 0], X[~core, 1], marker="x", c=MUTED, s=13,
                  linewidths=0.9, alpha=0.7)
        a.set_aspect("equal")
        _bare(a)
        a.set_title(name, color=color, fontsize=13, pad=8)
        caps.append((nk, noise))
    assert caps[0][0] > caps[1][0] > caps[2][0]
    caption_row(fig, axes,
                [f"{k} cluster{'s' if k != 1 else ''}  ·  {p:.0%} noise"
                 for k, p in caps],
                y=0.16, size=11.5)
    ax = canvas(fig)
    ax.text(W / 2, 0.22, "Too small and almost every point is called noise; "
                         "too large and the three populations merge into one.",
            ha="center", va="center", color=MUTED, fontsize=11.5)


@figure("knob_nmf_rank")
def knob_nmf_rank(fig):
    """Lecture 5: the rank, scored by holding entries out of the matrix."""
    X, rtrue = _nmf_toy(seed=1, p=30, n=45, r=4, noise=0.12)
    rs = np.arange(1, 11)
    tr = np.zeros((5, len(rs)))
    ho = np.zeros((5, len(rs)))
    for s in range(5):
        rng = np.random.default_rng(100 + s)
        mask = (rng.random(X.shape) > 0.2).astype(float)
        for j, r in enumerate(rs):
            Wm, Hm = _nmf_mu(X, int(r), iters=400, seed=s, mask=mask)
            R = Wm @ Hm
            tr[s, j] = np.sqrt((((R - X) ** 2) * mask).sum() / mask.sum())
            ho[s, j] = np.sqrt((((R - X) ** 2) * (1 - mask)).sum()
                               / (1 - mask).sum())
    trm, hom = tr.mean(0), ho.mean(0)
    best = int(rs[int(np.argmin(hom))])
    assert best == rtrue

    ax = fig.add_axes([0.285, 0.265, 0.43, 0.545])
    ax.plot(rs, trm, "o-", color=TRAIN, ms=5, lw=2.2)
    ax.plot(rs, hom, "o-", color=TEST, ms=5, lw=2.2)
    ax.plot(best, hom[best - 1], "o", color=CHOSEN, ms=14, mfc="none",
            mew=2.2)
    ax.set_xlabel("$r$")
    ax.set_ylabel("reconstruction error")
    ax.set_xticks([1, 4, 7, 10])
    despine(ax, keep=("left", "bottom"))
    ax.annotate("entries used to fit", xy=(rs[-1], trm[-1]), xytext=(2, 11),
                textcoords="offset points", ha="right", va="bottom",
                color=TRAIN, fontsize=10)
    ax.annotate("entries held out", xy=(rs[-2], hom[-2]), xytext=(0, 12),
                textcoords="offset points", ha="center", va="bottom",
                color=TEST, fontsize=10)

    ax2 = canvas(fig)
    note(ax2, f"The held-out entries are best at $r = {best}$, the rank the "
              f"data was built with cross-validation, on a mask.",
         y=0.30, size=12.5)


@figure("knob_gmm_k")
def knob_gmm_k(fig):
    """Lecture 6: K in a mixture — here a likelihood is available, so the
    train/test picture of the polynomial comes back exactly."""
    from sklearn.mixture import GaussianMixture
    X, _ = _gmm_blobs(seed=5, n=400)
    Xv, _ = _gmm_blobs(seed=9, n=2000)
    Ks = np.arange(1, 9)
    tr, te = [], []
    models = {}
    for K in Ks:
        gm = GaussianMixture(int(K), covariance_type="full", n_init=5,
                             random_state=0).fit(X)
        models[int(K)] = gm
        tr.append(float(gm.score(X)))
        te.append(float(gm.score(Xv)))
    tr, te = np.array(tr), np.array(te)
    best = int(Ks[int(np.argmax(te))])
    assert best == 3 and np.all(np.diff(tr) > 0)

    ax = fig.add_axes([0.085, 0.265, 0.30, 0.545])
    ax.plot(Ks, tr, "o-", color=TRAIN, ms=5, lw=2.2)
    ax.plot(Ks, te, "o-", color=TEST, ms=5, lw=2.2)
    ax.plot(best, te[best - 1], "o", color=CHOSEN, ms=14, mfc="none", mew=2.2)
    ax.set_xlabel("$K$")
    ax.set_ylabel("log-likelihood / point")
    despine(ax, keep=("left", "bottom"))
    ax.annotate("fitted sample", xy=(Ks[-1], tr[-1]), xytext=(-2, 7),
                textcoords="offset points", ha="right", va="bottom",
                color=TRAIN, fontsize=10)
    ax.annotate("fresh sample", xy=(Ks[-1], te[-1]), xytext=(-2, -8),
                textcoords="offset points", ha="right", va="top",
                color=TEST, fontsize=10)

    for i, (K, color) in enumerate(((best, GREEN), (8, RED))):
        a = fig.add_axes([0.470 + i * 0.235, 0.265, 0.215, 0.545])
        gm = models[K]
        a.scatter(X[:, 0], X[:, 1], c=MUTED, s=7, edgecolors="none",
                  alpha=0.45)
        for k in range(K):
            ellipse(a, gm.means_[k], gm.covariances_[k], color, nsig=(1.6,),
                    lw=1.6)
        a.set_aspect("equal")
        a.set_xlim(-3.6, 3.6)
        a.set_ylim(-2.8, 2.8)
        _bare(a)
        a.set_title(f"$K = {K}$", color=color, fontsize=12, pad=6)

    ax2 = canvas(fig)
    note(ax2, f"The fitted score rises with every component; the fresh one "
              f"peaks at $K = {best}$.", y=0.30, size=12.5)


@figure("knob_recap_supervised")
def knob_recap_supervised(fig):
    """Every knob met in the supervised half of the course, and what the
    two ends of it look like."""
    ax = canvas(fig)
    ax.text(W / 2, 3.50, "What goes wrong at each end.", ha="center", va="center", color=MUTED,
            fontsize=12.5)
    rows = [
        (r"$\alpha$ in naive Bayes", INK,
         "an unseen value zeroes the whole product",
         "all values look about equally likely"),
        ("NB / LDA / QDA", INK, "an assumption more data cannot repair",
         "a boundary that follows this sample"),
        ("$M$, the polynomial order", BLUE,
         "the curve cannot bend to the data",
         "it threads every point, noise included"),
        (r"$\lambda$ in ridge, lasso", BLUE,
         "coefficients blow up on 10 points",
         "everything shrunk to zero, pattern lost"),
        (r"$\delta$ in a robust loss", BLUE,
         "every residual is treated as an outlier",
         "least squares: one outlier tilts the fit"),
        ("$C$ in a soft margin", GOLD,
         "slack is free, the margin ignores the points",
         "no slack: the boundary wraps noise"),
        (r"$\gamma$ in an RBF kernel", GOLD,
         "the boundary is nearly straight",
         "one island around each point"),
        (r"$\varepsilon$, the SVR tube", GOLD,
         "nearly every point is a support vector",
         "the tube swallows the signal"),
    ]
    _knob_table(ax, rows, x=(0.42, 3.00, 5.85))


@figure("knob_recap_unsupervised")
def knob_recap_unsupervised(fig):
    """The same, for the half of the course with no labels to score."""
    ax = canvas(fig)
    ax.text(W / 2, 3.50, "What goes wrong at each end.", ha="center",
            va="center", color=MUTED, fontsize=12.5)
    rows = [
        ("$q$ in PCA", INK, "directions carrying real signal are dropped",
         "the directions kept are mostly noise"),
        ("$K$ in $k$-means", GREEN, "two populations merged into one cluster",
         "a single population cut into pieces"),
        (r"$\varepsilon$ in DBSCAN", GREEN,
         "almost every point is labelled noise",
         "every cluster merged, nothing is noise"),
        ("MinPts in DBSCAN", GREEN, "noise is promoted into clusters",
         "real clusters are called noise"),
        ("the cut of a dendrogram", GREEN, "one leaf per point",
         "everything in a single branch"),
        ("$r$ in NMF", PURPLE, "distinct parts mixed into one component",
         "components fitting the noise of the matrix"),
        ("$K$ in a mixture", RED, "one bell covering two populations",
         "a component glued to a single point"),
        ("the covariance type", RED, "spherical cannot follow the shape",
         "full costs $K d (d+1) / 2$ numbers"),
    ]
    _knob_table(ax, rows, x=(0.42, 2.85, 5.75))


def _knob_table(ax, rows, x):
    """The two-ended table both recap slides are drawn with."""
    for xi, head, col in zip(x, ("The knob", "Too small", "Too large"),
                             (MUTED, RED, RED)):
        ax.text(xi, 3.08, head, color=col, fontsize=11.5, va="center")
    ax.plot([0.38, 8.62], [2.92, 2.92], color=GRID, lw=1.2)
    for i, (name, color, small, large) in enumerate(rows):
        y = 2.62 - i * 0.33
        ax.text(x[0], y, name, color=color, fontsize=11, va="center",
                weight="bold")
        ax.text(x[1], y, small, color=INK, fontsize=10.5, va="center")
        ax.text(x[2], y, large, color=INK, fontsize=10.5, va="center")
        if i:
            ax.plot([0.38, 8.62], [y + 0.165, y + 0.165], color=LIGHT, lw=1.0)


@figure("todays_question")
def todays_question(fig):
    """The slide the two tables lead into: none of those numbers is fitted,
    so today is about choosing them."""
    ax = canvas(fig)
    ax.text(W / 2, 3.08, "And evaluate the quality.", ha="center", va="center",
            color=INK, fontsize=19)
    tools = [
        (BLUE, "hold out", "score the model where\nit was not fitted"),
        (GOLD, "cross-validate", "use every point for\nboth jobs, in turn"),
        (PURPLE, "search", "grids, random draws,\nand guided searches"),
        (GREEN, "penalise", "AIC, BIC: the fit minus\na price for complexity"),
    ]
    w, gap = 1.92, 0.22
    x0 = (W - (4 * w + 3 * gap)) / 2
    for i, (color, title, body) in enumerate(tools):
        xi = x0 + i * (w + gap)
        box(ax, xi, 0.82, w, 1.26, color, "", fill="white", lw=1.6)
        ax.text(xi + w / 2, 1.80, title, ha="center", va="center",
                color=color, fontsize=13, weight="bold")
        ax.text(xi + w / 2, 1.34, body, ha="center", va="center", color=INK,
                fontsize=10.5, linespacing=1.6)
    note(ax, "How to estimate error on data that the model has never seen.", y=0.44, size=11.5)


# ==========================================================================
# 2. generalization, defined
# ==========================================================================
@figure("eq_risk")
def eq_risk(fig):
    ax = canvas(fig)
    ax.text(W / 2, 2.82, r"$R(f) \;=\; E_{(X, T)}\!\left[ \rho(f(X), T) "
                         r"\right] \;=\; \int \; \rho(f(x), t) \, "
                         r"p(x, t) \, dx \, dt$",
            ha="center", va="center", color=INK, fontsize=19)
    # one arrow per term of the equation; the x positions are the glyphs of
    # the line above, measured on the rendered figure
    above = [
        (3.7, 3.2, "the data $X$", BLUE),
        (4.2, 4.8, "the target $T$", GREEN),
    ]
    for xterm, xlab, label, color in above:
        ax.annotate(label, xy=(xterm, 3.06), xytext=(xlab, 3.42),
                    ha="center", va="center", color=color, fontsize=10.5,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5))
    below = [
        (1.7, 0.95, "the risk of the\ncandidate $f$", INK),
        (2.9, 2.95, "over the law of the data,\nnot over our sample", PURPLE),
        (5.3, 5.15, "the loss we chose:\nsquared, hinge, 0–1, …", BLUE),
        (6.8, 7.45, "the law we do\nnot know", RED),
    ]
    for xterm, xlab, label, color in below:
        ax.annotate(label, xy=(xterm, 2.54), xytext=(xlab, 1.98),
                    ha="center", va="center", color=color, fontsize=10.5,
                    linespacing=1.5,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5))
    column(ax, 0.55, 1.46, 3.9, "Problem:", [
        r"$p(x, t)$ is exactly what we do not know",
        r"so $R(f)$ can never be computed",
    ], RED, leading=0.30, item_size=11.5)
    note(ax, "Averaging the loss over more and more unseen points converges "
             "to $R(f)$.", y=0.16, size=11.5)


@figure("eq_empirical_risk")
def eq_empirical_risk(fig):
    ax = canvas(fig)
    steps(ax, [
        (r"$R_N(f) \;=\; \frac{1}{N} \sum_i \rho(f(x_i), t_i)$",
         r"Average over the $N$ test points", BLUE),
        (r"$E[R_N(f)] = R(f)$,$\quad$ $R_N(f) \to R(f)$ as $N \to \infty$",
         r"Unbiased", GREEN),
        (r"For $\hat{f}$ fitted on the same $N$ points, $R_N(\hat{f})$ is biased (too optimistic)",
         r'$R_N(\hat{f})$ is the "training error"', RED),
        (r"Score $\hat{f}$ where it was not fitted",
         r"Use held-out points to score $\hat{f}$", GREEN),
    ], top=3.08, gap=0.74, x=0.45, eq_size=13, why_off=0.36)
    note(ax, r"When $N$ is small, the cost of holding out is high.",
         y=0.18, size=11.5, color=PENALTY)


@figure("risk_picture")
def risk_picture(fig):
    x, t = _sin_data(10)
    xt, tt = _sin_data(400, seed=99)
    Ms = np.arange(0, 10)
    tr = np.zeros((40, len(Ms)))
    te = np.zeros((40, len(Ms)))
    for s in range(40):
        xs, ts = _sin_data(10, seed=200 + s)
        for j, M in enumerate(Ms):
            w = _poly_fit(xs, ts, M)
            tr[s, j] = _rms(w, xs, ts) ** 2
            te[s, j] = _rms(w, xt, tt) ** 2

    fig.text(0.5, 0.955, "Forty samples of ten points, every order fitted "
                         "to each", ha="center", va="center", color=MUTED,
             fontsize=12.5)
    ax = fig.add_axes([0.065, 0.255, 0.915, 0.545])
    for s in range(40):
        ax.plot(Ms, tr[s], color=TRAIN, lw=0.6, alpha=0.16)
        ax.plot(Ms, te[s], color=TEST, lw=0.6, alpha=0.16)
    mtr, mte = np.median(tr, 0), np.median(te, 0)
    ax.plot(Ms, mtr, color=TRAIN, lw=2.6)
    ax.plot(Ms, mte, color=TEST, lw=2.6)
    kb = int(Ms[int(np.argmin(mte))])
    ax.plot(kb, mte.min(), "o", color=CHOSEN, ms=13, mfc="none", mew=2.2,
            zorder=5)
    ax.annotate("expected training error", xy=(4.5, 0.025),
                xytext=(4.2, 0.27), color=TRAIN, fontsize=11, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=TRAIN, lw=1.3))
    ax.annotate("expected test error", xy=(6.6, 0.10), xytext=(6.4, 0.42),
                color=TEST, fontsize=11, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=TEST, lw=1.3))
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("model complexity $M$")
    ax.set_ylabel("squared error")
    despine(ax, keep=("left", "bottom"))

    fig.text(0.5, 0.055, "High bias, low variance on the left.   "
                         "Low bias, high variance on the right.",
             ha="center", va="center", color=PENALTY, fontsize=11)


@figure("bias_variance")
def bias_variance(fig):
    g = np.linspace(0, 1, 200)
    truth = np.sin(2 * np.pi * g)
    Ms = (1, 3, 9)
    names = ("high bias, low variance", "balanced",
             "low bias, high variance")
    colors = (RED, GREEN, RED)

    fig.text(0.5, 0.955, "Twenty different samples",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    axes = panels(fig, 3, gridspec_kw=dict(left=0.055, right=0.625,
                                           top=0.78, bottom=0.26,
                                           wspace=0.12))
    stats = []
    for a, M, name, color in zip(axes, Ms, names, colors):
        preds = []
        for s in range(20):
            xs, ts = _sin_data(10, seed=300 + s)
            w = _poly_fit(xs, ts, M)
            p = _poly_eval(w, g)
            preds.append(p)
            a.plot(g, p, color=color, lw=0.8, alpha=0.30)
        preds = np.array(preds)
        a.plot(g, preds.mean(0), color=color, lw=2.4)
        a.plot(g, truth, color=INK, lw=1.6, ls="--")
        a.set_ylim(-2.2, 2.2)
        a.set_xticks([])
        a.set_yticks([])
        despine(a)
        a.set_title(f"$M = {M}$", color=INK, fontsize=12, pad=6)
        bias2 = float(((preds.mean(0) - truth) ** 2).mean())
        var = float(preds.var(0).mean())
        stats.append((bias2, var))
    caption_row(fig, axes, [name for name in names], y=0.195)

    ax = canvas(fig)
    ax.plot([5.85, 5.85], [0.45, 3.05], color=GRID, lw=1.2)
    ax.text(6.10, 3.02, "Measured over the twenty", color=INK, fontsize=13,
            weight="bold", va="top")
    ax.text(7.45, 2.56, "bias$^2$", color=PENALTY, fontsize=11,
            ha="right", va="center")
    ax.text(8.45, 2.56, "variance", color=GOLD, fontsize=11, ha="right",
            va="center")
    for i, (M, (b, v)) in enumerate(zip(Ms, stats)):
        y = 2.18 - i * 0.40
        ax.text(6.10, y, f"$M = {M}$", color=INK, fontsize=11.5,
                va="center")
        ax.text(7.45, y, f"{b:.2f}", color=PENALTY, fontsize=11.5,
                ha="right", va="center")
        ax.text(8.45, y, f"{v:.2f}", color=GOLD, fontsize=11.5, ha="right",
                va="center")


# ==========================================================================
# 3. hold-out and cross-validation
# ==========================================================================
def _cv_data():
    """The sample the cross-validation section runs on: large enough that
    ten folds make sense, small enough that the choice is still uncertain."""
    return _sin_data(60, seed=2)


def _split_bar(ax, x, y, w, h, parts, labels, colors, size=10.5):
    """A horizontal bar cut into coloured blocks: the deck's split diagram."""
    left = x
    for frac, lab, col in zip(parts, labels, colors):
        wd = w * frac
        ax.add_patch(Rectangle((left, y), wd, h, facecolor=col,
                               edgecolor="white", lw=1.4, zorder=2))
        if lab:
            ax.text(left + wd / 2, y + h / 2, lab, ha="center", va="center",
                    color="white", fontsize=size, zorder=3)
        left += wd


@figure("select_on_test")
def select_on_test(fig):
    """The winner's curse: the score that picked a model is no longer an
    honest score for it, which is why a third split exists."""
    xte, tte = _sin_data(4000, seed=99)

    def draw(seed, nval=25, n_cand=10):
        rng = np.random.default_rng(seed)
        xtr, ttr = _sin_data(40, seed=1000 + seed)
        xva, tva = _sin_data(nval, seed=5000 + seed)
        val, fresh = [], []
        for _ in range(n_cand):
            idx = rng.choice(40, 32, replace=False)
            w = _poly_fit(xtr[idx], ttr[idx], 5)
            val.append(float(((_poly_eval(w, xva) - tva) ** 2).mean()))
            fresh.append(float(((_poly_eval(w, xte) - tte) ** 2).mean()))
        return np.array(val), np.array(fresh)

    val, fresh = draw(5)
    k = int(np.argmin(val))
    best = int(np.argmin(fresh))
    assert fresh[k] > val[k] and best != k
    fig.text(0.5, 0.955, "Ten candidates, scored on the set that also "
                         "chooses between them", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.075, 0.30, 0.40, 0.50])
    cand = np.arange(1, len(val) + 1)
    for c, v, f in zip(cand, val, fresh):
        ax.plot([c, c], [v, f], color=GRID, lw=1.2, zorder=1)
    ax.plot(cand, val, "o", color=GOLD, ms=7, label="score on that set")
    ax.plot(cand, fresh, "o", color=TEST, ms=7, label="score on fresh data")
    ax.plot(cand[k], val[k], "o", color=CHOSEN, ms=15, mfc="none", mew=2.4,
            zorder=5)
    ax.annotate("validation picks this", xy=(cand[k], val[k]),
                xytext=(6.4, 0.0415), color=CHOSEN,
                fontsize=10, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=CHOSEN, lw=1.2))
    ax.annotate("actual best", xy=(cand[best], fresh[best]),
                xytext=(1.9, 0.059), color=TEST,
                fontsize=10, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=TEST, lw=1.2))
    ax.set_xticks(cand)
    ax.set_xlim(0.3, len(val) + 0.7)
    ax.set_ylim(0.036, 0.080)
    ax.set_xlabel("candidate model")
    ax.set_ylabel("squared error")
    ax.legend(fontsize=9.5, loc="upper right", ncol=1)
    despine(ax, keep=("left", "bottom"))

    ax2 = canvas(fig)
    ax2.plot([5.05, 5.05], [0.30, 3.05], color=GRID, lw=1.2)
    ax2.text(5.30, 2.30, "The winning score is the smallest of ten\n"
                         "noisy numbers, so it is biased low.",
             color=INK, fontsize=12, va="center", linespacing=1.6)
    _split_bar(ax2, 5.30, 1.10, 3.30, 0.32, [0.55, 0.22, 0.23],
               ["train", "val.", "test"], [TRAIN, GOLD, TEST], size=10)
    ax2.text(5.30, 0.78, "fit on train, choose with validation, report on "
                         "test", color=GREEN, fontsize=10.8, va="center")


@figure("holdout_idea")
def holdout_idea(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Never score on the data you fitted on",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    _split_bar(ax, 0.55, 2.62, 7.90, 0.50,
               (0.6, 0.2, 0.2),
               (r"$\mathcal{D}_{\mathrm{train}}$",
                r"$\mathcal{D}_{\mathrm{val}}$",
                r"$\mathcal{D}_{\mathrm{test}}$"),
               (BLUE, GOLD, RED), size=12)
    ax.text(0.55, 3.24, r"$\mathcal{D}$", color=INK, fontsize=13,
            va="center")
    rows = [
        (BLUE, "1.", r"Split $\mathcal{D}$ at random into three parts"),
        (BLUE, "2.", r"Fit every candidate model on "
                     r"$\mathcal{D}_{\mathrm{train}}$"),
        (GOLD, "3.", r"Score each on $\mathcal{D}_{\mathrm{val}}$"),
        (GREEN, "4.", r"Keep model with best validation score"),
        (RED, "5.", r"Report error on $\mathcal{D}_{\mathrm{test}}$"),
    ]
    for i, (color, n, text) in enumerate(rows):
        y = 2.24 - i * 0.35
        ax.text(0.70, y, n, color=color, fontsize=11.5, weight="bold",
                va="center")
        ax.text(1.05, y, text, color=INK, fontsize=11.5, va="center")
    box(ax, 0.55, 0.1, 3.70, 0.44, GOLD, "", fill="#fdf8ef")
    ax.text(2.40, 0.32, "Validation: selection metric", ha="center", va="center",
            color=GOLD, fontsize=12)
    box(ax, 4.75, 0.1, 3.70, 0.44, RED, "", fill="#fdf0f0")
    ax.text(6.60, 0.32, "Test: reporting metric", ha="center", va="center",
            color=RED, fontsize=12)


@figure("kfold_idea")
def kfold_idea(fig):
    """The noisy single split and its cure, on one slide: the spread of 25
    hold-outs on the left, the K rounds that average it away on the right."""
    x, t = _cv_data()
    Ms = np.arange(0, 10)
    rng = np.random.default_rng(0)
    picks, curves = [], []
    for _ in range(25):
        idx = rng.permutation(len(x))
        cut = int(0.7 * len(x))
        tr, va = idx[:cut], idx[cut:]
        e = [float(((_poly_eval(_poly_fit(x[tr], t[tr], M), x[va])
                     - t[va]) ** 2).mean()) for M in Ms]
        curves.append(e)
        picks.append(int(Ms[int(np.argmin(e))]))
    curves = np.array(curves)
    chosen = sorted(set(picks))

    axp = fig.add_axes([0.075, 0.465, 0.305, 0.375])
    for e in curves:
        axp.plot(Ms, e, color=GOLD, lw=0.9, alpha=0.45)
    axp.plot(Ms, np.median(curves, 0), color=INK, lw=2.6)
    axp.set_ylim(0, 0.46)
    axp.set_xlabel("$M$", fontsize=10)
    axp.set_ylabel("validation error", fontsize=10)
    axp.tick_params(labelsize=9)
    axp.set_title(f"{len(curves)} random 70/30 splits", fontsize=11,
                  color=MUTED, pad=6)
    despine(axp, keep=("left", "bottom"))

    ax = canvas(fig)
    ax.text(2.05, 1.00, f"One split is a noisy judge: the winner\nmoves "
                        f"from $M = {min(chosen)}$ to $M = {max(chosen)}$.",
            ha="center", va="center", color=PENALTY, fontsize=11,
            linespacing=1.6)
    ax.plot([4.55, 4.55], [0.70, 3.10], color=GRID, lw=1.2)

    K = 5
    x0, bw = 5.05, 2.95
    for k in range(K):
        y = 2.80 - k * 0.40
        ax.text(x0 - 0.15, y + 0.13, f"round {k + 1}", ha="right",
                va="center", color=MUTED, fontsize=10)
        _split_bar(ax, x0, y, bw, 0.26, [1 / K] * K,
                   ["" for _ in range(K)],
                   [GOLD if j == k else BLUE for j in range(K)])
    ax.add_patch(Rectangle((x0, 3.22), 0.22, 0.15, facecolor=BLUE,
                           edgecolor="none"))
    ax.text(x0 + 0.32, 3.295, "train", color=BLUE, fontsize=10.5,
            va="center")
    ax.add_patch(Rectangle((x0 + 1.10, 3.22), 0.22, 0.15, facecolor=GOLD,
                           edgecolor="none"))
    ax.text(x0 + 1.42, 3.295, "validate", color=GOLD, fontsize=10.5,
            va="center")
    ax.text(x0 + bw / 2, 0.92, r"Average the $K$ scores.", ha="center",
            va="center", color=GREEN, fontsize=12.5)
    note(ax, "Every point is validated exactly once, so the answer no "
             "longer rests on one lucky split.", y=0.32, size=11.5)


@figure("loo_vs_k")
def loo_vs_k(fig):
    """What actually changes with K: measured, not asserted.  One fixed
    model, many resamples, R_CV compared with the risk of the model that
    would really be shipped."""
    N, M, reps = 40, 5, 40
    Ks = [2, 3, 5, 10, N]
    xt, tt = _sin_data(2000, seed=99)
    truth, est = [], {K: [] for K in Ks}
    for d in range(reps):
        xs, ts = _sin_data(N, seed=500 + d)
        truth.append(_rms(_poly_fit(xs, ts, M), xt, tt) ** 2)
        for K in Ks:
            est[K].append(_cv_poly(xs, ts, M, K=K, seed=7 + d)[0])
    T = float(np.mean(truth))
    mu = np.array([float(np.mean(est[K])) for K in Ks])
    sd = np.array([float(np.std(est[K])) for K in Ks])
    assert mu[0] - T > mu[3] - T > 0

    fig.text(0.5, 0.955, f"order {M}, {N} points, {reps} resamples",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.085, 0.235, 0.395, 0.55])
    xx = np.arange(len(Ks))
    ax.errorbar(xx, mu, yerr=sd, fmt="o-", color=GOLD, ms=6, lw=2.2,
                capsize=4)
    ax.axhline(T, color=INK, ls="--", lw=1.4)
    ax.text(2.4, 0.014, "the risk of the model you actually ship",
            color=INK, fontsize=9.5, va="bottom", ha="center")
    ax.set_xticks(xx)
    ax.set_xticklabels(["2", "3", "5", "10", "$N$"])
    ax.set_xlim(-0.4, len(Ks) - 0.6)
    ax.set_ylim(0, 0.22)
    ax.set_xlabel("$K$")
    ax.set_ylabel(r"$R_{\mathrm{CV}}$")
    despine(ax, keep=("left", "bottom"))

    ax2 = canvas(fig)
    ax2.plot([5.05, 5.05], [0.42, 3.05], color=GRID, lw=1.2)
    ax2.text(5.30, 3.14, r"$R_{\mathrm{CV}} \;=\; \frac{1}{K} "
                         r"\sum_k \; (\mathrm{score\ of\ fold}\ k)$",
             color=INK, fontsize=13.5, va="center")
    ax2.text(5.30, 2.78, "each fold is scored by the model fitted "
                         "without it", color=MUTED, fontsize=10, va="center")
    rows = [
        (BLUE, "$K = 2$", f"$+${mu[0] - T:.3f} too high", ""),
        (GOLD, "$K = 10$", f"$+${mu[3] - T:.3f}", ""),
        (GREEN, "$K = N$", f"$+${mu[4] - T:.3f}, for $N$ fits", ""),
    ]
    y = 2.32
    for color, name, delta, why in rows:
        ax2.text(5.30, y, name, color=color, fontsize=11.5, weight="bold",
                 va="center")
        ax2.text(6.15, y, delta, color=INK, fontsize=11, va="center")
        ax2.text(5.30, y - 0.36, why, color=MUTED, fontsize=10, va="center",
                 linespacing=1.5)
        y -= 0.74
    note(ax2, r"$K = 10$ is the default (good balance).", y=0.14, size=11)


@figure("cv_cost")
def cv_cost(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.06, "number of fits   =   $K$ folds   ×   candidate "
                         "models   ×   repeats", ha="center",
            va="center", color=INK, fontsize=14.5)
    rows = [
        (BLUE, "one knob, ten orders, $K = 10$", "10 × 10", "100"),
        (GOLD, "two knobs, a 10 × 10 grid", "10 × 100", "1 000"),
        (PENALTY, "the same, five repeated partitions", "10 × 100 × 5",
         "5 000"),
    ]
    x = (0.55, 4.45, 7.10)
    for xi, head, ha in zip(x, ("", "arithmetic", "fits"),
                            ("left", "left", "right")):
        ax.text(xi, 2.40, head, color=MUTED, fontsize=11, va="center",
                ha=ha)
    ax.plot([0.47, 8.53], [2.24, 2.24], color=GRID, lw=1.2)
    for i, (color, name, arith, total) in enumerate(rows):
        y = 1.96 - i * 0.42
        ax.text(x[0], y, name, color=color, fontsize=11.5, va="center")
        ax.text(x[1], y, arith, color=MUTED, fontsize=11, va="center")
        ax.text(x[2], y, total, color=color, fontsize=12, va="center",
                ha="right", weight="bold")
        if i:
            ax.plot([0.47, 8.53], [y + 0.21, y + 0.21], color=LIGHT, lw=1.0)
    ax.plot([0.47, 8.53], [0.92, 0.92], color=GRID, lw=1.2)


def _cells(ax, x, y, n, w, h, colors, gap=0.0, lw=1.0):
    """A strip of n cells, one colour each: the deck's fold diagram."""
    for j in range(n):
        ax.add_patch(Rectangle((x + j * (w + gap), y), w, h,
                               facecolor=colors[j], edgecolor="white",
                               lw=lw, zorder=2))


@figure("cv_variants")
def cv_variants(fig):
    ax = canvas(fig)
    xa, xb, wide = 0.45, 4.72, 3.80

    def title(x, y, text, color):
        ax.text(x, y, text, color=color, fontsize=12, weight="bold",
                va="center")

    def cap(x, y, text):
        ax.text(x, y, text, color=MUTED, fontsize=10.5, va="center")

    # stratified: five folds of four rows, one rare case in each
    title(xa, 3.24, "stratified: imbalanced data", BLUE)
    fgap = 0.08
    cw = (wide - 4 * fgap) / 20
    for k in range(5):
        x0 = xa + k * (4 * cw + fgap)
        _cells(ax, x0, 2.58, 4, cw, 0.40,
               [RED if j == 2 else BLUE for j in range(4)])
        ax.text(x0 + 2 * cw, 2.42, f"{k + 1}", color=MUTED, fontsize=9,
                ha="center", va="center")
    cap(xa, 2.16, "Folds keep the same share of the rare class (red)")

    # grouped: the same rows, reordered so a group is never split
    title(xb, 3.24, "grouped: separating the classes", GOLD)
    ramp = [plt.get_cmap("YlOrBr")(v) for v in (0.28, 0.42, 0.56, 0.70, 0.86)]
    order = [0, 3, 1, 4, 0, 2, 3, 1, 2, 4, 1, 0, 4, 2, 3, 0, 1, 4, 2, 3]
    cw2 = wide / 20
    _cells(ax, xb, 2.82, 20, cw2, 0.26, [ramp[g] for g in order])
    sorted_cols = []
    for g in range(5):
        sorted_cols += [ramp[g]] * 4
    cwb = (wide - 4 * 0.06) / 20
    for k in range(5):
        _cells(ax, xb + k * (4 * cwb + 0.06), 2.46, 4, cwb, 0.26,
               sorted_cols[4 * k:4 * k + 4])
    arrow(ax, (xb - 0.22, 2.98), (xb - 0.22, 2.50), color=MUTED, lw=1.2)
    cap(xb, 2.16, "Rows are regrouped: one fold per subject")

    ax.plot([0.42, 8.58], [1.96, 1.96], color=LIGHT, lw=1.0)

    # time series: an expanding window, always validating on the future
    title(xa, 1.72, "time series: ordered data", GREEN)
    cw3, ch = wide / 20, 0.22
    for r in range(3):
        y = 1.02 - r * 0.28
        cols = [LIGHT] * 20
        for j in range(6 + 4 * r):
            cols[j] = BLUE
        for j in range(6 + 4 * r, 9 + 4 * r):
            cols[j] = GOLD
        _cells(ax, xa, y, 20, cw3, ch, cols)
    ax.text(xa + wide + 0.06, 0.82, "time", color=MUTED, fontsize=9.5,
            va="center")
    cap(xa, 0.18, "Train on the past, score on the future")

    # blocked: a held-out block, with a buffer around it
    title(xb, 1.72, "blocked: correlated neighbours", PURPLE)
    nc, nr = 14, 4
    cw4, ch4 = 0.235, 0.20
    x0 = xb + (wide - nc * cw4) / 2
    for r in range(nr):
        cols = []
        for c in range(nc):
            if 6 <= c <= 8 and 1 <= r <= 2:
                cols.append(GOLD)
            elif 5 <= c <= 9 and 0 <= r <= 3:
                cols.append(LIGHT)
            else:
                cols.append(BLUE)
        _cells(ax, x0, 0.62 + (nr - 1 - r) * (ch4 + 0.025), nc, cw4, ch4,
               cols)
    ax.text(x0 + 7 * cw4, 0.46, "held out", color=GOLD, fontsize=9.5,
            ha="center", va="center")
    cap(xb, 0.18, "Neighbourhoods are held out together, possibly with a "
                  "buffer")

# ==========================================================================
# 4. hyper-parameter optimisation
#    (the landscape and Bayesian-optimisation material of Advanced Topics in
#    Data Science, session 3, redrawn on this deck's canvas)
# ==========================================================================
def _val_surface(le, dep):
    """A plausible validation-AUC surface over (log learning rate, depth)."""
    return (0.86 - 0.055 * (le + 1.5) ** 2 - 0.0022 * (dep - 6.0) ** 2
            - 0.010 * (le + 1.5) * (dep - 6.0))


def _bo_target(x):
    """The expensive unknown: a hyper-parameter in, a validation loss out."""
    return np.sin(3 * np.pi * x) * 0.45 + (x - 0.55) ** 2 * 3.2


def _gp(xs, ys, grid, ell=0.15, sig=0.09, amp=0.55):
    """The surrogate: a Gaussian-process mean and its uncertainty band."""
    def k(a, b):
        return np.exp(-((a[:, None] - b[None, :]) ** 2) / (2 * ell ** 2))

    K = k(xs, xs) + sig ** 2 * np.eye(len(xs))
    mu = k(grid, xs) @ np.linalg.solve(K, ys)
    v = 1.0 - np.einsum("ij,ij->i", k(grid, xs),
                        np.linalg.solve(K, k(grid, xs).T).T)
    return mu, amp * np.sqrt(np.clip(v, 1e-6, None))


def _ei(mu, sd, best):
    """Expected improvement below the best score so far."""
    from scipy.stats import norm
    z = (best - mu) / sd
    return (best - mu) * norm.cdf(z) + sd * norm.pdf(z)


@figure("hyper_hard")
def hyper_hard(fig):
    ax = canvas(fig)
    rows = [
        (RED, "expensive", "one trial is a fit (or a cross-validation loop)"),
        (GOLD, "noisy", "redraw the training samples can change the score"),
        (BLUE, "no gradient", "descent is not possible"),
        (PURPLE, "not convex", "landscape hard to explore"),
        (GOLD, "mixed", "continuous, integer and categorical together"),
        (GREEN, "conditional", "e.g.: hyper-parameters depend on the choice of kernel"),
    ]
    for i, (color, name, why) in enumerate(rows):
        y = 3.26 - i * 0.50
        ax.text(0.55, y, name, color=color, fontsize=13, weight="bold",
                va="center")
        ax.text(2.70, y, why, color=INK, fontsize=11.5, va="center")
        if i:
            ax.plot([0.47, 8.53], [y + 0.25, y + 0.25], color=LIGHT, lw=1.0)
    note(ax, "The best methods spend few evaluations, and where they are worth.",
         y=0.22, size=11.5)


@figure("log_scale")
def log_scale(fig):
    rng = np.random.default_rng(4)
    n = 40
    lin = rng.uniform(1e-4, 1.0, n)
    log = 10 ** rng.uniform(-4, 0, n)

    fig.text(0.5, 0.955, "Same range, same budget", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    axes = [fig.add_axes([0.07, 0.57, 0.90, 0.25]),
            fig.add_axes([0.07, 0.28, 0.90, 0.25])]
    for ax, s, name, color in ((axes[0], lin, "uniform on "
                                              "[$10^{-4}$, $1$]", RED),
                               (axes[1], log, "log-uniform on "
                                              "[$10^{-4}$, $1$]", GREEN)):
        ax.plot(s, np.zeros_like(s), "|", color=color, ms=26, mew=2)
        ax.set_xscale("log")
        ax.set_xlim(6e-5, 1.6)
        ax.set_ylim(-1, 1)
        ax.set_yticks([])
        ax.text(7.5e-5, 0.58, name, fontsize=12, color=color)
        ax.text(7.5e-5, -0.72, f"{int((s < 0.01).sum())} of {n} draws below "
                               f"0.01", fontsize=10.5, color=MUTED)
        for side in ("left", "top", "right"):
            ax.spines[side].set_visible(False)
    axes[0].set_xticklabels([])
    axes[1].set_xlabel("learning rate")
    fig.text(0.5, 0.045, "Learning rates, $C$, $\\gamma$, $\\lambda$: always "
                         "log. Depths, counts, folds: linear integers.",
             ha="center", va="center", color=INK, fontsize=11.5)


@figure("landscape_1d")
def landscape_1d(fig):
    rng = np.random.default_rng(2)
    lam = np.logspace(-5, 2, 400)
    loss = 0.30 + 0.052 * (np.log10(lam) + 1.6) ** 2
    probe = np.logspace(-5, 2, 22)
    meas = (0.30 + 0.052 * (np.log10(probe) + 1.6) ** 2
            + rng.normal(0, 0.012, len(probe)))
    k = int(np.argmin(loss))

    ax = fig.add_axes([0.085, 0.235, 0.39, 0.56])
    ax.axhspan(loss[k], loss[k] + 0.02, color=CHOSEN, alpha=0.16)
    ax.plot(lam, loss, color=BLUE, lw=2.6, label="true validation loss")
    ax.plot(probe, meas, "o", color=TEST, ms=5, label="measured validation loss")
    ax.axvline(lam[k], color=MUTED, ls="--", lw=1.2)
    ax.set_xscale("log")
    ax.set_ylim(0.14, 1.05)
    ax.set_xlabel(r"$\lambda$  (log scale)")
    ax.set_ylabel("validation loss")
    ax.legend(fontsize=9.5, loc="upper center")
    despine(ax, keep=("left", "bottom"))

    ax2 = canvas(fig)
    ax2.plot([5.00, 5.00], [0.42, 3.05], color=GRID, lw=1.2)
    column(ax2, 5.25, 3.02, 3.4, "Interpretation", [
        "smooth on a log scale",
        "flat near the optimum",
    ], INK, leading=0.30, item_size=11)
    ax2.text(5.25, 1.72, "Aim for the right order of magnitude,\nnot the "
                         "exact minimum.", color=PENALTY, fontsize=11,
             va="center", linespacing=1.6)


@figure("landscape_2d")
def landscape_2d(fig):
    le = np.linspace(-4, 0, 300)
    dep = np.linspace(2, 14, 300)
    LE, DEP = np.meshgrid(le, dep)
    auc = _val_surface(LE, DEP)

    fig.text(0.5, 0.955, "Two knobs, and they are not independent",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.075, 0.235, 0.355, 0.56])
    im = ax.contourf(10 ** LE, DEP, auc, levels=22, cmap="viridis")
    ax.contour(10 ** LE, DEP, auc, levels=10, colors="white", linewidths=0.6,
               alpha=0.5)
    j, i = np.unravel_index(int(np.argmax(auc)), auc.shape)
    ax.plot([10 ** LE[j, i]], [DEP[j, i]], "*", color="white", ms=18,
            zorder=4)
    ax.set_xscale("log")
    ax.set_xlabel(r"learning rate $\eta$  (log scale)")
    ax.set_ylabel("max depth")
    cax = fig.add_axes([0.445, 0.235, 0.013, 0.56])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("validation AUC", fontsize=10)
    cb.ax.tick_params(labelsize=8)

    ax2 = canvas(fig)
    ax2.plot([5.15, 5.15], [0.42, 3.05], color=GRID, lw=1.2)
    column(ax2, 5.38, 3.02, 3.3, "Interpretation", [
        "No need for exact best,\nbut a 'good region'",
        "Parameters are not independent",
    ], INK, leading=0.30, item_size=11)
    ax2.text(5.38, 0.58, "The star is not worth chasing to the last decimal.",
             color=PENALTY, fontsize=10.5, va="center", linespacing=1.5)


@figure("search_compare")
def search_compare(fig):
    rng = np.random.default_rng(0)
    le = np.linspace(-4, 0, 200)
    dep = np.linspace(2, 14, 200)
    LE, DEP = np.meshgrid(le, dep)
    auc = _val_surface(LE, DEP)

    picks = {}
    g = np.meshgrid(np.linspace(-3.5, -0.5, 5), np.linspace(3, 13, 5))
    picks["grid search"] = (g[0].ravel(), g[1].ravel())
    picks["random search"] = (rng.uniform(-4, 0, 25), rng.uniform(2, 14, 25))
    bx, by = list(rng.uniform(-4, 0, 6)), list(rng.uniform(2, 14, 6))
    for _ in range(19):
        k = int(np.argmax([_val_surface(a, b) for a, b in zip(bx, by)]))
        bx.append(float(np.clip(bx[k] + rng.normal(0, 0.45), -4, 0)))
        by.append(float(np.clip(by[k] + rng.normal(0, 1.5), 2, 14)))
    picks["Bayesian optimisation"] = (np.array(bx), np.array(by))

    fig.text(0.5, 0.955, "The same surface, the same budget of 25 trials",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    bests = {}
    for c, (name, (px, py)) in enumerate(picks.items()):
        ax = fig.add_axes([0.055 + c * 0.325, 0.235, 0.275, 0.52])
        ax.contourf(LE, DEP, auc, levels=18, cmap="viridis", alpha=0.92)
        ax.scatter(px, py, s=26, color="white", edgecolors=INK, lw=0.7,
                   zorder=4)
        best = max(_val_surface(a, b) for a, b in zip(px, py))
        bests[name] = best
        ax.set_title(f"{name}\nbest AUC {best:.4f}", fontsize=11.5, pad=6)
        ax.set_xlabel(r"$\log_{10} \eta$", fontsize=10)
        ax.tick_params(labelsize=8.5)
        if c:
            ax.set_yticklabels([])
        else:
            ax.set_ylabel("max depth", fontsize=10)


@figure("bo_surrogate")
def bo_surrogate(fig):
    grid = np.linspace(0, 1, 400)
    xs = np.array([0.08, 0.42, 0.88])
    ys = _bo_target(xs)
    mu, sd = _gp(xs, ys, grid)

    left = fig.add_axes([0.07, 0.235, 0.41, 0.55])
    right = fig.add_axes([0.565, 0.235, 0.41, 0.55])
    for ax in (left, right):
        ax.plot(xs, ys, "o", color=INK, ms=8, zorder=5)
        ax.set_ylim(-1.5, 2.3)
        ax.set_xlabel("hyper-parameter $x$")
        despine(ax, keep=("left", "bottom"))
    right.set_yticklabels([])

    left.set_title("known numbers", fontsize=11.5, pad=6)
    left.set_ylabel("validation loss")
    for x, y in zip(xs, ys):
        left.plot([x, x], [-1.5, y], color=MUTED, lw=1, ls=":")
    left.text(0.5, -1.15, "curve between them is unknown", ha="center",
              fontsize=10, color=MUTED, linespacing=1.4)

    right.set_title("what the surrogate believes", fontsize=11.5, pad=6)
    right.plot(grid, mu, color=BLUE, lw=2.4, label="mean: the best guess")
    right.fill_between(grid, mu - 2 * sd, mu + 2 * sd, color=BLUE, alpha=0.16,
                       label="band: how wrong it could be")
    right.legend(fontsize=9, loc="upper left")
    right.annotate("tight where measured", xy=(xs[1], ys[1]),
                   xytext=(0.22, -1.18), fontsize=9.5, color=GOLD,
                   ha="center", linespacing=1.4,
                   arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=1.2))
    right.annotate("wide where not measured", xy=(0.66, (mu - 2 * sd)[264]),
                   xytext=(0.84, -1.18), fontsize=9.5, color=PENALTY,
                   ha="center", linespacing=1.4,
                   arrowprops=dict(arrowstyle="-|>", color=PENALTY, lw=1.2))
    _credit(fig, "surrogate is nearly free to query")


@figure("bo_acquisition")
def bo_acquisition(fig):
    grid = np.linspace(0, 1, 400)
    xs = np.array([0.08, 0.30, 0.42, 0.86])
    ys = _bo_target(xs)
    mu, sd = _gp(xs, ys, grid)

    fig.text(0.5, 0.955, "Where to spend the next fit: exploit the mean, or "
                         "explore the band", ha="center", va="center",
             color=MUTED, fontsize=12.5)
    top = fig.add_axes([0.075, 0.50, 0.90, 0.36])
    bot = fig.add_axes([0.075, 0.255, 0.90, 0.195])
    top.plot(grid, mu, color=BLUE, lw=2.4)
    top.fill_between(grid, mu - 2 * sd, mu + 2 * sd, color=BLUE, alpha=0.16)
    top.plot(xs, ys, "o", color=INK, ms=7, zorder=5)
    top.axhline(ys.min(), color=MUTED, ls=":", lw=1.4)
    top.text(0.995, ys.min() + 0.24, r"best $f^\star$ so far", fontsize=9.5,
             color=MUTED, ha="right")
    top.set_ylabel("validation loss", fontsize=10.5)
    top.set_xticklabels([])
    top.set_ylim(-1.5, 2.3)
    top.annotate("exploit:\nthe mean is low", xy=(0.52, -0.33),
                 xytext=(0.18, -1.15), fontsize=9.5, color=GOLD, ha="center",
                 linespacing=1.4,
                 arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=1.2))
    top.annotate("explore:\nthe band is wide", xy=(0.64, 0.55),
                 xytext=(0.66, 1.65), fontsize=9.5, color=PENALTY,
                 ha="center", linespacing=1.4,
                 arrowprops=dict(arrowstyle="-|>", color=PENALTY, lw=1.2))
    despine(top, keep=("left", "bottom"))

    ei = _ei(mu, sd, ys.min())
    ucb = -(mu - 2.0 * sd)
    for sc, lab, color in ((ei / ei.max(), "expected improvement", GREEN),
                           ((ucb - ucb.min()) / np.ptp(ucb),
                            r"UCB  ($\kappa = 2$)", PURPLE)):
        bot.plot(grid, sc, color=color, lw=2.2, label=lab)
        bot.axvline(grid[int(np.argmax(sc))], color=color, ls="--", lw=1.4)
    bot.set_yticks([])
    bot.set_xlabel("hyper-parameter $x$")
    bot.set_ylabel("acquisition", fontsize=10.5)
    bot.legend(fontsize=9.5, loc="upper left", ncol=2)
    despine(bot, keep=("bottom",))
    fig.text(0.5, 0.032, "Maximise the acquisition, never the expensive "
                         "function itself: the dashed lines are the two "
                         "recommendations.", ha="center", va="center",
             color=INK, fontsize=11)


@figure("bo_loop")
def bo_loop(fig):
    ax = canvas(fig)
    cards = [
        (BLUE, "fit the surrogate", "on the trials\nalready computed"),
        (GREEN, "maximise the\nacquisition", "cheap: thousands of\ncandidates"),
        (RED, "evaluate once,\nfor real", "one full CV run:\nminutes"),
        (GOLD, "add the result", "and start again"),
    ]
    w, gap = 1.84, 0.30
    for i, (color, title, body) in enumerate(cards):
        x = 0.55 + i * (w + gap)
        box(ax, x, 1.70, w, 0.98, color, "", fill="white", lw=2.0)
        ax.text(x + w / 2, 2.42, title, ha="center", va="center", color=color,
                fontsize=12, weight="bold", linespacing=1.4)
        ax.text(x + w / 2, 1.98, body, ha="center", va="center", color=MUTED,
                fontsize=10, linespacing=1.4)
        if i < len(cards) - 1:
            arrow(ax, (x + w + 0.03, 2.19), (x + w + gap - 0.03, 2.19),
                  color=MUTED, lw=1.8)
    ax.annotate("", xy=(1.47, 1.62), xytext=(7.45, 1.62),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.6,
                                connectionstyle="arc3,rad=-0.10"))
    ax.text(W / 2, 0.98, "repeat until the budget runs out", ha="center",
            va="center", color=MUTED, fontsize=11)
    note(ax, "Start with five to ten random trials: with no data the "
             "surrogate has nothing to model.", y=0.58, size=11.5,
         color=INK)


@figure("optuna_code")
def optuna_code(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "In practice: the search space is Python",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    code = [
        "def objective(trial):",
        '    depth = trial.suggest_int("depth", 3, 12)',
        '    lr    = trial.suggest_float("lr", 1e-4, 0.3, log=True)',
        "",
        "    model = XGBClassifier(max_depth=depth, learning_rate=lr)",
        '    return cross_val_score(model, X, y, cv=5,',
        '                           scoring="roc_auc").mean()',
        "",
        'study = optuna.create_study(direction="maximize")',
        "study.optimize(objective, n_trials=100)",
    ]
    ax.add_patch(FancyBboxPatch((0.45, 0.80), 5.55, 2.38,
                                boxstyle="round,pad=0.10,rounding_size=0.08",
                                linewidth=0, facecolor="#f4f5f7", zorder=1))
    for i, line in enumerate(code):
        ax.text(0.60, 3.02 - i * 0.24, line, family="monospace",
                fontsize=10, color=INK, va="center", zorder=2)
    ax.annotate("log for learning rate", xy=(5.55, 2.54),
                xytext=(7.30, 2.76), color=GREEN, fontsize=10.5, ha="center",
                va="center", linespacing=1.5,
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.4))
    ax.annotate("one trial is a whole\ncross-validation (expensive)",
                xy=(4.55, 1.82), xytext=(7.30, 1.70), color=RED,
                fontsize=10.5, ha="center", va="center", linespacing=1.5,
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.4))
    note(ax, "The space is defined while the trial runs, so a knob can "
             "depend on another one.", y=0.48,
         size=11.5)
    # note(ax, "Optuna's default sampler is TPE: it models the good trials and "
    #          "the bad ones separately.", y=0.16, size=11, color=MUTED)


@figure("optuna_history")
def optuna_history(fig):
    rng = np.random.default_rng(6)
    n = 120
    trials = np.arange(1, n + 1)
    vals = 0.735 + 0.055 * (1 - np.exp(-trials / 22)) + rng.normal(0, 0.014, n)
    vals[:10] = 0.70 + rng.normal(0, 0.03, 10)
    best = np.maximum.accumulate(vals)

    fig.text(0.5, 0.955, "when to stop paying",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.085, 0.235, 0.39, 0.56])
    ax.axvspan(0, 10, color=LIGHT)
    ax.axvspan(70, n, color=CHOSEN, alpha=0.10)
    ax.plot(trials, vals, "o", color=MUTED, ms=3.5, label="trial")
    ax.plot(trials, best, color=TEST, lw=2.4, label="best so far")
    ax.set_xlabel("trial")
    ax.set_ylabel("validation AUC")
    ax.set_ylim(0.64, 0.82)
    ax.legend(fontsize=9.5, loc="lower right")
    despine(ax, keep=("left", "bottom"))

    ax2 = canvas(fig)
    ax2.plot([5.00, 5.00], [0.42, 3.05], color=GRID, lw=1.2)
    column(ax2, 5.25, 3.02, 3.4, "Interpretation", [
        "First ten trials are random start-up\nnothing is modelled yet",
        "The best performance curve climbs\nas the search finds better parameters sets",
        "It ends flat: more budget\nis not improving anymore",
    ], INK, leading=0.30, item_size=11)
    gain = float(best[-1] - best[69])
    spread = float(np.std(vals[70:]))
    assert gain < spread
    ax2.text(5.25, 0.62, f"Here the last {n - 70} trials moved the best "
                         f"score by\n{gain:.3f}, against a trial-to-trial "
                         f"spread of {spread:.3f}:\nthat is the signal to "
                         f"stop.", color=PENALTY, fontsize=10.5,
             va="center", linespacing=1.5)


@figure("pruning")
def pruning(fig):
    rng = np.random.default_rng(8)
    steps_ = np.arange(1, 101)

    fig.text(0.5, 0.955, "Stop a hopeless trial before it finishes",
             ha="center", va="center", color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.085, 0.235, 0.39, 0.56])
    kept = 0
    for _ in range(24):
        ceiling = rng.uniform(0.70, 0.81)
        curve = (ceiling * (1 - np.exp(-steps_ / rng.uniform(8, 26)))
                 + rng.normal(0, 0.004, 100))
        if ceiling > 0.756:
            ax.plot(steps_, curve, color=CHOSEN, lw=1.7, alpha=0.9)
            kept += 1
        else:
            stop = int(rng.integers(14, 34))
            ax.plot(steps_[:stop], curve[:stop], color=MUTED, lw=1.1,
                    alpha=0.75)
            ax.plot([steps_[stop - 1]], [curve[stop - 1]], "x", color=TEST,
                    ms=7, mew=1.8)
    ax.set_xlabel("rounds within one trial")
    ax.set_ylabel("validation AUC")
    despine(ax, keep=("left", "bottom"))

    ax2 = canvas(fig)
    ax2.plot([5.00, 5.00], [0.42, 3.05], color=GRID, lw=1.2)
    code = [
        "for round in trial:",
        "    s = score(round)",
        "    report(s, round)",
        "",
        "    if s < median(past, round):",
        "        prune(trial)",
    ]
    ax2.add_patch(FancyBboxPatch((5.25, 1.52), 3.55, 1.62,
                                 boxstyle="round,pad=0.10,rounding_size=0.08",
                                 linewidth=0, facecolor="#f4f5f7", zorder=1))
    for i, line in enumerate(code):
        ax2.text(5.42, 2.98 - i * 0.25, line, family="monospace",
                 fontsize=10.5, color=INK, va="center", zorder=2)
    ax2.text(5.25, 1.18, f"Here {24 - kept} of 24 trials were pruned "
                         f"(red crosses).", color=INK, fontsize=11,
             va="center")
    ax2.text(5.25, 0.82, "The budget goes to the survivors.",
             color=GREEN, fontsize=11, va="center")


# ==========================================================================
# 5. information criteria
# ==========================================================================
@figure("ic_idea")
def ic_idea(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "Keep the likelihood, charge for the parameters",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    box(ax, 1.05, 2.42, 6.90, 0.72, INK, "", fill="white", lw=1.8)
    ax.text(W / 2, 2.78, r"criterion $\;=\;$ fit $\;-\;$ penalty",
            ha="center", va="center", color=INK, fontsize=18)
    ax.annotate("", xy=(4.35, 2.38), xytext=(3.95, 1.98),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6))
    ax.text(3.89, 1.92, r"$\ln p(x \mid \hat{\theta}_{ML})$", ha="right",
            va="center", color=BLUE, fontsize=12)
    ax.annotate("", xy=(5.85, 2.38), xytext=(6.25, 1.98),
                arrowprops=dict(arrowstyle="-|>", color=PENALTY, lw=1.6))
    ax.text(6.31, 1.92, r"a function of $M_j$ and $N$", ha="left",
            va="center", color=PENALTY, fontsize=12)
    column(ax, 0.55, 1.54, 3.9, "Idea", [
        "Maximised likelihood is optimistic",
        "Optimism grows with the number\nof free parameters",
    ], INK, leading=0.30, item_size=11)
    column(ax, 4.90, 1.54, 3.9, "Benefits", [
        "No folds / refits",
        "Single number per candidate model",
    ], GREEN, leading=0.30, item_size=11)
    ax.plot([4.65, 4.65], [0.46, 1.60], color=GRID, lw=1.2)
    note(ax, r"$M_j$ is the number of free parameters; $N$ is the number of data points.", y=0.18, size=11)


@figure("eq_aic")
def eq_aic(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.20, r"$\mathrm{AIC}(j) \;=\; \ln p(x \mid "
                         r"\hat{\theta}_{ML}) \;-\; M_j$",
            ha="center", va="center", color=INK, fontsize=24)
    ax.annotate("", xy=(6.55, 2.88), xytext=(6.95, 2.42),
                arrowprops=dict(arrowstyle="-|>", color=PENALTY, lw=1.6))
    ax.text(7.0, 2.36, "one unit per parameter", ha="left", va="center",
            color=PENALTY, fontsize=11)
    column(ax, 0.55, 2.00, 3.9, "Origins", [
        "Estimate the expected Kullback–Leibler\ndistance to the truth",
        r"Models the optimism of $\ln p(x \mid \hat{\theta})$ is $\approx M_j$",
        "Asymptotic and assumes maximum likelihood estimator",
    ], INK, leading=0.30, item_size=11)
    column(ax, 4.90, 2.00, 3.9, "Remarks", [
        "Aims at the best prediction,\nnot at the true model",
        "Penalty does not grow with $N$",
        "Keeps choosing richer models\nas $N \\to \\infty$",
    ], GOLD, leading=0.30, item_size=11)
    ax.plot([4.65, 4.65], [0.52, 2.06], color=GRID, lw=1.2)
    note(ax, r"Often written to be minimised: $-2 \ln p(x \mid \hat{\theta}) + 2 M_j$.",
         y=0.10, size=11)


@figure("eq_bic")
def eq_bic(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "also called \"minimum description length\"",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 2.84, r"$\mathrm{BIC}(j) \;=\; \ln p(x \mid "
                         r"\hat{\theta}_{ML}) \;-\; \frac{1}{2} M_j "
                         r"\log N$",
            ha="center", va="center", color=INK, fontsize=24)
    ax.annotate("", xy=(6.30, 2.48), xytext=(6.85, 2.02),
                arrowprops=dict(arrowstyle="-|>", color=PENALTY, lw=1.6))
    ax.text(6.91, 1.96, "grows with $N$", ha="left", va="center",
            color=PENALTY, fontsize=11)
    column(ax, 0.55, 1.58, 3.9, "Origins", [
        "Laplace approximation of model's evidence",
        r"$\log p(\mathcal{D} \mid \mathcal{M}) \approx \mathrm{BIC} + O(1)$",
    ], INK, leading=0.30, item_size=11)
    column(ax, 4.90, 1.58, 3.9, "Remarks", [
        "Aims at the true model, hoping it is\namong the candidates",
        r"Heavier than AIC for $N > 8$",
    ], GREEN, leading=0.30, item_size=11)
    ax.plot([4.65, 4.65], [0.46, 1.64], color=GRID, lw=1.2)
    # note(ax, "No integrals, no held-out data.", y=0.18, size=11)
    note(ax, r"As a minimiser: $-2\ln p(x \mid \hat{\theta}) + M \ln N$",
         y=0.10, size=11)


@figure("eq_ic_conventions")
def eq_ic_conventions(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "scikit-learn's $\\mathtt{aic()}$ and $\\mathtt{bic()}$ return the minimise form",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(2.50, 3.04, "maximise", ha="center", va="center", color=GREEN,
            fontsize=12.5, weight="bold")
    ax.text(6.50, 3.04, "minimise", ha="center", va="center", color=BLUE,
            fontsize=12.5, weight="bold")
    ax.plot([4.50, 4.50], [1.58, 3.14], color=GRID, lw=1.2)
    rows = [
        (GOLD, r"$\ln p(x \mid \hat{\theta}) - M$",
         r"$-2 \ln p(x \mid \hat{\theta}) + 2 M$", "AIC"),
        (GREEN, r"$\ln p(x \mid \hat{\theta}) - \frac{1}{2} M \log N$",
         r"$-2 \ln p(x \mid \hat{\theta}) + M \log N$", "BIC"),
    ]
    for i, (color, left, right, name) in enumerate(rows):
        y = 2.52 - i * 0.70
        ax.text(0.55, y, name, color=color, fontsize=13, weight="bold",
                va="center")
        ax.text(2.50, y, left, color=INK, fontsize=13, ha="center",
                va="center")
        ax.text(6.50, y, right, color=INK, fontsize=13, ha="center",
                va="center")
    note(ax, "A difference of 10 is decisive; a difference of 2 is not.",
         y=0.20, size=11)


@figure("aic_vs_bic")
def aic_vs_bic(fig):
    Ns = np.logspace(1, 4, 200)

    # fig.text(0.5, 0.955, "The two penalties, per parameter",
    #          ha="center", va="center", color=MUTED, fontsize=12.5)
    ax = fig.add_axes([0.095, 0.21, 0.40, 0.58])
    ax.semilogx(Ns, np.full_like(Ns, 1.0), color=GOLD, lw=2.6, label="AIC")
    ax.semilogx(Ns, 0.5 * np.log(Ns), color=GREEN, lw=2.6, label="BIC")
    cross = float(np.exp(2.0))
    ax.set_xlabel("$N$")
    ax.set_ylabel("penalty per parameter")
    ax.legend(fontsize=10)
    despine(ax, keep=("left", "bottom"))

    ax2 = canvas(fig)
    ax2.plot([5.25, 5.25], [0.45, 3.05], color=GRID, lw=1.2)
    column(ax2, 5.50, 3.02, 3.2, "Interpretation", [
        "AIC charges one unit per parameter,\nwhatever the sample size",
        "BIC charges $\\frac{1}{2}\\log N$, so is\nstricter as data accumulates",
    ], INK, leading=0.28, item_size=11)
    ax2.text(5.50, 0.86, r"At $N = 1000$: AIC pays 1 per parameter,"
                         "\nBIC pays 3.5.", color=PENALTY, fontsize=11,
             va="center", linespacing=1.6)
    ax2.text(5.50, 0.34, "On a large sample BIC keeps far fewer parameters.",
             color=MUTED, fontsize=10.5, va="center")


@figure("ic_guidelines")
def ic_guidelines(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "No clear winner — but the differences are "
                         "predictable", ha="center", va="center",
            color=MUTED, fontsize=12.5)
    rows = [
        (GOLD, "BIC penalises harder", "on very big samples it may pick "
         "a model that is too simple"),
        (GREEN, "BIC is consistent", "if the true model is among the "
         "candidates, BIC finds it as $N$ grows"),
        (BLUE, "AIC is usually preferable otherwise",
         "when no candidate is true"),
        (PURPLE, "AIC aims at prediction", "it tends to choose models that "
         "are too complex as $N \\to \\infty$"),
        (RED, "both need $N$ large against $d$",
         r"typically $d \ll \sqrt{N}$; otherwise use the corrected version"),
    ]
    for i, (color, name, why) in enumerate(rows):
        y = 2.92 - i * 0.56
        ax.text(3.55, y, name, ha="right", va="center", color=color,
                fontsize=12, weight="bold")
        ax.text(3.75, y, why, ha="left", va="center", color=INK,
                fontsize=11)
        if i:
            ax.plot([0.45, 8.55], [y + 0.28, y + 0.28], color=LIGHT, lw=1.0)
    note(ax, "A practical habit: report both.", y=0.24, size=11.5)


@figure("eq_aicc")
def eq_aicc(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.18, r"$\mathrm{mAIC}(j) \;=\; \ln p(x \mid "
                         r"\hat{\theta}_{ML}) \;-\; M_j \;-\; "
                         r"\frac{M_j (M_j + 1)}{N - M_j - 1}$",
            ha="center", va="center", color=INK, fontsize=20)
    Ns = np.array([20, 50, 100, 500])
    Mj = 8
    ax.text(1.20, 2.56, r"extra term at $M_j = 8$:", color=MUTED,
            fontsize=11, va="center")
    for i, N in enumerate(Ns):
        x = 3.70 + i * 1.30
        ax.text(x, 2.56, f"$N = {N}$", ha="center", va="center", color=MUTED,
                fontsize=10.5)
        ax.text(x, 2.24, f"{Mj * (Mj + 1) / (N - Mj - 1):.2f}",
                ha="center", va="center", color=PENALTY, fontsize=13)
    column(ax, 0.55, 1.88, 3.9, "Fixes", [
        r"AIC assumption $N \gg M_j$",
        "Vanishing extra term as $N$ grows",
    ], GREEN, leading=0.30, item_size=11)
    column(ax, 4.90, 1.88, 3.9, "When to use it", [
        r"If $N / M_j$ is below about 40",
        r"Blows up as $M_j \to N - 1$",
    ], INK, leading=0.30, item_size=11)
    ax.plot([4.65, 4.65], [0.56, 1.94], color=GRID, lw=1.2)
    note(ax, "Also known as AICc.", y=0.14, size=11)


# ==========================================================================
# 6. the knobs of this course, chosen
# ==========================================================================
@figure("knobs_in_practice")
def knobs_in_practice(fig):
    ax = canvas(fig)
    rows = [
        (r"$\lambda$ in ridge or lasso", BLUE, "cross-validation",
         "cheap, can fit every $\\lambda$ at once"),
        (r"$C$, $\gamma$ in an SVM", GOLD, "grid or random search, with CV",
         "no likelihood, so no information criterion"),
        (r"$K$ in $k$-means" + "\n" + r"$\varepsilon$, MinPts in DBSCAN", GREEN, "elbow, silhouette, stability",
         "no likelihood, and no held-out label"),
        (r"$r$ in NMF", PURPLE, "held-out entries",
         "cross-validation on a mask"),
        (r"$K$ in a Gaussian mixture", RED, "BIC / held-out likelihood",
         "real likelihood, so criteria apply"),
    ]
    x = (0.50, 3.05, 5.70)
    for xi, head in zip(x, ("The knob", "Usual method", "Why")):
        ax.text(xi, 3.36, head, color=MUTED, fontsize=11.5, va="center")
    ax.plot([0.42, 8.58], [3.18, 3.18], color=GRID, lw=1.2)
    for i, (name, color, how, why) in enumerate(rows):
        y = 2.90 - i * 0.42
        ax.text(x[0], y, name, color=color, fontsize=11.5, va="center",
                weight="bold")
        ax.text(x[1], y, how, color=INK, fontsize=11, va="center")
        ax.text(x[2], y, why, color=MUTED, fontsize=10.5, va="center")
        if i:
            ax.plot([0.42, 8.58], [y + 0.21, y + 0.21], color=LIGHT, lw=1.0)
    box(ax, 0.80, 0.10, 7.40, 0.40, INK, "", fill="white", lw=1.5)
    ax.text(W / 2, 0.30, "A likelihood allows AIC and BIC.",
            ha="center", va="center", color=INK, fontsize=12)


# ==========================================================================
# 7. in practice
# ==========================================================================
@figure("method_choice")
def method_choice(fig):
    ax = canvas(fig)
    rows = [
        (INK, "cross-validation", "always applicable",
         "$K$ fits each", "by default"),
        (GREEN, "BIC", "likelihood & parameter count",
         "free", "true model in the list"),
        (GOLD, "AIC", "likelihood & parameter count",
         "free", "good prediction"),
        (PURPLE, "Guided search", "few dozen fits",
         "sequential", "several knobs, useful if fit takes time"),
        (BLUE, "Hold-out set", "lot of data",
         "part of the data", "deep learning"),
    ]
    x = (0.45, 2.30, 4.75, 6.10)
    for xi, head in zip(x, ("Method", "Needs", "Cost", "Reach for it when")):
        ax.text(xi, 3.36, head, color=MUTED, fontsize=11.5, va="center")
    ax.plot([0.42, 8.58], [3.18, 3.18], color=GRID, lw=1.2)
    for i, (color, name, needs, cost, when) in enumerate(rows):
        y = 2.92 - i * 0.48
        ax.text(x[0], y, name, color=color, fontsize=11.5, weight="bold",
                va="center")
        ax.text(x[1], y, needs, color=INK, fontsize=10.5, va="center")
        ax.text(x[2], y, cost, color=INK, fontsize=10.5, va="center")
        ax.text(x[3], y, when, color=MUTED, fontsize=10, va="center")
        if i:
            ax.plot([0.42, 8.58], [y + 0.24, y + 0.24], color=LIGHT, lw=1.0)
    note(ax, "All estimate the generalization in different way.", y=0.34, size=11)


# ==========================================================================
def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course08/img")
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
