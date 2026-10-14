---
theme: default
title: "Session 4: Clustering"
info: |
  Advanced Machine Learning · MSc DSBA · 2026 · Paul Dubois
  Interactive companion to Course04/slides.pptx.
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
favicon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23fff'/%3E%3Ccircle cx='9' cy='10' r='2.6' fill='%232b6cb0'/%3E%3Ccircle cx='14' cy='7' r='2.6' fill='%232b6cb0'/%3E%3Ccircle cx='23' cy='13' r='2.6' fill='%23c53030'/%3E%3Ccircle cx='24' cy='20' r='2.6' fill='%23c53030'/%3E%3Ccircle cx='11' cy='23' r='2.6' fill='%2300ab0e'/%3E%3Ccircle cx='17' cy='25' r='2.6' fill='%2300ab0e'/%3E%3C/svg%3E"
layout: cover
---

# Session 4<br>Clustering

Advanced Machine Learning · MSc DSBA · 2026

Paul Dubois

<div class="note mt-8">Week 4 lecture</div>

---
layout: section
---

# What is clustering?

---
layout: fig
---

## No labels

<ClusterSetting />

---
layout: fig
---

## Two ways to simplify a table

<ClusteringVsDimred />

---
layout: eq
---

## Use cases

<div class="apps">

| | | input | what a cluster becomes |
|---|---|---|---|
| <UseCaseIcon kind="market" /> | <em class="hl-blue">market segmentation</em> | purchase history | segments to target |
| <UseCaseIcon kind="image" /> | <em class="hl-green">image segmentation</em> | pixels, voxels | blood, muscle, tumour |
| <UseCaseIcon kind="text" /> | <em class="hl-purple">text mining</em> | e-mails, documents | folders, themes |
| <UseCaseIcon kind="anomaly" /> | <em class="hl-gold">anomaly detection</em> | transactions, logs | what fits nowhere |

<div class="note mt-4">Same algorithm gives four different ideas of what a group is.</div>

</div>

<style>
.apps { font-size: 1.05rem; padding-top: 1rem; }
.apps td { padding: 0.55rem 0.9rem 0.55rem 0; vertical-align: middle; }
.apps td:first-child { width: 1%; padding-right: 1.4rem; }
</style>

---
layout: fig
---

## What a cluster can mean

<ClusterTypes />

---
layout: fig
---

## Partitional or hierarchical

<PartitionalVsHierarchical />

---
layout: fig
---

## Exclusive or overlapping

<ExclusiveVsOverlapping />

---
layout: fig
---

## Hard or fuzzy

<HardVsFuzzy />

---
layout: fig
---

## Complete or partial

<CompleteVsPartial />

---
layout: fig
---

## Homogeneous or heterogeneous

<HomogeneousVsHeterogeneous />

---
layout: eq
---

## Choice of algorithm assumes

<div class="dist">

| | | meaning |
|---|---|---|
| <em class="hl-red">partitional</em> vs <em class="hl-red">hierarchical</em> | | one level, or clusters inside clusters |
| <em class="hl-blue">exclusive</em> vs <em class="hl-blue">overlapping</em> | | one cluster per point, or several |
| <em class="hl-green">hard</em> vs <em class="hl-green">fuzzy</em> | | a label, or a weight $w_k \in [0,1]$ with $\sum_k w_k = 1$ |
| <em class="hl-purple">complete</em> vs <em class="hl-purple">partial</em> | | everything is clustered, or some points are left out |
| <em class="hl-gold">homogeneous</em> vs <em class="hl-gold">heterogeneous</em> | | same size, shape and density, or not |

<div class="note mt-4">A method answers all five questions.</div>

</div>

<style>
.dist { font-size: 1rem; padding-top: 0.6rem; }
.dist td { padding: 0.5rem 0.9rem 0.5rem 0; }
</style>

---
layout: eq
---

## Distance and dissimilarity

<div class="note">

