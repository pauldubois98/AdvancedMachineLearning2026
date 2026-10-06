#!/usr/bin/env python3
"""Every figure of Course03-bis (trees, forests and boosting).

One function per figure, registered under the stem the slide deck asks for.
All figures share one canvas (9 x 3.7075 in), which is exactly the content
area pandoc leaves under a slide title, so a figure never has to be resized.
The tree and forest figures are ported from Course03/imports/figs.py; the
boosting-family ones are imported straight from Course03/imports/figs2.py and
only have their typeface changed. The helpers are the ones from Course01, so
the deck matches the others.

    python3 scripts/make_figures_c03bis.py Course03/img-bis [stem ...]
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


RC = {
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

_DEFAULTS = plt.rcParams.copy()          # pristine, before anyone touches them
plt.rcParams.update(RC)


# --------------------------------------------------------------------------
# the boosting half of the deck is drawn by Course03/imports/figs2.py, which is
# imported rather than copied out: it saves (and pads) its own files, and it
# brings its own rcParams — savefig.bbox="tight" above all, which would crop
# the figures drawn here off their canvas. So it is imported under the pristine
# defaults, its settings are kept aside, and ours are what stays in force.
# --------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent
                       / "Course03" / "imports"))

with matplotlib.rc_context(_DEFAULTS):
    import figs2  # noqa: E402  (its rcParams land as it loads)

    IMPORT_RC = plt.rcParams.copy()
    IMPORT_RC["font.family"] = RC["font.family"]
    IMPORT_RC["mathtext.fontset"] = RC["mathtext.fontset"]

# boosting_stages and bagging_vs_boosting also exist in figs2; the deck keeps
# the versions ported below from imports/figs.py
IMPORTED = {
    name: getattr(figs2, f"fig_{name}")
    for name in (
        "additive_model", "eq_boosting", "shrinkage", "learning_rate",
        "eq_xgboost", "xgb_split_search", "eq_leaf_objective", "xgb_leaf_score",
        "xgb_gh", "xgb_leaf_predict",
        "lgbm_bins", "lgbm_prefix", "lgbm_binned_scan", "lgbm_subtract",
        "lgbm_leafwise", "lgbm_goss",
        "cat_example", "cat_leak_why", "cat_chain", "cat_ordered_ts",
        "cat_oblivious",
        "gbm_compare",
    )
}


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
# helpers ported from Course03/imports/figs.py
# ==========================================================================
def unit(fig):
    """A 0-1 x 0-1 axes, the coordinate system the imported diagrams use."""
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return ax


def ubox(ax, xy, w, h, text, fc="white", ec=BLUE, fs=11, lw=1.8, tc=INK):
    """A rounded label box placed by its centre, in unit coordinates."""
    ax.add_patch(
        FancyBboxPatch(
            (xy[0] - w / 2, xy[1] - h / 2), w, h,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            facecolor=fc, edgecolor=ec, linewidth=lw,
        )
    )
    if text:
        ax.text(xy[0], xy[1], text, ha="center", va="center", fontsize=fs,
                color=tc, linespacing=1.5)


def uarrow(ax, a, b, color=MUTED, lw=1.6, style="-|>"):
    ax.add_patch(
        FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=12, color=color,
                        lw=lw, shrinkA=2, shrinkB=2)
    )


def _bare(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def _moons(n=260, noise=0.22, seed=0):
    from sklearn.datasets import make_moons

    return make_moons(n_samples=n, noise=noise, random_state=seed)


def _scatter_classes(ax, X, y, s=20, alpha=1.0):
    for cls, colour, marker in ((0, BLUE, "o"), (1, RED, "^")):
        m = y == cls
        ax.scatter(X[m, 0], X[m, 1], s=s, color=colour, marker=marker,
                   edgecolors="none", alpha=alpha, zorder=3)


def _field(ax, model, X, cmap="RdBu_r", res=300, pad=0.4):
    """The predicted-probability field of a fitted classifier over the data."""
    gx, gy = np.meshgrid(
        np.linspace(X[:, 0].min() - pad, X[:, 0].max() + pad, res),
        np.linspace(X[:, 1].min() - pad, X[:, 1].max() + pad, res),
    )
    z = model.predict_proba(np.c_[gx.ravel(), gy.ravel()])[:, 1].reshape(gx.shape)
    ax.imshow(z, extent=(gx.min(), gx.max(), gy.min(), gy.max()), origin="lower",
              cmap=cmap, vmin=0, vmax=1, alpha=0.72, aspect="auto",
              interpolation="bilinear")
    ax.contour(gx, gy, z, levels=[0.5], colors=[INK], linewidths=1.4)
    ax.set_aspect("equal")


def _tree_toy(seed=0, n=240):
    """A dataset whose true boundary really is axis-aligned: trees shine here."""
    rng = np.random.default_rng(seed)
    X = rng.uniform(0, 1, (n, 2))
    y = ((X[:, 0] > 0.55) | ((X[:, 1] > 0.62) & (X[:, 0] > 0.22))).astype(int)
    flip = rng.random(n) < 0.06
    y[flip] = 1 - y[flip]
    return X, y


def _gini(y):
    if len(y) == 0:
        return 0.0
    p = y.mean()
    return 2 * p * (1 - p)


# ==========================================================================
# 1. decision trees
# ==========================================================================
@figure("tree_questions")
def tree_questions(fig):
    """The tree and the partition it draws are the same object."""
    X, y = _tree_toy()
    ax = fig.add_axes([0.00, 0.02, 0.50, 0.94])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ubox(ax, (0.5, 0.92), 0.36, 0.12, r"$x_1 > 0.55$ ?", ec=INK, fs=12)
    ax.text(0.32, 0.78, "no", fontsize=10.5, color=MUTED, ha="right")
    ax.text(0.715, 0.77, "yes", fontsize=10.5, color=MUTED)
    uarrow(ax, (0.42, 0.86), (0.26, 0.70))
    uarrow(ax, (0.58, 0.86), (0.76, 0.70))
    ubox(ax, (0.24, 0.62), 0.34, 0.12, r"$x_2 > 0.62$ ?", ec=INK, fs=12)
    ubox(ax, (0.78, 0.62), 0.26, 0.12, "class 1", ec=RED, fs=12, fc="#fdeaea")
    ax.text(0.10, 0.48, "no", fontsize=10.5, color=MUTED, ha="right")
    ax.text(0.375, 0.47, "yes", fontsize=10.5, color=MUTED)
    uarrow(ax, (0.17, 0.56), (0.11, 0.40))
    uarrow(ax, (0.31, 0.56), (0.42, 0.40))
    ubox(ax, (0.10, 0.32), 0.26, 0.12, "class 0", ec=BLUE, fs=12, fc="#e9f0f8")
    ubox(ax, (0.46, 0.32), 0.30, 0.12, r"$x_1 > 0.22$ ?", ec=INK, fs=11.5)
    ax.text(0.31, 0.18, "no", fontsize=10.5, color=MUTED, ha="right")
    ax.text(0.615, 0.17, "yes", fontsize=10.5, color=MUTED)
    uarrow(ax, (0.40, 0.26), (0.32, 0.14))
    uarrow(ax, (0.52, 0.26), (0.62, 0.14))
    ubox(ax, (0.30, 0.07), 0.20, 0.11, "class 0", ec=BLUE, fs=11, fc="#e9f0f8")
    ubox(ax, (0.66, 0.07), 0.20, 0.11, "class 1", ec=RED, fs=11, fc="#fdeaea")

    ax2 = fig.add_axes([0.58, 0.16, 0.37, 0.70])
    ax2.axvspan(0.55, 1.0, color="#fdeaea")
    ax2.add_patch(plt.Rectangle((0, 0), 0.55, 0.62, color="#e9f0f8"))
    ax2.add_patch(plt.Rectangle((0, 0.62), 0.22, 0.38, color="#e9f0f8"))
    ax2.add_patch(plt.Rectangle((0.22, 0.62), 0.33, 0.38, color="#fdeaea"))
    ax2.axvline(0.55, color=INK, lw=2)
    ax2.plot([0, 0.55], [0.62, 0.62], color=INK, lw=2)
    ax2.plot([0.22, 0.22], [0.62, 1.0], color=INK, lw=2)
    _scatter_classes(ax2, X, y, s=14)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_xlabel(r"$x_1$")
    ax2.set_ylabel(r"$x_2$")
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_title("every leaf is a rectangle of feature space", pad=10,
                  fontsize=12.5)


@figure("tree_split")
def tree_split(fig):
    """How the first question is chosen: try every threshold, score each one."""
    X, y = _tree_toy()
    ths = np.linspace(0.03, 0.97, 200)

    def score(col):
        out = []
        for t in ths:
            m = X[:, col] <= t
            n = len(y)
            out.append(m.sum() / n * _gini(y[m]) + (~m).sum() / n * _gini(y[~m]))
        return np.array(out)

    s1, s2 = score(0), score(1)
    k = int(np.argmin(s1))

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.06, right=0.97, top=0.84, bottom=0.22, wspace=0.26),
    )
    _scatter_classes(axes[0], X, y, s=14)
    axes[0].axvline(ths[k], color=GREEN, lw=2.6)
    for t in (0.2, 0.35, 0.8):
        axes[0].axvline(t, color=MUTED, lw=1.2, ls="--")
    axes[0].set_xlabel(r"$x_1$")
    axes[0].set_ylabel(r"$x_2$")
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[0].set_xlim(0, 1)
    axes[0].set_ylim(0, 1)
    axes[0].set_title("candidates (dashed) — one wins", pad=10, fontsize=13)

    axes[1].plot(ths, s1, color=BLUE, lw=2.4, label=r"split on $x_1$")
    axes[1].plot(ths, s2, color=GOLD, lw=2.4, label=r"split on $x_2$")
    axes[1].plot([ths[k]], [s1[k]], "o", color=GREEN, ms=9, zorder=4)
    axes[1].annotate("best of all:\nfeature and threshold", (ths[k], s1[k]),
                     (ths[k] - 0.05, s1[k] + 0.10), fontsize=11, color=GREEN,
                     ha="center", arrowprops=dict(arrowstyle="->", color=GREEN))
    axes[1].set_xlabel("threshold")
    axes[1].set_ylabel("weighted Gini after the split")
    axes[1].legend(frameon=False, fontsize=11)
    despine(axes[1], keep=("bottom", "left"))
    axes[1].set_title("greedy: take the biggest drop in impurity", pad=10,
                      fontsize=13)


@figure("impurity")
def impurity(fig):
    """What 'pure' means, for the three usual measures."""
    p = np.linspace(1e-6, 1 - 1e-6, 400)
    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.07, right=0.98, top=0.84, bottom=0.22, wspace=0.18),
    )
    ax = axes[0]
    ax.plot(p, 2 * p * (1 - p), color=BLUE, lw=2.6, label=r"Gini  $2p(1-p)$")
    ax.plot(p, -(p * np.log2(p) + (1 - p) * np.log2(1 - p)) / 2, color=GOLD,
            lw=2.6, label="entropy (÷2)")
    ax.plot(p, np.minimum(p, 1 - p), color=MUTED, lw=2.2, ls="--",
            label="misclassification")
    ax.set_xlabel(r"share of class 1 in the node, $p$")
    ax.set_ylabel("impurity")
    ax.legend(frameon=False, fontsize=10.5)
    despine(ax, keep=("bottom", "left"))
    ax.set_title("maximal at 50/50, zero when pure", pad=10, fontsize=13)

    ax = axes[1]
    ax.set_xlim(0, 1.25)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for i, (frac, label) in enumerate(((0.5, "impure: 50/50"),
                                       (0.8, "better: 80/20"),
                                       (1.0, "pure: 100/0"))):
        y0 = 0.78 - i * 0.28
        rng = np.random.default_rng(i)
        xs = rng.uniform(0.36, 0.96, 40)
        ys = y0 + rng.uniform(-0.055, 0.055, 40)
        lab = (rng.random(40) < frac).astype(int)
        for cls, colour, marker in ((0, BLUE, "o"), (1, RED, "^")):
            m = lab == cls
            ax.scatter(xs[m], ys[m], s=26, color=colour, marker=marker)
        ax.text(0.32, y0, label, ha="right", va="center", fontsize=12)
        ax.text(1.00, y0, f"Gini {2 * lab.mean() * (1 - lab.mean()):.2f}",
                ha="left", va="center", fontsize=11.5, color=MUTED)
    ax.set_title("a split is good when both children are purer", pad=10,
                 fontsize=13)


@figure("tree_grow")
def tree_grow(fig):
    """The same tree, stopped at four depths."""
    from sklearn.tree import DecisionTreeClassifier

    X, y = _tree_toy()
    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.78, bottom=0.10, wspace=0.10),
    )
    for ax, d in zip(axes, (1, 2, 4, None)):
        m = DecisionTreeClassifier(max_depth=d, random_state=0).fit(X, y)
        _field(ax, m, X)
        _scatter_classes(ax, X, y, s=10)
        title = f"depth {d}" if d else "unlimited"
        ax.set_title(f"{title} — {m.get_n_leaves()} leaves\n"
                     f"train acc {m.score(X, y):.0%}", pad=8, fontsize=11.5,
                     linespacing=1.7)
        _bare(ax)


@figure("tree_regression")
def tree_regression(fig):
    """A regression tree predicts a constant per leaf: staircases, not lines."""
    from sklearn.tree import DecisionTreeRegressor

    rng = np.random.default_rng(0)
    x = np.sort(rng.uniform(0, 1, 80))
    y = np.sin(2 * np.pi * x) + rng.normal(0, 0.18, 80)
    grid = np.linspace(0, 1, 600)[:, None]

    axes = fig.subplots(
        1, 3, sharey=True,
        gridspec_kw=dict(left=0.06, right=0.98, top=0.82, bottom=0.20, wspace=0.10),
    )
    for ax, d in zip(axes, (1, 3, 12)):
        m = DecisionTreeRegressor(max_depth=d).fit(x[:, None], y)
        ax.scatter(x, y, s=16, color=BLUE, edgecolors="none", zorder=3)
        ax.plot(grid.ravel(), m.predict(grid), color=RED, lw=2.4)
        ax.plot(grid.ravel(), np.sin(2 * np.pi * grid.ravel()), color=MUTED,
                lw=1.4, ls="--")
        ax.set_title(f"max_depth = {d}", pad=10, fontsize=13)
        ax.set_xlabel("x")
        despine(ax, keep=("bottom", "left"))
    axes[0].set_ylabel("y")
    fig.text(0.5, 0.04, "a leaf is a constant, so the fit is flat inside every box",
             ha="center", color=MUTED, fontsize=12)


@figure("tree_overfit")
def tree_overfit(fig):
    """Depth is the capacity knob, and it overfits exactly as advertised."""
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeClassifier

    X, y = _tree_toy(0, 700)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.6, random_state=0)
    depths = np.arange(1, 21)
    tr = [DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr)
          .score(Xtr, ytr) for d in depths]
    te = [DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr)
          .score(Xte, yte) for d in depths]

    ax = fig.subplots(gridspec_kw=dict(left=0.26, right=0.74, top=0.86,
                                       bottom=0.20))
    ax.plot(depths, 1 - np.array(tr), "o-", color=BLUE, lw=2.4, ms=4,
            label="training error")
    ax.plot(depths, 1 - np.array(te), "o-", color=RED, lw=2.4, ms=4,
            label="test error")
    k = int(np.argmax(te))
    ax.axvline(depths[k], color=MUTED, ls="--", lw=1.2)
    ax.set_xlabel("max_depth")
    ax.set_ylabel("error rate")
    ax.set_xticks(depths[::3])
    ax.legend(frameon=False, fontsize=11)
    despine(ax, keep=("bottom", "left"))
    ax.set_title("an unpruned tree always reaches zero training error", pad=10,
                 fontsize=13)


@figure("tree_instability")
def tree_instability(fig):
    """Change 10% of the rows, get a different tree: the variance problem."""
    from sklearn.tree import DecisionTreeClassifier

    X, y = _moons(300, 0.22, 0)
    rng = np.random.default_rng(1)
    axes = fig.subplots(
        1, 3, sharey=True,
        gridspec_kw=dict(left=0.04, right=0.98, top=0.80, bottom=0.14, wspace=0.10),
    )
    for i, ax in enumerate(axes):
        idx = rng.choice(len(X), len(X), replace=True)
        m = DecisionTreeClassifier(random_state=0).fit(X[idx], y[idx])
        _field(ax, m, X)
        _scatter_classes(ax, X[idx], y[idx], s=10)
        ax.set_title(f"resample #{i + 1}", pad=8, fontsize=12.5)
        _bare(ax)
    fig.text(0.5, 0.045, "three bootstrap samples give three different trees",
             ha="center", color=MUTED, fontsize=12)


# ==========================================================================
# 2. random forests
# ==========================================================================
@figure("forest_idea")
def forest_idea(fig):
    """Averaging many noisy-but-unbiased guesses."""
    rng = np.random.default_rng(0)
    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.05, right=0.97, top=0.82, bottom=0.22, wspace=0.14),
    )
    single = rng.normal(0.0, 1.0, 4000)
    avg = rng.normal(0.0, 1.0, (4000, 50)).mean(1)
    bins = np.linspace(-3.5, 3.5, 60)
    axes[0].hist(single, bins=bins, color=BLUE, alpha=0.8)
    axes[1].hist(avg, bins=bins, color=GREEN, alpha=0.85)
    axes[0].set_title(f"one tree: spread {single.std():.2f}", color=BLUE, pad=10,
                      fontsize=13)
    axes[1].set_title(f"50 independent trees, averaged: spread {avg.std():.2f}",
                      color=GREEN, pad=10, fontsize=13)
    for ax in axes:
        ax.axvline(0.0, color=INK, lw=2)
        ax.set_xlabel("prediction error at one test point")
        ax.set_yticks([])
        despine(ax, keep=("bottom",))
    fig.text(0.5, 0.045, "the bias is unchanged; only the spread shrinks",
             ha="center", color=MUTED, fontsize=12)


@figure("eq_forest_variance")
def eq_forest_variance(fig):
    """The formula, with both of its symbols defined in words."""
    ax = canvas(fig)
    pieces = [
        (r"$\mathrm{Var}\left(\bar f\right) =$", INK, None),
        (r"$\frac{\sigma^2}{M}$", GREEN, "ONE tree's spread,\ndivided by M"),
        (r"$+$", INK, None),
        (r"$\frac{M-1}{M}\,\rho\,\sigma^2$", RED,
         "how alike two trees are,\ndivided by nothing"),
    ]
    size, gap, y = 24, 0.80, 2.85
    widths = [text_width(fig, ax, text, size) for text, _, _ in pieces]
    x = (W - sum(widths) - gap * (len(pieces) - 1)) / 2
    for (text, color, label), w in zip(pieces, widths):
        ax.text(x, y, text, ha="left", va="center", color=color, fontsize=size)
        if label:
            centre = x + w / 2
            ax.text(centre, 1.85, label, ha="center", va="top", color=color,
                    fontsize=12, linespacing=1.6)
            arrow(ax, (centre, 2.00), (centre, 2.45), color=color, lw=1.4)
        x += w + gap
    ax.text(2.55, 0.95, r"$\sigma^2$ : refit one tree on a fresh sample",
            ha="center", va="center", color=GREEN, fontsize=11.5)
    ax.text(2.55, 0.65, "how far does its prediction jump?", ha="center",
            va="center", color=MUTED, fontsize=11.5)
    ax.text(6.45, 0.95, r"$\rho$ : take two trees of the forest", ha="center",
            va="center", color=RED, fontsize=11.5)
    ax.text(6.45, 0.65, "do they get the same rows wrong?", ha="center",
            va="center", color=MUTED, fontsize=11.5)
    note(ax, "deep unstable trees make σ² big; trees grown on the same rows and "
             "columns make ρ big", y=0.22)


@figure("forest_variance")
def forest_variance(fig):
    """Averaging buys you a floor, not zero — and the floor is set by rho."""
    M = np.arange(1, 1001)
    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.08, right=0.97, top=0.82, bottom=0.26, wspace=0.30),
    )
    ax = axes[0]
    for rho, colour in ((0.0, GREEN), (0.2, BLUE), (0.5, GOLD), (0.9, RED)):
        ax.plot(M, 1 / M + (M - 1) / M * rho, color=colour, lw=2.4,
                label=rf"$\rho$ = {rho}")
        ax.plot([M.min(), M.max()], [rho, rho], color=colour, ls=":", lw=1.1)
    ax.set_xscale("log")
    ax.set_xlabel("number of trees M")
    ax.set_ylabel(r"variance of the average, in units of $\sigma^2$")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(1, 8000)
    ax.legend(frameon=False, loc="center right", fontsize=10.5)
    despine(ax, keep=("bottom", "left"))
    ax.set_title(r"it stops falling at the floor $\rho\,\sigma^2$", pad=10,
                 fontsize=13)
    caption(ax, "dotted: the floor")

    ax = axes[1]
    for rho, colour in ((0.0, GREEN), (0.2, BLUE), (0.5, GOLD), (0.9, RED)):
        ax.plot(M, M / (1 + (M - 1) * rho), color=colour, lw=2.4)
        if rho:
            ax.plot([M.min(), M.max()], [1 / rho] * 2, color=colour, ls=":", lw=1.1)
            ax.text(1300, 1 / rho, rf"  $1/\rho$ = {1 / rho:.1f}", color=colour,
                    fontsize=10.5, va="center")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1, 6000)
    ax.set_xlabel("number of trees M")
    ax.set_ylabel(r"trees that count: $M/(1+(M-1)\rho)$")
    despine(ax, keep=("bottom", "left"))
    ax.set_title("1000 correlated trees are worth a handful", pad=10, fontsize=13)
    caption(ax, r"$\rho = 0.5$, M = 1000  →  worth two independent trees")


@figure("forest_diagram")
def forest_diagram(fig):
    """Two sources of randomness, one vote."""
    ax = unit(fig)
    ubox(ax, (0.34, 0.90), 0.20, 0.11, "training data", ec=INK, fs=11.5)
    for i in range(5):
        x = 0.07 + i * 0.135
        uarrow(ax, (0.34, 0.835), (x, 0.70), color=GRID, lw=1.1)
        ubox(ax, (x, 0.615), 0.118, 0.145, f"bootstrap\nsample {i + 1}", ec=BLUE,
             fs=8.5)
        uarrow(ax, (x, 0.535), (x, 0.44), color=GRID, lw=1.1)
        ubox(ax, (x, 0.355), 0.118, 0.145, f"deep tree {i + 1}", ec=GREEN, fs=8.5)
        uarrow(ax, (x, 0.275), (0.34, 0.17), color=GRID, lw=1.1)
    ubox(ax, (0.34, 0.10), 0.28, 0.11, "average  /  majority vote", ec=GREEN,
         fs=11.5)
    ax.text(0.78, 0.615, "① rows drawn\nwith replacement", fontsize=10.5,
            color=BLUE, va="center", ha="left", linespacing=1.6)
    ax.text(0.78, 0.355, "② √p random\ncolumns per split",
            fontsize=10.5, color=GREEN, va="center", ha="left", linespacing=1.6)


@figure("forest_boundary")
def forest_boundary(fig):
    """One tree, ten trees, five hundred: the boundary stops twitching."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier

    X, y = _moons(260, 0.22, 0)
    models = (
        ("1 tree", DecisionTreeClassifier(random_state=0)),
        ("10 trees", RandomForestClassifier(10, random_state=0)),
        ("500 trees", RandomForestClassifier(500, random_state=0)),
    )
    axes = fig.subplots(
        1, 3, sharey=True,
        gridspec_kw=dict(left=0.04, right=0.98, top=0.82, bottom=0.14, wspace=0.10),
    )
    for ax, (title, m) in zip(axes, models):
        m.fit(X, y)
        _field(ax, m, X)
        _scatter_classes(ax, X, y, s=11)
        ax.set_title(title, pad=8, fontsize=13)
        _bare(ax)
    fig.text(0.5, 0.045, "same bias, less and less variance",
             ha="center", color=MUTED, fontsize=12)


