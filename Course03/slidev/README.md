# Session 3 — Support Vector Machines, interactive

The same lecture as `Course03/slides.pptx`, as a [Slidev](https://sli.dev) deck
where the figures are *computed in the browser*. Every knob the printed deck can
only show three snapshots of — C, γ, ε, the kernel, the scale of a feature — is
a slider here, and the model is refitted as it moves.

Published at <https://pauldubois98.github.io/AdvancedMachineLearning2026/Course03/interactive.html>.

```bash
make interactive          # dev server with hot reload, from the repo root
make interactive-build    # rebuild the published copy (commit the result)
```

`make interactive-build` writes `Course03/interactive.html` and
`Course03/interactive-assets/`, one level up. Those two are **committed to the
repository**, because `.github/workflows/static.yml` uploads the repo as it
stands and never runs a build — so after changing a slide, rebuild *and commit*
or the published deck stays on the old version.

The deck uses `routerMode: hash` and a relative `--base`, so the single HTML
file works from any path without server rewrites; deep links look like
`interactive.html#/29`.

or, from this directory, `npm install && npm run dev`.
`npm run export` writes a PDF (needs playwright-chromium).

## What is live

| slide | knobs |
| --- | --- |
| Separating classes with a line | click the panel to score a test point |
| Which line? | reveal the street each candidate line gets |
| The widest street | turn and shift the line by hand, against the SVM optimum |
| Fixing the scale | scale (w, b) and watch the f = ±1 lines move |
| The Lagrangian has a saddle | move w and α over the contour of L |
| Only a few points matter | drop the non-support vectors and refit |
| When no line works | push the clouds together until no line separates them |
| Slack | C, with the ξ arrows and the three cases counted |
| C: how much misbehaviour is allowed? | C, with street width and the SV share swept |
| Hinge, log loss, squares | slide one point's margin, read what each loss charges |
| The kernel trick | tilt the lift into 3D, and slide the cutting plane |
| XOR | morph from (x₁, x₂) into the (Φ₁, Φ₂) plane |
| RBF kernel | γ, on the kernel profile and on the vote of bumps |
| Kernels in practice | kernel, C, γ, degree, r — on the moons |
| Scale features first | the unit of x₂, and standardising |
| Choosing C and γ | the 5 × 7 grid is cross-validated live; click a cell |
| SVMs scaling | n, against the Gram matrix and the fit times |
| More than two classes | one-against-all vs one-against-one |
| The same idea, for regression | ε, C, γ on the tube |
| The width of the tube | ε, against the number of support vectors |
| Recap | hover a stage for what it bought |

## How the figures are computed

`lib/svm.ts` is a C-SVC trained with Platt's SMO, and `lib/svr.ts` is ε-SVR
solved on β = α − α\* with an exact piecewise line search on each pair. Both were
checked against scikit-learn on the datasets used here: identical support-vector
counts, decision functions agreeing to ~1e-3, and margins to four decimals. The
intercept follows libsvm, including the bracketed fallback when no support
vector is free.

`lib/data.ts` regenerates the printed deck's datasets (separable blobs, moons,
rings, XOR, the sine for SVR) with a seeded RNG, so the pictures are the same on
every machine. They are not pixel-identical to the matplotlib figures — the
random draws differ — but the shapes, spreads and seeds-by-intent match.

One deliberate difference: the cross-validation slide stratifies its folds by
dealing contiguous blocks within each class, as scikit-learn's `StratifiedKFold`
does. scikit-learn's own partition of this dataset happens to collapse to a
single predicted class in the degenerate corners of the grid (tiny C), which
shows up as a few 0.49 cells that distract from the ridge the slide is about.
Everything else matches it cell for cell.

## Gotchas worth knowing before editing

- **Never put a bare `opacity`, `fill-opacity` or `stroke-opacity` attribute on
  an SVG element.** Slidev runs UnoCSS with attributify, which reads
  `opacity="1"` as the utility `opacity-1` and renders it at *1%*. `LineChart.vue`
  therefore sets every paint property through `:style`.
- Inline `$math$` inside a raw HTML block is not parsed. Leave a blank line after
  the opening tag and before the closing one, and markdown-it (and KaTeX) will
  see it.
- The deck pins `@iconify/utils` and `unocss` in `package.json` `overrides`:
  their newer releases need Node ≥ 20.19, and this repo builds on Node 18.
  Drop the pins once the machine is on a newer Node.
