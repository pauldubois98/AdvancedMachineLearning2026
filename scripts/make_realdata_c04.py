#!/usr/bin/env python3
"""The real datasets behind Course04's use-case slides, as small JSON files.

Both decks read these files: the printed figures (make_figures_c04.py) and the
interactive deck (Course04/slidev), so the two show the same rows. The files are
committed, and this script only needs re-running to change the samples; it
downloads the raw data, so it needs a network connection.

    python3 scripts/make_realdata_c04.py Course04/data

- flower.json      scikit-learn's sample photo flower.jpg, shrunk to 160 x 107,
                   as base64 RGB bytes (flickr/vultilion, CC BY 2.0)
- newsgroups.json  1000 posts from four newsgroups of 20 Newsgroups, as sparse
                   l2-normalised TF-IDF rows over a 500-word vocabulary
- http.json        1230 HTTP connections of the KDD Cup 99 logs, 30 of them
                   attacks, as log(duration), log(bytes in), log(bytes out)
"""

import base64
import json
import sys
from pathlib import Path

import numpy as np

NEWSGROUPS = ["comp.graphics", "rec.sport.hockey", "sci.space", "soc.religion.christian"]
# words every group uses, which only blur the four topics apart
GENERIC = {"just", "like", "don", "know", "think", "does", "did", "good", "use", "used",
           "way", "time", "make", "really", "want", "say", "said", "going", "thing",
           "things", "people", "lot", "sure", "need", "doesn", "didn", "isn", "ve",
           "got", "let", "thanks", "anybody", "anyone", "post", "edu", "com"}


def flower(out):
    from PIL import Image
    from sklearn.datasets import load_sample_image

    img = Image.fromarray(load_sample_image("flower.jpg")).resize((160, 107), Image.LANCZOS)
    px = np.asarray(img, dtype=np.uint8)
    json.dump({
        "source": "scikit-learn sample image flower.jpg, flickr/vultilion, CC BY 2.0",
        "width": px.shape[1], "height": px.shape[0],
        "rgb": base64.b64encode(px.tobytes()).decode(),
    }, out, separators=(",", ":"))


def newsgroups(out, data_home):
    from sklearn.datasets import fetch_20newsgroups
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

    ng = fetch_20newsgroups(data_home=data_home, subset="train", categories=NEWSGROUPS,
                            remove=("headers", "footers", "quotes"))
    rng = np.random.default_rng(0)
    long = np.array([len(d.split()) >= 40 for d in ng.data])
    pick = np.concatenate([
        rng.choice(np.where(long & (ng.target == g))[0], 250, replace=False)
        for g in range(len(NEWSGROUPS))
    ])
    docs = [ng.data[i] for i in pick]
    tf = TfidfVectorizer(max_features=500, stop_words=list(ENGLISH_STOP_WORDS | GENERIC),
                         min_df=5, max_df=0.3, sublinear_tf=True,
                         token_pattern=r"(?u)\b[a-zA-Z]{3,}\b")
    T = tf.fit_transform(docs).tocsr()
    rows = []
    for r in range(T.shape[0]):
        lo, hi = T.indptr[r], T.indptr[r + 1]
        rows.append([T.indices[lo:hi].tolist(), np.round(T.data[lo:hi], 4).tolist()])
    json.dump({
        "source": "20 Newsgroups (Lang 1995), training set, headers and quotes removed",
        "groups": [ng.target_names[g] for g in range(len(NEWSGROUPS))],
        "group": ng.target[pick].tolist(),
        "vocab": tf.get_feature_names_out().tolist(),
        "rows": rows,
    }, out, separators=(",", ":"))


def http(out, data_home):
    from sklearn.datasets import fetch_kddcup99

    kdd = fetch_kddcup99(data_home=data_home, subset="http", percent10=True, random_state=0)
    X = kdd.data.astype(float)
    attack = kdd.target != b"normal."
    rng = np.random.default_rng(1)
    pick = np.concatenate([
        rng.choice(np.where(~attack)[0], 1200, replace=False),
        rng.choice(np.where(attack)[0], 30, replace=False),
    ])
    json.dump({
        "source": "KDD Cup 1999, 10% sample, http connections (scikit-learn's log transform)",
        "features": ["log duration", "log bytes from the client", "log bytes back"],
        "X": np.round(X[pick], 4).tolist(),
        "attack": attack[pick].astype(int).tolist(),
        "kind": [t.decode().rstrip(".") for t in kdd.target[pick]],
    }, out, separators=(",", ":"))


def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course04/data")
    out.mkdir(parents=True, exist_ok=True)
    cache = str(Path.home() / "scikit_learn_data")
    for name, make in [("flower", flower),
                       ("newsgroups", lambda f: newsgroups(f, cache)),
                       ("http", lambda f: http(f, cache))]:
        with open(out / f"{name}.json", "w") as f:
            make(f)
        print(f"  {name}.json")


if __name__ == "__main__":
    main(sys.argv)
