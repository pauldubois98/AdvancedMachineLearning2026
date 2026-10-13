# Advanced Machine Learning — MSc DSBA, CentraleSupélec

## Layout

```
CourseNN/slides.md        the deck, one h2 per slide, one figure per slide
CourseNN/img/*.png        generated — never edited by hand
scripts/make_figures_cNN.py   every figure of course NN, one function per stem
scripts/make_figures_datasets.py   Course01's suggested-dataset slides (ds_*)
scripts/fit_pptx.py       post-processes pandoc's output (autofit, centred statements)
Makefile                  figures -> pptx
Course03/slidev/          Course03 as an interactive Slidev deck (npm)
```

## Building

```
make figures     # only what changed
make slides      # CourseNN/slides.md -> CourseNN/slides.pptx
make clean-slides clean-figures
```

`make interactive` serves Course03's interactive companion deck (sliders for C,
gamma, epsilon, the kernel). `make interactive-build` writes the published copy,
a single self-contained `Course03/interactive.html`, which **is committed**: the Pages workflow uploads the repository as it stands and never
runs a build, so the deck is only as fresh as the last `make interactive-build`
that was committed. It is served at
<https://pauldubois98.github.io/AdvancedMachineLearning2026/Course03/interactive.html>,
and the same file opens offline by double-clicking it.
Both need `node` and `npm`; see `Course03/slidev/README.md`.

`make slides` needs `pandoc`; the figures need `numpy`, `matplotlib`, `scipy`, `scikit-learn` and the Lato font (`fonts-lato`).
The `ds_*` figures are drawn from the real datasets: the first build downloads them (about 370 MB) into `.cache/datasets/`, later builds reuse that cache.

## Adding a course

1. `CourseNN/slides.md` with the same YAML header and `#` / `##` structure.
2. `scripts/make_figures_cNN.py` — copy the helpers from `c01`.
3. In the `Makefile`: a `CNN_STEMS` list, the rule that builds them, and `CourseNN/slides.pptx: $(CNN_FIGURES)`.
