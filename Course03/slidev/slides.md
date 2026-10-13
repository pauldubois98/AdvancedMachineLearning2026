---
theme: default
title: "Session 3: Support Vector Machines"
info: |
  Advanced Machine Learning · MSc DSBA · 2026 · Paul Dubois
  Interactive companion to Course03/slides.pptx.
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
favicon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23fff'/%3E%3Cpath d='M4 26 L28 6' stroke='%231b1b1b' stroke-width='2.5'/%3E%3Cpath d='M4 19 L21 2 M11 30 L28 13' stroke='%239aa0a6' stroke-width='1.6' stroke-dasharray='3 3'/%3E%3Ccircle cx='9' cy='9' r='3' fill='%232b6cb0'/%3E%3Ccircle cx='23' cy='23' r='3' fill='%23c53030'/%3E%3C/svg%3E"
layout: cover
---

# Session 3<br>Support Vector Machines

Advanced Machine Learning · MSc DSBA · 2026

Paul Dubois

<div class="note mt-8">Week 3 lecture · every figure here is live: move the sliders</div>

---
layout: section
---

# The linear SVM

---
layout: fig
---

## Separating classes with a line

<LinearScore />

---
layout: fig
---

## Which line?

<WhichLine />

---
layout: fig
---

## The widest street

<WidestStreet />

---
layout: eq
---

## Width of the street

$$ d(x_i, H) \;=\; \frac{y_i\,(w^{T}x_i + b)}{\|w\|} \;=\; \frac{|f(x_i)|}{\|w\|} $$

<div class="text-center mt-6 text-[var(--green)] text-lg">

$y_i f(x_i) > 0$

</div>

<div class="note text-center">if correctly classified</div>

<div class="note text-center mt-8">the margin of the classifier is twice the smallest of these</div>

---
layout: fig
---

## Fixing the scale

<CanonicalScale />

---
layout: eq
---

## Optimization problem

<div class="note text-center">widen the street while keeping points out of it</div>

$$ \min_{w,\,b}\ \ \frac{1}{2}\|w\|^2 \qquad \mathrm{subject\ to}\qquad y_i\,(w^{T}x_i + b) \geq 1, \quad i = 1,\dots,n $$

<div class="cols mt-6 text-center">
<div class="text-[var(--green)]">

$\|w\|$ small $\Leftrightarrow$ street wide

</div>
<div class="text-[var(--blue)]">

one constraint per training point

</div>
</div>

<div class="text-center mt-8">quadratic objective with linear constraints</div>

---
layout: eq
---

## Lagrangian to α ≥ 0 constraints

<div class="note text-center">an inequality can be made into an equality</div>

$$ g_i(w, b) = y_i(w^{T}x_i + b) - 1 \;\geq\; 0 \qquad \Longleftrightarrow \qquad g_i(w, b) - s_i^2 = 0, \quad s_i \in \mathbb{R} $$

$$ \tilde{L}(w, b, \alpha, s) = \frac{1}{2}\|w\|^2 - \sum_i \alpha_i\left[g_i(w,b) - s_i^2\right] $$

<div class="note text-center">

$\alpha_i$ are free in sign

</div>

<div class="cols mt-4 text-center">
<div>

<span class="text-[var(--green)]">$\dfrac{\partial \tilde{L}}{\partial s_i} = 2\alpha_i s_i = 0$</span>

$\alpha_i = 0$ &nbsp;or&nbsp; $s_i = 0$

<span class="note">complementary slackness: zero multiplier, or a point on the margin</span>

</div>
<div>

<span class="text-[var(--blue)]">$\dfrac{\partial^2 \tilde{L}}{\partial s_i^2} = 2\alpha_i \geq 0$</span>

$\alpha_i \geq 0$

<span class="note">$s_i = 0$ has to be a minimum, not a maximum</span>

</div>
</div>

---
layout: eq
---

## Expressing constraint in two ways

<div class="text-center">

the constraint on point $i$: &nbsp; $g_i(w,b) = y_i(w^{T}x_i + b) - 1 \;\geq\; 0$

</div>

<div class="cols mt-5 text-center">
<div>

<h4 class="text-[var(--gold)]">write it as an equality</h4>

<span class="text-[var(--gold)]">$g_i - s_i^2 = 0, \quad s_i \in \mathbb{R}$</span>

