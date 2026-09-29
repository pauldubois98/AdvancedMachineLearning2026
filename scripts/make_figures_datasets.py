#!/usr/bin/env python3
"""One figure per suggested project dataset (SUGGESTED_DATASETS.md), for Course01.

Each figure is an identity card on the left (what the data is, its size, its
types, its format, where to get it) and, on the right, a thumbnail drawn from
the real data.  The raw files are downloaded once into .cache/datasets/ and
reused afterwards, so only the first build needs a network connection.

    python3 scripts/make_figures_datasets.py Course01/img [stem ...]
"""

import csv
import gzip
import io
import json
import sys
import tarfile
import textwrap
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

import numpy as np

from make_figures_c01 import (
    BLUE,
    CYCLE,
    DPI,
    GOLD,
    GREEN,
    GRID,
    H,
    INK,
    MUTED,
    PURPLE,
    RED,
    W,
    blank,
    canvas,
    plt,
)

CACHE = Path(__file__).resolve().parent.parent / ".cache" / "datasets"


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
# data access
# --------------------------------------------------------------------------
def fetch(url, name):
    """Path to a cached copy of `url`, downloading it the first time."""
    path = CACHE / name
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        print(f"    downloading {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r:
            data = r.read()
        path.write_bytes(data)
    return path


def read_csv(path_or_text, delimiter=",", opener=open):
    if isinstance(path_or_text, Path):
        with opener(path_or_text, "rt", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f, delimiter=delimiter))
    return list(csv.DictReader(io.StringIO(path_or_text), delimiter=delimiter))


def floats(rows, key):
    return np.array([float(r[key]) for r in rows])


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------
LEFT_W = 3.75  # inches taken by the identity card
FIELDS = ("Size", "Data", "Format", "Source")


def card(fig, what, size, types, fmt, source, color=BLUE):
    """The identity card on the left; returns the canvas axes."""
    ax = canvas(fig)
    y = H - 0.28
    for line in textwrap.wrap(what, 40):
        ax.text(0.3, y, line, ha="left", va="top", color=INK, fontsize=12.5)
        y -= 0.25
    y -= 0.2
    for label, value in zip(FIELDS, (size, types, fmt, source)):
        ax.text(
            0.3, y, label, ha="left", va="top", color=color, fontsize=10.5,
            weight="bold",
        )
        for line in textwrap.wrap(value, 38):
            ax.text(1.02, y, line, ha="left", va="top", color=INK, fontsize=10.5)
            y -= 0.215
        y -= 0.1
    ax.plot([LEFT_W + 0.1] * 2, [0.3, H - 0.3], color=GRID, lw=1.2)
    return ax


def thumb(fig, x0=LEFT_W + 0.55, y0=0.62, x1=W - 0.2, y1=H - 0.22):
    """One plotting axes filling the thumbnail area (inches)."""
    return fig.add_axes([x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H])


def grid(fig, rows, cols, x0=LEFT_W + 0.4, y0=0.45, x1=W - 0.2, y1=H - 0.2,
         gap=0.04):
    """rows x cols image axes, square cells, centred in the thumbnail area."""
    cell = min((x1 - x0 - (cols - 1) * gap) / cols, (y1 - y0 - (rows - 1) * gap) / rows)
    wx = cols * cell + (cols - 1) * gap
    wy = rows * cell + (rows - 1) * gap
    ox, oy = x0 + (x1 - x0 - wx) / 2, y0 + (y1 - y0 - wy) / 2
    axes = []
    for i in range(rows):
        row = []
        for j in range(cols):
            x = ox + j * (cell + gap)
            y = oy + (rows - 1 - i) * (cell + gap)
            a = fig.add_axes([x / W, y / H, cell / W, cell / H])
            blank(a)
            row.append(a)
        axes.append(row)
    return axes, (ox, oy, wx, wy)


def thumb_caption(fig, text, y=0.2):
    """A grey line under the thumbnail, `y` in inches from the bottom."""
    fig.text(
        (LEFT_W + 0.1 + W) / 2 / W, y / H, text, ha="center", va="center",
        color=MUTED, fontsize=10,
    )


def table(ax, header, rows, x0, x1, y_top, widths, size=9.5, leading=0.3):
    """A plain text table drawn on the canvas, columns sized by `widths`."""
    widths = np.asarray(widths, float)
    xs = x0 + np.concatenate([[0], np.cumsum(widths)[:-1]]) / widths.sum() * (x1 - x0)
    for x, h in zip(xs, header):
        ax.text(x, y_top, h, ha="left", va="top", color=BLUE, fontsize=size,
                weight="bold")
    ax.plot([x0, x1], [y_top - leading * 0.82] * 2, color=GRID, lw=1)
    for i, r in enumerate(rows):
        y = y_top - leading * (i + 1)
        for x, v in zip(xs, r):
            ax.text(x, y, v, ha="left", va="top", color=INK, fontsize=size)
    return y_top - leading * (len(rows) + 1)


