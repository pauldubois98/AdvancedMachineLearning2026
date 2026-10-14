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
```

## Building

```
make figures     # only what changed
make slides      # CourseNN/slides.md -> CourseNN/slides.pptx
make clean-slides clean-figures
```

`make interactive` serves Course03's interactive companion deck (sliders for C,
gamma, epsilon, the kernel), `make interactive-bis` the trees-and-boosting one
(depth, max_features, M, eta, lambda, gamma, bins). `make interactive-build`
writes both published copies, the single self-contained files
`Course03/interactive.html` and `Course03/interactive-bis.html`, which **are
committed**: the Pages workflow uploads the repository as it stands and never
runs a build, so a deck is only as fresh as the last `make interactive-build`
that was committed. They are served at
<https://pauldubois98.github.io/AdvancedMachineLearning2026/Course03/interactive.html>
and <https://pauldubois98.github.io/AdvancedMachineLearning2026/Course03/interactive-bis.html>,
and the same files open offline by double-clicking them.
Both need `node` and `npm`; see `Course03/slidev/README.md`.

`make slides` needs `pandoc`; the figures need `numpy`, `matplotlib`, `scipy`, `scikit-learn` and the Lato font (`fonts-lato`).
The `ds_*` figures are drawn from the real datasets: the first build downloads them (about 370 MB) into `.cache/datasets/`, later builds reuse that cache.

## Adding a course

1. `CourseNN/slides.md` with the same YAML header and `#` / `##` structure.
2. `scripts/make_figures_cNN.py` — copy the helpers from `c01`.
3. In the `Makefile`: a `CNN_STEMS` list, the rule that builds them, and `CourseNN/slides.pptx: $(CNN_FIGURES)`.
