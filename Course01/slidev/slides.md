---
theme: default
title: "Session 1: Introduction and Reminders on Machine Learning"
info: |
  Advanced Machine Learning · MSc DSBA · 2026 · Paul Dubois
  Interactive companion to Course01/slides.pptx.
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

# Session 1<br>Introduction and Reminders on Machine Learning

Advanced Machine Learning · MSc DSBA · 2026

Paul Dubois

<div class="note mt-8">Week 1 lecture</div>

---
layout: section
---

# Practical information

---
layout: fig
---

## Summary

<StaticFig name="about" />

---
layout: fig
---

## Expected to be known already

<StaticFig name="prerequisites" />

---
layout: eq
---

## Reading material

<div class="lead" style="font-size: 1.1rem; line-height: 2">

- G. James, D. Witten, T. Hastie, R. Tibshirani: *An Introduction to Statistical Learning* (2013)
- T. Hastie, R. Tibshirani, J. Friedman: *The Elements of Statistical Learning* (2009)
- C. M. Bishop: *Pattern Recognition and Machine Learning* (2006)

</div>

<p class="note" style="margin-top: 1.5rem">Slides, labs, data and announcements live on GitHub.</p>

---
layout: eq
---

## Grading

<div class="lead" style="font-size: 1.1rem; line-height: 1.8">

100% of your grade will be based on the final project report.

The goal is for you to pick up some topic of your interest, with public data available.
Produce an analysis using one or more technique(s) introduced during this course.
You will write your findings in a report of ~5 pages.

</div>

---
layout: section
---

# Suggested datasets for the project

---
layout: fig
---

## 1. Stars CYG OB1

<StaticFig name="ds_stars" />

---
layout: fig
---

## 2. Ames Housing

<StaticFig name="ds_ames" />

---
layout: fig
---

## 3. DVF, Demandes de Valeurs Foncières

<StaticFig name="ds_dvf" />

---
layout: fig
---

## 4. Breast Cancer Wisconsin (Diagnostic)

<StaticFig name="ds_breast_cancer" />

---
layout: fig
---

## 5. Adult (Census Income)

<StaticFig name="ds_adult" />

---
layout: fig
---

## 6. Credit Card Fraud Detection (ULB)

<StaticFig name="ds_creditcard" />

---
layout: fig
---

## 7. Spambase

<StaticFig name="ds_spambase" />

---
layout: fig
---

## 8. USGS Earthquake Catalogue

<StaticFig name="ds_earthquakes" />

---
layout: fig
---

## 9. Vélib' Métropole station availability

<StaticFig name="ds_velib" />

---
layout: fig
---

## 10. Online Retail II

<StaticFig name="ds_online_retail" />

---
layout: fig
---

## 11. Wholesale Customers

<StaticFig name="ds_wholesale" />

---
layout: fig
---

## 12. 20 Newsgroups

<StaticFig name="ds_newsgroups" />

---
layout: fig
---

## 13. Olivetti Faces (AT&T)

<StaticFig name="ds_olivetti" />

---
layout: fig
---

## 14. MovieLens 100K

<StaticFig name="ds_movielens" />

---
layout: fig
---

## 15. Galaxies (Roeder, 1990)

<StaticFig name="ds_galaxies" />

---
layout: fig
---

## 16. Palmer Penguins

<StaticFig name="ds_penguins" />

---
layout: fig
---

## 17. Berkeley Segmentation Dataset (BSDS500)

<StaticFig name="ds_bsds" />

---
layout: fig
---

## 18. Fashion MNIST

<StaticFig name="ds_fashion_mnist" />

---
layout: fig
---

## 19. PBMC 3k (single cell RNA sequencing)

<StaticFig name="ds_pbmc" />

---
layout: fig
---

## 20. Human Activity Recognition Using Smartphones

<StaticFig name="ds_har" />

---
layout: fig
---

## 21. COIL 20

<StaticFig name="ds_coil20" />

---
layout: fig
---

## Where Machine Learning is used

<StaticFig name="applications" />

---
layout: section
---

# Reminders on parameter estimation

---
layout: eq
---

## Learning is estimating parameters

<div class="chain">
<div><div class="lab">labelled examples</div><div class="box blue">

$X,\ y$

</div></div>
<div class="arrow">→</div>
<div><div class="lab">a hypothesis</div><div class="box green">

$f_\theta(x)$

</div></div>
<div class="arrow">→</div>
<div><div class="lab">a cost</div><div class="box red">

$J(\theta)$