def style(ax, xlabel=None, ylabel=None):
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.tick_params(labelsize=9)


# ==========================================================================
# the 21 datasets, in the order of SUGGESTED_DATASETS.md
# ==========================================================================
@figure("ds_stars")
def ds_stars(fig):
    card(
        fig,
        "Classic robust regression benchmark: 47 stars of the Cygnus OB1 "
        "cluster on a Hertzsprung-Russell diagram (Rousseeuw & Leroy).",
        "47 stars, 2 variables",
        "continuous numerical",
        "CSV",
        "Rdatasets, robustbase::starsCYG",
    )
    rows = read_csv(fetch(
        "https://vincentarelbundock.github.io/Rdatasets/csv/robustbase/starsCYG.csv",
        "starsCYG.csv",
    ))
    t, light = floats(rows, "log.Te"), floats(rows, "log.light")
    giant = t < 3.6
    ax = thumb(fig)
    ax.scatter(t[~giant], light[~giant], s=22, color=BLUE, label="main sequence")
    ax.scatter(t[giant], light[giant], s=22, color=RED, label="red giants")
    ax.invert_xaxis()
    ax.legend(loc="upper center")
    style(ax, "log surface temperature", "log light intensity")


@figure("ds_ames")
def ds_ames(fig):
    card(
        fig,
        "House sale prices in Ames, Iowa (2006 to 2010), compiled by "
        "De Cock as a modern replacement for Boston Housing.",
        "2,930 sales, 80 explanatory variables",
        "mixed: continuous, discrete, ordinal, nominal",
        "tab separated text",
        "jse.amstat.org (J. Stat. Education, 2011)",
    )
    rows = read_csv(
        fetch("http://jse.amstat.org/v19n3/decock/AmesHousing.txt", "AmesHousing.txt"),
        delimiter="\t",
    )
    area = floats(rows, "Gr Liv Area") * 0.0929  # sq ft -> m2
    price = floats(rows, "SalePrice") / 1000
    ax = thumb(fig)
    ax.scatter(area, price, s=5, color=BLUE, alpha=0.35, lw=0)
    style(ax, "living area (m²)", "sale price (k$)")