$D : E \times E \to \mathbb{R}^{+}$

</div>

<div class="cols">
<div>

#### <em class="hl-blue">dissimilarity assumes</em>

- $D(x, y) = D(y, x) \geq 0$
- $D(x, x) = 0$

</div>
<div>

#### <em class="hl-green">distance assumes, on top</em>

- $D(x, y) = 0 \Leftrightarrow x = y$
- $D(x, y) \leq D(x, z) + D(z, y)$

</div>
</div>

<div class="mt-6">Every clustering method reads the data through this function</div>

---
layout: fig
---

## Distances examples

<DistanceZoo />

---
layout: fig
---

## Hamming: a distance for categories

<HammingDemo />

---
layout: fig
---

## Distances between groups

<LinkageDefinitions />

---
layout: section
---

# Clustering quality

---
layout: eq
---

## Within and between

<div class="rows">

| | |
|---|---|
| $m_i = \frac{1}{n_i}\sum_{x \in C_i} x$ | the centre of cluster $C_i$ |
| $m = \frac{1}{n}\sum_{x} x$ | the centre of the whole dataset |
| <em class="hl-blue">$J_w = \sum_i \sum_{x \in C_i} D^2(x, m_i)$</em> | within: how tight the clusters are |
| <em class="hl-green">$J_b = \sum_i n_i\, D^2(m_i, m)$</em> | between: how far each $m_i$ sits from $m$ |

</div>

<div class="mt-4">

a good clustering makes $J_w$ small and $J_b$ large, and $J_w + J_b$ is the same
for every clustering of the same data

</div>

<div class="note mt-2">

<em class="hl-red">$J_w$ with $K = n$ is zero</em>, so $J_w$ alone cannot choose $K$

</div>

<style>
.rows { font-size: 1.05rem; }
.rows td { padding: 0.4rem 1.4rem 0.4rem 0; }
</style>

---
layout: fig
---

## What a good clustering looks like

<GoodClustering />

---
layout: section
---

# K-means

---
layout: eq
---

## The objective

$$ J_w \;=\; \sum_{k=1}^{K} \sum_{x_i \in C_k} \|x_i - \mu_k\|^2 $$

<div>

find the $K$ centres that make this as small as possible

</div>

<div class="note mt-4">

There are $P(n, K) = \frac{1}{K!}\sum_{k=0}^{K}(-1)^{K-k}\binom{K}{k} k^{\,n}$ partitions to try, so the exact problem is NP-hard.

</div>

<PartitionCount />

---
layout: fig
---

## Lloyd's algorithm

<KmeansLloyd />

---
layout: fig
---

## Inertia

<InertiaDemo />

---
layout: fig
---

## Random results

<KmeansInit />

---
layout: fig
---

## k-means fails with

<KmeansLimits />

---
layout: eq
---

## Variants

<div class="variants">

| | what changes | when |
|---|---|---|
| <em class="hl-green">k-means++</em> | spread the initial centres out | the default |
| <em class="hl-blue">k-medoids</em> | centres are actual data points | robust to outliers |
| <em class="hl-purple">kernel k-means</em> | cluster in a feature space | non-convex shapes |
| <em class="hl-gold">mini-batch k-means</em> | update on samples of rows | large $n$ |

<div class="note mt-4">

All of them still need $K$.

</div>

</div>

<style>
.variants { font-size: 1.05rem; padding-top: 1rem; }
.variants td { padding: 0.55rem 0.9rem 0.55rem 0; }
</style>

---
layout: section
---

# Mountain and subtractive clustering

---
layout: fig
---

## Clusters as peaks of a landscape

<MountainIdea />

---
layout: fig
---

## Mountain function

<MountainProfile />

---
layout: fig
---

## Take a peak, flatten it, repeat

<MountainSteps />

---
layout: fig
---

## Dropping the grid

<SubtractiveDemo />

---
layout: eq
---

## Pros and cons

<div class="cols">
<div>

#### <em class="hl-green">Pros</em>

