---
theme: default
title: "Session 8: Model Order Selection"
info: |
  Advanced Machine Learning · MSc DSBA · 2026 · Paul Dubois
  Interactive companion to Course08/slides.pptx.
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
favicon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23fff'/%3E%3Cpath d='M4 8 C9 26 13 26 16 22 C19 18 22 18 28 24' fill='none' stroke='%23c53030' stroke-width='2.4'/%3E%3Cpath d='M4 6 C10 20 18 26 28 28' fill='none' stroke='%232b6cb0' stroke-width='2.4'/%3E%3C/svg%3E"
layout: cover
---

# Session 8<br>Model Order Selection

Advanced Machine Learning · MSc DSBA · 2026

Paul Dubois

<div class="note mt-8">Week 7 lecture</div>

---
layout: fig
---

## Kernel of SVM

<SvmKnob knob="gamma" />

---
layout: fig
---

## Kernel of SVM

<SvmKnob knob="C" />

---
layout: fig
---

## Naive Bayes, LDA, QDA

<RigidFlexible />

---
layout: fig
---

## Ridge regression

<RidgeKnob />

---
layout: fig
---

## k-means

<KmeansKnob />

---
layout: fig
---

## DBSCAN

<DbscanKnob />

---
layout: fig
---

## Non-negative Matrix Factorization

<NmfRank />

---
layout: fig
---

## Gaussian mixture

<GmmK />

---
layout: eq
---

## Classification and regression

<div class="note" style="text-align: center">What goes wrong at each end.</div>

<table class="knobs">
<tr><th>The knob</th><th class="bad">Too small</th><th class="bad">Too large</th></tr>
<tr><td><b><i>α</i> in naive Bayes</b></td><td>an unseen value zeroes the whole product</td><td>all values look about equally likely</td></tr>
<tr><td><b>NB / LDA / QDA</b></td><td>an assumption more data cannot repair</td><td>a boundary that follows this sample</td></tr>
<tr><td><b class="hl-blue"><i>M</i>, the polynomial order</b></td><td>the curve cannot bend to the data</td><td>it threads every point, noise included</td></tr>
<tr><td><b class="hl-blue"><i>λ</i> in ridge, lasso</b></td><td>coefficients blow up on 10 points</td><td>everything shrunk to zero, pattern lost</td></tr>
<tr><td><b class="hl-blue"><i>δ</i> in a robust loss</b></td><td>every residual is treated as an outlier</td><td>least squares: one outlier tilts the fit</td></tr>
<tr><td><b class="hl-gold"><i>C</i> in a soft margin</b></td><td>slack is free, the margin ignores the points</td><td>no slack: the boundary wraps noise</td></tr>
<tr><td><b class="hl-gold"><i>γ</i> in an RBF kernel</b></td><td>the boundary is nearly straight</td><td>one island around each point</td></tr>
<tr><td><b class="hl-gold"><i>ε</i>, the SVR tube</b></td><td>nearly every point is a support vector</td><td>the tube swallows the signal</td></tr>
</table>

---
layout: eq
---

## Clustering, mixtures, factorization

<div class="note" style="text-align: center">What goes wrong at each end.</div>

<table class="knobs">
<tr><th>The knob</th><th class="bad">Too small</th><th class="bad">Too large</th></tr>
<tr><td><b><i>q</i> in PCA</b></td><td>directions carrying real signal are dropped</td><td>the directions kept are mostly noise</td></tr>
<tr><td><b class="hl-green"><i>K</i> in <i>k</i>-means</b></td><td>two populations merged into one cluster</td><td>a single population cut into pieces</td></tr>
<tr><td><b class="hl-green"><i>ε</i> in DBSCAN</b></td><td>almost every point is labelled noise</td><td>every cluster merged, nothing is noise</td></tr>
<tr><td><b class="hl-green">MinPts in DBSCAN</b></td><td>noise is promoted into clusters</td><td>real clusters are called noise</td></tr>
<tr><td><b class="hl-green">the cut of a dendrogram</b></td><td>one leaf per point</td><td>everything in a single branch</td></tr>
<tr><td><b class="hl-purple"><i>r</i> in NMF</b></td><td>distinct parts mixed into one component</td><td>components fitting the noise of the matrix</td></tr>
<tr><td><b class="hl-red"><i>K</i> in a mixture</b></td><td>one bell covering two populations</td><td>a component glued to a single point</td></tr>
<tr><td><b class="hl-red">the covariance type</b></td><td>spherical cannot follow the shape</td><td>full costs <i>Kd</i>(<i>d</i> + 1)/2 numbers</td></tr>
</table>

