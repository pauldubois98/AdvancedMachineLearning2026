#!/usr/bin/env python3
"""Every figure of Course02 (robust regression).

One function per figure, registered under the stem the slide deck asks for.
All figures share one canvas (9 x 3.7075 in), which is exactly the content
area pandoc leaves under a slide title, so a figure never has to be resized.
The helpers below are the ones from Course01, kept here so each course
builds on its own.

    python3 scripts/make_figures_c02.py Course02/img [stem ...]
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import (
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
# 1. reminders — linear regression
# ==========================================================================
def _line_data(rng, n=60, slope=1.1, intercept=0.6, noise=0.9, lo=-3.0, hi=3.0):
    x = rng.uniform(lo, hi, n)
    y = intercept + slope * x + rng.normal(0, noise, n)
    return x, y


def _fit(x, y):
    X = np.c_[np.ones_like(x), x]
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    return beta


@figure("regression_setting")
def regression_setting(fig):
    ax = canvas(fig)
    box(ax, 0.45, 2.35, 1.75, 0.80, BLUE, r"$X = (x_1,\dots,x_n)$", size=12.5)
    box(ax, 0.45, 1.25, 1.75, 0.80, GREEN, r"$y = (y_1,\dots,y_n)$", size=12.5)
    box(ax, 2.85, 1.80, 1.55, 0.90, PURPLE, r"learn  $f_\beta$", size=15)
    arrow(ax, (2.30, 2.75), (2.78, 2.45))
    arrow(ax, (2.30, 1.65), (2.78, 2.05))
    arrow(ax, (4.50, 2.25), (5.05, 2.25))
    ax.text(1.32, 3.28, "inputs", ha="center", color=BLUE, fontsize=11.5)
    ax.text(1.32, 1.05, "labels", ha="center", color=GREEN,
            fontsize=11.5)

    plot = fig.add_axes([0.58, 0.22, 0.38, 0.60])
    rng = np.random.default_rng(3)
    x, y = _line_data(rng, 50)
    beta = _fit(x, y)
    plot.scatter(x, y, s=18, color=BLUE, alpha=0.65, edgecolor="white", linewidth=0.4)
    grid = np.linspace(-3.2, 3.2, 10)
    plot.plot(grid, beta[0] + beta[1] * grid, color=PURPLE, lw=2.6)
    plot.set_xlabel(r"$x$")
    plot.set_ylabel(r"$y \in \mathbb{R}$")
    plot.set_xticks([])
    plot.set_yticks([])
    despine(plot, keep=("bottom", "left"))


@figure("regression_apps")
def regression_apps(fig):
    ax = canvas(fig)
    rows = [
        (BLUE, "product sales", "purchase history, season, price"),
        (GREEN, "economic growth", "trade, investment, employment"),
        (PURPLE, "house prices", "surface, location, year"),
        (GOLD, "temperature", "place, altitude, time of year"),
        (RED, "goals next season", "minutes played, past scoring"),
    ]
    for i, (color, target, inputs) in enumerate(rows):
        y = 3.20 - i * 0.62
        ax.text(2.95, y, target, ha="right", va="center", color=color, fontsize=13,
                weight="bold")
        ax.text(3.20, y, "←", ha="center", va="center", color=MUTED, fontsize=13)
        ax.text(3.45, y, inputs, ha="left", va="center", color=INK, fontsize=12)
    ax.text(2.95, 3.60, "predict", ha="right", va="center", color=MUTED, fontsize=11.5)
    ax.text(3.45, 3.60, "from", ha="left", va="center", color=MUTED, fontsize=11.5)


@figure("why_linear")
def why_linear(fig):
    ax = canvas(fig)
    items = [
        (BLUE, "simple", "a good baseline"),
        (GREEN, "interpretable", "coefficients link\ninputs to outputs"),
        (PURPLE, "strong when data is thin", "works with few points"),
        (GOLD, "extensible", "replace $x$ by $\\phi(x)$\ne.g. $x^2$, $x^3$"),
    ]
    w, gap = 1.95, 0.28
    x0 = (W - (4 * w + 3 * gap)) / 2
    for i, (color, title, sub) in enumerate(items):
        x = x0 + i * (w + gap)
        box(ax, x, 1.35, w, 1.40, color, "")
        ax.text(x + w / 2, 2.45, title, ha="center", va="center", color=color,
                fontsize=13, weight="bold")
        ax.text(x + w / 2, 1.85, sub, ha="center", va="center", color=INK,
                fontsize=11, linespacing=1.6)


@figure("linreg_multi")
def linreg_multi(fig):
    rng = np.random.default_rng(2)
    n = 90
    x1 = rng.uniform(25, 145, n)
    x2 = rng.uniform(0, 8, n)
    y = 1.7 * x1 + 14 * x2 + 40 + rng.normal(0, 22, n)

    ax = canvas(fig)
    equation(ax, r"$\hat y \;=\; w_1x_1+w_2x_2+\cdots+w_px_p+b$", x=6.55, y=2.85,
             size=19)
    note(ax, "one weight per column\n"
             "each weight = “how much $\\hat y$ moves\n"
             "when this column moves by 1, all else fixed”",
         x=6.55, y=1.75, size=12.5)
    note(ax, "NB: units of the columns matter",
         x=6.55, y=0.65, color=GOLD, size=12.5)

    plot = fig.add_axes([0.0, 0.0, 0.48, 1.0], projection="3d")
    plot.scatter(x1, x2, y, s=14, color=BLUE, alpha=0.75, depthshade=False)
    g1, g2 = np.meshgrid(np.linspace(25, 145, 12), np.linspace(0, 8, 12))
    plot.plot_surface(g1, g2, 1.7 * g1 + 14 * g2 + 40, color=PURPLE, alpha=0.25,
                      edgecolor=PURPLE, linewidth=0.4)
    plot.set_xlabel("surface", labelpad=-8)
    plot.set_ylabel("floor", labelpad=-8)
    plot.set_zlabel("price", labelpad=-8)
    plot.set_xticklabels([])
    plot.set_yticklabels([])
    plot.set_zticklabels([])
    plot.set_title("2 features → a plane", pad=0)
    plot.view_init(18, -60)


@figure("linreg_basis")
def linreg_basis(fig):
    rng = np.random.default_rng(0)
    x = np.sort(rng.uniform(0, 1, 45))
    y = np.sin(2 * np.pi * x) + rng.normal(0, 0.2, 45)
    grid = np.linspace(0, 1, 400)

    axes = panels(
        fig,
        3,
        titles=[r"$x$ only", r"$x, x^2, x^3$", r"up to $x^{12}$"],
        sharey=True,
        gridspec_kw=dict(left=0.06, right=0.98, top=0.86, bottom=0.22, wspace=0.10),
    )
    for ax, d in zip(axes, (1, 3, 12)):
        p = np.polynomial.Polynomial.fit(x, y, d)
        ax.scatter(x, y, s=18, color=BLUE, alpha=0.65, edgecolor="white",
                   linewidth=0.4, zorder=3)
        ax.plot(grid, p(grid), color=PURPLE, lw=2.6)
        ax.set_xlabel(r"$x$")
        ax.set_ylim(-2.0, 2.0)
        ax.set_xticks([])
        ax.set_yticks([])
        despine(ax, keep=("bottom", "left"))
    axes[0].set_ylabel(r"$y$")
    fig.text(
        0.5,
        0.045,
        r"the same least squares, on the columns $\phi(x) = (x, x^2, \dots, x^d)$",
        ha="center",
        color=MUTED,
        fontsize=12,
    )


@figure("eq_linear_model")
def eq_linear_model(fig):
    ax = canvas(fig)
    equation(
        ax,
        r"$f_\beta(x_i) \;=\; \beta_0 + \beta_1 x_{i,1} + \dots + \beta_d x_{i,d}"
        r"\;=\; x_i'^{T}\beta \;=\; [X\beta]_i$",
        y=3.00,
        size=21,
    )
    plot = fig.add_axes([0.20, 0.10, 0.60, 0.52])
    plot.axis("off")
    plot.set_xlim(0, 10)
    plot.set_ylim(0, 4)
    blocks = [
        (0.4, 3.0, 2.6, r"$X$", BLUE, r"$n \times (d+1)$"),
        (4.2, 0.6, 2.6, r"$\beta$", GREEN, r"$d+1$"),
        (6.9, 0.9, 2.6, r"$\hat{y}$", PURPLE, r"$n$"),
    ]
    for x, w, h, label, color, shape in blocks:
        plot.add_patch(
            Rectangle((x, 0.6), w, h, facecolor="none", edgecolor=color, lw=2.2)
        )
        plot.text(x + w / 2, 0.6 + h / 2, label, ha="center", va="center",
                  color=color, fontsize=17)
        plot.text(x + w / 2, 0.30, shape, ha="center", va="center", color=MUTED,
                  fontsize=11)
    plot.text(3.75, 1.9, r"$\times$", ha="center", va="center", color=INK, fontsize=16)
    plot.text(6.2, 1.9, r"$=$", ha="center", va="center", color=INK, fontsize=16)
    plot.text(0.4, 3.85, r"a column of 1's carries the intercept $\beta_0$",
              ha="left", va="center", color=MUTED, fontsize=11.5)


@figure("ls_residuals")
def ls_residuals(fig):
    rng = np.random.default_rng(11)
    x, y = _line_data(rng, 22, noise=1.1)
    beta = _fit(x, y)
    grid = np.linspace(-3.4, 3.4, 10)
    fitted = beta[0] + beta[1] * x

    axes = panels(
        fig,
        2,
        titles=["Residuals", "Square error"],
        colors=[INK, RED],
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.22, wspace=0.18),
    )
    for ax in axes:
        ax.scatter(x, y, s=26, color=BLUE, alpha=0.8, edgecolor="white", linewidth=0.5,
                   zorder=3)
        ax.plot(grid, beta[0] + beta[1] * grid, color=INK, lw=2.4)
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-4.6, 4.9)
        ax.set_xticks([])
        ax.set_yticks([])
        despine(ax)
    for xi, yi, fi in zip(x, y, fitted):
        axes[0].plot([xi, xi], [fi, yi], color=RED, lw=1.6, alpha=0.8)
    box_ = axes[1].get_position()
    aspect = (7.2 / 9.5) * (box_.height * H) / (box_.width * W)
    for xi, yi, fi in zip(x, y, fitted):
        e = yi - fi
        axes[1].add_patch(
            Rectangle(
                (xi, min(yi, fi)),
                abs(e) * aspect,
                abs(e),
                facecolor=RED,
                alpha=0.18,
                edgecolor=RED,
                lw=0.8,
            )
        )
    caption(axes[0], r"$e_i = y_i - x_i'^{T}\beta$")
    caption(axes[1], r"$L(\beta) = \frac{1}{2}\sum_i e_i^2"
                     r" = \frac{1}{2}\|X\beta - y\|^2$")


@figure("eq_normal_equations")
def eq_normal_equations(fig):
    ax = canvas(fig)
    lines = [
        ((r"$L(\beta) = \frac{1}{2}\|X\beta - y\|^2"
         r" = \frac{1}{2}y^{T}y - \beta^{T}X^{T}y"
         r" + \frac{1}{2}\beta^{T}X^{T}X\beta$"), INK, 3.05),
        (r"$\nabla L(\beta) = X^{T}X\beta - X^{T}y$", INK, 2.20),
        (r"$\hat{\beta} = (X^{T}X)^{-1}X^{T}y$", GREEN, 1.35),
    ]
    for text, color, y in lines:
        ax.text(W / 2, y, text, ha="center", va="center", color=color, fontsize=19)
    ax.text( W / 2, 0.72, r"The loss function is convex.", 
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(
        W / 2,
        0.30,
        r"Unique if $X$ has full column rank; else $X^{T}X$ is not invertible",
        ha="center",
        va="center",
        color=RED,
        fontsize=12,
    )


def _iso(v, offset=np.array([1.85, 0.85])):
    """A 3D point, seen on the slide: y runs back-right, z runs up."""
    x, y, z = v
    return np.array([x + 0.46 * y, 0.30 * y + z]) + offset


@figure("hat_matrix")
def hat_matrix(fig):
    ax = canvas(fig)
    col1 = np.array([2.55, 0.0, 0.0])
    col2 = np.array([0.0, 2.00, 0.0])
    origin = np.zeros(3)
    b1, b2 = 0.80, 0.35
    fitted = b1 * col1 + b2 * col2
    target = fitted + np.array([0.0, 0.0, 2.30])

    corners = [(-0.42, -0.42), (1.62, -0.42), (1.62, 1.45), (-0.42, 1.45)]
    ax.add_patch(
        plt.Polygon(
            [_iso(s * col1 + t * col2) for s, t in corners],
            closed=True,
            facecolor="#eef3fa",
            edgecolor=BLUE,
            lw=2,
        )
    )
    ax.text(*(_iso(0.30 * col1 - 0.42 * col2) + np.array([0.0, -0.28])),
            r"span of the columns of $X$", color=BLUE, fontsize=12, ha="center")

    # the columns themselves, and beta as the recipe that mixes them
    for col, label, shift in (
        (col1, r"$x_1$", np.array([0.10, -0.20])),
        (col2, r"$x_2$", np.array([-0.26, 0.04])),
    ):
        arrow(ax, _iso(origin), _iso(col), color=BLUE, lw=2.0)
        ax.text(*(_iso(col) + shift), label, color=BLUE, fontsize=13, va="center")
    for a, b in ((b1 * col1, fitted), (b2 * col2, fitted)):
        ax.plot(*zip(_iso(a), _iso(b)), color=GRID, lw=1.4, ls="--")

    arrow(ax, _iso(origin), _iso(target), color=PURPLE, lw=2.6)
    arrow(ax, _iso(origin), _iso(fitted), color=GREEN, lw=2.6)
    arrow(ax, _iso(fitted), _iso(target), color=RED, lw=2.6)

    # a right angle that is actually a right angle on the slide
    foot = _iso(fitted)
    along = _iso(origin) - foot
    along = 0.26 * along / np.linalg.norm(along)
    up = np.array([0.0, 0.26])
    ax.plot(*zip(foot + along, foot + along + up, foot + up), color=RED, lw=1.3)

    ax.text(*(_iso(target) + np.array([0.12, 0.05])), r"$y$", color=PURPLE,
            fontsize=16, va="center")
    ax.text(*(_iso(fitted) + np.array([0.34, 0.20])), r"$\hat{y} = X\hat\beta$",
            color=GREEN, fontsize=14, ha="left", va="center")
    ax.text(*(_iso(fitted + np.array([0.0, 0.0, 0.95])) + np.array([0.14, 0.0])),
            r"$e = y - \hat{y}$", color=RED, fontsize=13, ha="left", va="center")

    ax.text(0.35, 3.45, r"$\hat{y} = Hy \qquad H = X(X^{T}X)^{-1}X^{T}$",
            color=INK, fontsize=15, ha="left", va="center")
    ax.text(0.35, 3.00, "orthogonal projection on model domain",
            color=MUTED, fontsize=11.5, ha="left", va="center")
    ax.text(0.35, 2.62, r"$\hat{y} = \hat\beta_1 x_1 + \hat\beta_2 x_2$",
            color=GREEN, fontsize=13, ha="left", va="center")
    ax.text(0.35, 2.22, r"$e \perp$ columns of $X$", color=RED, fontsize=13,
            ha="left", va="center")
    ax.text(0.35, 1.92, r"$X^{T}e = 0$", color=MUTED, fontsize=12.5, ha="left",
            va="center")


# the running example for the rank-deficiency slides: the same measurement
# recorded twice, in hours and in half-hours, so that x2 = 2 x1 exactly
_HOURS = np.array([1.0, 2.0, 3.0, 4.0])
_SCORE = np.array([1.1, 1.9, 3.2, 3.8])
_CANDIDATES = [(1.0, 0.0, BLUE), (0.0, 0.5, GREEN), (2.0, -0.5, PURPLE)]


@figure("collinear_example")
def collinear_example(fig):
    """The same information twice: no fit can tell the two columns apart."""
    ax = canvas(fig)
    ax.text(
        W / 2,
        3.48,
        "two features represent the same information: "
        r"$x_2 = 2\,x_1$",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=12.5,
    )

    # --- the data ---------------------------------------------------------
    cols = [(0.70, r"$x_1$" + "\n1st feature"), (1.70, r"$x_2$" + "\n2nd feature"),
            (2.80, r"$y$" + "\nscore")]
    for x, head in cols:
        ax.text(x, 3.00, head, ha="center", va="center", color=INK, fontsize=11.5,
                linespacing=1.5)
    ax.plot([0.40, 3.15], [2.72, 2.72], color=GRID, lw=1.2)
    for i, (h, sc) in enumerate(zip(_HOURS, _SCORE)):
        y = 2.45 - i * 0.34
        for x, value in ((0.70, f"{h:.0f}"), (1.70, f"{2 * h:.0f}"),
                         (2.80, f"{sc:.1f}")):
            ax.text(x, y, value, ha="center", va="center", color=INK, fontsize=12)

    # --- three recipes, one prediction ------------------------------------
    ax.text(4.30, 3.00, r"$\hat\beta_1$", ha="center", va="center", color=INK,
            fontsize=12)
    ax.text(5.05, 3.00, r"$\hat\beta_2$", ha="center", va="center", color=INK,
            fontsize=12)
    ax.text(6.95, 3.00, r"prediction  $\hat\beta_1 x_1 + \hat\beta_2 x_2$",
            ha="center", va="center", color=INK, fontsize=12)
    ax.plot([4.00, 8.60], [2.72, 2.72], color=GRID, lw=1.2)
    for i, (b1, b2, color) in enumerate(_CANDIDATES):
        y = 2.35 - i * 0.45
        ax.text(4.30, y, f"{b1:.1f}", ha="center", va="center", color=color,
                fontsize=13)
        ax.text(5.05, y, f"{b2:+.1f}", ha="center", va="center", color=color,
                fontsize=13)
        ax.text(
            6.95,
            y,
            f"{b1:.1f}" + r"$\,x_1$" + f" {b2:+.1f}" + r"$\,(2x_1)$"
            + r"$\;=\;$" + r"$1.0\,x_1$",
            ha="center",
            va="center",
            color=color,
            fontsize=12.5,
        )
    ax.plot([4.00, 8.60], [0.88, 0.88], color=GRID, lw=1.2)
    ax.text(6.95, 0.58, "predicted scores are identical",
            ha="center", va="center", color=MUTED, fontsize=11.5)

    ax.text(
        W / 2,
        0.18,
        r"the data pins down $\hat\beta_1 + 2\hat\beta_2 = 1$",
        ha="center",
        va="center",
        color=RED,
        fontsize=13.5,
    )


@figure("collinear_valley")
def collinear_valley(fig):
    """The least-squares objective, when only one combination is identified."""
    x1, y = _HOURS, _SCORE
    best = float(x1 @ y / (x1 @ x1))

    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.06, right=0.98, top=0.82, bottom=0.24, wspace=0.30),
    )

    ax = axes[0]
    b1g, b2g = np.meshgrid(np.linspace(-1.2, 2.6, 300), np.linspace(-1.0, 1.6, 300))
    combo = b1g + 2 * b2g
    loss = 0.5 * ((y[:, None, None] - combo * x1[:, None, None]) ** 2).sum(0)
    ax.contourf(b1g, b2g, loss, levels=14, cmap="Blues_r", alpha=0.85)
    line_b2 = np.linspace(-1.0, 1.6, 10)
    ax.plot(best - 2 * line_b2, line_b2, color=RED, lw=2.6)
    for b1, b2, color in _CANDIDATES:
        ax.plot([b1], [b2], "o", color=color, ms=10, mec="white", mew=1.2, zorder=4)
    ax.set_xlim(-1.2, 2.6)
    ax.set_ylim(-1.0, 1.6)
    ax.set_xlabel(r"$\beta_1$")
    ax.set_ylabel(r"$\beta_2$")
    ax.set_title("loss", pad=10, fontsize=13)

    ax = axes[1]
    t = np.linspace(-1.1, 1.1, 300)
    along = np.array(
        [0.5 * ((y - (best - 2 * tt + 2 * tt) * x1) ** 2).sum() for tt in t]
    )
    across = np.array(
        [0.5 * ((y - (best + tt) * x1) ** 2).sum() for tt in t]
    )
    ax.plot(t, along, color=RED, lw=2.8)
    ax.plot(t, across, color=INK, lw=2.4, ls="--")
    ax.text(0.55, along[0] + 0.5, "along red line", color=RED, fontsize=11.5)
    ax.text(-0.85, across[0] * 0.75, "orthogonal to red line", color=INK, fontsize=11.5)
    ax.set_xlabel("how far you move")
    ax.set_ylabel("loss")
    ax.set_title("direction", pad=10, fontsize=13)

    ax = axes[2]
    ax.axis("off")
    gram = np.array([[x1 @ x1, 2 * x1 @ x1], [2 * x1 @ x1, 4 * x1 @ x1]])
    ax.text(0.0, 0.93, r"$X^{T}X$", transform=ax.transAxes, color=INK, fontsize=15,
            va="center")
    for r in range(2):
        for c in range(2):
            ax.text(0.34 + c * 0.30, 0.78 - r * 0.17, f"{gram[r, c]:.0f}",
                    transform=ax.transAxes, color=INK, fontsize=14, ha="center",
                    va="center")
    for xb, side in ((0.22, 1), (0.82, -1)):
        ax.plot([xb + 0.03 * side, xb, xb, xb + 0.03 * side],
                [0.87, 0.87, 0.52, 0.52], color=INK, lw=1.4,
                transform=ax.transAxes, clip_on=False)
    ax.text(0.0, 0.36, r"$\det(X^{T}X) = 0$", transform=ax.transAxes, color=RED,
            fontsize=15, va="center")
    ax.text(0.0, 0.02, r"so $(X^{T}X)^{-1}$ does not exist", transform=ax.transAxes,
            color=RED, fontsize=13, va="center")


@figure("near_collinear")
def near_collinear(fig):
    """The version you actually meet: almost collinear, and very unstable."""
    rng = np.random.default_rng(12)
    n, reps = 40, 150

    def sample(corr):
        x1 = rng.normal(size=n)
        x2 = corr * x1 + np.sqrt(1 - corr**2) * rng.normal(size=n)
        y = 1.0 * x1 + 1.0 * x2 + rng.normal(0, 0.4, n)
        return np.c_[x1, x2], y

    def refit(corr, lam=0.0):
        out = []
        for _ in range(reps):
            X, y = sample(corr)
            gram = X.T @ X + lam * np.eye(2)
            out.append(np.linalg.solve(gram, X.T @ y))
        return np.array(out)

    panels_ = [
        (BLUE, "independent informations", refit(0.0), r"$\rho(x_1,x_2) = 0$"),
        (RED, "nearly same information", refit(0.999), r"$\rho(x_1,x_2) = 0.999$"),
        (GREEN, "nearly same with ridge", refit(0.999, lam=5.0), "$\\rho(x_1,x_2) = 0.999$\n$\\lambda = 5$"),
    ]
    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.05, right=0.98, top=0.82, bottom=0.24, wspace=0.16),
    )
    for ax, (color, title, betas, tag) in zip(axes, panels_):
        ax.plot([1.0], [1.0], "X", color=MUTED, ms=13, zorder=2)
        ax.scatter(betas[:, 0], betas[:, 1], s=22, color=color, alpha=0.55,
                   edgecolor="none", zorder=3)
        ax.axhline(0, color=GRID, lw=1.0)
        ax.axvline(0, color=GRID, lw=1.0)
        ax.set_xlim(-4.5, 6.5)
        ax.set_ylim(-4.5, 6.5)
        ax.set_aspect("equal")
        ax.set_xticks([0])
        ax.set_yticks([0])
        ax.set_xlabel(r"$\hat\beta_1$", labelpad=1)
        ax.set_ylabel(r"$\hat\beta_2$", labelpad=1)
        despine(ax, keep=("bottom", "left"))
        ax.set_title(title, color=color, pad=10, fontsize=13)
        ax.text(0.03, 0.95, tag, transform=ax.transAxes, color=MUTED, fontsize=11,
                va="top")
        ax.annotate(
            r"spread $\pm %.2f$ on $\hat\beta_1$" % betas[:, 0].std(),
            xy=(0.5, -0.20),
            xycoords="axes fraction",
            ha="center",
            va="top",
            color=color,
            fontsize=11.5,
        )
    fig.text(
        0.5,
        0.0,
        "ridge stabilizes coefficients",
        # "the cross is the truth\nridge stabilizes coefficients",
        ha="center",
        color=MUTED,
        fontsize=12,
    )


@figure("ls_variance")
def ls_variance(fig):
    rng = np.random.default_rng(21)
    grid = np.linspace(-3.4, 3.4, 10)
    designs = [("x spread out", 2.6, BLUE), ("x bunched together", 0.7, RED)]
    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.05, right=0.97, top=0.84, bottom=0.24, wspace=0.24),
    )
    clouds = {}
    for ax, (title, spread, color) in zip(axes, designs):
        betas = []
        for rep in range(60):
            x = rng.uniform(-spread, spread, 25)
            y = 0.6 + 1.1 * x + rng.normal(0, 0.9, 25)
            b = _fit(x, y)
            betas.append(b)
            ax.plot(grid, b[0] + b[1] * grid, color=color, lw=0.9, alpha=0.25)
        x = rng.uniform(-spread, spread, 25)
        y = 0.6 + 1.1 * x + rng.normal(0, 0.9, 25)
        ax.scatter(x, y, s=16, color=INK, alpha=0.6, edgecolor="none", zorder=3)
        ax.plot(grid, 0.6 + 1.1 * grid, color=INK, lw=2.2, ls="--")
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-5.5, 6.5)
        ax.set_xticks([])
        ax.set_yticks([])
        despine(ax)
        ax.set_title(title, color=color, pad=10, fontsize=13)
        clouds[title] = np.array(betas)
    caption(axes[0], "60 samples")
    caption(axes[1], "60 samples")

    ax = axes[2]
    for (title, _, color), marker in zip(designs, ("o", "o")):
        b = clouds[title]
        ax.scatter(b[:, 0], b[:, 1], s=18, color=color, alpha=0.6, edgecolor="none")
    ax.plot([0.6], [1.1], "X", color=INK, ms=12, mec="white", mew=1.4)
    ax.set_xlabel(r"$\hat\beta_0$")
    ax.set_ylabel(r"$\hat\beta_1$")
    ax.set_title(r"$\mathrm{Var}(\hat\beta) = (X^{T}X)^{-1}\sigma^2$", pad=10,
                 fontsize=13)


# ==========================================================================
# 2. reminders — regularized regression
# ==========================================================================
def _sparse_design(rng, n=60, d=12, k=3, noise=1.0):
    X = rng.normal(size=(n, d))
    beta = np.zeros(d)
    beta[:k] = rng.choice([-2.5, -1.8, 1.9, 2.6], k)
    y = X @ beta + rng.normal(0, noise, n)
    return X, y, beta


@figure("high_dim")
def high_dim(fig):
    rng = np.random.default_rng(31)
    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.08, right=0.97, top=0.84, bottom=0.24, wspace=0.26),
    )

    ax = axes[0]
    n = 40
    dims = np.arange(1, 34, 2)
    train, test = [], []
    for d in dims:
        tr, te = [], []
        for _ in range(60):
            X = rng.normal(size=(n, d))
            beta = np.zeros(d)
            beta[: min(3, d)] = 2.0
            y = X @ beta + rng.normal(0, 1.0, n)
            b = np.linalg.lstsq(X, y, rcond=None)[0]
            tr.append(np.mean((y - X @ b) ** 2))
            Xte = rng.normal(size=(400, d))
            yte = Xte @ beta + rng.normal(0, 1.0, 400)
            te.append(np.mean((yte - Xte @ b) ** 2))
        train.append(np.mean(tr))
        test.append(np.mean(te))
    ax.plot(dims, train, color=GREEN, lw=2.6)
    ax.plot(dims, test, color=RED, lw=2.6)
    ax.text(dims[-1], train[-1], "  training", color=GREEN, fontsize=12, va="center")
    ax.text(24, min(test[-1], 9.0), "test", color=RED, fontsize=12, va="bottom")
    ax.axvline(n, color=MUTED, lw=1.2, ls=":")
    ax.set_xlim(1, 42)
    ax.set_ylim(0, 10)
    ax.set_xlabel(r"number of features $d$    (with $n = 40$)")
    ax.set_ylabel("squared error")
    ax.set_title("accuracy", color=RED, pad=10, fontsize=13.5)
    caption(ax, "fits better and better, predicts worse and worse")

    ax = axes[1]
    X, y, beta = _sparse_design(rng, n=60, d=12, k=3)
    fitted = np.linalg.lstsq(X, y, rcond=None)[0]
    idx = np.arange(1, 13)
    ax.bar(idx, fitted, color=[GREEN if beta[i] else GRID for i in range(12)],
           edgecolor="none")
    ax.axhline(0, color=INK, lw=1.2)
    ax.set_xticks(idx)
    ax.set_xticklabels([str(i) for i in idx], fontsize=9)
    ax.set_xlabel("feature")
    ax.set_ylabel(r"$\hat\beta_j$")
    ax.set_title("interpretation", color=GREEN, pad=10, fontsize=13.5)
    despine(ax, keep=("bottom", "left"))
    caption(ax, "a few features only are actually used")


@figure("eq_regularized")
def eq_regularized(fig):
    ax = canvas(fig)
    pieces = [
        (r"$L_{new}(\beta)$", INK, None),
        (r"$=$", INK, None),
        (r"$\frac{1}{2}\|y - X\beta\|^2$", BLUE, "fit the data"),
        (r"$+$", INK, None),
        (r"$\lambda$", GOLD, "how much we insist"),
        (r"$R(\beta)$", RED, "keep β small\nor sparse"),
    ]
    size, gap, y = 24, 0.18, 2.45
    widths = [text_width(fig, ax, text, size) for text, _, _ in pieces]
    x = (W - sum(widths) - gap * (len(pieces) - 1)) / 2
    for (text, color, label), w in zip(pieces, widths):
        ax.text(x, y, text, ha="left", va="center", color=color, fontsize=size)
        if label:
            centre = x + w / 2
            low = label.startswith("how")
            ax.text(centre, 0.95 if low else 1.55, label, ha="center", va="top",
                    color=color, fontsize=12, linespacing=1.6)
            arrow(ax, (centre, 1.08 if low else 1.68), (centre, 2.02), color=color,
                  lw=1.4)
        x += w + gap
    note(ax, "λ = 0 is least squares; λ → ∞ crushes coefficients to 0",
         y=0.55)


@figure("penalty_zoo")
def penalty_zoo(fig):
    grid = np.linspace(-2.2, 2.2, 600)
    columns = [
        (BLUE, "ridge", r"$R(\beta) = \frac{1}{2}\|\beta\|^2$", 0.5 * grid**2,
         "shrinks every coefficient", "explicit solution"),
        (GREEN, "lasso", r"$R(\beta) = \|\beta\|_1$", np.abs(grid),
         "sets many of them to zero", "convex, not differentiable"),
        (RED, "best subset", r"$R(\beta) = \|\beta\|_0$", None,
         "counts the ones you keep", "not convex, not differentiable"),
    ]
    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.04, right=0.98, top=0.80, bottom=0.30, wspace=0.16),
    )
    for ax, (color, name, formula, values, effect, cost) in zip(axes, columns):
        if values is None:
            for side in (grid[grid < -0.02], grid[grid > 0.02]):
                ax.plot(side, np.ones_like(side), color=color, lw=2.6)
            ax.plot([0], [0], "o", color=color, ms=8)
            ax.plot([0], [1], "o", color="white", mec=color, mew=2.0, ms=8)
        else:
            ax.plot(grid, values, color=color, lw=2.6)
        ax.set_ylim(-0.15, 2.6)
        ax.set_xticks([0])
        ax.set_yticks([])
        ax.set_xlabel(r"$\beta_j$", labelpad=1)
        despine(ax, keep=("bottom",))
        ax.set_title(f"{name}\n{formula}", color=color, pad=10, fontsize=13,
                     linespacing=1.8)
        ax.annotate(effect, xy=(0.5, -0.22), xycoords="axes fraction", ha="center",
                    va="top", color=INK, fontsize=12)
        ax.annotate(cost, xy=(0.5, -0.42), xycoords="axes fraction", ha="center",
                    va="top", color=MUTED, fontsize=11)


@figure("penalty_geometry")
def penalty_geometry(fig):
    beta_ls = np.array([1.55, 1.05])
    A = np.array([[1.0, 0.75], [0.75, 1.3]])
    gx, gy = np.meshgrid(np.linspace(-0.6, 2.4, 400), np.linspace(-0.9, 2.1, 400))
    pts = np.c_[gx.ravel() - beta_ls[0], gy.ravel() - beta_ls[1]]
    loss = np.einsum("ij,jk,ik->i", pts, A, pts).reshape(gx.shape)

    theta = np.linspace(0, 2 * np.pi, 800)
    shapes = [
        (BLUE, r"ridge   $\frac{1}{2}\|\beta\|^2$", 2.0, "a circle has no corner"),
        (GREEN, r"lasso   $\|\beta\|_1$", 1.0, "the corner sits on the axis"),
        (RED, r"elastic net   $\alpha\|\beta\|_1 + "
              r"\frac{1-\alpha}{2}\|\beta\|^2$", None,
         "a corner, and a rounded edge"),
    ]
    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.82, bottom=0.28, wspace=0.12),
    )
    for ax, (color, title, q, remark) in zip(axes, shapes):
        c, s = np.cos(theta), np.sin(theta)
        if q is None:                       # elastic net, alpha = 0.6
            alpha = 0.6
            quad = (1 - alpha) / 2
            lin = alpha * (np.abs(c) + np.abs(s))
            radius = (-lin + np.sqrt(lin**2 + 4 * quad)) / (2 * quad)
        else:
            radius = (np.abs(c) ** q + np.abs(s) ** q) ** (-1.0 / q)
        bx, by = radius * c, radius * s
        ax.plot(bx, by, color=color, lw=2.4)
        ax.fill(bx, by, color=color, alpha=0.10)
        on_ball = np.c_[bx - beta_ls[0], by - beta_ls[1]]
        scores = np.einsum("ij,jk,ik->i", on_ball, A, on_ball)
        best = np.argmin(scores)
        ax.contour(gx, gy, loss, levels=[scores[best], scores[best] * 2.4,
                                         scores[best] * 4.6],
                   colors=[MUTED], linewidths=1.2)
        ax.plot(*beta_ls, "+", color=INK, ms=13, mew=2)
        ax.text(beta_ls[0] + 0.08, beta_ls[1] + 0.06, r"$\hat\beta_{LS}$", color=INK,
                fontsize=12)
        ax.plot(bx[best], by[best], "o", color=color, ms=10, zorder=4)
        ax.axhline(0, color=GRID, lw=1.0)
        ax.axvline(0, color=GRID, lw=1.0)
        ax.set_xlim(-0.75, 2.4)
        ax.set_ylim(-0.95, 2.1)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        despine(ax)
        ax.set_title(title, color=color, pad=10, fontsize=11.5)
        caption(ax, remark)
    fig.text(
        0.5,
        0.0125,
        "solution is where the loss contours first touch the ball",
        ha="center",
        color=MUTED,
        fontsize=12,
    )


@figure("lambda_path")
def lambda_path(fig):
    from sklearn.linear_model import lasso_path, ridge_regression

    rng = np.random.default_rng(41)
    X, y, beta = _sparse_design(rng, n=60, d=10, k=3, noise=1.5)
    axes = panels(
        fig,
        2,
        titles=["ridge", "lasso"],
        colors=[BLUE, GREEN],
        gridspec_kw=dict(left=0.07, right=0.97, top=0.84, bottom=0.28, wspace=0.22),
    )
    lambdas = np.logspace(-2, 3, 120)
    coefs = np.array([ridge_regression(X, y, alpha=lam) for lam in lambdas])
    for j in range(X.shape[1]):
        color = INK if beta[j] else MUTED
        axes[0].plot(lambdas, coefs[:, j], color=color, lw=1.8,
                     alpha=1.0 if beta[j] else 0.45)
    axes[0].set_xscale("log")
    axes[0].set_xlabel(r"$\lambda$")
    axes[0].set_ylabel(r"$\hat\beta_j$")
    caption(axes[0], "everything shrinks, nothing ever reaches zero")

    alphas, lasso_coefs, _ = lasso_path(X, y, n_alphas=120)
    for j in range(X.shape[1]):
        color = INK if beta[j] else MUTED
        axes[1].plot(alphas, lasso_coefs[j], color=color, lw=1.8,
                     alpha=1.0 if beta[j] else 0.45)
    axes[1].set_xscale("log")
    axes[1].set_xlabel(r"$\lambda$")
    caption(axes[1], "coefficients hit zero one by one")
    for ax in axes:
        ax.axhline(0, color=GRID, lw=1.0)
        ax.invert_xaxis()
    fig.text(0.5, 0.025, "dark lines: features actually carrying information",
             ha="center", color=MUTED, fontsize=11.5)


@figure("thresholding")
def thresholding(fig):
    grid = np.linspace(-3, 3, 600)
    lam = 1.0
    curves = [
        (BLUE, "ridge", r"$\hat\beta_j / (1+\lambda)$", grid / (1 + lam),
         "weight decay"),
        (GREEN, "lasso", r"$\mathrm{sign}(\hat\beta_j)(|\hat\beta_j|-\lambda)_+$",
         np.sign(grid) * np.maximum(np.abs(grid) - lam, 0), "soft thresholding"),
        (RED, "best subset", r"$\hat\beta_j \cdot \delta(\hat\beta_j^2 \geq 2\lambda)$",
         grid * (grid**2 >= 2 * lam), "hard thresholding"),
    ]
    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.05, right=0.98, top=0.78, bottom=0.26, wspace=0.18),
    )
    for ax, (color, name, formula, values, label) in zip(axes, curves):
        ax.plot(grid, grid, color=GRID, lw=1.4, ls="--")
        ax.plot(grid, values, color=color, lw=2.8)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_aspect("equal")
        ax.set_xticks([0])
        ax.set_yticks([0])
        ax.set_xlabel(r"$\hat\beta_j$ from least squares", labelpad=1, fontsize=10.5)
        ax.set_ylabel("after the penalty", labelpad=1, fontsize=10.5)
        despine(ax, keep=("bottom", "left"))
        ax.set_title(f"{name}\n{formula}", color=color, pad=8, fontsize=12,
                     linespacing=1.8)
        caption(ax, label, color=color)


@figure("prox_idea")
def prox_idea(fig):
    ax = canvas(fig)
    ax.text(
        W / 2,
        3.42,
        r"$R(\beta)$ is not differentiable",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=13,
    )
    box(ax, 1.30, 1.95, 2.85, 0.95, BLUE, "", fill="white")
    ax.text(2.72, 2.62, "1.  gradient step", ha="center", va="center", color=BLUE,
            fontsize=13, weight="bold")
    ax.text(2.72, 2.22, r"$\bar\beta^k = \beta^k - \theta \nabla L(\beta^k)$",
            ha="center", va="center", color=INK, fontsize=15)
    box(ax, 4.85, 1.95, 2.85, 0.95, RED, "", fill="white")
    ax.text(6.27, 2.62, "2.  proximal step", ha="center", va="center", color=RED,
            fontsize=13, weight="bold")
    ax.text(6.27, 2.18,
            r"$\beta^{k+1} = \arg\min_\beta \frac{1}{2}\|\bar\beta^k - \beta\|^2"
            r" + \lambda\theta R(\beta)$",
            ha="center", va="center", color=INK, fontsize=12.5)
    arrow(ax, (4.22, 2.42), (4.78, 2.42))
    ax.add_patch(
        FancyArrowPatch(
            (6.27, 1.86),
            (2.72, 1.86),
            arrowstyle="-|>",
            mutation_scale=15,
            linewidth=2.0,
            color=MUTED,
            connectionstyle="arc3,rad=-0.30",
            shrinkA=0,
            shrinkB=0,
            zorder=4,
        )
    )
    ax.text(4.50, 1.08, "repeat", ha="center", va="center", color=MUTED, fontsize=12)
    ax.text(2.72, 0.80, "handles the smooth part\nof the objective", ha="center",
            va="center", color=BLUE, fontsize=11.5, linespacing=1.6)
    ax.text(6.27, 0.80, "handles the penalty,\nin closed form", ha="center",
            va="center", color=RED, fontsize=11.5, linespacing=1.6)


@figure("eq_prox")
def eq_prox(fig):
    ax = canvas(fig)
    rows = [
        (GREEN, r"$R(\beta) = \|\beta\|_1$",
         r"$\beta^{k+1} = \mathrm{sign}(\bar\beta^k)\,"
         r"\max(|\bar\beta^k| - \lambda\theta,\ 0)$"),
        (RED, r"$R(\beta) = \|\beta\|_0$",
         r"$\beta^{k+1} = \bar\beta^k \cdot \delta\!\left((\bar\beta^k)^2 "
         r"\geq 2\lambda\theta\right)$"),
    ]
    for i, (color, penalty, formula) in enumerate(rows):
        y = 2.65 - i * 0.75
        ax.text(1.55, y, penalty, ha="right", va="center", color=color, fontsize=15)
        ax.text(1.85, y, formula, ha="left", va="center", color=INK, fontsize=15)
    column(
        ax,
        1.40,
        1.05,
        6.4,
        "Behaviour:",
        [
            r"Convergence for $\theta \in\ ]0,\ 2/\|X^{T}X\|[$",
            r"Global minimum with $\ell_1$ & a local minimum with $\ell_0$",
        ],
        INK,
        item_size=12,
        title_size=12.5,
    )


# ==========================================================================
# 3. robust regression — why, and the M-estimation idea
# ==========================================================================
def _outlier_data(rng, n=26, n_out=1):
    x = np.linspace(-3, 3, n)
    y = 0.6 + 1.1 * x + rng.normal(0, 0.55, n)
    x_out = np.array([2.35, -2.2][:n_out])
    y_out = np.array([-5.4, 5.0][:n_out])
    return x, y, x_out, y_out


def rho_huber(e, delta=1.0):
    a = np.abs(e)
    return np.where(a <= delta, 0.5 * e**2, delta * (a - 0.5 * delta))


def psi_huber(e, delta=1.0):
    return np.clip(e, -delta, delta)


def w_huber(e, delta=1.0):
    a = np.abs(e)
    return np.where(a <= delta, 1.0, delta / np.maximum(a, 1e-12))


def rho_tukey(e, delta=3.0):
    a = np.abs(e)
    inner = 1 - (1 - (e / delta) ** 2) ** 3
    return np.where(a <= delta, (delta**2 / 6) * inner, delta**2 / 6)


def psi_tukey(e, delta=3.0):
    a = np.abs(e)
    return np.where(a <= delta, e * (1 - (e / delta) ** 2) ** 2, 0.0)


def w_tukey(e, delta=3.0):
    a = np.abs(e)
    return np.where(a <= delta, (1 - (e / delta) ** 2) ** 2, 0.0)


@figure("outlier_demo")
def outlier_demo(fig):
    rng = np.random.default_rng(7)
    x, y, x_out, y_out = _outlier_data(rng)
    grid = np.linspace(-3.4, 3.4, 10)
    clean = _fit(x, y)
    dirty = _fit(np.r_[x, x_out], np.r_[y, y_out])

    axes = panels(
        fig,
        2,
        titles=["clean data", "one point moved"],
        colors=[GREEN, RED],
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.22, wspace=0.16),
    )
    for ax in axes:
        ax.scatter(x, y, s=26, color=BLUE, alpha=0.75, edgecolor="white", linewidth=0.5)
        ax.plot(grid, clean[0] + clean[1] * grid, color=GREEN, lw=2.4)
        ax.set_xlim(-3.5, 3.5)
        ax.set_ylim(-6.5, 6.0)
        ax.set_xticks([])
        ax.set_yticks([])
        despine(ax)
    axes[1].scatter(x_out, y_out, s=90, color=RED, zorder=4, edgecolor="white",
                    linewidth=1.0)
    axes[1].plot(grid, dirty[0] + dirty[1] * grid, color=RED, lw=2.8)
    axes[1].annotate(
        "one point out of 27",
        xy=(x_out[0], y_out[0]),
        xytext=(-1.2, -5.4),
        color=RED,
        fontsize=11.5,
        ha="center",
        arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.4),
    )
    caption(axes[0], rf"$\hat\beta_1 = {clean[1]:.2f}$")
    caption(axes[1], rf"$\hat\beta_1 = {dirty[1]:.2f}$")


@figure("squared_loss_pull")
def squared_loss_pull(fig):
    rng = np.random.default_rng(7)
    x, y, x_out, y_out = _outlier_data(rng)
    X = np.r_[x, x_out]
    Y = np.r_[y, y_out]
    beta = _fit(X, Y)
    residuals = Y - (beta[0] + beta[1] * X)
    share = 0.5 * residuals**2
    share = share / share.sum()

    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.07, right=0.97, top=0.84, bottom=0.24, wspace=0.26),
    )
    ax = axes[0]
    span = np.abs(residuals).max() * 1.1
    grid = np.linspace(-span, span, 400)
    ax.plot(grid, 0.5 * grid**2, color=RED, lw=2.8)
    ax.plot(residuals[:-1], 0.5 * residuals[:-1] ** 2, "o", color=BLUE, ms=7)
    ax.plot(residuals[-1], 0.5 * residuals[-1] ** 2, "o", color=RED, ms=11)
    ax.set_xlabel(r"residual $e_i$")
    ax.set_ylabel(r"$\rho(e) = e^2/2$")
    ax.set_title("every residual is squared", pad=10, fontsize=13.5)
    caption(ax, "twice as far away, four times as loud")

    ax = axes[1]
    order = np.argsort(-share)
    colors = [RED if i == len(share) - 1 else BLUE for i in order]
    ax.bar(np.arange(len(share)), share[order], color=colors, edgecolor="none")
    ax.set_xticks([])
    ax.set_xlabel("the 27 points sorted")
    ax.set_ylabel("share of the total loss")
    ax.text(
        0.35,
        0.85,
        "one point carries %.0f %% of the loss" % (100 * share.max()),
        transform=ax.transAxes,
        color=RED,
        fontsize=12,
    )
    despine(ax, keep=("bottom", "left"))
    caption(ax, "least squares can not ignore a point")


@figure("outliers_vs_mismodelling")
def outliers_vs_mismodelling(fig):
    rng = np.random.default_rng(13)
    axes = panels(
        fig,
        2,
        titles=["outliers", "mismodelling"],
        colors=[RED, GOLD],
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.30, wspace=0.16),
    )
    grid = np.linspace(-3.4, 3.4, 200)

    x, y, x_out, y_out = _outlier_data(rng, n_out=2)
    ax = axes[0]
    ax.scatter(x, y, s=24, color=BLUE, alpha=0.75, edgecolor="white", linewidth=0.5)
    ax.scatter(x_out, y_out, s=80, color=RED, zorder=4, edgecolor="white", linewidth=1)
    beta = _fit(x, y)
    ax.plot(grid, beta[0] + beta[1] * grid, color=GREEN, lw=2.4)
    caption(ax, "the model is right, a few points are off")

    ax = axes[1]
    xc = np.linspace(-3, 3, 40)
    yc = 0.45 * xc**2 - 0.8 + rng.normal(0, 0.35, xc.size)
    ax.scatter(xc, yc, s=24, color=BLUE, alpha=0.75, edgecolor="white", linewidth=0.5)
    b = _fit(xc, yc)
    ax.plot(grid, b[0] + b[1] * grid, color=GOLD, lw=2.4)
    caption(ax, "the model is wrong")

    for ax in axes:
        ax.set_xlim(-3.5, 3.5)
        ax.set_xticks([])
        ax.set_yticks([])
        despine(ax)


@figure("eq_m_estimation")
def eq_m_estimation(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.42, r"i.i.d. sample $x_1,\dots,x_n \sim f(x;\theta)$",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    lines = [
        (r"$\max_\theta\ \prod_i f(x_i;\theta)"
         r"\quad\Longleftrightarrow\quad"
         r"\min_\theta\ \sum_i \rho(x_i;\theta)"
         r"\quad\mathrm{with}\quad \rho = -\log f$", BLUE, 2.75),
        (r"$\min_\theta\ \sum_i \rho(x_i;\theta)"
         r"\qquad \rho \ \mathrm{free\ to\ choose}$", GREEN, 1.85),
        # (r"$\sum_i \psi(x_i;\theta) = 0"
        #  r"\qquad \psi = \frac{\partial \rho}{\partial \theta}$", INK, 1.05),
    ]
    for text, color, y in lines:
        ax.text(W / 2, y, text, ha="center", va="center", color=color, fontsize=16)
    ax.text(2.30, 2.35, "maximum likelihood", ha="center", va="center", color=BLUE,
            fontsize=11.5)
    ax.text(2.30, 1.45, "M-estimation", ha="center", va="center", color=GREEN,
            fontsize=11.5)
    # note(ax, "keep the machinery of likelihood, drop the obligation to believe f",
    #      y=0.38)


@figure("rho_from_density")
def rho_from_density(fig):
    grid = np.linspace(-4.5, 4.5, 500)
    families = [
        (BLUE, "Gaussian noise",
         np.exp(-0.5 * grid**2), 0.5 * grid**2, r"$\rho(e) = e^2/2$", "least squares"),
        (GREEN, "Laplace noise",
         np.exp(-np.abs(grid)), np.abs(grid), r"$\rho(e) = |e|$",
         "least absolute deviations"),
        (PURPLE, "Student noise",
         (1 + grid**2 / 2) ** (-1.5), np.log1p(grid**2 / 2),
         r"$\rho(e) = \log(1 + e^2/\nu)$", "heavy tails allowed"),
    ]
    axes = fig.subplots(
        2,
        3,
        gridspec_kw=dict(
            left=0.04,
            right=0.98,
            top=0.84,
            bottom=0.20,
            wspace=0.14,
            hspace=0.55,
            height_ratios=[1, 1.1],
        ),
    )
    for i, (color, name, density, rho, formula, label) in enumerate(families):
        top, bottom = axes[0, i], axes[1, i]
        top.plot(grid, density, color=color, lw=2.4)
        top.fill_between(grid, density, color=color, alpha=0.12)
        top.set_ylim(0, 1.15)
        top.set_xticks([0])
        top.set_yticks([])
        despine(top, keep=("bottom",))
        top.set_title(name, color=color, pad=8, fontsize=13)

        bottom.plot(grid, rho, color=color, lw=2.6)
        bottom.set_ylim(-0.3, 6.0)
        bottom.set_xticks([0])
        bottom.set_yticks([])
        bottom.set_xlabel(r"$e$", labelpad=1)
        despine(bottom, keep=("bottom",))
        bottom.annotate(formula, xy=(0.5, 1.12), xycoords="axes fraction",
                        ha="center", va="bottom", color=color, fontsize=13)
        bottom.annotate(label, xy=(0.5, -0.30), xycoords="axes fraction",
                        ha="center", va="top", color=MUTED, fontsize=11.5)
    fig.text(
        0.5,
        0.955,
        r"a noise model is a loss:  $\rho = -\log f$",
        ha="center",
        color=MUTED,
        fontsize=12.5,
    )


@figure("eq_robust_regression")
def eq_robust_regression(fig):
    ax = canvas(fig)
    equation(
        ax,
        r"$L_{robust}(\beta) \;=\; \sum_{i=1}^{n} \rho\!\left(y_i - "
        r"x_i'^{T}\beta\right)$",
        y=2.85,
        size=24,
        color=GREEN,
    )
    column(
        ax,
        1.05,
        1.95,
        3.6,
        "ρ must satisfy",
        [
            r"$\rho(e) \geq 0$ and $\rho(0) = 0$",
            r"$\rho(e) = \rho(-e)$",
            r"$\rho(e) \geq \rho(e')$ when $|e| \geq |e'|$",
        ],
        INK,
        item_size=12,
        title_size=12.5,
    )
    ax.text(
        5.35,
        0.62,
        r"$\rho(e) = e^2$ gives least squares back",
        color=MUTED,
        fontsize=11.5,
        va="top",
    )


@figure("rho_zoo")
def rho_zoo(fig):
    grid = np.linspace(-4.5, 4.5, 700)
    convex = [
        (MUTED, "least squares", 0.5 * grid**2),
        (BLUE, "Huber", rho_huber(grid, 1.5)),
        (GREEN, r"$\ell_1$", np.abs(grid)),
        (GOLD, "log cosh", np.log(np.cosh(grid))),
    ]
    nonconvex = [
        (MUTED, "least squares", 0.5 * grid**2),
        (PURPLE, "Cauchy", np.log1p(grid**2 / 2)),
        (RED, "Welsch", 1 - np.exp(-(grid**2) / (2 * 1.5**2))),
        (INK, "Tukey", rho_tukey(grid, 3.0) / 2.0),
    ]
    axes = panels(
        fig,
        2,
        titles=["convex", "non-convex"],
        colors=[BLUE, RED],
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.24, wspace=0.18),
    )
    for ax, family in zip(axes, (convex, nonconvex)):
        for color, name, values in family:
            ax.plot(grid, values, color=color, lw=2.4,
                    ls="--" if name == "least squares" else "-",
                    alpha=0.6 if name == "least squares" else 1.0)
            if name != "least squares":
                ax.text(4.8, values[-1], name, color=color, fontsize=12,
                        va="center", ha="left")
        ax.text(2.0, 5.2, "least squares", color=MUTED, fontsize=11.5, ha="right")
        ax.set_xlim(-4.6, 7.4)
        ax.set_ylim(0, 5.6)
        ax.set_xlabel(r"residual $e$")
        ax.set_yticks([])
        despine(ax, keep=("bottom",))
    caption(axes[0], "Dominated by large residuals")
    caption(axes[1], "Flat tails")


@figure("eq_stationarity")
def eq_stationarity(fig):
    """Why a derivative of rho shows up at all."""
    ax = canvas(fig)
    plot = fig.add_axes([0.06, 0.22, 0.34, 0.56])
    grid = np.linspace(-5, 5, 500)
    plot.plot(grid, rho_huber(grid, 1.5), color=INK, lw=2.6)
    for e, color in ((0.8, GREEN), (3.4, RED)):
        slope = psi_huber(np.array([e]), 1.5)[0]
        base = rho_huber(np.array([e]), 1.5)[0]
        seg = np.linspace(e - 1.1, e + 1.1, 2)
        plot.plot(seg, base + slope * (seg - e), color=color, lw=2.0)
        plot.plot([e], [base], "o", color=color, ms=8)
        plot.annotate(
            r"slope $\dot\rho(e) = %.1f$" % slope,
            xy=(e, base),
            xytext=(e - 2.6, base + 1.5),
            color=color,
            fontsize=11,
            arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2),
        )
    plot.set_xlabel(r"residual $e$")
    plot.set_ylabel(r"$\rho(e)$")
    plot.set_ylim(-0.3, 5.2)
    despine(plot, keep=("bottom", "left"))

    ax.text(4.35, 3.35, r"$\dot\rho(e) = \mathrm{d}\rho/\mathrm{d}e$",
            ha="left", va="center", color=MUTED, fontsize=12.5)
    ax.text(4.35, 2.78, "Set gradient to zero:", ha="left",
            va="center", color=INK, fontsize=12.5)
    ax.text(4.35, 2.20, r"$\frac{\partial}{\partial \beta}"
                        r"\sum_i \rho(y_i - x_i'^{T}\beta)"
                        r" \;=\; -\sum_i \dot\rho(e_i)\, x_i'$",
            ha="left", va="center", color=GREEN, fontsize=16)
    # ax.plot([4.35, 8.70], [1.72, 1.72], color=GRID, lw=1.2)
    ax.text(4.35, 1.40, "least squares:",
            ha="left", va="center", color=MUTED, fontsize=12)
    ax.text(4.35, 0.88, r"$\rho(e) = \frac{e^2}{2}"
                        r"\;\Rightarrow\; \dot\rho(e) = e"
                        r"\;\Rightarrow\; \text{ set } \sum_i e_i\, x_i' = 0$",
            ha="left", va="center", color=BLUE, fontsize=15)


@figure("eq_weight")
def eq_weight(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.42, r"Stationarity condition: "
                         r"$\sum_i \dot\rho(e_i)\, x_i' = 0$",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(W / 2, 2.72, r"$\dot\rho(e_i) \;=\; \omega(e_i)\; e_i$",
            ha="center", va="center", color=INK, fontsize=22)
    ax.text(W / 2, 2.20, "split the slope into (a weight) × (the residual)",
            ha="center", va="center", color=MUTED, fontsize=12)
    equation(
        ax,
        r"$\omega(e_i) \;=\; \frac{\dot\rho(e_i)}{e_i} \;\in\; [0, +\infty]$",
        y=1.48,
        size=24,
        color=GREEN,
    )
    ax.text(
        W / 2,
        0.80,
        r"$\sum_i \omega(e_i)\, e_i\, x_i' = 0$ is a least squares problem, with one weight per point",
        ha="center",
        va="center",
        color=INK,
        fontsize=13,
    )
    ax.text(2.45, 0.30, r"least squares:  $\omega \equiv 1$", ha="center",
            va="center", color=MUTED, fontsize=12.5)
    ax.text(6.35, 0.30, "robust:  ω falls as |e| grows", ha="center", va="center",
            color=GREEN, fontsize=12.5)


@figure("psi_and_weights")
def psi_and_weights(fig):
    grid = np.linspace(-8, 8, 700)
    curves = [
        (MUTED, "least squares", grid, np.ones_like(grid)),
        (BLUE, "Huber", psi_huber(grid, 1.5), w_huber(grid, 1.5)),
        (RED, "Tukey", psi_tukey(grid, 4.0), w_tukey(grid, 4.0)),
    ]
    axes = panels(
        fig,
        2,
        titles=[r"influence   $\psi(e) = \dot\rho(e)$",
                r"weight   $\omega(e) = \dot\rho(e)/e$"],
        colors=[INK, GREEN],
        gridspec_kw=dict(left=0.06, right=0.97, top=0.78, bottom=0.26, wspace=0.20),
    )
    for color, name, psi, w in curves:
        style = dict(lw=2.6, color=color, ls="--" if color is MUTED else "-",
                     alpha=0.7 if color is MUTED else 1.0)
        axes[0].plot(grid, psi, **style)
        axes[1].plot(grid, w, **style)
    axes[0].set_ylim(-5, 5)
    axes[0].axhline(0, color=GRID, lw=1.0)
    axes[1].set_ylim(-0.1, 1.25)
    for ax in axes:
        ax.set_xlabel(r"residual $e$")
        despine(ax, keep=("bottom", "left"))
    for i, (color, name, _, _) in enumerate(curves):
        axes[1].text(0.70, 0.62 - i * 0.11, name, transform=axes[1].transAxes,
                     color=color, fontsize=12)
    axes[0].annotate("unbounded", xy=(4.3, 4.3), xytext=(-0.6, 4.4), color=MUTED,
                     fontsize=11, va="center",
                     arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.2))
    axes[0].annotate("bounded", xy=(6.6, 1.5), xytext=(6.6, 3.4), color=BLUE,
                     fontsize=11, ha="center",
                     arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.2))
    axes[0].annotate("redescending", xy=(6.0, 0.0), xytext=(4.4, -3.6), color=RED,
                     fontsize=11, ha="center",
                     arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.2))
    fig.text(
        0.5,
        0.925,
        r"point $i$ pushes the fit through the term $\psi(e_i)\,x_i'$",
        ha="center",
        color=MUTED,
        fontsize=12.5,
    )
    caption(axes[0], "residual pull strength")


@figure("influence_demo")
def influence_demo(fig):
    """The influence function, measured: drag one point and watch the slope."""
    rng = np.random.default_rng(31)
    x = np.linspace(-3, 3, 17)
    y = 0.6 + 1.1 * x + rng.normal(0, 0.45, x.size)
    moved = 13                      # the point we drag
    positions = np.linspace(-12, 14, 70)

    def slope(values, weight_fn):
        if weight_fn is None:
            return _fit(x, values)[1]
        beta, _, _ = _irls(x, values, weight_fn)
        return beta[1]

    methods = [
        (MUTED, "least squares", None),
        (BLUE, "Huber", lambda e: w_huber(e, 1.345)),
        (RED, "Tukey", lambda e: w_tukey(e, 4.685)),
    ]
    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.24, wspace=0.24),
    )

    ax = axes[0]
    grid = np.linspace(-3.4, 3.4, 10)
    ax.scatter(np.delete(x, moved), np.delete(y, moved), s=24, color=INK, alpha=0.6,
               edgecolor="white", linewidth=0.5, zorder=3)
    for target, shade in ((y[moved], 1.0), (9.0, 0.7), (-7.0, 0.7)):
        values = y.copy()
        values[moved] = target
        b = _fit(x, values)
        ax.plot(grid, b[0] + b[1] * grid, color=GOLD, lw=2.2, alpha=shade)
        rb, _, _ = _irls(x, values, lambda e: w_huber(e, 1.345))
        ax.plot(grid, rb[0] + rb[1] * grid, color=BLUE, lw=2.0, ls="--", alpha=shade)
        ax.plot([x[moved]], [target], "o", color=INK, ms=9, alpha=shade, zorder=4)
    ax.set_xlim(-3.5, 3.9)
    ax.set_ylim(-8.5, 11.5)
    ax.set_xticks([])
    ax.set_yticks([])
    despine(ax)
    ax.set_title("Influence of a point on the fit", pad=10, fontsize=13.5)

    ax = axes[1]
    for color, name, weight_fn in methods:
        slopes = []
        for target in positions:
            values = y.copy()
            values[moved] = target
            slopes.append(slope(values, weight_fn))
        ax.plot(positions, slopes, color=color, lw=2.6,
                ls="--" if weight_fn is None else "-",
                alpha=0.75 if weight_fn is None else 1.0)
        if weight_fn is None:
            ax.text(12.5, 1.3, name, color=color,
                    fontsize=11.5, ha="left", va="bottom")
        else:
            bump = 0.035 if name == "Huber" else -0.035
            ax.text(positions[-1] + 0.4, slopes[-1] + bump, name, color=color,
                    fontsize=11.5, va="center")
    ax.axhline(1.1, color=GRID, lw=1.4, ls=":")
    ax.set_xlim(-12, 18)
    ax.set_xlabel("$y$ value")
    ax.set_ylabel(r"slope $\hat\beta_1$")
    despine(ax, keep=("bottom", "left"))
    ax.set_title("Influence", pad=10, fontsize=13.5)


# ==========================================================================
# 4. robust regression — IRLS
# ==========================================================================
def _mad_scale(e):
    scale = 1.4826 * np.median(np.abs(e - np.median(e)))
    return max(scale, 1e-6)


def _irls(x, y, weight_fn, iters=12, beta=None):
    """Iteratively reweighted least squares on a single-feature design."""
    X = np.c_[np.ones_like(x), x]
    if beta is None:
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
    history = [beta.copy()]
    weights = np.ones_like(y)
    for _ in range(iters):
        e = y - X @ beta
        weights = weight_fn(e / _mad_scale(e))
        root = np.sqrt(weights)
        beta = np.linalg.lstsq(X * root[:, None], y * root, rcond=None)[0]
        history.append(beta.copy())
    return beta, weights, history


@figure("weights_on_data")
def weights_on_data(fig):
    rng = np.random.default_rng(7)
    x, y, x_out, y_out = _outlier_data(rng, n_out=2)
    X = np.r_[x, x_out]
    Y = np.r_[y, y_out]
    ls = _fit(X, Y)
    beta, weights, _ = _irls(X, Y, lambda e: w_huber(e, 1.345))
    grid = np.linspace(-3.4, 3.4, 10)

    ax = fig.subplots(
        gridspec_kw=dict(left=0.06, right=0.78, top=0.88, bottom=0.18)
    )
    ax.scatter(
        X, Y, s=30 + 150 * weights, color=BLUE, alpha=0.25 + 0.7 * weights,
        edgecolor="white", linewidth=0.6, zorder=3
    )
    ax.plot(grid, ls[0] + ls[1] * grid, color=RED, lw=2.6, label="least squares")
    ax.plot(grid, beta[0] + beta[1] * grid, color=GREEN, lw=2.6, label="Huber")
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-6.5, 6.5)
    ax.set_xticks([])
    ax.set_yticks([])
    despine(ax)
    ax.legend(loc="lower left", fontsize=11.5)
    for xo, yo, wo in zip(X[-2:], Y[-2:], weights[-2:]):
        ax.annotate(
            r"$\omega = %.2f$" % wo,
            xy=(xo, yo),
            xytext=(xo + (0.95 if yo > 0 else -0.95), yo + (0.55 if yo > 0 else -0.55)),
            color=RED,
            fontsize=11.5,
            ha="center",
            arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.2),
        )

    side = fig.add_axes([0.80, 0.18, 0.19, 0.70])
    side.axis("off")
    side.text(0.0, 0.52, "All points get\nsame weights", color=GREEN, fontsize=12.5,
              weight="bold", va="center")
    side.text(0.0, 0.31, "Far points get\nsmall weights", color=RED, fontsize=12.5,
              weight="bold", va="center")
    side.text(0.0, 0.10, "No handcrafted\noutlier detection", color=MUTED, fontsize=11,
              va="center", linespacing=1.6)


@figure("eq_irls")
def eq_irls(fig):
    ax = canvas(fig)
    lines = [
        (r"$\sum_i \dot\rho(e_i)\, x_i' = 0$", INK, 3.00,
         "minimiser"),
        (r"$\sum_i \omega(e_i)\, e_i\, x_i' = 0$", GREEN, 2.15,
         r"since $\dot\rho(e) = \omega(e)\, e$"),
        (r"$\min_\beta\ \sum_i \omega(e_i)\, e_i^2"
         r"\;=\;\min_\beta\ \|W^{1/2}(X\beta - y)\|^2$", BLUE, 1.25,
         "weighted least squares problem"),
    ]
    for text, color, y, label in lines:
        ax.text(2.95, y, text, ha="center", va="center", color=color, fontsize=17)
        ax.text(6.25, y, label, ha="left", va="center", color=MUTED, fontsize=12)
    arrow(ax, (2.95, 2.78), (2.95, 2.45), color=GRID)
    arrow(ax, (2.95, 1.92), (2.95, 1.58), color=GRID)
    # note(ax, "the hard problem became a familiar one with weights in front", y=0.50)


def _box_edge(centre, half, towards, pad=0.08):
    """Where the segment centre -> towards leaves a box, plus a small gap."""
    d = np.asarray(towards, float) - np.asarray(centre, float)
    if abs(d[0]) < 1e-9 and abs(d[1]) < 1e-9:
        return np.asarray(centre, float)
    scale = min(
        half[0] / abs(d[0]) if abs(d[0]) > 1e-9 else np.inf,
        half[1] / abs(d[1]) if abs(d[1]) > 1e-9 else np.inf,
    )
    return np.asarray(centre, float) + d * scale + d / np.linalg.norm(d) * pad


@figure("irls_loop")
def irls_loop(fig):
    ax = canvas(fig)
    nodes = [
        (BLUE, (1.45, 2.05), (1.95, 0.72), r"$\beta^k$", "estimate"),
        (GREEN, (4.50, 3.05), (2.45, 0.68), r"$e^k = y - X\beta^k$",
         "residuals"),
        (GOLD, (7.45, 2.05), (2.70, 0.68), r"$W^k = \mathrm{diag}(\omega(e^k))$",
         "weights"),
        (PURPLE, (4.50, 1.08), (3.75, 0.68),
         r"$\beta^{k+1} = (X^{T}W^kX)^{-1}X^{T}W^ky$", "new estimate"),
    ]
    for color, centre, size, label, sub in nodes:
        box(ax, centre[0] - size[0] / 2, centre[1] - size[1] / 2, size[0], size[1],
            color, "", fill="white")
        ax.text(centre[0], centre[1], label, ha="center", va="center", color=color,
                fontsize=13)
        below = centre[1] - size[1] / 2 - 0.20
        ax.text(centre[0], below, sub, ha="center", va="center", color=MUTED,
                fontsize=11)

    for i in range(len(nodes)):
        _, centre_a, size_a, _, _ = nodes[i]
        _, centre_b, size_b, _, _ = nodes[(i + 1) % len(nodes)]
        half_a = (size_a[0] / 2, size_a[1] / 2)
        half_b = (size_b[0] / 2, size_b[1] / 2)
        tail = _box_edge(centre_a, half_a, centre_b, pad=0.10)
        head = _box_edge(centre_b, half_b, centre_a, pad=0.10)
        ax.add_patch(
            FancyArrowPatch(
                tail,
                head,
                arrowstyle="-|>",
                mutation_scale=15,
                linewidth=2.0,
                color=MUTED,
                connectionstyle="arc3,rad=-0.16",
                shrinkA=0,
                shrinkB=0,
                zorder=1,
            )
        )
    note(ax, "weights need residuals, residuals need estimate [...]", y=0.20)


@figure("irls_steps")
def irls_steps(fig):
    rng = np.random.default_rng(7)
    x, y, x_out, y_out = _outlier_data(rng, n_out=2)
    X = np.r_[x, x_out]
    Y = np.r_[y, y_out]
    grid = np.linspace(-3.4, 3.4, 10)
    design = np.c_[np.ones_like(X), X]
    beta = np.linalg.lstsq(design, Y, rcond=None)[0]

    axes = fig.subplots(
        1,
        4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.82, bottom=0.18, wspace=0.10),
    )
    titles = ["k = 0   least squares", "k = 1", "k = 2", "k = 8   converged"]
    steps = [0, 1, 2, 8]
    weights = np.ones_like(Y)
    states = {}
    for k in range(9):
        if k in steps:
            states[k] = (beta.copy(), weights.copy())
        e = Y - design @ beta
        weights = w_huber(e / _mad_scale(e), 1.345)
        root = np.sqrt(weights)
        beta = np.linalg.lstsq(design * root[:, None], Y * root, rcond=None)[0]

    for ax, k, title in zip(axes, steps, titles):
        b, w = states[k]
        ax.scatter(X, Y, s=18 + 90 * w, color=BLUE, alpha=0.25 + 0.7 * w,
                   edgecolor="white", linewidth=0.5, zorder=3)
        ax.plot(grid, b[0] + b[1] * grid, color=INK, lw=2.4)
        ax.set_xlim(-3.5, 3.5)
        ax.set_ylim(-6.5, 6.5)
        ax.set_xticks([])
        ax.set_yticks([])
        despine(ax)
        ax.set_title(title, pad=8, fontsize=12.5)
        ax.text(0.04, 0.05, r"$\hat\beta_1 = %.2f$" % b[1], transform=ax.transAxes,
                color=INK, fontsize=11.5)
    fig.text(
        0.5,
        0.045,
        "pale & small points have smaller weights",
        ha="center",
        color=MUTED,
        fontsize=12,
    )


@figure("irls_algorithm")
def irls_algorithm(fig):
    ax = canvas(fig)
    box(ax, 0.55, 0.70, 4.35, 2.70, BLUE, "", fill="white")
    ax.text(2.72, 3.10, "IRLS", ha="center", va="center", color=BLUE, fontsize=15,
            weight="bold")
    steps = [
        r"initialise $\beta^0$: least squares with no weights",
        r"$e^{k-1} = y - X\beta^{k-1}$",
        r"$W^k = \mathrm{diag}\left[\omega(e^{k-1}_i)\right]$",
        r"$\beta^k = (X^{T}W^kX)^{-1}X^{T}W^ky$",
        "stop when β stops moving",
    ]
    for i, step in enumerate(steps):
        y = 2.65 - i * 0.44
        ax.text(0.85, y, "·" if i in (0, 4) else f"{i}.", ha="left", va="center",
                color=MUTED, fontsize=12)
        ax.text(1.25, y, step, ha="left", va="center", color=INK, fontsize=12.5)
    column(
        ax,
        5.35,
        3.30,
        3.3,
        "costs",
        [
            "one weighted least squares per pass",
            "usually a few passes needed",
        ],
        GREEN,
        item_size=11.5,
        title_size=12.5,
    )
    ax.text(
        5.35,
        1.15,
        "convex ρ: global solution\n"
        "non-convex ρ: starting point matters",
        color=RED,
        fontsize=11.5,
        va="top",
        linespacing=1.7,
    )


@figure("mm_idea")
def mm_idea(fig):
    delta = 1.6

    def rho(e):
        return 1 - np.exp(-(e**2) / (2 * delta**2))

    def drho(e):
        return e / delta**2 * np.exp(-(e**2) / (2 * delta**2))

    def omega(e):
        return np.exp(-(e**2) / (2 * delta**2)) / delta**2

    grid = np.linspace(-6, 6, 600)
    axes = panels(
        fig,
        2,
        titles=["approximattion of ρ with a quadratic that sits above", "next iteration"],
        colors=[GOLD, GREEN],
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.24, wspace=0.20),
    )

    def majorant(e, at):
        return rho(at) + drho(at) * (e - at) + 0.5 * omega(abs(at)) * (e - at) ** 2

    ax = axes[0]
    at = 3.4
    ax.plot(grid, rho(grid), color=INK, lw=2.6)
    ax.plot(grid, majorant(grid, at), color=GOLD, lw=2.2, ls="--")
    ax.plot([at], [rho(at)], "o", color=GOLD, ms=10)
    ax.annotate("they touch here", xy=(at, rho(at)), xytext=(at - 0.4, 1.55),
                color=GOLD, fontsize=11.5, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=1.2))
    ax.text(0.03, 0.92, r"$\rho$", transform=ax.transAxes, color=INK, fontsize=15)
    ax.set_ylim(-0.1, 1.9)
    ax.set_xlabel(r"residual $e$")
    ax.set_yticks([])
    despine(ax, keep=("bottom",))

    ax = axes[1]
    ax.plot(grid, rho(grid), color=INK, lw=2.6)
    point = 4.6
    for color in (GOLD, GREEN):
        ax.plot(grid, majorant(grid, point), color=color, lw=1.8, ls="--", alpha=0.9)
        ax.plot([point], [rho(point)], "o", color=color, ms=9)
        nxt = point - drho(point) / omega(abs(point))
        ax.annotate(
            "",
            xy=(nxt, rho(nxt)),
            xytext=(point, rho(point)),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8),
        )
        point = nxt
    ax.set_ylim(-0.1, 1.9)
    ax.set_xlabel(r"residual $e$")
    ax.set_yticks([])
    despine(ax, keep=("bottom",))


@figure("eq_mm")
def eq_mm(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.40, r"let $\rho(x) = \varphi(|x|)$, need",
            ha="center", va="center", color=MUTED, fontsize=13)
    conditions = [
        r"$\varphi$ differentiable on $]0, +\infty[$",
        r"$\varphi(\sqrt{\cdot})$ concave on $]0, +\infty[$",
        r"$\dot\varphi(x) \geq 0$",
        r"$\lim_{x \to 0^{+}} \omega(x) = \dot\varphi(x)/x \in \mathbb{R}$",
    ]
    for i, text in enumerate(conditions):
        x = 0.70 + (i % 2) * 4.30
        y = 2.80 - (i // 2) * 0.55
        ax.text(x, y, "·", ha="left", va="center", color=MUTED, fontsize=14)
        ax.text(x + 0.25, y, text, ha="left", va="center", color=INK, fontsize=13)
    ax.text(
        W / 2,
        1.35,
        r"$\rho(x) \;\leq\; \rho(y) + \dot\rho(y)(x-y) + "
        r"\frac{1}{2}\,\omega(|y|)\,(x-y)^2$",
        ha="center",
        va="center",
        color=GREEN,
        fontsize=19,
    )
    note(ax, r"$\rho$ has a quadratic lower bound minimised by IRLS step",
         y=0.55)


@figure("delta_meaning")
def delta_meaning(fig):
    """What the delta in Huber's loss actually marks."""
    delta = 1.5
    grid = np.linspace(-5, 5, 700)
    panels_ = [
        (INK, r"the loss  $\rho(e)$", rho_huber(grid, delta),
         "squared inside, straight outside"),
        (BLUE, r"the influence  $\psi(e)$", psi_huber(grid, delta),
         r"a point can never push harder than $\delta$"),
        (GREEN, r"the weight  $\omega(e)$", w_huber(grid, delta),
         r"full weight inside, $\delta / |e|$ outside"),
    ]
    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.05, right=0.98, top=0.78, bottom=0.26, wspace=0.22),
    )
    for ax, (color, title, values, remark) in zip(axes, panels_):
        ax.axvspan(-delta, delta, color=GOLD, alpha=0.10)
        ax.plot(grid, values, color=color, lw=2.8)
        for sign in (-1, 1):
            ax.axvline(sign * delta, color=GOLD, lw=1.6, ls="--")
        ax.set_xticks([-delta, 0, delta])
        ax.set_xticklabels([r"$-\delta$", "0", r"$\delta$"], fontsize=12)
        ax.set_yticks([])
        ax.set_xlabel(r"residual $e$", labelpad=1)
        despine(ax, keep=("bottom",))
        ax.set_title(title, color=color, pad=10, fontsize=13)
        caption(ax, remark)
    # axes[0].text(0.0, rho_huber(np.array([4.4]), delta)[0], "ordinary", color=GOLD,
    #              fontsize=11.5, ha="center")
    # axes[0].text(3.3, rho_huber(np.array([2.2]), delta)[0], "large", color=RED,
    #              fontsize=11.5, ha="center")
    fig.text(
        0.5,
        0.935,
        r"$\delta$ is the residual size at which a point stops counting as ordinary",
        ha="center",
        color=MUTED,
        fontsize=12.5,
    )


