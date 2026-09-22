#!/usr/bin/env python3
"""Every figure of Course01 (introduction and reminders on machine learning).

One function per figure, registered under the stem the slide deck asks for.
All figures share one canvas (9 x 3.7075 in), which is exactly the content
area pandoc leaves under a slide title, so a figure never has to be resized.

    python3 scripts/make_figures_c01.py Course01/img [stem ...]
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
from matplotlib import font_manager
from matplotlib.patches import (
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    Rectangle,
)
import matplotlib.pyplot as plt

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
# 1. course logistics
# ==========================================================================
@figure("about")
def about(fig):
    ax = canvas(fig)
    column(
        ax,
        0.35,
        3.05,
        4.0,
        "This course is about",
        [
            "advanced machine learning, with the theory behind it",
            "supervised and unsupervised approaches",
            "optimisation, high dimensions, statistical robustness",
        ],
        GREEN,
    )
    column(
        ax,
        4.85,
        3.05,
        4.0,
        "... and not",
        [
            "a course on applications with no theory",
            "a pure math theory course",
            "a neural networks course",
            "a reinforcement learning course",
        ],
        RED,
    )
    ax.plot([4.62, 4.62], [0.75, 3.15], color=GRID, lw=1.2)


@figure("prerequisites")
def prerequisites(fig):
    ax = canvas(fig)
    items = [
        (BLUE, "linear algebra", "matrix inversion,\neigenvectors, rank"),
        (GREEN, "probability", "densities, expectation,\nlikelihood, Bayes rule"),
        (PURPLE, "ML foundations", "train / test, loss,\nover-fitting"),
        (GOLD, "Python", "numpy, matplotlib,\nscikit-learn"),
    ]
    w, gap = 1.85, 0.32
    x0 = (W - (4 * w + 3 * gap)) / 2
    for i, (color, title, sub) in enumerate(items):
        x = x0 + i * (w + gap)
        box(ax, x, 1.55, w, 1.0, color, "")
        ax.text(
            x + w / 2,
            2.28,
            title,
            ha="center",
            va="center",
            color=color,
            fontsize=14,
            weight="bold",
        )
        ax.text(
            x + w / 2,
            1.88,
            sub,
            ha="center",
            va="center",
            color=INK,
            fontsize=10.5,
            linespacing=1.5,
        )
    note(ax, "the lab sessions assume you can already write and debug Python", y=0.75)


# ==========================================================================
# 2. background and reminders on ML
# ==========================================================================
@figure("applications")
def applications(fig):
    ax = canvas(fig)
    apps = [
        (BLUE, "spam filtering", "text → class"),
        (GREEN, "medical diagnosis", "image → label"),
        (RED, "fraud detection", "transaction → risk"),
        (PURPLE, "recommendation", "history → item"),
        (GOLD, "demand forecasting", "past → future"),
        (BLUE, "speech recognition", "signal → words"),
        (GREEN, "market segmentation", "customers → groups"),
        (PURPLE, "data visualisation", "d dims → 2 dims"),
    ]
    w, h, gx, gy = 2.0, 1.15, 0.24, 0.30
    x0 = (W - (4 * w + 3 * gx)) / 2
    for i, (color, title, sub) in enumerate(apps):
        col, row = i % 4, i // 4
        x, y = x0 + col * (w + gx), 1.95 - row * (h + gy)
        box(ax, x, y, w, h, color, "")
        ax.text(
            x + w / 2,
            y + 0.72,
            title,
            ha="center",
            va="center",
            color=color,
            fontsize=12.5,
            weight="bold",
        )
        ax.text(
            x + w / 2,
            y + 0.38,
            sub,
            ha="center",
            va="center",
            color=MUTED,
            fontsize=10.5,
        )


# ==========================================================================
# 3. reminders on parameter estimation
# ==========================================================================
@figure("estimation_setup")
def estimation_setup(fig):
    """The recipe from last year's linear regression, read as estimation."""
    ax = canvas(fig)
    steps = [
        (BLUE, "labelled examples", r"$X,\ y$"),
        (GREEN, "a hypothesis", r"$f_\theta(x)$"),
        (RED, "a cost", r"$J(\theta)$"),
        (PURPLE, "the parameters", r"$\hat{\theta} = \arg\min_\theta J(\theta)$"),
    ]
    w, gap = 1.85, 0.32
    x0 = (W - (4 * w + 3 * gap)) / 2
    for i, (color, label, formula) in enumerate(steps):
        x = x0 + i * (w + gap)
        box(ax, x, 2.42, w, 0.82, color, "")
        ax.text(
            x + w / 2, 2.83, formula, ha="center", va="center", color=color, fontsize=15
        )
        ax.text(
            x + w / 2, 3.44, label, ha="center", va="center", color=MUTED, fontsize=11.5
        )
        if i:
            arrow(ax, (x - gap + 0.04, 2.83), (x - 0.06, 2.83))
    ax.text(
        W / 2,
        2.00,
        "the parameters are estimated using the training data",
        ha="center",
        va="center",
        color=INK,
        fontsize=13,
    )
    column(
        ax,
        1.30,
        1.62,
        6.5,
        "two questions of estimation theory:",
        [
            r"which cost: least squares, a likelihood, a posterior ?",
            r"how good is the $\hat{\theta}$ we chose ?",
        ],
        INK,
        item_size=12.5,
        title_size=13,
    )


@figure("bias")
def bias(fig):
    ax = fig.subplots(gridspec_kw=dict(left=0.06, right=0.97, top=0.88, bottom=0.14))
    rng = np.random.default_rng(0)
    draws = rng.normal(1.35, 0.55, 40000)
    ax.hist(draws, bins=70, color=BLUE, alpha=0.5, density=True, edgecolor="none")
    ax.axvline(1.0, color=INK, lw=2)
    ax.axvline(draws.mean(), color=BLUE, lw=2, ls="--")
    ax.annotate(
        "",
        xy=(draws.mean(), 0.62),
        xytext=(1.0, 0.62),
        arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=2),
    )
    ax.text(1.18, 0.66, "bias", color=RED, fontsize=14, ha="center")
    ax.text(0.92, 0.80, r"$\theta_0$", color=INK, fontsize=14, ha="right")
    ax.text(
        draws.mean() + 0.08,
        0.80,
        r"$E[\hat{\theta}]$",
        color=BLUE,
        fontsize=14,
        ha="left",
    )
    ax.set_xlim(-0.6, 3.2)
    ax.set_ylim(0, 0.92)
    ax.set_yticks([])
    ax.set_xlabel(r"value taken by the estimator $\hat{\theta}$")
    despine(ax, keep=("bottom",))
    ax.set_title(
        r"$\mathrm{bias}(\hat{\theta}) = E[\hat{\theta}] - \theta_0$",
        color=RED,
        fontsize=16,
        pad=12,
    )


@figure("variance")
def variance(fig):
    axes = panels(
        fig,
        2,
        titles=["low variance", "high variance"],
        colors=[GREEN, RED],
        gridspec_kw={
            "left": 0.06,
            "right": 0.97,
            "top": 0.85,
            "bottom": 0.22,
            "wspace": 0.18,
        },
    )
    rng = np.random.default_rng(1)
    for ax, sd, color in zip(axes, (0.35, 1.05), (GREEN, RED)):
        draws = rng.normal(1.0, sd, 40000)
        ax.hist(draws, bins=80, color=color, alpha=0.45, density=True, edgecolor="none")
        ax.axvline(1.0, color=INK, lw=2)
        ax.text(
            1.3,
            ax.get_ylim()[1] * 0.84,
            r"$\theta_0$",
            color=INK,
            fontsize=14,
            ha="center",
        )
        ax.set_xlim(-2.6, 4.6)
        ax.set_yticks([])
        ax.set_xlabel(r"$\hat{\theta}$")
        despine(ax, keep=("bottom",))


@figure("dartboard")
def dartboard(fig):
    axes = fig.subplots(
        1,
        4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.82, bottom=0.16, wspace=0.10),
    )
    rng = np.random.default_rng(7)
    setups = [
        ("low bias\nlow variance", (0, 0), 0.16, GREEN),
        ("low bias\nhigh variance", (0, 0), 0.48, BLUE),
        ("high bias\nlow variance", (0.55, 0.35), 0.16, GOLD),
        ("high bias\nhigh variance", (0.55, 0.35), 0.48, RED),
    ]
    for ax, (title, centre, sd, color) in zip(axes, setups):
        for r, shade in [(1.0, "#f6f6f7"), (0.66, "#edeef0"), (0.33, "#e2e4e8")]:
            ax.add_patch(Circle((0, 0), r, facecolor=shade, edgecolor="white", lw=1.5))
        pts = rng.normal(centre, sd, size=(28, 2))
        ax.scatter(
            pts[:, 0],
            pts[:, 1],
            s=26,
            color=color,
            alpha=0.85,
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
        ax.scatter([0], [0], marker="+", s=90, color=INK, lw=2, zorder=4)
        ax.set_xlim(-1.35, 1.35)
        ax.set_ylim(-1.35, 1.35)
        ax.set_aspect("equal")
        ax.set_title(title, color=color, fontsize=12.5, pad=8, linespacing=1.5)
        blank(ax)
    axes[0].text(
        0.0,
        -1.30,
        r"the cross is $\theta_0$",
        ha="center",
        va="top",
        color=MUTED,
        fontsize=10.5,
        transform=axes[0].transData,
    )


@figure("eq_mse")
def eq_mse(fig):
    ax = canvas(fig)
    pieces = [
        (r"$MSE(\hat{\theta}_j)$", INK, "what we want small"),
        (r"$=$", INK, None),
        (r"$E\left[(\hat{\theta}_j - \theta_j)^2\right]$", PURPLE,
         "how far from the truth,\non average over samples"),
        (r"$=$", INK, None),
        (r"$\mathrm{bias}(\hat{\theta}_j)^2$", RED, "being wrong\non average"),
        (r"$+$", INK, None),
        (r"$Var(\hat{\theta}_j)$", BLUE, "being\nunstable"),
    ]
    size, gap, y = 25, 0.16, 2.55
    widths = [text_width(fig, ax, text, size) for text, _, _ in pieces]
    x = (W - sum(widths) - gap * (len(pieces) - 1)) / 2
    above = True
    for (text, color, label), w in zip(pieces, widths):
        ax.text(x, y, text, ha="left", va="center", color=color, fontsize=size)
        if label:
            centre = x + w / 2
            if above:
                ax.text(centre, 3.30, label, ha="center", va="bottom", color=color,
                        fontsize=11.5, linespacing=1.6)
                arrow(ax, (centre, 3.20), (centre, 2.95), color=color, lw=1.4)
            else:
                ax.text(centre, 1.80, label, ha="center", va="top", color=color,
                        fontsize=11.5, linespacing=1.6)
                arrow(ax, (centre, 1.90), (centre, 2.18), color=color, lw=1.4)
            above = not above if text.startswith("$E") else above
        x += w + gap


@figure("three_methods")
def three_methods(fig):
    ax = canvas(fig)
    methods = [
        (
            BLUE,
            "method of moments",
            "match the moments\nof the model to the\nmoments of the data",
            "easy, robust,\nless accurate",
        ),
        (
            GREEN,
            "maximum likelihood",
            "pick the parameter\nthat makes the data\nmost probable",
            "efficient,\nmodel-dependent",
        ),
        (
            PURPLE,
            "Bayesian estimation",
            "combine a prior on θ\nwith the likelihood,\nthen minimise a cost",
            "prior knowledge,\nprior sensitivity",
        ),
    ]
    w, gap = 2.65, 0.32
    x0 = (W - (3 * w + 2 * gap)) / 2
    for i, (color, title, idea, tradeoff) in enumerate(methods):
        x = x0 + i * (w + gap)
        box(ax, x, 1.15, w, 2.0, color, "")
        ax.text(
            x + w / 2,
            2.85,
            title,
            ha="center",
            va="center",
            color=color,
            fontsize=13.5,
            weight="bold",
        )
        ax.text(
            x + w / 2,
            2.15,
            idea,
            ha="center",
            va="center",
            color=INK,
            fontsize=11.5,
            linespacing=1.6,
        )
        ax.text(
            x + w / 2,
            1.45,
            tradeoff,
            ha="center",
            va="center",
            color=MUTED,
            fontsize=11,
            linespacing=1.5,
        )


@figure("mom_idea")
def mom_idea(fig):
    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.05, right=0.97, top=0.86, bottom=0.26, wspace=0.22),
    )
    rng = np.random.default_rng(4)
    x = rng.normal(2.0, 1.0, 400)
    ax = axes[0]
    ax.hist(x, bins=26, color=BLUE, alpha=0.45, density=True, edgecolor="none")
    ax.axvline(x.mean(), color=BLUE, lw=2)
    ax.annotate(
        "",
        xy=(x.mean() + x.std(), 0.12),
        xytext=(x.mean(), 0.12),
        arrowprops=dict(arrowstyle="<|-|>", color=BLUE, lw=1.8),
    )
    ax.text(
        x.mean() + x.std() / 2,
        0.16,
        r"$\hat\sigma$",
        color=BLUE,
        fontsize=13,
        ha="center",
    )
    ax.text(x.mean() + 0.12, 0.05, r"$U_1$", color=BLUE, fontsize=14, ha="left")
    ax.set_xlabel("the data")
    ax.set_yticks([])
    despine(ax, keep=("bottom",))
    ax.set_title("sample moments", color=BLUE, pad=10, fontsize=14)
    ax.text(
        0.98,
        0.95,
        r"$U_p = \frac{1}{n}\sum_i x_i^p$",
        color=BLUE,
        fontsize=14,
        transform=ax.transAxes,
        va="top",
        ha="right",
    )

    ax = axes[1]
    grid = np.linspace(-1.6, 5.6, 400)
    ax.plot(
        grid, np.exp(-0.5 * (grid - 2) ** 2) / np.sqrt(2 * np.pi), color=GREEN, lw=2.4
    )
    ax.axvline(2.0, color=GREEN, lw=2)
    ax.text(1.85, 0.9, r"$m_1 = E_\theta[x]$", color=GREEN, fontsize=14, ha="right", va="top",)
    ax.set_xlabel(r"the model $P_\theta$")
    ax.set_yticks([])
    despine(ax, keep=("bottom",))
    ax.set_title("theoretical moments", color=GREEN, pad=10, fontsize=14)
    ax.text(
        0.98,
        0.95,
        r"$m_k = E_\theta[x^k]$",
        color=GREEN,
        fontsize=14,
        transform=ax.transAxes,
        va="top",
        ha="right",
    )
    fig.text(
        0.5,
        0.04,
        "set them equal, solve for θ",
        ha="center",
        color=MUTED,
        fontsize=12,
    )