---
layout: eq
---

## Choosing hyper-parameter values

<div class="big">And evaluate the quality.</div>

<div class="cards4">
<div class="card" style="border-color: var(--blue)"><div class="h hl-blue">hold out</div><div>score the model where<br>it was not fitted</div></div>
<div class="card" style="border-color: var(--gold)"><div class="h hl-gold">cross-validate</div><div>use every point for<br>both jobs, in turn</div></div>
<div class="card" style="border-color: var(--purple)"><div class="h hl-purple">search</div><div>grids, random draws,<br>and guided searches</div></div>
<div class="card" style="border-color: var(--green)"><div class="h hl-green">penalise</div><div>AIC, BIC: the fit minus<br>a price for complexity</div></div>
</div>

<div class="note mt-4" style="text-align: center">How to estimate error on data that the model has never seen.</div>

---
layout: eq
---

## An unfitted parameter

<div class="chain">
<div class="box3" style="border-color: var(--purple)"><div class="h hl-purple">order</div><div><i>M</i>: <i>K</i>, <i>r</i>, <i>ε</i>, <i>γ</i>, depth, …</div></div>
<div class="arrow">→</div>
<div class="box3" style="border-color: var(--blue)"><div class="h hl-blue">parameters</div><div><i>θ</i>: <i>w</i>, <i>μ<sub>k</sub></i>, <i>W</i>, <i>H</i>, …</div></div>
<div class="arrow">→</div>
<div class="box3" style="border-color: var(--green)"><div class="h hl-green">fitted model</div><div>model ready to use</div></div>
<div class="under" style="color: var(--red)">the loss cannot choose it</div><div></div>
<div class="under note">fitted by minimising a loss</div><div></div><div></div>
</div>

<div class="note mt-12" style="text-align: center">Which model generalises best to unseen data?</div>

---
layout: fig
---

## Classic example

<CurveSetup />

---
layout: eq
---

## Fitting a polynomial

<div class="steps2">

$f(x, w) = w_0 + w_1 x + \cdots + w_M x^M$

<p class="note"><i>M</i> is the order of the polynomial; <i>w</i> are its coefficients (to be learnt)</p>

$e(w) = \sum_i \rho\big(f(x_i, w) - t_i\big)$

<p class="note">the error function over the <i>N</i> observed points</p>

<p class="hl-green-t"><Tex formula="\rho(u) = u^2" /> &nbsp;&nbsp; so <Tex formula="e" /> is quadratic in <Tex formula="w" /></p>

<p class="note">a closed form for <Tex formula="w^\star" /> exists for every value of <Tex formula="M" /></p>

<p class="hl-red-t"><Tex formula="e(w^\star)" /> does not help choosing <Tex formula="M" /></p>

<p class="note"><Tex formula="e(w^\star)" /> can only go down as <Tex formula="M" /> grows</p>

</div>

<div class="box purple mt-4">Two nested problems: find <i>w</i> given <i>M</i> and find <i>M</i></div>

---
layout: fig
---

## Effect of model order

<PolyOrder />

---
layout: fig
---

## Training error against test error

<TrainTest />

---
layout: fig
---

## Inside the over-fitted model

<Coefficients />

---
layout: fig
---

## Modern solution

<MoreData />

---
layout: eq
---

## Vocabulary

<table class="vocab">
<tr><th></th><th>What happens</th><th>What is measured</th><th>Why</th></tr>
<tr><td><b class="hl-red">underfitting</b></td><td>cannot represent the pattern</td><td>train high, test high</td><td class="hl-red"><i>M</i> too small</td></tr>
<tr><td><b class="hl-green">"sweet spot"</b></td><td>the pattern and not the noise</td><td>train low, test lowest</td><td class="hl-green"><i>M</i> about right</td></tr>
<tr><td><b class="hl-red">overfitting</b></td><td>this sample, noise included</td><td>train tiny, test high</td><td class="hl-red"><i>M</i> too large</td></tr>
</table>

