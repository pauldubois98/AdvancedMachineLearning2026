# Advanced Machine Learning — MSc DSBA, CentraleSupélec

## Layout

```
CourseNN/slides.md        the deck, one h2 per slide, one figure per slide
CourseNN/img/*.png        generated — never edited by hand
scripts/make_figures_cNN.py   every figure of course NN, one function per stem
scripts/make_figures_datasets.py   Course01's suggested-dataset slides (ds_*)
scripts/fit_pptx.py       post-processes pandoc's output (autofit, centred statements)
Makefile                  figures -> pptx
Course03/slidev/          Course03's two lectures as interactive Slidev decks (npm)
Course04/slidev/          Course04's lecture as an interactive Slidev deck (npm)
Course05/slidev/, Course06/slidev/   the same, for Course05 and Course06
```

## Building

```
make figures     # only what changed
make slides      # CourseNN/slides.md -> CourseNN/slides.pptx
make clean-slides clean-figures
```

`make interactive` serves Course03's interactive companion deck (sliders for C,
gamma, epsilon, the kernel), `make interactive-bis` the trees-and-boosting one
(depth, max_features, M, eta, lambda, gamma, bins), `make interactive-c04`
Course04's clustering one (K, the linkage and the cut, epsilon, MinPts, C_min),
`make interactive-c05` Course05's NMF one (r, the loss, beta, the start, the
mask, lambda, MU against ALS and HALS), and `make interactive-c06` Course06's
mixtures-and-EM one (the weights, means and widths, K, the start, the pass of
EM, N for N-SEM, the covariance family, n for BIC).
`make interactive-build` writes all five published copies, the single
self-contained files `Course03/interactive.html`,
`Course03/interactive-bis.html`, `Course04/interactive.html`,
`Course05/interactive.html` and `Course06/interactive.html`, which **are
committed**: the Pages workflow uploads the repository as it stands and never
runs a build, so a deck is only as fresh as the last `make interactive-build`
that was committed. They are served at
<https://pauldubois98.github.io/AdvancedMachineLearning2026/Course03/interactive.html>,
<https://pauldubois98.github.io/AdvancedMachineLearning2026/Course03/interactive-bis.html>,
<https://pauldubois98.github.io/AdvancedMachineLearning2026/Course04/interactive.html>,
<https://pauldubois98.github.io/AdvancedMachineLearning2026/Course05/interactive.html>
and <https://pauldubois98.github.io/AdvancedMachineLearning2026/Course06/interactive.html>,
and the same files open offline by double-clicking them.
All five need `node` and `npm`; see `Course03/slidev/README.md`,
`Course04/slidev/README.md`, `Course05/slidev/README.md` and
`Course06/slidev/README.md`. The four projects
are independent: rebuilding one never touches the others.

Course05's interactive deck reads `Course05/data/*.json`, which
`scripts/make_data_c05.py` writes from the same generators as the printed
figures (and from the faces and posts in `.cache/`). Those files are committed,
so the deck builds without the cache.

Course05's figures read the Olivetti faces and 20 Newsgroups from the same `.cache/datasets/sklearn/` that Course01 fills; everything else they draw is computed in the script.

Course06's figures need no download: the animal-length table of the 2023 lecture is in the script, Fisher's iris ships with scikit-learn, and everything else is simulated.

`make slides` needs `pandoc`; the figures need `numpy`, `matplotlib`, `scipy`, `scikit-learn` and the Lato font (`fonts-lato`).
The `ds_*` figures are drawn from the real datasets: the first build downloads them (about 370 MB) into `.cache/datasets/`, later builds reuse that cache.

## Adding a course

1. `CourseNN/slides.md` with the same YAML header and `#` / `##` structure.
2. `scripts/make_figures_cNN.py` — copy the helpers from `c01`.
3. In the `Makefile`: a `CNN_STEMS` list, the rule that builds them, and `CourseNN/slides.pptx: $(CNN_FIGURES)`.