<span class="note">allowed when some $s_i$ exists</span>

</div>
<div>

<h4 class="text-[var(--green)]">or charge for breaking it</h4>

<span class="text-[var(--green)]">$\max_{\alpha_i \geq 0}\ \left(-\alpha_i g_i\right)$</span>

<span class="note">allowed when the charge is zero</span>

</div>
</div>

<div class="mt-6 w-3/4 mx-auto narrow">

|  | is there an $s_i$? | what it costs |
| --- | --- | --- |
| <span class="text-[var(--green)]">$g_i \geq 0$</span> | yes | <span class="text-[var(--green)]">$0$</span> |
| <span class="text-[var(--red)]">$g_i < 0$</span> | none exists | <span class="text-[var(--red)]">$+\infty$</span> |

</div>

<div class="text-center mt-4">

The problem becomes $\min_{w,b}\ \max_{\alpha \geq 0}\ L(w,b,\alpha)$.

</div>

---
layout: eq
---

## Dual formulation

<div class="box-blue">
  <div class="box-head text-[var(--blue)]">PRIMAL <span class="note">d + 1 unknowns (w, b)</span></div>

  $$ \min_{w,b}\ \tfrac{1}{2}\|w\|^2 \quad \mathrm{s.t.}\quad y_i(w^{T}x_i + b) \geq 1 $$
</div>

$$ L(w, b, \alpha) = \frac{1}{2}\|w\|^2 - \sum_i \alpha_i\left[y_i(w^{T}x_i + b) - 1\right] $$

<div class="text-center text-[var(--gold)]">

$\partial L/\partial w = 0 \;\Rightarrow\; w = \sum_i \alpha_i y_i x_i \qquad \partial L/\partial b = 0 \;\Rightarrow\; \sum_i \alpha_i y_i = 0$

</div>

<div class="note text-center">

put these back into $L$: $w$ and $b$ are gone

</div>

<div class="box-green">
  <div class="box-head text-[var(--green)]">DUAL <span class="note">n unknowns (α)</span></div>

  $$ \max_{\alpha}\ \sum_i \alpha_i - \frac{1}{2}\sum_{i,j}\alpha_i\alpha_j y_i y_j\, x_i^{T}x_j \quad \mathrm{s.t.}\quad \alpha_i \geq 0, \ \sum_i \alpha_i y_i = 0 $$
</div>