<div class="rows mt-8">
<div class="k hl-purple">generalisation</div><div>how the model behaves on data drawn from the same law, but never seen</div>
<div class="k hl-purple">model selection</div><div>choosing <i>M</i> so that the generalisation is as good as it can be</div>
</div>

---
layout: eq
---

## True risk

<TrueRisk />

<h4 class="hl-red-t mt-6">Problem:</h4>

- $p(x, t)$ is exactly what we do not know
- so $R(f)$ can never be computed

<div class="note mt-2" style="text-align: center">Averaging the loss over more and more unseen points converges to <Tex formula="R(f)" />.</div>

---
layout: fig
---

## Empirical risk

<div class="er">
<div>

<p class="hl-blue-t"><Tex formula="R_N(f) = \frac1N \sum_i \rho(f(x_i), t_i)" /></p>
<p class="note">Average over the <i>N</i> test points</p>
<p class="hl-green-t"><Tex formula="E[R_N(f)] = R(f)" />, &nbsp; <Tex formula="R_N(f) \to R(f)" /> as <Tex formula="N \to \infty" /></p>
<p class="note">Unbiased</p>
<p class="hl-red-t">For <Tex formula="\hat f" /> fitted on the same <Tex formula="N" /> points, <Tex formula="R_N(\hat f)" /> is biased (too optimistic)</p>
<p class="note"><Tex formula="R_N(\hat f)" /> is the "training error"</p>
<p class="hl-green-t">Score <Tex formula="\hat f" /> where it was not fitted</p>
<p class="hl-purple-t">When <i>N</i> is small, the cost of holding out is high.</p>

</div>
<RiskConverge />
</div>

---
layout: fig
---

## Train vs Test curves

<RiskPicture />

---
layout: fig
---

## Bias and variance

<BiasVariance />

---
layout: fig
---

## Choosing model on test set

<SelectOnTest />

---
layout: fig
---

## Hold out, select, report

<HoldoutSplit />

---
layout: fig
---

## K-fold

<KFold />

---
layout: fig
---

## Choosing the number of folds

<LooVsK />

---
layout: fig
---

## Uncontaminated split

<CvVariants />

---
layout: fig
---

## Model selection costs

<CvCost />

---
layout: section
---

# Hyper-parameter optimization

---
layout: eq
---

## Why this search is hard

<table class="hard">
<tr><td class="hl-red"><b>expensive</b></td><td>one trial is a fit (or a cross-validation loop)</td></tr>
<tr><td class="hl-gold"><b>noisy</b></td><td>redrawing the training samples can change the score</td></tr>
<tr><td class="hl-blue"><b>no gradient</b></td><td>descent is not possible</td></tr>
<tr><td class="hl-purple"><b>not convex</b></td><td>landscape hard to explore</td></tr>
<tr><td class="hl-gold"><b>mixed</b></td><td>continuous, integer and categorical together</td></tr>
<tr><td class="hl-green"><b>conditional</b></td><td>e.g.: hyper-parameters depend on the choice of kernel</td></tr>
</table>

<div class="note mt-4" style="text-align: center">The best methods spend few evaluations, and where they are worth.</div>

---
layout: fig
---

## Search on a log scale

<LogScale />

---
layout: fig
---

## The landscape with one knob

<Landscape1d />

---
layout: fig
---

## The landscape with two knobs

<Landscape2d />

---
layout: fig
---

## Grid, random, Bayesian

<SearchCompare />

---
layout: fig
---

## A cheap stand-in for an expensive score

<BoSurrogate />

---
layout: fig
---

## Explore or exploit

<BoAcquisition />

---
layout: fig
---

## The loop

<BoLoop />

<p class="note" style="text-align: center; margin: 0">Start with five to ten random trials: with no data the surrogate has nothing to model.</p>

---
layout: eq
---

## In practice: Optuna

