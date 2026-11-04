#!/usr/bin/env python3
"""The data Course01's interactive deck reads, written as JSON.

    python3 scripts/make_data_c01.py Course01/data

digits.json  scikit-learn's 1797 handwritten digits (8 x 8 pixels, values
             0-16), the data of the printed "PCA: how much can be dropped"
             figure, so the browser runs the same PCA on the same pixels.
"""

import json
import sys
from pathlib import Path


def main(argv):
    from sklearn.datasets import load_digits

    out = Path(argv[1] if len(argv) > 1 else "Course01/data")
    out.mkdir(parents=True, exist_ok=True)
    d = load_digits()
    (out / "digits.json").write_text(json.dumps(
        {"X": d.data.astype(int).tolist(), "y": d.target.astype(int).tolist()},
        separators=(",", ":")))
    print("  digits.json")


if __name__ == "__main__":
    main(sys.argv)
