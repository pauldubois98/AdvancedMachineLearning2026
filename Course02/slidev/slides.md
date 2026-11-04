---
theme: default
title: "Session 2: Robust Regression"
info: |
  Advanced Machine Learning · MSc DSBA · 2026 · Paul Dubois
  Interactive companion to Course02/slides.pptx.
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
favicon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23fff'/%3E%3Ccircle cx='9' cy='10' r='3' fill='%232b6cb0'/%3E%3Ccircle cx='22' cy='9' r='3' fill='%23c53030'/%3E%3Ccircle cx='16' cy='23' r='3' fill='%2300ab0e'/%3E%3C/svg%3E"
layout: cover
---

# Session 2<br>Robust Regression

Advanced Machine Learning · MSc DSBA · 2026

Paul Dubois

<div class="note mt-8">Week 2 lecture</div>

---
layout: section
---

# Reminders: linear regression

---
layout: fig
---

## Regression

<RegSetting />

---
layout: eq
---

## Use cases

<div class="apps">
<div class="muted r">predict</div><div></div><div class="muted">from</div>
<div class="r" style="color: var(--blue)">product sales</div><div class="muted">←</div><div>purchase history, season, price</div>
<div class="r" style="color: var(--green)">economic growth</div><div class="muted">←</div><div>trade, investment, employment</div>
<div class="r" style="color: var(--purple)">house prices</div><div class="muted">←</div><div>surface, location, year</div>
<div class="r" style="color: var(--gold)">temperature</div><div class="muted">←</div><div>place, altitude, time of year</div>
<div class="r" style="color: var(--red)">goals next season</div><div class="muted">←</div><div>minutes played, past scoring</div>
</div>

---
layout: eq
---

## Why a linear model?

<div class="cards4">
<div class="card" style="border-color: var(--blue)"><div class="h" style="color: var(--blue)">simple</div><p>a good baseline</p></div>
<div class="card" style="border-color: var(--green)"><div class="h" style="color: var(--green)">interpretable</div><p>coefficients link inputs to outputs</p></div>
<div class="card" style="border-color: var(--purple)"><div class="h" style="color: var(--purple)">strong when data is thin</div><p>works with few points</p></div>
<div class="card" style="border-color: var(--gold)"><div class="h" style="color: var(--gold)">extensible</div>

replace $x$ by $\phi(x)$, e.g. $x^2$, $x^3$

</div>
</div>

---
layout: fig
---

## More columns: the line becomes a plane

<LinregMulti />

---
layout: fig
---

## "Linear" means linear in the *weights*

<PolyBasis />

---
layout: eq
---

## Model via matrix multiplication

$$
f_\beta(x_i) \;=\; \beta_0 + \beta_1 x_{i,1} + \dots + \beta_d x_{i,d} \;=\; x_i'^{T}\beta \;=\; [X\beta]_i
$$

<div class="matmul">
<div class="mblock" style="border-color: var(--blue); color: var(--blue); width: 9rem; height: 8rem">X<span>n × (d+1)</span></div>
<div class="op">×</div>
<div class="mblock" style="border-color: var(--green); color: var(--green); width: 2rem; height: 8rem">β<span>d+1</span></div>
<div class="op">=</div>
<div class="mblock" style="border-color: var(--purple); color: var(--purple); width: 2.6rem; height: 8rem">ŷ<span>n</span></div>
</div>

<p class="note" style="text-align: center">a column of 1's carries the intercept β₀</p>

---
layout: fig
---

## Least squares

<LsResiduals />

---
layout: eq
---

## Analytical solution

$$
L(\beta) = \tfrac{1}{2}\|X\beta - y\|^2 = \tfrac{1}{2}y^{T}y - \beta^{T}X^{T}y + \tfrac{1}{2}\beta^{T}X^{T}X\beta
$$

$$
\nabla L(\beta) = X^{T}X\beta - X^{T}y
$$

<div style="color: var(--green)">

$$
\hat{\beta} = (X^{T}X)^{-1}X^{T}y
$$

</div>

<p class="note" style="text-align: center">The loss function is convex.</p>
<p style="text-align: center; color: var(--red); font-size: 0.9rem">Unique if X has full column rank; else XᵀX is not invertible</p>

---
layout: fig
---

## What the solution is doing

<HatMatrix />

---
layout: fig
---

## Repeated information

<CollinearExample />

---
layout: fig
---

## Loss with a flat valley

<CollinearValley />

---
layout: fig
---

## Detecting in practice

<NearCollinear />

---
layout: fig
---

## How precise is the estimate?

<LsVariance />

---
layout: section
---

# Regularized regression

---
layout: fig
---

## When d gets large

<HighDim />

---
layout: eq
---

## Add a penalty

<div style="font-size: 1.5em">

