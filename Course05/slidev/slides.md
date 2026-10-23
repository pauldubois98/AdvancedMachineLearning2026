---
theme: default
title: "Session 5: Non-negative Matrix Factorization"
info: |
  Advanced Machine Learning · MSc DSBA · 2026 · Paul Dubois
  Interactive companion to Course05/slides.pptx.
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
favicon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23fff'/%3E%3Crect x='4' y='6' width='10' height='20' rx='1.5' fill='%232b6cb0'/%3E%3Crect x='17' y='6' width='4' height='20' rx='1' fill='%236b46c1'/%3E%3Crect x='23' y='6' width='5' height='5' rx='1' fill='%23b7791f'/%3E%3C/svg%3E"
layout: cover
---

# Session 5<br>Non-negative Matrix Factorization

Advanced Machine Learning · MSc DSBA · 2026

Paul Dubois

<div class="note mt-8">Week 5 lecture</div>

---
layout: section
---

# A matrix as a product

---
layout: fig
---

## Reducing size

<FactorSize />

---
layout: eq
---

## Modeling problem

<div class="note">

Given $x_j \in \mathbb{R}^p$ for $1 \leq j \leq n$, and a target dimension $r < \min(p, n)$, find $r$ basis elements $w_k \in \mathbb{R}^p$ and weights $h_j \in \mathbb{R}^r$ such that

</div>

$$
x_j \approx \sum_{k=1}^{r} w_k\, h_j(k)
\qquad\text{equivalently}\qquad
X \approx W H
$$

<div class="three">
<div>

<em class="hl-blue">$X \in \mathbb{R}^{p \times n}$</em>

$X(:, j) = x_j$, the data

</div>
<div>

<em class="hl-purple">$W \in \mathbb{R}^{p \times r}$</em>

$W(:, k) = w_k$, the dictionary

</div>
<div>

<em class="hl-gold">$H \in \mathbb{R}^{r \times n}$</em>

$H(:, j) = h_j$, the codes

</div>
</div>

---
layout: fig
---

## Column as a weighted sum

<ColumnSum />

---
layout: fig
---

## Why non-negative

<WhyNonneg />

---
layout: fig
---

## Additive components

<NmfVsPca />

---
layout: eq
---

## Three questions

<div class="note">

Goal: a low-rank approximation $\;X \approx WH$

</div>

<div class="cards3">
<div class="card" style="border-color: var(--blue)">
<div class="h hl-blue">1. How good is the approximation?</div>
<div>Frobenius, Kullback–Leibler, Itakura–Saito, logistic, …</div>
<div class="out hl-blue">→ a loss function</div>
</div>
<div class="card" style="border-color: var(--purple)">

<div class="h hl-purple">

2. What shape must $W$ and $H$ have?

</div>
<div>orthogonality, independence, sparsity, normalisation, …</div>
<div class="out hl-purple">→ non-negativity</div>

</div>
<div class="card" style="border-color: var(--green)">
<div class="h hl-green">3. How do we find them?</div>
<div>the problem has no formula for its solution</div>
<div class="out hl-green">→ an algorithm</div>
</div>
</div>

<div class="note mt-4">

NMF: find $(W, H)$ with $X \approx WH$, $\;W \geq 0$, $\;H \geq 0$. Questions 1 and 2 are this slide; question 3 is the rest of the deck.

</div>

---
layout: section
---

# What it is used for

---
layout: fig
---

## Faces: the three matrices

<FacesSetup />

---
layout: fig
---

## Faces: what comes out

<FacesApp />

---
layout: fig
---

## Hyperspectral unmixing: a cube, unfolded

<CubeSetup />

---
layout: fig
---

## Hyperspectral unmixing: the three matrices

<SpectralSetup />

---
layout: fig
---

## Hyperspectral unmixing: what comes out

<SpectralApp />

---
layout: fig
---

## Topics in text: the three matrices

<TopicsSetup />

---
layout: fig
---

## Topics in text: what comes out

<TopicsApp />

---
layout: fig
---

## Fill missing values

<Recsys />

---
layout: fig
---

## Music: the three matrices

<MusicSetup />

---
layout: fig
---

## Music: what comes out

<MusicApp />

---
layout: section
---

# Choosing a loss

---
layout: eq
---

## Entry by entry

<div class="note">

Measure $X \approx WH$ with a divergence between $X$ and $WH$

</div>