@figure("delta_scale")
def delta_scale(fig):
    """Delta only means something once the residuals are in units of scale."""
    rng = np.random.default_rng(5)
    residuals = rng.normal(0, 4.0, 400)      # a dataset measured in euros, say
    residuals[:8] += rng.normal(0, 30, 8)    # a few outliers
    scale = _mad_scale(residuals)
    delta = 1.345

    axes = fig.subplots(
        1,
        3,
        gridspec_kw=dict(left=0.05, right=0.98, top=0.80, bottom=0.26, wspace=0.26),
    )

    ax = axes[0]
    ax.hist(residuals, bins=50, color=MUTED, alpha=0.45, edgecolor="none")
    for sign in (-1, 1):
        ax.axvline(sign * delta, color=RED, lw=2.0)
    ax.set_xlim(-25, 25)
    ax.set_yticks([])
    ax.set_xlabel("residuals, in euros")
    despine(ax, keep=("bottom",))
    ax.set_title(r"$\delta = 1.345$ on the raw residuals", color=RED, pad=10,
                 fontsize=13)
    caption(ax, "almost every point is declared an outlier")

    ax = axes[1]
    ax.hist(residuals / scale, bins=50, color=BLUE, alpha=0.45, edgecolor="none")
    for sign in (-1, 1):
        ax.axvline(sign * delta, color=GREEN, lw=2.0)
    ax.set_xlim(-6.2, 6.2)
    ax.set_yticks([])
    ax.set_xlabel(r"residuals, divided by $\hat\sigma$")
    despine(ax, keep=("bottom",))
    ax.set_title(r"$\delta = 1.345$ after scaling", color=GREEN, pad=10,
                 fontsize=13)
    caption(ax, "now it marks the edge of the bulk")

    ax = axes[2]
    ax.axis("off")
    ax.text(0.0, 0.96, "a robust scale, from the data", transform=ax.transAxes,
            color=INK, fontsize=12.5, va="center", weight="bold")
    ax.text(0.0, 0.80, r"$\hat\sigma = 1.4826 \times \mathrm{MAD}$",
            transform=ax.transAxes, color=BLUE, fontsize=13, va="center")
    ax.text(0.0, 0.67, r"$\mathrm{MAD} = \mathrm{median}_i\,"
                       r"|e_i - \mathrm{median}(e)|$",
            transform=ax.transAxes, color=MUTED, fontsize=10.5, va="center")
    ax.text(0.0, 0.55, "outliers cannot inflate it", transform=ax.transAxes,
            color=MUTED, fontsize=11, va="center")
    ax.text(0.0, 0.37, "usual choices", transform=ax.transAxes, color=INK,
            fontsize=12.5, va="center", weight="bold")
    for i, (color, text) in enumerate(
        [(BLUE, r"Huber  $\delta = 1.345$"), (RED, r"Tukey  $\delta = 4.685$")]
    ):
        ax.text(0.0, 0.26 - i * 0.13, text, transform=ax.transAxes, color=color,
                fontsize=12.5, va="center")
    ax.text(0.0, -0.06, "95 % as efficient as least squares,\nif the noise is Gaussian",
            transform=ax.transAxes, color=MUTED, fontsize=10.5, va="top",
            linespacing=1.6)


