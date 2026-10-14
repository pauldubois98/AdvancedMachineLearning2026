---
theme: default
title: "Session 3 bis: Trees, Forests and Boosting"
info: |
  Advanced Machine Learning · MSc DSBA · 2026 · Paul Dubois
  Interactive companion to Course03/slides-bis.pptx.
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
favicon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23fff'/%3E%3Cpath d='M16 4 L16 11 M16 11 L8 19 M16 11 L24 19' stroke='%231b1b1b' stroke-width='2.2' fill='none'/%3E%3Ccircle cx='8' cy='23' r='3.4' fill='%232b6cb0'/%3E%3Ccircle cx='24' cy='23' r='3.4' fill='%23c53030'/%3E%3C/svg%3E"
layout: cover
---

# Session 3 bis<br>Trees, Forests and Boosting

Advanced Machine Learning · MSc DSBA · 2026

Paul Dubois

<div class="note mt-8">Week 3 lecture · every figure here is live: move the sliders</div>

---
layout: section
---

# Decision trees

---
layout: fig
---

## A tree is a sequence of questions

<TreeQuestions />

---
layout: fig
---

## Choosing the split

<TreeSplit />

---
layout: fig
---

## What "pure" means

<ImpurityCurves />

---
layout: fig
---

## Depth is the capacity knob

<TreeDepth />

---
layout: fig
---

## Regression trees predict staircases

<TreeRegression />

---
layout: fig
---

## And they over-fit

<TreeOverfit />

---
layout: fig
---

## The real problem: instability

<TreeInstability />

---
layout: section
---

# Random forests

---
layout: fig
---

## The idea

<AveragingDemo />

---
layout: eq
---

## Trees must disagree

$$ \mathrm{Var}\left(\bar f\right) \;=\; \textcolor{#00ab0e}{\frac{\sigma^2}{M}} \;+\; \textcolor{#c53030}{\frac{M-1}{M}\,\rho\,\sigma^2} $$

<VarianceFormula />

---
layout: fig
---

## Averaging is not magic

<VarianceFloor />

---
layout: fig
---

## What max_features does

<MaxFeaturesDraw />

---
layout: fig
---

## The knob: max_features

<ForestFeatures />

---
layout: fig
---

## Two injections of randomness

<ForestDiagram />

---
layout: fig
---

## The boundary stops twitching

<ForestBoundary />

---
layout: fig
---

## Strength against diversity

<ForestCorrelation />

---
layout: fig
---

## More trees never over-fits

<ForestNTrees />

---
layout: section
---

# Boosting

---
layout: fig
---

## Combine many trees differently

<BoostingStages />

---
layout: fig
---

## Forest and boosting attack different errors

<BaggingVsBoosting />

---
layout: fig
---

## Boosting *can* over-fit

<BoostingOverfit />

---
layout: fig
---

## Boosting as an additive model

<AdditiveModel />

---
layout: eq
---

## Boosting is gradient descent in function space

$$ r_{im} \;=\; -\left[\frac{\partial L(y_i, F(x_i))}{\partial F(x_i)}\right]_{F = F_{m-1}} \qquad\qquad F_m \;=\; F_{m-1} + \eta\, h_m $$

<GradientStep />

---
layout: section
---

# Shrinkage

---
layout: fig
---

## Shrinkage

<ShrinkageDemo />

---
layout: fig
---

## The learning rate is a regulariser

<LearningRate />

---
layout: section
---

# XGBoost

---
layout: eq
---

## Regularisation inside the tree objective

$$ \mathcal{L}^{(m)} \;=\; \textcolor{#2b6cb0}{\sum_i \ell\left(y_i,\; F_{m-1}(x_i) + h(x_i)\right)} \;+\; \textcolor{#c53030}{\gamma\,T} \;+\; \textcolor{#6b46c1}{\frac{1}{2}\lambda\sum_{j=1}^{T} w_j^2} $$

<XgbObjective />

---
layout: fig
---

## Splitting candidates

<XgbSplitSearch />

---
layout: eq
---

## Loss simplification for one leaf

<div class="note text-center">expand to second order in the new tree, drop the constant, then add the rows up leaf by leaf</div>

$$ \mathcal{L}^{(m)} \;\simeq\; \sum_{j=1}^{T}\left[\,G_j\,w_j + \frac{1}{2}\left(H_j + \lambda\right)w_j^{2}\,\right] \;+\; \gamma T \qquad G_j = \sum_{i \in I_j} g_i,\quad H_j = \sum_{i \in I_j} h_i $$

<LeafQuadratic />

---
layout: fig
---

## Scoring candidate splits

<XgbLeafScore />

---
layout: fig
---

## Gradient and Hessian

<XgbGh />

---
layout: fig
---

## Summing trees to get the prediction

<XgbLeafPredict />

---
layout: section
---

# LightGBM

---
layout: fig
---

## Bin each feature once

<LgbmBins />

---
layout: fig
---

## Finding the optimal cut in one sweep

<LgbmPrefix />

---
layout: fig
---

## Scan bin edges, not rows

<LgbmBinnedScan />

---
layout: fig
---

## A child's histogram is the parent minus its sibling

<LgbmSubtract />

---
layout: fig
---

## Leaf-wise growth: spend every split where it pays most

<LgbmLeafwise />

---
layout: fig
---

## GOSS: sample the rows that are already fitted

<LgbmGoss />

---
layout: section
---

# CatBoost

---
layout: fig
---

## Categories: the target statistic problem

<CatExample />

---
layout: fig
---

## The encoding leaks the label

<CatLeakWhy />

---
layout: fig
---

## Ordered target statistics: use only what came before

<CatChain />

---
layout: fig
---

## Ordered target statistics: the correlation is gone

<CatOrderedTs />

---
layout: fig
---

## Oblivious trees: one split per level

<CatOblivious />

---
layout: fig
---

## XGBoost, LightGBM, CatBoost

<GbmCompare />