$$
D(X, WH) = \sum_{i=1}^{p} \sum_{j=1}^{n} d\big(\textcolor{#2b6cb0}{[X]_{ij}},\; \textcolor{#6b46c1}{[WH]_{ij}}\big)
$$

<div class="three small">
<div class="note">one scalar loss</div>
<div><em class="hl-blue">one entry of the data</em></div>
<div><em class="hl-purple">the same entry of the model</em></div>
</div>

<div class="box green mt-6">Separable: the loss of one entry never looks at another entry.</div>

<div class="note mt-2">This is what makes every update rule entrywise.</div>

---
layout: fig
---

## Divergence, not distance

<LossAsym />

---
layout: eq
---

## Classic choices

<div class="zoo">

| | | |
|---|---|---|
| <em class="hl-blue">Quadratic</em><br>$d(x, y) = (x - y)^2$ | | Gaussian noise; not robust to outliers; $\ell_1$ and friends for robustness |
| <em class="hl-green">Kullback–Leibler</em><br>$d(x, y) = x \log \dfrac{x}{y} - x + y$ | | counts, Poisson noise; text mining, photon imaging; cheap to differentiate |
| <em class="hl-gold">Itakura–Saito</em><br>$d(x, y) = \dfrac{x}{y} - \log \dfrac{x}{y} - 1$ | | scale invariant: $d(\lambda x, \lambda y) = d(x, y)$; music and audio spectra; harder to optimise |

</div>

---
layout: fig
---

## Classic choices

<LossShapes />

---
layout: eq
---

## Where a loss comes from

<div class="note">A loss is a noise model in disguise</div>

$[X]_{ij} \sim p(\,\cdot \mid [WH]_{ij})$, independently over $(i, j)$ <span class="note">: assume the model entry is the parameter of a distribution.</span>

$$
\max_{W, H} \; \prod_{ij} p([X]_{ij} \mid [WH]_{ij}) \;\;\Leftrightarrow\;\; \min_{W, H} \; \sum_{ij} -\log p([X]_{ij} \mid [WH]_{ij})
$$

<div class="note">Maximum likelihood, written as a minimisation.</div>

$$
d(x, y) = -\log p(x \mid y) + c(x)
$$

<div class="note">

Add whatever depends on $x$ alone: it cannot move $W$ or $H$. <em class="hl-green">$c(x)$ is chosen so that $d(x, x) = 0$</em>; that is the only thing the constant is for.

</div>

<div class="note mt-4">Pick the distribution your data actually follows, and the loss follows from it.</div>

---
layout: fig
---

## Gaussian noise gives the square

<NoiseModel kind="gauss" />

---
layout: fig
---

## Poisson counts give KL

<NoiseModel kind="poisson" />

---
layout: fig
---

## Multiplicative noise gives Itakura–Saito

<NoiseModel kind="exp" />

---
layout: fig
---

## General formula

<BetaFamily />

---
layout: eq
---

## Derivative

<div class="note">One derivative for the whole family, and it is why one algorithm covers them all</div>

$$
\frac{\partial d_\beta}{\partial y}(x, y) = \frac{(\beta - 1)\beta\, y^{\beta - 1} - \beta(\beta - 1)\, x\, y^{\beta - 2}}{\beta(\beta - 1)}
$$

<div class="note">

Only the last two terms of $d_\beta$ contain $y$.

</div>

$$
\textcolor{#00ab0e}{\frac{\partial d_\beta}{\partial y}(x, y) = y^{\beta - 1} - x\, y^{\beta - 2} = y^{\beta - 2}\,(y - x)}
$$

<div class="note">Everything cancels; the same expression holds in the two limits.</div>

<div class="three mt-2">
<div>

<em class="hl-blue">$\beta = 2$</em>: $\;y - x$

</div>
<div>

<em class="hl-green">$\beta = 1$</em>: $\;1 - x / y$

</div>
<div>

<em class="hl-gold">$\beta = 0$</em>: $\;(y - x) / y^2$

</div>
</div>

<div class="box green mt-4">Zero exactly when the model matches the data, whatever β is.</div>

---
layout: eq
---

## Choosing the loss

<div class="zoo">

| Loss | $\beta$ | Noise it assumes | Reach for it when |
|---|---|---|---|
| <em class="hl-blue">Quadratic</em> | $\beta = 2$ | Gaussian, additive | default, anything on one scale |
| <em class="hl-green">KL</em> | $\beta = 1$ | Poisson, counts | text, photon imaging, clicks |
| <em class="hl-gold">Itakura–Saito</em> | $\beta = 0$ | multiplicative | audio, anything spanning decades |
| <em class="hl-red">$\ell_1$ / Huber</em> | none | heavy tails | outliers you do not want to fit |

</div>

<div class="note mt-4">The loss and the non-negativity constraint together are the model; change either one and you change what NMF finds.</div>

---
layout: section
---

# Mathematical optimisation

---
layout: eq
---

## Problem formulation

$$
\min_{W,\, H} \; \textcolor{#2b6cb0}{D(X, WH)} \qquad \text{s.t.} \quad \textcolor{#6b46c1}{W \geq 0, \; H \geq 0}
$$

<div class="three small">
<div></div>
<div><em class="hl-blue">the loss</em></div>
<div>

<em class="hl-purple">entrywise, on all $r(p + n)$ unknowns</em>

</div>
</div>

<div class="cols mt-6">
<div>

#### <em class="hl-red">What makes it hard</em>

- non-convex in $(W, H)$ jointly
- the answer is never unique
- NP-hard in general

</div>
<div>

#### <em class="hl-green">What makes it workable</em>

- convex in $W$ alone, and in $H$ alone
- the loss is separable
- cheap updates that never leave $\geq 0$

</div>
</div>

---
layout: eq
---

## Convex in each half

<div class="note">Half the problem at a time is easy</div>

$$
F(W, H) = \tfrac{1}{2}\|X - WH\|_F^2 \;=\; \tfrac{1}{2}\sum_j \|x_j - W h_j\|_2^2
$$

With $W$ fixed: $F$ is a sum of $n$ independent quadratics in $h_j \geq 0$. <span class="note">A non-negative least squares problem, convex.</span>

With $H$ fixed: $F$ is a sum of $p$ independent quadratics in the rows of $W \geq 0$. <span class="note">The same problem, transposed, convex.</span>

<em class="hl-red">In $(W, H)$ together: $F$ contains the products $W_{ik} H_{kj}$, not convex.</em> <span class="note">Already visible at $p = n = r = 1$: $f(w, h) = (x - wh)^2$.</span>

<div class="box gold mt-4">Biconvex, so algorithms alternate.</div>

---
layout: fig
---

## Convex in each half

<Biconvex />

---
layout: fig
---

## The answer is never unique

<Ambiguity />

---
layout: eq
---

## Hard ill-posed problem

<div class="zoo">

| | |
|---|---|
| <em class="hl-red">NP-hard</em> | exact NMF is NP-hard |
| <em class="hl-red">ill-posed</em> | no unique solution |
| <em class="hl-gold">stationary points only</em> | algorithms are proven to reach a stationary point, not the minimum |
| <em class="hl-gold">sensitive to the start</em> | two initialisations give two different answers (both legitimate) |

</div>

<div class="note mt-4">"Converged" means the updates stopped moving, not that the answer is the best.</div>

---
layout: section
---

# Multiplicative updates

---
layout: eq
---

## The Frobenius norm, as a trace

$$
\|A\|_F^2 \;=\; \sum_{i}\sum_{j} A_{ij}^2 \;=\; \mathrm{tr}\!\left( A^\top A \right)
$$

<div class="note">

The sum of the squares of every entry, written without indices: $[A^\top A]_{jj} = \sum_i A_{ij}^2$.

</div>

$$
\mathrm{tr}(AB) = \mathrm{tr}(BA), \qquad \mathrm{tr}(A^\top) = \mathrm{tr}(A), \qquad \mathrm{tr} \text{ is linear}
$$

<div class="note">The only three facts about the trace used anywhere in this deck.</div>

$$
\begin{aligned}
F(W, H) &= \tfrac{1}{2}\|X - WH\|_F^2 = \tfrac{1}{2}\,\mathrm{tr}\!\left[ (X - WH)^\top (X - WH) \right] \\
&= \textcolor{#00ab0e}{\tfrac{1}{2}\,\mathrm{tr}(X^\top X) \;-\; \mathrm{tr}(H^\top W^\top X) \;+\; \tfrac{1}{2}\,\mathrm{tr}(H^\top W^\top W H)}
\end{aligned}
$$

<div class="note">

Constant in $H$, linear in $H$, quadratic in $H$: a convex quadratic, so the gradient is all we need.

</div>

---
layout: eq
---

## The gradient

$$
F = \tfrac{1}{2}\,\mathrm{tr}(X^\top X) - \mathrm{tr}(H^\top W^\top X) + \tfrac{1}{2}\,\mathrm{tr}(H^\top W^\top W H)
$$

<div class="note">

Expand; the two cross terms are equal because $\mathrm{tr}(A) = \mathrm{tr}(A^\top)$.

</div>

$$
\frac{\partial}{\partial H}\,\mathrm{tr}(H^\top W^\top X) = W^\top X, \qquad \frac{\partial}{\partial H}\,\mathrm{tr}(H^\top W^\top W H) = 2\, W^\top W H
$$

<div class="note">

The two standard identities, with $W^\top W$ symmetric.

</div>

<div class="box green mt-4">

$\nabla_H F = W^\top (WH - X) \qquad\qquad \nabla_W F = (WH - X) H^\top$

</div>

---
layout: eq
---

## W & H can be swapped

$$
\|X - WH\|_F = \|X^\top - H^\top W^\top\|_F
$$

<div class="note">The same loss, read with the roles swapped.</div>

<div class="zoo narrow">

| | problem in $H$ | problem in $W$ |
|---|---|---|
| data | $X$ | $X^\top$ |
| dictionary | $W$ | $H^\top$ |
| codes | $H$ | $W^\top$ |

</div>

<div class="box green mt-4">Derive every rule for H only, then transpose it to get the rule for W.</div>

---
layout: fig
---

## Gradient descent kept positive

<GradientStep />

---
layout: eq
---

## One step size per entry

$$
H_{kj} \;\leftarrow\; H_{kj} - \eta_{kj}\, [\nabla_H F]_{kj}, \qquad \eta_{kj} > 0
$$

<div class="note">

Nothing forces one single step size: $\eta$ may depend on $(k, j)$. Choose $\eta_{kj} = \dfrac{H_{kj}}{[W^\top W H]_{kj}}$, legal since $W, H \geq 0$.

</div>

$$
H_{kj} \leftarrow H_{kj} - \frac{H_{kj}}{[W^\top W H]_{kj}} \left( [W^\top W H]_{kj} - [W^\top X]_{kj} \right)
\quad\Longrightarrow\quad
\textcolor{#00ab0e}{H_{kj} \;\leftarrow\; H_{kj}\, \frac{[W^\top X]_{kj}}{[W^\top W H]_{kj}}}
$$

<div class="note">

Substitute $\nabla_H F = W^\top W H - W^\top X$; the two $[W^\top W H]_{kj}$ cancel.

</div>

<div class="box green mt-4">A product of non-negative numbers: H can never leave the orthant, and no projection is needed.</div>

---
layout: eq
---

## Why that step size

<div class="note">

Three questions about $\eta_{kj} = H_{kj} / [W^\top W H]_{kj}$

</div>

<div class="cols3">
<div>

#### <em class="hl-blue">Why one per entry?</em>

- the constraint $H_{kj} \geq 0$ is itself one per entry
- a single $\eta$ must be small enough for the entry closest to zero, and every other entry then crawls
- $\eta_{kj} \propto H_{kj}$: an entry near the wall shortens its own step

</div>
<div>

#### <em class="hl-purple">Why this value?</em>

- $[W^\top W H]_{kj}$ adds up $r$ non-negative terms, one of which is $[W^\top W]_{kk} H_{kj}$
- so $\eta_{kj} \leq 1 / [W^\top W]_{kk}$
- that bound is the exact step for a parabola of curvature $[W^\top W]_{kk}$: a Newton step along $H_{kj}$, damped by the other entries

</div>
<div>

#### <em class="hl-green">Just so it cancels?</em>

- the cancellation is how it was found, not why it is right
- the next section builds an upper bound on $F$ and minimizes it: out comes the same $\eta$, with nothing chosen by hand
- and, as a bonus, a proof that the loss falls at every pass

</div>
</div>

<div class="note mt-2">Shorter than a Newton step, and never across zero: that is the whole design of η.</div>

---
layout: fig
---

## Lee and Seung rules

<MuRatio />

---
layout: eq
---

## Why split the gradient

<div class="note">

$\eta_{kj} = H_{kj} / [W^\top W H]_{kj}$ was invented for one loss. Must we redo that algebra for every other one?

</div>

<div class="box green mt-2">

No: write $\nabla = \nabla^{+} - \nabla^{-}$ with both parts $\geq 0$, take $\eta = H / \nabla^{+}$:
$\;H - \eta \odot \nabla = H - \dfrac{H}{\nabla^{+}} \odot (\nabla^{+} - \nabla^{-}) = H \odot \dfrac{\nabla^{-}}{\nabla^{+}}$

</div>

<div class="cols3 mt-4 centered">
<div>

#### <em class="hl-blue">stays non-negative</em>

<div class="note">A ratio of two non-negative numbers, times a non-negative entry: nothing can go below 0.</div>

</div>
<div>

#### <em class="hl-purple">stops only where it should</em>

<div class="note">

A fixed point needs $\nabla^{+} = \nabla^{-}$ or $H_{kj} = 0$: exactly the optimality condition for a constrained $H \geq 0$.

</div>

</div>
<div>

#### <em class="hl-gold">one recipe, every loss</em>

<div class="note">No step size to tune, and a new loss only needs its gradient read in two pieces.</div>

</div>
</div>

<div class="note mt-4">The split is never unique: any valid one gives a working rule.</div>

---
layout: eq
---

## Splitting the gradient

<div class="note">The same recipe works for every loss in this deck</div>

Split the gradient: $\nabla_H D = \nabla^{+} - \nabla^{-}$ with $\nabla^{+} \geq 0$ and $\nabla^{-} \geq 0$ <span class="note">(always possible, and usually obvious by inspection)</span>, then

$$
\textcolor{#00ab0e}{H \;\leftarrow\; H \odot \frac{\nabla^{-}}{\nabla^{+}}}
$$

<div class="zoo narrow">

| loss | $\nabla^{+}$ | $\nabla^{-}$ |
|---|---|---|
| <em class="hl-blue">Frobenius</em> | $W^\top W H$ | $W^\top X$ |
| <em class="hl-green">KL</em> | $W^\top \mathbf{1}$ | $W^\top \left( X \oslash W H \right)$ |
| <em class="hl-purple">weighted</em> | $W^\top (\Sigma \odot WH)$ | $W^\top (\Sigma \odot X)$ |
| <em class="hl-gold">regularized</em> | $(W^\top W + \mu I_r) H$ | $W^\top X - \lambda \mathbf{1}$ |

</div>

---
layout: section
---

# Why it works

---
layout: eq
---

## Two nested arguments

<div class="mm">
<div class="card" style="border-color: var(--purple)">
<div class="h hl-purple">outer loop: alternate</div>
<div class="inner">

$H \leftarrow$ better $H$, $\;W$ frozen

</div>
<div class="inner">

$W \leftarrow$ better $W$, $\;H$ frozen

</div>
<div class="note">Each half-step minimizes over a subset of the variables, and the current point is one of the candidates.</div>
</div>
<div class="arrow note">but how? →</div>
<div class="card" style="border-color: var(--green)">
<div class="h hl-green">inner step: one MU update</div>

- do not solve the frozen half exactly
- build $G(H \mid \bar H) \geq F(H)$, touching at $\bar H$
- minimize $G$ instead (easier, as it is separable)
- the minimizer of $G$ is the multiplicative rule

</div>
</div>

---
layout: fig
---

## Minimize a majorant

<MmIdea />

---
layout: eq
---

## What a surrogate is

<div class="box purple">

A **surrogate** is an upper bound that touches: $\;G(h \mid \bar{h}) \geq F(h)$ for all $h \geq 0$, with equality at $h = \bar{h}$.

</div>

$$
F(h) = \tfrac{1}{2}\|x - Wh\|_2^2 = \tfrac{1}{2}\sum_i \Big( x_i - \sum_k W_{ik} h_k \Big)^2
$$

<div class="note">

Minimize one column $h$ of $H$, with $W$ frozen: every other column is independent.

</div>

<div class="note hl-red">The obstacle: one square holds all r entries of h at once, so nothing is minimized entry by entry.</div>

$$
\textcolor{#00ab0e}{[Wh]_i = \sum_k \lambda_{ik} z_{ik}, \qquad \lambda_{ik} = \frac{W_{ik} \bar{h}_k}{[W\bar{h}]_i}, \qquad z_{ik} = \frac{h_k}{\bar{h}_k}\,[W\bar{h}]_i}
$$

<div class="note">

$\lambda_{ik} \geq 0$ and $\sum_k \lambda_{ik} = 1$: a weighted average of the $r$ components. The loss is untouched: the model entry $[Wh]_i$ is written as an average, then convexity is used.

</div>

---
layout: eq
---

## The quadratic surrogate

<div class="note">

Convexity turns one coupled square into $r$ separate ones

</div>

$$
\Big( x_i - \sum_k \lambda_{ik} z_{ik} \Big)^2 \;\leq\; \sum_k \lambda_{ik} \left( x_i - z_{ik} \right)^2
$$

<div class="note">

$u \mapsto (x_i - u)^2$ is convex, so the square of an average is below the average of the squares.

</div>

$$
G(h \mid \bar{h}) = \tfrac{1}{2} \sum_i \sum_k \lambda_{ik} \left( x_i - \frac{h_k}{\bar{h}_k}[W\bar{h}]_i \right)^2 \;\geq\; F(h)
$$

<div class="note">

Term $k$ holds $h_k$ and nothing else: a sum of $r$ independent parabolas.

</div>

<em class="hl-green">$z_{ik} = [W\bar{h}]_i$ when $h = \bar{h}$, so $G(\bar{h} \mid \bar{h}) = F(\bar{h})$</em> <span class="note">: the bound touches at the current point, a valid surrogate.</span>

<div class="note mt-4">

The approximation is in the coupling, never in the loss: $G$ is never below $F$, and the two agree at $\bar h$.

</div>

---
layout: eq
---

## Minimizing the surrogate

$$
\frac{\partial G}{\partial h_k} = -2 \sum_i W_{ik} \left( x_i - \frac{h_k}{\bar{h}_k}[W\bar{h}]_i \right) = -2\left( [W^\top x]_k - \frac{h_k}{\bar{h}_k}[W^\top W \bar{h}]_k \right)
$$

<div class="note">

The chain rule; only the $k$-th parabola contains $h_k$, and the factors $[W\bar{h}]_i$ and $\bar{h}_k$ cancel.

</div>

$$
\textcolor{#00ab0e}{\text{set to zero:}\quad h_k = \bar{h}_k\, \frac{[W^\top x]_k}{[W^\top W \bar{h}]_k}}
$$

<div class="note">

And $\partial^2 G / \partial h_k^2 = 2[W^\top W\bar h]_k / \bar{h}_k > 0$: it is the minimum.

</div>

<div class="box green mt-4">The same rule as before, now with a proof that every pass lowers the loss.</div>

---
layout: fig
---

## Where the step size came from

<EtaSurrogate />

---
layout: eq
---

## The other losses, same recipe

<div class="note">Minimize a majorant in closed form</div>

<div class="zoo narrow">

| | | |
|---|---|---|
| <em class="hl-blue">Frobenius</em> | $\beta = 2$ | $H \leftarrow H \odot \dfrac{W^\top X}{W^\top W H}$ |
| <em class="hl-green">Kullback–Leibler</em> | $\beta = 1$ | $H \leftarrow H \odot \dfrac{W^\top (X \oslash WH)}{W^\top \mathbf{1}}$ |
| <em class="hl-gold">Itakura–Saito</em> | $\beta = 0$ | $H \leftarrow H \odot \dfrac{W^\top (X \oslash (WH)^{2})}{W^\top (WH)^{-1}}$ |

</div>

<div class="box purple mt-4">

General formula: $\;H \leftarrow H \odot \dfrac{W^\top\!\left[(WH)^{\beta-2} \odot X\right]}{W^\top (WH)^{\beta-1}}$, from $\;\partial d_\beta / \partial y = y^{\beta-2}(y - x)$

</div>

---
layout: eq
---

## Multiplicative Updates

<div class="algo" style="border-color: var(--blue)">

| | |
|---|---|
| <em class="hl-blue">input</em> | $X \geq 0$, rank $r$, a loss, a tolerance |
| <em class="hl-blue">init</em> | $W_0 > 0$, $H_0 > 0$ (strictly: zeros are absorbing) |
| **repeat** | $H \leftarrow H \odot \nabla_H^{-} \oslash \nabla_H^{+}$ |
| | $W \leftarrow W \odot \nabla_W^{-} \oslash \nabla_W^{+}$ |
| | optionally rescale: $w_k \leftarrow w_k / \lVert w_k\rVert$, $\; h^{(k)} \leftarrow \lVert w_k\rVert\, h^{(k)}$ |
| <em class="hl-gold">until</em> | $D$ stops decreasing, or the budget runs out |
| <em class="hl-green">output</em> | $(W, H)$, a stationary point (not always the minimum) |

</div>

<div class="note mt-4">

Cost per pass: a handful of $p \times n$ products, $\mathcal{O}(pnr)$. No step size to tune.

</div>

---
layout: fig
---

## Monotone and slow

<MuConvergence />

---
layout: eq
---

## Initialization

<div class="note">The answer you get is the answer your start led to</div>

<div class="zoo">

| | |
|---|---|
| <em class="hl-red">identity, constants</em> | degenerate: every column of $W$ identical, and MU cannot break the tie |
| <em class="hl-gold">random positive</em> | the usual default; restart a few times and keep the best |
| <em class="hl-green">SVD, then truncate</em> | NNDSVD: take the leading singular vectors, keep the positive part |
| <em class="hl-blue">$r$ columns of $X$</em> | cheap, and already in the right cone |
| <em class="hl-blue">a clustering</em> | run k-means with $K = r$: the centroids become $W$, the assignments $H$ |

</div>

<div class="note mt-2">Never start at exactly zero, and never start symmetric.</div>

---
layout: fig
---

## Initialization

<InitGeometry />

---
layout: fig
---

## Initialization

<InitFaces />

---
layout: fig
---

## Initialization

<InitCompare />

---
layout: section
---

# Weighted NMF

---
layout: fig
---

## Entries with different importances

<WeightedIdea />

---
layout: eq
---

## Weighted loss

<div class="note">One matrix of weights, multiplied in entry by entry</div>

$$
D_\Sigma(X, WH) = \tfrac{1}{2}\, \|\Sigma \odot (X - WH)\|_F^2 = \tfrac{1}{2}\sum_{ij} \Sigma_{ij}^2\, \left( X_{ij} - [WH]_{ij} \right)^2
$$

<div class="zoo narrow">

| | |
|---|---|
| <em class="hl-green">$\Sigma_{ij} = 1$</em> | the entry counts, exactly as before |
| <em class="hl-red">$\Sigma_{ij} = 0$</em> | the entry costs nothing, whatever the model says there |
| <em class="hl-gold">$0 < \Sigma_{ij} < 1$</em> | the entry counts, but less |

</div>

<div class="box purple mt-4">For a binary mask Σ ⊙ Σ = Σ, so Σ² and Σ can be written interchangeably.</div>

---
layout: eq
---

## Weighted rules

<div class="hl-blue">

Weighted Frobenius $\;\|\Sigma \odot (X - WH)\|_F^2$

</div>

$$
W \leftarrow W \odot \frac{(\Sigma \odot X) H^\top}{(\Sigma \odot WH) H^\top}
\qquad\qquad
H \leftarrow H \odot \frac{W^\top (\Sigma \odot X)}{W^\top (\Sigma \odot WH)}
$$

<div class="hl-green mt-4">

Weighted KL, with a weight $p_i$ per row and $q_j$ per column

</div>

$$
W_{ik} \leftarrow W_{ik}\, \frac{\sum_l H_{kl} X_{il} / (p_i [WH]_{il})}{\sum_l q_l H_{kl}}
\qquad\qquad
H_{kj} \leftarrow H_{kj}\, \frac{\sum_i W_{ik} X_{ij} / (q_j [WH]_{ij})}{\sum_i p_i W_{ik}}
$$

<div class="note">

That is, $\mathrm{KL}\!\left( X,\; \mathrm{Diag}(p)\, W H\, \mathrm{Diag}(q) \right)$: the weights change the numerator and the denominator by different amounts.

</div>

---
layout: fig
---

## Matrix completion

<CompletionDemo />

---
layout: section
---

# Regularized NMF

---
layout: eq
---

## Three reasons for a penalty

<div class="cards3">
<div class="card" style="border-color: var(--green)">
<div class="h hl-green">sparsity</div>

$\lambda \|H\|_1$

<div class="note">few components per column; the parts become nameable</div>
</div>
<div class="card" style="border-color: var(--blue)">
<div class="h hl-blue">stability</div>

$\tfrac{\mu}{2}\|H\|_F^2$

<div class="note">a better conditioned subproblem; no entry can blow up</div>
</div>
<div class="card" style="border-color: var(--purple)">
<div class="h hl-purple">scale</div>

$\tfrac{\nu}{2}\|W\|_F^2$

<div class="note">penalising both factors freezes the Λ ambiguity</div>
</div>
</div>

<div class="note mt-4">

Since $H \geq 0$, the $\ell_1$ norm is differentiable, with gradient 1. The penalty fits the multiplicative update without a proximal step.

</div>

---
layout: eq
---

## The penalized loss

<div class="note">The penalized objective</div>

$$
\textcolor{#2b6cb0}{\tfrac{1}{2}\|X - WH\|_F^2} + \textcolor{#00ab0e}{\tfrac{\mu}{2}\|H\|_F^2} + \textcolor{#b7791f}{\lambda \|H\|_1} + \textcolor{#6b46c1}{\tfrac{\nu}{2}\|W\|_F^2}
$$

<div class="four small">
<div><em class="hl-blue">fit</em></div>
<div><em class="hl-green">keeps H small</em></div>
<div><em class="hl-gold">makes H sparse</em></div>
<div><em class="hl-purple">keeps W small</em></div>
</div>

<div class="box green mt-6">Penalties are separable in the entries, so the derivation is unchanged.</div>

<div class="note mt-2">λ, μ, ν are hyperparameters to tune.</div>

---
layout: eq
---

## The regularized rules

$$
W \;\leftarrow\; W \odot \frac{X H^\top}{W (H H^\top + \nu I_r)}
\qquad\qquad
H \;\leftarrow\; H \odot \frac{\left[ W^\top X - \lambda \mathbf{1} \right]_{+}}{(W^\top W + \mu I_r) H}
$$

<div class="note hl-red">

$[\,\cdot\,]_{+} = \max(\cdot, 0)$: without it a large $\lambda$ would make $H$ negative.

</div>

<div class="zoo narrow mt-2">

| | |
|---|---|
| <em class="hl-gold">λ up</em> | more zeros in $H$, a worse fit |
| <em class="hl-green">μ up</em> | the denominator grows: $H$ shrinks, smoothly |
| <em class="hl-purple">ν up</em> | $W$ shrinks and $H$ grows to compensate |

</div>

<div class="note mt-2">The penalties cost nothing: they only change which two matrices the ratio is made of.</div>

---
layout: fig
---

## Sparsity

<Sparsity />

---
layout: section
---

# Other algorithms

---
layout: eq
---

## Alternating least squares

<div class="note">One half of the problem is an ordinary least squares, so solve it, instead of nudging it</div>

<div class="hl-purple"><strong>Alternating least squares</strong></div>

$$
H \;\leftarrow\; \left[ (W^\top W)^{-1} W^\top X \right]_{+}, \qquad W \;\leftarrow\; \left[ X H^\top (H H^\top)^{-1} \right]_{+}
$$

<div class="note">

The unconstrained optimum of the frozen half, then $\max(\cdot, 0)$ entry by entry.

</div>

<div class="box red mt-2">The catch: clipping is not the solution of the constrained problem, so the loss can go up.</div>

<div class="mt-4">

<strong class="hl-green">Alternating NNLS</strong>: $\;h_j \leftarrow \arg\min_{h \geq 0} \|x_j - W h\|_2^2$ for each column, exact and monotone,

</div>

<div class="note">but it needs an inner solver per column, and is far too slow to run from the start.</div>

---
layout: fig
---

## Rank-one layers

<HalsLayers />

---
layout: fig
---

## One layer at a time

<HalsResidual />

---
layout: fig
---

## One entry at a time

<HalsColumn />

---
layout: eq
---

## HALS in one slide

<div class="algo" style="border-color: var(--gold)">

| | |
|---|---|
| <em class="hl-blue">precompute</em> | $A = X H^\top, \quad B = H H^\top$ |
| for $k = 1 \ldots r$ | $w_k \leftarrow \left[ w_k + \dfrac{A_{:k} - W B_{:k}}{B_{kk}} \right]_{+}$ |
| <em class="hl-blue">precompute</em> | $C = W^\top X, \quad D = W^\top W$ |
| for $k = 1 \ldots r$ | $h^{(k)} \leftarrow \left[ h^{(k)} + \dfrac{C_{k:} - D_{k:} H}{D_{kk}} \right]_{+}$ |

</div>

<div class="note mt-4">

The same $\mathcal{O}(pnr)$ cost as one MU pass: the two matrix products are computed once, outside the loop. A floor of $\varepsilon$ instead of 0 keeps a column from dying.

</div>

---
layout: eq
---

## Families of algorithms

<div class="note">All of them alternate; they differ in what they do with one half</div>

<div class="zoo">

| Family | What one step does | Costs you |
|---|---|---|
| <em class="hl-blue">Multiplicative</em> | one cheap rescaling of every entry | monotone, never leaves $\geq 0$, slow |
| <em class="hl-purple">Alternating LS</em> | solve unconstrained, then clip at 0 | fast, may oscillate |
| <em class="hl-green">Alternating NNLS</em> | solve the constrained problem exactly | expensive, used as a refinement |
| <em class="hl-gold">HALS</em> | one column of $W$ (one row of $H$) at a time | closed form, simple, fast |

</div>

<div class="box blue mt-4">We derived the multiplicative ones in full; the next slide compares them.</div>

---
layout: fig
---

## Three algorithms, measured

<AlgoCompare />

---
layout: fig
---

## Choosing r

<ChoosingR />

---
layout: eq
---

## NMF

<div class="cols">
<div>

#### <em class="hl-green">Pros</em>

- dimension reduction for non-negative data
- components that add up: readable, nameable
- weighted and regularized variants come almost free
- cheap updates, easy to implement

</div>
<div>

#### <em class="hl-red">Cons</em>

- non-convex: the start decides where you land
- no unique answer
- MU converges slowly, and stalls at small values
- $r$ has to come from somewhere

</div>
</div>

<div class="note mt-6">Use NMF when the parts have to mean something; use PCA when you only want the best rank-r fit.</div>
