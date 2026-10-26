#!/usr/bin/env python3
"""The data behind Course05's interactive deck, as small JSON files.

The interactive deck refits NMF in the browser, so it needs the matrices the
printed figures are drawn from. Every toy matrix comes from the very function
make_figures_c05.py builds it with, so both decks show the same data. The
files are committed; re-run this only to change them (the faces and the posts
are fetched into .cache/ on first use, which needs a network connection).

    python3 scripts/make_data_c05.py Course05/data
    python3 scripts/make_data_c05.py Course05/data choosing   # one file only

- faces.json      400 Olivetti faces shrunk to 32 x 32, as bytes; plus the
                  16 PCA components and a rank-16 NMF of the first 300
- topics.json     1000 posts of the four newsgroups, TF-IDF over 600 words
- spectral.json   the hyperspectral toy: 60 bands, 3 spectra, 3 abundance maps
                  (the deck rebuilds X from them, with the same tiny noise)
- music.json      the spectrogram toy: 3 notes, their envelopes, and X
- layers.json     the HALS toy: X built from three rank-one layers, and its fit
- ratings.json    the ratings toy, and the uniform draws that hide its cells
- arms.json       the two-arm cloud of the initialization slide
- init.json       the loss traces of the initialization race (64 x 64 faces)
- choosing.json   rank-r fits of the 300 small faces for r = 2 ... 48: the
                  error curve, the parts and weights, and how well each part
                  comes back after a restart from another start
"""

import base64
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("figs", ROOT / "make_figures_c05.py")
figs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(figs)


def f32(a):
    """A float array as base64 little-endian float32: a quarter of the JSON."""
    return base64.b64encode(np.ascontiguousarray(a, dtype="<f4").tobytes()).decode()


def r4(a):
    return np.round(np.asarray(a, dtype=float), 4).tolist()


def dump(out, name, obj):
    with open(out / f"{name}.json", "w") as f:
        json.dump(obj, f, separators=(",", ":"))
    print(f"  {name}.json")


def faces(out):
    imgs, _ = figs._faces(400)
    small = imgs.reshape(400, 32, 2, 32, 2).mean((2, 4))  # 2 x 2 blocks
    X = small.reshape(400, -1).T                           # pixels x faces
    X300 = X[:, :300]
    U, s, Vt = np.linalg.svd(X300, full_matrices=False)
    Wn, Hn = figs._order(*figs._hals(X300, 16, 300, init="nndsvd"))
    dump(out, "faces", {
        "source": "Olivetti faces, AT&T Laboratories Cambridge; 64 x 64 shrunk to 32 x 32",
        "side": 32, "n": 400,
        "pixels": base64.b64encode(np.round(X.T * 255).astype(np.uint8).tobytes()).decode(),
        # PCA of the 300 faces, uncentred like the printed slide: U, singular values
        "pca": f32(U[:, :16].T), "pcaS": r4(s[:16]), "pcaV": f32(Vt[:16]),
        "nmfW": f32(Wn.T), "nmfH": f32(Hn),
    })


def topics(out):
    from sklearn.datasets import fetch_20newsgroups
    from sklearn.feature_extraction.text import TfidfVectorizer

    groups = ["sci.space", "rec.sport.hockey", "comp.graphics", "talk.politics.mideast"]
    d = fetch_20newsgroups(subset="train", categories=groups, data_home=figs.CACHE,
                           remove=("headers", "footers", "quotes"))
    rng = np.random.default_rng(0)
    target = np.array(d.target)
    pick = np.concatenate([rng.choice(np.where(target == g)[0], 250, replace=False)
                           for g in range(4)])
    tf = TfidfVectorizer(max_features=600, stop_words="english", min_df=5, max_df=0.5)
    T = tf.fit_transform([d.data[i] for i in pick]).tocsr()
    rows = []
    for r in range(T.shape[0]):
        lo, hi = T.indptr[r], T.indptr[r + 1]
        rows.append([T.indices[lo:hi].tolist(), np.round(T.data[lo:hi], 4).tolist()])
    dump(out, "topics", {
        "source": "20 Newsgroups (Lang 1995), training set, headers and quotes removed",
        "groups": list(d.target_names), "group": target[pick].tolist(),
        "vocab": tf.get_feature_names_out().tolist(), "rows": rows,
    })


