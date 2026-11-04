---
theme: default
title: "Session 9: Dimension Reduction"
info: |
  Advanced Machine Learning · MSc DSBA · 2026 · Paul Dubois
  Interactive companion to Course09/slides.pptx.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
routerMode: hash
# the deck must also run with no network: no webfont fetch, no remote favicon
fonts:
  provider: none
favicon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23fff'/%3E%3Ccircle cx='9' cy='10' r='3' fill='%232b6cb0'/%3E%3Ccircle cx='22' cy='9' r='3' fill='%23b7791f'/%3E%3Ccircle cx='16' cy='23' r='3' fill='%2300ab0e'/%3E%3C/svg%3E"
layout: cover
---

# Session 9<br>Dimension Reduction

Advanced Machine Learning · MSc DSBA · 2026

Paul Dubois

<div class="note mt-8">Week 8 lecture</div>

---
layout: section
---

# Dimension Reduction

---
layout: fig
---

## No map is perfect: room for neighbours

<CrowdingFit />

---
layout: fig
---

## No map is perfect: the edge of the ball

<CrowdingShell />

---
layout: fig
---

## No map is perfect: topology

<MapTopology />

---
layout: fig
---

## No map is perfect: curvature

<MapCurvature />

---
layout: fig
---

## No map is perfect: hidden dimensions

<MapDimensions />

---
layout: fig
---

## No map is perfect: concentration

<MapConcentration />

---
layout: fig
---

## No map is perfect: useless features

<MapNoise />

---
layout: fig
---

## No map is perfect: density

<MapDensity />

---
layout: section
---

# Reminders on PCA

---
layout: eq
---

## A linear projection

<div style="font-size: 1.6em">

$$
\underbrace{X}_{N \times d} \;\approx\; \underbrace{Z}_{N \times q}\; \underbrace{P^T}_{q \times d} \;+\; \text{noise}
$$

</div>

<div class="note" style="text-align: center; margin-top: 1.2rem">

$P \in \mathbb{R}^{d \times q}$ has $q < d$ orthonormal columns ($P^T P = I_q$) and $Z = XP$ holds the coordinates.<br>
$P$ is chosen so that the variance of the projected data is maximal.

</div>

---
layout: fig
---

## Example: 2D Gaussian

<PcaGauss />

---
layout: fig
---

## Two equivalent views

<PcaViews />

---
layout: eq
---

## Algorithm

<div class="cols" style="align-items: center">
<div class="algo" style="border-color: var(--purple)">

| | |
|---|---|
| 1. | standardise: $X_{ij} \leftarrow (X_{ij} - \mu_j) / \sigma_j$ |
| 2. | correlation matrix: $\Sigma = \frac{1}{N-1} X^T X$ |
| 3. | eigen-decomposition of $\Sigma$: $\{p_j, \lambda_j\}$ |
| 4. | order the $\lambda_j$ by decreasing value |
| 5. | principal axes: $P = (p_1, \dots, p_q)$ |
| 6. | principal components: $Z = XP$ |

</div>
<div>

```python
Xs = (X - X.mean(0)) / X.std(0)
S = Xs.T @ Xs / (N - 1)
lam, V = np.linalg.eigh(S)
order = np.argsort(lam)[::-1]
P = V[:, order[:q]]
Z = Xs @ P
```

<p class="note">or <code>sklearn.decomposition.PCA(q)</code>; standardise when the features have different units</p>
</div>
</div>

---
layout: fig
---

## Limitation: non-linear structure

<PcaRoll />

---
layout: section
---

# Stochastic Neighbor Embedding

---
layout: eq
---

## Three steps

<div class="cards3">
<div class="card" style="border-color: var(--blue)">
<div class="h" style="color: var(--blue)">1. in the data</div>
<p>distances → probabilities P</p>
<p class="note">once, at the start</p>
</div>
<div class="card" style="border-color: var(--gold)">
<div class="h" style="color: var(--gold)">2. start the map</div>
<p>random y₁, …, y<sub>N</sub></p>

