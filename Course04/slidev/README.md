# Session 4, interactive

The interactive companion to `Course04/slides.pptx`: the same lecture as a
[Slidev](https://sli.dev) deck, where every figure is *computed in the
browser*. Where the printed deck shows three snapshots of a parameter, this one
gives the parameter a slider and refits the model as it moves.

Published as
[`Course04/interactive.html`](https://pauldubois98.github.io/AdvancedMachineLearning2026/Course04/interactive.html).

```bash
make interactive-c04      # dev server
make interactive-build    # rebuild the published copies (commit the result)
```

or, from this directory, `npm install && npm run dev`. `npm run export` writes a
PDF (needs playwright-chromium).

This is its own npm project, separate from `Course03/slidev/`: the two decks
share no files, so rebuilding one never changes the other.

`make interactive-build` writes `Course04/interactive.html` one level up: a
single self-contained file with scripts, styles and fonts inlined (2.9 MB, about
1.4 MB over the wire). It is **committed to the repository**, because
`.github/workflows/static.yml` uploads the repo as it stands and never runs a
build, so after changing a slide, rebuild *and commit*, or the published deck
stays on the old version.

Being one file also means it runs with no server at all: double-click it, open
it from a USB stick, or mail it to a student. A split build cannot do that:
browsers refuse to load ES modules next to a `file://` page, and the deck opens
blank.

The deck uses `routerMode: hash` and a relative `--base`, so the file works from
any path without server rewrites; deep links look like `interactive.html#/36`.

## What is live

| slide | knobs |
| --- | --- |
| No labels | the spread of the groups, and the K asked for |
| Two ways to simplify a table | q columns kept, K rows kept, on the same table |
| What a cluster can mean | blur the blobs together, ε for the density panel |
| Partitional or hierarchical | pull the sub-groups apart until the nesting shows |
| Exclusive or overlapping | the width of the shared zone |
| Hard or fuzzy | the fuzzifier m; click a point to read its weights |
| Complete or partial | how near a point must sit to be assigned |
| Homogeneous or heterogeneous | how unlike the three clusters are made |
| Distances examples | q of the Lq ball, and the correlation Mahalanobis reads |
| Hamming | click a letter to mutate it, the count follows |
| Distances between groups | the gap between the groups, and which linkage to draw |
| What a good clustering looks like | K, against three deliberately bad labellings |
| The objective | n and K, against the number of partitions to try |
| Lloyd's algorithm | step through assign and move, K, the starting draw, k-means++ |
| Inertia | K, with the spokes and the whole inertia curve |
| Random results | the starting draw, against the best of ten restarts |
| k-means fails with | the dataset, and K |
| Clusters as peaks of a landscape | σ of one hill, and the grid step |
| Mountain function | σ and β, on a profile of the two formulas |
| Take a peak, flatten it, repeat | peaks subtracted, σ, β, and the stopping fraction |
| Dropping the grid | r_a, and the fraction a peak must keep to count |
| Representing clusters inside clusters | linkage, and the number of clusters kept |
| Agglomerative, one merge at a time | the merges done so far, and the linkage |
| Cutting the dendrogram | the cut height, the linkage, and clusters against height |
| Ward: the cost of a merge | the three cluster sizes, against the nearest pairs |
| Moving the reference point | click anywhere to move m, both sides recomputed |
| Ward distance | n_i, n_j, the centre gap, and the size factor |
| Every merge changes every distance | the three known distances and the three sizes |
| Unweighted Pair Group Method | the two sizes and the two distances |
| Four linkages | stray points added, and the number of clusters kept |
| Four linkages (dendrograms) | stray points, cluster size, and the chaining measure |
| Neighborhood and crowdedness | ε and MinPts, on two neighbourhoods |
| Core, border, noise | ε and MinPts, with the three counts |
| Effect of ε | ε, with clusters and noise swept over every ε |
| Reading ε off the k-NN curve | MinPts and the line, against the suggested knee |
| Effect of MinPts | MinPts, with the sweep, and ε |
| Shapes k-means cannot reach | ε, scaled over three datasets at once |
| Step 1: measure the density | MinPts, on the circles and on the colour map |
| Step 2: a worked example | k, and which of the three numbers wins the max |
| Step 2: why the maximum | stray points in the path, k, and the joining threshold |
| What the new distance does | k, on every pair of the cloud |
| Step 3: the minimum spanning tree | k, and the heaviest edges removed |
| Step 3: how the tree is built | Prim's algorithm, edge by edge |
| Step 4: cluster hierarchy | the heaviest edges cut, tree and dendrogram together |
| Step 4 on real data | the cut, C_min and MinPts, against three reference cuts |
| Step 5: condense the tree | C_min, and the two sides of each of the three cases |
| Step 5 on real data | C_min and MinPts, raw tree beside condensed tree |
| Stability | the points and the span of each of the two bars |
| Stability example | λ_birth, λ_death, and when each point leaves |
| Step 6: keep the stable clusters | the six stabilities, and what the rule returns |
| Dataset with multiple densities | ε for DBSCAN, C_min and MinPts for HDBSCAN |
| Four methods on four datasets | one knob per method, over the whole grid |

## The libraries

Everything is written from scratch in TypeScript, so a slider can refit in a few
milliseconds with no server and no wasm:

| file | holds |
| --- | --- |
| `lib/data4.ts` | the datasets: blobs, moons, rings, the two arms, the three-density cloud, the toy point sets |
| `lib/cluster.ts` | k-means: Lloyd step by step, k-means++, inertia, J_w and J_b, fuzzy weights |
| `lib/hier.ts` | agglomerative clustering: the Lance-Williams update for five linkages, scipy's linkage matrix, both cuts, a dendrogram layout |
| `lib/density.ts` | DBSCAN, core distances, mutual reachability, Prim's tree, HDBSCAN's condensed tree, stability and excess-of-mass selection |
| `lib/mountain.ts` | the mountain function, peak subtraction, Chiu's subtractive clustering |

### Checked against scikit-learn and scipy

The libraries are tested on the same rows the browser uses, by dumping them from
an esbuild bundle and reading them back in Python:

- **linkage**: for single, complete, average, weighted and Ward, the merge
  heights match `scipy.cluster.hierarchy.linkage` to 7e-15, the merged pairs are
  identical, and so are the dendrogram leaf order and both ways of cutting;
- **k-means**: Lloyd from the same starting centres reproduces
  `KMeans(init=mu0, n_init=1)` to 7e-16, with the same inertia;
- **DBSCAN**: the partition, the noise set and the core-point count are
  identical to `sklearn.cluster.DBSCAN` at five settings of (ε, MinPts),
  including the degenerate ones;
- **core distances**: identical to `np.sort(D)[:, k]`, and the k-distance curve
  to `NearestNeighbors(n_neighbors=k).kneighbors()`;
- **minimum spanning tree**: the same total weight as
  `scipy.sparse.csgraph.minimum_spanning_tree` under d_mreach, and reading
  single linkage off it reproduces scipy's tree exactly;
- **HDBSCAN**: the same number of clusters, the same number of noise points and
  the *same partition* as `sklearn.cluster.HDBSCAN(min_cluster_size=10)`;
- **mountain and subtractive**: the peak heights, the peak positions and the
  potentials match a numpy transcription to 1e-9.

## Gotchas

- **`layout: fig` and `layout: eq`** are the two layouts: a title plus a figure
  that eats the remaining height, or everything centred. They mirror the
  geometry pandoc gives the printed deck.
- **Math inside a component** is not markdown, so KaTeX never sees it: use
  `<Tex formula="..." display />`. In `slides.md`, `$...$` inside a `<div>` only
  renders when blank lines surround it.
- **UnoCSS attributify** rewrites a bare `opacity="1"` on an SVG element into
  the utility class `opacity-1`, i.e. 1%. Use `stroke-opacity` / `fill-opacity`.
- **`preserveAspectRatio="none"`** stretches an SVG to its box, which squashes
  text. A chart that fills its box takes its viewBox from `useFitBox`
  (`lib/fitbox.ts`), which measures the box and gives the viewBox the same
  aspect ratio; a hand-drawn figure uses `xMidYMid meet` instead.
- **A `.value` in a template** is wrong twice over: Vue unwraps refs there, so
  `kept.value` compiles to `kept.value.value` and throws at render time.