$$
L_{new}(\beta) \;=\; \color{#2b6cb0}{\underbrace{\tfrac{1}{2}\|y - X\beta\|^2}_{\text{fit the data}}} \;+\; \color{#b7791f}{\underbrace{\lambda}_{\substack{\text{how much}\\\text{we insist}}}}\; \color{#c53030}{\underbrace{R(\beta)}_{\substack{\text{keep }\beta\text{ small}\\\text{or sparse}}}}
$$

</div>

<p class="note" style="text-align: center; margin-top: 1.5rem">λ = 0 is least squares; λ → ∞ crushes coefficients to 0</p>

---
layout: fig
---

## Three penalties

<PenaltyZoo />

---
layout: fig
---

## Penalties behavior

<PenaltyGeometry />

---
layout: fig
---

## Effect of λ

<LambdaPath />

---
layout: fig
---

## Effect of λ

<Thresholding />

---
layout: eq
---

## Handling non-differentiable penalty

<p class="note" style="text-align: center">

$R(\beta)$ is not differentiable

</p>

<div class="loop" style="width: 85%; margin: 0.8rem auto 0">
<div class="box blue"><b>1. gradient step</b>

$$\bar\beta^k = \beta^k - \theta \nabla L(\beta^k)$$

</div>
<div class="arrows"><div class="a">→</div><div class="a">↺</div>repeat</div>
<div class="box red"><b>2. proximal step</b>

$$\beta^{k+1} = \arg\min_\beta \tfrac{1}{2}\|\bar\beta^k - \beta\|^2 + \lambda\theta R(\beta)$$

</div>
</div>

<div class="cols" style="width: 85%; margin: 0.6rem auto 0; text-align: center">
<p style="color: var(--blue)">handles the smooth part of the objective</p>
<p style="color: var(--red)">handles the penalty, in closed form</p>
</div>

---
layout: fig
---

## The proximal step

<div class="formula">

$$
\color{#00ab0e}{R = \|\beta\|_1:}\;\; \beta^{k+1} = \mathrm{sign}(\bar\beta^k)\max(|\bar\beta^k| - \lambda\theta,\, 0)
\qquad
\color{#c53030}{R = \|\beta\|_0:}\;\; \beta^{k+1} = \bar\beta^k \cdot \delta\big((\bar\beta^k)^2 \geq 2\lambda\theta\big)
$$

</div>

<p class="lead-note note" style="text-align: center; margin: 0 0 0.4rem">Convergence for θ ∈ ]0, 2/‖XᵀX‖[ · global minimum with ℓ₁, a local minimum with ℓ₀</p>

<ProxDemo />

---
layout: section
---

# Robust regression

---
layout: fig
---

## Outliers

<OutlierDemo />

---
layout: fig
---

## Why squares break

<SquaredLossPull />

---
layout: fig
---

## Robustness vs complexity

<OutliersVsMis />

---
layout: eq
---

## Likelihood to M-estimation

<p class="note" style="text-align: center">

i.i.d. sample $x_1,\dots,x_n \sim f(x;\theta)$

</p>

<div class="rows" style="width: 90%; margin: 1rem auto; font-size: 1.15rem">
<div class="k" style="color: var(--blue)">maximum likelihood</div>
<div>

$\max_\theta \prod_i f(x_i;\theta) \;\Longleftrightarrow\; \min_\theta \sum_i \rho(x_i;\theta)$ with $\rho = -\log f$

</div>
<div class="k" style="color: var(--green)">M-estimation</div>
<div>

$\min_\theta \sum_i \rho(x_i;\theta)$, $\;\rho$ free to choose

</div>
</div>

---
layout: fig
---

## Loss ~ Noise model

<RhoFromDensity />

---
layout: eq
---

## Robust regression

<div style="color: var(--green); font-size: 1.3em">

$$
L_{robust}(\beta) \;=\; \sum_{i=1}^{n} \rho\big(y_i - x_i'^{T}\beta\big)
$$

</div>

<div style="width: 60%; margin: 1rem auto 0; font-size: 1.05rem">

**ρ must satisfy**

- $\rho(e) \geq 0$ and $\rho(0) = 0$
- $\rho(e) = \rho(-e)$
- $\rho(e) \geq \rho(e')$ when $|e| \geq |e'|$

<p class="note" style="text-align: right">

$\rho(e) = e^2$ gives least squares back

</p>
</div>

---
layout: fig
---

## Possible ρ

<RhoZoo />

---
layout: fig
---

## δ parameter

<DeltaMeaning />

---
layout: fig
---

## δ effect on residual scale

<DeltaScale />

---
layout: fig
---

## Choosing δ

<TuningDelta />

---
layout: fig
---

## Derivative of ρ

<Stationarity />

---
layout: eq
---

## Interpret as weights

<p class="note" style="text-align: center">

Stationarity condition: $\sum_i \dot\rho(e_i)\, x_i' = 0$

</p>

<div style="font-size: 1.3em">

$$
\dot\rho(e_i) \;=\; \omega(e_i)\; e_i
$$

</div>

<p class="note" style="text-align: center">split the slope into (a weight) × (the residual)</p>

<div style="color: var(--green); font-size: 1.3em">

$$
\omega(e_i) \;=\; \frac{\dot\rho(e_i)}{e_i} \;\in\; [0, +\infty]
$$

</div>

<p style="text-align: center">

$\sum_i \omega(e_i)\, e_i\, x_i' = 0$ is a least squares problem, with one weight per point

</p>

<div class="cols" style="width: 70%; margin: 0.6rem auto 0; text-align: center">
<p class="note">least squares: ω ≡ 1</p>
<p style="color: var(--green)">robust: ω falls as |e| grows</p>
</div>

---
layout: fig
---

## Influence of a point

<InfluenceDemo />

---
layout: fig
---

## Influence and weight

<PsiWeights />

---
layout: fig
---

## Weights & data

<WeightsOnData />

---
layout: section
---

# IRLS algorithm

---
layout: eq
---

## Fixed point

<table class="steps" style="width: 85%; margin: 0 auto; font-size: 1.2rem">
<tr><td>

$\sum_i \dot\rho(e_i)\, x_i' = 0$

</td><td>minimiser</td></tr>
<tr><td style="color: var(--green)">

$\sum_i \omega(e_i)\, e_i\, x_i' = 0$

</td><td>

since $\dot\rho(e) = \omega(e)\, e$

</td></tr>
<tr><td style="color: var(--blue)">

$\min_\beta \sum_i \omega(e_i)\, e_i^2 \;=\; \min_\beta \|W^{1/2}(X\beta - y)\|^2$

</td><td>weighted least squares problem</td></tr>
</table>

---
layout: eq
---

## IRLS loop

<div class="irls">
<div class="box blue n1">

$\beta^k$

<div class="sub">estimate</div></div>
<div class="box green n2">

$e^k = y - X\beta^k$

<div class="sub">residuals</div></div>
<div class="box gold n3">

$W^k = \mathrm{diag}(\omega(e^k))$

<div class="sub">weights</div></div>
<div class="box purple n4">

$\beta^{k+1} = (X^{T}W^kX)^{-1}X^{T}W^ky$

<div class="sub">new estimate</div></div>
<div class="a a12">↗</div><div class="a a23">↘</div><div class="a a34">↙</div><div class="a a41">↖</div>
</div>

<p class="note" style="text-align: center">weights need residuals, residuals need estimate [...]</p>

---
layout: fig
---

## IRLS step by step

<IrlsSteps />

---
layout: eq
---

## IRLS algorithm

<div class="cols" style="grid-template-columns: 1.3fr 1fr; align-items: center">
<div class="algo" style="border-color: var(--blue)">

| | |
|---|---|
| · | initialise $\beta^0$: least squares with no weights |
| 1. | $e^{k-1} = y - X\beta^{k-1}$ |
| 2. | $W^k = \mathrm{diag}\left[\omega(e^{k-1}_i)\right]$ |
| 3. | $\beta^k = (X^{T}W^kX)^{-1}X^{T}W^ky$ |
| · | stop when β stops moving |

</div>
<div>
<h4 style="color: var(--green)">costs</h4>
<ul>
<li>one weighted least squares per pass</li>
<li>usually a few passes needed</li>
</ul>
<p style="color: var(--red); margin-top: 1.2rem; font-size: 0.9rem">convex ρ: global solution<br>non-convex ρ: starting point matters</p>
</div>
</div>

---
layout: fig
---

## Algorithm approximation

<MmIdea />

---
layout: eq
---

## ρ requirements for convergence

<p class="note" style="text-align: center">

let $\rho(x) = \varphi(|x|)$, need

</p>

<div class="cols" style="width: 85%; margin: 0.5rem auto 1.4rem; font-size: 1.05rem">
<ul>
<li>

$\varphi$ differentiable on $]0, +\infty[$

</li>
<li>

$\dot\varphi(x) \geq 0$

</li>
</ul>
<ul>
<li>

$\varphi(\sqrt{\cdot})$ concave on $]0, +\infty[$

</li>
<li>

$\lim_{x \to 0^{+}} \omega(x) = \dot\varphi(x)/x \in \mathbb{R}$

</li>
</ul>
</div>

<div style="color: var(--green); font-size: 1.2em">

$$
\rho(x) \;\leq\; \rho(y) + \dot\rho(y)(x-y) + \tfrac{1}{2}\,\omega(|y|)\,(x-y)^2
$$

</div>

<p class="note" style="text-align: center">ρ has a quadratic upper bound minimised by the IRLS step</p>

---
layout: eq
---

## Recap

<div class="recap">
<div class="card" style="border-color: var(--blue)"><div class="h" style="color: var(--blue)">least squares</div>

$\rho(e) = e^2/2$

</div>
<div class="arrow">→</div>
<div class="card" style="border-color: var(--red)"><div class="h" style="color: var(--red)">outlier(s)</div><p>allowed by the fit</p></div>
<div class="arrow">→</div>
<div class="card" style="border-color: var(--green)"><div class="h" style="color: var(--green)">choice of ρ</div>

$\omega(e) = \dot\rho(e)/e$

</div>
<div class="arrow">→</div>
<div class="card" style="border-color: var(--purple)"><div class="h" style="color: var(--purple)">IRLS</div><p>weighted least squares, repeated</p></div>
</div>

---
layout: section
---

# Logistic regression

---
layout: fig
---

## From regression to classification

<LogisticSetting />

---
layout: fig
---

## Why not least squares on the labels?

<WhyNotLS />

---
layout: fig
---

## The sigmoid

<SigmoidFit />

---
layout: eq
---

## The log-odds

<div style="font-size: 1.3em">

$$
\color{#00ab0e}{\underbrace{\log \frac{\Pr(G = 1 \mid X = x)}{1 - \Pr(G = 1 \mid X = x)}}_{\text{the log-odds, anything in } \mathbb{R}}} \;=\; \color{#2b6cb0}{\underbrace{\beta_0 + \beta^{T}x}_{\text{a linear score, anything in } \mathbb{R}}}
$$

</div>

<p style="text-align: center; margin-top: 1.4rem">no Pr(x | G), no prior: unlike LDA or naive Bayes, nothing is assumed about how x is spread</p>

---
layout: eq
---

## More than two classes

<p class="note" style="text-align: center">K classes: pick one as the reference</p>

$$
\log \frac{\Pr(G=k \mid x)}{\Pr(G=K \mid x)} \;=\; \beta_{k0} + \beta_k^{T}x, \qquad k = 1,\dots,K-1
$$

<div style="color: var(--green); font-size: 0.85em">

$$
\Pr(G=k \mid x) = \frac{\exp(\beta_{k0} + \beta_k^{T}x)}{1 + \sum_{\ell=1}^{K-1}\exp(\beta_{\ell 0} + \beta_\ell^{T}x)}
\qquad
\Pr(G=K \mid x) = \frac{1}{1 + \sum_{\ell=1}^{K-1}\exp(\beta_{\ell 0} + \beta_\ell^{T}x)}
$$

</div>

<p style="text-align: center">

classify with $\hat{k} = \arg\max_k \Pr(G=k \mid x)$; the probabilities add up to one by construction

</p>

<SoftmaxDemo />

---
layout: fig
---

## The loss

<LogisticLoss />

---
layout: eq
---

## Fitting

<p class="note" style="text-align: center">IRLS algorithm, with different weights</p>

<table class="plain fitting">
<tr><th></th><th style="color: var(--blue)">robust regression</th><th style="color: var(--green)">logistic regression</th></tr>
<tr><td>minimise</td><td>

$\sum_i \rho(e_i)$

</td><td>

$\sum_i \log\left(1 + e^{[L\beta]_i}\right)$

<div class="note">

$[L\beta]_i = -y_i\,\beta^{T}x_i$, $\;L = -\mathrm{Diag}(y)X$

</div></td></tr>
<tr><td>weight</td><td>

$\omega(e_i) = \dot\rho(e_i)/e_i$

</td><td>

$\omega([L\beta]_i)$

</td></tr>
<tr><td>one step</td><td>

$\beta \leftarrow (X^{T}WX)^{-1}X^{T}Wy$

<div class="note">weighted least squares</div></td><td>

$\beta \leftarrow \beta - \Omega(\beta)^{-1}\nabla F(\beta)$

<div class="note">

$\Omega(\beta) = L^{T}\mathrm{Diag}(\omega(L\beta))\,L$ and $\nabla F(\beta) = L^{T}\dot{f}(L\beta)$

</div></td></tr>
</table>

---
layout: fig
---

## IRLS quadratic approximation

<LogisticMm />

---
layout: fig
---

## Logistic regression, step by step

<LogisticFit />

---
layout: eq
---

## What logistic regression is worth

<div class="pros">
<div>
<h4 style="color: var(--green)">in its favour</h4>
<ul>
<li>simple, and easy to implement</li>
<li>gives probabilities, not just a side</li>
<li>no assumption on how x is distributed</li>
<li>convex: one global minimum</li>
</ul>
</div>
<div>
<h4 style="color: var(--red)">against</h4>
<ul>
<li>the boundary is linear</li>
<li>needs regularisation when d is large</li>
<li>separable data sends β to infinity</li>
</ul>
</div>
</div>

---
layout: section
---

# Next week

Support vector machines