@figure("mom_gaussian")
def mom_gaussian(fig):
    ax = canvas(fig)
    ax.text(
        W / 2,
        3.42,
        r"Gaussian:  $\theta = (\mu, \sigma^2)$",
        ha="center",
        va="center",
        color=INK,
        fontsize=15,
    )
    rows = [
        (GREEN, r"$E[x] = \mu$", r"$E[x^2] = \sigma^2 + \mu^2$", "theoretical"),
        (
            BLUE,
            r"$U_1 = \frac{1}{n}\sum_i x_i$",
            r"$U_2 = \frac{1}{n}\sum_i x_i^2$",
            "sample",
        ),
    ]
    for j, (color, left, right, tag) in enumerate(rows):
        y = 2.65 - j * 0.72
        ax.text(1.05, y, tag, ha="right", va="center", color=color, fontsize=12)
        ax.text(2.55, y, left, ha="center", va="center", color=color, fontsize=17)
        ax.text(5.90, y, right, ha="center", va="center", color=color, fontsize=17)
    ax.plot([1.25, 8.0], [1.60, 1.60], color=GRID, lw=1.2)
    ax.text(1.05, 1.15, "solution", ha="right", va="center", color=PURPLE, fontsize=12)
    ax.text(
        2.55,
        1.10,
        r"$\hat\mu = \frac{1}{n}\sum_i x_i$",
        ha="center",
        va="center",
        color=PURPLE,
        fontsize=17,
    )
    ax.text(
        5.90,
        1.10,
        r"$\hat\sigma^2 = \frac{1}{n}\sum_i (x_i - \hat\mu)^2$",
        ha="center",
        va="center",
        color=PURPLE,
        fontsize=17,
    )


@figure("mom_props")
def mom_props(fig):
    ax = canvas(fig)
    column(
        ax,
        0.55,
        3.20,
        3.8,
        "in its favour",
        [
            "strongly consistent",
            "robust — moments move slowly",
            "cheap: closed form, no search",
            "a good starting point for other methods",
        ],
        GREEN,
    )
    column(
        ax,
        4.90,
        3.20,
        3.8,
        "against",
        [
            "not asymptotically efficient",
            "generally less accurate",
            "higher moments are noisy",
            "can leave the parameter space",
        ],
        RED,
    )
    ax.plot([4.65, 4.65], [0.55, 3.30], color=GRID, lw=1.2)


@figure("eq_likelihood")
def eq_likelihood(fig):
    ax = canvas(fig)
    ax.text(
        W / 2,
        3.42,
        r"the model gives every observation a density  $f(x;\theta)$"
        r"   —   the sample is i.i.d.",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=13,
    )
    equation(
        ax,
        r"$L(x_1,\dots,x_n;\theta)\ =\ \prod_{i=1}^{n} f(x_i;\theta)"
        r"\qquad \ell(\theta)\ =\ \log L\ =\ \sum_{i=1}^{n}"
        r"\log f(x_i;\theta)$",
        y=2.62,
        size=21,
    )
    readings = [
        (
            BLUE,
            r"as a function of $x$, with $\theta$ fixed",
            "a density: how the data is spread",
            r"$\int f(x;\theta)\, dx = 1$",
        ),
        (
            GREEN,
            r"as a function of $\theta$, with $x$ fixed",
            "the likelihood: how well θ explains the data",
            r"$\int L(x;\theta)\, d\theta \neq 1$",
        ),
    ]
    for i, (color, heading, meaning, integral) in enumerate(readings):
        x = 0.50 + i * 4.15
        box(ax, x, 0.55, 3.85, 1.30, color, "")
        ax.text(
            x + 1.93, 1.60, heading, ha="center", va="center", color=color, fontsize=13
        )
        ax.text(
            x + 1.93, 1.20, meaning, ha="center", va="center", color=INK, fontsize=11
        )
        ax.text(
            x + 1.93, 0.83, integral, ha="center", va="center", color=MUTED, fontsize=14
        )
    ax.text(
        4.65,
        0.20,
        "the likelihood is not a probability over θ",
        ha="center",
        va="center",
        color=RED,
        fontsize=12,
    )


@figure("likelihood_build")
def likelihood_build(fig):
    from scipy.stats import norm

    rng = np.random.default_rng(19)
    x = rng.normal(2.0, 1.0, 7)
    grid = np.linspace(-2.0, 6.0, 400)
    bad, good = 0.3, x.mean()

    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.05, right=0.98, top=0.84, bottom=0.24, wspace=0.26),
    )
    for ax, mu, color, title in [
        (axes[0], bad, RED, r"a poor $\theta$"),
        (axes[1], good, GREEN, r"a better $\theta$"),
    ]:
        heights = norm.pdf(x, mu, 1.0)
        ax.plot(grid, norm.pdf(grid, mu, 1.0), color=color, lw=2.4)
        ax.vlines(x, 0, heights, color=color, lw=1.4, alpha=0.7)
        ax.plot(x, heights, "o", color=color, ms=6)
        ax.plot(x, np.zeros_like(x), "|", color=INK, ms=12, mew=1.6)
        ax.set_ylim(0, 0.46)
        ax.set_yticks([])
        ax.set_xlabel(r"$x$")
        despine(ax, keep=("bottom",))
        ax.set_title(title, color=color, pad=10, fontsize=14)
        caption(
            ax,
            rf"$L = {np.prod(heights):.1e}$      $\ell = {np.sum(np.log(heights)):.1f}$",
        )

    ax = axes[2]
    mus = np.linspace(-1.0, 5.0, 400)
    like = np.array([np.prod(norm.pdf(x, m, 1.0)) for m in mus])
    ax.plot(mus, like, color=PURPLE, lw=2.6)
    for mu, color in [(bad, RED), (good, GREEN)]:
        value = np.prod(norm.pdf(x, mu, 1.0))
        ax.plot([mu], [value], "o", color=color, ms=9)
        ax.vlines(mu, 0, value, color=color, lw=1.4, ls="--")
    ax.set_xlabel(r"$\theta$")
    ax.set_yticks([])
    despine(ax, keep=("bottom",))
    ax.set_title(r"$L(\theta)$", color=PURPLE, pad=10, fontsize=14)


@figure("log_likelihood")
def log_likelihood(fig):
    from scipy.stats import norm

    rng = np.random.default_rng(19)
    x = rng.normal(2.0, 1.0, 40)
    mus = np.linspace(0.6, 3.4, 400)
    like = np.array([np.prod(norm.pdf(x, m, 1.0)) for m in mus])
    loglike = np.array([np.sum(norm.logpdf(x, m, 1.0)) for m in mus])

    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.09, right=0.97, top=0.84, bottom=0.24, wspace=0.26),
    )
    for ax, values, color, title, label in [
        (axes[0], like, RED, r"$L(\theta)$ — a product of 40 terms", "likelihood"),
        (axes[1], loglike, GREEN, r"$\ell(\theta)$ — a sum of 40 terms",
         "log-likelihood"),
    ]:
        ax.plot(mus, values, color=color, lw=2.6)
        ax.axvline(mus[values.argmax()], color=INK, lw=1.6, ls="--")
        ax.set_xlabel(r"$\theta$")
        ax.set_ylabel(label)
        ax.set_title(title, color=color, pad=10, fontsize=14)
    axes[0].ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    caption(axes[0], "values near the limit of a float")
    caption(axes[1], "the argmax is the same")


@figure("mle_idea")
def mle_idea(fig):
    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.05, right=0.98, top=0.84, bottom=0.22, wspace=0.28),
    )
    rng = np.random.default_rng(11)
    x = rng.normal(1.8, 1.0, 12)
    grid = np.linspace(-2.5, 6.0, 400)

    ax = axes[0]
    for mu, color, alpha in [(0.2, MUTED, 0.9), (1.8, GREEN, 1.0), (3.6, MUTED, 0.9)]:
        ax.plot(
            grid,
            np.exp(-0.5 * (grid - mu) ** 2) / np.sqrt(2 * np.pi),
            color=color,
            lw=2.2,
            alpha=alpha,
        )
    ax.plot(x, np.full_like(x, -0.03), "|", color=BLUE, ms=14, mew=2)
    ax.set_title("1.  the data is fixed", pad=10, fontsize=13)
    ax.set_yticks([])
    ax.set_xlabel(r"$x$")
    despine(ax, keep=("bottom",))
    caption(ax, "the model slides over it")

    ax = axes[1]
    mus = np.linspace(-1.0, 4.6, 300)
    ll = np.array([np.sum(-0.5 * (x - m) ** 2) for m in mus])
    ax.plot(mus, ll, color=GREEN, lw=2.4)
    ax.axvline(mus[ll.argmax()], color=GREEN, ls="--", lw=1.6)
    ax.set_title(r"2.  read log-likelyhood as a function of $\theta$", pad=10, fontsize=13)
    ax.set_yticks([])
    ax.set_xlabel(r"$\mu$")
    ax.set_ylabel(r"$\ell(x;\mu)$")
    despine(ax, keep=("bottom",))
    caption(ax, "the log-likelihood")

    ax = axes[2]
    ax.plot(mus, ll, color=GREEN, lw=2.4, alpha=0.35)
    i = ll.argmax()
    ax.plot(mus[i], ll[i], "o", color=GREEN, ms=11)
    ax.annotate(
        r"$\hat\theta_n$",
        xy=(mus[i], ll[i]),
        xytext=(mus[i] + 0.9, ll[i] - 5.5),
        color=GREEN,
        fontsize=15,
        arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.6),
    )
    ax.set_title("3.  take the argmax", pad=10, fontsize=13)
    ax.set_yticks([])
    ax.set_xlabel(r"$\mu$")
    despine(ax, keep=("bottom",))
    caption(ax, "first derivative zero, second negative")