@figure("max_features")
def max_features(fig):
    """What the knob literally does: a fresh draw of columns at every node."""
    rng = np.random.default_rng(7)
    p_cols, k = 12, 4
    ax = fig.add_axes([0.01, 0.06, 0.58, 0.88])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.97, f"p = {p_cols} columns,  max_features = {k}", ha="center",
            fontsize=12.5, color=INK)
    for r, name in enumerate(("root", "left child", "right child")):
        y = 0.74 - r * 0.215
        drawn = np.sort(rng.choice(p_cols, k, replace=False))
        winner = drawn[rng.integers(k)]
        ax.text(0.0, y, name, ha="left", va="center", fontsize=11, color=MUTED)
        for c in range(p_cols):
            x = 0.215 + c * 0.047
            on = c in drawn
            ax.add_patch(FancyBboxPatch(
                (x - 0.019, y - 0.050), 0.038, 0.100,
                boxstyle="round,pad=0.004,rounding_size=0.012",
                facecolor="#dce7f3" if on else "white",
                edgecolor=GREEN if c == winner else (BLUE if on else GRID),
                linewidth=2.4 if c == winner else 1.2))
            ax.text(x, y, f"$x_{{{c + 1}}}$", ha="center", va="center",
                    fontsize=9, color=INK if on else MUTED)
        ax.text(1.0, y, f"best: $x_{{{winner + 1}}}$", ha="right", va="center",
                fontsize=11, color=GREEN)
    ax.text(0.5, 0.12, "the winner is the best of the 4 drawn, never of all 12",
            ha="center", fontsize=11.5, color=MUTED)
    ax.text(0.5, 0.02, "a NEW draw at every node — not once per tree", ha="center",
            fontsize=12, color=RED)

    side = fig.add_axes([0.62, 0.08, 0.36, 0.84])
    side.axis("off")
    side.text(0.0, 0.97, "at every split, the tree:", fontsize=12.5, color=INK,
              va="center")
    for i, (n, t) in enumerate((("1.", "draws max_features columns"),
                                ("2.", "tries every threshold, on those"),
                                ("3.", "keeps the best, then recurses"))):
        y = 0.84 - i * 0.09
        side.text(0.02, y, n, fontsize=11.5, color=BLUE, va="center")
        side.text(0.10, y, t, fontsize=11.5, color=INK, va="center")
    side.text(0.0, 0.48, "what to set it to", fontsize=12.5, color=INK, va="center")
    rows = ((r"$\sqrt{p}$", "classification default", GREEN),
            (r"$p/3$ or all", "regression defaults", GREEN),
            ("1", "most diversity, weakest trees", GOLD),
            ("all p", "no column randomness: bagging", RED))
    for i, (val, what, colour) in enumerate(rows):
        y = 0.35 - i * 0.095
        side.text(0.26, y, val, ha="right", fontsize=11.5, color=colour,
                  va="center")
        side.text(0.31, y, what, fontsize=11, color=INK, va="center")


