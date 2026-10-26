# Session 5, interactive

The interactive companion to `Course05/slides.pptx`: the same lecture on
non-negative matrix factorization as a [Slidev](https://sli.dev) deck, where
NMF is *refitted in the browser* as the sliders move. The multiplicative
updates, ALS and HALS run live, a few passes per animation frame, so the loss
curves grow and the parts of the faces appear while you watch.

Published as
[`Course05/interactive.html`](https://pauldubois98.github.io/AdvancedMachineLearning2026/Course05/interactive.html).

```bash
make interactive-c05      # dev server
make interactive-build    # rebuild the published copies (commit the result)
```

or, from this directory, `npm install && npm run dev`.

This is its own npm project, like `Course04/slidev/`: the decks share no files.
`make interactive-build` writes `Course05/interactive.html` one level up, a
single self-contained file, **committed to the repository** because the Pages
workflow never runs a build. It also opens straight from disk.

Press `h` to hide Slidev's navigation bar (and `h` again to bring it back).
On a tall window Slidev pins that bar over the bottom of the slide; `style.css`
makes it appear only on hover, and `setup/shortcuts.ts` adds the key.

## What is live

| slide | knobs |
| --- | --- |
| Reducing size | r, against the numbers stored |
| Column as a weighted sum | the three amounts h<sub>j</sub>(k): rebuild the column by hand |
| Why non-negative | the weight of each part, signed or not |
| Additive components | the face, and how many PCA or NMF components rebuild it |
| Faces: the three matrices | the face j, and the part k |
| Faces: what comes out | r, refitted live (HALS); the face to rebuild |
| Hyperspectral: a cube, unfolded | the wavelength, the pixel |
| Hyperspectral: the three matrices | the pixel |
| Hyperspectral: what comes out | r, NNDSVD or random start, the seed |
| Topics: the three matrices | the post, the topic |
| Topics: what comes out | r, the start |
| Fill missing values | the share hidden, r |
| Music: the three matrices | the frame |
| Music: what comes out | the loss (Frobenius, KL, Itakura–Saito), r, passes |
| Divergence, not distance | x and y, against d(x, y) and d(y, x) |
| Classic choices | x, and the y the scaling panel is read at |
| The three noise slides | the model y, the observed x (and σ) |
| General formula | β, continuously, and x |
| Convex in each half | which variable is frozen, and its value |
| The answer is never unique | λ₁, λ₂, a swap, and a mix that breaks non-negativity |
| Gradient descent kept positive | the start and the step size η |
| Lee and Seung rules | the current entry, against the ratio |
| Minimize a majorant | MM steps, the start, the curvature of the surrogate |
| Where the step size came from | the current entry, the vertex, the other entries' share |
| Monotone and slow | r and the start, MU live for Frobenius and KL |
| Initialization (rays) | MU passes from five starts, r = 2 |
| Initialization (faces) | MU passes from five starts, r = 6, live |
| Initialization (race) | the pass the losses are read at |
| Entries with different importances | the share observed |
| Matrix completion | r, against the share hidden |
| Sparsity | λ, refitted live |
| Rank-one layers | how many layers are summed |
| One layer at a time | the layer k |
| One entry at a time | [R h]<sub>i</sub> and ‖h‖² |
| Three algorithms, measured | r; MU, ALS and HALS race live |
| Choosing r | r (precomputed fits, r = 2 … 48), the face rebuilt |

## The data

`lib/data5.ts` imports `Course05/data/*.json`, written by
`scripts/make_data_c05.py`. That script loads `make_figures_c05.py` and calls
its own generators (`_spectral_toy`, `_music_toy`, `_layers_fit`, the ratings
toy, the two-arm cloud), so the matrices are the printed ones, not look-alikes.
The faces are the Olivetti faces shrunk from 64 × 64 to 32 × 32, which keeps a
live refit fast; the initialization race is the printed run itself, at 64 × 64.
The fits behind *Choosing r* are too slow to run live for r up to 48, so
`choosing.json` holds them: the parts, the weights, and how well each part
is found again by a fit from another start.

`lib/nmf.ts` is a transcription of the script's `_mu`, `_als`, `_hals` and
`_init`: the same rules, the same floors, the same five starts.

## Gotchas worth knowing before editing

- A component name that starts like an icon collection (`Fa…`, `Ic…`, …) and
  has no `.vue` file behind it is resolved as an icon, and the build fails
  with `Icon "fa/ces-setup" not found`. Create the component first.
- A scoped style of a parent applies to the *root* element of a child
  component. A parent rule for `.tiles` styled the root of `Tiles.vue` too;
  keep container class names distinct from the child components' roots.
- Inline `$math$` inside a one-line HTML block is not parsed: put the content
  on its own line with blank lines around it.
- The live fits only step while their slide is visible (`lib/runner.ts`), and
  stay within about 14 ms per frame, so a hidden slide costs nothing.
- The decks pin `@iconify/utils` and `unocss` in `package.json` `overrides`,
  as Course03 and Course04 do, for Node 18.