@figure("mle_gaussian")
def mle_gaussian(fig):
    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.05, right=0.96, top=0.86, bottom=0.30, wspace=0.22),
    )
    rng = np.random.default_rng(5)
    x = rng.normal(2.0, 1.2, 300)
    grid = np.linspace(-2.5, 6.5, 400)
    ax = axes[0]
    ax.hist(x, bins=26, density=True, color=LIGHT, edgecolor="white")
    ax.plot(
        grid,
        np.exp(-0.5 * ((grid - x.mean()) / x.std()) ** 2)
        / (x.std() * np.sqrt(2 * np.pi)),
        color=GREEN,
        lw=2.6,
    )
    ax.set_yticks([])
    ax.set_xlabel(r"$x$")
    despine(ax, keep=("bottom",))
    ax.set_title("the fitted Gaussian", color=GREEN, pad=10, fontsize=13.5)
    caption(ax, "same answer as the method of moments in the Gaussian case")

    ax = axes[1]
    mus = np.linspace(1.2, 2.8, 160)
    sds = np.linspace(0.85, 1.7, 160)
    MU, SD = np.meshgrid(mus, sds)
    ll = -len(x) * np.log(SD) - ((x[:, None, None] - MU) ** 2).sum(0) / (2 * SD**2)
    ax.contourf(MU, SD, ll, levels=18, cmap="Purples")
    ax.plot(x.mean(), x.std(), "o", color=RED, ms=10)
    ax.set_xlabel(r"$\mu$")
    ax.set_ylabel(r"$\sigma$")
    ax.set_title("the log-likelihood surface", color=PURPLE, pad=10, fontsize=13.5)
    ax.annotate(
        r"$\hat\mu = \bar{x}$,  $\hat\sigma^2 = \frac{1}{n}\sum_i"
        r"(x_i-\bar{x})^2$",
        xy=(0.5, -0.30),
        xycoords="axes fraction",
        ha="center",
        va="top",
        color=MUTED,
        fontsize=12,
    )


@figure("mle_props")
def mle_props(fig):
    ax = canvas(fig)
    column(
        ax,
        0.55,
        3.20,
        3.8,
        "in its favour",
        [
            "one analytical function to optimise",
            "strongly consistent, asymptotically unbiased",
            "asymptotically efficient",
            "smallest variance among unbiased estimators",
        ],
        GREEN,
    )
    column(
        ax,
        4.90,
        3.20,
        3.8,
        "against",
        [
            "needs the shape of the density",
            "not robust to outliers",
            "no closed form in general",
            "can be biased for finite n",
        ],
        RED,
    )
    ax.plot([4.65, 4.65], [0.55, 3.30], color=GRID, lw=1.2)


@figure("bayes_setup")
def bayes_setup(fig):
    ax = fig.subplots(gridspec_kw=dict(left=0.06, right=0.97, top=0.86, bottom=0.18))
    grid = np.linspace(-1.0, 5.0, 500)

    def norm(m, s):
        return np.exp(-0.5 * ((grid - m) / s) ** 2) / (s * np.sqrt(2 * np.pi))

    prior, like = norm(0.8, 0.9), norm(3.0, 0.55)
    post = prior * like
    post /= np.trapezoid(post, grid)
    for y, color, label in [
        (prior, BLUE, r"prior  $p(\theta)$"),
        (like, GREEN, r"likelihood  $L(x;\theta)$"),
        (post, PURPLE, r"posterior  $p(\theta|x)$"),
    ]:
        ax.plot(grid, y, color=color, lw=2.6, label=label)
    ax.fill_between(grid, post, color=PURPLE, alpha=0.12)
    ax.legend(loc="upper left", fontsize=12)
    ax.set_xlabel(r"$\theta$")
    ax.set_yticks([])
    despine(ax, keep=("bottom",))


@figure("eq_posterior")
def eq_posterior(fig):
    ax = canvas(fig)
    equation(
        ax,
        r"$p(\theta|x_1,\dots,x_n) \;=\; "
        r"\frac{L(x_1,\dots,x_n;\theta)\; p(\theta)}"
        r"{\int_{\mathbb{R}^p} L(x_1,\dots,x_n;\theta)\, p(\theta)\, d\theta}"
        r"\;\propto\; L(x_1,\dots,x_n;\theta)\, p(\theta)$",
        y=2.50,
        size=21,
    )
    ax.text(
        W / 2,
        1.40,
        "the posterior gives a whole distribution",
        ha="center",
        va="center",
        color=PURPLE,
        fontsize=15,
    )
    note(ax, r"which number $\hat\theta$ should be reported"+"?", y=0.80)


@figure("cost_idea")
def cost_idea(fig):
    ax = canvas(fig)
    grid = np.linspace(-1.5, 6.0, 600)
    post = 0.65 * np.exp(-0.5 * ((grid - 1.6) / 0.75) ** 2) + 0.35 * np.exp(
        -0.5 * ((grid - 3.8) / 0.55) ** 2
    )
    post /= np.trapezoid(post, grid)

    plot = fig.add_axes([0.05, 0.20, 0.41, 0.58])
    plot.plot(grid, post, color=PURPLE, lw=2.4)
    plot.fill_between(grid, post, color=PURPLE, alpha=0.12)
    answer = 2.6
    plot.axvline(answer, color=GREEN, lw=2.2)
    plot.annotate(
        "",
        xy=(4.2, 0.55),
        xytext=(answer, 0.55),
        arrowprops={"arrowstyle": "<|-|>", "color": RED, "lw": 1.6},
    )
    plot.text(3.45, 0.1, r"$\theta - \hat\theta$", color=RED, fontsize=13,
              ha="center")
    plot.text(answer + 0.12, post.max() * 1.02, r"answer $\hat\theta$",
              color=GREEN, fontsize=12, ha="left")
    plot.text(-1.6, post.max() * 0.55, r"$\theta$'s distribution",
              color=PURPLE, fontsize=12, ha="left", linespacing=1.5)
    plot.set_ylim(0, post.max() * 1.18)
    plot.set_xlabel(r"$\theta$")
    plot.set_yticks([])
    despine(plot, keep=("bottom",))

    x0 = 4.55
    ax.text(
        x0,
        3.25,
        r"$c(\theta, \hat\theta)$  :  what it costs to answer $\hat{\theta}$",
        ha="left",
        va="center",
        color=INK,
        fontsize=14,
    )
    ax.text(
        x0+1,
        2.88,
        r"when the truth turns out to be $\theta$",
        ha="left",
        va="center",
        color=INK,
        fontsize=12.5,
    )
    ax.text(
        x0,
        2.2,
        r"$\theta$ is unknown"
        "\nthe average cost over the posterior is:",
        ha="left",
        va="center",
        color=INK,
        fontsize=12.5,
        linespacing=1.6,
    )
    ax.text(
        x0 + 1.95,
        1.35,
        r"$\hat{\theta} \;=\; \arg\min_{a}\ "
        r"\int c(\theta, a)\, p(\theta|x)\, d\theta$",
        ha="center",
        va="center",
        color=GREEN,
        fontsize=18,
    )


@figure("cost_zoo")
def cost_zoo(fig):
    grid = np.linspace(-1.5, 6.0, 800)
    post = 0.65 * np.exp(-0.5 * ((grid - 1.6) / 0.75) ** 2) + 0.35 * np.exp(
        -0.5 * ((grid - 3.8) / 0.55) ** 2
    )
    post /= np.trapezoid(post, grid)
    cdf = np.concatenate([[0], np.cumsum((post[1:] + post[:-1]) / 2 * np.diff(grid))])
    mean = np.trapezoid(grid * post, grid)
    median = grid[np.searchsorted(cdf, 0.5)]
    mode = grid[post.argmax()]

    err = np.linspace(-2, 2, 400)
    columns = [
        (GREEN, "squared cost", r"$(\theta - a)^2$", err**2, mean,
         "the posterior mean — MMSE"),
        (GOLD, "absolute cost", r"$|\theta - a|$", np.abs(err), median,
         "the posterior median"),
        (RED, "0–1 cost", r"$\mathbb{1}[\theta \neq a]$",
         (np.abs(err) > 0.12).astype(float), mode, "the posterior mode — MAP"),
    ]
    axes = fig.subplots(
        2,
        3,
        gridspec_kw=dict(
            left=0.04,
            right=0.98,
            top=0.82,
            bottom=0.24,
            wspace=0.14,
            hspace=0.55,
            height_ratios=[1, 1.5],
        ),
    )
    for i, (color, name, formula, cost, estimate, label) in enumerate(columns):
        top, bottom = axes[0, i], axes[1, i]
        top.plot(err, cost, color=color, lw=2.4)
        top.set_ylim(-0.15, 1.3 if i else 4.2)
        top.set_xlabel(r"$\theta - a$", labelpad=1)
        top.set_xticks([0])
        top.set_yticks([])
        despine(top, keep=("bottom",))
        top.set_title(f"{name}   {formula}", color=color, pad=8, fontsize=13)

        bottom.plot(grid, post, color=PURPLE, lw=2.2)
        bottom.fill_between(grid, post, color=PURPLE, alpha=0.10)
        bottom.axvline(estimate, color=color, lw=2.4)
        bottom.text(
            estimate + 0.12,
            post.max() * 0.92,
            f"{estimate:.2f}",
            color=color,
            fontsize=12,
            ha="left",
        )
        bottom.set_xlabel(r"$\theta$", labelpad=1)
        bottom.set_yticks([])
        despine(bottom, keep=("bottom",))
        bottom.annotate(
            label,
            xy=(0.5, -0.40),
            xycoords="axes fraction",
            ha="center",
            va="top",
            color=color,
            fontsize=12,
        )


@figure("prior_effect")
def prior_effect(fig):
    axes = panels(
        fig,
        3,
        titles=[r"$n = 3$", r"$n = 20$", r"$n = 200$"],
        colors=[INK] * 3,
        gridspec_kw=dict(left=0.05, right=0.98, top=0.78, bottom=0.22, wspace=0.18),
    )
    rng = np.random.default_rng(2)
    grid = np.linspace(-1.5, 5.0, 500)
    true_mu, sd, prior_mu, prior_sd = 2.5, 1.2, 0.0, 0.8
    for ax, n in zip(axes, (3, 20, 200)):
        x = rng.normal(true_mu, sd, n)
        prior = np.exp(-0.5 * ((grid - prior_mu) / prior_sd) ** 2)
        like = np.exp(-0.5 * n * ((grid - x.mean()) / sd) ** 2)
        post = prior * like
        for y, color in [(prior, BLUE), (like, GREEN), (post, PURPLE)]:
            ax.plot(grid, y / y.max(), color=color, lw=2.4)
        ax.axvline(true_mu, color=MUTED, lw=1.4, ls=":")
        ax.set_yticks([])
        ax.set_xlabel(r"$\mu$")
        despine(ax, keep=("bottom",))
    for x, label, color in [
        (0.30, "prior", BLUE),
        (0.47, "likelihood", GREEN),
        (0.67, "posterior", PURPLE),
    ]:
        fig.text(x, 0.955, label, color=color, fontsize=12, ha="center")


@figure("divisor_family")
def divisor_family(fig):
    """The three estimators of the compare-slide are one family, three rules."""
    ax = canvas(fig)
    ax.text(
        W / 2,
        3.40,
        r"every estimator of $\sigma^2$ below divides the same scatter"
        r"   $S = \sum_i (x_i - \bar{x})^2$",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=12.5,
    )
    ax.text(
        W / 2,
        2.80,
        r"$\hat{\sigma}^2 \;=\; S \,/\, c$",
        ha="center",
        va="center",
        color=INK,
        fontsize=26,
    )
    rules = [
        (GREEN, "MLE", r"$c = n$", "maximise the likelihood"),
        (BLUE, "unbiased", r"$c = n-1$", r"make $E[\hat\sigma^2] = \sigma^2$"),
        (PURPLE, "shrunk", r"$c = n+1$", "minimise the MSE"),
    ]
    w, gap = 2.55, 0.35
    x0 = (W - (3 * w + 2 * gap)) / 2
    for i, (color, name, divisor, principle) in enumerate(rules):
        x = x0 + i * (w + gap)
        box(ax, x, 0.85, w, 1.30, color, "")
        ax.text(
            x + w / 2, 1.88, name, ha="center", va="center", color=color,
            fontsize=14, weight="bold",
        )
        ax.text(
            x + w / 2, 1.48, divisor, ha="center", va="center", color=color,
            fontsize=17,
        )
        ax.text(
            x + w / 2, 1.08, principle, ha="center", va="center", color=INK,
            fontsize=11.5,
        )


