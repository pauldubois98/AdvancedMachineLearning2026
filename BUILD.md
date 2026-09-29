# Advanced Machine Learning — MSc DSBA, CentraleSupélec

## Layout

```
CourseNN/slides.md        the deck, one h2 per slide, one figure per slide
CourseNN/img/*.png        generated — never edited by hand
scripts/make_figures_cNN.py   every figure of course NN, one function per stem
scripts/fit_pptx.py       post-processes pandoc's output (autofit, centred statements)
Makefile                  figures -> pptx
```

## Building

```
make figures     # only what changed
make slides      # CourseNN/slides.md -> CourseNN/slides.pptx
make clean-slides clean-figures
```

`make slides` needs `pandoc`; the figures need `numpy`, `matplotlib`, `scipy`,
`scikit-learn` and the Lato font (`fonts-lato`).

## Adding a course

1. `CourseNN/slides.md` with the same YAML header and `#` / `##` structure.
2. `scripts/make_figures_cNN.py` — copy the helpers from `c01`.
3. In the `Makefile`: a `CNN_STEMS` list, the rule that builds them, and
   `CourseNN/slides.pptx: $(CNN_FIGURES)`.
