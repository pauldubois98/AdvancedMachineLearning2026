---
theme: default
title: "Session 6: Mixture Models and Expectation-Maximization"
info: |
  Advanced Machine Learning · MSc DSBA · 2026 · Paul Dubois
  Interactive companion to Course06/slides.pptx.
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
favicon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23fff'/%3E%3Cpath d='M3 26 C8 26 8 8 11 8 C14 8 14 20 17 20 C20 20 20 5 24 5 C28 5 27 26 30 26' fill='none' stroke='%231b1b1b' stroke-width='2.4'/%3E%3C/svg%3E"
layout: cover
---

# Session 6<br>Mixture Models and Expectation-Maximization

Advanced Machine Learning · MSc DSBA · 2026

Paul Dubois

<div class="note mt-8">Week 6 lecture</div>

---
layout: section
---

# A mixture of populations

---
layout: fig
---

## Two regimes in one sample

<AnimalTable />

---
layout: fig
---

## One bell is not enough

<OneBell />

---
layout: eq
---

## Where mixtures come up

<div class="note" style="text-align: center">One sample with several populations</div>

<div class="cards4">
<div class="card" style="border-color: var(--blue)">
<div class="h hl-blue">Populations</div>
<div>multiple group origins,<br>male and female</div>
<div class="out note">Task: predict the label</div>
</div>
<div class="card" style="border-color: var(--gold)">
<div class="h hl-gold">Images</div>
<div>sky, road and building<br>in one photograph</div>
<div class="out note">Task: segmentation</div>
</div>
<div class="card" style="border-color: var(--green)">
<div class="h hl-green">Signals</div>
<div>speakers, phonemes,<br>instruments</div>
<div class="out note">Task: speech GMM</div>
</div>
<div class="card" style="border-color: var(--purple)">
<div class="h hl-purple">Density</div>
<div>odd shapes: skewed, heavy, multi-modal</div>
<div class="out note"></div>
</div>
</div>

<div class="note mt-4" style="text-align: center">The group label exists, but is never recorded (it is "latent").</div>

---
layout: fig
---

## Mixture density

<div class="formula">

$$
f(x) \;=\; \sum_k p_k \, f_k(x) \;=\; p_1 f_1(x) + \cdots + p_K f_K(x)
$$

</div>

<MixtureBuilder />

---
layout: eq
---

## Latent variable

<div class="note" style="text-align: center">Where a point comes from: first the class, then the value</div>

<div class="flow">
<div class="box purple">draw <i>Z</i><div class="lab">P(<i>Z</i> = <i>k</i>) = <i>p<sub>k</sub></i></div></div>
<div class="arrow">→</div>
<div class="stack">
<div class="box blue"><i>Z</i> = 1: &nbsp;<i>X</i> ∼ <i>f</i><sub>1</sub></div>
<div class="box gold"><i>Z</i> = 2: &nbsp;<i>X</i> ∼ <i>f</i><sub>2</sub></div>
</div>
<div class="arrow">→</div>
<div class="box" style="border-color: var(--ink)">keep <i>x</i><div class="lab" style="color: var(--red)">throw <i>z</i> away</div></div>
</div>

<div class="rows">
<div class="k hl-green" style="color: var(--green)">Complete data</div><div>

$T = (X, Z)$: what the generator produced

</div>
<div class="k" style="color: var(--blue)">Observed data</div><div>

$X$ alone: what the experiment recorded

</div>
</div>

<div class="note mt-4" style="text-align: center">

$Z$ is latent: it exists in the model, it is missing from the data.

</div>

---
layout: fig
---

## Simulating mixture

<GenerativeSim />

---
layout: eq
---

## Two components case

<table class="steps">
<tr><td>

$Y_1 \sim \mathcal{N}(\mu_1, \sigma_1^2), \quad Y_2 \sim \mathcal{N}(\mu_2, \sigma_2^2), \quad Z \sim \mathcal{B}(1, p)$

</td><td>two bells and one coin, drawn independently</td></tr>
<tr><td>

$X = Z\, Y_1 + (1 - Z)\, Y_2$

</td><td>

the coin picks which bell is read: $P(Z = 1) = p$

</td></tr>
<tr><td>

$f_X(x) = \sum_k P(Z = k)\, f(x \mid Z = k) = p\, \varphi_{\theta_1}(x) + (1 - p)\, \varphi_{\theta_2}(x)$

</td><td>

marginalising: sum the joint $P(z, x) = P(z) f(x \mid z)$ over $z$

</td></tr>
<tr><td style="color: var(--blue)">

$\ell(\theta; x) = \sum_i \log\left( p\, \varphi_{\theta_1}(x_i) + (1 - p)\, \varphi_{\theta_2}(x_i) \right)$

</td><td>

the log-likelihood of $n$ i.i.d. observations

</td></tr>
</table>

<div class="box gold mt-4">

Five unknowns: $\theta = (p, \mu_1, \sigma_1, \mu_2, \sigma_2)$. How do we estimate them?

</div>

---
layout: fig
---