@figure("mle_variance")
def mle_variance(fig):
    ax = canvas(fig)
    ax.text(
        W / 2,
        3.38,
        r"the Gaussian log-likelihood, once $\hat\mu = \bar{x}$ is plugged in",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=12.5,
    )
    lines = [
        (r"$\ell(\sigma^2) \;=\; -\frac{n}{2}\log(2\pi\sigma^2)"
         r" \;-\; \frac{S}{2\sigma^2}$", INK, 2.80),
        (r"$\frac{\partial \ell}{\partial \sigma^2} \;=\; "
         r"-\frac{n}{2\sigma^2} \;+\; \frac{S}{2\sigma^4} \;=\; 0$",
         INK, 1.90),
        (r"$\hat{\sigma}^2_{MLE} \;=\; \frac{S}{n}$", GREEN, 1.00),
    ]
    for text, color, y in lines:
        ax.text(W / 2, y, text, ha="center", va="center", color=color, fontsize=20)
    note(
        ax,
        "the likelihood only asks which σ² makes this sample most probable, it does not make it right on average",
        y=0.32,
    )


@figure("bessel")
def bessel(fig):
    rng = np.random.default_rng(6)
    n = 8
    mu = 0.0
    x = rng.normal(mu, 1.0, n)
    xbar = x.mean()

    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.05, right=0.97, top=0.84, bottom=0.22, wspace=0.18),
    )
    ax = axes[0]
    ax.axhline(0, color=GRID, lw=1.2)
    ax.plot(x, np.zeros(n), "o", color=INK, ms=7, zorder=3)
    ax.axvline(mu, color=MUTED, lw=2)
    ax.axvline(xbar, color=BLUE, lw=2)
    for j, xi in enumerate(x):
        top, bottom = 0.18 + 0.055 * j, -0.18 - 0.055 * j
        ax.plot([xi, xbar], [top, top], color=BLUE, lw=1.4, alpha=0.75)
        ax.plot([xi, mu], [bottom, bottom], color=MUTED, lw=1.4, alpha=0.75)
    ax.text(mu - 0.10, -0.80, r"distances to $\mu$", color=MUTED, fontsize=12,
            ha="right")
    ax.text(xbar + 0.10, 0.80, r"distances to $\bar{x}$", color=BLUE,
            fontsize=12, ha="left")
    ax.set_ylim(-0.92, 0.92)
    ax.set_yticks([])
    ax.set_xlabel(r"$x$")
    despine(ax, keep=("bottom",))
    caption(
        ax,
        r"$\sum_i (x_i-\bar{x})^2 = %.1f$   <   $\sum_i (x_i-\mu)^2 = %.1f$"
        % (((x - xbar) ** 2).sum(), ((x - mu) ** 2).sum()),
    )

    ax = axes[1]
    ax.axis("off")
    ax.text(
        0.5,
        0.93,
        r"$\sum_i (x_i-\mu)^2 \;=\; S \;+\; n(\bar{x}-\mu)^2$",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=17,
        color=INK,
    )
    ax.text(
        0.5,
        0.70,
        "the sample mean sits where it fits the sample best,\n"
        "so S is always a little too small",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=12,
        color=MUTED,
        linespacing=1.6,
    )
    ax.text(
        0.5,
        0.44,
        r"$E[S] \;=\; (n-1)\,\sigma^2$",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=19,
        color=RED,
    )
    ax.text(
        0.5,
        0.20,
        r"$E\!\left[\frac{S}{n-1}\right] = \sigma^2$"
        r"      but      "
        r"$E\!\left[\frac{S}{n}\right] = \frac{n-1}{n}\,\sigma^2$",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=16,
        color=BLUE,
    )
    ax.text(
        0.5,
        0.02,
        "one degree of freedom was spent estimating the mean",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=12,
        color=MUTED,
    )


@figure("mse_divisor")
def mse_divisor(fig):
    """MSE of S/c as c moves, for a Gaussian sample of size n."""
    n = 8
    c = np.linspace(5.0, 14.0, 500)
    variance = 2 * (n - 1) / c**2
    bias2 = ((n - 1) / c - 1) ** 2
    total = variance + bias2

    ax = fig.subplots(
        gridspec_kw=dict(left=0.08, right=0.72, top=0.86, bottom=0.20)
    )
    ax.plot(c, bias2, color=RED, lw=2.2, ls="--")
    ax.plot(c, variance, color=GOLD, lw=2.2, ls="--")
    ax.plot(c, total, color=INK, lw=2.8)
    ax.text(12.6, 0.315, "MSE", color=INK, fontsize=12, ha="center")
    ax.text(13.1, 0.155, r"bias$^2$", color=RED, fontsize=12, ha="center")
    ax.text(12.6, 0.045, "variance", color=GOLD, fontsize=12, ha="center")
    marks = [
        (n - 1, BLUE, "unbiased", (6.2, 0.185)),
        (n, GREEN, "MLE", (7.7, 0.125)),
        (n + 1, PURPLE, "shrunk", (10.7, 0.175)),
    ]
    for value, color, name, xytext in marks:
        score = 2 * (n - 1) / value**2 + ((n - 1) / value - 1) ** 2
        ax.plot([value], [score], "o", color=color, ms=10, zorder=4)
        ax.annotate(
            f"{name}\nc = {value}",
            xy=(value, score),
            xytext=xytext,
            ha="center",
            va="center",
            color=color,
            fontsize=11,
            linespacing=1.5,
            arrowprops=dict(arrowstyle="-", color=color, lw=1.0, shrinkB=8),
        )
    ax.set_xlabel(r"the divisor $c$")
    ax.set_ylabel(r"error on $\sigma^2$")
    ax.set_ylim(0, 0.42)
    ax.set_title(r"$n = 8$", pad=10, fontsize=13)

    side = fig.add_axes([0.74, 0.20, 0.25, 0.66])
    side.axis("off")
    side.text(
        0.0, 0.88, "raising c", transform=side.transAxes, fontsize=13,
        color=INK, weight="bold", va="center",
    )
    for i, (color, text) in enumerate(
        [(GOLD, "shrinks the variance"), (RED, "grows the bias")]
    ):
        side.text(
            0.0, 0.70 - i * 0.14, text, transform=side.transAxes, fontsize=12,
            color=color, va="center",
        )
    side.text(
        0.0,
        0.34,
        r"the sum is smallest at $c = n+1$",
        transform=side.transAxes,
        fontsize=13,
        color=PURPLE,
        va="center",
        linespacing=1.6,
    )


@figure("estimators_compare")
def estimators_compare(fig):
    """Three estimators of the same variance, judged by bias, spread and MSE."""
    rng = np.random.default_rng(12)
    n, true_sigma2, reps = 8, 1.0, 4000
    samples = rng.normal(0.0, np.sqrt(true_sigma2), size=(reps, n))
    scatter = ((samples - samples.mean(1, keepdims=True)) ** 2).sum(1)
    estimators = [
        (BLUE, "unbiased", r"$n-1$", scatter / (n - 1)),
        (GREEN, "MLE", r"$n$", scatter / n),
        (PURPLE, "shrunk", r"$n+1$", scatter / (n + 1)),
    ]

    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(
            left=0.02,
            right=0.97,
            top=0.82,
            bottom=0.20,
            wspace=0.24,
            width_ratios=[1.0, 1.45, 0.95],
        ),
    )

    # --- what the experiment is -------------------------------------------
    ax = axes[0]
    ax.axis("off")
    ax.set_title("experiment:", pad=10, fontsize=13.5)
    ax.text(
        0.0,
        0.95,
        r"draw $n = 8$ points from $N(0, \sigma^2)$",
        transform=ax.transAxes,
        fontsize=12,
        color=INK,
        va="center",
    )
    ax.text(
        0.0,
        0.80,
        "measure their scatter",
        transform=ax.transAxes,
        fontsize=12,
        color=INK,
        va="center",
    )
    ax.text(
        0.10,
        0.66,
        r"$S = \sum_i (x_i - \bar{x})^2$",
        transform=ax.transAxes,
        fontsize=12,
        color=INK,
        va="center",
    )
    ax.text(
        0.0,
        0.50,
        "then divide by:",
        transform=ax.transAxes,
        fontsize=12,
        color=INK,
        va="center",
    )
    for i, (color, name, divisor, _) in enumerate(estimators):
        y = 0.35 - i * 0.12
        ax.text(
            0.10, y, name, transform=ax.transAxes, fontsize=12, color=color,
            va="center", weight="bold",
        )
        ax.text(
            0.62, y, divisor, transform=ax.transAxes, fontsize=13, color=color,
            va="center",
        )
    ax.text(
        0.0,
        0.01,
        "repeat 4000 times",
        transform=ax.transAxes,
        fontsize=12,
        color=MUTED,
        va="center",
    )

    # --- where the 4000 estimates land, one strip per estimator -----------
    ax = axes[1]
    ax.set_title("histogram of the 4000 estimates", pad=10, fontsize=13.5)
    edges = np.linspace(0, 3.2, 80)
    centres = (edges[:-1] + edges[1:]) / 2
    for i, (color, name, _, values) in enumerate(estimators):
        base = 2 - i
        density, _ = np.histogram(values, bins=edges, density=True)
        floor = base + 0.22
        ax.fill_between(
            centres, floor, floor + density * 0.70, color=color, alpha=0.35, lw=0
        )
        ax.plot(centres, floor + density * 0.70, color=color, lw=1.8)
        mean = values.mean()
        ax.plot([mean, mean], [floor, floor + 0.72], color=color, lw=2.2)
        ax.text(
            3.12, base + 0.62, name, color=color, fontsize=12, va="center",
            ha="right", weight="bold",
        )
        if abs(mean - true_sigma2) > 0.01:
            ax.annotate(
                "",
                xy=(mean, base + 0.09),
                xytext=(true_sigma2, base + 0.09),
                arrowprops=dict(arrowstyle="<|-|>", color=color, lw=1.6),
            )
            ax.text(
                min(mean, true_sigma2) - 0.07,
                base + 0.09,
                "bias",
                color=color,
                fontsize=11,
                ha="right",
                va="center",
            )
        else:
            ax.text(
                mean + 0.10, base + 0.09, "no bias", color=color, fontsize=11,
                ha="left", va="center",
            )
    ax.axvline(true_sigma2, color=INK, lw=2, zorder=0)
    ax.text(
        true_sigma2, 3.02, r"real $\sigma^2$", color=INK, fontsize=12,
        ha="center",
    )
    ax.set_xlim(0, 3.2)
    ax.set_ylim(0, 3.25)
    ax.set_yticks([])
    ax.set_xlabel(r"the estimate of $\sigma^2$")
    despine(ax, keep=("bottom",))

    # --- the same three, scored -------------------------------------------
    ax = axes[2]
    ax.set_title(r"$\mathrm{bias}^2 + \mathrm{Var} = MSE$", pad=10, fontsize=13.5)
    for i, (color, name, _, values) in enumerate(estimators):
        bias2 = (values.mean() - true_sigma2) ** 2
        var = values.var()
        ax.bar(i, bias2, color=color, edgecolor=color, hatch="///", alpha=0.35)
        ax.bar(i, var, bottom=bias2, color=color, alpha=0.85, edgecolor="none")
        ax.text(
            i,
            bias2 + var + 0.012,
            f"{bias2 + var:.2f}",
            ha="center",
            va="bottom",
            color=color,
            fontsize=12,
        )
    ax.set_xticks(range(3))
    ax.set_xticklabels([name for _, name, _, _ in estimators], fontsize=11)
    ax.set_ylim(0, 0.42)
    ax.set_yticks([])
    despine(ax, keep=("bottom",))
    ax.text(
        0.5,
        0.99,
        "hatched: bias²      solid: variance",
        transform=ax.transAxes,
        fontsize=10.5,
        color=MUTED,
        ha="center",
        va="top",
    )


# ==========================================================================
# 4. supervised learning
# ==========================================================================
def _two_gaussians(
    rng,
    n=220,
    mu1=(-1.1, -0.5),
    mu2=(1.3, 0.7),
    cov1=((1.0, 0.35), (0.35, 0.7)),
    cov2=None,
):
    cov2 = cov1 if cov2 is None else cov2
    a = rng.multivariate_normal(mu1, cov1, n)
    b = rng.multivariate_normal(mu2, cov2, n)
    X = np.vstack([a, b])
    y = np.r_[np.zeros(n), np.ones(n)]
    return X, y


def _scatter_classes(ax, X, y, colors=(BLUE, RED), s=16):
    for k, color in enumerate(colors):
        ax.scatter(
            X[y == k, 0],
            X[y == k, 1],
            s=s,
            color=color,
            alpha=0.65,
            edgecolor="white",
            linewidth=0.4,
        )


