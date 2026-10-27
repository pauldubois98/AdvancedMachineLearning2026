# Session 6, interactive

The interactive companion to `Course06/slides.pptx`: the same lecture on
mixture models and the EM algorithm as a [Slidev](https://sli.dev) deck, where
the mixtures are *refitted in the browser* as the sliders move. EM, its hard
and stochastic variants and k-means run live on the animal lengths of the 2023
lecture, on 2-D clouds drawn from a fixed seed, and on Fisher's iris.

Published as
[`Course06/interactive.html`](https://pauldubois98.github.io/AdvancedMachineLearning2026/Course06/interactive.html).

```bash
make interactive-c06      # dev server
make interactive-build    # rebuild the published copies (commit the result)
```

or, from this directory, `npm install && npm run dev`.

This is its own npm project, like `Course05/slidev/`: the decks share no files.
`make interactive-build` writes `Course06/interactive.html` one level up, a
single self-contained file, **committed to the repository** because the Pages
workflow never runs a build. It also opens straight from disk.

Press `h` to hide Slidev's navigation bar (and `h` again to bring it back).

## What is live

| slide | knobs |
| --- | --- |
| Two regimes in one sample | the two peaks marked or not |
| One bell is not enough | the single bell's mean and width, against the mixture's likelihood |
| Mixture density | p₁, μ₁, σ₁, μ₂, σ₂ |
| Simulating mixture | p₁, n, the seed, the generator's colours shown or hidden |
| A fitted model is | a length x: its density and its label probabilities |
| Sums of normals | the six mixtures of the 2023 lecture, components shown or not |
| Effect of growing K | K, refitted live |
| Shapes of the covariance | the family, and each component's σₓ, σᵧ, correlation |
| Counting parameters | K and d |
| Mixture relabeled | swap the labels |
| Surface of likelihood | μ₁, μ₂ (or click the map), the common width |
| Likelihood is unbounded | σ₂, down to 10⁻³ |
| If we knew the labels | the labels known or not |
| Class probabilities from the fit | x₀ |
| Along axis | the prior p₁: the boundary moves |
| Responsibility | a point x, the widths |
| Responsibility as a matrix | the EM pass |
| Soft and hard | soft or hard, the certainty threshold |
| The E-step, The M-step | the current θᵗ |
| Example run | the pass, the start |
| Same run | the pass, the deck's start or a random one |
| Likelihood evolution | a start of your own, against the three of the figure |
| Jensen inequality | u₁, u₂ and the weight |
| E-step, M-step (the bound) | θᵗ, and how close q is to the posterior |
| Minorize–maximize steps | the passes, the start |
| k-means is a limit case of EM | σ, from soft to hard |
| k-means vs Gaussian mixture | the sample seed, n |
| SEM example | the pass, the seed |
| k-means vs EM vs SEM vs N-SEM | N, the seed |
| Starts comparison | the number of random starts, the first seed |
| Covariance types | K |
| Number of components | n, the seed: BIC and AIC recomputed |
| Example on real data | petals or sepals, k-means or random start |
| Scoring a new point | the contour level; click to score a point of your own |

## Data

None to build: the animal-length table and Fisher's iris (scikit-learn's copy)
are written into `lib/gmm.ts` and `lib/iris.ts`; every other sample is drawn in
the browser with `lib/rng.ts` from a fixed seed. The clouds therefore differ
from the printed figures' (numpy's generator), but follow the same models.
