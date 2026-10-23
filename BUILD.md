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
```

## Building

```
make figures     # only what changed
make slides      # CourseNN/slides.md -> CourseNN/slides.pptx
make clean-slides clean-figures
```

`make interactive` serves Course03's interactive companion deck (sliders for C,
gamma, epsilon, the kernel), `make interactive-bis` the trees-and-boosting one
(depth, max_features, M, eta, lambda, gamma, bins), and `make interactive-c04`
Course04's clustering one (K, the linkage and the cut, epsilon, MinPts, C_min).
`make interactive-build` writes all three published copies, the single
self-contained files `Course03/interactive.html`,
`Course03/interactive-bis.html` and `Course04/interactive.html`, which **are
committed**: the Pages workflow uploads the repository as it stands and never
runs a build, so a deck is only as fresh as the last `make interactive-build`
that was committed. They are served at
<https://pauldubois98.github.io/AdvancedMachineLearning2026/Course03/interactive.html>,
<https://pauldubois98.github.io/AdvancedMachineLearning2026/Course03/interactive-bis.html>
and <https://pauldubois98.github.io/AdvancedMachineLearning2026/Course04/interactive.html>,
and the same files open offline by double-clicking them.
All three need `node` and `npm`; see `Course03/slidev/README.md` and
`Course04/slidev/README.md`. The two projects are independent: rebuilding one
never touches the other.

Course05's figures read the Olivetti faces and 20 Newsgroups from the same `.cache/datasets/sklearn/` that Course01 fills; everything else they draw is computed in the script.

`make slides` needs `pandoc`; the figures need `numpy`, `matplotlib`, `scipy`, `scikit-learn` and the Lato font (`fonts-lato`).
The `ds_*` figures are drawn from the real datasets: the first build downloads them (about 370 MB) into `.cache/datasets/`, later builds reuse that cache.

## Adding a course

1. `CourseNN/slides.md` with the same YAML header and `#` / `##` structure.
2. `scripts/make_figures_cNN.py` — copy the helpers from `c01`.
3. In the `Makefile`: a `CNN_STEMS` list, the rule that builds them, and `CourseNN/slides.pptx: $(CNN_FIGURES)`.