- no need to guesstimate the number of clusters
- the centres are real peaks of density
- cheap to use as an initialisation for k-means

</div>
<div>

#### <em class="hl-red">Cons</em>

- $\sigma$ (or $r_a$) is very sensitive
- the grid grows as $m^d$, so $d$ must be small
- subtractive drops the grid, but still pays $O(n^2)$

</div>
</div>

---
layout: section
---

# Hierarchical clustering

---
layout: fig
---

## Representing clusters inside clusters

<HierarchyIdea />

---
layout: fig
---

## Agglomerative, one merge at a time

<AgglomerativeSteps />

---
layout: fig
---

## Cutting the dendrogram

<DendrogramCut />

---
layout: fig
---

## Ward: the cost of a merge

<WardIdea />

---
layout: fig
---

## Moving the reference point

<HuygensDemo />

---
layout: eq
---

## Where the Ward formula comes from

<div class="proof">

$\Delta J_w = \sum_{x \in C_a \cup C_b} \|x - m\|^2 - \sum_{x \in C_a} \|x - m_a\|^2 - \sum_{x \in C_b} \|x - m_b\|^2$

<div class="note">

with $m = \dfrac{n_a m_a + n_b m_b}{n_a + n_b}$, the centre of the merged cluster

</div>

$\Delta J_w = n_a \|m_a - m\|^2 + n_b \|m_b - m\|^2$

<div class="note">the identity of the previous slide, applied to each half: the inner sums cancel</div>

$m_a - m = \dfrac{n_b}{n_a + n_b}(m_a - m_b), \quad m_b - m = \dfrac{n_a}{n_a + n_b}(m_b - m_a)$

<div class="note">both centres sit on the segment between them</div>

<em class="hl-green">$\Delta J_w = \dfrac{n_a n_b^2 + n_b n_a^2}{(n_a + n_b)^2}\|m_a - m_b\|^2 = \dfrac{n_a n_b}{n_a + n_b} D^2(m_a, m_b)$</em>

<div class="note">substitute, and the squares collapse: only the two centroids and the two sizes are needed</div>

</div>

<style>
.proof { font-size: 0.95rem; line-height: 1.5; }
.proof > p { margin: 0.35rem 0 0; }
.proof .note { margin-bottom: 0.5rem; }
</style>

---
layout: fig
---

## Ward distance

<WardFormula />

---
layout: fig
---

## Every merge changes every distance

<LanceWilliams />

---
layout: eq
---

## WPGMA: Weighted Pair Group Method with Arithmetic mean

$$ D(C_i, C_j) = \frac{D(C_a, C_j) + D(C_b, C_j)}{2} $$

<div>a distance computed from the previous step, never from the points again</div>

<div class="note mt-4">Each merge costs one average, so hierarchical clustering
can afford to rebuild the whole table at every step.</div>

---
layout: fig
---

## Unweighted Pair Group Method with Arithmetic mean

<WpgmaVsUpgma />

---
layout: fig
---

## Four linkages

<LinkageCompare />

---
layout: fig
---

## Four linkages

<LinkageDendrograms />

---
layout: eq
---

## Which linkage to use

<div class="props">

| | good at | bad at |
|---|---|---|
| <em class="hl-blue">single / MIN</em> | follows chains of any shape | one bridge of noise joins two clusters |
| <em class="hl-red">complete / MAX</em> | resists outliers | breaks large clusters, prefers round ones |
| <em class="hl-green">average</em> | does not break large clusters | prefers round clusters |
| <em class="hl-purple">Ward</em> | balanced, k-means-like clusters | prefers round clusters of similar size |

<div class="note mt-4">Linkage is a second modelling choice, as consequential as the distance.</div>

</div>

<style>
.props { font-size: 1rem; padding-top: 0.8rem; }
.props td { padding: 0.5rem 0.9rem 0.5rem 0; }
</style>

---
layout: eq
---

## Tree

