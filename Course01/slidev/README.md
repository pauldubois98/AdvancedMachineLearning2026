# Session 1, interactive

The interactive companion to `Course01/slides.pptx`: the same lecture
(estimation theory, Bayes classifiers, LDA/QDA, k-means, PCA) as a
[Slidev](https://sli.dev) deck. Every estimator, posterior, classifier and
clustering is *computed in the browser*, so a slider changes the data or the
model and the figure follows. The course logistics and the 21 suggested
datasets stay the printed figures (shrunk to WebP and inlined).

Published as
[`Course01/interactive.html`](https://pauldubois98.github.io/AdvancedMachineLearning2026/Course01/interactive.html).

```bash
make interactive-c01      # dev server
make interactive-build    # rebuild the published copies (commit the result)
```

or, from this directory, `npm install && npm run dev`.

This is its own npm project, like `Course09/slidev/`: the decks share no files.
`make Course01/interactive.html` writes the deck one level up, a single
self-contained file, **committed to the repository** because the Pages workflow
never runs a build. It also opens straight from disk. The PCA slide reads
`Course01/data/digits.json` (scikit-learn's 1797 digits), written by
`scripts/make_data_c01.py`; `img/*.webp` are made from `Course01/img/*.png`.

Press `h` to hide Slidev's navigation bar (and `h` again to bring it back).

## What is live

| slide | knobs |
| --- | --- |
| How close, on average? | the scale c of the estimator c · x̄, the sample size n |
| How stable? | the sample size on each side, the noise σ |
| Bias and variance are independent problems | the bias, the spread: bias², variance, MSE |
| Method of moments: match what you can compute | the model's μ and σ against the sample moments |
| Likelihood on data | the candidate θ: the density heights, L and ℓ |
| Maximum likelihood on data | the model μ (slope of ℓ), a new sample |
| Why taking the log | n, up to 2000: L underflows a float, ℓ does not |
| Maximum likelihood: the Gaussian case | μ and σ on the log-likelihood surface |
| When parameters follow a random distribution | the prior mean and sd, n |
| From parameter predicted distribution to value | the answer θ̂: the expected squared, absolute and 0-1 costs |
| Three costs, three estimators | the weight of a bump, the gap: mean, median, mode |
| How much the prior matters | n, the prior sd |
| Unbiased is not the same as best | n: S/(n−1), S/n, S/(n+1) on 4000 samples |
| Where n − 1 comes from | the reference c, a new sample |
| Where n + 1 comes from | n: the exact bias², variance and MSE of S/c |
| Regression or classification | the regression noise, the class separation |
| Two ways to build a classifier | n per class, a new sample: logistic regression vs LDA |
| Bayes classifier (ingredients) | the prior π₁, class 2's mean and sd |
| Naive Bayes: spam filtering | the words in the e-mail, the share of spam |
| Naive Bayes: the zero distribution problem | the words in the e-mail, the smoothing α |
| Naive Bayes on continuous features | the correlation inside a class, the separation |
| LDA, step by step | the share of class 1, n |
| LDA: a linear decision boundary | the prior π₁ |
| LDA: why the boundary is straight | the projection direction (or snap to w) |
| QDA: one covariance per class | class 2's length ratio and angle, n |
| QDA shapes | the distance, elongation, class 2's scale and angle (and presets) |
| LDA vs QDA: costs & benefits | K, d: the parameter count and a live learning curve |
| k-means algorithm | the half-step, the start |
| k-means limitations | K, the outlier distance, the moon noise |
| PCA: directions of maximum variance | the direction (or snap), the correlation |
| PCA: how much can be dropped | q: variance kept and six digits rebuilt |