@figure("tuning_delta")
def tuning_delta(fig):
    rng = np.random.default_rng(7)
    x, y, x_out, y_out = _outlier_data(rng, n_out=2)
    X = np.r_[x, x_out]
    Y = np.r_[y, y_out]
    grid = np.linspace(-3.4, 3.4, 10)

    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.24, wspace=0.24),
    )
    ax = axes[0]
    ax.scatter(X, Y, s=24, color=MUTED, alpha=0.8, edgecolor="white", linewidth=0.5)
    for delta, color, label in [
        (0.2, GREEN, r"$\delta = 0.2$"),
        (1.345, BLUE, r"$\delta = 1.345$"),
        (20.0, RED, r"$\delta = 20$"),
    ]:
        beta, _, _ = _irls(X, Y, lambda e, d=delta: w_huber(e, d))
        ax.plot(grid, beta[0] + beta[1] * grid, color=color, lw=2.4, label=label)
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-6.5, 6.5)
    ax.set_xticks([])
    ax.set_yticks([])
    despine(ax)
    ax.legend(loc="upper left", fontsize=11)
    caption(ax, "large δ walks back to least squares")

    ax = axes[1]
    deltas = np.linspace(0.1, 12, 60)
    slopes = []
    for delta in deltas:
        beta, _, _ = _irls(X, Y, lambda e, d=delta: w_huber(e, d))
        slopes.append(beta[1])
    ax.plot(deltas, slopes, color=PURPLE, lw=2.6)
    ax.axhline(1.1, color=INK, lw=1.8, ls="--")
    ax.text(11.6, 1.12, "the truth", color=INK, fontsize=11, ha="right", va="bottom")
    ax.axvline(1.345, color=BLUE, lw=1.6, ls=":")
    ax.text(1.5, min(slopes) + 0.02, "1.345", color=BLUE, fontsize=11)
    ax.set_xlabel(r"Huber's $\delta$")
    ax.set_ylabel(r"$\hat\beta_1$")
    despine(ax, keep=("bottom", "left"))
    caption(ax, "δ is measured in units of the residual scale")