@figure("ds_dvf")
def ds_dvf(fig):
    card(
        fig,
        "Every French real estate sale published by the DGFiP (except Alsace, "
        "Moselle and Mayotte): price, surface, rooms, type and location.",
        "millions of transactions per year, about 40 columns, 5 years",
        "mixed: numerical, categorical, dates, addresses, coordinates",
        "pipe delimited text, CSV (geolocated)",
        "data.gouv.fr",
    )
    rows = read_csv(
        fetch(
            "https://files.data.gouv.fr/geo-dvf/latest/csv/2024/departements/75.csv.gz",
            "dvf_2024_75.csv.gz",
        ),
        opener=gzip.open,
    )
    lines = Counter(r["id_mutation"] for r in rows)
    lon, lat, ppm = [], [], []
    for r in rows:
        if (
            lines[r["id_mutation"]] == 1
            and r["nature_mutation"] == "Vente"
            and r["type_local"] == "Appartement"
            and r["surface_reelle_bati"]
            and r["longitude"]
            and r["valeur_fonciere"]
        ):
            s = float(r["surface_reelle_bati"])
            if s >= 9:
                lon.append(float(r["longitude"]))
                lat.append(float(r["latitude"]))
                ppm.append(float(r["valeur_fonciere"]) / s / 1000)
    ax = thumb(fig, x0=LEFT_W + 0.5, y0=0.45, x1=W - 0.1)
    sc = ax.scatter(lon, lat, c=np.clip(ppm, 5, 16), s=1.2, cmap="viridis", lw=0)
    ax.set_aspect(1 / np.cos(np.deg2rad(48.86)))
    blank(ax)
    cb = fig.colorbar(sc, ax=ax, shrink=0.8, pad=0.02)
    cb.set_label("k€ / m²", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    thumb_caption(fig, f"{len(ppm):,} single-flat sales in Paris, 2024", y=0.25)


@figure("ds_breast_cancer")
def ds_breast_cancer(fig):
    from sklearn.datasets import load_breast_cancer

    card(
        fig,
        "Tumour diagnosis from cell nuclei measured on digitised images of "
        "fine needle aspirates (radius, texture, concavity, ...).",
        "569 samples, 30 features, 212 malignant / 357 benign",
        "continuous numerical, binary label",
        "CSV (.data), built into scikit-learn",
        "UCI Machine Learning Repository",
    )
    d = load_breast_cancer()
    x = d.data[:, list(d.feature_names).index("mean radius")]
    y = d.data[:, list(d.feature_names).index("worst concave points")]
    ax = thumb(fig)
    for k, (name, color) in enumerate([("malignant", RED), ("benign", BLUE)]):
        m = d.target == k
        ax.scatter(x[m], y[m], s=10, color=color, alpha=0.6, lw=0, label=name)
    ax.legend(loc="lower right")
    style(ax, "mean radius", "worst concave points")


@figure("ds_adult")
def ds_adult(fig):
    ax = card(
        fig,
        "Predict whether income exceeds 50K USD per year, from the 1994 US "
        "census. Missing values, about 24% positives.",
        "48,842 individuals, 14 features",
        "mixed: continuous, categorical; binary label",
        "CSV (.data / .test)",
        "UCI Machine Learning Repository",
    )
    path = fetch(
        "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data",
        "adult.data",
    )
    raw = [r for r in csv.reader(path.open(), skipinitialspace=True) if r][:8]
    cols = [0, 1, 3, 6, 9, 12, 14]  # age, workclass, education, occupation, sex, hours, income
    header = ["age", "workclass", "education", "occupation", "sex", "h/week", "income"]
    rows = [[textwrap.shorten(r[c], 16, placeholder="…") for c in cols] for r in raw]
    table(ax, header, rows, LEFT_W + 0.35, W - 0.1, H - 0.45,
          [0.5, 1.25, 1.0, 1.4, 0.75, 0.7, 0.6], size=9)
    thumb_caption(fig, "first 8 rows, 7 of the 15 columns", y=0.45)


@figure("ds_creditcard")
def ds_creditcard(fig):
    card(
        fig,
        "Fraudulent card transactions by European cardholders over two days "
        "in 2013. For confidentiality, 28 features are PCA components.",
        "284,807 transactions, 30 features, 492 frauds (0.17%)",
        "continuous numerical, binary label",
        "CSV (about 150 MB)",
        "Kaggle, mlg-ulb/creditcardfraud (free account)",
    )
    path = fetch(
        "https://storage.googleapis.com/download.tensorflow.org/data/creditcard.csv",
        "creditcard.csv",
    )
    small = CACHE / "creditcard_v14_v17_class.npy"
    if not small.exists():
        with path.open() as f:
            header = f.readline().replace('"', "").strip().split(",")
            idx = [header.index(c) for c in ("V14", "V17", "Class")]
            data = np.loadtxt(
                (l.replace('"', "") for l in f), delimiter=",", usecols=idx
            )
        np.save(small, data)
    v14, v17, cls = np.load(small).T
    rng = np.random.default_rng(0)
    ok = np.flatnonzero(cls == 0)
    ok = rng.choice(ok, 6000, replace=False)
    fraud = cls == 1
    ax = thumb(fig)
    ax.scatter(v14[ok], v17[ok], s=4, color=BLUE, alpha=0.3, lw=0,
               label="legitimate (6,000 drawn)")
    ax.scatter(v14[fraud], v17[fraud], s=6, color=RED, alpha=0.7, lw=0,
               label="fraud (all 492)")
    ax.legend(loc="upper left", markerscale=3)
    style(ax, "V14", "V17")


@figure("ds_spambase")
def ds_spambase(fig):
    card(
        fig,
        "Spam versus legitimate email. Each email is summarised by word and "
        "character frequencies, plus statistics on runs of capitals.",
        "4,601 emails, 57 features, about 39% spam",
        "continuous numerical, binary label",
        "CSV (.data)",
        "UCI Machine Learning Repository",
    )
    names = fetch(
        "https://archive.ics.uci.edu/ml/machine-learning-databases/spambase/spambase.names",
        "spambase.names",
    ).read_text()
    feats = [l.split(":")[0] for l in names.splitlines()
             if l.startswith(("word_freq_", "char_freq_", "capital_run"))]
    X = np.loadtxt(fetch(
        "https://archive.ics.uci.edu/ml/machine-learning-databases/spambase/spambase.data",
        "spambase.data",
    ), delimiter=",")
    X, y = X[:, :-1], X[:, -1]
    words = ["free", "your", "remove", "money", "000", "hp", "george", "edu"]
    idx = [feats.index("word_freq_" + w) for w in words]
    spam, ham = X[y == 1][:, idx].mean(0), X[y == 0][:, idx].mean(0)
    ax = thumb(fig)
    xs = np.arange(len(words))
    ax.bar(xs - 0.2, spam, 0.4, color=RED, label="spam")
    ax.bar(xs + 0.2, ham, 0.4, color=BLUE, label="legitimate")
    ax.set_xticks(xs, [f"“{w}”" for w in words])
    ax.legend(loc="upper center")
    style(ax, None, "mean frequency (%)")


@figure("ds_earthquakes")
def ds_earthquakes(fig):
    card(
        fig,
        "Worldwide earthquakes with location, depth and magnitude. Choose "
        "your own time window, region and minimum magnitude.",
        "configurable: thousands to hundreds of thousands of events",
        "numerical (coordinates, depth, magnitude), timestamps, categorical",
        "CSV, GeoJSON, KML, QuakeML",
        "USGS earthquake search",
    )
    rows = read_csv(fetch(
        "https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv"
        "&starttime=2025-01-01&endtime=2026-01-01&minmagnitude=5",
        "usgs_2025_m5.csv",
    ))
    lon, lat = floats(rows, "longitude"), floats(rows, "latitude")
    depth, mag = floats(rows, "depth"), floats(rows, "mag")
    ax = thumb(fig, x0=LEFT_W + 0.3, y0=0.45, x1=W, y1=H - 0.1)
    order = np.argsort(-depth)
    sc = ax.scatter(lon[order], lat[order], c=np.log10(depth[order] + 1),
                    s=(mag[order] - 4.5) ** 2 * 4, cmap="plasma_r", lw=0, alpha=0.8)
    ax.set_xlim(-180, 180)
    ax.set_ylim(-70, 80)
    ax.set_aspect("equal")
    for side in ax.spines.values():
        side.set_visible(True)
        side.set_color(GRID)
    ax.set_xticks([])
    ax.set_yticks([])
    cb = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.01, ticks=[1, 2, 3])
    cb.ax.set_yticklabels(["10", "100", "1000"])
    cb.set_label("depth (km)", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    thumb_caption(fig, f"{len(rows):,} events of magnitude ≥ 5 in 2025", y=0.28)


@figure("ds_velib")
def ds_velib(fig):
    card(
        fig,
        "Real time availability of bikes and docks at the Vélib' stations "
        "of 55 municipalities around Paris.",
        "about 1,400 stations, snapshots every minute",
        "numerical counts, coordinates, timestamps, categorical",
        "JSON (API, GBFS standard), CSV export",
        "opendata.paris.fr (history on GitHub)",
    )
    rows = read_csv(fetch(
        "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/"
        "velib-disponibilite-en-temps-reel/exports/csv?delimiter=%3B",
        "velib_snapshot.csv",
    ), delimiter=";")
    rows = [r for r in rows if r["coordonnees_geo"] and r["is_installed"] == "OUI"]
    lat, lon = np.array([[float(v) for v in r["coordonnees_geo"].split(",")]
                         for r in rows]).T
    cap = floats(rows, "capacity")
    fill = floats(rows, "numbikesavailable") / np.maximum(cap, 1)
    when = max(r["duedate"] for r in rows)[:16].replace("T", " ")
    ax = thumb(fig, x0=LEFT_W + 0.5, y0=0.45, x1=W - 0.1)
    sc = ax.scatter(lon, lat, c=np.clip(fill, 0, 1), s=cap / 5, cmap="RdYlGn",
                    vmin=0, vmax=1, lw=0)
    ax.set_aspect(1 / np.cos(np.deg2rad(48.86)))
    blank(ax)
    cb = fig.colorbar(sc, ax=ax, shrink=0.8, pad=0.02)
    cb.set_label("share of docks holding a bike", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    thumb_caption(fig, f"{len(rows):,} stations, snapshot of {when} UTC", y=0.25)


def _xlsx_head(path, n):
    """First n rows of the first sheet of an .xlsx, without openpyxl."""
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    with zipfile.ZipFile(path) as z:
        strings = [
            "".join(t.text or "" for t in si.iter(ns + "t"))
            for si in ElementTree.parse(z.open("xl/sharedStrings.xml")).getroot()
        ]
        rows = []
        for _, el in ElementTree.iterparse(z.open("xl/worksheets/sheet1.xml")):
            if el.tag != ns + "row":
                continue
            row = []
            for c in el.iter(ns + "c"):
                v = c.find(ns + "v")
                v = "" if v is None else v.text
                row.append(strings[int(v)] if c.get("t") == "s" else v)
            rows.append(row)
            if len(rows) == n:
                break
    return rows


@figure("ds_online_retail")
def ds_online_retail(fig):
    ax = card(
        fig,
        "All transactions of a UK online gift retailer, 2009 to 2011. Each "
        "line is one product of one invoice.",
        "about 1,067,000 invoice lines, 8 columns",
        "mixed: numerical, categorical, dates, text descriptions",
        "XLSX",
        "UCI Machine Learning Repository",
    )
    head = CACHE / "online_retail_ii_head.json"
    if not head.exists():
        outer = fetch("https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip",
                      "online_retail_ii.zip")
        with zipfile.ZipFile(outer) as z:
            name = next(n for n in z.namelist() if n.endswith(".xlsx"))
            xlsx = io.BytesIO(z.read(name))
        head.write_text(json.dumps(_xlsx_head(xlsx, 9)))
    header, *rows = json.loads(head.read_text())
    base = np.datetime64("1899-12-30")
    shown = []
    for r in rows:
        date = str(base + np.timedelta64(round(float(r[4]) * 1440), "m"))
        shown.append([
            r[0], r[1], textwrap.shorten(r[2].title(), 21, placeholder="…"), r[3],
            date[:10], f"{float(r[5]):.2f}", r[6], r[7],
        ])
    header = ["Invoice", "Stock", "Description", "Qty", "Date", "Price", "Cust.",
              "Country"]
    table(ax, header, shown, LEFT_W + 0.3, W - 0.05, H - 0.45,
          [0.45, 0.45, 1.3, 0.28, 0.7, 0.38, 0.45, 0.8], size=8)
    thumb_caption(fig, "first 8 invoice lines (December 2009)", y=0.45)


@figure("ds_wholesale")
def ds_wholesale(fig):
    card(
        fig,
        "Annual spending of the clients of a Portuguese wholesale "
        "distributor on six product categories, plus channel and region.",
        "440 clients, 8 variables",
        "continuous numerical, categorical",
        "CSV",
        "UCI Machine Learning Repository",
    )
    rows = read_csv(fetch(
        "https://archive.ics.uci.edu/ml/machine-learning-databases/00292/"
        "Wholesale%20customers%20data.csv",
        "wholesale.csv",
    ))
    channel = floats(rows, "Channel")
    fresh, grocery = floats(rows, "Fresh"), floats(rows, "Grocery")
    ax = thumb(fig)
    for k, name, color in [(1, "hotel / restaurant / café", GOLD), (2, "retail", PURPLE)]:
        m = channel == k
        ax.scatter(fresh[m], grocery[m], s=12, color=color, alpha=0.7, lw=0, label=name)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend(loc="lower left")
    style(ax, "fresh products (m.u. / year)", "grocery (m.u. / year)")


@figure("ds_newsgroups")
def ds_newsgroups(fig):
    from sklearn.datasets import fetch_20newsgroups

    ax = card(
        fig,
        "Posts from 20 Usenet discussion groups: computers, sport, religion, "
        "politics, science, ... A standard text corpus.",
        "about 18,800 documents, 20 categories",
        "text, categorical label",
        "tar.gz of plain text files, built into scikit-learn",
        "qwone.com/~jason/20Newsgroups",
    )
    d = fetch_20newsgroups(subset="train", categories=["sci.space"],
                           remove=("headers", "footers", "quotes"),
                           data_home=CACHE / "sklearn")
    post = " ".join(d.data[49].split())  # a short, self-contained post
    x0 = LEFT_W + 0.45
    ax.text(x0, H - 0.3, "sci.space", color=BLUE, fontsize=11, weight="bold",
            ha="left", va="top")
    y = H - 0.62
    for line in textwrap.wrap(post, 52)[:6]:
        ax.text(x0, y, line, color=INK, fontsize=9.5, ha="left", va="top",
                family="monospace")
        y -= 0.21
    groups = fetch_20newsgroups(subset="train", data_home=CACHE / "sklearn").target_names
    tops = sorted({g.split(".")[0] for g in groups})
    colors = {t: CYCLE[i % len(CYCLE)] for i, t in enumerate(tops)}
    y -= 0.2
    for i, g in enumerate(groups):
        col, row = i % 3, i // 3
        ax.text(x0 + col * 1.6, y - row * 0.2, g, fontsize=8.5,
                color=colors[g.split(".")[0]], ha="left", va="top")


@figure("ds_olivetti")
def ds_olivetti(fig):
    from sklearn.datasets import fetch_olivetti_faces

    card(
        fig,
        "Grey level face images under varying expression, lighting and "
        "small pose changes.",
        "400 images, 40 people, 10 images each, 64×64 pixels",
        "images (grey level intensities), identity label",
        "PGM images; NumPy arrays via scikit-learn",
        "AT&T / Cambridge, fetch_olivetti_faces",
    )
    d = fetch_olivetti_faces(data_home=CACHE / "sklearn")
    axes, _ = grid(fig, 3, 7)
    for i, person in enumerate([0, 12, 30]):
        for j in range(7):
            axes[i][j].imshow(d.images[person * 10 + j], cmap="gray")


@figure("ds_movielens")
def ds_movielens(fig):
    card(
        fig,
        "Movie ratings from 1 to 5 stars collected by the MovieLens "
        "recommender site, with user and movie metadata.",
        "100,000 ratings, 943 users, 1,682 movies",
        "integer ratings, timestamps, categorical metadata",
        "ZIP of tab or pipe separated text files",
        "GroupLens",
    )
    with zipfile.ZipFile(fetch("https://files.grouplens.org/datasets/movielens/ml-100k.zip",
                               "ml-100k.zip")) as z:
        r = np.loadtxt(z.open("ml-100k/u.data"), dtype=int)
    users, movies = 943, 1682
    R = np.full((users, movies), np.nan)
    R[r[:, 0] - 1, r[:, 1] - 1] = r[:, 2]
    ax = thumb(fig, x0=LEFT_W + 0.6, y0=0.55, y1=H - 0.45)
    shown = R[:120, :300]
    cmap = plt.get_cmap("viridis", 5).with_extremes(bad="white")
    im = ax.imshow(shown, aspect="auto", cmap=cmap, vmin=0.5, vmax=5.5,
                   interpolation="nearest")
    cb = fig.colorbar(im, ax=ax, ticks=range(1, 6), pad=0.02, shrink=0.85)
    cb.set_label("stars", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    style(ax, "movie", "user")
    empty = 1 - len(r) / (users * movies)
    ax.set_title(f"first 120 users × 300 movies: {empty:.1%} of the full matrix is empty",
                 fontsize=10, color=MUTED, pad=6)


@figure("ds_galaxies")
def ds_galaxies(fig):
    card(
        fig,
        "Velocities of 82 galaxies of the Corona Borealis region (Roeder, "
        "1990). How many clusters of galaxies are there?",
        "82 observations, 1 variable",
        "continuous numerical",
        "CSV",
        "Rdatasets, MASS::galaxies",
    )
    rows = read_csv(fetch(
        "https://vincentarelbundock.github.io/Rdatasets/csv/MASS/galaxies.csv",
        "galaxies.csv",
    ))
    v = floats(rows, "dat") / 1000
    ax = thumb(fig)
    ax.hist(v, bins=np.arange(8, 36, 1), color=BLUE, alpha=0.85, edgecolor="white")
    ax.plot(v, np.full_like(v, -0.4), "|", color=INK, ms=8)
    ax.set_ylim(-0.9, None)
    style(ax, "velocity (1000 km/s)", "galaxies")


@figure("ds_penguins")
def ds_penguins(fig):
    card(
        fig,
        "Morphological measurements (bill, flipper, body mass) of three "
        "penguin species on three islands of the Palmer Archipelago.",
        "344 penguins, 8 variables",
        "continuous numerical, categorical",
        "CSV",
        "github.com/allisonhorst/palmerpenguins",
    )
    rows = read_csv(fetch(
        "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/"
        "extdata/penguins.csv",
        "penguins.csv",
    ))
    rows = [r for r in rows if r["bill_length_mm"] != "NA"]
    ax = thumb(fig)
    for sp, color in [("Adelie", GOLD), ("Chinstrap", PURPLE), ("Gentoo", GREEN)]:
        s = [r for r in rows if r["species"] == sp]
        ax.scatter(floats(s, "bill_length_mm"), floats(s, "bill_depth_mm"), s=14,
                   color=color, alpha=0.75, lw=0, label=sp)
    ax.legend(loc="lower left")
    style(ax, "bill length (mm)", "bill depth (mm)")


@figure("ds_bsds")
def ds_bsds(fig):
    from scipy.io import loadmat

    card(
        fig,
        "Benchmark for image segmentation and contour detection: natural "
        "images, each segmented by several people.",
        "500 natural images, several human segmentations each",
        "images (RGB pixels), segmentation maps",
        "JPG images, MATLAB .mat ground truth",
        "Berkeley Computer Vision Group",
    )
    stem = "100007"
    img_p, gt_p = CACHE / f"bsds_{stem}.jpg", CACHE / f"bsds_{stem}.mat"
    if not img_p.exists():
        tgz = fetch("https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/"
                    "grouping/BSR/BSR_bsds500.tgz", "BSR_bsds500.tgz")
        with tarfile.open(tgz) as t:
            for m in t:
                if m.name.endswith(f"images/test/{stem}.jpg"):
                    img_p.write_bytes(t.extractfile(m).read())
                elif m.name.endswith(f"groundTruth/test/{stem}.mat"):
                    gt_p.write_bytes(t.extractfile(m).read())
    img = plt.imread(img_p)
    gts = loadmat(gt_p)["groundTruth"][0]
    seg = gts[0]["Segmentation"][0, 0]
    bnd = sum(g["Boundaries"][0, 0].astype(float) for g in gts) / len(gts)
    # the image large on the left, two ground truths stacked on the right
    r = img.shape[0] / img.shape[1]
    x0, gap, title = LEFT_W + 0.4, 0.12, 0.25
    h = min(((W - 0.15 - x0 - gap) * r - gap - title) / 3,
            (H - 0.4 - 2 * title - gap) / 2)
    big = 2 * h + gap + title
    y0 = (H - big - title) / 2
    panels = [
        (img, {}, "image", (x0, y0, big / r, big)),
        (seg, {"cmap": "tab20", "interpolation": "nearest"}, "a human segmentation",
         (x0 + big / r + gap, y0 + h + gap + title, h / r, h)),
        (1 - bnd, {"cmap": "gray"}, f"boundaries, {len(gts)} people",
         (x0 + big / r + gap, y0, h / r, h)),
    ]
    for data, kw, title, (x, y, w, h) in panels:
        a = fig.add_axes([x / W, y / H, w / W, h / H])
        a.imshow(data, **kw)
        blank(a)
        a.set_title(title, fontsize=9, color=MUTED, pad=3)


@figure("ds_fashion_mnist")
def ds_fashion_mnist(fig):
    card(
        fig,
        "Grey level images of Zalando clothing items: a drop-in replacement "
        "for MNIST, harder and less saturated.",
        "70,000 images (60,000 train, 10,000 test), 28×28 pixels, 10 classes",
        "images (intensities 0 to 255), class label",
        "gzip IDX binary, also on OpenML",
        "github.com/zalandoresearch/fashion-mnist",
    )
    base = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
    with gzip.open(fetch(base + "t10k-images-idx3-ubyte.gz", "fmnist_t10k_img.gz")) as f:
        X = np.frombuffer(f.read(), np.uint8, offset=16).reshape(-1, 28, 28)
    with gzip.open(fetch(base + "t10k-labels-idx1-ubyte.gz", "fmnist_t10k_lbl.gz")) as f:
        y = np.frombuffer(f.read(), np.uint8, offset=8)
    names = ["T-shirt", "trouser", "pullover", "dress", "coat", "sandal", "shirt",
             "sneaker", "bag", "boot"]
    axes, _ = grid(fig, 3, 10, y1=H - 0.45)
    for k in range(10):
        idx = np.flatnonzero(y == k)[:3]
        for i, j in enumerate(idx):
            axes[i][k].imshow(X[j], cmap="gray_r")
        axes[0][k].set_title(names[k], fontsize=8.5, color=MUTED, pad=3)


@figure("ds_pbmc")
def ds_pbmc(fig):
    card(
        fig,
        "Single cell RNA sequencing: gene expression of peripheral blood "
        "mononuclear cells from a healthy donor (10x Genomics).",
        "about 2,700 cells, about 32,700 genes",
        "integer counts (sparse matrix), gene and cell identifiers",
        "Matrix Market + TSV in a tar.gz, or scanpy.datasets.pbmc3k()",
        "10x Genomics",
    )
    small = CACHE / "pbmc3k_dense_head.npz"
    if not small.exists():
        from scipy.io import mmread

        tgz = fetch("https://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/"
                    "pbmc3k_filtered_gene_bc_matrices.tar.gz", "pbmc3k.tar.gz")
        with tarfile.open(tgz) as t:
            m = next(m for m in t if m.name.endswith("matrix.mtx"))
            M = mmread(io.BytesIO(t.extractfile(m).read())).tocsr()  # genes x cells
        genes, cells = M.shape
        nnz = M.nnz
        rng = np.random.default_rng(0)
        expressed = np.flatnonzero(np.asarray(M.sum(1)).ravel() > 0.5 * cells)
        g = np.sort(rng.choice(expressed, 60, replace=False))
        c = np.sort(rng.choice(cells, 150, replace=False))
        np.savez(small, X=M[g][:, c].toarray(), shape=[genes, cells, nnz])
    d = np.load(small)
    genes, cells, nnz = d["shape"]
    X = np.ma.masked_equal(d["X"], 0)
    ax = thumb(fig, x0=LEFT_W + 0.6, y0=0.35, y1=H - 0.45)
    cmap = plt.get_cmap("magma_r").with_extremes(bad="white")
    im = ax.imshow(np.ma.log2(X + 0), aspect="auto", cmap=cmap, interpolation="nearest",
                   vmin=0)
    cb = fig.colorbar(im, ax=ax, pad=0.02, shrink=0.85)
    cb.set_label("log₂ UMI count", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    style(ax, "cell", "gene")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"150 cells × 60 commonly expressed genes; "
                 f"{1 - nnz / (genes * cells):.1%} of the full matrix is zero",
                 fontsize=10, color=MUTED, pad=6)


@figure("ds_har")
def ds_har(fig):
    card(
        fig,
        "Activity recognition from smartphone accelerometer and gyroscope "
        "signals: walking, upstairs, downstairs, sitting, standing, lying.",
        "10,299 samples, 561 features, 6 activities, 30 subjects",
        "continuous numerical, raw time series, class and subject labels",
        "ZIP of space separated text files",
        "UCI Machine Learning Repository",
    )
    small = CACHE / "har_body_acc_x_examples.npy"
    if not small.exists():
        outer = fetch("https://archive.ics.uci.edu/static/public/240/"
                      "human+activity+recognition+using+smartphones.zip", "har.zip")
        with zipfile.ZipFile(outer) as z:
            inner = zipfile.ZipFile(io.BytesIO(z.read("UCI HAR Dataset.zip")))
        y = np.loadtxt(inner.open("UCI HAR Dataset/train/y_train.txt"), dtype=int)
        acc = np.loadtxt(inner.open(
            "UCI HAR Dataset/train/Inertial Signals/total_acc_x_train.txt"))
        np.save(small, np.stack([acc[np.flatnonzero(y == k)[10]] for k in range(1, 7)]))
    sig = np.load(small)
    names = ["walking", "upstairs", "downstairs", "sitting", "standing", "lying"]
    colors = [BLUE, GREEN, RED, PURPLE, GOLD, MUTED]
    ax = thumb(fig, y0=0.5, y1=H - 0.45)
    t = np.arange(sig.shape[1]) / 50
    for k in range(6):
        s = sig[k] - sig[k].mean()
        ax.plot(t, s - 1.2 * k, color=colors[k], lw=1.3)
        ax.text(t[-1] + 0.08, -1.2 * k, names[k], color=colors[k], fontsize=9.5,
                va="center")
    ax.set_xlim(0, t[-1] + 0.9)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    style(ax, "time (s), one 2.56 s window per activity", None)
    ax.set_title("raw acceleration along x (centred)", fontsize=10, color=MUTED, pad=4)


@figure("ds_coil20")
def ds_coil20(fig):
    card(
        fig,
        "Grey level images of 20 objects, each photographed every 5° while "
        "rotating on a turntable.",
        "1,440 images, 20 objects, 72 poses each, 128×128 pixels",
        "images (pixel intensities), object and pose labels",
        "PNG images",
        "Columbia University, CAVE",
    )
    z = zipfile.ZipFile(fetch(
        "https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/"
        "coil-20-proc.zip", "coil-20-proc.zip"))
    names = {Path(n).name: n for n in z.namelist() if n.endswith(".png")}

    def img(obj, pose):
        return plt.imread(io.BytesIO(z.read(names[f"obj{obj}__{pose}.png"])))

    axes, _ = grid(fig, 3, 10, y0=0.7, gap=0.06)
    for j in range(10):
        axes[0][j].imshow(img(j + 1, 0), cmap="gray", vmin=0, vmax=1)
        axes[1][j].imshow(img(j + 11, 0), cmap="gray", vmin=0, vmax=1)
        axes[2][j].imshow(img(5, j * 7), cmap="gray", vmin=0, vmax=1)
    thumb_caption(fig, "rows 1-2: the 20 objects · row 3: object 5, every 35°", y=0.45)


# ==========================================================================
# driver
# ==========================================================================
def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course01/img")
    out.mkdir(parents=True, exist_ok=True)
    wanted = argv[2:] or list(FIGURES)
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