## A fitted model is

<DensityLabel />

---
layout: eq
---

## Key questions

<div class="note" style="text-align: center">

Fitting a mixture to a sample: $\; f(x) = \sum_k p_k f_k(x)$

</div>

<div class="cards3">
<div class="card" style="border-color: var(--blue)">
<div class="h hl-blue">1. What family are the components?</div>
<div>Gaussian, Poisson, Student, exponential, …</div>
<div class="out hl-blue">→ Assume Gaussian</div>
</div>
<div class="card" style="border-color: var(--purple)">
<div class="h hl-purple">2. How many are there?</div>
<div>

$K$ known, guessed, or estimated from the data

</div>
<div class="out hl-purple">→ Assume known</div>
</div>
<div class="card" style="border-color: var(--green)">
<div class="h hl-green">3. How do we find θ = (p<sub>k</sub>, μ<sub>k</sub>, σ<sub>k</sub>)<sub>k</sub>?</div>
<div>the likelihood has no closed-form maximiser</div>
<div class="out hl-green">→ Expectation-Maximization</div>
</div>
</div>

---
layout: section
---

# What a Gaussian mixture can model

---
layout: eq
---

## The model

<div class="note" style="text-align: center">Every component is a normal density</div>

$$
f(x) \;=\; \sum_k p_k \, \frac{1}{\sqrt{2 \pi \sigma_k^2}}\, \exp\left( -\frac{(x - \mu_k)^2}{2 \sigma_k^2} \right)
$$

<div class="cols">
<div>

<h4 class="hl-purple" style="color: var(--purple)">The constraints</h4>

- $p_k \geq 0$ and $p_1 + \cdots + p_K = 1$
- $\mu_k \in \mathbb{R}$, no constraint at all
- $\sigma_k > 0$ (zero is not allowed)

</div>
<div>

<h4 style="color: var(--gold)">The unknowns</h4>

- $\theta = (p_k, \mu_k, \sigma_k)_{k = 1, \ldots, K}$
- $3K - 1$ free numbers (since $\sum_k p_k = 1$)
- and $K$ itself, if unknown

</div>
</div>

<div class="note mt-4" style="text-align: center">With enough components, a Gaussian mixture can reach almost any density.</div>

---
layout: fig
---

## Sums of normals

<GmmZoo />

---
layout: fig
---

## Effect of growing K

<GrowingK />

---
layout: eq
---

## In d dimensions

<div class="note" style="text-align: center">The same formula, with a covariance matrix</div>

$$
f(x) = \sum_k p_k \, \frac{1}{(2\pi)^{d/2} |\Sigma_k|^{1/2}} \, \exp\left( -\frac{1}{2}(x - \mu_k)^{\top} \Sigma_k^{-1}(x - \mu_k) \right)
$$

<div class="cols">
<div>

<h4 style="color: var(--blue)">Multi-dimension:</h4>

- $\mu_k \in \mathbb{R}^d$ are centres
- $\Sigma_k$ is $d \times d$, symmetric, positive definite
- level sets are ellipsoids

</div>
<div>

<h4 style="color: var(--green)">Unchanged:</h4>

- the latent class $Z$
- the weights $p_k$ (summing to $1$)

</div>
</div>

<div class="note mt-4" style="text-align: center">

$\Sigma_k$ carries $d(d+1)/2$ numbers, so the parameter count grows like $d^2$.

</div>

---
layout: fig
---

## Shapes of the covariance

<CovShapes />

---
layout: fig
---

## Counting parameters

<ParamCount />

---
layout: fig
---

## Mixture relabeled

<Relabel />

---
layout: eq
---

## Simulation / Estimation asymmetry

<table class="steps">
<tr><td>

$Z \sim \mathcal{M}(p_1, \ldots, p_K)$ on $\{1, \ldots, K\}$, i.e. $P(Z = k) = p_k$

</td><td>

one multinomial draw, with $p_1 + \cdots + p_K = 1$

</td></tr>
<tr><td>

$\mathcal{L}(x \mid Z = k) = f_k(x)$

</td><td>given the class, the point is an ordinary draw from one component</td></tr>
<tr><td style="color: var(--green)">

$T = (X, Z)$

</td><td>the complete data: the pair the generator actually produced</td></tr>
<tr><td style="color: var(--blue)">

$X$ alone

</td><td>

the observed data: $Z$ is dropped, $f(x) = \sum_k p_k f_k(x)$

</td></tr>
</table>

<div class="box purple mt-4">

Simulation is much easier than estimation ($Z$ missing makes it hard).

</div>

---
layout: section
---

# Fitting by maximum likelihood

---
layout: eq
---

## Likelihood of observed data

<div class="note" style="text-align: center">Maximum likelihood, as usual</div>