@figure("robust_map")
def robust_map(fig):
    ax = canvas(fig)
    stages = [
        (BLUE, "least squares", r"$\rho(e) = e^2/2$"),
        (RED, "outlier(s)", "allowed by the fit"),
        (GREEN, "choice of ρ", r"$\omega(e) = \dot\rho(e)/e$"),
        (PURPLE, "IRLS", "weighted least squares\nrepeated"),
    ]
    w, gap = 1.95, 0.30
    x0 = (W - (4 * w + 3 * gap)) / 2
    for i, (color, title, sub) in enumerate(stages):
        x = x0 + i * (w + gap)
        box(ax, x, 1.75, w, 1.15, color, "")
        ax.text(x + w / 2, 2.62, title, ha="center", va="center", color=color,
                fontsize=13, weight="bold")
        ax.text(x + w / 2, 2.12, sub, ha="center", va="center", color=INK,
                fontsize=11, linespacing=1.6)
        if i:
            arrow(ax, (x - gap + 0.04, 2.32), (x - 0.06, 2.32))

# ==========================================================================
# 5. logistic regression — the same machinery, for labels
# ==========================================================================
def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def _blobs(rng, n=120, gap=1.6, spread=1.0):
    """Two classes in 2D, with labels in {0, 1}."""
    a = rng.normal([-gap, -0.4], spread, (n, 2))
    b = rng.normal([gap, 0.5], spread, (n, 2))
    X = np.vstack([a, b])
    y = np.r_[np.zeros(n), np.ones(n)]
    return X, y