<style>
.box-blue, .box-green { border-radius: 0.5rem; padding: 0.1rem 1rem 0.4rem; margin: 0.3rem 0; }
.box-blue { border: 1.8px solid var(--blue); background: #f2f6fb; }
.box-green { border: 1.8px solid var(--green); background: #f1f9f1; }
.box-head { font-weight: 700; font-size: 0.8rem; letter-spacing: 0.04em; padding-top: 0.35rem; }
.box-blue .katex-display, .box-green .katex-display { margin: 0.1rem 0 0; }
</style>

---
layout: fig
---

## The Lagrangian has a saddle

<SaddleExplorer />

---
layout: eq
---

## Reading the primal back off the dual

<div class="note text-center">

from $\hat\alpha$, everything else follows

</div>

<div class="grid grid-cols-2 gap-10 mt-4 items-center">
<div class="text-center leading-loose">

<span class="text-[var(--green)]">$\hat{w} = \sum_i \hat\alpha_i y_i x_i$</span>

<span class="text-[var(--blue)]">$\hat\alpha_i\left[y_i(\hat{w}^{T}x_i + \hat{b}) - 1\right] = 0$</span>

<span class="text-[var(--purple)]">$\hat{b} = y_i - \hat{w}^{T}x_i$ for any $\hat\alpha_i > 0$</span>

</div>
<div class="text-center border-l border-[var(--grid)] pl-8">

**but $\hat{w}$ is never built**

<span class="text-[var(--green)]">$f(x) = \sum_{SV} \hat\alpha_i y_i\, \langle x_i,\, x\rangle + \hat{b}$</span>

<span class="note">the prediction asks only for inner products of $x$ with the support vectors</span>

</div>
</div>

<div class="mt-5 w-5/6 mx-auto narrow">

| storing | cost | when it breaks |
| --- | --- | --- |
| <span class="text-[var(--gold)]">$\hat{w}$</span> | $d$ numbers | <span class="note">hopeless if $x$ lives in a huge space</span> |
| <span class="text-[var(--green)]">the $\hat\alpha_i$</span> | one per support vector | <span class="note">the sum stays finite</span> |

</div>

<div class="text-center mt-3 text-[var(--red)]">

This is what kernels exploit: replace $\langle x_i, x\rangle$ by $k(x_i, x)$

</div>

---
layout: fig
---

## Only a few points matter

<SupportVectorsDrop />

---
layout: section
---

# The soft margin

---
layout: fig
---

## When no line works

<GapExplorer />

---
layout: fig
---

## Slack

<SlackExplorer />

---
layout: eq
---

## Soft-margin problem

$$ \min_{w,\,b,\,\xi}\ \ \underbrace{\frac{1}{2}\|w\|^2}_{\textcolor{#00ab0e}{\text{a wide street}}} \;+\; \underbrace{C\sum_{i=1}^{n}\xi_i}_{\textcolor{#c53030}{\text{few and small violations}}} $$

<div class="text-center mt-3">

subject to $\quad y_i(w^{T}x_i + b) \geq 1 - \xi_i, \quad \xi_i \geq 0$

</div>

<div class="note text-center">

$C$ sets the exchange rate between the two

</div>

<hr class="my-4 border-[var(--grid)] w-2/3 mx-auto" />

<div class="text-center text-[var(--blue)]">

$$ \max_{\alpha}\ \sum_i \alpha_i - \frac{1}{2}\sum_{i,j}\alpha_i\alpha_j y_i y_j\,x_i^{T}x_j \qquad 0 \leq \alpha_i \leq C, \ \ \sum_i \alpha_i y_i = 0 $$

</div>

<div class="note text-center">

the same dual as before, with the multipliers capped at $C$

</div>

---
layout: fig
---

## C: how much misbehaviour is allowed?

<CExplorer />

---
layout: eq
---

## The loss

$$ \min_{w,b}\ \ \underbrace{\frac{1}{2}\|w\|^2}_{\textcolor{#00ab0e}{\text{make the street as WIDE as possible}}} \;+\; \underbrace{C\sum_i \max\left(0,\, 1 - y_i(w^{T}x_i + b)\right)}_{\textcolor{#c53030}{\text{pay } C \text{ for every point inside it, or on the wrong side}}} $$

<div class="note text-center mt-8">

the margin is the penalty, the hinge is the loss; one more regularised fit

</div>

---
layout: fig
---

## Hinge, log loss, squares

<HingeExplorer />

---
layout: section
---

# Kernels

---
layout: fig
---

## The kernel trick

<KernelLift />

---
layout: fig
---

## XOR

<XorLift />

---
layout: eq
---

## Why the trick works

<div class="note text-center">Embedded problem</div>

$$ f(x) = w^{T}\Phi(x) + b = \sum_{SV} \alpha_i y_i\, \Phi(x_i)^{T}\Phi(x) + b $$

<div class="text-center text-[var(--red)]">

$\Phi$ only ever appears inside an inner product

</div>

$$ \textcolor{#00ab0e}{k(x, x') \;=\; \langle \Phi(x),\, \Phi(x')\rangle} $$

<div class="text-center mt-2">so compute the similarity directly, never build Φ</div>

<div class="cols mt-4 text-center note">
<div>

implicit space can be infinite

</div>
<div>

cost follows $n$, not the dimension

</div>
</div>

---
layout: fig
---

## RBF kernel

<RbfSimilarity />

---
layout: eq
---

## Kernel requirements

<div class="w-4/5 mx-auto">

**1. symmetric** &nbsp;&nbsp; $k(x, x') = k(x', x)$

**2. positive semi-definite** &nbsp;&nbsp; $\sum_i \sum_j \alpha_i \alpha_j\, k(x_i, x_j) \geq 0$

</div>

<div class="text-center text-[var(--green)] mt-6">

So that the dual stays convex (hence the solution stays unique)

</div>

<div class="note text-center mt-4">sums and products of kernels are kernels</div>

---
layout: eq
---

## Typical kernels

| kernel | $k(x, x')$ | knobs | reach for it when |
| --- | --- | --- | --- |
| <span class="text-[var(--blue)]">linear</span> | $x^{T}x'$ | C only | $d$ is large, $n$ is huge, text / sparse features |
| <span class="text-[var(--purple)]">polynomial</span> | $(\gamma\, x^{T}x' + r)^{p}$ | C, $\gamma$, r, p | want explicit feature interactions |
| <span class="text-[var(--green)]">RBF / Gaussian</span> | $\exp(-\gamma\|x - x'\|^2)$ | C, $\gamma$ | the default |
| <span class="text-[var(--gold)]">sigmoid</span> | $\tanh(\gamma\, x^{T}x' + r)$ | C, $\gamma$, r | not always a valid kernel |

<div class="text-center mt-6">Kernels can be written for strings, graphs or sequences.</div>

---
layout: fig
---

## Kernels in practice

<KernelExplorer />

---
layout: fig
---

## Scale features first

<ScalingDemo />

---
layout: fig
---

## Choosing C and γ

<CvHeatmap />

---
layout: eq
---

## Dual problem with a kernel

<div class="note text-center">

replace every $x_i^{T}x_j$ by $k(x_i, x_j)$, and nothing else changes

</div>

<div class="text-[var(--blue)]">

$$ \max_{\alpha}\ \sum_i \alpha_i - \frac{1}{2}\sum_{i,j}\alpha_i\alpha_j y_i y_j\, k(x_i, x_j) \qquad 0 \leq \alpha_i \leq C, \ \ \sum_i \alpha_i y_i = 0 $$

</div>

<div class="text-[var(--green)] mt-4">

$$ f(x) \;=\; \sum_{SV} \alpha_i y_i\, k(x_i, x) \;+\; b $$

</div>

<div class="text-center mt-4">Prediction is a weighted vote of the support vectors.</div>

---
layout: eq
---

## What kernels cost

<div class="cols">
<div>

#### <span class="text-[var(--green)]">Gain</span>

- curved boundaries at a linear price
- Φ never has to be written down
- any data with a similarity: text, graphs, time series

</div>
<div class="border-l border-[var(--grid)] pl-10">

#### <span class="text-[var(--red)]">Costs</span>

- the support vectors must be kept
- no principled way to pick the kernel
- the Gram matrix is n × n: only applies to small/moderate datasets

</div>
</div>

<div class="note text-center mt-8">"instance-based method": stores data (not parameters)</div>

---
layout: fig
---

## SVMs scaling

<GramCost />

---
layout: fig
---

## More than two classes

<MulticlassDemo />

---
layout: section
---

# Beyond classification

---
layout: fig
---

## The same idea, for regression

<SvrTube />

---
layout: eq
---

## Regression in the dual

<div class="note text-center">a point can miss the tube from above or from below</div>

$$ \min\ \frac{1}{2}\|w\|^2 + C\sum_i \left(\xi_i + \xi_i^{*}\right) \qquad \mathrm{s.t.}\qquad |y_i - f(x_i)| \leq \varepsilon + \xi_i^{(*)} $$

<div class="note text-center">

two slacks, so two multipliers: $\alpha_i$ above and $\alpha_i^{*}$ below

</div>

<div class="text-[var(--green)]">

$$ f(x) = \sum_i \left(\hat\alpha_i - \hat\alpha_i^{*}\right) k(x_i, x) + \hat{b} $$

</div>

<div class="w-4/5 mx-auto mt-4 narrow">

| where the point is | the multipliers | role |
| --- | --- | --- |
| <span class="text-[var(--green)]">inside the tube</span> | $\hat\alpha_i = \hat\alpha_i^{*} = 0$ | not a support vector |
| <span class="text-[var(--gold)]">on the tube</span> | $0 < \hat\alpha_i^{(*)} < C$ | used to recover $\hat{b}$ |
| <span class="text-[var(--red)]">outside it</span> | $\hat\alpha_i^{(*)} = C$ | bounded |

</div>

<div class="text-center text-[var(--red)] mt-4">

the same machinery as the classifier (kernels, soft-margin, etc...)

</div>

---
layout: fig
---

## The width of the tube

<SvrEpsilon />

---
layout: fig
---

## Recap

<RecapMap />

---
layout: center
class: text-center
---

## Next week

Density-based and hierarchical clustering:<br>
learning without labels.