$$
\ell_{\mathrm{obs}}(x_1, \ldots, x_n; \theta) \;=\; \sum_i \log\Big( \underbrace{\sum_k p_k \, f_k(x_i)}_{\color{#c53030}\text{a sum inside a log}} \Big)
$$

<div class="cols">
<div>

<h4 style="color: var(--green)">Classic setting:</h4>

- set the gradient to zero
- solve, in closed form

</div>
<div>

<h4 style="color: var(--red)">Mixture model:</h4>

- the log does not split over the components
- the derivative mixes all of $\theta$
- no closed form

</div>
</div>

<div class="note mt-4" style="text-align: center">

Maximising $\ell_{\mathrm{obs}}$ directly is hard. Expectation-Maximization avoids the problem.

</div>

---
layout: eq
---

## Sum inside the log

<table class="steps">
<tr><td>

$\ell_{\mathrm{obs}}(\theta) = \sum_i \log\left( p\, \varphi_{\theta_1}(x_i) + (1-p)\, \varphi_{\theta_2}(x_i) \right)$

</td><td>

$K = 2$ already has five unknowns

</td></tr>
<tr><td style="color: var(--red)">

$\displaystyle \frac{\partial \ell_{\mathrm{obs}}}{\partial \mu_1} = \sum_i \frac{p\, \varphi_{\theta_1}(x_i)}{p\, \varphi_{\theta_1}(x_i) + (1-p)\, \varphi_{\theta_2}(x_i)} \cdot \frac{x_i - \mu_1}{\sigma_1^2}$

</td><td>the fraction depends on every parameter</td></tr>
<tr><td>

$\Rightarrow$ no parameter separates from the others

</td><td>

while a Gaussian alone gives $\hat{\mu} = \bar{x}$

</td></tr>
</table>

---
layout: fig
---

## Surface of likelihood

<LikSurface />

---
layout: fig
---

## Likelihood is unbounded

<Unbounded />

---
layout: fig
---

## If we knew the labels

<KnownLabels />

---
layout: eq
---

## Complete-data likelihood splits

<table class="steps">
<tr><td>

$\ell(\theta; x, z) = \sum_i \log\left( p_{z_i} f_{z_i}(x_i) \right) = \sum_i \sum_k \mathbb{1}_{z_i = k} \log( p_k f_k(x_i) )$

</td><td>

with $z$ known, the point belongs to one component and only one

</td></tr>
<tr><td style="color: var(--blue)">

$K = 2$: $\; \ell(\theta; x, z) = \sum_i \left( z_i \log \varphi_{\theta_1}(x_i) + (1 - z_i) \log \varphi_{\theta_2}(x_i) \right)$<br>$\qquad\qquad\qquad + \sum_i \left( z_i \log p + (1 - z_i) \log(1 - p) \right)$

</td><td>one line per component, plus the weights</td></tr>
<tr><td>

$\Rightarrow$ the log sits on a single density, not on a sum

</td><td>

$\theta_1$, $\theta_2$ and $p$ appear in separate terms

</td></tr>
</table>

<div class="box green mt-4">Separable: three independent maximisations instead of one hard one</div>

---
layout: fig
---

## Closed form class by class

<div class="mle">
<div>
<div class="note">Maximising it: count, average, average again</div>

$\color{#6b46c1}\hat{p}_k = \frac{1}{n} \sum_i \mathbb{1}_{z_i = k}$ <span class="note">the share of the sample that carries label $k$</span>

$\color{#2b6cb0}\hat{\mu}_k = \frac{1}{n \hat{p}_k} \sum_{i : z_i = k} x_i$ <span class="note">the mean of the points of class $k$</span>

$\color{#b7791f}\hat{\sigma}_k^2 = \frac{1}{n \hat{p}_k} \sum_{i : z_i = k} (x_i - \hat{\mu}_k)^2$ <span class="note">their spread around that mean</span>

<div class="note">Exactly the single-Gaussian formulas, applied inside each class.</div>
</div>
<ClassMle />
</div>

---
layout: fig
---

## Class probabilities from the fit

<PosteriorPoint />

---
layout: fig
---

## Along axis

<PosteriorCurve />

---
layout: eq
---

## Chicken and egg

<div class="note" style="text-align: center">Each half is easy</div>

<div class="loop">
<div class="box green">know <i>z</i> ⇒ get <i>θ</i><div class="sub">count and average</div></div>
<div class="arrows"><div class="a">⇄</div>and back</div>
<div class="box blue">know <i>θ</i> ⇒ get <i>z</i><div class="sub">Bayes' rule, point by point</div></div>
</div>

<div class="cols">
<div>

<h4 style="color: var(--red)">Problem:</h4>

- neither is known
- the likelihood couples $z$ and $\theta$

</div>
<div>

<h4 style="color: var(--green)">Solution:</h4>

- alternate guessing $\theta$ and deducing $z$

</div>
</div>

<div class="note mt-4" style="text-align: center">Keep the probability of each label, and weight by it.</div>

---
layout: section
---

# Responsibilities

---
layout: eq
---

## Bayes (reminder)

<div class="note" style="text-align: center">Three lines of probability, and nothing else</div>

| | | |
|---|---|---|
| <b style="color: var(--blue)">conditioning</b> | $P(A \mid B) = \dfrac{P(A \cap B)}{P(B)}$ | renormalise inside $B$ |
| <b style="color: var(--purple)">Bayes' rule</b> | $P(B \mid A) = \dfrac{P(A \mid B)\, P(B)}{P(A)}$ | turn the conditioning around |
| <b style="color: var(--gold)">total probability</b> | $P(A) = \sum_i P(A \cap B_i)$ | for a partition $B_1, \ldots, B_n$ of $\Omega$ |

<div class="box green mt-4">

Put $B_k = \{Z = k\}$ and $A = \{X = x\}$: the three lines give the responsibility

</div>

---
layout: eq
---

## Posterior over the label

<div class="note" style="text-align: center">The posterior probability of the label, given the point</div>

$$
\gamma_{ik}(\theta) \;=\; P(Z_i = k \mid X_i = x_i, \theta) \;=\; \frac{\overbrace{p_k \, f_k(x_i)}^{\color{#6b46c1}\text{prior times likelihood}}}{\underbrace{\textstyle\sum_l p_l \, f_l(x_i)}_{\color{#2b6cb0}\text{the mixture density at } x_i}}
$$

<div class="cols">
<div>

<h4 style="color: var(--gold)">Interpret as</h4>

- $\gamma_{ik} \geq 0$ and $\gamma_{i1} + \cdots + \gamma_{iK} = 1$
- the expected label: $\gamma_{ik} = E[\mathbb{1}_{Z_i = k} \mid x_i, \theta]$
- $K = 2$: $\; \gamma_{i1} = E[Z_i \mid x_i, \theta]$

</div>
<div>

<h4 style="color: var(--green)">Benefits</h4>

- computable the moment $\theta$ is known
- a soft label: no decision is taken

</div>
</div>

<div class="note mt-4" style="text-align: center">

$\gamma_{ik}$ is the responsibility of component $k$ for point $i$.

</div>

---
layout: fig
---

## Responsibility

<RespPicture />

---
layout: fig
---

## Responsibility as a matrix

<RespMatrix />

---
layout: fig
---

## Soft and hard

<SoftHard />

---
layout: section
---

# Expectation-Maximization algorithm

---
layout: eq
---

## Alternate

<div class="loop">
<div class="box blue"><b>E-step</b><div class="sub"><i>θ</i> fixed → compute <i>γ<sub>ik</sub></i></div></div>
<div class="arrows">soft labels<div class="a">⇄</div>new parameters</div>
<div class="box green"><b>M-step</b><div class="sub"><i>γ</i> fixed → compute <i>θ</i></div></div>
</div>

<div class="cols">
<div>

<h4>Each half is exact</h4>

- Bayes' rule, no approximation
- weighted means and variances

</div>
<div>

<h4 style="color: var(--red)">The flaws</h4>

- a local maximum
- an initialization to pick

</div>
</div>

<div class="note mt-4" style="text-align: center">Nothing is ever optimised jointly, yet the observed likelihood climbs at every pass.</div>

---
layout: eq
---

## Expectation–Maximization

<div class="algo" style="border-color: var(--blue)">

| | |
|---|---|
| <em class="hl-blue">input</em> | $x_1, \ldots, x_n$, and the number of components $K$ |
| <em class="hl-blue">init</em> | $\theta^0 = (p_k^0, \mu_k^0, \sigma_k^0)_k$, at random or from a clustering |
| **repeat** | E-step: $\;\gamma_{ik} \leftarrow p_k^t f_{k,t}(x_i) \,/\, \sum_l p_l^t f_{l,t}(x_i)$, for all $i, k$ |
| | M-step: $\;n_k \leftarrow \sum_i \gamma_{ik}, \quad p_k^{t+1} \leftarrow n_k / n$ |
| | $\qquad\qquad\; \mu_k^{t+1} \leftarrow (1/n_k) \sum_i \gamma_{ik}\, x_i$ |
| | $\qquad\qquad\; (\sigma_k^{t+1})^2 \leftarrow (1/n_k) \sum_i \gamma_{ik}\,(x_i - \mu_k^{t+1})^2$ |
| <em class="hl-gold">until</em> | $\ell_{\mathrm{obs}}(\theta^t)$ stops increasing |
| <em class="hl-green">output</em> | $\hat{\theta}$, and the responsibilities $\gamma$ as soft labels |

</div>

<div class="note mt-4" style="text-align: center">

Cost per pass: $\mathcal{O}(nKd)$ on the line, $\mathcal{O}(nKd^2)$ with full covariances. No step size, no line search: every update is a closed form.

</div>

---
layout: fig
---

## The E-step

<EStep />

---
layout: fig
---

## The M-step

<MStep />

---
layout: eq
---

## Weighted by responsibility

<div class="note" style="text-align: center">Formulas counted softly</div>

| labels known | | labels unknown |
|---|---|---|
| $\color{#6b46c1}\hat{p}_k = \frac{1}{n} \sum_i \mathbb{1}_{z_i = k}$ | → | $\color{#6b46c1}p_k^{t+1} = \frac{1}{n} \sum_i \gamma_{ik}$ |
| $\color{#2b6cb0}\hat{\mu}_k = \frac{1}{n \hat{p}_k} \sum_{i : z_i = k} x_i$ | → | $\color{#2b6cb0}\mu_k^{t+1} = \frac{1}{n_k} \sum_i \gamma_{ik}\, x_i$ |
| $\color{#b7791f}\hat{\sigma}_k^2 = \frac{1}{n \hat{p}_k} \sum_{i : z_i = k} (x_i - \hat{\mu}_k)^2$ | → | $\color{#b7791f}(\sigma_k^{t+1})^2 = \frac{1}{n_k} \sum_i \gamma_{ik}(x_i - \mu_k^{t+1})^2$ |

<div class="box green mt-4">

The only change: $\mathbb{1}_{z_i = k}$ becomes $\gamma_{ik}$, and $n \hat{p}_k$ becomes $n_k = \gamma_{1k} + \cdots + \gamma_{nk}$

</div>

---
layout: fig
---

## Example run

<EmRun />

---
layout: fig
---

## Same run

<EmRun2d />

---
layout: fig
---

## Likelihood evolution

<EmMonotone />

---
layout: eq
---

## Cost per pass

| | Work | Cost | Note |
|---|---|---|---|
| <b style="color: var(--blue)">E-step</b> | $nK$ densities, then one division per entry | $\mathcal{O}(n K d^2)$ | the $d^2$ is the quadratic form |
| <b style="color: var(--green)">M-step</b> | $K$ weighted means and covariances | $\mathcal{O}(n K d^2)$ | one pass over the data |
| <b style="color: var(--gold)">memory</b> | the $\gamma$ matrix | $\mathcal{O}(n K)$ | |
| <b style="color: var(--purple)">passes</b> | until the likelihood flattens | usually tens | fast at first, slow near the top |

<div class="note mt-4" style="text-align: center">Linear in the sample size, so EM scales.</div>

---
layout: section
---

# Why it works

---
layout: eq
---

## EM alternate view

<div class="cols" style="gap: 0 1.5rem">
<div class="box blue" style="color: var(--ink)">

<b style="color: var(--blue)">As alternating estimation</b>

E: $\gamma \leftarrow$ labels, given $\theta$<br>M: $\theta \leftarrow$ parameters, given $\gamma$

<span class="note">the interpretation so far</span>

</div>
<div class="box green" style="color: var(--ink)">

<b style="color: var(--green)">As one function, maximised twice</b>

$F(\theta, q) = E_q[\ell(\theta; x, z)] - E_q[\log q(z)]$<br>E: $\max_q F$. $\quad$ M: $\max_{\theta} F$

<span class="note">the view for the proof</span>

</div>
</div>

<div class="mt-4">

**Used for the proof:**

- $q$ is any distribution over the latent labels, not just the posterior
- $F(\theta, q) \leq \ell_{\mathrm{obs}}(\theta)$ always, with equality exactly at $q(z) = P(z \mid x, \theta)$
- increasing $F$ increases $\ell_{\mathrm{obs}}$
- $F$ is separable, unlike $\ell_{\mathrm{obs}}$

</div>

---
layout: eq
---

## Splitting the log-likelihood

<div class="note" style="text-align: center">

An exact identity, true for any distribution $q$ over the labels: no inequality yet

</div>

<table class="steps">
<tr><td>

$\ell_{\mathrm{obs}}(\theta) = \log f(x \mid \theta)$

</td><td>

the observed log-likelihood: it does not depend on $z$

</td></tr>
<tr><td>

$\ell_{\mathrm{obs}}(\theta) = \log f(x, z \mid \theta) - \log P(z \mid x, \theta)$

</td><td>

Bayes' rule, $f(x \mid \theta) = f(x, z \mid \theta) / P(z \mid x, \theta)$, true for every $z$

</td></tr>
<tr><td>

$\ell_{\mathrm{obs}}(\theta) = \sum_z q(z) \log f(x, z \mid \theta) - \sum_z q(z) \log P(z \mid x, \theta)$

</td><td>

average over $z$ with weights $q(z)$: the left side is constant, and $q$ sums to 1

</td></tr>
<tr><td>

$\ell_{\mathrm{obs}}(\theta) = \sum_z q(z) \log \dfrac{f(x, z \mid \theta)}{q(z)} + \sum_z q(z) \log \dfrac{q(z)}{P(z \mid x, \theta)}$

</td><td>

subtract and add the average of $\log q(z)$, then group the logs

</td></tr>
<tr><td style="color: var(--green)">

$\ell_{\mathrm{obs}}(\theta) = F(\theta, q) + \mathrm{KL}\left( q \,\|\, P(\cdot \mid x, \theta) \right)$

</td><td>

name the two terms: $F$, and the Kullback-Leibler divergence

</td></tr>
</table>

<div class="note mt-2" style="text-align: center">

$F$ is the lecture's $F$, the ELBO of the Bayesian literature.

</div>

---
layout: eq
---

## Lower bound on the log-likelihood

<div class="note" style="text-align: center">

$\ell_{\mathrm{obs}}(\theta) = F(\theta, q) + \mathrm{KL}(q \,\|\, P(\cdot \mid x, \theta))$: a lower bound, plus a gap

</div>

<table class="steps">
<tr><td style="color: var(--blue)">

$-\mathrm{KL} = \sum_z q(z) \log \dfrac{P(z \mid x, \theta)}{q(z)} \leq \log \sum_z P(z \mid x, \theta) = 0$

</td><td>

Jensen (log is concave), then the $q(z)$ cancel and the posterior sums to 1

</td></tr>
<tr><td style="color: var(--blue)">

$\mathrm{KL} \geq 0$, $= 0$ only when $q(z) = P(z \mid x, \theta)$

</td><td>

so $F(\theta, q) \leq \ell_{\mathrm{obs}}(\theta)$, touching exactly at the posterior

</td></tr>
<tr><td>

$F(\theta, q) = E_q[\log f(x, z \mid \theta)] - E_q[\log q(z)]$

</td><td>

expected complete log-likelihood, plus the entropy of $q$

</td></tr>
<tr><td style="color: var(--green)">

$F(\theta, q) = \sum_i \sum_k q_{ik} \left( \log p_k f_k(x_i) - \log q_{ik} \right)$

</td><td>

mixture: the labels are independent given $x$, one row $(q_{i1}, \ldots, q_{iK})$ per point

</td></tr>
</table>

<div class="box green mt-4">

EM climbs $F$: over $q$ (E-step, $q_{ik} = \gamma_{ik}$), then over $\theta$ (M-step)

</div>

---
layout: eq
---

## Jensen step

<div class="note" style="text-align: center">Where the bound comes from: Jensen's inequality</div>

<table class="steps">
<tr><td>

$\log$ is concave: $\quad \log\left( \sum_z q(z)\, u(z) \right) \geq \sum_z q(z) \log u(z)$

</td><td>the log of an average is at least the average of the logs</td></tr>
<tr><td style="color: var(--green)">

$\ell_{\mathrm{obs}}(\theta) = \log \sum_z q(z)\, \dfrac{f(x, z \mid \theta)}{q(z)} \geq \sum_z q(z) \log \dfrac{f(x, z \mid \theta)}{q(z)}$

</td><td>

apply it with $u(z) = f(x, z \mid \theta) / q(z)$

</td></tr>
<tr><td>

$\ell_{\mathrm{obs}}(\theta) \geq F(\theta, q)$

</td><td>the sum has come out of the log, and that was the whole difficulty</td></tr>
</table>

<div class="box blue mt-4">

Equality when $f(x, z \mid \theta) / q(z)$ does not depend on $z$, that is, when $q$ is the posterior

</div>

---
layout: fig
---

## Jensen inequality

<JensenPic />

---
layout: fig
---

## E-step

<ElboE />

---
layout: fig
---

## M-step

<ElboM />

---
layout: fig
---

## Minorize–maximize steps

<MmSteps />

---
layout: eq
---

## Inequalities proving monotonicity

<table class="steps">
<tr><td style="color: var(--blue)">

$\ell_{\mathrm{obs}}(\theta^{t}) = F(\theta^{t}, q^{t})$

</td><td>

the E-step chose $q^t = P(z \mid x, \theta^t)$, which closes the KL gap

</td></tr>
<tr><td style="color: var(--green)">

$F(\theta^{t}, q^{t}) \leq F(\theta^{t+1}, q^{t})$

</td><td>

the M-step maximised $F(\cdot, q^t)$, and $\theta^t$ was one candidate

</td></tr>
<tr><td style="color: var(--gold)">

$F(\theta^{t+1}, q^{t}) \leq \ell_{\mathrm{obs}}(\theta^{t+1})$

</td><td>

$F$ is a lower bound for every $\theta$, touching or not

</td></tr>
</table>

<div class="box mt-4" style="border-color: var(--ink)">

$\ell_{\mathrm{obs}}(\theta^{t}) \leq \ell_{\mathrm{obs}}(\theta^{t+1}) \qquad \forall t$

</div>

---
layout: eq
---

## Closed form derivation

<div class="note" style="text-align: center">Three independent problems</div>

<table class="steps">
<tr><td style="color: var(--purple)">

$\max_{p} \; \sum_i \sum_k \gamma_{ik} \log p_k \quad$ subject to $\;p_1 + \cdots + p_K = 1$

</td><td>

a Lagrange multiplier gives $p_k = n_k / n$ with $n_k = \sum_i \gamma_{ik}$

</td></tr>
<tr><td style="color: var(--blue)">

$\max_{\mu_k} \; -\dfrac{1}{2\sigma_k^2} \sum_i \gamma_{ik} (x_i - \mu_k)^2$

</td><td>

a weighted least squares: $\mu_k = (1/n_k) \sum_i \gamma_{ik} x_i$

</td></tr>
<tr><td style="color: var(--gold)">

$\max_{\sigma_k} \; -\sum_i \gamma_{ik} \left( \log \sigma_k + \dfrac{(x_i - \mu_k)^2}{2 \sigma_k^2} \right)$

</td><td>

set the derivative to zero: $\sigma_k^2 = (1/n_k) \sum_i \gamma_{ik} (x_i - \mu_k)^2$

</td></tr>
</table>

---
layout: eq
---

## Where it stops

<div class="note" style="text-align: center">What the proof does and does not promise</div>

<div class="cols">
<div>

<h4 style="color: var(--green)">Guaranteed</h4>

- $\ell_{\mathrm{obs}}(\theta^t)$ increases at every pass
- limit points are stationary points of $\ell_{\mathrm{obs}}$
- no step size, no divergence, no tuning

</div>
<div>

<h4 style="color: var(--red)">Not guaranteed</h4>

- the global maximum (only a local maximum)
- the point of convergence depends on the initialization
- a finite limit: $\sigma_k \to 0$ sends $\ell_{\mathrm{obs}} \to +\infty$

</div>
</div>

<div class="note mt-4" style="text-align: center">

In practice: use several random starts, keep the best $\ell_{\mathrm{obs}}$.

</div>

---
layout: section
---

# Expectation-Maximization variations

---
layout: eq
---

## Algorithm variations

| Variant | What replaces $z_i$ | Information kept | Character |
|---|---|---|---|
| <b style="color: var(--green)">EM</b> | keep $\gamma_{ik}$, weight by it | the expectation itself | monotone, smooth |
| <b style="color: var(--blue)">Classification EM</b> | $z_i = \arg\max_k \gamma_{ik}$ | the most likely label | equivalent to $k$-means |
| <b style="color: var(--gold)">SEM (Stochastic)</b> | draw $z_i \sim \gamma_{i\cdot}$ | one random label | escapes saddles, noisy |
| <b style="color: var(--purple)">$N$-SEM</b> | draw $N$ labels per point | $N$ random labels | EM is the limit $N \to \infty$ |

<div class="note mt-4" style="text-align: center">All four share the M-step.</div>

---
layout: fig
---

## k-means is a limit case of EM

<div class="formula">

$$
p_k = \tfrac{1}{K},\; \sigma_k = \sigma: \qquad \gamma_{ik} = \frac{\exp\left( -\|x_i - \mu_k\|^2 / 2\sigma^2 \right)}{\sum_l \exp\left( -\|x_i - \mu_l\|^2 / 2\sigma^2 \right)} \;\xrightarrow[\sigma \to 0]{}\; \mathbb{1}\left[k = \arg\min_l \|x_i - \mu_l\|^2\right]
$$

</div>

<KmeansLimit />

<div class="box green lead-note" style="font-size: 0.85rem; padding: 0.35rem">

$k$-means is EM with hard assignment and spherical, equal, vanishing covariances: then $\mu_k \leftarrow$ the mean of its points.

</div>

---
layout: fig
---

## k-means vs Gaussian mixture

<KmeansVsGmm />

---
layout: eq
---

## Stochastic EM

<div class="algo" style="border-color: var(--gold)">

| | |
|---|---|
| <em class="hl-blue">init</em> | labels $z_1, \ldots, z_n$ at random |
| **repeat** | M: $\hat{\theta} = \arg\max_\theta \; \ell\left[(x_1, z_1), \ldots, (x_n, z_n); \theta\right]$, the complete-data MLE (count and average) |
| | S: for each $i$, draw $z_i \sim P_{\hat{\theta}}(Z \mid X_i = x_i)$: a draw, not an arg max and not an average |
| <em class="hl-gold">until</em> | the parameters stop drifting |

</div>

<div class="cols mt-4">
<div>

<h4 style="color: var(--green)">Pros</h4>

- can "jump out of a bad basin"
- easy to implement

</div>
<div>

<h4 style="color: var(--red)">Cons</h4>

- the likelihood no longer climbs monotonically
- it never fully converges: $\theta^t$ wanders

</div>
</div>

---
layout: fig
---

## SEM example

<SemRun />

---
layout: eq
---

## N draws per point

<div class="cards3">
<div class="card" style="border-color: var(--blue)">
<div class="h hl-blue">N = 1</div>
<div>one label per point, drawn at random</div>
<div class="out hl-blue">stochastic, noisy</div>
</div>
<div class="card" style="border-color: var(--gold)">
<div class="h hl-gold">N draws</div>
<div>replicate the sample N times, draw a label in each</div>
<div class="out hl-gold">noise averages out</div>
</div>
<div class="card" style="border-color: var(--green)">
<div class="h hl-green">N → ∞</div>
<div>the average over draws becomes an expectation</div>
<div class="out hl-green">original EM</div>
</div>
</div>

$$
\frac{1}{N} \sum_{j=1}^{N} \ell\left[ (x_i, z_i^j)_i ; \theta \right] \;\longrightarrow\; E\left[ \ell\left[ (x_i, Z_i)_i; \theta \right] \right]
$$

<div class="note" style="text-align: center">Law of large numbers over independent draws: the randomness disappears and the expectation is reached.</div>

---
layout: fig
---

## k-means vs EM vs SEM vs N-SEM

<Variants />

---
layout: section
---

# Reach convergence

---
layout: eq
---

## Where you start matters

<div class="rows">
<div class="k" style="color: var(--red)">all components equal</div><div>stuck: already a (bad) fixed point</div>
<div class="k" style="color: var(--gold)">K points drawn at random</div><div>a cheap, honest start; keep the best</div>
<div class="k" style="color: var(--green)">k-means</div><div>

the usual default: centroids become $\mu_k$, clusters give $p_k$ and $\Sigma_k$

</div>
<div class="k" style="color: var(--blue)">previous fit</div><div>

a good "warm start" when $K$ or the data changes

</div>
</div>

<div class="note mt-6" style="text-align: center">Avoid a symmetric start and a zero variance.</div>

---
layout: fig
---

## Starts comparison

<InitCompare />

---
layout: eq
---

## Guarding against collapse

<div class="note" style="text-align: center">Keeping a component from collapsing onto a point</div>

<table class="steps">
<tr><td style="color: var(--red)">

Symptom: $\; n_k \to 1$, $|\Sigma_k| \to 0$, $\;\ell_{\mathrm{obs}} \to +\infty$

</td><td>

the more likely, the larger $K$ and $d$ are

</td></tr>
<tr><td style="color: var(--green)">

Cure 1: $\; \Sigma_k \leftarrow \Sigma_k + \varepsilon I$

</td><td>a ridge on the covariance</td></tr>
<tr><td style="color: var(--green)">

Cure 2: $\;$ restart the component when $n_k$ falls below a floor

</td><td>put it back on a random point</td></tr>
<tr><td style="color: var(--green)">

Cure 3: $\;$ restrict $\Sigma_k$

</td><td>fewer free numbers give less room to collapse</td></tr>
</table>

<div class="box mt-4" style="border-color: var(--ink)">None of these change the algorithm</div>

---
layout: fig
---

## Covariance types

<CovChoice />

---
layout: eq
---

## AIC and BIC

<div class="note" style="text-align: center">Two penalised likelihoods: fit, minus a price per free parameter</div>

$$
{\color{#b7791f}\mathrm{AIC} = -2\,\ell_{\mathrm{obs}}(\hat\theta) + 2\,m}
\qquad\qquad
{\color{#00ab0e}\mathrm{BIC} = -2\,\ell_{\mathrm{obs}}(\hat\theta) + m\,\log n}
$$

<div class="note" style="text-align: center">

$\hat\theta$: the fitted model, $\; n$: the sample size, $\; m$: the free parameters; for $K$ Gaussians in $d$ dimensions, $m = (K - 1) + Kd + K\,d(d+1)/2$

</div>

<div class="cols mt-2">
<div>

<h4 style="color: var(--gold)">AIC (Akaike, 1973)</h4>

- estimates how well the model will predict new data
- penalty: 2 per parameter
- tends to pick a $K$ a bit too large

</div>
<div>

<h4 style="color: var(--green)">BIC (Schwarz, 1978)</h4>

- $-\mathrm{BIC}/2 \approx \log P(x \mid \text{model})$, the evidence for the model
- penalty: $\log n$ per parameter
- finds the true $K$ as $n$ grows

</div>
</div>

<div class="box mt-4" style="border-color: var(--ink)">

Both: lower is better; fit every $K$, keep the minimum. BIC penalises more as soon as $n \geq 8$.

</div>

---
layout: fig
---

## Number of components

<ChoosingK />

---
layout: fig
---

## Example on real data

<IrisFit />

---
layout: fig
---

## Scoring a new point

<Anomaly />

---
layout: eq
---

## Beyond the Gaussian

<div class="note" style="text-align: center">The same two steps with a different component density</div>

| | | |
|---|---|---|
| <b style="color: var(--blue)">Student mixture</b> | $f_k$ a multivariate $t$ | heavy tails (outliers stop dragging the centres) |
| <b style="color: var(--green)">Bernoulli mixture</b> | $f_k$ a product of Bernoullis | binary data |
| <b style="color: var(--gold)">Poisson mixture</b> | $f_k$ a Poisson law | counts |
| <b style="color: var(--purple)">mixture of regressions</b> | $f_k$ a law for $y \mid x$ | |
| <b style="color: var(--red)">hidden Markov model</b> | $Z$ a Markov chain, not i.i.d. | |

<div class="note mt-4" style="text-align: center">EM only used the latent label and the complete-data likelihood, so it can be adapted.</div>

---
layout: eq
---

## Conclusion

<div class="cols">
<div>

<h4 style="color: var(--green)">Pros</h4>

- density and soft clustering in one fit
- clusters with shape
- no step size to tune
- transfers to other latent-variable models

</div>
<div>

<h4 style="color: var(--red)">Cons</h4>

- a local maximum
- dependence on the initialization
- the likelihood is unbounded, and needs guarding
- $K$ needs tuning

</div>
</div>