def _logistic_irls(X, y, iters=8):
    """Newton / IRLS steps for logistic regression; keeps every iterate."""
    design = np.c_[np.ones(len(X)), X]
    beta = np.zeros(design.shape[1])
    history = [beta.copy()]
    for _ in range(iters):
        p = _sigmoid(design @ beta)
        w = np.clip(p * (1 - p), 1e-6, None)
        gram = design.T @ (design * w[:, None]) + 1e-8 * np.eye(design.shape[1])
        beta = beta + np.linalg.solve(gram, design.T @ (y - p))
        history.append(beta.copy())
    return beta, history


def _logistic_loss(design, y, beta):
    z = design @ beta
    return float(np.sum(np.logaddexp(0, z) - y * z))


@figure("logistic_setting")
def logistic_setting(fig):
    rng = np.random.default_rng(3)
    axes = panels(
        fig,
        2,
        titles=["linearly separable", "reality"],
        colors=[GREEN, RED],
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.24, wspace=0.18),
    )
    for ax, gap, spread in ((axes[0], 2.4, 0.75), (axes[1], 1.1, 1.05)):
        X, y = _blobs(rng, 90, gap=gap, spread=spread)
        beta, _ = _logistic_irls(X, y)
        gx = np.linspace(-5.5, 5.5, 10)
        ax.plot(gx, -(beta[0] + beta[1] * gx) / beta[2], color=INK, lw=2.4)
        for k, color in enumerate((BLUE, RED)):
            ax.scatter(X[y == k, 0], X[y == k, 1], s=18, color=color, alpha=0.7,
                       edgecolor="white", linewidth=0.4)
        ax.set_xlim(-5.5, 5.5)
        ax.set_ylim(-4.0, 4.0)
        ax.set_xticks([])
        ax.set_yticks([])
        despine(ax)
    caption(axes[0], "a hyperplane gets every point right")
    caption(axes[1], "no perfect linear model")