def spectral(out):
    bands, spectra, maps, X, size = figs._spectral_toy()
    dump(out, "spectral", {
        "size": size, "bands": r4(bands), "spectra": r4(spectra.T),
        "maps": f32(maps.reshape(3, -1)),
    })


def music(out):
    freqs, notes, env, t, X = figs._music_toy()
    dump(out, "music", {"freqs": r4(freqs), "t": r4(t), "notes": r4(notes.T),
                        "env": r4(env), "X": f32(X), "p": X.shape[0], "n": X.shape[1]})


def layers(out):
    X, Wm, Hm = figs._layers_fit()
    dump(out, "layers", {"X": r4(X), "W": r4(Wm.T), "H": r4(Hm)})


def ratings(out):
    # _ratings_toy, unrolled so the uniform draws that hide the cells survive:
    # the cell is shown when u > hide, which is exactly the printed mask at 0.55
    rng = np.random.default_rng(5)
    taste = rng.random((60, 3)) ** 1.6
    profile = rng.random((3, 24)) ** 1.3
    base = 1 + 4 * (taste @ profile) / (taste @ profile).max()
    full = np.clip(np.round(base + rng.normal(0, 0.45, base.shape)), 1, 5)
    u = rng.random(full.shape)
    ref_full, ref_mask = figs._ratings_toy()
    assert np.array_equal(full.T, ref_full) and np.array_equal((u > 0.55).T, ref_mask > 0)
    dump(out, "ratings", {"full": full.T.astype(int).tolist(), "u": r4(u.T)})


def arms(out):
    rng = np.random.default_rng(3)
    n = 70
    a = np.array([[1.00, 0.30], [0.32, 1.00]]).T
    XA = np.outer(a[:, 0], 0.25 + rng.random(n) * 1.05) + rng.normal(0, 0.035, (2, n))
    XB = np.outer(a[:, 1], 0.25 + rng.random(n) * 1.05) + rng.normal(0, 0.035, (2, n))
    dump(out, "arms", {"X": r4(np.maximum(np.c_[XA, XB], 1e-3))})


def init(out):
    _, Xf = figs._faces(200)
    X = Xf.T
    r, iters = 10, 150
    runs = {f"random {s + 1}": figs._mu(X, r, iters, seed=s, trace=True)[2] for s in range(5)}
    for how in ("constant", "nndsvd", "cols", "kmeans"):
        runs[how] = figs._mu(X, r, iters, init=how, trace=True)[2]
    dump(out, "init", {"faces": 200, "r": r, "traces": {k: r4(v) for k, v in runs.items()}})


def choosing(out):
    # the printed choosing_r slide, on the 32 x 32 faces: HALS from NNDSVD,
    # 150 passes per r. Each part is matched (Hungarian, cosine) to the parts
    # of a second fit from a random start: a part that does not come back is
    # one a restart would not find again.
    from scipy.optimize import linear_sum_assignment

    imgs, _ = figs._faces(300)
    X = imgs.reshape(300, 32, 2, 32, 2).mean((2, 4)).reshape(300, -1).T
    fits = []
    for r in (2, 4, 8, 12, 16, 24, 32, 48):
        Wm, Hm = figs._order(*figs._hals(X, r, 150, init="nndsvd"))
        Wb, _ = figs._hals(X, r, 150, seed=1)
        unit = lambda M: M / np.maximum(np.linalg.norm(M, axis=0), 1e-12)
        cos = unit(Wm).T @ unit(Wb)
        rows, cols = linear_sum_assignment(-cos)
        match = np.empty(r)
        match[rows] = cos[rows, cols]
        top = Wm.max(axis=0)
        fits.append({
            "r": r, "err": round(float(np.linalg.norm(X - Wm @ Hm) / np.linalg.norm(X)), 5),
            # parts as bytes, each scaled to its own max; that max goes into H
            "W": base64.b64encode(np.round(255 * Wm / top).T.astype(np.uint8).tobytes()).decode(),
            "H": f32(Hm * top[:, None]), "match": r4(match),
        })
        print(f"    r = {r}: {fits[-1]['err']:.4f}, stable {np.mean(match > 0.8):.2f}")
    dump(out, "choosing", {"faces": 300, "side": 32, "fits": fits})


def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course05/data")
    out.mkdir(parents=True, exist_ok=True)
    only = set(argv[2:])
    for make in (faces, topics, spectral, music, layers, ratings, arms, init, choosing):
        if not only or make.__name__ in only:
            make(out)


if __name__ == "__main__":
    main(sys.argv)