<div class="note" style="text-align: center">In practice: the search space is Python</div>

<div class="optuna">

```python
def objective(trial):
    depth = trial.suggest_int("depth", 3, 12)
    lr    = trial.suggest_float("lr", 1e-4, 0.3, log=True)

    model = XGBClassifier(max_depth=depth, learning_rate=lr)
    return cross_val_score(model, X, y, cv=5,
                           scoring="roc_auc").mean()

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
```

<div class="ann">
<p class="hl-green-t">← log for learning rate</p>
<p class="hl-red-t">← one trial is a whole<br>cross-validation (expensive)</p>
</div>
</div>

<div class="note mt-4" style="text-align: center">The space is defined while the trial runs, so a knob can depend on another one.</div>

---
layout: fig
---

## Reading the history

<OptunaHistory />

---
layout: fig
---

## Pruning

<Pruning />

---
layout: section
---

# Information criteria

---
layout: eq
---

## Fit minus penalty

<div class="note" style="text-align: center">Keep the likelihood, charge for the parameters</div>

<div class="crit">criterion &nbsp; = &nbsp; fit &nbsp; − &nbsp; penalty</div>

<div class="critlab">
<div class="hl-blue-t">↑ <Tex formula="\ln p(x \mid \hat\theta_{ML})" /></div>
<div class="hl-purple-t">↑ a function of <Tex formula="M_j" /> and <Tex formula="N" /></div>
</div>

<div class="cols mt-6">
<div>

#### Idea

- Maximised likelihood is optimistic
- Optimism grows with the number of free parameters

</div>
<div>

<h4 style="color: var(--green)">Benefits</h4>

- No folds / refits
- Single number per candidate model

</div>
</div>

<div class="note mt-4" style="text-align: center">

$M_j$ is the number of free parameters; $N$ is the number of data points.

</div>

---
layout: eq
---

## Akaike's criterion

$$
\mathrm{AIC}(j) \;=\; \ln p(x \mid \hat\theta_{ML}) \;-\; \underbrace{M_j}_{\text{one unit per parameter}}
$$

<div class="cols mt-6">
<div>

#### Origins

- Estimates the expected Kullback–Leibler distance to the truth
- Models the optimism of $\ln p(x \mid \hat\theta)$ as $\approx M_j$
- Asymptotic, and assumes the maximum-likelihood estimator

</div>
<div>

<h4 style="color: var(--gold)">Remarks</h4>

- Aims at the best prediction, not at the true model
- Penalty does not grow with $N$
- Keeps choosing richer models as $N \to \infty$

</div>
</div>

<div class="note mt-4" style="text-align: center">

Often written to be minimised: $-2 \ln p(x \mid \hat\theta) + 2 M_j$.

</div>

---
layout: eq
---

## The Bayesian criterion

<div class="note" style="text-align: center">also called "minimum description length"</div>

$$
\mathrm{BIC}(j) \;=\; \ln p(x \mid \hat\theta_{ML}) \;-\; \underbrace{\tfrac12 M_j \log N}_{\text{grows with } N}
$$

<div class="cols mt-6">
<div>

#### Origins

- Laplace approximation of the model's evidence
- $\log p(\mathcal D \mid \mathcal M) \approx \mathrm{BIC} + O(1)$

</div>
<div>

<h4 style="color: var(--green)">Remarks</h4>

- Aims at the true model, hoping it is among the candidates
- Heavier than AIC for $N > 8$

</div>
</div>

<div class="note mt-4" style="text-align: center">

As a minimiser: $-2 \ln p(x \mid \hat\theta) + M_j \ln N$.

</div>

---
layout: eq
---

## Two conventions

<div class="note" style="text-align: center">scikit-learn's <code>aic()</code> and <code>bic()</code> return the minimise form</div>

<table class="conv">
<tr><th></th><th class="hl-green">maximise</th><th class="hl-blue">minimise</th></tr>
<tr><td class="hl-gold"><b>AIC</b></td><td>

$\ln p(x \mid \hat\theta) - M$

</td><td>

$-2 \ln p(x \mid \hat\theta) + 2M$

</td></tr>
<tr><td class="hl-green"><b>BIC</b></td><td>

