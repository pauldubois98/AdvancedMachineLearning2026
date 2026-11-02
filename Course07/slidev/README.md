# Session 7, interactive

The interactive companion to the printed deck, a [Slidev](https://sli.dev) deck
where the figures are *computed in the browser*. Every knob the printed deck can
only show three snapshots of is a slider here, and the model is refitted as it
moves.

| source | published as | the lecture |
| --- | --- | --- |
| `slides.md` | [`Course07/interactive.html`](https://pauldubois98.github.io/AdvancedMachineLearning2026/Course07/interactive.html) | Trees, Forests and Boosting: depth, max_features, M, η, λ, γ, bins |

```bash
make interactive-c07    # dev server
make interactive-build    # rebuild every published copy (commit the result)
```

`make interactive-build` writes `Course07/interactive.html` one level up: a single self-contained
file, scripts, styles and fonts inlined (2.5 MB, about 1.3 MB over the wire). It
is **committed to the repository**, because `.github/workflows/static.yml`
uploads the repo as it stands and never runs a build — so after changing a
slide, rebuild *and commit*, or the published deck stays on the old version.

Being one file also means it runs with no server at all: double-click it, open
it from a USB stick, or mail it to a student. A split build cannot do that —
browsers refuse to load ES modules next to a `file://` page, and the deck opens
blank.

The deck uses `routerMode: hash` and a relative `--base`, so the single HTML
file works from any path without server rewrites; deep links look like
`interactive.html#/29`.

Or, from this directory, `npm install && npm run dev`. `npm run export` writes a
PDF (needs playwright-chromium).

Press `h` to hide Slidev's navigation bar (and `h` again to bring it back).
On a tall window Slidev pins that bar over the bottom of the slide; `style.css`
makes it appear only on hover, and `setup/shortcuts.ts` adds the key.

## What is live — Trees, Forests and Boosting

| slide | knobs |
| --- | --- |
| A tree is a sequence of questions | the three thresholds, on the tree and on the partition at once |
| Choosing the split | feature, threshold and impurity measure, against the scan of every candidate |
| What "pure" means | the share of class 1 in the node, read off all three measures |
| Depth is the capacity knob | max_depth and min_samples_leaf, with train and test accuracy |
| Regression trees predict staircases | depth, noise, rows: the training error against the error on the true curve |
| And they over-fit | the depth curve is refitted as the label noise moves |
| The real problem: instability | two bootstrap samples side by side, and eight more boundaries on top |
| The idea | M and ρ, against the simulated spread and the formula |
| Trees must disagree | ρ and M, as a stacked bar of the two terms |
| Averaging is not magic | ρ, on the variance floor and on "trees that count" |
| What max_features does | p, max_features, and a fresh draw of columns per node |
| The knob: max_features | one forest per value of max_features, measured in the background |
| Two injections of randomness | how many trees the diagram draws |
| The boundary stops twitching | M from 1 to 120, as a running average of cached per-tree fields |
| Strength against diversity | ρ and single-tree error, measured, against the forest's error |
| More trees never over-fits | the running vote of the first M trees, three seeds |
| Combine many trees differently | m, η and depth: F_m above, the residuals and the next tree below |
| Forest and boosting attack different errors | M, on the same data, fitted both ways |
| Boosting *can* over-fit | rounds, η, depth, label noise: where the test curve turns |
| Boosting as an additive model | one row's ledger: every tree's leaf value and the running sum |
| Boosting is gradient descent in function space | the loss, and the pseudo-residual read off its slope |
| Shrinkage | η against η = 1, at the same number of trees |
| The learning rate is a regulariser | four η, one boosting run each, with their minima |
| Regularisation inside the tree objective | λ and γ, on a tree that is really grown with them |
| Splitting candidates | the exhaustive gain scan, with λ and γ |
| Loss simplification for one leaf | G, H, λ on the leaf's parabola |
| Scoring candidate splits | the gain arithmetic, term by term, on the 40-row node |
| Gradient and Hessian | the loss, the row's label and the current prediction |
| Summing trees to get the prediction | a row routed through tree 1, and the ledger of all 30 |
| Bin each feature once | the number of bins, against what gets stored |
| Finding the optimal cut in one sweep | the cut, on the running totals and the gain it feeds |
| Scan bin edges, not rows | bins, against the exact scan: what the approximation costs |
| A child's histogram is the parent minus its sibling | the split, and which child is the cheap one |
| Leaf-wise growth | the budget of leaves, both policies grown for real |
| GOSS | top_rate, other_rate, and the reweighting switched off |
| Categories: the target statistic problem | leave the row out of its own average; the prior weight |
| The encoding leaks the label | how many customers share the category |
| Ordered target statistics: use only what came before | another permutation, and the prior weight |
| Ordered target statistics: the correlation is gone | categories and prior weight, with corr(encoding, y) measured |
| Oblivious trees | the row's two features, routed to an array index |
| XGBoost, LightGBM, CatBoost | read one library's column on its own |

## How the figures are computed

`lib/tree.ts` is CART, `lib/forest.ts` bagging with a per-node column draw,
`lib/boost.ts` gradient boosting (squared loss, and log loss with the Newton
leaf step), `lib/gbm.ts` the second-order objective XGBoost scores splits with,
plus LightGBM's histograms, leaf-wise growth and GOSS, and CatBoost's greedy and
ordered target statistics. The first three were checked against scikit-learn on
the datasets used here, on identical rows:

- classification and regression trees: identical leaf counts, identical accuracy
  and MSE, predictions equal to ~1e-17, and a depth-4 boundary that agrees with
  `DecisionTreeClassifier` on 100% of a 20 × 20 grid, under both Gini and entropy;
- forests: ρ and single-tree error within 0.003 of `RandomForestClassifier`;
- boosting: `decision_function` reproduced to 4e-16 against
  `GradientBoostingClassifier`, including the init and the Newton leaf values,
  and squared-loss predictions to 6e-17 against `GradientBoostingRegressor`;
- the gain formula, the bin totals and the prefix sums: identical to numpy on the
  40-row node the XGBoost and LightGBM slides share.

`lib/data.ts` and `lib/databis.ts` regenerate the printed deck's datasets with a
seeded RNG, so the pictures are the same on every machine. They are not
pixel-identical to the matplotlib figures — the random draws differ — but the
shapes, spreads and seeds-by-intent match.

## Gotchas worth knowing before editing

- **Never put a bare `opacity`, `fill-opacity` or `stroke-opacity` attribute on
  an SVG element.** Slidev runs UnoCSS with attributify, which reads
  `opacity="1"` as the utility `opacity-1` and renders it at *1%*. `LineChart.vue`
  therefore sets every paint property through `:style`.
- **`preserveAspectRatio="none"`** stretches an SVG to its box, which squashes
  text. `LineChart.vue` takes its viewBox from `useFitBox` (`lib/fitbox.ts`),
  which measures the box and gives the viewBox the same aspect ratio.
- Inline `$math$` inside a raw HTML block is not parsed. Leave a blank line after
  the opening tag and before the closing one, and markdown-it (and KaTeX) will
  see it.
- This deck pins `@iconify/utils` and `unocss` in `package.json` `overrides`:
  their newer releases need Node ≥ 20.19, and this repo builds on Node 18.
  Drop the pins once the machine is on a newer Node.
