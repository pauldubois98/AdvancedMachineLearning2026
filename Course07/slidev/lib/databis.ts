// The datasets of the trees-and-boosting deck (scripts/make_figures_c03bis.py),
// regenerated here so the sliders can refit on them.
import { Rng } from './rng'
import { Dataset } from './data'

/** A dataset whose true boundary really is axis-aligned: trees shine here. */
export function treeToy(seed = 0, n = 240, flip = 0.06): Dataset {
  const rng = new Rng(seed + 1)
  const X: number[][] = []
  const y: number[] = []
  for (let i = 0; i < n; i++) {
    const a = rng.uniform()
    const b = rng.uniform()
    X.push([a, b])
    y.push(a > 0.55 || (b > 0.62 && a > 0.22) ? 1 : 0)
  }
  for (let i = 0; i < n; i++) if (rng.next() < flip) y[i] = 1 - y[i]
  return { X, y }
}

/** sin(2 pi x) with noise: the regression-tree and boosting-stages slides. */
export function sine1d(n = 80, noise = 0.18, seed = 0) {
  const rng = new Rng(seed + 2)
  const x: number[] = []
  for (let i = 0; i < n; i++) x.push(rng.uniform())
  x.sort((a, b) => a - b)
  const truth = (v: number) => Math.sin(2 * Math.PI * v)
  const y = x.map((v) => truth(v) + rng.normal(0, noise))
  return { x, X: x.map((v) => [v]), y, truth }
}

/** Informative columns, redundant copies of them, and pure noise columns:
 *  the 25-column dataset the max_features slides are measured on. */
export function classif(
  o: {
    n?: number
    p?: number
    informative?: number
    redundant?: number
    classSep?: number
    flipY?: number
    seed?: number
  } = {},
): Dataset {
  const n = o.n ?? 600
  const p = o.p ?? 25
  const inf = o.informative ?? 12
  const red = o.redundant ?? 8
  const sep = o.classSep ?? 0.7
  const flipY = o.flipY ?? 0.05
  const rng = new Rng((o.seed ?? 0) + 3)

  // one centroid per class, on a vertex of the informative hypercube
  const centre = [new Array(inf), new Array(inf)]
  for (let j = 0; j < inf; j++) {
    const s = rng.next() < 0.5 ? -1 : 1
    centre[0][j] = -s * sep
    centre[1][j] = s * sep
  }
  // sklearn mixes the informative block with a random square matrix, which is
  // what stops any single column from carrying the whole signal (and is what
  // makes max_features worth tuning at all)
  const A: number[][] = []
  for (let r = 0; r < inf; r++) {
    const row = new Array(inf)
    for (let j = 0; j < inf; j++) row[j] = rng.normal(0, 1)
    A.push(row)
  }
  // the redundant columns are random linear combinations of the informative ones
  const mix: number[][] = []
  for (let r = 0; r < red; r++) {
    const row = new Array(inf)
    for (let j = 0; j < inf; j++) row[j] = rng.normal(0, 1)
    mix.push(row)
  }

  const X: number[][] = []
  const y: number[] = []
  for (let i = 0; i < n; i++) {
    const k = rng.next() < 0.5 ? 1 : 0
    const raw = new Array(inf)
    for (let j = 0; j < inf; j++) raw[j] = rng.normal(centre[k][j], 1)
    const z = A.map((row) => {
      let s = 0
      for (let j = 0; j < inf; j++) s += row[j] * raw[j]
      return s / Math.sqrt(inf)
    })
    const row = z.slice()
    for (const m of mix) {
      let s = 0
      for (let j = 0; j < inf; j++) s += m[j] * z[j]
      row.push(s / Math.sqrt(inf))
    }
    while (row.length < p) row.push(rng.normal(0, 1))
    X.push(row.slice(0, p))
    y.push(rng.next() < flipY ? 1 - k : k)
  }
  return { X, y }
}

/** Friedman #1, the regression problem the learning-rate curves are drawn on:
 *  five columns matter, the rest are decoys. */
export function friedman1(n = 250, noise = 1.0, seed = 0, p = 7) {
  const rng = new Rng(seed + 4)
  const X: number[][] = []
  const y: number[] = []
  for (let i = 0; i < n; i++) {
    const row: number[] = []
    for (let j = 0; j < p; j++) row.push(rng.uniform())
    X.push(row)
    y.push(
      10 * Math.sin(Math.PI * row[0] * row[1]) +
        20 * (row[2] - 0.5) ** 2 +
        10 * row[3] +
        5 * row[4] +
        rng.normal(0, noise),
    )
  }
  return { X, y }
}

/** A deterministic train/test split, sklearn's train_test_split with a seed. */
export function split<T extends { X: number[][]; y: number[] }>(
  d: T,
  testSize = 0.5,
  seed = 0,
): { Xtr: number[][]; ytr: number[]; Xte: number[][]; yte: number[] } {
  const rng = new Rng(seed + 5)
  const order = d.X.map((_, i) => i)
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(rng.next() * (i + 1))
    const t = order[i]
    order[i] = order[j]
    order[j] = t
  }
  const nTe = Math.round(testSize * order.length)
  const te = order.slice(0, nTe)
  const tr = order.slice(nTe)
  return {
    Xtr: tr.map((i) => d.X[i]),
    ytr: tr.map((i) => d.y[i]),
    Xte: te.map((i) => d.X[i]),
    yte: te.map((i) => d.y[i]),
  }
}

/** Bootstrap resample of a dataset: the instability slide's three panels. */
export function resample(d: Dataset, seed: number): Dataset {
  const rng = new Rng(seed + 6)
  const X: number[][] = []
  const y: number[] = []
  for (let i = 0; i < d.X.length; i++) {
    const j = Math.floor(rng.next() * d.X.length)
    X.push(d.X[j])
    y.push(d.y[j])
  }
  return { X, y }
}

/** Fine structure on one side, one easy rule on the other: the dataset where
 *  level-wise and leaf-wise growth genuinely part company, because one half of
 *  the space keeps paying for splits long after the other has stopped. */
export function staircase(n = 400, seed = 2): Dataset {
  const rng = new Rng(seed + 8)
  const X: number[][] = []
  const y: number[] = []
  for (let i = 0; i < n; i++) {
    const a = rng.uniform()
    const b = rng.uniform()
    X.push([a, b])
    y.push(a < 0.5 ? Math.floor(a * 12) % 2 : b > 0.7 ? 1 : 0)
  }
  return { X, y }
}