@figure("supervised_principle")
def supervised_principle(fig):
    ax = canvas(fig)
    box(ax, 0.60, 2.10, 1.75, 0.85, BLUE, r"$X = (x_1,\dots,x_N)$", size=13)
    box(ax, 0.60, 0.85, 1.75, 0.85, GREEN, r"$Y = (y_1,\dots,y_N)$", size=13)
    box(ax, 3.55, 1.48, 1.9, 0.95, PURPLE, r"learn  $f$", size=16)
    box(ax, 6.65, 1.48, 1.75, 0.95, GOLD, r"$\hat{y} = f(x)$", size=15)
    arrow(ax, (2.45, 2.50), (3.45, 2.15))
    arrow(ax, (2.45, 1.25), (3.45, 1.70))
    arrow(ax, (5.55, 1.95), (6.55, 1.95))
    ax.text(2.95, 2.95, "inputs", ha="center", color=BLUE, fontsize=11.5)
    ax.text(2.95, 0.68, "labels", ha="center", color=GREEN, fontsize=11.5)
    ax.text(
        7.52, 1.20, "on new inputs", ha="center", va="top", color=MUTED, fontsize=11
    )
    note(ax, "the labels are known", y=0.35)


@figure("regression_vs_classification")
def regression_vs_classification(fig):
    axes = panels(
        fig,
        2,
        titles=["regression", "classification"],
        colors=[BLUE, RED],
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.22, wspace=0.20),
    )
    rng = np.random.default_rng(8)
    x = np.sort(rng.uniform(-2.5, 2.5, 90))
    y = 0.9 * x + 0.4 * np.sin(2 * x) + rng.normal(0, 0.35, x.size)
    ax = axes[0]
    ax.scatter(x, y, s=18, color=BLUE, alpha=0.65, edgecolor="white", linewidth=0.4)
    ax.plot(x, 0.9 * x + 0.4 * np.sin(2 * x), color=INK, lw=2.2)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y \in \mathbb{R}$")
    caption(ax, "predict a number")

    ax = axes[1]
    X, y2 = _two_gaussians(rng, 150)
    _scatter_classes(ax, X, y2)
    xx = np.linspace(-4, 4.5, 10)
    ax.plot(xx, -0.9 * xx + 0.45, color=INK, lw=2.2)
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$x_2$")
    ax.set_xlim(-4, 4.2)
    ax.set_ylim(-3.2, 3.4)
    caption(ax, r"predict a label:  $y \in \{0,1\}$  or  $y \in \{1,\dots,K\}$")


@figure("supervised_apps")
def supervised_apps(fig):
    ax = canvas(fig)
    rows = [
        (
            BLUE,
            "stock price",
            r"$x$: economic, social, political variables",
            r"$y$: a price",
            "regression",
        ),
        (
            GREEN,
            "weather",
            r"$x$: location, season, past measurements",
            r"$y$: a temperature",
            "regression",
        ),
        (
            PURPLE,
            "image classification",
            r"$x$: pixels or voxels",
            r"$y$: one of $K$ labels",
            "classification",
        ),
        (
            RED,
            "digit recognition",
            r"$x$: a $28\times 28$ image",
            r"$y \in \{0,\dots,9\}$",
            "classification",
        ),
    ]
    for i, (color, name, xin, yout, kind) in enumerate(rows):
        y = 3.15 - i * 0.78
        ax.text(
            0.45,
            y,
            name,
            ha="left",
            va="center",
            color=color,
            fontsize=13,
            weight="bold",
        )
        ax.text(3.05, y, xin, ha="left", va="center", color=INK, fontsize=12)
        ax.text(6.25, y, yout, ha="left", va="center", color=INK, fontsize=12)
        ax.text(
            8.55,
            y,
            kind,
            ha="right",
            va="center",
            color=color,
            fontsize=12,
            weight="bold",
        )
        if i:
            ax.plot([0.45, 8.55], [y + 0.39, y + 0.39], color=GRID, lw=0.9)
    # note(ax, "R = regression    C = classification", y=0.25, size=11)


@figure("discriminative_vs_generative")
def discriminative_vs_generative(fig):
    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.24, wspace=0.20),
    )
    rng = np.random.default_rng(9)
    X, y = _two_gaussians(rng, 160)
    ax = axes[0]
    _scatter_classes(ax, X, y)
    xx = np.linspace(-4, 4.5, 10)
    ax.plot(xx, -0.9 * xx + 0.45, color=INK, lw=2.6)
    ax.set_title("discriminative", color=BLUE, pad=10, fontsize=15)
    caption(
        ax,
        "model $p(y|x)$ — best on large datasets",
    )

    ax = axes[1]
    _scatter_classes(ax, X, y)
    for k, color, mu in [(0, BLUE, (-1.1, -0.5)), (1, RED, (1.3, 0.7))]:
        cov = np.array([[1.0, 0.35], [0.35, 0.7]])
        vals, vecs = np.linalg.eigh(cov)
        angle = np.degrees(np.arctan2(*vecs[:, 1][::-1]))
        for scale in (1.0, 2.0):
            ax.add_patch(
                Ellipse(
                    mu,
                    *(2 * scale * np.sqrt(vals)),
                    angle=angle,
                    facecolor="none",
                    edgecolor=color,
                    lw=2,
                    alpha=0.9 - 0.3 * scale,
                )
            )
    ax.set_title("generative", color=RED, pad=10, fontsize=15)
    caption(
        ax,
        "model $p(x|y)$ and $p(y)$ — best on small datasets",
    )
    for ax in axes:
        ax.set_xlim(-4, 4.2)
        ax.set_ylim(-3.2, 3.4)
        ax.set_xticks([])
        ax.set_yticks([])


@figure("eq_bayes_classifier")
def eq_bayes_classifier(fig):
    ax = canvas(fig)
    equation(
        ax,
        r"$\hat{C}(x) \;=\; \arg\max_k\ P(C = k \,|\, X = x)"
        r"\;=\; \arg\max_k\ \frac{f_k(x)\,\pi_k}"
        r"{\sum_{i=1}^{K} f_i(x)\,\pi_i}"
        r"\;=\; \arg\max_k\ f_k(x)\,\pi_k$",
        y=2.45,
        size=20,
    )
    ax.text(
        2.55,
        1.55,
        r"$\pi_k$ : the prior of class $k$",
        ha="center",
        va="center",
        color=BLUE,
        fontsize=14,
    )
    ax.text(
        6.45,
        1.55,
        r"$f_k(x)$ : the density inside class $k$",
        ha="center",
        va="center",
        color=RED,
        fontsize=14,
    )
    note(
        ax,
        "the denominator does not depend on k",
        y=0.80,
    )


@figure("bayes_ingredients")
def bayes_ingredients(fig):
    axes = panels(
        fig,
        3,
        titles=[r"priors  $\pi_k$", r"densities  $f_k(x)$", r"posterior  $P(C=k|x)$"],
        colors=[BLUE, RED, PURPLE],
        gridspec_kw=dict(left=0.05, right=0.98, top=0.84, bottom=0.22, wspace=0.26),
    )
    grid = np.linspace(-5, 6, 500)
    pi = np.array([0.65, 0.35])
    dens = np.vstack(
        [
            np.exp(-0.5 * ((grid + 1.2) / 1.1) ** 2) / (1.1 * np.sqrt(2 * np.pi)),
            np.exp(-0.5 * ((grid - 2.0) / 1.4) ** 2) / (1.4 * np.sqrt(2 * np.pi)),
        ]
    )
    ax = axes[0]
    ax.bar([0, 1], pi, color=[BLUE, RED], width=0.55)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["class 1", "class 2"])
    ax.set_ylim(0, 0.85)
    ax.set_yticks([0, 0.25, 0.5])
    despine(ax, keep=("bottom", "left"))
    caption(ax, r"$\hat\pi_k = N_k / N$")

    ax = axes[1]
    for k, color in enumerate((BLUE, RED)):
        ax.plot(grid, dens[k], color=color, lw=2.4)
    ax.set_yticks([])
    ax.set_xlabel(r"$x$")
    despine(ax, keep=("bottom",))
    caption(ax, "Gaussian, mixture, non-parametric, ...")

    ax = axes[2]
    joint = dens * pi[:, None]
    post = joint / joint.sum(0)
    for k, color in enumerate((BLUE, RED)):
        ax.plot(grid, post[k], color=color, lw=2.4)
    cut = grid[np.argmin(np.abs(post[0] - post[1]))]
    ax.axvline(cut, color=INK, ls="--", lw=1.8)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel(r"$x$")
    despine(ax, keep=("bottom", "left"))


@figure("eq_naive_bayes")
def eq_naive_bayes(fig):
    ax = canvas(fig)
    equation(
        ax, r"$f_k(x) \;=\; \prod_{j=1}^{d} f_k(x_j)$", y=2.60, size=30, color=GREEN
    )
    ax.text(
        W / 2,
        1.70,
        "the features are assumed independent inside a class",
        ha="center",
        va="center",
        color=INK,
        fontsize=15,
    )
    ax.text(
        2.35,
        0.95,
        "d univariate densities\ninstead of one in d dimensions",
        ha="center",
        va="center",
        color=GREEN,
        fontsize=12,
        linespacing=1.6,
    )
    ax.text(
        6.55,
        0.95,
        "the assumption is almost always false\n"
        "...but the classifier often works anyway",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=12,
        linespacing=1.6,
    )


@figure("spam_filter")
def spam_filter(fig):
    ax = canvas(fig)
    words = ["free", "meeting", "click", "report", "winner"]
    spam = [0.031, 0.002, 0.024, 0.003, 0.018]
    ham = [0.004, 0.019, 0.002, 0.022, 0.001]
    ax.text(0.55, 3.35, "bag of words", color=BLUE, fontsize=14, weight="bold")
    ax.text(
        0.55,
        2.95,
        r"$x_j$ = how often word $j$ occurs",
        color=INK,
        fontsize=12,
        va="center",
    )
    ax.text(
        0.55, 2.55, r"$d$ = size of the dictionary", color=INK, fontsize=12, va="center"
    )
    ax.text(
        0.55,
        1.90,
        r"$f_k(x_j)$ : frequency of word $j$ in class $k$",
        color=RED,
        fontsize=12,
        va="center",
    )
    ax.text(
        0.55,
        1.50,
        r"$\pi_k$ : share of spam in the mailbox",
        color=RED,
        fontsize=12,
        va="center",
    )
    ax.text(
        0.55,
        0.85,
        "→ basically counting words",
        color=GREEN,
        fontsize=13.5,
        va="center",
        weight="bold",
    )
    x0, col = 4.85, 1.25
    ax.text(x0, 3.30, "word", color=MUTED, fontsize=12)
    ax.text(x0 + col * 1.4, 3.30, "spam", color=RED, fontsize=12, ha="center")
    ax.text(x0 + col * 2.4, 3.30, "normal", color=BLUE, fontsize=12, ha="center")
    ax.plot([x0, x0 + col * 2.9], [3.10, 3.10], color=GRID, lw=1.2)
    for i, (word, s, h) in enumerate(zip(words, spam, ham)):
        y = 2.80 - i * 0.42
        ax.text(x0, y, word, color=INK, fontsize=12)
        ax.text(x0 + col * 1.4, y, f"{s:.3f}", color=RED, fontsize=12, ha="center")
        ax.text(x0 + col * 2.4, y, f"{h:.3f}", color=BLUE, fontsize=12, ha="center")
    ax.text(
        x0,
        0.45,
        r"$\hat{C}(x) = \arg\max_k\ \pi_k \prod_j f_k(x_j)$",
        color=INK,
        fontsize=14,
    )


@figure("laplace_smoothing")
def laplace_smoothing(fig):
    ax = canvas(fig)
    ax.text(
        W / 2,
        3.25,
        r"what if a word never appeared in a class?",
        ha="center",
        va="center",
        color=INK,
        fontsize=15,
    )
    ax.text(
        W / 2,
        2.55,
        r"$\exists j \text{ s.t. } f_k(x_j) = 0 \;\Longrightarrow\; "
        r"\prod_j f_k(x_j) = 0$",
        ha="center",
        va="center",
        color=RED,
        fontsize=22,
    )
    ax.text(
        W / 2,
        1.95,
        "one unseen word vetoes the whole class",
        ha="center",
        va="center",
        color=RED,
        fontsize=12.5,
    )
    ax.text(
        W / 2,
        1.20,
        r"$\hat{f}_k(x_j) = \frac{n_{kj} + \alpha}"
        r"{n_k + \alpha\, d}$",
        ha="center",
        va="center",
        color=GREEN,
        fontsize=24,
    )
    ax.text(
        W / 2,
        0.40,
        "Laplace smoothing: give every word a small head start",
        ha="center",
        va="center",
        color=GREEN,
        fontsize=12.5,
    )