$\ln p(x \mid \hat\theta) - \tfrac12 M \log N$

</td><td>

$-2 \ln p(x \mid \hat\theta) + M \log N$

</td></tr>
</table>

<div class="note mt-8" style="text-align: center">A difference of 10 (in the minimise form) is decisive; a difference of 2 is not.</div>

---
layout: fig
---

## AIC vs BIC

<AicBic />

---
layout: eq
---

## Practical guidelines

<div class="note" style="text-align: center">No clear winner, but the differences are predictable</div>

<table class="guide">
<tr><td class="hl-gold"><b>BIC penalises harder</b></td><td>on very big samples it may pick a model that is too simple</td></tr>
<tr><td class="hl-green"><b>BIC is consistent</b></td><td>if the true model is among the candidates, BIC finds it as <i>N</i> grows</td></tr>
<tr><td class="hl-blue"><b>AIC is usually preferable otherwise</b></td><td>when no candidate is true</td></tr>
<tr><td class="hl-purple"><b>AIC aims at prediction</b></td><td>it tends to choose models that are too complex as <i>N</i> → ∞</td></tr>
<tr><td class="hl-red"><b>both need <i>N</i> large against <i>d</i></b></td><td>typically <Tex formula="d \ll \sqrt N" />; otherwise use the corrected version</td></tr>
</table>

<div class="note mt-4" style="text-align: center">A practical habit: report both.</div>

---
layout: fig
---

## A correction for small samples

<div class="formula">

$$
\mathrm{mAIC}(j) \;=\; \ln p(x \mid \hat\theta_{ML}) \;-\; M_j \;-\; \frac{M_j (M_j + 1)}{N - M_j - 1}
$$

</div>

<Aicc />

<p class="note" style="text-align: center; margin: 0">Also known as AICc.</p>

---
layout: eq
---

## How each one is chosen

<table class="vocab">
<tr><th>The knob</th><th>Usual method</th><th>Why</th></tr>
<tr><td><b class="hl-blue"><i>λ</i> in ridge or lasso</b></td><td>cross-validation</td><td class="note">cheap, can fit every <i>λ</i> at once</td></tr>
<tr><td><b class="hl-gold"><i>C</i>, <i>γ</i> in an SVM</b></td><td>grid or random search, with CV</td><td class="note">no likelihood, so no information criterion</td></tr>
<tr><td><b class="hl-green"><i>K</i> in <i>k</i>-means<br><i>ε</i>, MinPts in DBSCAN</b></td><td>elbow, silhouette, stability</td><td class="note">no likelihood, and no held-out label</td></tr>
<tr><td><b class="hl-purple"><i>r</i> in NMF</b></td><td>held-out entries</td><td class="note">cross-validation on a mask</td></tr>
<tr><td><b class="hl-red"><i>K</i> in a Gaussian mixture</b></td><td>BIC / held-out likelihood</td><td class="note">real likelihood, so criteria apply</td></tr>
</table>

<div class="box mt-6" style="border-color: var(--ink)">A likelihood allows AIC and BIC.</div>

---
layout: eq
---

## Which tool, when

<table class="vocab">
<tr><th>Method</th><th>Needs</th><th>Cost</th><th>Reach for it when</th></tr>
<tr><td><b>cross-validation</b></td><td>always applicable</td><td><i>K</i> fits each</td><td class="note">by default</td></tr>
<tr><td><b class="hl-green">BIC</b></td><td>likelihood &amp; parameter count</td><td>free</td><td class="note">true model in the list</td></tr>
<tr><td><b class="hl-gold">AIC</b></td><td>likelihood &amp; parameter count</td><td>free</td><td class="note">good prediction</td></tr>
<tr><td><b class="hl-purple">Guided search</b></td><td>a few dozen fits</td><td>sequential</td><td class="note">several knobs, useful if a fit takes time</td></tr>
<tr><td><b class="hl-blue">Hold-out set</b></td><td>a lot of data</td><td>part of the data</td><td class="note">deep learning</td></tr>
</table>

<div class="note mt-6" style="text-align: center">All estimate the generalisation, each in a different way.</div>
