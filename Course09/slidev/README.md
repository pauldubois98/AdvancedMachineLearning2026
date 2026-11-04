# Session 9, interactive

The interactive companion to `Course09/slides.pptx`: the same lecture on
dimension reduction (PCA, SNE, t-SNE) as a [Slidev](https://sli.dev) deck. PCA,
the perplexity bisection, SNE's three steps on the 45-point toy and t-SNE itself
are all *computed in the browser*: the live maps form while you watch, and any
slider starts them again.

Published as
[`Course09/interactive.html`](https://pauldubois98.github.io/AdvancedMachineLearning2026/Course09/interactive.html).

```bash
make interactive-c09      # dev server
make interactive-build    # rebuild the published copies (commit the result)
```

or, from this directory, `npm install && npm run dev`.

This is its own npm project, like `Course06/slidev/`: the decks share no files.
`make interactive-build` writes `Course09/interactive.html` one level up, a
single self-contained file, **committed to the repository** because the Pages
workflow never runs a build. It also opens straight from disk.

Press `h` to hide Slidev's navigation bar (and `h` again to bring it back).

## What is live

| slide | knobs |
| --- | --- |
| No map is perfect: room for neighbours | the number of neighbours at distance 1 (2-D vs a line) |
| No map is perfect: the edge of the ball | the dimension d, the width of the outer shell |
| No map is perfect: topology | how far the loop is opened, where it is cut |
| No map is perfect: curvature | where A sits on the spiral, how far B is |
| No map is perfect: hidden dimensions | the depth of the box, the viewing angle |
| No map is perfect: concentration | the dimension, the number of points |
| No map is perfect: useless features | the number of noise features, their level |
| No map is perfect: density | the radius, the spread of the sparse group |
| Example: 2D Gaussian | the correlation ρ and σ₂/σ₁: axes, projection, components |
| Two equivalent views | the angle of the axis (or snap to PCA): variance + error = total |
| Limitation: non-linear structure | the length of the roll, the 3-D view |
| Distances from one point | click a point |
| Similarity bell | σ; click a point |
| Normalizing as a distribution | σ: p<sub>j\|i</sub>, its perplexity, the points holding 90% |
| Choosing the width σ | one σ for all, or σᵢ from the perplexity |
| Perplexity | the target, the bisection try; click a point |
| Probability similarity matrix | the perplexity |
| Random initialization | the seed, the start spread |
| Initialization & convergence | random (seed) or PCA start: the map after 300 moves |
| Neighborhoods in the map | the move t: the map's bell, q against p |
| Kullback–Leibler divergence | move Q towards P: the terms, KL both ways |
| Asymmetry of KL in SNE | click a pair's (data, map) distances |
| Springs on one point | the move t |
| Moving the points | the move t, the learning rate |
| Compare P and Q | the move t |
| Heavy-tailed map | the degrees of freedom ν, the similarity level |
| Initialization dependence | the seed, the perplexity: t-SNE runs live on the 10-D blobs |
| PCA vs t-SNE (blobs) | the wide cluster's spread, the far cluster's distance, the perplexity |
| PCA vs t-SNE (swiss roll) | the perplexity |
| PCA vs t-SNE (MNIST) | the perplexity (5, 30, 100: precomputed), a digit to highlight |
| SNE vs t-SNE | the perplexity: both run live on the same 600 digits |

A live run computes only while its slide is on screen: Slidev keeps the
neighbouring slides mounted, and several runs at once would starve each other.

## Data

`Course09/data/digits600.json` (the 600 digits of the printed SNE-vs-t-SNE
figure) and `Course09/data/mnist_maps.json` (5000 MNIST images mapped by PCA and
by t-SNE at perplexities 5, 30 and 100, too slow to compute on a slide) are
written by `scripts/make_data_c09.py` and committed. The toy, the blobs and the
swiss roll are drawn in the browser with `lib/rng.ts` from a fixed seed, so they
follow the printed figures' models but not numpy's draws.