<p class="note">

$Y^{(0)} \sim \mathcal{N}(0, 10^{-4} I)$

</p>
</div>
<div class="card" style="border-color: var(--green)">
<div class="h" style="color: var(--green)">3. in the map</div>
<p>measure Q, compare, move</p>
<p class="note">repeat until KL(P‖Q) stops falling ↺</p>
</div>
</div>

---
layout: fig
---

## Example

<ToyIntro />

---
layout: section
---

# Step 1: distances to probabilities

---
layout: fig
---

## Distances from one point

<ToyDistances />

---
layout: fig
---

## Similarity bell

<ToyBell />

---
layout: fig
---

## Normalizing as a distribution

<ToyNormalise />

---
layout: fig
---

## Choosing the width σ

<SigmaEffect />

---
layout: fig
---

## Perplexity

<PerplexitySearch />

---
layout: eq
---

## Neighborhoods in the data

$$
p_{j|i} = \frac{\exp(-\|x_i - x_j\|^2 / 2\sigma_i^2)}{\sum_{k \neq i} \exp(-\|x_i - x_k\|^2 / 2\sigma_i^2)}
\qquad p_{i|i} = 0
$$

<p class="note" style="text-align: center">the chance that x<sub>i</sub> picks x<sub>j</sub> as its neighbour; a point is not its own neighbour</p>

$$
p_{ij} = \frac{p_{j|i} + p_{i|j}}{2N}
$$

<p class="note" style="text-align: center">symmetrised: one distribution over all the pairs. Each point has its own width, so p<sub>j|i</sub> ≠ p<sub>i|j</sub>;<br>symmetrising still gives an outlier a share, Σ<sub>j</sub> p<sub>ij</sub> &gt; 1/2N</p>

---
layout: fig
---

## Probability similarity matrix

<PMatrix />

---
layout: section
---

# Step 2: initialize the map

---
layout: fig
---

## Random initialization

<InitRandom />

---
layout: fig
---

## Initialization & convergence

<InitChoices />

---
layout: section
---

# Step 3: measure, compare, move

---
layout: eq
---

## Probability similarity matrix in target space

$$
q_{j|i} = \frac{\exp(-\|y_i - y_j\|^2)}{\sum_{k \neq i} \exp(-\|y_i - y_k\|^2)}
\qquad
q_{ij} = \frac{\exp(-\|y_i - y_j\|^2)}{\sum_{k \neq l} \exp(-\|y_k - y_l\|^2)}
$$

<p class="note" style="text-align: center">the same recipe as p<sub>j|i</sub>, in the map; symmetric SNE uses q<sub>ij</sub>, one distribution over the pairs</p>
<p class="note" style="text-align: center">one fixed width σ = 1/√2 for every point: the scale of the map is free. Q changes at every move; P never does.</p>

---
layout: fig
---

## Neighborhoods in the map

<QNeighbours />

---
layout: fig
---

## Kullback–Leibler divergence

<KlBars />

---
layout: fig
---

## Asymmetry of KL in SNE

<KlAsym />

---
layout: fig
---

## Springs on one point

<Springs />

---
layout: eq
---

## Gradient

$$
\min_{y_1, \dots, y_N}\; C = \mathrm{KL}(P \,\|\, Q) = \sum_{i,j} p_{ij} \log \frac{p_{ij}}{q_{ij}}
$$

$$
\frac{\partial C}{\partial y_i} = 4 \sum_j (p_{ij} - q_{ij})(y_i - y_j)
$$

<p class="note" style="text-align: center">symmetric SNE: a spring between each pair, pulling when p &gt; q, pushing when p &lt; q</p>

<div class="cols" style="margin-top: 1rem">
<div class="box red"><p>non-convex: no guarantee, several restarts, added noise</p></div>
<div class="box green">

one move: $y_i \leftarrow y_i - \eta\, \partial C / \partial y_i$, for every $i$

</div>
</div>

---
layout: fig
---

## Moving the points

<SneRun />