@figure("forest_features")
def forest_features(fig):
    """Why max_features is the knob that makes a forest a forest."""
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    X, y = make_classification(n_samples=1200, n_features=25, n_informative=12,
                               n_redundant=8, class_sep=0.7, flip_y=0.05,
                               random_state=0)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.5, random_state=0)
    ks = [1, 2, 3, 5, 8, 12, 18, 25]
    err = np.array([[1 - RandomForestClassifier(300, max_features=k, random_state=s)
                     .fit(Xtr, ytr).score(Xte, yte) for k in ks] for s in range(3)])

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.08, right=0.97, top=0.84, bottom=0.22, wspace=0.22),
    )
    ax = axes[0]
    ax.plot(ks, err.mean(0), "o-", color=GREEN, lw=2.6, ms=6)
    ax.fill_between(ks, err.mean(0) - err.std(0), err.mean(0) + err.std(0),
                    color=GREEN, alpha=0.15)
    ax.axvline(np.sqrt(25), color=MUTED, ls="--", lw=1.3)
    ax.text(np.sqrt(25) + 0.5, err.max() * 0.99, r"the $\sqrt{p}$ default",
            fontsize=11, color=MUTED)
    ax.set_xlabel("max_features, out of 25")
    ax.set_ylabel("test error")
    despine(ax, keep=("bottom", "left"))
    ax.set_title("25 columns: 12 informative, 8 redundant", pad=10, fontsize=13)

    ax = axes[1]
    ax.axis("off")
    ax.text(0.5, 0.92, "both ends are worse than the middle", ha="center",
            transform=ax.transAxes, fontsize=13, color=GREEN)
    ax.text(0.5, 0.58, "all columns allowed → every tree takes\n"
                       "the same strong split first → ρ large\n"
                       "→ averaging buys almost nothing",
            ha="center", transform=ax.transAxes, fontsize=11.5, color=RED,
            linespacing=1.7)
    ax.text(0.5, 0.22, "one column allowed → the trees disagree,\n"
                       "but each is barely better than chance\n"
                       "→ low ρ, high individual error",
            ha="center", transform=ax.transAxes, fontsize=11.5, color=GOLD,
            linespacing=1.7)
    ax.text(0.5, 0.02, r"$\sqrt{p}$ is a default, not a law — tune it",
            ha="center", transform=ax.transAxes, fontsize=12, color=MUTED)