@figure("eq_logodds")
def eq_logodds(fig):
    ax = canvas(fig)
    equation(
        ax,
        r"$\log \frac{\Pr(G = 1 \mid X = x)}{1 - \Pr(G = 1 \mid X = x)}"
        r"\;=\; \beta_0 + \beta^{T}x$",
        y=2.55,
        size=22,
    )
    ax.text(2.45, 1.62, "the log-odds", ha="center", va="center", color=GREEN,
            fontsize=13)
    ax.text(2.45, 1.28, r"anything in $\mathbb{R}$", ha="center", va="center",
            color=MUTED, fontsize=11.5)
    ax.text(6.55, 1.62, "a linear score", ha="center", va="center", color=BLUE,
            fontsize=13)
    ax.text(6.55, 1.28, r"anything in $\mathbb{R}$", ha="center", va="center",
            color=MUTED, fontsize=11.5)
    arrow(ax, (2.45, 1.82), (3.35, 2.25), color=GREEN, lw=1.4)
    arrow(ax, (6.55, 1.82), (6.15, 2.25), color=BLUE, lw=1.4)
    ax.text(
        W / 2,
        0.62,
        r"no $\Pr(x \mid G)$, no prior: unlike LDA or naive Bayes, "
        r"nothing is assumed about how $x$ is spread",
        ha="center",
        va="center",
        color=INK,
        fontsize=12.5,
    )