@figure("naive_bayes_gaussian")
def naive_bayes_gaussian(fig):
    from scipy.stats import norm

    rng = np.random.default_rng(14)
    X, y = _two_gaussians(rng, 180, cov1=((0.8, 0.0), (0.0, 0.6)))
    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.05, right=0.98, top=0.84, bottom=0.26, wspace=0.24),
    )
    titles = [
        "1.  choose a density",
        "2.  estimate it per class",
        "3.  classify by MAP",
    ]
    for ax, title in zip(axes, titles):
        ax.set_title(title, pad=10, fontsize=13)

    ax = axes[0]
    _scatter_classes(ax, X, y)
    caption(ax, "Gaussian, one per feature")

    ax = axes[1]
    grid = np.linspace(-4, 4.5, 300)
    for k, color in enumerate((BLUE, RED)):
        m, s = X[y == k, 0].mean(), X[y == k, 0].std()
        ax.plot(grid, norm.pdf(grid, m, s), color=color, lw=2.4)
        ax.plot(
            X[y == k, 0],
            np.full((y == k).sum(), -0.02),
            "|",
            color=color,
            ms=8,
            alpha=0.5,
        )
    ax.set_yticks([])
    ax.set_xlabel(r"$x_1$")
    despine(ax, keep=("bottom",))
    caption(ax, "maximum likelihood, feature by feature")

    ax = axes[2]
    gx, gy = np.meshgrid(np.linspace(-4, 4.5, 260), np.linspace(-3.2, 3.4, 260))
    score = np.zeros_like(gx)
    for k, sign in ((0, -1), (1, 1)):
        Xi = X[y == k]
        logp = np.zeros_like(gx)
        for j, g in enumerate((gx, gy)):
            logp += norm.logpdf(g, Xi[:, j].mean(), Xi[:, j].std())
        score += sign * (logp + np.log((y == k).mean()))
    ax.contourf(
        gx, gy, score > 0, levels=[-0.5, 0.5, 1.5], colors=["#e9f0f8", "#fbecec"]
    )
    ax.contour(gx, gy, score, levels=[0], colors=[INK], linewidths=2)
    _scatter_classes(ax, X, y)
    ax.set_xticks([])
    ax.set_yticks([])
    caption(ax, r"$\arg\max_k\ \pi_k \prod_j f_k(x_j)$")
    for ax in (axes[0], axes[2]):
        ax.set_xlim(-4, 4.5)
        ax.set_ylim(-3.2, 3.4)
        ax.set_xticks([])
        ax.set_yticks([])


@figure("lda_setup")
def lda_setup(fig):
    ax = canvas(fig)
    ax.text(
        W / 2,
        3.25,
        "continuous features, Gaussian classes",
        ha="center",
        va="center",
        color=INK,
        fontsize=15,
    )
    equation(
        ax,
        r"$f_k(x) = \frac{1}{(2\pi)^{d/2}|\Sigma_k|^{1/2}}\ "
        r"\exp\left(-\frac{1}{2}(x-\mu_k)^{T}\Sigma_k^{-1}"
        r"(x-\mu_k)\right)$",
        y=2.35,
        size=21,
    )
    ax.text(
        W / 2,
        1.30,
        r"LDA assumes one shared covariance:  "
        r"$\Sigma_k = \Sigma \quad \forall k$",
        ha="center",
        va="center",
        color=GREEN,
        fontsize=17,
    )
    note(ax, "same shape for every class, only the centres move", y=0.55)


def _ellipse(ax, mu, cov, color, scales=(1.0, 2.0), lw=2.0, ls="-"):
    vals, vecs = np.linalg.eigh(cov)
    angle = np.degrees(np.arctan2(*vecs[:, 1][::-1]))
    for scale in scales:
        ax.add_patch(
            Ellipse(
                mu,
                *(2 * scale * np.sqrt(vals)),
                angle=angle,
                facecolor="none",
                edgecolor=color,
                lw=lw,
                ls=ls,
                alpha=1.0 - 0.35 * (scale - 1),
            )
        )


def _gaussian_scores(gx, gy, means, covs, priors):
    """delta_k(x) for each class, on a grid — the log of f_k(x) pi_k."""
    points = np.c_[gx.ravel(), gy.ravel()]
    out = []
    for mu, cov, prior in zip(means, covs, priors):
        diff = points - np.asarray(mu)
        inv = np.linalg.inv(cov)
        quad = np.einsum("ij,jk,ik->i", diff, inv, diff)
        out.append(
            (-0.5 * np.log(np.linalg.det(cov)) - 0.5 * quad + np.log(prior)).reshape(
                gx.shape
            )
        )
    return out


@figure("lda_fit_steps")
def lda_fit_steps(fig):
    rng = np.random.default_rng(41)
    X, y = _two_gaussians(rng, 160)
    pooled = np.cov(np.vstack([X[y == k] - X[y == k].mean(0) for k in (0, 1)]).T)
    means = [X[y == k].mean(0) for k in (0, 1)]
    priors = [(y == k).mean() for k in (0, 1)]

    axes = panels(
        fig,
        3,
        titles=[
            "1.  the labelled data",
            r"2.  one Gaussian per class, one shared $\Sigma$",
            "3.  the MAP rule",
        ],
        colors=[INK, INK, INK],
        gridspec_kw=dict(left=0.03, right=0.98, top=0.84, bottom=0.22, wspace=0.12),
    )
    gx, gy = np.meshgrid(np.linspace(-4.2, 4.6, 300), np.linspace(-3.4, 3.6, 300))
    d0, d1 = _gaussian_scores(gx, gy, means, [pooled, pooled], priors)

    _scatter_classes(axes[0], X, y)

    _scatter_classes(axes[1], X, y, s=10)
    for k, color in enumerate((BLUE, RED)):
        _ellipse(axes[1], means[k], pooled, color)
        axes[1].plot(*means[k], "X", color=color, ms=12, mec="white", mew=1.4)
    axes[1].text(
        0.03,
        0.97,
        r"$\hat\pi_1 = %.2f$" % priors[0] + "\n" + r"$\hat\pi_2 = %.2f$" % priors[1],
        transform=axes[1].transAxes,
        fontsize=11,
        va="top",
        color=MUTED,
        linespacing=1.6,
    )
    caption(axes[1], "same shape per class, only the centres differ")

    axes[2].contourf(gx, gy, d1 - d0, levels=[-99, 0, 99], colors=["#e9f0f8", "#fbecec"])
    axes[2].contour(gx, gy, d1 - d0, levels=[0], colors=[INK], linewidths=2.4)
    _scatter_classes(axes[2], X, y, s=10)
    caption(axes[2], r"predict $k$ with largest $f_k(x)\,\pi_k$")

    for ax in axes:
        ax.set_xlim(-4.2, 4.6)
        ax.set_ylim(-3.4, 3.6)
        ax.set_xticks([])
        ax.set_yticks([])


@figure("lda_why_linear")
def lda_why_linear(fig):
    rng = np.random.default_rng(43)
    cov = np.array([[1.0, 0.35], [0.35, 0.7]])
    mu0, mu1 = np.array([-1.1, -0.5]), np.array([1.3, 0.7])
    X, y = _two_gaussians(rng, 200, mu1=mu0, mu2=mu1, cov1=cov)

    axes = fig.subplots(
        1,
        2,
        gridspec_kw={"left": 0.04, "right": 0.97, "top": 0.84, "bottom": 0.24, "wspace": 0.20},
    )

    ax = axes[0]
    gx, gy = np.meshgrid(np.linspace(-4.2, 4.6, 300), np.linspace(-3.4, 3.6, 300))
    d0, d1 = _gaussian_scores(gx, gy, [mu0, mu1], [cov, cov], [0.5, 0.5])
    ax.contour(gx, gy, d1 - d0, levels=[0], colors=[INK], linewidths=2.6)
    _scatter_classes(ax, X, y, s=10)
    for mu, color in ((mu0, BLUE), (mu1, RED)):
        _ellipse(ax, mu, cov, color)
        ax.plot(*mu, "X", color=color, ms=12, mec="white", mew=1.4)
    w = np.linalg.solve(cov, mu1 - mu0)
    centre = (mu0 + mu1) / 2
    ax.annotate(
        "",
        xy=centre + 0.55 * w,
        xytext=centre,
        arrowprops={"arrowstyle": "-|>", "color": GREEN, "lw": 2.4},
    )
    ax.text(
        0.02,
        0.96,
        r"arrow:\\n$w = \Sigma^{-1}(\mu_1 - \mu_2)$",
        transform=ax.transAxes,
        color=GREEN,
        fontsize=12,
        ha="left",
        va="top",
    )
    ax.set_xlim(-4.2, 4.6)
    ax.set_ylim(-3.4, 3.6)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("same shape for both classes", pad=10, fontsize=13.5)

    ax = axes[1]
    z = X @ w
    grid = np.linspace(z.min() - 1, z.max() + 1, 400)
    within = np.concatenate([z[y == k] - z[y == k].mean() for k in (0, 1)]).std()
    for k, color in enumerate((BLUE, RED)):
        zk = z[y == k]
        ax.hist(zk, bins=26, density=True, color=color, alpha=0.30, edgecolor="none")
        sd = within
        ax.plot(
            grid,
            np.exp(-0.5 * ((grid - zk.mean()) / sd) ** 2) / (sd * np.sqrt(2 * np.pi)),
            color=color,
            lw=2.4,
        )
    threshold = 0.5 * (z[y == 0].mean() + z[y == 1].mean())
    ax.axvline(threshold, color=INK, lw=2.4)
    ax.set_yticks([])
    ax.set_xlabel(r"projection  $w^{T}x$")
    despine(ax, keep=("bottom",))

@figure("qda_shapes")
def qda_shapes(fig):
    configs = [
        (
            "equal Σ  →  line (equiv. LDA)",
            [-1.3, -0.4],
            [1.4, 0.5],
            [[1.0, 0.3], [0.3, 0.8]],
            [[1.0, 0.3], [0.3, 0.8]],
        ),
        (
            "different spread  →  circle",
            [0.0, 0.0],
            [0.0, 0.0],
            [[0.25, 0.0], [0.0, 0.25]],
            [[3.0, 0.0], [0.0, 3.0]],
        ),
        (
            "different orientation  →  hyperbola",
            [-0.3, 0.0],
            [0.3, 0.0],
            [[2.2, 0.0], [0.0, 0.32]],
            [[0.32, 0.0], [0.0, 2.2]],
        ),
    ]
    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.82, bottom=0.20, wspace=0.12),
    )
    gx, gy = np.meshgrid(np.linspace(-4.5, 4.5, 400), np.linspace(-3.6, 3.6, 400))
    for ax, (title, mu0, mu1, cov0, cov1) in zip(axes, configs):
        d0, d1 = _gaussian_scores(
            gx, gy, [mu0, mu1], [np.array(cov0), np.array(cov1)], [0.5, 0.5]
        )
        ax.contourf(
            gx, gy, d1 - d0, levels=[-999, 0, 999], colors=["#e9f0f8", "#fbecec"]
        )
        ax.contour(gx, gy, d1 - d0, levels=[0], colors=[INK], linewidths=2.4)
        for mu, cov, color in ((mu0, cov0, BLUE), (mu1, cov1, RED)):
            _ellipse(ax, mu, np.array(cov), color, scales=(1.0, 2.0), lw=1.8)
        if np.allclose(mu0, mu1):
            ax.plot(*mu0, "X", color=INK, ms=11, mec="white", mew=1.2)
            ax.text(0.0, -1.85, "same centre", color=INK, fontsize=11,
                    ha="center", va="top")
        else:
            for mu, color in ((mu0, BLUE), (mu1, RED)):
                ax.plot(*mu, "X", color=color, ms=11, mec="white", mew=1.2)
        ax.set_xlim(-4.5, 4.5)
        ax.set_ylim(-3.6, 3.6)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title, pad=10, fontsize=13)
    fig.text(
        0.5,
        0.045,
        "the quadratic term does not cancel, so the the boundary is a conic",
        ha="center",
        color=MUTED,
        fontsize=12.5,
    )


