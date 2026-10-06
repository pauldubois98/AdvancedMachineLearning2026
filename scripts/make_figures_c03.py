#!/usr/bin/env python3
"""Every figure of Course03 (support vector machines).

One function per figure, registered under the stem the slide deck asks for.
All figures share one canvas (9 x 3.7075 in), which is exactly the content
area pandoc leaves under a slide title, so a figure never has to be resized.
The helpers below are the ones from Course01, kept here so each course
builds on its own.

    python3 scripts/make_figures_c03.py Course03/img [stem ...]
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
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
LIGHT = "#edeef0"
GRID = "#cccfd2"

CYCLE = [BLUE, GREEN, RED, PURPLE, GOLD]


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


def despine(ax, keep=()):
    for side in ("top", "right", "left", "bottom"):
        if side not in keep:
            ax.spines[side].set_visible(False)


def blank(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    despine(ax)






# ==========================================================================
# shared helpers — the drawing conventions come from Course03/imports/figs.py
# ==========================================================================
def _sep_blobs(n=90, seed=3, gap=2.6):
    """Two clearly separable clouds: the slide only works if a gap exists."""
    rng = np.random.default_rng(seed)
    a = rng.normal((-gap / 2, -gap / 2 + 0.3), 0.62, (n // 2, 2))
    b = rng.normal((gap / 2, gap / 2 - 0.3), 0.62, (n // 2, 2))
    X = np.vstack([a, b])
    return X, np.r_[np.zeros(n // 2, int), np.ones(n // 2, int)]


def _moons(n=260, noise=0.22, seed=0):
    from sklearn.datasets import make_moons

    return make_moons(n_samples=n, noise=noise, random_state=seed)


def _scatter_classes(ax, X, y, s=22, alpha=1.0):
    for cls, colour, marker in ((0, BLUE, "o"), (1, RED, "^")):
        m = y == cls
        ax.scatter(X[m, 0], X[m, 1], s=s, color=colour, marker=marker,
                   edgecolors="none", alpha=alpha, zorder=3)


def _svm_field(ax, m, X, res=340, pad=0.7, margins=True):
    """Shade by the decision function, and draw the street: f = -1, 0, +1."""
    gx, gy = np.meshgrid(
        np.linspace(X[:, 0].min() - pad, X[:, 0].max() + pad, res),
        np.linspace(X[:, 1].min() - pad, X[:, 1].max() + pad, res),
    )
    z = m.decision_function(np.c_[gx.ravel(), gy.ravel()]).reshape(gx.shape)
    ax.imshow(1 / (1 + np.exp(-z)), extent=(gx.min(), gx.max(), gy.min(), gy.max()),
              origin="lower", cmap="RdBu_r", vmin=0, vmax=1, alpha=0.7,
              aspect="auto", interpolation="bilinear")
    ax.contour(gx, gy, z, levels=[0], colors=[INK], linewidths=1.8)
    if margins:
        ax.contour(gx, gy, z, levels=[-1, 1], colors=[INK], linewidths=1.1,
                   linestyles="dashed")
    ax.set_aspect("equal")


def _mark_sv(ax, m, s=140, lw=2.0):
    ax.scatter(m.support_vectors_[:, 0], m.support_vectors_[:, 1], s=s,
               facecolors="none", edgecolors=GREEN, linewidths=lw, zorder=4)


def _bare(ax):
    """Keep the data area, drop the ticks and the frame."""
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


# ==========================================================================
# 1. the linear SVM
# ==========================================================================
@figure("svm_setting")
def svm_setting(fig):
    from sklearn.svm import SVC

    X, y = _sep_blobs(80, seed=3)
    model = SVC(kernel="linear", C=1000).fit(X, y)
    plot = fig.add_axes([0.04, 0.12, 0.46, 0.78])
    _svm_field(plot, model, X, margins=False)
    _scatter_classes(plot, X, y, s=26)
    _bare(plot)

    ax = canvas(fig)
    ax.text(5.05, 3.25, r"$f(x) = w^{T}x + b$", ha="left", va="center", color=INK,
            fontsize=17)
    ax.text(5.05, 2.72, "one linear score per point", ha="left", va="center",
            color=MUTED, fontsize=12)
    ax.text(5.05, 2.10, r"$\hat{y} = \mathrm{sign}\, f(x)$", ha="left", va="center",
            color=GREEN, fontsize=17)
    ax.text(5.05, 1.57, "the sign picks the class", ha="left", va="center",
            color=MUTED, fontsize=12)
    ax.text(5.05, 0.95, r"the labels are $\pm 1$ here —", ha="left", va="center",
            color=INK, fontsize=12.5)
    ax.text(5.05, 0.58, r"so $y_i f(x_i) > 0$ means 'right'", ha="left",
            va="center", color=INK, fontsize=12.5)


@figure("svm_which")
def svm_which(fig):
    """Every one of these lines has zero training error. Which one?"""
    X, y = _sep_blobs()
    lo, hi = X.min(0) - 0.7, X.max(0) + 0.7
    grid = np.linspace(lo[0], hi[0], 2)

    ax = fig.subplots(gridspec_kw=dict(left=0.22, right=0.78, top=0.88, bottom=0.18))
    for a, b in ((-1.506, -0.727), (-1.49, -0.11), (-0.95, 0.10), (-2.6, -0.55)):
        ax.plot(grid, a * grid + b, color=MUTED, lw=2.0, ls="--")
    _scatter_classes(ax, X, y, s=30)
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title("all four separate the training data perfectly", pad=10,
                 fontsize=13.5)
    caption(ax, "the training error cannot choose between them — "
                "something else has to", color=RED, size=12.5)


@figure("svm_margin")
def svm_margin(fig):
    """The answer: the line with the widest empty street around it."""
    from sklearn.svm import SVC

    X, y = _sep_blobs()
    model = SVC(kernel="linear", C=1000).fit(X, y)
    best = 2 / np.linalg.norm(model.coef_[0])
    lo, hi = X.min(0) - 0.7, X.max(0) + 0.7
    grid = np.linspace(lo[0], hi[0], 2)

    a, c = -1.506, -0.727
    d = np.abs(a * X[:, 0] - X[:, 1] + c) / np.hypot(a, 1)
    half = d.min()

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.26, wspace=0.14),
    )
    ax = axes[0]
    ax.plot(grid, a * grid + c, color=INK, lw=1.8)
    band = half * np.hypot(a, 1)
    ax.fill_between(grid, a * grid + c - band, a * grid + c + band, color=GOLD,
                    alpha=0.30)
    _scatter_classes(ax, X, y, s=28)
    ax.set_title(f"a valid line — street {2 * half:.2f} wide", color=GOLD, pad=10,
                 fontsize=13)
    caption(ax, "line close to the blue cloud")

    _svm_field(axes[1], model, X)
    _scatter_classes(axes[1], X, y, s=28)
    _mark_sv(axes[1], model)
    axes[1].set_title(f"the SVM line — street {best:.2f} wide", color=GREEN, pad=10,
                      fontsize=13)
    caption(axes[1], "circled: the support vectors\nthe line is equally close to both")
    for ax in axes:
        ax.set_xlim(lo[0], hi[0])
        ax.set_ylim(lo[1], hi[1])
        ax.set_aspect("equal")
        _bare(ax)


@figure("eq_margin")
def eq_margin(fig):
    ax = canvas(fig)
    # ax.text(W / 2, 3.40, "How wide is the street?", ha="center",
    #         va="center", color=MUTED, fontsize=13)
    equation(
        ax,
        r"$d(x_i, H) \;=\; \frac{y_i\,(w^{T}x_i + b)}{\|w\|}"
        r"\;=\; \frac{|f(x_i)|}{\|w\|}$",
        y=2.55,
        size=23,
    )

    ax.text(4.5, 1.60, r"$y_i f(x_i) > 0$", ha="center", va="center", color=GREEN,
            fontsize=15)
    ax.text(4.5, 1.20, "if correctly classified", ha="center", va="center",
            color=MUTED, fontsize=12)
    # ax.text(2.55, 1.60, r"$y_i f(x_i) > 0$", ha="center", va="center", color=GREEN,
    #         fontsize=15)
    # ax.text(2.55, 1.20, "if correctly classified", ha="center", va="center",
    #         color=MUTED, fontsize=12)
    # ax.text(6.45, 1.60, r"divide by $\|w\|$", ha="center", va="center", color=BLUE,
    #         fontsize=15)
    # ax.text(6.45, 1.20, "a score is not yet a distance", ha="center", va="center",
    #         color=MUTED, fontsize=12)
    note(ax, "the margin of the classifier is twice the smallest of these", y=0.50)


@figure("canonical")
def canonical(fig):
    from sklearn.svm import SVC

    X, y = _sep_blobs()
    model = SVC(kernel="linear", C=1000).fit(X, y)
    w, b = model.coef_[0], model.intercept_[0]
    lo, hi = X.min(0) - 0.7, X.max(0) + 0.7
    grid = np.linspace(lo[0], hi[0], 200)

    axes = panels(
        fig,
        3,
        titles=[r"$(w, b)$", r"$(3w, 3b)$", "canonical choice"],
        colors=[MUTED, MUTED, GREEN],
        gridspec_kw=dict(left=0.04, right=0.98, top=0.82, bottom=0.30, wspace=0.14),
    )
    for ax, scale in zip(axes, (1.0, 3.0, 1.0)):
        _scatter_classes(ax, X, y, s=16)
        ax.plot(grid, -(w[0] * grid + b) / w[1], color=INK, lw=2.2)
        ax.set_xlim(lo[0], hi[0])
        ax.set_ylim(lo[1], hi[1])
        ax.set_aspect("equal")
        _bare(ax)
    for ax, scale in zip(axes[:2], (1.0, 3.0)):
        closest = np.min(np.abs(X @ w + b)) * scale
        ax.text(0.04, 0.95, r"$\min_i |f(x_i)| = %.1f$" % closest,
                transform=ax.transAxes, color=MUTED, fontsize=11.5, va="top")
    ax = axes[2]
    for level in (-1, 1):
        ax.plot(grid, -(w[0] * grid + b - level) / w[1], color=GREEN, lw=1.4,
                ls="--")
    _mark_sv(ax, model, s=110, lw=1.6)
    ax.text(0.04, 0.95, r"$\min_i |f(x_i)| = 1$", transform=ax.transAxes,
            color=GREEN, fontsize=11.5, va="top")
    # caption(axes[0], "same boundary")
    caption(axes[1], "same values scaled")
    caption(axes[2], r"support vectors have $y_i f(x_i) = 1$")
    fig.text(0.5, 0.025, r"with the scale fixed the margin is exactly $M = 2/\|w\|$",
             ha="center", color=MUTED, fontsize=12.5)


@figure("eq_primal")
def eq_primal(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.40, "widen the street while keeping points out of it",
            ha="center", va="center", color=MUTED, fontsize=13)
    ax.text(
        W / 2,
        2.45,
        r"$\min_{w,\,b}\ \ \frac{1}{2}\|w\|^2"
        r"\qquad \mathrm{subject\ to}\qquad"
        r"y_i\,(w^{T}x_i + b) \geq 1, \quad i = 1,\dots,n$",
        ha="center",
        va="center",
        color=INK,
        fontsize=17,
    )
    ax.text(2.85, 1.55, r"$\|w\|$ small  $\Leftrightarrow$  street wide",
            ha="center", va="center", color=GREEN, fontsize=13)
    ax.text(6.55, 1.55, "one constraint per training point", ha="center",
            va="center", color=BLUE, fontsize=13)
    ax.text(
        W / 2,
        0.80,
        "quadratic objective with linear constraints",
        ha="center",
        va="center",
        color=INK,
        fontsize=12.5,
    )
    # note(ax, r"$\Rightarrow$ convex, one solution, no local minima", y=0.30)


@figure("eq_squared_slack")
def eq_squared_slack(fig):
    """The textbook route: an inequality becomes an equality with a squared slack."""
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "an inequality can be made into an equality",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(
        W / 2,
        3.05,
        r"$g_i(w, b) = y_i(w^{T}x_i + b) - 1 \;\geq\; 0"
        r"\qquad \Longleftrightarrow \qquad"
        r"g_i(w, b) - s_i^2 = 0, \quad s_i \in \mathbb{R}$",
        ha="center",
        va="center",
        color=INK,
        fontsize=14,
    )
    ax.text(
        W / 2,
        2.40,
        r"$\tilde{L}(w, b, \alpha, s) = \frac{1}{2}\|w\|^2"
        r" - \sum_i \alpha_i\left[g_i(w,b) - s_i^2\right]$",
        ha="center",
        va="center",
        color=INK,
        fontsize=16,
    )
    ax.text(W / 2, 1.92, r"$\alpha_i$ are free in sign",
            ha="center", va="center", color=MUTED, fontsize=11.5)
    ax.plot([0.60, 8.55], [1.62, 1.62], color=GRID, lw=1.2)

    ax.text(2.45, 1.30, r"$\frac{\partial \tilde{L}}{\partial s_i}"
                        r" = 2\alpha_i s_i = 0$",
            ha="center", va="center", color=GREEN, fontsize=15)
    ax.text(2.45, 0.78, r"$\alpha_i = 0$   or   $s_i = 0$", ha="center",
            va="center", color=INK, fontsize=13)
    ax.text(2.45, 0.38, "complementary slackness:", ha="center", va="center",
            color=MUTED, fontsize=11.5)
    ax.text(2.45, 0.10, "zero multiplier, or a point on the margin", ha="center",
            va="center", color=MUTED, fontsize=11.5)

    ax.text(6.55, 1.30, r"$\frac{\partial^2 \tilde{L}}{\partial s_i^2}"
                        r" = 2\alpha_i \;\geq\; 0$",
            ha="center", va="center", color=BLUE, fontsize=15)
    ax.text(6.55, 0.78, r"$\alpha_i \geq 0$", ha="center", va="center",
            color=INK, fontsize=13)
    ax.text(6.55, 0.38, r"$s_i = 0$ has to be a minimum,", ha="center",
            va="center", color=MUTED, fontsize=11.5)
    ax.text(6.55, 0.10, "not a maximum", ha="center", va="center",
            color=MUTED, fontsize=11.5)


@figure("slack_or_max")
def slack_or_max(fig):
    """Two ways of saying the same constraint — one of them is a price."""
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"the constraint on point $i$:   "
                         r"$g_i(w,b) = y_i(w^{T}x_i + b) - 1 \;\geq\; 0$",
            ha="center", va="center", color=INK, fontsize=14)

    ax.text(2.45, 2.95, "write it as an equality", ha="center", va="center",
            color=GOLD, fontsize=13, weight="bold")
    ax.text(2.45, 2.50, r"$g_i - s_i^2 = 0, \quad s_i \in \mathbb{R}$",
            ha="center", va="center", color=GOLD, fontsize=15)
    ax.text(2.45, 2.08, "allowed when some $s_i$ exists", ha="center", va="center",
            color=MUTED, fontsize=11.5)

    ax.text(6.55, 2.95, "or charge for breaking it", ha="center", va="center",
            color=GREEN, fontsize=13, weight="bold")
    ax.text(6.55, 2.50, r"$\max_{\alpha_i \geq 0}\ \left(-\alpha_i g_i\right)$",
            ha="center", va="center", color=GREEN, fontsize=15)
    ax.text(6.55, 2.08, "allowed when the charge is zero", ha="center",
            va="center", color=MUTED, fontsize=11.5)

    ax.plot([1.05, 7.95], [1.80, 1.80], color=GRID, lw=1.2)
    cols = [(1.35, ""), (3.30, r"is there an $s_i$?"), (6.10, "what it costs")]
    for x, head in cols:
        ax.text(x, 1.52, head, ha="center", va="center", color=MUTED,
                fontsize=11.5)
    rows = [
        (GREEN, r"$g_i \geq 0$", "yes", r"$0$"),
        (RED, r"$g_i < 0$", "none exists", r"$+\infty$"),
    ]
    for i, (color, case, exists, cost) in enumerate(rows):
        y = 1.12 - i * 0.42
        ax.text(1.35, y, case, ha="center", va="center", color=color, fontsize=14)
        ax.text(3.30, y, exists, ha="center", va="center", color=INK,
                fontsize=12.5)
        ax.text(6.10, y, cost, ha="center", va="center", color=color, fontsize=14)
    ax.text(W / 2, 0.22, r"The problem becomes $\min_{w,b}\ \max_{\alpha \geq 0}\ L(w,b,\alpha)$.",
            ha="center", va="center", color=INK, fontsize=12.5)


@figure("eq_dual")
def eq_dual(fig):
    """One problem, written twice: once in w and b, once in alpha."""
    ax = canvas(fig)

    ax.add_patch(
        FancyBboxPatch((0.45, 2.62), 8.1, 0.92, boxstyle="round,pad=0.05,"
                       "rounding_size=0.10", linewidth=1.8, edgecolor=BLUE,
                       facecolor="#f2f6fb", zorder=0)
    )
    ax.text(0.75, 3.30, "PRIMAL", ha="left", va="center", color=BLUE,
            fontsize=12.5, weight="bold")
    ax.text(0.75, 3.02, r"$d+1$ unknowns ($w, b$)", ha="left", va="center", color=MUTED,
            fontsize=10.5)
    ax.text(5.00, 3.06, r"$\min_{w,b}\ \frac{1}{2}\|w\|^2$"
                        r"$\quad \mathrm{s.t.}\quad$"
                        r"$y_i(w^{T}x_i + b) \geq 1$",
            ha="center", va="center", color=INK, fontsize=15)

    ax.text(W / 2, 2.30, r"$L(w, b, \alpha) = \frac{1}{2}\|w\|^2"
                         r" - \sum_i \alpha_i\left[y_i(w^{T}x_i + b) - 1\right]$",
            ha="center", va="center", color=INK, fontsize=14)
    ax.text(W / 2, 1.86, r"$\partial L/\partial w = 0 \;\Rightarrow\; "
                         r"w = \sum_i \alpha_i y_i x_i"
                         r"\qquad \partial L/\partial b = 0 \;\Rightarrow\;"
                         r"\sum_i \alpha_i y_i = 0$",
            ha="center", va="center", color=GOLD, fontsize=13)
    ax.text(W / 2, 1.50, "put these back into L: w and b are gone", ha="center",
            va="center", color=MUTED, fontsize=11.5)

    ax.add_patch(
        FancyBboxPatch((0.45, 0.30), 8.1, 0.92, boxstyle="round,pad=0.05,"
                       "rounding_size=0.10", linewidth=1.8, edgecolor=GREEN,
                       facecolor="#f1f9f1", zorder=0)
    )
    ax.text(0.75, 0.98, "DUAL", ha="left", va="center", color=GREEN,
            fontsize=12.5, weight="bold")
    ax.text(0.75, 0.70, r"$n$ unknowns ($\alpha$)", ha="left", va="center", color=MUTED,
            fontsize=10.5)
    ax.text(5.00, 0.74, r"$\max_{\alpha}\ \sum_i \alpha_i"
                        r" - \frac{1}{2}\sum_{i,j}\alpha_i\alpha_j y_i y_j\,"
                        r"x_i^{T}x_j$"
                        r"$\quad \mathrm{s.t.}\quad \alpha_i \geq 0,"
                        r"\ \sum_i \alpha_i y_i = 0$",
            ha="center", va="center", color=INK, fontsize=12.5)
    # arrow(ax, (W / 2, 2.58), (W / 2, 2.42), color=MUTED, lw=1.6)
    # arrow(ax, (W / 2, 1.38), (W / 2, 1.26), color=MUTED, lw=1.6)


@figure("duality_saddle")
def duality_saddle(fig):
    """At a saddle, minimising first or maximising first lands in the same place."""
    w = np.linspace(-0.4, 2.6, 400)
    a = np.linspace(0.0, 2.4, 400)
    Wg, Ag = np.meshgrid(w, a)
    L = 0.5 * Wg**2 - Ag * (Wg - 1)

    ax = fig.subplots(gridspec_kw=dict(left=0.08, right=0.60, top=0.90,
                                       bottom=0.16))
    im = ax.contourf(Wg, Ag, L, levels=20, cmap="RdBu_r", alpha=0.9)
    ax.contour(Wg, Ag, L, levels=[0.5], colors=[INK], linewidths=1.2)
    ax.plot([1.0], [1.0], "o", color=INK, ms=12, mfc="white", mew=2.2, zorder=4)
    ax.annotate("", xy=(1.0, 0.18), xytext=(1.0, 2.25),
                arrowprops=dict(arrowstyle="<|-|>", color=GREEN, lw=1.8))
    ax.annotate("", xy=(0.05, 1.0), xytext=(2.5, 1.0),
                arrowprops=dict(arrowstyle="<|-|>", color=BLUE, lw=1.8))
    ax.text(1.08, 2.30, r"maximise over $\alpha$", color=GREEN, fontsize=11.5,
            va="top")
    ax.text(2.52, 0.92, r"minimise over $w$", color=BLUE, fontsize=11.5,
            ha="right", va="top")
    ax.text(1.12, 1.08, r"$(\hat{w}, \hat\alpha)$", color=INK, fontsize=12.5)
    ax.set_xlabel(r"$w$")
    ax.set_ylabel(r"$\alpha$")
    ax.set_title(r"$L(w, \alpha) = \frac{1}{2}w^2 - \alpha(w - 1)$"
                 r"   for   $\min \frac{1}{2}w^2$ s.t. $w \geq 1$",
                 pad=10, fontsize=13)

    side = fig.add_axes([0.64, 0.18, 0.34, 0.68])
    side.axis("off")
    side.text(0.0, 0.95, "a saddle, not a peak", color=INK, fontsize=13,
              weight="bold", va="center")
    side.text(0.0, 0.80, "lowest along one direction,", color=MUTED, fontsize=11.5,
              va="center")
    side.text(0.0, 0.70, "highest along the other", color=MUTED, fontsize=11.5,
              va="center")
    side.text(0.0, 0.50, r"$\min_w \max_\alpha L \;=\; "
                         r"\max_\alpha \min_w L$",
              color=GREEN, fontsize=13, va="center")


@figure("kkt_recover")
def kkt_recover(fig):
    """Solve the dual, read the primal back — and never build w."""
    ax = canvas(fig)
    ax.text(W / 2, 3.52, r"from $\hat\alpha$, everything else follows",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    rows = [
        (GREEN, r"$\hat{w} = \sum_i \hat\alpha_i y_i x_i$"),
        (BLUE, r"$\hat\alpha_i\left[y_i(\hat{w}^{T}x_i + \hat{b}) - 1\right] = 0$"),
        (PURPLE, r"$\hat{b} = y_i - \hat{w}^{T}x_i$   for any $\hat\alpha_i > 0$"),
    ]
    for i, (color, formula) in enumerate(rows):
        ax.text(2.35, 3.00 - i * 0.52, formula, ha="center", va="center",
                color=color, fontsize=13.5)

    ax.plot([4.60, 4.60], [1.55, 3.25], color=GRID, lw=1.2)
    ax.text(6.80, 3.15, r"but $\hat{w}$ is never built", ha="center", va="center",
            color=INK, fontsize=13, weight="bold")
    ax.text(6.80, 2.72, r"$f(x) = \sum_{SV} \hat\alpha_i y_i\,"
                        r"\langle x_i,\, x\rangle + \hat{b}$",
            ha="center", va="center", color=GREEN, fontsize=14)
    ax.text(6.80, 2.25, "the prediction asks only for inner products", ha="center",
            va="center", color=MUTED, fontsize=11.5)
    ax.text(6.80, 1.95, "of x with the support vectors", ha="center", va="center",
            color=MUTED, fontsize=11.5)

    ax.plot([0.70, 8.40], [1.45, 1.45], color=GRID, lw=1.2)
    heads = [(2.05, "storing"), (4.60, "cost"), (7.10, "when it breaks")]
    for x, head in heads:
        ax.text(x, 1.18, head, ha="center", va="center", color=MUTED,
                fontsize=11.5)
    table = [
        (GOLD, r"$\hat{w}$", r"$d$ numbers",
         r"hopeless if $x$ lives in a huge space"),
        (GREEN, r"the $\hat\alpha_i$", "one per support vector",
         "the sum stays finite"),
    ]
    for i, (color, what, cost, when) in enumerate(table):
        y = 0.80 - i * 0.40
        ax.text(2.05, y, what, ha="center", va="center", color=color, fontsize=12.5)
        ax.text(4.60, y, cost, ha="center", va="center", color=INK, fontsize=12)
        ax.text(7.10, y, when, ha="center", va="center", color=MUTED, fontsize=11)
    ax.text(W / 2, 0.10, r"This is what kernels exploit: "
                         r"replace $\langle x_i, x\rangle$ by $k(x_i, x)$",
            ha="center", va="center", color=RED, fontsize=12)


@figure("support_vectors")
def support_vectors(fig):
    from sklearn.svm import SVC

    X, y = _sep_blobs()
    model = SVC(kernel="linear", C=1000).fit(X, y)
    keep = np.zeros(len(X), bool)
    keep[model.support_] = True
    lo, hi = X.min(0) - 0.7, X.max(0) + 0.7

    axes = panels(
        fig,
        2,
        titles=[f"all {len(X)} points", f"only the {keep.sum()} support vectors"],
        colors=[INK, GREEN],
        gridspec_kw=dict(left=0.05, right=0.72, top=0.84, bottom=0.26, wspace=0.14),
    )
    _svm_field(axes[0], model, X)
    _scatter_classes(axes[0], X, y, s=26)
    _mark_sv(axes[0], model)
    second = SVC(kernel="linear", C=1000).fit(X[keep], y[keep])
    _svm_field(axes[1], second, X)
    _scatter_classes(axes[1], X[keep], y[keep], s=40)
    for ax in axes:
        ax.set_xlim(lo[0], hi[0])
        ax.set_ylim(lo[1], hi[1])
        ax.set_aspect("equal")
        _bare(ax)
    caption(axes[0], r"$\alpha_i > 0$ only on the margin")
    caption(axes[1], "same boundary")

    side = fig.add_axes([0.745, 0.22, 0.25, 0.62])
    side.axis("off")
    side.text(0.0, 0.95, "two cases", color=INK, fontsize=13, weight="bold",
              va="center")
    side.text(0.0, 0.76, r"$y_i f(x_i) = 1$", color=GREEN, fontsize=13, va="center")
    side.text(0.0, 0.64, r"on the margin, $\alpha_i > 0$", color=MUTED, fontsize=11,
              va="center")
    side.text(0.0, 0.46, r"$y_i f(x_i) > 1$", color=BLUE, fontsize=13, va="center")
    side.text(0.0, 0.34, r"further away, $\alpha_i = 0$", color=MUTED, fontsize=11,
              va="center")
    # side.text(0.0, 0.13, r"$f(x) = \sum_{SV} \alpha_i y_i\, x_i^{T}x + b$",
    #           color=BLUE, fontsize=12.5, va="center")
    # side.text(0.0, 0.0, "the rest can be thrown away", color=MUTED, fontsize=11,
    #           va="center")


@figure("not_separable")
def not_separable(fig):
    from sklearn.svm import SVC

    X, y = _sep_blobs(160, seed=5, gap=1.5)
    lo, hi = X.min(0) - 0.7, X.max(0) + 0.7
    axes = panels(
        fig,
        2,
        titles=["no line gets everything right", "so allow a few mistakes"],
        colors=[RED, GREEN],
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.26, wspace=0.14),
    )
    _scatter_classes(axes[0], X, y, s=20)
    model = SVC(kernel="linear", C=1.0).fit(X, y)
    _svm_field(axes[1], model, X)
    _scatter_classes(axes[1], X, y, s=20)
    wrong = model.predict(X) != y
    axes[1].scatter(X[wrong, 0], X[wrong, 1], s=110, facecolors="none",
                    edgecolors=RED, linewidths=1.6, zorder=5)
    for ax in axes:
        ax.set_xlim(lo[0], hi[0])
        ax.set_ylim(lo[1], hi[1])
        ax.set_aspect("equal")
        _bare(ax)
    caption(axes[0], "the hard-margin problem has no solution at all")
    caption(axes[1], f"the {wrong.sum()} circled points are the ones it gives up on")


@figure("slack_idea")
def slack_idea(fig):
    from sklearn.svm import SVC

    X, y = _sep_blobs(90, seed=5, gap=1.5)
    model = SVC(kernel="linear", C=1.0).fit(X, y)
    w, b = model.coef_[0], model.intercept_[0]
    norm = np.linalg.norm(w)
    signed = np.where(y == 1, 1.0, -1.0)

    ax = fig.subplots(gridspec_kw=dict(left=0.04, right=0.55, top=0.94, bottom=0.06))
    _svm_field(ax, model, X)
    _scatter_classes(ax, X, y, s=22)
    scores = signed * (X @ w + b)
    slack = np.maximum(0, 1 - scores)
    for i in np.argsort(-slack)[:5]:
        direction = signed[i] * w / norm**2
        ax.annotate("", xy=X[i] + direction * slack[i], xytext=X[i],
                    arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=1.8))
    ax.set_xlim(X[:, 0].min() - 0.7, X[:, 0].max() + 0.7)
    ax.set_ylim(X[:, 1].min() - 0.7, X[:, 1].max() + 0.7)
    ax.set_aspect("equal")
    _bare(ax)

    side = fig.add_axes([0.58, 0.14, 0.40, 0.74])
    side.axis("off")
    side.text(0.0, 0.95, r"$\xi_i \geq 0$ : how far point $i$ is", color=GOLD,
              fontsize=13.5, va="center")
    side.text(0.0, 0.84, "from where it ought to be", color=GOLD, fontsize=13.5,
              va="center")
    side.text(0.0, 0.64, r"$y_i(w^{T}x_i + b) \geq 1 - \xi_i$", color=INK,
              fontsize=15, va="center")
    rows = [
        (GREEN, r"$\xi_i = 0$", "outside the street, fine"),
        (GOLD, r"$0 < \xi_i \leq 1$", "inside it, still right"),
        (RED, r"$\xi_i > 1$", "on the wrong side"),
    ]
    for i, (color, head, text) in enumerate(rows):
        side.text(0.0, 0.42 - i * 0.13, head, color=color, fontsize=12.5,
                  va="center")
        side.text(0.33, 0.42 - i * 0.13, text, color=MUTED, fontsize=11,
                  va="center")
    side.text(0.0, 0.02, r"and we pay $C$ for every unit of $\xi$", color=INK,
              fontsize=12, va="center")


@figure("eq_soft")
def eq_soft(fig):
    ax = canvas(fig)
    # lay the objective out from measured fragments, so each arrow can point at
    # the exact centre of the term it names
    pieces = [
        (r"$\min_{w,\,b,\,\xi}$", INK, None),
        (r"$\frac{1}{2}\|w\|^2$", GREEN, "a wide street"),
        (r"$+$", INK, None),
        (r"$C\sum_{i=1}^{n}\xi_i$", RED, "few and small violations"),
    ]
    size, gap, y = 20, 0.60, 3.00
    widths = [text_width(fig, ax, text, size) for text, _, _ in pieces]
    x = (W - sum(widths) - gap * (len(pieces) - 1)) / 2
    for (text, color, label), w in zip(pieces, widths):
        ax.text(x, y, text, ha="left", va="center", color=color, fontsize=size)
        if label:
            centre = x + w / 2
            ax.text(centre, 2.12, label, ha="center", va="top", color=color,
                    fontsize=12.5)
            arrow(ax, (centre, 2.26), (centre, 2.56), color=color, lw=1.4)
        x += w + gap
    ax.text(
        W / 2,
        1.72,
        r"$\mathrm{subject\ to}\quad y_i(w^{T}x_i + b) \geq 1 - \xi_i,"
        r"\quad \xi_i \geq 0$",
        ha="center",
        va="center",
        color=INK,
        fontsize=14,
    )
    ax.text(W / 2, 1.35, r"$C$ sets the exchange rate between the two",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.plot([1.40, 7.60], [1.05, 1.05], color=GRID, lw=1.2)
    ax.text(
        W / 2,
        0.68,
        r"$\max_{\alpha}\ \sum_i \alpha_i"
        r" - \frac{1}{2}\sum_{i,j}\alpha_i\alpha_j y_i y_j\,x_i^{T}x_j"
        r"\qquad 0 \leq \alpha_i \leq C, \ \ \sum_i \alpha_i y_i = 0$",
        ha="center",
        va="center",
        color=BLUE,
        fontsize=14,
    )
    note(ax, r"the same dual as before, with the multipliers capped at $C$", y=0.22)


@figure("svm_c")
def svm_c(fig):
    """C is the regularisation knob: how much are violations allowed to cost?"""
    from sklearn.svm import SVC

    X, y = _sep_blobs(160, seed=5, gap=1.5)
    axes = fig.subplots(
        1, 3,
        gridspec_kw=dict(left=0.04, right=0.98, top=0.78, bottom=0.32, wspace=0.12),
    )
    for ax, C, color in zip(axes, (0.02, 1.0, 100.0), (GREEN, BLUE, RED)):
        model = SVC(kernel="linear", C=C).fit(X, y)
        _svm_field(ax, model, X)
        _scatter_classes(ax, X, y, s=14)
        _mark_sv(ax, model, s=46, lw=1.1)
        width = 2 / np.linalg.norm(model.coef_[0])
        ax.set_title(f"C = {C:g}", color=color, pad=8, fontsize=13)
        caption(ax, f"street {width:.2f} wide, {len(model.support_)} "
                    f"support vectors")
        _bare(ax)
    fig.text(0.23, 0.02, "soft: a wide street, violations tolerated", ha="center",
             color=GREEN, fontsize=12)
    fig.text(0.79, 0.02, "hard: a narrow street, fits the training points",
             ha="center", color=RED, fontsize=12)


@figure("eq_svm")
def eq_svm(fig):
    ax = canvas(fig)
    pieces = [
        (r"$\min_{w,b}$", INK, None),
        (r"$\frac{1}{2}\|w\|^2$", GREEN, "make the street\nas WIDE as possible"),
        (r"$+$", INK, None),
        (r"$C\sum_i \max\left(0,\, 1 - y_i(w^{T}x_i + b)\right)$", RED,
         "pay C for every point inside it\nor on the wrong side"),
    ]
    size, gap, y = 22, 0.22, 2.55
    widths = [text_width(fig, ax, text, size) for text, _, _ in pieces]
    x = (W - sum(widths) - gap * (len(pieces) - 1)) / 2
    for (text, color, label), w in zip(pieces, widths):
        ax.text(x, y, text, ha="left", va="center", color=color, fontsize=size)
        if label:
            centre = x + w / 2
            ax.text(centre, 1.35, label, ha="center", va="top", color=color,
                    fontsize=12, linespacing=1.6)
            arrow(ax, (centre, 1.50), (centre, 2.10), color=color, lw=1.4)
        x += w + gap
    note(ax, "the margin is the penalty, the hinge is the loss — "
             "one more regularised fit", y=0.45)


@figure("hinge_loss")
def hinge_loss(fig):
    margin = np.linspace(-2.5, 3, 500)
    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.07, right=0.97, top=0.84, bottom=0.24, wspace=0.26),
    )
    ax = axes[0]
    ax.plot(margin, np.maximum(0, 1 - margin), color=GREEN, lw=2.8)
    ax.plot(margin, np.log1p(np.exp(-margin)) / np.log(2), color=BLUE, lw=2.2,
            ls="--")
    ax.plot(margin, (1 - margin) ** 2, color=GOLD, lw=2.2, ls="-.")
    ax.step(margin, (margin < 0).astype(float), color=INK, lw=1.8, where="mid",
            alpha=0.7)
    ax.text(2.05, 1.45, "squared", color=GOLD, fontsize=12)
    ax.text(1.4, 0.55, "logistic", color=BLUE, fontsize=12)
    ax.text(0.15, 2.3, "hinge", color=GREEN, fontsize=12.5)
    ax.text(0.9, 0.08, "0 / 1", color=INK, fontsize=11.5)
    ax.axvline(1, color=GRID, lw=1.2, ls=":")
    ax.text(1.05, 2.6, "margin 1", color=MUTED, fontsize=11)
    ax.set_ylim(-0.1, 3.0)
    ax.set_xlabel(r"margin  $y_i f(x_i)$")
    ax.set_ylabel("loss of one point")
    ax.set_title("the hinge loss", color=GREEN, pad=10, fontsize=13.5)

    ax = axes[1]
    ax.axis("off")
    rows = [
        (GREEN, "SVM", r"$\frac{1}{2}\|w\|^2$", "hinge"),
        (BLUE, "logistic + ridge", r"$\frac{\lambda}{2}\|w\|^2$", "log loss"),
        (GOLD, "ridge regression", r"$\frac{\lambda}{2}\|w\|^2$", "squared loss"),
    ]
    ax.text(0.04, 0.92, "penalty", transform=ax.transAxes, color=MUTED,
            fontsize=11.5, ha="left")
    ax.text(0.50, 0.92, "+", transform=ax.transAxes, color=MUTED, fontsize=11.5,
            ha="center")
    ax.text(0.72, 0.92, "loss", transform=ax.transAxes, color=MUTED, fontsize=11.5,
            ha="left")
    for i, (color, name, penalty, loss) in enumerate(rows):
        y = 0.70 - i * 0.20
        ax.text(0.04, y, name, transform=ax.transAxes, color=color, fontsize=12.5,
                ha="left", va="center")
        ax.text(0.50, y, penalty, transform=ax.transAxes, color=INK, fontsize=14,
                ha="center", va="center")
        ax.text(0.72, y, loss, transform=ax.transAxes, color=INK, fontsize=12.5,
                ha="left", va="center")


# ==========================================================================
# 3. kernels
# ==========================================================================
def _ring_data(seed=1, n=150):
    rng = np.random.default_rng(seed)
    t = rng.uniform(0, 2 * np.pi, n)
    r = np.r_[rng.normal(0.85, 0.16, n // 2), rng.normal(2.1, 0.20, n // 2)]
    X = np.c_[r * np.cos(t), r * np.sin(t)]
    y = np.r_[np.zeros(n // 2, int), np.ones(n // 2, int)]
    return X, y


@figure("svm_kernel")
def svm_kernel(fig):
    """The trick: a circle in 2D is a flat plane one dimension up."""
    from sklearn.svm import SVC

    X, y = _ring_data()
    z = (X**2).sum(1)

    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1.3, 1], wspace=0.10,
                          left=0.03, right=0.98, top=0.88, bottom=0.22)
    ax = fig.add_subplot(gs[0])
    _scatter_classes(ax, X, y, s=18)
    ax.set_title("no straight line works", pad=8, fontsize=12.5)
    ax.set_aspect("equal")
    _bare(ax)

    ax2 = fig.add_subplot(gs[1], projection="3d")
    for cls, colour, marker in ((0, BLUE, "o"), (1, RED, "^")):
        m_ = y == cls
        ax2.scatter(X[m_, 0], X[m_, 1], z[m_], s=14, color=colour, marker=marker,
                    depthshade=False)
    g1, g2 = np.meshgrid(np.linspace(-2.6, 2.6, 8), np.linspace(-2.6, 2.6, 8))
    ax2.plot_surface(g1, g2, np.full_like(g1, 2.2), color=MUTED, alpha=0.35,
                     edgecolor=MUTED, linewidth=0.3)
    ax2.set_title(r"lift: add a column $x_1^2 + x_2^2$", pad=2, fontsize=12.5)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_zticks([])
    ax2.view_init(16, -62)

    ax3 = fig.add_subplot(gs[2])
    model = SVC(kernel="rbf", C=10, gamma=0.5).fit(X, y)
    _svm_field(ax3, model, X, margins=False)
    _scatter_classes(ax3, X, y, s=18)
    ax3.set_title("back in 2D: a circle", pad=8, fontsize=12.5)
    _bare(ax3)
    fig.text(0.5, 0.08, "the kernel computes the lifted dot products without ever "
                        "building the extra columns",
             ha="center", color=INK, fontsize=12.5)


@figure("xor_example")
def xor_example(fig):
    X = np.array([[1.0, 1.0], [-1.0, -1.0], [1.0, -1.0], [-1.0, 1.0]])
    y = np.array([1, 1, 0, 0])
    phi1 = np.sqrt(2) * X[:, 0]
    phi2 = np.sqrt(2) * X[:, 0] * X[:, 1]

    axes = fig.subplots(
        1, 3,
        gridspec_kw=dict(left=0.05, right=0.98, top=0.82, bottom=0.26, wspace=0.28),
    )
    ax = axes[0]
    _scatter_classes(ax, X, y, s=90)
    ax.axhline(0, color=GRID, lw=1.0)
    ax.axvline(0, color=GRID, lw=1.0)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect("equal")
    _bare(ax)
    ax.set_title("the XOR classes", pad=10, fontsize=13)
    caption(ax, "no line")

    ax = axes[1]
    ax.axis("off")
    ax.text(0.5, 0.72, r"$\Phi(x) = (\sqrt{2}x_1,\ \sqrt{2}x_1x_2,\ 1,$",
            transform=ax.transAxes, ha="center", va="center", color=INK,
            fontsize=13)
    ax.text(0.5, 0.56, r"$\sqrt{2}x_2,\ x_1^2,\ x_2^2)$", transform=ax.transAxes,
            ha="center", va="center", color=INK, fontsize=13)
    ax.text(0.5, 0.28, r"$\mathbb{R}^2 \to \mathbb{R}^6$", transform=ax.transAxes,
            ha="center", va="center", color=GREEN, fontsize=16)

    ax = axes[2]
    for cls, colour, marker in ((0, BLUE, "o"), (1, RED, "^")):
        m = y == cls
        ax.scatter(phi1[m], phi2[m], s=90, color=colour, marker=marker,
                   edgecolors="none", zorder=3)
    ax.axhline(0, color=INK, lw=2.2)
    ax.set_xlabel(r"$\Phi_1 = \sqrt{2}x_1$")
    ax.set_ylabel(r"$\Phi_2 = \sqrt{2}x_1x_2$")
    ax.set_xlim(-2.4, 2.4)
    ax.set_ylim(-2.4, 2.4)
    despine(ax, keep=("bottom", "left"))
    ax.set_title(r"in the $(\Phi_1, \Phi_2)$ plane", color=GREEN, pad=10,
                 fontsize=13)
    caption(ax, "separable, by one horizontal line")


@figure("eq_kernel_trick")
def eq_kernel_trick(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.45, "Embedded problem", ha="center",
            va="center", color=MUTED, fontsize=12.5)
    ax.text(
        W / 2,
        2.90,
        r"$f(x) = w^{T}\Phi(x) + b"
        r" = \sum_{SV} \alpha_i y_i\, \Phi(x_i)^{T}\Phi(x) + b$",
        ha="center",
        va="center",
        color=INK,
        fontsize=16,
    )
    ax.text(W / 2, 2.30, r"$\Phi$ only ever appears inside an inner product",
            ha="center", va="center", color=RED, fontsize=13)
    ax.text(
        W / 2,
        1.60,
        r"$k(x, x') \;=\; \langle \Phi(x),\, \Phi(x')\rangle$",
        ha="center",
        va="center",
        color=GREEN,
        fontsize=22,
    )
    ax.text(W / 2, 0.90, "so compute the similarity directly, never build Φ",
            ha="center", va="center", color=INK, fontsize=13.5)
    ax.text(2.55, 0.40, "implicit space can be infinite", ha="center",
            va="center", color=MUTED, fontsize=11.5)
    ax.text(6.45, 0.40, "cost follows n, not the dimension", ha="center",
            va="center", color=MUTED, fontsize=11.5)


@figure("svm_similarity")
def svm_similarity(fig):
    """A kernel is a similarity, and the prediction is a vote of similarities."""
    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.07, right=0.97, top=0.84, bottom=0.24, wspace=0.24),
    )
    d = np.linspace(0, 3, 300)
    for g, colour in ((0.2, BLUE), (1.0, GREEN), (5.0, RED)):
        axes[0].plot(d, np.exp(-g * d**2), color=colour, lw=2.6,
                     label=rf"$\gamma$ = {g}")
    axes[0].set_xlabel(r"distance  $\|x - x'\|$")
    axes[0].set_ylabel(r"$k(x, x')$")
    axes[0].set_title(r"RBF:  $k(x,x') = \exp(-\gamma\|x-x'\|^2)$", pad=10,
                      fontsize=13)
    axes[0].legend(frameon=False, fontsize=11, loc="upper right")
    despine(axes[0], keep=("bottom", "left"))
    caption(axes[0], "small γ: far points still count as similar\nlarge γ: only near neighbours count", size=9)

    ax = axes[1]
    sv = ((-2.0, 1), (-0.8, 1), (0.5, -1), (1.4, -1), (2.4, 1))
    grid = np.linspace(-3.4, 3.6, 500)
    total = np.zeros_like(grid)
    for x0, sign in sv:
        bump = sign * np.exp(-1.6 * (grid - x0) ** 2)
        total += bump
        ax.plot(grid, bump, color=(RED if sign > 0 else BLUE), lw=1.2, alpha=0.55)
        ax.plot([x0], [0], "^" if sign > 0 else "o",
                color=(RED if sign > 0 else BLUE), ms=8, clip_on=False, zorder=4)
    ax.plot(grid, total, color=INK, lw=2.8)
    ax.axhline(0, color=MUTED, lw=1.2, ls="--")
    ax.fill_between(grid, 0, total, where=total > 0, color=RED, alpha=0.10)
    ax.fill_between(grid, 0, total, where=total < 0, color=BLUE, alpha=0.10)
    ax.set_title(r"$f(x) = \sum_i \alpha_i y_i\, k(x, x_i) + b$", pad=10,
                 fontsize=13)
    ax.set_xlabel(r"$x$")
    ax.set_yticks([])
    despine(ax, keep=("bottom",))
    caption(ax, "one bump per support vector; predict the sign of the sum")


@figure("eq_kernel_conditions")
def eq_kernel_conditions(fig):
    ax = canvas(fig)
    ax.text(1.05, 2.80, "1.  symmetric", ha="left", va="center", color=INK,
            fontsize=13.5)
    ax.text(3.55, 2.80, r"$k(x, x') = k(x', x)$", ha="left", va="center",
            color=BLUE, fontsize=15)
    ax.text(1.05, 2.10, "2.  positive semi-definite", ha="left", va="center",
            color=INK, fontsize=13.5)
    ax.text(3.55, 2.10, r"$\sum_i \sum_j \alpha_i \alpha_j\, k(x_i, x_j) \geq 0$",
            ha="left", va="center", color=BLUE, fontsize=15)
    ax.text(W / 2, 1.30, "So that the dual stays convex (hence the solution stays unique)",
            ha="center", va="center", color=GREEN, fontsize=13)
    note(ax, "sums and products of kernels are kernels", y=0.25)


@figure("svm_kernel_zoo")
def svm_kernel_zoo(fig):
    """The four kernels a student will actually meet, and when to use them."""
    ax = canvas(fig)
    heads = [(1.15, "kernel"), (3.45, r"$k(x, x')$"), (5.75, "knobs"),
             (7.55, "reach for it when")]
    for x, text in heads:
        ax.text(x, 3.42, text, ha="center", va="center", color=MUTED, fontsize=12)
    rows = (
        ("linear", r"$x^{T}x'$", "C only",
         "d is large, n is huge,\ntext / sparse features", BLUE),
        ("polynomial", r"$(\gamma\, x^{T}x' + r)^{p}$", r"C, $\gamma$, r, p",
         "want explicit\nfeature interactions", PURPLE),
        ("RBF / Gaussian", r"$\exp(-\gamma\|x - x'\|^2)$", r"C, $\gamma$",
         "the default", GREEN),
        ("sigmoid", r"$\tanh(\gamma\, x^{T}x' + r)$", r"C, $\gamma$, r",
         "not always\na valid kernel", GOLD),
    )
    for i, (name, formula, knobs, when, colour) in enumerate(rows):
        y = 2.90 - i * 0.66
        ax.plot([0.35, 8.70], [y + 0.33, y + 0.33], color=GRID, lw=1.0)
        ax.text(1.15, y, name, ha="center", va="center", color=colour,
                fontsize=12.5)
        ax.text(3.45, y, formula, ha="center", va="center", color=INK, fontsize=14)
        ax.text(5.75, y, knobs, ha="center", va="center", color=INK, fontsize=11.5)
        ax.text(7.55, y, when, ha="center", va="center", color=MUTED, fontsize=11,
                linespacing=1.5)
    ax.text(W / 2, 0.20, "Kernels can be written for strings, graphs or sequences.",
            ha="center", va="center", color=INK, fontsize=11.5)


@figure("svm_kernels")
def svm_kernels(fig):
    """Four kernels, four shapes of boundary — and what gamma does."""
    from sklearn.svm import SVC

    X, y = _moons(260, 0.22, 0)
    models = (
        ("linear", SVC(kernel="linear", C=1)),
        ("polynomial, p = 3", SVC(kernel="poly", degree=3, C=1, coef0=1)),
        (r"RBF, $\gamma$ = 0.5", SVC(kernel="rbf", C=1, gamma=0.5)),
        (r"RBF, $\gamma$ = 50", SVC(kernel="rbf", C=1, gamma=50)),
    )
    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.82, bottom=0.22, wspace=0.10),
    )
    for ax, (title, model) in zip(axes, models):
        model.fit(X, y)
        _svm_field(ax, model, X, margins=False)
        _scatter_classes(ax, X, y, s=11)
        ax.set_title(title, pad=8, fontsize=12)
        _bare(ax)
    axes[2].set_title(r"RBF, $\gamma$ = 0.5", color=GREEN, pad=8, fontsize=12)
    axes[3].set_title(r"RBF, $\gamma$ = 50", color=RED, pad=8, fontsize=12)
    fig.text(0.5, 0.06, "big γ: treat each point as an island",
             ha="center", color=RED, fontsize=12)


@figure("kernel_cv")
def kernel_cv(fig):
    """C and gamma are chosen together, by cross-validation."""
    from sklearn.model_selection import cross_val_score
    from sklearn.svm import SVC

    X, y = _moons(220, 0.28, 2)
    gammas = np.array([0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0])
    Cs = np.array([0.03, 0.1, 1.0, 10.0, 100.0])
    scores = np.zeros((len(Cs), len(gammas)))
    for i, C in enumerate(Cs):
        for j, g in enumerate(gammas):
            scores[i, j] = cross_val_score(
                SVC(kernel="rbf", C=C, gamma=g), X, y, cv=4
            ).mean()

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.08, right=0.97, top=0.84, bottom=0.26,
                         wspace=0.24, width_ratios=[1.25, 1]),
    )
    ax = axes[0]
    im = ax.imshow(scores, cmap="Greens", origin="lower", aspect="auto",
                   vmin=0.72, vmax=scores.max())
    ax.set_xticks(range(len(gammas)))
    ax.set_xticklabels([f"{g:g}" for g in gammas], fontsize=10)
    ax.set_yticks(range(len(Cs)))
    ax.set_yticklabels([f"{c:g}" for c in Cs], fontsize=10)
    ax.set_xlabel(r"$\gamma$")
    ax.set_ylabel(r"$C$")
    best = np.unravel_index(scores.argmax(), scores.shape)
    ax.plot(best[1], best[0], "o", color=RED, ms=22, mfc="none", mew=2.4)
    for i in range(len(Cs)):
        for j in range(len(gammas)):
            ax.text(j, i, f"{scores[i, j]:.2f}", ha="center", va="center",
                    color=INK if scores[i, j] < 0.93 else "white", fontsize=8.5)
    ax.set_title("4-fold cross-validated accuracy", pad=10, fontsize=13)

    ax = axes[1]
    model = SVC(kernel="rbf", C=Cs[best[0]], gamma=gammas[best[1]]).fit(X, y)
    _svm_field(ax, model, X, margins=False)
    _scatter_classes(ax, X, y, s=12)
    _bare(ax)
    ax.set_title(r"$C = %g$,  $\gamma = %g$" % (Cs[best[0]], gammas[best[1]]),
                 color=RED, pad=10, fontsize=13)


@figure("feature_scaling")
def feature_scaling(fig):
    """The RBF measures distances, so an unscaled feature drowns the others."""
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_val_score
    from sklearn.svm import SVC

    rng = np.random.default_rng(4)
    n = 140
    # a well-behaved feature, and the same feature measured in another unit
    x1 = np.r_[rng.normal(-0.7, 0.55, n // 2), rng.normal(0.7, 0.55, n // 2)]
    x2 = np.r_[rng.normal(-0.6, 0.6, n // 2), rng.normal(0.6, 0.6, n // 2)] * 400
    X = np.c_[x1, x2]
    y = np.r_[np.zeros(n // 2, int), np.ones(n // 2, int)]

    raw = SVC(kernel="rbf", C=1, gamma="scale").fit(X, y)
    scaled = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1)).fit(X, y)
    Z = StandardScaler().fit_transform(X)

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.06, right=0.98, top=0.80, bottom=0.26, wspace=0.30),
    )
    ax = axes[0]
    _svm_field(ax, raw, X, margins=False, pad=60)
    _scatter_classes(ax, X, y, s=16)
    ax.set_aspect("auto")
    ax.set_xlabel(r"$x_1$  (units of 1)")
    ax.set_ylabel(r"$x_2$  (units of 400)")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("as measured", color=RED, pad=10, fontsize=13)
    caption(ax, r"the boundary ignores $x_1$ completely")

    ax = axes[1]
    inner = scaled.named_steps["svc"]
    _svm_field(ax, inner, Z, margins=False)
    _scatter_classes(ax, Z, y, s=16)
    ax.set_aspect("auto")
    ax.set_xlabel(r"$x_1$  (standardised)")
    ax.set_ylabel(r"$x_2$  (standardised)")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("after standardising", color=GREEN, pad=10, fontsize=13)
    caption(ax, "both features get a say")



@figure("svr")
def svr(fig):
    """The same margin idea, with a continuous target."""
    from sklearn.svm import SVR

    rng = np.random.default_rng(6)
    x = np.sort(rng.uniform(-3, 3, 70))
    y = np.sin(x) + 0.35 * x + rng.normal(0, 0.18, x.size)
    eps = 0.35
    model = SVR(kernel="rbf", C=10, epsilon=eps, gamma=0.5).fit(x[:, None], y)
    grid = np.linspace(-3.2, 3.2, 300)
    pred = model.predict(grid[:, None])
    inside = np.abs(y - model.predict(x[:, None])) <= eps + 1e-9

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.24, wspace=0.26),
    )
    ax = axes[0]
    ax.fill_between(grid, pred - eps, pred + eps, color=GREEN, alpha=0.16)
    ax.plot(grid, pred, color=GREEN, lw=2.6)
    ax.plot(grid, pred - eps, color=GREEN, lw=1.0, ls="--")
    ax.plot(grid, pred + eps, color=GREEN, lw=1.0, ls="--")
    ax.scatter(x[inside], y[inside], s=22, color=MUTED, alpha=0.8,
               edgecolors="none", zorder=3)
    ax.scatter(x[~inside], y[~inside], s=60, facecolors="none", edgecolors=RED,
               linewidths=1.6, zorder=4)
    at = float(model.predict(np.array([[2.4]]))[0])
    ax.annotate("", xy=(2.4, at + eps), xytext=(2.4, at),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.4))
    ax.text(2.55, at + eps / 2, r"$\varepsilon$", color=INK, fontsize=15,
            va="center", ha="left")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    despine(ax, keep=("bottom", "left"))
    ax.set_title(r"a tube of width $2\varepsilon$ around the fit", color=GREEN,
                 pad=10, fontsize=13)
    caption(ax, f"only the {(~inside).sum()} circled points support the tube")

    ax = axes[1]
    e = np.linspace(-2.2, 2.2, 500)
    ax.plot(e, np.maximum(0, np.abs(e) - eps * 2), color=GREEN, lw=2.8)
    ax.plot(e, 0.5 * e**2, color=GOLD, lw=2.0, ls="--")
    ax.plot(e, np.where(np.abs(e) <= 1, 0.5 * e**2, np.abs(e) - 0.5), color=BLUE,
            lw=2.0, ls=":")
    ax.text(1.35, 0.35, "ε-insensitive", color=GREEN, fontsize=12)
    ax.text(1.05, 1.55, "squared", color=GOLD, fontsize=12)
    ax.text(-2.1, 1.0, "Huber", color=BLUE, fontsize=12)
    ax.axvspan(-eps * 2, eps * 2, color=GREEN, alpha=0.10)
    ax.set_ylim(-0.1, 2.3)
    ax.set_xlabel(r"residual $e$")
    ax.set_ylabel("loss of one point")
    despine(ax, keep=("bottom", "left"))
    ax.set_title("a loss that is flat near zero", pad=10, fontsize=13)
    caption(ax, "close enough is free")


@figure("svr_dual")
def svr_dual(fig):
    """The regression dual: two multipliers per point, and the same kernel."""
    ax = canvas(fig)
    ax.text(W / 2, 3.50, "a point can miss the tube from above or from below",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(
        W / 2,
        2.95,
        r"$\min\ \frac{1}{2}\|w\|^2"
        r" + C\sum_i \left(\xi_i + \xi_i^{*}\right)"
        r"\qquad \mathrm{s.t.}\qquad"
        r"|y_i - f(x_i)| \leq \varepsilon + \xi_i^{(*)}$",
        ha="center",
        va="center",
        color=INK,
        fontsize=14,
    )
    ax.text(W / 2, 2.40, r"two slacks, so two multipliers:  "
                         r"$\alpha_i$ above and $\alpha_i^{*}$",
            ha="center", va="center", color=MUTED, fontsize=12)
    ax.text(
        W / 2,
        1.80,
        r"$f(x) = \sum_i \left(\hat\alpha_i - \hat\alpha_i^{*}\right)"
        r" k(x_i, x) + \hat{b}$",
        ha="center",
        va="center",
        color=GREEN,
        fontsize=18,
    )
    rows = [
        (GREEN, "inside the tube", r"$\hat\alpha_i = \hat\alpha_i^{*} = 0$",
         "not a support vector"),
        (GOLD, "on the tube", r"$0 < \hat\alpha_i^{(*)} < C$",
         r"used to recover $\hat{b}$"),
        (RED, "outside it", r"$\hat\alpha_i^{(*)} = C$", "bounded"),
    ]
    ax.plot([0.80, 8.30], [1.35, 1.35], color=GRID, lw=1.2)
    for i, (color, where, value, role) in enumerate(rows):
        y = 1.05 - i * 0.33
        ax.text(2.25, y, where, ha="right", va="center", color=color, fontsize=12)
        ax.text(4.30, y, value, ha="center", va="center", color=INK, fontsize=12.5)
        ax.text(6.00, y, role, ha="left", va="center", color=MUTED, fontsize=11.5)
    ax.text(W / 2, 0.08, "the same machinery as the classifier (kernels, soft-margin, etc...)",
            ha="center", va="center", color=RED, fontsize=12)


@figure("svr_epsilon")
def svr_epsilon(fig):
    """What the width of the tube buys and costs."""
    from sklearn.svm import SVR

    rng = np.random.default_rng(6)
    x = np.sort(rng.uniform(-3, 3, 70))
    y = np.sin(x) + 0.35 * x + rng.normal(0, 0.18, x.size)
    grid = np.linspace(-3.2, 3.2, 300)

    axes = fig.subplots(
        1, 3,
        gridspec_kw=dict(left=0.05, right=0.98, top=0.80, bottom=0.26, wspace=0.14),
    )
    for ax, eps, color, label in zip(
        axes, (0.05, 0.35, 1.2), (RED, GREEN, GOLD),
        ("tight", "balanced", "loose"),
    ):
        model = SVR(kernel="rbf", C=10, epsilon=eps, gamma=0.5).fit(x[:, None], y)
        pred = model.predict(grid[:, None])
        ax.fill_between(grid, pred - eps, pred + eps, color=color, alpha=0.16)
        ax.plot(grid, pred, color=color, lw=2.4)
        is_sv = np.zeros(len(x), bool)
        is_sv[model.support_] = True
        ax.scatter(x[~is_sv], y[~is_sv], s=14, color=MUTED, alpha=0.8,
                   edgecolors="none", zorder=3)
        ax.scatter(x[is_sv], y[is_sv], s=34, facecolors="none", edgecolors=color,
                   linewidths=1.3, zorder=4)
        ax.set_ylim(-2.4, 2.4)
        ax.set_xticks([])
        ax.set_yticks([])
        despine(ax)
        ax.set_title(f"{label}\n" + rf"$\varepsilon = {eps:g}$", color=color,
                     pad=8, fontsize=12.5, linespacing=1.8)
        caption(ax, f"{is_sv.sum()} support vectors")
    fig.text(0.5, 0.03, "a wider tube means fewer support vectors and a flatter fit",
             ha="center", color=MUTED, fontsize=12)


@figure("svm_cost")
def svm_cost(fig):
    """Where the kernel SVM stops being the right tool."""
    import time

    from sklearn.datasets import make_classification
    from sklearn.svm import SVC, LinearSVC

    sizes = [250, 500, 1000, 2000, 4000]
    kernel_times, linear_times = [], []
    for n in sizes:
        X, y = make_classification(n_samples=n, n_features=20, n_informative=8,
                                   random_state=0)
        t0 = time.perf_counter()
        SVC(kernel="rbf", C=1).fit(X, y)
        kernel_times.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        LinearSVC(C=1, dual="auto", max_iter=3000).fit(X, y)
        linear_times.append(time.perf_counter() - t0)

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.08, right=0.97, top=0.84, bottom=0.24, wspace=0.28),
    )
    ax = axes[0]
    ax.plot(sizes, kernel_times, "o-", color=RED, lw=2.4, ms=6)
    ax.plot(sizes, linear_times, "o-", color=GREEN, lw=2.4, ms=6)
    ax.text(sizes[-1] * 1.05, kernel_times[-1], "SVC (RBF)", color=RED,
            fontsize=11.5, va="center")
    ax.text(sizes[-1] * 1.05, linear_times[-1], "LinearSVC", color=GREEN,
            fontsize=11.5, va="center")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(200, 12000)
    ax.set_xlabel("training points n")
    ax.set_ylabel("fit time (s)")
    despine(ax, keep=("bottom", "left"))
    ax.set_title("20 features", pad=10, fontsize=13)
    caption(ax, r"the kernel fit grows like $n^2$ to $n^3$")

    ax = axes[1]
    ax.axis("off")
    ax.text(0.0, 0.93, "the Gram matrix is n × n", color=INK, fontsize=13.5,
            weight="bold", va="center")
    for i, (n, color) in enumerate([("1 000", GREEN), ("100 000", GOLD),
                                    ("1 000 000", RED)]):
        memory = {"1 000": "8 MB", "100 000": "80 GB", "1 000 000": "8 TB"}[n]
        ax.text(0.02, 0.76 - i * 0.13, f"n = {n}", color=color, fontsize=12.5,
                va="center")
        ax.text(0.46, 0.76 - i * 0.13, memory, color=color, fontsize=12.5,
                va="center")
    ax.text(0.0, 0.32, "rules of thumb", color=INK, fontsize=13.5, weight="bold",
            va="center")
    ax.text(0.02, 0.18, "n below ~10 000: any kernel", color=GREEN,
            fontsize=11.5, va="center")
    ax.text(0.02, 0.06, "n above that: LinearSVC, or a different model",
            color=RED, fontsize=11.5, va="center")


@figure("eq_kernel_dual")
def eq_kernel_dual(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.42, r"replace every $x_i^{T}x_j$ by $k(x_i, x_j)$, and "
                         r"nothing else changes",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(
        W / 2,
        2.65,
        r"$\max_{\alpha}\ \sum_i \alpha_i"
        r" - \frac{1}{2}\sum_{i,j}\alpha_i\alpha_j y_i y_j\, k(x_i, x_j)"
        r"\qquad 0 \leq \alpha_i \leq C, \ \ \sum_i \alpha_i y_i = 0$",
        ha="center",
        va="center",
        color=BLUE,
        fontsize=14,
    )
    ax.text(
        W / 2,
        1.60,
        r"$f(x) \;=\; \sum_{SV} \alpha_i y_i\, k(x_i, x) \;+\; b$",
        ha="center",
        va="center",
        color=GREEN,
        fontsize=20,
    )
    ax.text(W / 2, 0.95, "Prediction is a weighted vote of the support vectors.",
            ha="center", va="center", color=INK, fontsize=13)


@figure("kernel_props")
def kernel_props(fig):
    ax = canvas(fig)
    column(ax, 0.55, 3.25, 3.9, "Gain", [
        "curved boundaries at a linear price",
        "Φ never has to be written down",
        "any data with a similarity:\ntext, graphs, time series",
    ], GREEN, leading=0.34)
    column(ax, 4.90, 3.25, 3.9, "Costs", [
        "the support vectors must be kept",
        "no principled way to pick the kernel",
        "the Gram matrix is n × n:\nonly applies to small/moderate datasets",
    ], RED, leading=0.34)
    ax.plot([4.65, 4.65], [0.75, 3.35], color=GRID, lw=1.2)
    note(ax, "\"instance-based method\": stores data (not parameters)", y=0.38)


# ==========================================================================
# 4. more than two classes
# ==========================================================================
@figure("multiclass")
def multiclass(fig):
    from sklearn.svm import SVC

    rng = np.random.default_rng(13)
    centres = [(-2.2, -1.4), (2.3, -1.2), (0.1, 2.4)]
    X = np.vstack([rng.normal(c, 0.85, (45, 2)) for c in centres])
    y = np.repeat([0, 1, 2], 45)
    colors = (BLUE, RED, GREEN)
    markers = ("o", "^", "s")

    axes = fig.subplots(
        1, 3,
        gridspec_kw=dict(left=0.04, right=0.98, top=0.80, bottom=0.30, wspace=0.14),
    )
    gx, gy = np.meshgrid(np.linspace(-5, 5, 300), np.linspace(-4, 5, 300))
    grid = np.c_[gx.ravel(), gy.ravel()]

    def draw(ax, winner=None):
        if winner is not None:
            ax.contourf(gx, gy, winner, levels=[-0.5, 0.5, 1.5, 2.5],
                        colors=["#dce7f2", "#f6dcdc", "#d9efdb"])
        for k, (color, marker) in enumerate(zip(colors, markers)):
            ax.scatter(X[y == k, 0], X[y == k, 1], s=14, color=color,
                       marker=marker, edgecolors="none", zorder=3)
        ax.set_xlim(-5, 5)
        ax.set_ylim(-4, 5)
        ax.set_aspect("equal")
        _bare(ax)

    draw(axes[0])
    axes[0].set_title("three classes", pad=10, fontsize=13)
    caption(axes[0], "the SVM only knows how to say ±1")

    scores = [
        SVC(kernel="linear", C=1.0)
        .fit(X, np.where(y == k, 1, -1))
        .decision_function(grid)
        for k in range(3)
    ]
    draw(axes[1], np.argmax(scores, axis=0).reshape(gx.shape))
    axes[1].set_title("one against all", color=BLUE, pad=10, fontsize=13)
    caption(axes[1], r"$K$ fits,  $\hat{k} = \arg\max_k f_k(x)$")

    votes = np.zeros((len(grid), 3))
    for a in range(3):
        for b_ in range(a + 1, 3):
            mask = (y == a) | (y == b_)
            model = SVC(kernel="linear", C=1.0).fit(
                X[mask], np.where(y[mask] == a, 1, -1)
            )
            pick = model.decision_function(grid) > 0
            votes[pick, a] += 1
            votes[~pick, b_] += 1
    draw(axes[2], np.argmax(votes, axis=1).reshape(gx.shape))
    axes[2].set_title("one against one", color=GREEN, pad=10, fontsize=13)
    caption(axes[2], r"$K(K-1)/2$ fits, a majority vote")


@figure("svm_map")
def svm_map(fig):
    ax = canvas(fig)
    stages = [
        (BLUE, "widest street", r"$\min \frac{1}{2}\|w\|^2$"),
        (GOLD, "allow slack", r"$+\, C\sum_i \xi_i$"),
        (GREEN, "go to the dual", r"only $x_i^{T}x_j$ left"),
        (PURPLE, "swap in a kernel", r"$k(x_i, x_j)$"),
    ]
    w, gap = 1.95, 0.30
    x0 = (W - (4 * w + 3 * gap)) / 2
    for i, (color, title, sub) in enumerate(stages):
        x = x0 + i * (w + gap)
        box(ax, x, 1.75, w, 1.15, color, "")
        ax.text(x + w / 2, 2.62, title, ha="center", va="center", color=color,
                fontsize=13, weight="bold")
        ax.text(x + w / 2, 2.12, sub, ha="center", va="center", color=INK,
                fontsize=12)
        if i:
            arrow(ax, (x - gap + 0.04, 2.32), (x - 0.06, 2.32))


def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course03/img")
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