---
layout: fig
---

## Compare P and Q

<PQMatrices />

---
layout: section
---

# t-SNE

---
layout: fig
---

## Heavy-tailed map

<StudentT />

---
layout: eq
---

## t-SNE principle

$$
p_{ij} = \frac{p_{j|i} + p_{i|j}}{2N} \quad \text{(Gaussian, with perplexity: unchanged)}
$$

$$
q_{ij} = \frac{(1 + \|y_i - y_j\|^2)^{-1}}{\sum_{k \neq l} (1 + \|y_k - y_l\|^2)^{-1}} \quad \text{(Student's t, one degree of freedom)}
$$

$$
\frac{\partial C}{\partial y_i} = 4 \sum_j (p_{ij} - q_{ij})(y_i - y_j)(1 + \|y_i - y_j\|^2)^{-1}
$$

<p class="note" style="text-align: center">the same springs, weakened at long range. Large p: map distance &lt; data distance; small p: map distance &gt; data distance.</p>

---
layout: eq
---

## Algorithm

<div class="algo" style="border-color: var(--green)">

| | |
|---|---|
| input | data $X$, perplexity, $T$ iterations, rate $\eta$, momentum $\alpha(t)$ |
| 1. | $p_{j\|i}$ with the target perplexity, then $p_{ij}$ |
| 2. | draw $Y^{(0)} \sim \mathcal{N}(0, 10^{-4} I)$ |
| 3. | for $t = 1, \dots, T$: compute the $q_{ij}$ and the gradient $\partial C / \partial Y$ |
| | $Y^{(t)} = Y^{(t-1)} - \eta\, \partial C / \partial Y + \alpha(t)\,(Y^{(t-1)} - Y^{(t-2)})$ |

</div>

<div class="rows" style="margin-top: 1rem">
<div class="k" style="color: var(--green)">early exaggeration</div><div>p<sub>ij</sub> × 12 at the start: the clusters form first</div>
<div class="k" style="color: var(--green)">adaptive rates</div><div>one gain per coordinate</div>
<div class="k" style="color: var(--green)">accelerated versions</div><div>Barnes–Hut, FFT: O(N log N) instead of O(N²)</div>
</div>

---
layout: fig
---

## Initialization dependence

<TsneLive data="blobs" :knobs="['seed', 'perp']" :perp="30" foot="Three clusters in 10-D (N = 300). A new seed gives a different map of about the same quality (KL); a new perplexity changes the shapes and gaps, and no single value is right." />

---
layout: eq
---

## PCA vs t-SNE

| | PCA | t-SNE |
|---|---|---|
| keeps | the global structure, a linear subspace | the local structure, for visualization |
| curved structure | missed: far points can become neighbours | revealed |
| speed | fast | slow: O(N²) (or O(N log N)) |
| the axes | can be read back in terms of the features | mean nothing |
| a new point | projected by the same matrix | no map: t-SNE learns the points, not a function |
| variants | kernel PCA, probabilistic PCA | UMAP, … |

---
layout: fig
---

## PCA vs t-SNE

<TsneLive data="blobs" show-pca :knobs="['wide', 'far', 'perp']" :perp="30" foot="Same data in both panels. PCA keeps the wide cluster wide and the far one far; in a t-SNE map cluster sizes mean nothing and distances between clusters mean little." />

---
layout: fig
---

## PCA vs t-SNE

<TsneLive data="roll" show-pca :knobs="['perp']" :perp="30" foot="The swiss roll again (colour = position along the roll): t-SNE keeps the neighbours along the roll, often in pieces; PCA mixes the turns." />

---
layout: fig
---

## PCA vs t-SNE

<MnistMaps />

---
layout: fig
---

## SNE vs t-SNE

<TsneLive data="digits" :iters="750" :kernels="['sne', 't']" :knobs="['perp']" :perp="30" foot="The same 600 handwritten digits (8 × 8 pixels), the same code: only the map's kernel changes. SNE crowds the classes together; t-SNE separates them." />