<div class="cols">
<div>

#### <em class="hl-green">Pros</em>

- no $K$ to choose up front
- a readable tree at every scale
- any dissimilarity will do, not just Euclidean

</div>
<div>

#### <em class="hl-red">Cons</em>

- $O(N^2)$ memory, $O(N^2 \log N)$ time
- a threshold to cut still has to be chosen
- a merge is never undone

</div>
</div>

---
layout: section
---

# DBSCAN

---
layout: fig
---

## Neighborhood and crowdedness

<DbscanIdea />

---
layout: fig
---

## Core, border, noise

<DbscanPoints />

---
layout: eq
---

## Algorithm

<div class="cols">
<div>

#### <em class="hl-blue">DBSCAN</em>

1. take an unvisited point $x_i$
2. count its neighbours within $\varepsilon$
3. fewer than MinPts: mark it noise, move on
4. otherwise open a cluster and grow it:
    - core neighbours add their own neighbourhood
    - border points join without theirs

</div>
<div>

#### <em class="hl-green">Result</em>

- one cluster per dense region in the data
- a set of noise points
- no $K$, and no centre: a cluster is defined by its density, not by a prototype

</div>
</div>

---
layout: fig
---

## Effect of ε

<DbscanEpsilon />

---
layout: fig
---

## Reading ε off the k-NN curve

<DbscanElbow />

---
layout: fig
---

## Effect of MinPts

<DbscanMinpts />

---
layout: fig
---

## Shapes k-means cannot reach

<DbscanVsKmeans />

---
layout: eq
---

## DBSCAN

<div class="cols">
<div>

#### <em class="hl-green">Pros</em>

- clusters of any shape
- noise is labelled, not forced into a cluster
- no guesstimate needed for $K$

</div>
<div>

#### <em class="hl-red">Cons</em>

- MinPts and $\varepsilon$ are hard to choose
- one density is assumed for the whole dataset
- border points depend on the order of the scan

</div>
</div>

<div class="note mt-6">HDBSCAN tackles the uniform density assumption</div>

---
layout: section
---

# HDBSCAN

---
layout: eq
---

## DBSCAN at every scale at once

<div class="lead">

run DBSCAN for every value of $\varepsilon$ at once, and keep the clusters that last

</div>

<div class="cols mt-4">
<div>

#### <em class="hl-green">Benefits</em>

- no $\varepsilon$ to choose
- clusters of different densities, side by side in one dataset
- a hierarchy, not one partition

</div>
<div>

#### <em class="hl-gold">Need to choose</em>

- MinPts: the scale at which density is measured
- $C_{\min}$: the size of the smallest cluster worth the name

</div>
</div>

---
layout: eq
---

## Six steps

<div class="steps">

| | | |
|---|---|---|
| 1. compute $\mathrm{core}_k$ | <em class="hl-blue">measure the local density</em> | MinPts enters here |
| 2. transform the space | <em class="hl-blue">use $d_{\mathrm{mreach}}$ instead of $d$</em> | sparse points are pushed away |
| 3. spanning tree | <em class="hl-green">connect every point, cheaply</em> | $n - 1$ edges |
| 4. cluster hierarchy | <em class="hl-green">cut the edges, heaviest first</em> | a dendrogram |
| 5. condense the hierarchy | <em class="hl-gold">collapse branches under $C_{\min}$</em> | $C_{\min}$ enters here |
| 6. extract stable clusters | <em class="hl-red">keep what survives longest</em> | the answer |

</div>

<style>
.steps { font-size: 0.98rem; }
.steps td { padding: 0.42rem 1.1rem 0.42rem 0; }
</style>

---
layout: fig
---

## Step 1: measure the density

<CoreDistance />

---
layout: eq
---

## Step 2: transform the space

$$ d_{\mathrm{mreach}-k}(x_i, x_j) = \max\left(\mathrm{core}_k(x_i),\ \mathrm{core}_k(x_j),\ d(x_i, x_j)\right) $$