@figure("forest_correlation")
def forest_correlation(fig):
    """rho is not a metaphor: measure it, and watch it fight tree strength."""
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    X, y = make_classification(n_samples=1200, n_features=25, n_informative=12,
                               n_redundant=8, class_sep=0.7, flip_y=0.05,
                               random_state=0)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.5, random_state=0)
    ks = [1, 2, 3, 5, 8, 12, 18, 25]
    rho, solo, forest = [], [], []
    for k in ks:
        f = RandomForestClassifier(60, max_features=k, random_state=0).fit(Xtr, ytr)
        preds = np.array([t.predict(Xte) for t in f.estimators_])
        c = np.corrcoef(preds)
        rho.append(c[np.triu_indices_from(c, k=1)].mean())
        solo.append(np.mean([1 - np.mean(p == yte) for p in preds]))
        forest.append(1 - f.score(Xte, yte))
    rho, solo, forest = np.array(rho), np.array(solo), np.array(forest)

    axes = fig.subplots(
        1, 2,
        gridspec_kw=dict(left=0.09, right=0.93, top=0.82, bottom=0.24, wspace=0.52),
    )
    ax = axes[0]
    ax.plot(ks, rho, "o-", color=RED, lw=2.6, ms=5)
    ax.set_ylabel(r"pairwise correlation $\rho$", color=RED)
    ax.tick_params(axis="y", colors=RED)
    ax.set_xlabel("max_features, out of 25")
    ax.set_ylim(0, 0.42)
    twin = ax.twinx()
    twin.plot(ks, solo, "s--", color=BLUE, lw=2.2, ms=5)
    twin.set_ylabel("error of ONE tree", color=BLUE)
    twin.tick_params(axis="y", colors=BLUE)
    twin.set_ylim(0.30, 0.42)
    ax.set_title("the two effects pull apart", pad=10, fontsize=12.5)
    caption(ax, "more columns: stronger trees, more alike")

    ax = axes[1]
    ax.plot(rho, forest, "-", color=MUTED, lw=1.4, zorder=1)
    ax.scatter(rho, forest, s=60, color=GREEN, zorder=3)
    for k, r, e in zip(ks, rho, forest):
        ax.annotate(f"{k}", (r, e), (0, 9), textcoords="offset points",
                    ha="center", fontsize=10, color=INK)
    j = int(np.argmin(forest))
    ax.scatter([rho[j]], [forest[j]], s=160, facecolor="none", edgecolor=RED,
               lw=2.0, zorder=4)
    ax.set_xlabel(r"$\rho$   (labels: max_features)")
    ax.set_ylabel("test error of the forest")
    ax.margins(y=0.18)
    despine(ax, keep=("bottom", "left"))
    ax.set_title("the best forest is not the most diverse", pad=10, fontsize=12.5)
    caption(ax, "too diverse, or too alike: both lose")