@figure("sigmoid")
def sigmoid(fig):
    rng = np.random.default_rng(9)
    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.07, right=0.97, top=0.84, bottom=0.24, wspace=0.24),
    )

    ax = axes[0]
    z = np.linspace(-6, 6, 400)
    ax.plot(z, _sigmoid(z), color=GREEN, lw=2.8)
    ax.axhline(0.5, color=GRID, lw=1.2, ls="--")
    ax.axvline(0.0, color=INK, lw=1.8)
    ax.text(-5.8, 0.55, "p = 0.5", color=MUTED, fontsize=11.5)
    ax.set_xlabel(r"the score  $\beta_0 + \beta^{T}x$")
    ax.set_ylabel(r"$\Pr(G=1 \mid x)$")
    ax.set_title(r"$p = \sigma(\beta_0 + \beta^{T}x)"
                 r" = \frac{1}{1 + e^{-(\beta_0 + \beta^{T}x)}}$",
                 color=GREEN, pad=12, fontsize=14)
    caption(ax, "inverse of the log-odds")
    # caption(ax, "inverse of the log-odds; cannot leave [0, 1]")

    ax = axes[1]
    x = np.r_[rng.normal(-1.3, 1.6, 40), rng.normal(1.3, 1.6, 40)]
    y = np.r_[np.zeros(40), np.ones(40)]
    beta, _ = _logistic_irls(x[:, None], y)
    grid = np.linspace(-5, 5, 300)
    ax.plot(grid, _sigmoid(beta[0] + beta[1] * grid), color=GREEN, lw=2.8)
    for k, color in enumerate((BLUE, RED)):
        ax.plot(x[y == k], y[y == k], "|", color=color, ms=16, mew=2, alpha=0.8)
    cut = -beta[0] / beta[1]
    ax.axvline(cut, color=INK, lw=1.8, ls="--")
    # ax.text(cut + 0.15, 0.35, "decide here", color=INK, fontsize=11.5)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel("probability / label")
    ax.set_title("fitted to data", pad=12, fontsize=14)
    # caption(ax, "the labels are 0 and 1")