@figure("lda_qda_cost")
def lda_qda_cost(fig):
    from sklearn.discriminant_analysis import (
        LinearDiscriminantAnalysis,
        QuadraticDiscriminantAnalysis,
    )

    axes = fig.subplots(
        1,
        2,
        gridspec_kw={"left": 0.08, "right": 0.97, "top": 0.84, "bottom": 0.22, "wspace": 0.28},
    )

    ax = axes[0]
    d = np.arange(2, 31)
    K = 3
    lda = K * d + d * (d + 1) / 2
    qda = K * (d + d * (d + 1) / 2)
    ax.plot(d, lda, color=GREEN, lw=2.6)
    ax.plot(d, qda, color=PURPLE, lw=2.6)
    ax.text(30, lda[-1], "  LDA", color=GREEN, fontsize=12, va="center")
    ax.text(23, qda[-1] * 0.98, "QDA", color=PURPLE, fontsize=12, va="top")
    ax.set_xlabel("number of features d")
    ax.set_ylabel("parameters to estimate")
    ax.set_xlim(2, 33)
    ax.set_title(r"$K = 3$ classes", pad=10, fontsize=13.5)

    ax = axes[1]
    rng = np.random.default_rng(57)
    dim, reps = 10, 30
    A = rng.normal(size=(dim, dim))
    cov0 = A @ A.T / dim + np.eye(dim) * 0.5
    B = rng.normal(size=(dim, dim))
    cov1 = B @ B.T / dim + np.eye(dim) * 0.5
    mu0 = np.zeros(dim)
    mu1 = np.full(dim, 0.8)
    sizes = [40, 80, 160, 320, 800, 2000]

    def draw(n):
        half = n // 2
        X = np.vstack(
            [
                rng.multivariate_normal(mu0, cov0, half),
                rng.multivariate_normal(mu1, cov1, n - half),
            ]
        )
        return X, np.r_[np.zeros(half), np.ones(n - half)]

    Xte, yte = draw(4000)
    curves = {"LDA": [], "QDA": []}
    for n in sizes:
        scores = {"LDA": [], "QDA": []}
        for _ in range(reps):
            Xtr, ytr = draw(n)
            for name, model in (
                ("LDA", LinearDiscriminantAnalysis()),
                ("QDA", QuadraticDiscriminantAnalysis(reg_param=1e-3)),
            ):
                model.fit(Xtr, ytr)
                scores[name].append(model.score(Xte, yte))
        for name in curves:
            curves[name].append(np.mean(scores[name]))
    for name, color in (("LDA", GREEN), ("QDA", PURPLE)):
        ax.plot(sizes, curves[name], "o-", color=color, lw=2.4, ms=6)
        ax.text(sizes[-1] * 1.05, curves[name][-1], name, color=color, fontsize=12,
                va="center")
    ax.set_xscale("log")
    ax.set_xlabel("training samples n")
    ax.set_ylabel("test accuracy")
    ax.set_xlim(32, 3600)
    ax.set_title(r"$d = 10$", pad=10, fontsize=13.5)
    caption(ax, "on sample quadratic data")


@figure("lda_derivation")
def lda_derivation(fig):
    ax = canvas(fig)
    lines = [
        (r"$\hat{C}(x) = \arg\max_k\ P(C=k|X=x)$", INK),
        (
            r"$= \arg\max_k\ f_k(x)\,\pi_k = \arg\max_k\ \log\left[f_k(x)\,\pi_k\right]$",
            INK,
        ),
        (
            r"$= \arg\max_k\ -\frac{1}{2}(x-\mu_k)^{T}\Sigma^{-1}(x-\mu_k) + \log \pi_k$",
            INK,
        ),
        (
            r"$= \arg\max_k\ x^{T}\Sigma^{-1}\mu_k - \frac{1}{2}\mu_k^{T}"
            r"\Sigma^{-1}\mu_k + \log \pi_k$",
            GREEN,
        ),
    ]
    for i, (text, color) in enumerate(lines):
        ax.text(
            1.05,
            3.15 - i * 0.78,
            text,
            ha="left",
            va="center",
            color=color,
            fontsize=16.5,
        )
    ax.text(
        1.05,
        0.30,
        r"$-\frac{1}{2}x^{T}\Sigma^{-1}x$"
        " can be dropped, since it is the same for every class",
        ha="left",
        va="center",
        color=MUTED,
        fontsize=12,
    )


@figure("lda_boundary")
def lda_boundary(fig):
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

    rng = np.random.default_rng(15)
    X, y = _two_gaussians(rng, 200)
    model = LinearDiscriminantAnalysis(store_covariance=True).fit(X, y)
    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.24, wspace=0.20),
    )
    ax = axes[0]
    ax.text(
        0.5,
        0.78,
        r"$\delta_k(x) = x^{T}\Sigma^{-1}\mu_k"
        r" - \frac{1}{2}\mu_k^{T}\Sigma^{-1}\mu_k + \log \pi_k$",
        ha="center",
        va="center",
        fontsize=16,
        color=GREEN,
        transform=ax.transAxes,
    )
    ax.text(
        0.5,
        0.48,
        "is linear in x",
        ha="center",
        va="center",
        fontsize=13,
        color=INK,
        transform=ax.transAxes,
    )
    ax.axis("off")
    ax.set_title("the discriminant function", color=INK, pad=10, fontsize=14)

    ax = axes[1]
    gx, gy = np.meshgrid(np.linspace(-4.2, 4.6, 300), np.linspace(-3.4, 3.6, 300))
    zz = model.predict_proba(np.c_[gx.ravel(), gy.ravel()])[:, 1].reshape(gx.shape)
    ax.contourf(gx, gy, zz, levels=[0, 0.5, 1], colors=["#e9f0f8", "#fbecec"])
    ax.contour(gx, gy, zz, levels=[0.5], colors=[INK], linewidths=2.4)
    _scatter_classes(ax, X, y)
    ax.set_xticks([])
    ax.set_yticks([])


@figure("lda_training")
def lda_training(fig):
    ax = canvas(fig)
    rows = [
        (BLUE, "priors", r"$\hat\pi_k = N_k / N$"),
        (
            GREEN,
            "class means",
            (r"$\hat\mu_k = \frac{1}{N_k}"
            r"\sum_{x_i \in C_k} x_i$"),
        ),
        (
            PURPLE,
            "pooled covariance",
            (r"$\hat\Sigma = \frac{1}{N-K}"
            r"\sum_{k=1}^{K}\sum_{x_i \in C_k}"
            r"(x_i - \hat\mu_k)(x_i - \hat\mu_k)^{T}$"),
        ),
    ]
    for i, (color, name, formula) in enumerate(rows):
        y = 2.70 - i * 0.82
        ax.text(
            2.55,
            y,
            name,
            ha="right",
            va="center",
            color=color,
            fontsize=13,
            weight="bold",
        )
        ax.text(2.85, y, formula, ha="left", va="center", color=INK, fontsize=17)
    note(ax, r"estimates are poor when $N < d$", y=0.25, color=RED)


@figure("qda_vs_lda")
def qda_vs_lda(fig):
    from sklearn.discriminant_analysis import (
        LinearDiscriminantAnalysis,
        QuadraticDiscriminantAnalysis,
    )

    rng = np.random.default_rng(17)
    X, y = _two_gaussians(
        rng,
        240,
        mu1=(-1.0, -0.3),
        mu2=(1.4, 0.6),
        cov1=((1.4, 0.75), (0.75, 0.7)),
        cov2=((0.45, -0.25), (-0.25, 1.5)),
    )
    axes = panels(
        fig,
        2,
        titles=["LDA: one shared Σ", "QDA: one Σ per class"],
        colors=[GREEN, PURPLE],
        gridspec_kw={"left": 0.06, "right": 0.97, "top": 0.84, "bottom": 0.26, "wspace": 0.16},
    )
    gx, gy = np.meshgrid(np.linspace(-4.5, 4.8, 320), np.linspace(-3.6, 4.0, 320))
    grid = np.c_[gx.ravel(), gy.ravel()]
    for ax, model in zip(
        axes, (LinearDiscriminantAnalysis(), QuadraticDiscriminantAnalysis())
    ):
        model.fit(X, y)
        zz = model.predict_proba(grid)[:, 1].reshape(gx.shape)
        ax.contourf(gx, gy, zz, levels=[0, 0.5, 1], colors=["#e9f0f8", "#fbecec"])
        ax.contour(gx, gy, zz, levels=[0.5], colors=[INK], linewidths=2.4)
        _scatter_classes(ax, X, y)
        ax.set_xticks([])
        ax.set_yticks([])
        acc = (model.predict(X) == y).mean()
        ax.annotate(
            f"training accuracy {acc:.0%}",
            xy=(0.5, -0.12),
            xycoords="axes fraction",
            ha="center",
            va="top",
            color=MUTED,
            fontsize=11,
        )
    fig.text(
        0.5,
        0.03,
        "QDA has K times more covariance parameters to estimate",
        ha="center",
        color=MUTED,
        fontsize=12,
    )


# ==========================================================================
# 5. unsupervised learning
# ==========================================================================
@figure("unsupervised_principle")
def unsupervised_principle(fig):
    ax = canvas(fig)
    box(ax, 0.60, 1.48, 1.75, 0.95, BLUE, r"$X = (x_1,\dots,x_N)$", size=13)
    box(ax, 3.55, 1.48, 1.9, 0.95, PURPLE, "find structure", size=15)
    box(ax, 6.65, 2.05, 1.75, 0.72, GOLD, "groups", size=13)
    box(ax, 6.65, 0.95, 1.75, 0.72, GOLD, "coordinates", size=13)
    arrow(ax, (2.45, 1.95), (3.45, 1.95))
    arrow(ax, (5.55, 2.05), (6.55, 2.35))
    arrow(ax, (5.55, 1.85), (6.55, 1.45))
    ax.text(1.48, 1.20, "no labels", ha="center", va="top", color=MUTED, fontsize=11.5)
    note(ax, "the labels are unknown", y=0.42)


@figure("dimred_vs_clustering")
def dimred_vs_clustering(fig):
    axes = panels(
        fig,
        2,
        titles=["dimension reduction", "clustering"],
        colors=[BLUE, GOLD],
        gridspec_kw={"left": 0.06, "right": 0.97, "top": 0.84, "bottom": 0.24, "wspace": 0.20},
    )
    rng = np.random.default_rng(21)
    ax = axes[0]
    ax.add_patch(
        Rectangle(
            (0.1, 0.25),
            0.28,
            0.6,
            facecolor="#e9f0f8",
            edgecolor=BLUE,
            lw=2,
            transform=ax.transAxes,
        )
    )
    ax.text(
        0.24,
        0.90,
        r"$X \in \mathbb{R}^{N \times d}$",
        ha="center",
        color=BLUE,
        fontsize=14,
        transform=ax.transAxes,
    )
    ax.add_patch(
        Rectangle(
            (0.66, 0.25),
            0.12,
            0.6,
            facecolor="#e9f0f8",
            edgecolor=BLUE,
            lw=2,
            transform=ax.transAxes,
        )
    )
    ax.text(
        0.72,
        0.90,
        r"$Z \in \mathbb{R}^{N \times q}$",
        ha="center",
        color=BLUE,
        fontsize=14,
        transform=ax.transAxes,
    )
    ax.annotate(
        "",
        xy=(0.62, 0.55),
        xytext=(0.44, 0.55),
        xycoords="axes fraction",
        arrowprops={"arrowstyle": "-|>", "color": GREEN, "lw": 2.4},
    )
    ax.text(
        0.53,
        0.62,
        r"$q < d$",
        ha="center",
        color=GREEN,
        fontsize=13,
        transform=ax.transAxes,
    )
    ax.axis("off")
    caption(ax, "Used to: visualise, denoise, compute faster")

    ax = axes[1]
    centres = np.array([[-1.4, -0.9], [1.5, -0.6], [0.2, 1.5]])
    pts = np.vstack([rng.normal(c, 0.45, (40, 2)) for c in centres])
    labels = np.repeat([0, 1, 2], 40)
    for k, color in enumerate((BLUE, RED, GREEN)):
        ax.scatter(
            pts[labels == k, 0],
            pts[labels == k, 1],
            s=20,
            color=color,
            alpha=0.7,
            edgecolor="white",
            linewidth=0.4,
        )
        ax.scatter(
            *centres[k],
            marker="X",
            s=110,
            color=color,
            edgecolor="white",
            linewidth=1.2,
            zorder=4,
        )
        ax.text(
            centres[k][0],
            centres[k][1] + 0.42,
            f"$C_{k + 1}$",
            color=color,
            fontsize=13,
            ha="center",
        )
    ax.set_xticks([])
    ax.set_yticks([])
    despine(ax)
    caption(ax, "Used to: visualize, regroup, analyse")