</div></div>
<div class="arrow">→</div>
<div><div class="lab">the parameters</div><div class="box purple">

$\hat\theta = \arg\min_\theta J(\theta)$

</div></div>
</div>

<p style="text-align: center; margin-top: 1rem">the parameters are estimated using the training data</p>

<div style="margin: 1.6rem auto 0; width: fit-content">

**two questions of estimation theory:**

- which cost: least squares, a likelihood, a posterior?
- how good is the $\hat\theta$ we chose?

</div>

---
layout: fig
---

## How close, on average?

<BiasHist />

---
layout: fig
---

## How stable?

<VarianceHist />

---
layout: fig
---

## Bias and variance are independent problems

<Dartboard />

---
layout: eq
---

## One number for both bias & var

<div style="font-size: 1.5em">

$$
MSE(\hat\theta_j) \;=\; {\color{#6b46c1} E\big[(\hat\theta_j - \theta_j)^2\big]} \;=\; {\color{#c53030}\mathrm{bias}(\hat\theta_j)^2} \;+\; {\color{#2b6cb0} Var(\hat\theta_j)}
$$

</div>

<div class="three" style="margin-top: 1rem">
<div><b>what we want small</b></div>
<div style="color: var(--red)">being wrong on average</div>
<div style="color: var(--blue)">being unstable</div>
</div>

<p class="note" style="text-align: center; margin-top: 1rem">the MSE is how far from the truth we land, on average over samples</p>

---
layout: eq
---

## Three ways to find a good estimator

<div class="cards3">
<div class="card" style="border-color: var(--blue)">
<div class="h" style="color: var(--blue)">method of moments</div>
<p>match the moments of the model to the moments of the data</p>
<p class="note out">easy, robust, less accurate</p>
</div>
<div class="card" style="border-color: var(--green)">
<div class="h" style="color: var(--green)">maximum likelihood</div>
<p>pick the parameter that makes the data most probable</p>
<p class="note out">efficient, model-dependent</p>
</div>
<div class="card" style="border-color: var(--purple)">
<div class="h" style="color: var(--purple)">Bayesian estimation</div>
<p>combine a prior on θ with the likelihood, then minimise a cost</p>
<p class="note out">prior knowledge, prior sensitivity</p>
</div>
</div>

---
layout: fig
---

## Method of moments: match what you can compute

<MomIdea />

---
layout: eq
---

## Method of moments: the Gaussian case

<div style="text-align: center; font-size: 1.1rem">

Gaussian: $\theta = (\mu, \sigma^2)$

</div>

<table class="steps mom">
<tbody>
<tr><td style="color: var(--green)">theoretical</td><td>

${\color{#00ab0e} E[x] = \mu}$

</td><td>

${\color{#00ab0e} E[x^2] = \sigma^2 + \mu^2}$

</td></tr>
<tr><td style="color: var(--blue)">sample</td><td>

${\color{#2b6cb0} U_1 = \frac{1}{n}\sum_i x_i}$

</td><td>

${\color{#2b6cb0} U_2 = \frac{1}{n}\sum_i x_i^2}$

</td></tr>
<tr><td style="color: var(--purple)">solution</td><td>

${\color{#6b46c1} \hat\mu = \frac{1}{n}\sum_i x_i}$

</td><td>

${\color{#6b46c1} \hat\sigma^2 = \frac{1}{n}\sum_i (x_i - \hat\mu)^2}$

</td></tr>
</tbody>
</table>

---
layout: eq
---

## What the method of moments is worth

<div class="pros">
<div>
<h4 style="color: var(--green)">in its favour</h4>

- strongly consistent
- robust: moments move slowly
- cheap: closed form, no search
- a good starting point for other methods

</div>
<div>
<h4 style="color: var(--red)">against</h4>

- not asymptotically efficient
- generally less accurate
- higher moments are noisy
- can leave the parameter space

</div>
</div>

---
layout: eq
---

## What is likelihood?

<p class="note" style="text-align: center">the model gives every observation a density f(x; θ); the sample is i.i.d.</p>

$$
L(x_1, \dots, x_n; \theta) \;=\; \prod_{i=1}^n f(x_i; \theta)
\qquad\qquad
\ell(\theta) \;=\; \log L \;=\; \sum_{i=1}^n \log f(x_i; \theta)
$$

<div class="cols" style="margin-top: 1rem">
<div class="box blue">

as a function of $x$, with $\theta$ fixed

<span style="color: var(--ink)">a density: how the data is spread</span>

$\int f(x; \theta)\, dx = 1$

</div>
<div class="box green">

as a function of $\theta$, with $x$ fixed

<span style="color: var(--ink)">the likelihood: how well θ explains the data</span>

$\int L(x; \theta)\, d\theta \neq 1$

</div>
</div>

<p style="text-align: center; color: var(--red); margin-top: 0.8rem">the likelihood is not a probability over θ</p>

---
layout: fig
---

## Likelihood on data

<LikelihoodBuild />

---
layout: fig
---

## Maximum likelihood on data

<MleIdea />

---
layout: fig
---

## Why taking the log

<LogLik />

---
layout: fig
---

## Maximum likelihood: the Gaussian case

<MleGaussian />

---
layout: eq
---

## What maximum likelihood is worth

<div class="pros">
<div>
<h4 style="color: var(--green)">in its favour</h4>

- one analytical function to optimise
- strongly consistent, asymptotically unbiased
- asymptotically efficient
- smallest variance among unbiased estimators

</div>
<div>
<h4 style="color: var(--red)">against</h4>

- needs the shape of the density
- not robust to outliers
- no closed form in general
- can be biased for finite n

</div>
</div>

---
layout: fig
---

## When parameters follow a random distribution

<BayesSetup />

---
layout: eq
---

## The posterior

<div style="font-size: 1.05em">

$$
p(\theta \mid x_1, \dots, x_n) \;=\; \frac{L(x_1, \dots, x_n; \theta)\, p(\theta)}{\int_{\mathbb{R}^p} L(x_1, \dots, x_n; \theta)\, p(\theta)\, d\theta} \;\propto\; L(x_1, \dots, x_n; \theta)\, p(\theta)
$$

</div>

<p style="text-align: center; color: var(--purple); font-size: 1.1rem; margin-top: 1rem">the posterior gives a whole distribution</p>
<p class="note" style="text-align: center">which number θ̂ should be reported?</p>

---
layout: fig
---

## From parameter predicted distribution to value

<CostIdea />

---
layout: fig
---

## Three costs, three estimators

<CostZoo />

---
layout: fig
---

## How much the prior matters

<PriorEffect />

---
layout: eq
---

## Three divisors

<p class="note" style="text-align: center">every estimator of σ² below divides the same scatter S = Σᵢ (xᵢ − x̄)²</p>

<div style="font-size: 1.6em">

$$
\hat\sigma^2 \;=\; S \,/\, c
$$

</div>

<div class="cards3">
<div class="card" style="border-color: var(--green)">
<div class="h" style="color: var(--green)">MLE</div>
<p style="color: var(--green); font-size: 1.1rem">c = n</p>
<p>maximise the likelihood</p>
</div>
<div class="card" style="border-color: var(--blue)">
<div class="h" style="color: var(--blue)">unbiased</div>
<p style="color: var(--blue); font-size: 1.1rem">c = n − 1</p>

make $E[\hat\sigma^2] = \sigma^2$

</div>
<div class="card" style="border-color: var(--purple)">
<div class="h" style="color: var(--purple)">shrunk</div>
<p style="color: var(--purple); font-size: 1.1rem">c = n + 1</p>
<p>minimise the MSE</p>
</div>
</div>

---
layout: fig
---

## Unbiased is not the same as best

<EstimatorsCompare />

---
layout: eq
---

## Where n comes from: the likelihood

<p class="note" style="text-align: center">the Gaussian log-likelihood, once μ̂ = x̄ is plugged in</p>

$$
\ell(\sigma^2) \;=\; -\frac{n}{2}\log(2\pi\sigma^2) \;-\; \frac{S}{2\sigma^2}
$$

$$
\frac{\partial \ell}{\partial \sigma^2} \;=\; -\frac{n}{2\sigma^2} + \frac{S}{2\sigma^4} \;=\; 0
$$

$$
{\color{#00ab0e} \hat\sigma^2_{MLE} \;=\; \frac{S}{n}}
$$

<p class="note" style="text-align: center">the likelihood only asks which σ² makes this sample most probable, it does not make it right on average</p>

---
layout: fig
---

## Where n − 1 comes from: a lost degree of freedom

<Bessel />

---
layout: fig
---

## Where n + 1 comes from: the smallest MSE

<MseDivisor />

---
layout: section
---

# Supervised learning

---
layout: eq
---

## The setting

<div class="flow sup">
<div class="stack">
<div class="box blue">

$X = (x_1, \dots, x_N)$

<div class="lab">inputs</div>
</div>
<div class="box green">

$Y = (y_1, \dots, y_N)$

<div class="lab">labels</div>
</div>
</div>
<div class="arrow">→</div>
<div class="box purple" style="font-size: 1.2rem">learn f</div>
<div class="arrow">→</div>
<div class="box gold">

$\hat y = f(x)$

<div class="lab">on new inputs</div>
</div>
</div>

<p class="note" style="text-align: center">the labels are known</p>

---
layout: fig
---

## Regression or classification

<RegClass />

---
layout: eq
---

## Examples

| | x | y | |
|---|---|---|---|
| <b style="color: var(--blue)">stock price</b> | economic, social, political variables | a price | <span style="color: var(--blue)">regression</span> |
| <b style="color: var(--green)">weather</b> | location, season, past measurements | a temperature | <span style="color: var(--green)">regression</span> |
| <b style="color: var(--purple)">image classification</b> | pixels or voxels | one of K labels | <span style="color: var(--purple)">classification</span> |
| <b style="color: var(--red)">digit recognition</b> | a 28 × 28 image | y ∈ &#123;0, …, 9&#125; | <span style="color: var(--red)">classification</span> |

---
layout: fig
---

## Two ways to build a classifier

<DiscGen />

---
layout: eq
---

## Bayes classifier

<div style="font-size: 1.0em">

$$
\hat C(x) \;=\; \arg\max_k P(X{=}x \mid C{=}k) \;=\; \arg\max_k \frac{f_k(x)\, \pi_k}{\sum_{i=1}^K f_i(x)\, \pi_i} \;=\; \arg\max_k f_k(x)\, \pi_k
$$

</div>

<div class="cols" style="text-align: center; margin-top: 1rem">
<div style="color: var(--blue)">π<sub>k</sub>: the prior of class k</div>
<div style="color: var(--red)">f<sub>k</sub>(x): the density inside class k</div>
</div>

<p class="note" style="text-align: center; margin-top: 1rem">the denominator does not depend on k</p>

---
layout: fig
---

## Bayes classifier

<BayesIngredients />

---
layout: eq
---

## Naive Bayes: assume the features are independent

<div style="font-size: 1.8em">

$$
{\color{#00ab0e} f_k(x) \;=\; \prod_{j=1}^d f_k(x_j)}
$$

</div>

<p style="text-align: center; font-size: 1.05rem">the features are assumed independent inside a class</p>

<div class="cols" style="text-align: center; margin-top: 1rem">
<div style="color: var(--green)">d univariate densities<br>instead of one in d dimensions</div>
<div class="note">the assumption is almost always false<br>…but the classifier often works anyway</div>
</div>

---
layout: fig
---

## Naive Bayes: spam filtering

<SpamFilter />

---
layout: fig
---

## Naive Bayes: the zero distribution problem

<Laplace />

---
layout: fig
---

## Naive Bayes on continuous features

<NbGaussian />

---
layout: eq
---

## Linear discriminant analysis

<p style="text-align: center; font-size: 1.05rem">continuous features, Gaussian classes</p>

<div style="font-size: 1.3em">

$$
f_k(x) = \frac{1}{(2\pi)^{d/2} |\Sigma_k|^{1/2}} \exp\!\Big(-\tfrac12 (x - \mu_k)^T \Sigma_k^{-1} (x - \mu_k)\Big)
$$

</div>

<p style="text-align: center; color: var(--green); font-size: 1.15rem; margin-top: 0.8rem">

LDA assumes one shared covariance: $\Sigma_k = \Sigma \quad \forall k$

</p>

<p class="note" style="text-align: center">same shape for every class, only the centres move</p>

---
layout: fig
---

## LDA, step by step

<LdaFitSteps />

---
layout: eq
---

## LDA: computing the rule

<div style="font-size: 1.15em">

$$
\begin{aligned}
\hat C(x) &= \arg\max_k P(X{=}x \mid C{=}k) \\
&= \arg\max_k f_k(x)\,\pi_k \;=\; \arg\max_k \log\big[f_k(x)\,\pi_k\big] \\
&= \arg\max_k -\tfrac12 (x - \mu_k)^T \Sigma^{-1} (x - \mu_k) + \log \pi_k \\
&= {\color{#00ab0e} \arg\max_k\ x^T \Sigma^{-1}\mu_k - \tfrac12 \mu_k^T \Sigma^{-1} \mu_k + \log \pi_k}
\end{aligned}
$$

</div>

<p class="note" style="text-align: center">−½ xᵀΣ⁻¹x can be dropped, since it is the same for every class</p>

---
layout: fig
---

## LDA: a linear decision boundary

<LdaBoundary />

---
layout: fig
---

## LDA: why the boundary is straight

<LdaWhyLinear />

---
layout: eq
---

## LDA: values estimated from the training set

<div class="rows" style="font-size: 1.1rem; width: fit-content; margin: 0 auto">
<div class="k" style="color: var(--blue)">priors</div><div>

$\hat\pi_k = N_k / N$

</div>
<div class="k" style="color: var(--green)">class means</div><div>

$\hat\mu_k = \frac{1}{N_k} \sum_{x_i \in C_k} x_i$

</div>
<div class="k" style="color: var(--purple)">pooled covariance</div><div>

$\hat\Sigma = \frac{1}{N - K} \sum_{k=1}^K \sum_{x_i \in C_k} (x_i - \hat\mu_k)(x_i - \hat\mu_k)^T$

</div>
</div>

<p style="text-align: center; color: var(--red); margin-top: 1.2rem">estimates are poor when N &lt; d</p>

---
layout: fig
---

## QDA: one covariance per class

<QdaVsLda />

---
layout: fig
---

## QDA shapes

<QdaShapes />

---
layout: fig
---

## LDA vs QDA: costs & benefits

<LdaQdaCost />

---
layout: section
---

# Unsupervised learning

---
layout: eq
---

## The setting

<div class="flow unsup">
<div class="box blue">

$X = (x_1, \dots, x_N)$

<div class="lab">no labels</div>
</div>
<div class="arrow">→</div>
<div class="box purple" style="font-size: 1.2rem">find structure</div>
<div class="arrow">→</div>
<div class="stack">
<div class="box gold">groups</div>
<div class="box gold">coordinates</div>
</div>
</div>

<p class="note" style="text-align: center">the labels are unknown</p>

---
layout: eq
---

## Two families

<div class="cols" style="text-align: center; align-items: start">
<div>
<h4 style="color: var(--blue)">dimension reduction</h4>

$X \in \mathbb{R}^{N \times d} \;\xrightarrow{\;q < d\;}\; Z \in \mathbb{R}^{N \times q}$

<p class="note" style="margin-top: 0.8rem">fewer columns, the same rows</p>
<p class="note">used to: visualise, denoise, compute faster</p>
</div>
<div>
<h4 style="color: var(--gold)">clustering</h4>

$X \;\longrightarrow\; C_1, \dots, C_K$

<p class="note" style="margin-top: 0.8rem">every row gets a group</p>
<p class="note">used to: visualise, regroup, analyse</p>
</div>
</div>

---
layout: eq
---

## Typical tasks

| | x | output |
|---|---|---|
| <b style="color: var(--blue)">detect customer classes</b> | purchase history | C<sub>k</sub>: customer types |
| <b style="color: var(--green)">image segmentation</b> | patch of pixels or voxels | C<sub>k</sub>: blood, muscle, tumour |
| <b style="color: var(--purple)">text mining</b> | e-mails, documents | C<sub>k</sub>: themes |
| <b style="color: var(--gold)">data visualisation</b> | d-dimensional data | z ∈ ℝ² to plot |

---
layout: eq
---

## k-means goal

<div style="font-size: 1.6em">

$$
{\color{#b7791f} J_w \;=\; \sum_{k=1}^K \sum_{x_i \in C_k} \|x_i - \mu_k\|^2}
$$

</div>

<p style="text-align: center; font-size: 1.05rem">find the K centres that make the within-cluster distance as small as possible</p>

<div class="cols" style="text-align: center; margin-top: 1rem">
<div style="color: var(--red)">the exact problem is NP-hard</div>
<div style="color: var(--green)">

k-means finds a local minimum in $O(tKN)$

</div>
</div>

---
layout: fig
---

## k-means algorithm

<KmeansAlgo />

---
layout: fig
---

## k-means limitations

<KmeansWeak />

---
layout: fig
---

## PCA: directions of maximum variance

<PcaProjection />

---
layout: fig
---

## PCA: how much can be dropped

<PcaSpectrum />

---
layout: eq
---

## Conclusion

<div class="tree">
<div class="root box">estimate parameters</div>
<div class="branches">
<div>
<div class="box blue head">supervised</div>
<div class="box blue leaf">Bayes classifier</div>
<div class="box blue leaf">naive Bayes</div>
<div class="box blue leaf">LDA / QDA</div>
</div>
<div>
<div class="box gold head">unsupervised</div>
<div class="box gold leaf">k-means</div>
<div class="box gold leaf">PCA</div>
</div>
</div>
</div>