@figure("eq_softmax")
def eq_softmax(fig):
    ax = canvas(fig)
    ax.text(W / 2, 3.45, r"$K$ classes:  pick one as the reference, ",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(
        W / 2,
        2.75,
        r"$\log \frac{\Pr(G=k \mid x)}{\Pr(G=K \mid x)}"
        r" \;=\; \beta_{k0} + \beta_k^{T}x, \qquad k = 1,\dots,K-1$",
        ha="center",
        va="center",
        color=INK,
        fontsize=18,
    )
    ax.text(
        W / 2,
        1.70,
        r"$\Pr(G=k \mid x) = \frac{\exp(\beta_{k0} + \beta_k^{T}x)}"
        r"{1 + \sum_{\ell=1}^{K-1}\exp(\beta_{\ell 0} + \beta_\ell^{T}x)}"
        r"\qquad\quad"
        r"\Pr(G=K \mid x) = \frac{1}"
        r"{1 + \sum_{\ell=1}^{K-1}\exp(\beta_{\ell 0} + \beta_\ell^{T}x)}$",
        ha="center",
        va="center",
        color=GREEN,
        fontsize=14,
    )
    ax.text(W / 2, 0.80, r"classify with  $\hat{k} = \arg\max_k \Pr(G=k \mid x)$",
            ha="center", va="center", color=INK, fontsize=15)
    note(ax, "the probabilities add up to one by construction", y=0.30)


@figure("logistic_loss")
def logistic_loss(fig):
    axes = fig.subplots(
        1,
        2,
        gridspec_kw=dict(left=0.07, right=0.97, top=0.84, bottom=0.24, wspace=0.26),
    )

    ax = axes[0]
    m = np.linspace(-3, 3, 500)
    ax.step(m, (m < 0).astype(float), color=INK, lw=2.2, where="mid")
    ax.plot(m, np.log1p(np.exp(-m)) / np.log(2), color=GREEN, lw=2.8)
    ax.plot(m, (1 - m) ** 2 / 4, color=RED, lw=2.2, ls="--")
    # ax.plot(m, np.maximum(0, 1 - m), color=MUTED, lw=2.0, ls=":")
    for text, color, pos in [
        ("0 / 1 loss", INK, (-2.6, 1.12)),
        ("logistic", GREEN, (1.1, 0.55)),
        ("squared", RED, (1.7, 0.85)),
        # ("hinge", MUTED, (0.9, 1.35)),
    ]:
        ax.text(*pos, text, color=color, fontsize=11.5)
    ax.set_ylim(-0.1, 2.6)
    ax.set_xlabel(r"margin  $y_i\,\beta^{T}x_i$")
    ax.set_ylabel("loss of one point")
    caption(ax, "smooth & convex")

    ax = axes[1]
    rng = np.random.default_rng(4)
    X, y = _blobs(rng, 60, gap=1.4)
    design = np.c_[np.ones(len(X)), X]
    beta_hat, _ = _logistic_irls(X, y)
    b1, b2 = np.meshgrid(
        np.linspace(beta_hat[1] - 2.6, beta_hat[1] + 2.6, 160),
        np.linspace(beta_hat[2] - 2.6, beta_hat[2] + 2.6, 160),
    )
    loss = np.array(
        [
            _logistic_loss(design, y, np.array([beta_hat[0], a, b]))
            for a, b in zip(b1.ravel(), b2.ravel())
        ]
    ).reshape(b1.shape)
    ax.contourf(b1, b2, loss, levels=16, cmap="Greens_r", alpha=0.9)
    ax.plot([beta_hat[1]], [beta_hat[2]], "o", color=RED, ms=10, mec="white", mew=1.2)
    ax.set_xlabel(r"$\beta_1$")
    ax.set_ylabel(r"$\beta_2$")
    ax.set_title(r"$F(\beta) = \sum_i \log(1 + e^{-y_i \beta^{T}x_i})$",
                 pad=10, fontsize=13.5)
    caption(ax, "global minimum, and gradients pointing at it")


@figure("why_not_least_squares")
def why_not_least_squares(fig):
    rng = np.random.default_rng(17)
    x = np.r_[rng.normal(-1.5, 0.7, 25), rng.normal(1.5, 0.7, 25)]
    y = np.r_[np.zeros(25), np.ones(25)]
    x_far = np.r_[x, [7.5, 8.2]]
    y_far = np.r_[y, [1.0, 1.0]]
    grid = np.linspace(-4, 9, 300)

    axes = panels(
        fig,
        2,
        titles=["a straight line through 0 / 1 labels", "logistic regression"],
        colors=[RED, GREEN],
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.24, wspace=0.22),
    )
    ax = axes[0]
    beta = _fit(x_far, y_far)
    ax.plot(grid, beta[0] + beta[1] * grid, color=RED, lw=2.6)
    ax.axhline(0.5, color=GRID, lw=1.2, ls="--")
    cut = (0.5 - beta[0]) / beta[1]
    ax.axvline(cut, color=RED, lw=1.6, ls=":")
    caption(ax, "predictions below 0 and above 1")

    ax = axes[1]
    b, _ = _logistic_irls(x_far[:, None], y_far)
    ax.plot(grid, _sigmoid(b[0] + b[1] * grid), color=GREEN, lw=2.6)
    ax.axhline(0.5, color=GRID, lw=1.2, ls="--")
    ax.axvline(-b[0] / b[1], color=GREEN, lw=1.6, ls=":")
    caption(ax, "predictions between 0 and 1")

    for ax in axes:
        for k, color in enumerate((BLUE, RED)):
            ax.plot(x_far[y_far == k], y_far[y_far == k], "|", color=color, ms=15,
                    mew=2, alpha=0.8)
        ax.plot([7.5, 8.2], [1.0, 1.0], "o", color=GOLD, ms=8, zorder=4)
        ax.set_xlim(-4, 9)
        ax.set_ylim(-0.45, 1.45)
        ax.set_xticks([])
        ax.set_yticks([0, 0.5, 1])
        despine(ax, keep=("left",))
    axes[0].text(7.8, 1.25, "two far,\nvery obvious points", color=GOLD,
                 fontsize=11, ha="center", va="center", linespacing=1.5)


@figure("eq_logistic_irls")
def eq_logistic_irls(fig):
    """Logistic regression, written next to the robust fit it copies."""
    ax = canvas(fig)
    ax.text(W / 2, 3.52, "IRLS algorithm, with different weights",
            ha="center", va="center", color=MUTED, fontsize=12.5)
    ax.text(3.05, 3.08, "robust regression", ha="center", va="center", color=BLUE,
            fontsize=13.5, weight="bold")
    ax.text(6.75, 3.08, "logistic regression", ha="center", va="center", color=GREEN,
            fontsize=13.5, weight="bold")
    ax.plot([1.35, 8.60], [2.85, 2.85], color=GRID, lw=1.2)
    ax.plot([4.90, 4.90], [0.45, 2.95], color=GRID, lw=1.2)

    rows = [
        (
            "minimise",
            r"$\sum_i \rho(e_i)$",
            r"$\sum_i \log\!\left(1 + e^{[L\beta]_i}\right)$",
            2.40,
        ),
        (
            "weight",
            r"$\omega(e_i) = \dot\rho(e_i)/e_i$",
            r"$\omega([L\beta]_i)$",
            1.60,
        ),
        (
            "one step",
            r"$\beta \leftarrow (X^{T}WX)^{-1}X^{T}Wy$",
            r"$\beta \leftarrow \beta - \Omega(\beta)^{-1}\nabla F(\beta)$",
            0.80,
        ),
    ]
    for label, left, right, y in rows:
        ax.text(1.25, y, label, ha="right", va="center", color=INK, fontsize=12)
        ax.text(3.05, y, left, ha="center", va="center", color=BLUE, fontsize=14)
        ax.text(6.75, y, right, ha="center", va="center", color=GREEN, fontsize=14)

    ax.text(6.75, 2.03, r"$[L\beta]_i = -y_i\,\beta^{T}x_i$   |   "
                        r"$L = -\mathrm{Diag}(y)X$",
            ha="center", va="center", color=MUTED, fontsize=11)
    ax.text(6.75, 0.40, r"$\Omega(\beta) = L^{T}\mathrm{Diag}"
                        r"(\omega(L\beta))\,L$   and   "
                        r"$\nabla F(\beta) = L^{T}\dot{f}(L\beta)$",
            ha="center", va="center", color=MUTED, fontsize=11)
    ax.text(3.05, 0.40, "weighted least squares", ha="center",
            va="center", color=MUTED, fontsize=11)


@figure("logistic_mm")
def logistic_mm(fig):
    grid = np.linspace(-6, 6, 600)

    def f(z):
        return np.logaddexp(0, z)

    def df(z):
        return _sigmoid(z)

    def omega(z):
        z = np.where(np.abs(z) < 1e-6, 1e-6, z)
        return (_sigmoid(z) - 0.5) / z

    axes = panels(
        fig,
        2,
        titles=[r"$f(x) = \log(1 + e^{x})$ and its majorant",
                r"the weight  $\omega(y)$"],
        colors=[GOLD, GREEN],
        gridspec_kw=dict(left=0.07, right=0.97, top=0.84, bottom=0.24, wspace=0.24),
    )
    ax = axes[0]
    at = -2.6
    ax.plot(grid, f(grid), color=INK, lw=2.6)
    majorant = f(at) + df(at) * (grid - at) + 0.5 * omega(at) * (grid - at) ** 2
    ax.plot(grid, majorant, color=GOLD, lw=2.2, ls="--")
    ax.plot([at], [f(at)], "o", color=GOLD, ms=10)
    ax.annotate("tight at y", xy=(at, f(at)), xytext=(at - 0.2, 3.2), color=GOLD,
                fontsize=11.5, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=1.2))
    ax.set_ylim(-0.3, 6.5)
    ax.set_xlabel(r"$x$")
    ax.set_yticks([])
    despine(ax, keep=("bottom",))
    caption(ax, r"$f(x) \leq f(y) + \dot{f}(y)(x-y)"
                r" + \frac{1}{2}\omega(y)(x-y)^2$")

    ax = axes[1]
    ax.plot(grid, omega(grid), color=GREEN, lw=2.8)
    ax.set_ylim(0, 0.3)
    ax.set_xlabel(r"$y$")
    ax.set_ylabel(r"$\omega(y)$")
    despine(ax, keep=("bottom", "left"))
    caption(ax, r"$\omega(y) = \frac{1}{y}"
                r"\left(\frac{1}{1+e^{-y}} - \frac{1}{2}\right)$")


@figure("logistic_fit")
def logistic_fit(fig):
    rng = np.random.default_rng(23)
    X, y = _blobs(rng, 80, gap=1.5, spread=1.0)
    design = np.c_[np.ones(len(X)), X]
    beta, history = _logistic_irls(X, y, iters=8)
    gx = np.linspace(-5.5, 5.5, 10)

    axes = fig.subplots(
        1,
        4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.82, bottom=0.18, wspace=0.10),
    )
    for ax, k in zip(axes[:3], (0, 1, 2)):
        b = history[k]
        gy, gxx = np.meshgrid(np.linspace(-4, 4, 200), np.linspace(-5.5, 5.5, 200))
        prob = _sigmoid(b[0] + b[1] * gxx + b[2] * gy)
        ax.contourf(gxx, gy, prob, levels=[0, 0.5, 1], colors=["#e9f0f8", "#fbecec"])
        if abs(b[2]) > 1e-8:
            ax.plot(gx, -(b[0] + b[1] * gx) / b[2], color=INK, lw=2.2)
        for cls, color in enumerate((BLUE, RED)):
            ax.scatter(X[y == cls, 0], X[y == cls, 1], s=12, color=color, alpha=0.7,
                       edgecolor="none")
        ax.set_xlim(-5.5, 5.5)
        ax.set_ylim(-4, 4)
        ax.set_xticks([])
        ax.set_yticks([])
        despine(ax)
        ax.set_title("k = 0   (β = 0)" if k == 0 else f"k = {k}", pad=8,
                     fontsize=12.5)

    ax = axes[3]
    losses = [_logistic_loss(design, y, b) for b in history]
    ax.plot(range(len(losses)), losses, "o-", color=GREEN, lw=2.4, ms=6)
    ax.set_xlabel("iteration")
    ax.set_ylabel(r"$F(\beta)$")
    ax.set_title("the objective", pad=8, fontsize=12.5)
    despine(ax, keep=("bottom", "left"))
    fig.text(
        0.5,
        0.045,
        "a handful of weighted least squares steps",
        ha="center",
        color=MUTED,
        fontsize=12,
    )


@figure("logistic_props")
def logistic_props(fig):
    ax = canvas(fig)
    column(ax, 0.55, 3.25, 3.9, "in its favour", [
        "simple, and easy to implement",
        "gives probabilities, not just a side",
        "no assumption on how x is distributed",
        "convex: one global minimum",
    ], GREEN)
    column(ax, 4.90, 3.25, 3.9, "against", [
        "the boundary is linear",
        "needs regularisation when d is large",
        # "categorical features need encoding",
        "separable data sends β to infinity",
    ], RED)
    ax.plot([4.65, 4.65], [0.70, 3.35], color=GRID, lw=1.2)
    # note(ax, "the recipe: a linear score, a sigmoid, a likelihood, and IRLS", y=0.35)


def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course02/img")
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
