# Session 2, interactive

The interactive companion to `Course02/slides.pptx`: the same lecture
(linear regression reminders, ridge and lasso, robust regression, IRLS,
logistic regression) as a [Slidev](https://sli.dev) deck. Every fit is
*computed in the browser*, so a slider changes the data or the model and the
figure follows. No data file and no image: every sample is drawn from a fixed
seed.

Published as
[`Course02/interactive.html`](https://pauldubois98.github.io/AdvancedMachineLearning2026/Course02/interactive.html).

```bash
make interactive-c02      # dev server
make interactive-build    # rebuild the published copies (commit the result)
```

or, from this directory, `npm install && npm run dev`.

This is its own npm project, like `Course01/slidev/`: the decks share no files.
`make Course02/interactive.html` writes the deck one level up, a single
self-contained file, **committed to the repository** because the Pages workflow
never runs a build. It also opens straight from disk.

Press `h` to hide Slidev's navigation bar (and `h` again to bring it back).

## What is live

| slide | knobs |
| --- | --- |
| Regression | n, the noise, the true slope, a new sample |
| More columns: the line becomes a plane | turn and tilt the 3-D view, the true w₂, the noise |
| "Linear" means linear in the weights | the polynomial degree (and the train / test error curve), the noise, n |
| Least squares | the intercept and slope of a candidate line (or snap to least squares): residuals and squares |
| What the solution is doing | y's position, its distance to the plane, the angle between the columns |
| Repeated information | β₂ along the valley, a step off it |
| Loss with a flat valley | ε in x₂ = 2x₁ + εz: XᵀX, its determinant and eigenvalues |
| Detecting in practice | the correlation ρ, the ridge λ, n: 150 refits |
| How precise is the estimate? | the spread of x, the noise, n: 60 refits and the σ²(XᵀX)⁻¹ ellipse |
| When d gets large | d (n = 40): train / test error and the fitted coefficients |
| Three penalties | the exponent q of \|β\|^q |
| Penalties behavior | β̂_LS, the budget t, the elastic net α |
| Effect of λ (paths) | the ridge and lasso λ, the noise, a new sample |
| Effect of λ (thresholding) | λ, one coefficient |
| The proximal step | ℓ₁ or ℓ₀, λ, the step θ (past 2/‖XᵀX‖ it diverges), the iterations |
| Outliers | the moved point's x and y (or click) |
| Why squares break | the far point's y, squared or absolute loss |
| Robustness vs complexity | the outliers' distance, the curvature of the truth |
| Loss ~ Noise model | Student's ν |
| Possible ρ | a common scale for every δ |
| δ parameter | Huber's δ |
| δ effect on residual scale | the noise in euros, the number of outliers, δ |
| Choosing δ | δ, the outliers' distance |
| Derivative of ρ | the residual e, δ: the two tangents |
| Influence of a point | the moved point's y: LS, Huber and Tukey slopes |
| Influence and weight | Huber's δ, Tukey's δ |
| Weights & data | the two outliers' y, Huber or Tukey |
| IRLS step by step | the iteration k, Huber or Tukey, the outliers' distance |
| Algorithm approximation | the touch point; the start θ⁰ and step k of IRLS on Σ ρ(θ − xᵢ) |
| From regression to classification | the class separation, the spread, a new sample |
| Why not least squares on the labels? | where and how many far, obvious points |
| The sigmoid | β₀, β₁ (or snap to maximum likelihood) |
| More than two classes | two log-odds: the three softmax probabilities |
| The loss | the class separation (separable: no minimum) |
| IRLS quadratic approximation | the point y where the majorant is tight |
| Logistic regression, step by step | the Newton / IRLS iteration k, the class separation |