@figure("forest_ntrees")
def forest_ntrees(fig):
    """More trees never overfits — it just stops helping."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    X, y = _moons(900, 0.32, 7)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.55, random_state=0)
    ms = [1, 2, 3, 5, 8, 12, 20, 35, 60, 100, 200, 400]
    curves = np.array([[1 - RandomForestClassifier(m, random_state=seed)
                        .fit(Xtr, ytr).score(Xte, yte) for m in ms]
                       for seed in range(4)])

    ax = fig.subplots(gridspec_kw=dict(left=0.26, right=0.74, top=0.84,
                                       bottom=0.22))
    for c in curves:
        ax.plot(ms, c, color=MUTED, lw=1.0, alpha=0.6)
    ax.plot(ms, curves.mean(0), "o-", color=GREEN, lw=2.8, ms=5,
            label="mean over 4 seeds")
    ax.set_xscale("log")
    ax.set_xlabel("number of trees")
    ax.set_ylabel("test error")
    ax.legend(frameon=False, fontsize=11)
    despine(ax, keep=("bottom", "left"))
    ax.set_title("a budget knob, not a capacity knob", pad=10, fontsize=13)
    caption(ax, "flat is fine — you just pay for it")


# ==========================================================================
# 3. boosting
# ==========================================================================
@figure("boosting_stages")
def boosting_stages(fig):
    """Watch the residuals flatten: three rounds of boosting, drawn."""
    from sklearn.tree import DecisionTreeRegressor

    rng = np.random.default_rng(0)
    x = np.sort(rng.uniform(0, 1, 90))
    y = np.sin(2 * np.pi * x) + rng.normal(0, 0.18, 90)
    grid = np.linspace(0, 1, 400)
    eta = 0.8

    F = np.zeros_like(y)
    Fg = np.zeros_like(grid)
    axes = fig.subplots(
        2, 4, sharex=True,
        gridspec_kw=dict(left=0.07, right=0.98, top=0.86, bottom=0.14,
                         wspace=0.14, hspace=0.42),
    )
    for m in range(4):
        r = y - F
        top, bottom = axes[0, m], axes[1, m]
        top.plot(grid, np.sin(2 * np.pi * grid), color=MUTED, lw=1.4, ls="--")
        top.scatter(x, y, s=9, color=BLUE, alpha=0.6, edgecolors="none")
        top.plot(grid, Fg, color=RED, lw=2.2)
        top.set_title(rf"$F_{m}$  (after {m} trees)", pad=6, fontsize=11)
        top.set_ylim(-1.9, 1.9)

        bottom.axhline(0, color=INK, lw=0.9)
        bottom.scatter(x, r, s=9, color=GOLD, edgecolors="none")
        bottom.set_ylim(-1.9, 1.9)
        bottom.set_xlabel("x", labelpad=1)
        if m < 3:
            h = DecisionTreeRegressor(max_depth=2).fit(x[:, None], r)
            bottom.plot(grid, h.predict(grid[:, None]), color=GREEN, lw=2.0)
            bottom.set_title("residuals + its tree", pad=6, fontsize=10)
            F = F + eta * h.predict(x[:, None])
            Fg = Fg + eta * h.predict(grid[:, None])
        else:
            bottom.set_title("nearly flat", pad=6, fontsize=10)
        for ax in (top, bottom):
            ax.set_xticks([])
            ax.set_yticks([])
            despine(ax)
    axes[0, 0].set_ylabel("y")
    axes[1, 0].set_ylabel("residual")


@figure("bagging_vs_boosting")
def bagging_vs_boosting(fig):
    """Two ways to spend many trees, and the two errors they attack."""
    ax = unit(fig)
    ax.text(0.25, 0.96, "FOREST — parallel", ha="center", fontsize=13, color=GREEN)
    ax.text(0.75, 0.96, "BOOSTING — sequential", ha="center", fontsize=13,
            color=GOLD)
    ax.plot([0.5, 0.5], [0.05, 0.90], color=GRID, lw=1.0, ls="--")

    ubox(ax, (0.25, 0.80), 0.16, 0.10, "training data", ec=INK, fs=10.5)
    for i in range(4):
        x = 0.08 + i * 0.113
        uarrow(ax, (0.25, 0.75), (x, 0.63), color=GRID, lw=1.1)
        ubox(ax, (x, 0.555), 0.095, 0.12, f"deep\ntree {i + 1}", ec=GREEN, fs=9.5)
        uarrow(ax, (x, 0.49), (0.25, 0.35), color=GRID, lw=1.1)
    ubox(ax, (0.25, 0.27), 0.20, 0.10, "average / vote", ec=GREEN, fs=11)
    ax.text(0.25, 0.09, "each tree sees a bootstrap sample\n→ attacks VARIANCE",
            ha="center", fontsize=11, color=INK, linespacing=1.6)

    for i in range(4):
        x = 0.575 + i * 0.115
        ubox(ax, (x, 0.555), 0.095, 0.12, f"shallow\ntree {i + 1}", ec=GOLD,
             fs=9.5)
        if i:
            uarrow(ax, (x - 0.057, 0.555), (x - 0.050, 0.555), color=GRID, lw=1.4)
    ax.text(0.75, 0.73, "each tree fits the errors of the sum so far", ha="center",
            fontsize=10.5, color=MUTED)
    for i in range(4):
        uarrow(ax, (0.575 + i * 0.115, 0.49), (0.75, 0.35), color=GRID, lw=1.1)
    ubox(ax, (0.75, 0.27), 0.22, 0.10, r"weighted sum  $\sum \eta\, h_m$", ec=GOLD,
         fs=11)
    ax.text(0.75, 0.09, "each tree corrects the running model\n→ attacks BIAS",
            ha="center", fontsize=11, color=INK, linespacing=1.6)


@figure("boosting_overfit")
def boosting_overfit(fig):
    """Unlike a forest, adding boosting rounds eventually hurts."""
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.model_selection import train_test_split

    X, y = _moons(700, 0.38, 11)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.55, random_state=0)
    gb = GradientBoostingClassifier(n_estimators=600, learning_rate=0.25,
                                    max_depth=4, random_state=0).fit(Xtr, ytr)
    stages = np.arange(1, 601)
    gb_te = np.array([1 - np.mean((p[:, 1] > 0.5).astype(int) == yte)
                      for p in gb.staged_predict_proba(Xte)])
    gb_tr = np.array([1 - np.mean((p[:, 1] > 0.5).astype(int) == ytr)
                      for p in gb.staged_predict_proba(Xtr)])
    ms = [1, 2, 5, 10, 25, 50, 100, 200, 400, 600]
    rf_te = [1 - RandomForestClassifier(m, random_state=0).fit(Xtr, ytr)
             .score(Xte, yte) for m in ms]

    ax = fig.subplots(gridspec_kw=dict(left=0.24, right=0.76, top=0.84,
                                       bottom=0.22))
    ax.plot(stages, gb_tr, color=GOLD, lw=1.4, ls="--", label="boosting — train")
    ax.plot(stages, gb_te, color=GOLD, lw=2.4, label="boosting — test")
    ax.plot(ms, rf_te, "o-", color=GREEN, lw=2.4, ms=4, label="forest — test")
    k = int(np.argmin(gb_te))
    ax.plot([stages[k]], [gb_te[k]], "o", color=RED, ms=8, zorder=4)
    ax.annotate("early stopping goes here", (stages[k], gb_te[k]),
                (stages[k] + 60, gb_te[k] + 0.06), fontsize=11, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED))
    ax.set_xscale("log")
    ax.set_xlabel("number of trees")
    ax.set_ylabel("error rate")
    ax.legend(frameon=False, fontsize=10.5)
    despine(ax, keep=("bottom", "left"))
    ax.set_title("harmless in a forest, a real risk in boosting", pad=10,
                 fontsize=13)


@figure("zoo")
def zoo(fig):
    """One dataset, the models of this deck, side by side."""
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier

    X, y = _moons(300, 0.22, 0)
    models = (
        ("logistic regression", LogisticRegression()),
        ("one decision tree", DecisionTreeClassifier(random_state=0)),
        ("random forest, 300", RandomForestClassifier(300, random_state=0)),
        ("gradient boosting", GradientBoostingClassifier(random_state=0)),
    )
    axes = fig.subplots(
        1, 4,
        gridspec_kw=dict(left=0.03, right=0.98, top=0.82, bottom=0.16, wspace=0.10),
    )
    for ax, (title, m) in zip(axes, models):
        m.fit(X, y)
        _field(ax, m, X)
        _scatter_classes(ax, X, y, s=9)
        ax.set_title(title, pad=8, fontsize=11.5)
        _bare(ax)
    fig.text(0.5, 0.05, "a line, a staircase, a smoothed staircase, "
                        "and a sharpened one",
             ha="center", color=MUTED, fontsize=12)


def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course03/img-bis")
    out.mkdir(parents=True, exist_ok=True)
    wanted = argv[2:] or sorted({**FIGURES, **IMPORTED})
    for stem in wanted:
        if stem in FIGURES:
            fig = plt.figure(figsize=(W, H), dpi=DPI)
            FIGURES[stem](fig)
            fig.savefig(out / f"{stem}.png", dpi=DPI)
            plt.close(fig)
        elif stem in IMPORTED:
            with matplotlib.rc_context(IMPORT_RC):
                IMPORTED[stem](out)       # it saves, and pads, its own file
        else:
            raise SystemExit(f"unknown figure: {stem}")
        print(f"  {stem}.png")


if __name__ == "__main__":
    main(sys.argv)