@figure("unsupervised_apps")
def unsupervised_apps(fig):
    ax = canvas(fig)
    rows = [
        (BLUE, "detect costumer classes", r"$x$: purchase history", r"$C_k$: costumer types"),
        (
            GREEN,
            "image segmentation",
            r"$x$: patch of pixels or voxels",
            r"$C_k$: blood, muscle, tumour",
        ),
        (PURPLE, "text mining", r"$x$: e-mails, documents", r"$C_k$: themes"),
        (
            GOLD,
            "data visualisation",
            r"$x$: $d$-dimensional data",
            r"$z \in \mathbb{R}^2$ to plot",
        ),
    ]
    for i, (color, name, xin, out) in enumerate(rows):
        y = 3.15 - i * 0.78
        ax.text(
            0.45,
            y,
            name,
            ha="left",
            va="center",
            color=color,
            fontsize=13,
            weight="bold",
        )
        ax.text(3.55, y, xin, ha="left", va="center", color=INK, fontsize=12)
        ax.text(6.10, y, out, ha="left", va="center", color=INK, fontsize=12)
        if i:
            ax.plot([0.45, 8.65], [y + 0.39, y + 0.39], color=GRID, lw=0.9)


@figure("eq_kmeans")
def eq_kmeans(fig):
    ax = canvas(fig)
    equation(
        ax,
        r"$J_w \;=\; \sum_{k=1}^{K} \sum_{x_i \in C_k}"
        r"\ \|x_i - \mu_k\|^2$",
        y=2.55,
        size=28,
        color=GOLD,
    )
    ax.text(
        W / 2,
        1.60,
        "find the K centres that make the within-cluster distance as small as possible",
        ha="center",
        va="center",
        color=INK,
        fontsize=14,
    )
    ax.text(
        2.55,
        0.85,
        "the exact problem is NP-hard",
        ha="center",
        va="center",
        color=RED,
        fontsize=12.5,
    )
    ax.text(
        6.45,
        0.85,
        r"k-means finds a local minimum in $O(tKN)$",
        ha="center",
        va="center",
        color=GREEN,
        fontsize=12.5,
    )


@figure("kmeans_algorithm")
def kmeans_algorithm(fig):
    rng = np.random.default_rng(23)
    centres = np.array([[-1.6, -1.0], [1.7, -0.7], [0.1, 1.7]])
    X = np.vstack([rng.normal(c, 0.55, (70, 2)) for c in centres])
    mu = np.array([[-2.4, 1.6], [-1.9, 1.2], [-2.1, 0.7]])  # a bad start, on purpose
    axes = fig.subplots(
        1,
        4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.82, bottom=0.16, wspace=0.10),
    )
    titles = ["1.  initialise", "2.  assign", "3.  re-estimate", "4.  repeat"]
    colors = [BLUE, RED, GREEN]
    for step, (ax, title) in enumerate(zip(axes, titles)):
        if step:
            d = ((X[:, None, :] - mu[None]) ** 2).sum(-1)
            s = d.argmin(1)
        else:
            s = None
        if step >= 2:
            mu = np.array(
                [X[s == k].mean(0) if (s == k).any() else mu[k] for k in range(3)]
            )
            d = ((X[:, None, :] - mu[None]) ** 2).sum(-1)
            s = d.argmin(1)
        if step == 3:
            for _ in range(6):
                mu = np.array([X[s == k].mean(0) for k in range(3)])
                s = ((X[:, None, :] - mu[None]) ** 2).sum(-1).argmin(1)
        if s is None:
            ax.scatter(
                X[:, 0],
                X[:, 1],
                s=16,
                color=MUTED,
                alpha=0.6,
                edgecolor="white",
                linewidth=0.3,
            )
        else:
            for k, color in enumerate(colors):
                ax.scatter(
                    X[s == k, 0],
                    X[s == k, 1],
                    s=16,
                    color=color,
                    alpha=0.6,
                    edgecolor="white",
                    linewidth=0.3,
                )
        for k, color in enumerate(colors):
            ax.scatter(
                *mu[k],
                marker="X",
                s=130,
                color=color,
                edgecolor="white",
                linewidth=1.4,
                zorder=5,
            )
        ax.set_title(title, pad=8, fontsize=13)
        ax.set_xlim(-3.4, 3.4)
        ax.set_ylim(-2.8, 3.2)
        ax.set_aspect("equal")
        blank(ax)
    fig.text(
        0.5,
        0.045,
        r"assign to the nearest centre, move each centre to the "
        r"mean of its points, repeat",
        ha="center",
        color=MUTED,
        fontsize=12,
    )


@figure("kmeans_weaknesses")
def kmeans_weaknesses(fig):
    from sklearn.cluster import KMeans
    from sklearn.datasets import make_moons

    rng = np.random.default_rng(31)
    axes = fig.subplots(
        1,
        3,
        gridspec_kw={"left": 0.03, "right": 0.98, "top": 0.82, "bottom": 0.16, "wspace": 0.10},
    )
    colors = [BLUE, RED, GREEN, PURPLE]
    centres = np.array([[-1.6, -1.0], [1.7, -0.7], [0.1, 1.7]])
    X = np.vstack([rng.normal(c, 0.5, (60, 2)) for c in centres])

    # 1 - wrong K
    ax = axes[0]
    km = KMeans(5, n_init=10, random_state=0).fit(X)
    for k in range(5):
        ax.scatter(
            X[km.labels_ == k, 0],
            X[km.labels_ == k, 1],
            s=14,
            color=(colors + [GOLD])[k],
            alpha=0.65,
            edgecolor="none",
        )
    ax.set_title(r"$K$ must be known", color=RED, pad=8, fontsize=13)

    # 2 - outliers
    ax = axes[1]
    Xo = np.vstack([X, np.array([[6.5, 5.5], [7.0, 6.2]])])
    km = KMeans(3, n_init=10, random_state=0).fit(Xo)
    for k in range(3):
        ax.scatter(
            Xo[km.labels_ == k, 0],
            Xo[km.labels_ == k, 1],
            s=14,
            color=colors[k],
            alpha=0.65,
            edgecolor="none",
        )
    ax.add_patch(
        Circle((6.75, 5.85), 1.1, facecolor="none", edgecolor=INK, lw=1.4, ls="--")
    )
    ax.text(6.75, 4.35, "two points", ha="center", va="top", color=INK, fontsize=10.5)
    ax.set_title("outliers", color=RED, pad=8, fontsize=13)

    # 3 - non-convex shapes
    ax = axes[2]
    Xm, _ = make_moons(300, noise=0.06, random_state=0)
    km = KMeans(2, n_init=10, random_state=0).fit(Xm)
    for k in range(2):
        ax.scatter(
            Xm[km.labels_ == k, 0],
            Xm[km.labels_ == k, 1],
            s=14,
            color=colors[k],
            alpha=0.65,
            edgecolor="none",
        )
    ax.set_title("non-convex shapes", color=RED, pad=8, fontsize=13)

    for ax in axes:
        blank(ax)


@figure("pca_projection")
def pca_projection(fig):
    rng = np.random.default_rng(33)
    cov = np.array([[1.6, 1.05], [1.05, 0.9]])
    X = rng.multivariate_normal([0, 0], cov, 300)
    X -= X.mean(0)
    vals, vecs = np.linalg.eigh(np.cov(X.T))
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    axes = panels(
        fig,
        3,
        titles=["the data", "the directions", "the projection"],
        colors=[INK, BLUE, GREEN],
        gridspec_kw=dict(left=0.05, right=0.98, top=0.84, bottom=0.26, wspace=0.22),
    )
    for ax in axes[:2]:
        ax.scatter(X[:, 0], X[:, 1], s=14, color=MUTED, alpha=0.55, edgecolor="none")
        ax.set_xlim(-4.2, 4.2)
        ax.set_ylim(-3.0, 3.0)
        ax.set_aspect("equal")
        blank(ax)
    ax = axes[1]
    for i, (color, lw) in enumerate([(BLUE, 3.0), (RED, 2.2)]):
        v = vecs[:, i] * np.sqrt(vals[i]) * 2.2
        ax.annotate(
            "", xy=v, xytext=-v, arrowprops=dict(arrowstyle="<|-|>", color=color, lw=lw)
        )
    ax.text(2.4, 1.9, "most variance", color=BLUE, fontsize=11.5, ha="center")
    ax.text(-1.9, 1.7, "the rest", color=RED, fontsize=11.5, ha="center")

    ax = axes[2]
    z = X @ vecs[:, 0]
    ax.hist(z, bins=34, color=GREEN, alpha=0.5, edgecolor="none")
    ax.set_xlabel(r"$z = P^{T}x \in \mathbb{R}$")
    ax.set_yticks([])
    despine(ax, keep=("bottom",))
    caption(ax, "one number instead of two")


@figure("pca_spectrum")
def pca_spectrum(fig):
    from sklearn.datasets import load_digits
    from sklearn.decomposition import PCA

    digits = load_digits()
    X = digits.data
    pca = PCA().fit(X)
    axes = fig.subplots(
        1,
        2,
        gridspec_kw={"left": 0.06, "right": 0.98, "top": 0.86, "bottom": 0.20, "wspace": 0.18},
    )
    ax = axes[0]
    ratio = np.cumsum(pca.explained_variance_ratio_)
    ax.plot(np.arange(1, ratio.size + 1), ratio, color=BLUE, lw=2.4)
    for q, color in [(10, GREEN), (30, PURPLE)]:
        ax.plot([q, q], [0, ratio[q - 1]], color=color, lw=1.6, ls="--")
        ax.plot([0, q], [ratio[q - 1]] * 2, color=color, lw=1.6, ls="--")
        ax.text(
            q + 1.5,
            ratio[q - 1] - 0.08,
            f"q = {q}: {ratio[q - 1]:.0%}",
            color=color,
            fontsize=11.5,
        )
    ax.set_xlim(0, 64)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("number of components q")
    ax.set_ylabel("variance kept")
    ax.set_title("64 pixels, most of them redundant", pad=10, fontsize=14)

    ax = axes[1]
    ax.axis("off")
    sub = fig.add_axes([0.58, 0.16, 0.40, 0.66])
    sub.axis("off")
    rng = np.random.default_rng(2)
    idx = rng.choice(len(X), 6, replace=False)
    rows = {
        "original": X[idx],
        "q = 30": PCA(30).fit(X).inverse_transform(PCA(30).fit(X).transform(X[idx])),
        "q = 10": PCA(10).fit(X).inverse_transform(PCA(10).fit(X).transform(X[idx])),
    }
    for r, (label, imgs) in enumerate(rows.items()):
        for c in range(6):
            a = sub.inset_axes([c / 6.6 + 0.16, 1 - (r + 1) / 3.3, 1 / 7.6, 1 / 3.9])
            a.imshow(imgs[c].reshape(8, 8), cmap="gray_r")
            a.set_xticks([])
            a.set_yticks([])
            for s in a.spines.values():
                s.set_color(GRID)
        sub.text(
            0.14,
            1 - (r + 0.5) / 3.3,
            label,
            ha="right",
            va="center",
            color=[INK, PURPLE, GREEN][r],
            fontsize=11.5,
        )


@figure("concept_map")
def concept_map(fig):
    ax = canvas(fig)
    box(ax, 3.65, 3.05, 1.7, 0.52, INK, "estimate parameters", size=12.5)
    nodes = [
        (
            BLUE,
            "supervised",
            [("Bayes classifier", 0), ("naive Bayes", 1), ("LDA / QDA", 2)],
            0.75,
        ),
        (GOLD, "unsupervised", [("k-means", 0), ("PCA", 1), ("", 2)], 5.55),
    ]
    for color, title, children, x in nodes:
        box(ax, x, 2.00, 2.7, 0.55, color, title, size=13)
        arrow(ax, (4.5, 2.96), (x + 1.35, 2.60), color=GRID, style="-")
        for label, j in children:
            if label:
                box(
                    ax,
                    x + 0.25,
                    1.42 - j * 0.50,
                    2.2,
                    0.38,
                    color,
                    label,
                    size=11.5,
                    fill="white",
                    lw=1.4,
                )


# ==========================================================================
# driver
# ==========================================================================
def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course01/img")
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
