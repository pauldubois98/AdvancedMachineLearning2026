# Session 8, interactive

The interactive companion to `Course08/slides.pptx`: the same lecture on model
order selection as a [Slidev](https://sli.dev) deck, where the models are
*refitted in the browser* as the sliders move. RBF SVMs, naive Bayes, LDA and
QDA, polynomial fits with and without ridge, k-means, DBSCAN, NMF under a mask,
Gaussian mixtures, cross-validation and a Gaussian-process surrogate all run
live.

Published as
[`Course08/interactive.html`](https://pauldubois98.github.io/AdvancedMachineLearning2026/Course08/interactive.html).

```bash
make interactive-c08      # dev server
make interactive-build    # rebuild the published copies (commit the result)
```

or, from this directory, `npm install && npm run dev`.

This is its own npm project, like `Course06/slidev/`: the decks share no files.
`make interactive-build` writes `Course08/interactive.html` one level up, a
single self-contained file, **committed to the repository** because the Pages
workflow never runs a build. It also opens straight from disk.

Press `h` to hide Slidev's navigation bar (and `h` again to bring it back).

## What is live

| slide | knobs |
| --- | --- |
| Kernel of SVM (γ) | γ, refitted live; train and test accuracy swept over γ |
| Kernel of SVM (C) | C, the same |
| Naive Bayes, LDA, QDA | points per class, the sample |
| Ridge regression | λ, the order M; train and test RMS swept over λ |
| k-means | K, the sample; inertia against K |
| DBSCAN | ε, MinPts; clusters and noise swept over ε |
| Non-negative Matrix Factorization | r, the true rank, the noise, the held-out share |
| Gaussian mixture | K, the sample size |
| Classic example | N, σ, the sample |
| Effect of model order | M |
| Training error against test error | N, σ, the sample |
| Inside the over-fitted model | N, a ridge λ, the sample |
| Modern solution | N, M, the sample |
| Empirical risk | the order of f; R_N(f) against the training error of f̂ |
| Train vs Test curves | the number of samples, N, σ |
| Bias and variance | M, N; bias² and variance for every order |
| Choosing model on test set | candidates, validation points, the draw |
| Hold out, select, report | the train and validation shares, the shuffle |
| K-fold | K, the round, the number of random splits |
| Choosing the number of folds | N, M |
| Uncontaminated split | the round, through all four schemes |
| Model selection costs | folds, values per knob, knobs, repeats, seconds per fit |
| Search on a log scale | draws, the lower end, the threshold, the seed |
| The landscape with one knob | the noise, the probes, the tolerance |
| The landscape with two knobs | the tolerance; click to score a setting |
| Grid, random, Bayesian | the budget, the measurement noise, the seed |
| A cheap stand-in | measured points, the length-scale, the true curve |
| Explore or exploit | κ, ξ, measured points |
| The loop | the pass, EI or UCB, random starts, the seed |
| Reading the history | trials so far, the window, the noise, the seed |
| Pruning | the percentile, the warm-up, trials, the seed |
| AIC vs BIC | N, the sample: the order each criterion picks |
| A correction for small samples | M_j, N |

The tables, the equation slides and the Optuna code are static, as printed.

## Data

None to build. Bishop's ten points (numpy, seed 6) are written into
`lib/c08.ts`; every other sample is drawn in the browser with `lib/rng.ts` from
a fixed seed. These samples differ from the printed figures' (numpy's
generator), but follow the same models. The seeds of the blob slides (k-means,
DBSCAN, mixtures) and of the NMF matrix were picked so that the defaults tell
the same story as print.
