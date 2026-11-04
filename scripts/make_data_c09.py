#!/usr/bin/env python3
"""The data Course09's interactive deck reads, written as JSON.

    python3 scripts/make_data_c09.py Course09/data

digits600.json   the 600 handwritten digits the printed SNE-vs-t-SNE figure
                 uses (scikit-learn's 8 x 8 digits, the same random subset),
                 so the browser runs SNE and t-SNE on exactly that data.
mnist_maps.json  5000 MNIST test images mapped by PCA and by t-SNE at three
                 perplexities: t-SNE on 5000 points is too slow for a slide,
                 so these maps are computed here.  Coordinates are stored as
                 integers, tenths of a unit.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_figures_c09 as c09  # noqa: E402  (same loaders, same subsets)

PERPS = (5, 30, 100)


def main(argv):
    out = Path(argv[1] if len(argv) > 1 else "Course09/data")
    out.mkdir(parents=True, exist_ok=True)

    X, y = c09._digits_subset()
    (out / "digits600.json").write_text(json.dumps(
        {"X": X.astype(int).tolist(), "y": y.astype(int).tolist()},
        separators=(",", ":")))
    print("  digits600.json")

    from sklearn.manifold import TSNE
    Z, labels = c09._mnist_pca50()
    maps = {"pca": Z[:, :2]}
    for p in PERPS:
        maps[f"tsne{p}"] = TSNE(n_components=2, perplexity=p, random_state=0,
                                init="pca", learning_rate="auto").fit_transform(Z)
    enc = {k: np.round(v * 10).astype(int).ravel().tolist() for k, v in maps.items()}
    (out / "mnist_maps.json").write_text(json.dumps(
        {"y": labels.astype(int).tolist(), "perps": list(PERPS), **enc},
        separators=(",", ":")))
    print("  mnist_maps.json")


if __name__ == "__main__":
    main(sys.argv)