<div class="cols mt-4">
<div>

#### <em class="hl-blue">Two points are close only if</em>

- they are close in space
- they both sit in a dense region

</div>
<div>

#### <em class="hl-green">Sparse points</em>

- are pushed away from everything, including each other
- so single linkage stops chaining through them

</div>
</div>

<div class="note mt-4">Islands and sea: the sea widens, the land does not move.</div>

---
layout: fig
---

## Step 2: a worked example

<MreachExample />

---
layout: fig
---

## Step 2: why the maximum

<MreachIntuition />

---
layout: fig
---

## What the new distance does

<MreachEffect />

---
layout: fig
---

## Step 3: the minimum spanning tree

<MstStep />

---
layout: fig
---

## Step 3: how the tree is built

<MstBuild />

---
layout: fig
---

## Step 4: cluster hierarchy

<MstToHierarchy />

---
layout: fig
---

## Step 4 on real data

<HdbscanHierarchy />

---
layout: fig
---

## Step 5: condense the tree

<CondenseExample />

---
layout: fig
---

## Step 5 on real data

<CondensedTree />

---
layout: fig
---

## Stability

<StabilityIdea />

---
layout: fig
---

## Stability example

<StabilityExample />

---
layout: fig
---

## Step 6: keep the stable clusters

<ExtractExample />

---
layout: eq
---

## Six steps

<div class="steps">

| | | |
|---|---|---|
| 1. compute $\mathrm{core}_k$ | <em class="hl-blue">measure the local density</em> | MinPts enters here |
| 2. transform the space | <em class="hl-blue">use $d_{\mathrm{mreach}}$ instead of $d$</em> | sparse points are pushed away |
| 3. spanning tree | <em class="hl-green">connect every point, cheaply</em> | $n - 1$ edges |
| 4. cluster hierarchy | <em class="hl-green">cut the edges, heaviest first</em> | a dendrogram |
| 5. condense the hierarchy | <em class="hl-gold">collapse branches under $C_{\min}$</em> | $C_{\min}$ enters here |
| 6. extract stable clusters | <em class="hl-red">keep what survives longest</em> | the answer |

</div>

<style>
.steps { font-size: 0.98rem; }
.steps td { padding: 0.42rem 1.1rem 0.42rem 0; }
</style>

---
layout: fig
---

## Dataset with multiple densities

<HdbscanResult />

---
layout: eq
---

## HDBSCAN

<div class="cols">
<div>

#### <em class="hl-green">Pros</em>

- two parameters, MinPts and $C_{\min}$, both easier to tune than $\varepsilon$
- clusters at varying densities
- robust to outliers

</div>
<div>

#### <em class="hl-red">Cons</em>

- more machinery
- more compute
- suffers in high dimension, like every density method

</div>
</div>

<div class="note mt-6">HDBSCAN is the default choice when density varies</div>

---
layout: fig
---

## Four methods on four datasets

<AlgoCompare />

---
layout: eq
---

## The map

<div class="map">

| Method | Parameters | Good with | Benefits |
|---|---|---|---|
| <em class="hl-blue">k-means</em> | $K$ | spherical, similar size | fast |
| <em class="hl-purple">hierarchical</em> | cut height | whatever the linkage favours | a dendrogram to read |
| <em class="hl-red">subtractive</em> | $r_a$ | one blob per peak of density | finds $K$ by itself |
| <em class="hl-gold">DBSCAN</em> | $\varepsilon$, MinPts | any shape, one density | noise is labelled |
| <em class="hl-green">HDBSCAN</em> | MinPts, $C_{\min}$ | any shape, any density | the default when unsure |

<div class="note mt-4">

The distance comes first: every row above reads the data through $D$, and none
of them can repair a bad one.

</div>

</div>

<style>
.map { font-size: 1rem; padding-top: 0.6rem; }
.map td { padding: 0.5rem 0.9rem 0.5rem 0; }
</style>
