// CART, the one algorithm the whole deck is built on: a greedy axis-aligned
// split search, recursed until a stopping rule fires. Classification and
// regression share the search; they differ only in what a node's impurity and
// its prediction are.
//
// Deliberately the same conventions as sklearn's DecisionTree*, so a slide can
// be checked against the printed figure it mirrors:
//   - a split is "x[f] <= t", t the midpoint of two consecutive sorted values;
//   - candidate features are drawn without replacement at EVERY node;
//   - the best split must beat the incumbent strictly, and features are
//     visited in a shuffled order, which is how ties get broken.
import { Rng } from './rng'

export type Criterion = 'gini' | 'entropy' | 'misclass'

export interface TreeOpts {
  maxDepth?: number
  minSamplesLeaf?: number
  minSamplesSplit?: number
  /** columns drawn per node; everything when absent (a plain CART) */
  maxFeatures?: number
  criterion?: Criterion
  seed?: number
  /** sample weights, as boosting's row subsampling needs */
  weights?: number[]
}

export interface Node {
  /** mean (regression) or class probabilities (classification) */
  value: number[]
  n: number
  impurity: number
  feature?: number
  threshold?: number
  left?: Node
  right?: Node
}

export interface Tree {
  root: Node
  nLeaves: number
  depth: number
  /** class probabilities, or [mean] for a regression tree */
  predict(x: number[]): number[]
  /** the leaf a row lands in, for the slides that follow one row */
  leafOf(x: number[]): Node
}

// --------------------------------------------------------------- impurity
export function gini(counts: number[], n: number): number {
  if (!n) return 0
  let s = 0
  for (const c of counts) s += (c / n) ** 2
  return 1 - s
}

export function entropy(counts: number[], n: number): number {
  if (!n) return 0
  let s = 0
  for (const c of counts) {
    const p = c / n
    if (p > 0) s -= p * Math.log2(p)
  }
  return s
}

export function misclass(counts: number[], n: number): number {
  if (!n) return 0
  return 1 - Math.max(...counts) / n
}

export function impurityOf(counts: number[], n: number, crit: Criterion): number {
  return crit === 'gini' ? gini(counts, n) : crit === 'entropy' ? entropy(counts, n) : misclass(counts, n)
}

/** Gini of a 0/1 label vector: the 2p(1-p) the printed deck writes. */
export function gini01(y: number[]): number {
  if (!y.length) return 0
  let p = 0
  for (const v of y) p += v
  p /= y.length
  return 2 * p * (1 - p)
}

// ----------------------------------------------------------- the split scan
export interface Split {
  feature: number
  threshold: number
  /** weighted impurity of the two children */
  score: number
  gain: number
}

interface Problem {
  X: number[][]
  /** class index per row (classification) or target (regression) */
  y: number[]
  w: number[]
  nClasses: number
  regression: boolean
  crit: Criterion
}

/** Weighted impurity after splitting rows `idx` of feature `f` at every
 *  midpoint: the curve the "choosing the split" slide draws. */
export function scanFeature(
  X: number[][],
  y: number[],
  f: number,
  crit: Criterion = 'gini',
  nClasses = 2,
): { thresholds: number[]; scores: number[] } {
  const idx = X.map((_, i) => i).sort((a, b) => X[a][f] - X[b][f])
  const total = new Array(nClasses).fill(0)
  for (const i of idx) total[y[i]]++
  const left = new Array(nClasses).fill(0)
  const thresholds: number[] = []
  const scores: number[] = []
  const n = idx.length
  for (let k = 0; k < n - 1; k++) {
    left[y[idx[k]]]++
    const a = X[idx[k]][f]
    const b = X[idx[k + 1]][f]
    if (b <= a) continue
    const nl = k + 1
    const right = total.map((c, j) => c - left[j])
    thresholds.push((a + b) / 2)
    scores.push(
      (nl / n) * impurityOf(left, nl, crit) +
        ((n - nl) / n) * impurityOf(right, n - nl, crit),
    )
  }
  return { thresholds, scores }
}

function bestSplit(
  p: Problem,
  sorted: number[][],
  features: number[],
): Split | null {
  let best: Split | null = null
  const { X, y, w, nClasses, regression, crit } = p
  const idx = sorted[0]

  // the parent's totals, so each candidate costs one running update
  let wTot = 0
  const totC = new Array(regression ? 0 : nClasses).fill(0)
  let totSum = 0
  let totSq = 0
  for (const i of idx) {
    wTot += w[i]
    if (regression) {
      totSum += w[i] * y[i]
      totSq += w[i] * y[i] * y[i]
    } else totC[y[i]] += w[i]
  }
  const parent = regression
    ? totSq / wTot - (totSum / wTot) ** 2
    : impurityOf(totC, wTot, crit)

  for (const f of features) {
    const order = sorted[f]
    let wl = 0
    let sumL = 0
    let sqL = 0
    const cl = new Array(regression ? 0 : nClasses).fill(0)
    for (let k = 0; k < order.length - 1; k++) {
      const i = order[k]
      wl += w[i]
      if (regression) {
        sumL += w[i] * y[i]
        sqL += w[i] * y[i] * y[i]
      } else cl[y[i]] += w[i]
      const a = X[i][f]
      const b = X[order[k + 1]][f]
      if (b <= a) continue
      const wr = wTot - wl
      if (!wl || !wr) continue
      let score: number
      if (regression) {
        const vl = sqL / wl - (sumL / wl) ** 2
        const sumR = totSum - sumL
        const sqR = totSq - sqL
        const vr = sqR / wr - (sumR / wr) ** 2
        score = (wl / wTot) * Math.max(0, vl) + (wr / wTot) * Math.max(0, vr)
      } else {
        const cr = totC.map((c, j) => c - cl[j])
        score =
          (wl / wTot) * impurityOf(cl, wl, crit) +
          (wr / wTot) * impurityOf(cr, wr, crit)
      }
      if (!best || score < best.score - 1e-12) {
        best = { feature: f, threshold: (a + b) / 2, score, gain: parent - score }
      }
    }
  }
  return best && best.gain > 1e-12 ? best : null
}

function build(
  p: Problem,
  sorted: number[][],
  depth: number,
  o: Required<Pick<TreeOpts, 'maxDepth' | 'minSamplesLeaf' | 'minSamplesSplit'>> & {
    maxFeatures: number
  },
  rng: Rng,
  stats: { leaves: number; depth: number },
): Node {
  const { X, y, w, nClasses, regression, crit } = p
  const idx = sorted[0]
  let wTot = 0
  for (const i of idx) wTot += w[i]
  let value: number[]
  let impurity: number
  if (regression) {
    let s = 0
    let sq = 0
    for (const i of idx) {
      s += w[i] * y[i]
      sq += w[i] * y[i] * y[i]
    }
    value = [s / wTot]
    impurity = Math.max(0, sq / wTot - value[0] ** 2)
  } else {
    const c = new Array(nClasses).fill(0)
    for (const i of idx) c[y[i]] += w[i]
    value = c.map((v) => v / wTot)
    impurity = impurityOf(c, wTot, crit)
  }
  const node: Node = { value, n: idx.length, impurity }

  const pure = impurity <= 1e-12
  if (depth >= o.maxDepth || idx.length < o.minSamplesSplit || pure) {
    stats.leaves++
    stats.depth = Math.max(stats.depth, depth)
    return node
  }

  const nf = X[0].length
  const features = drawFeatures(nf, o.maxFeatures, rng)
  const split = bestSplit(p, sorted, features)
  if (!split) {
    stats.leaves++
    stats.depth = Math.max(stats.depth, depth)
    return node
  }
  // the split partitions every sorted column while keeping it sorted, so no
  // node ever has to sort again
  const goesLeft = (i: number) => X[i][split.feature] <= split.threshold
  const nL = idx.reduce((s, i) => s + (goesLeft(i) ? 1 : 0), 0)
  if (nL < o.minSamplesLeaf || idx.length - nL < o.minSamplesLeaf) {
    stats.leaves++
    stats.depth = Math.max(stats.depth, depth)
    return node
  }
  const sL: number[][] = []
  const sR: number[][] = []
  for (const col of sorted) {
    const l: number[] = []
    const r: number[] = []
    for (const i of col) (goesLeft(i) ? l : r).push(i)
    sL.push(l)
    sR.push(r)
  }
  node.feature = split.feature
  node.threshold = split.threshold
  node.left = build(p, sL, depth + 1, o, rng, stats)
  node.right = build(p, sR, depth + 1, o, rng, stats)
  return node
}

/** `k` columns out of `nf`, drawn without replacement: a fresh draw per node. */
function drawFeatures(nf: number, k: number, rng: Rng): number[] {
  const all = new Array(nf)
  for (let i = 0; i < nf; i++) all[i] = i
  for (let i = nf - 1; i > 0; i--) {
    const j = Math.floor(rng.next() * (i + 1))
    const t = all[i]
    all[i] = all[j]
    all[j] = t
  }
  return k >= nf ? all : all.slice(0, k)
}

/** Row indices sorted by each column, once per fit. */
function presort(X: number[][]): number[][] {
  const nf = X[0].length
  const base = X.map((_, i) => i)
  const out: number[][] = []
  for (let f = 0; f < nf; f++) out.push(base.slice().sort((a, b) => X[a][f] - X[b][f]))
  return out
}

function wrap(root: Node, stats: { leaves: number; depth: number }): Tree {
  const leafOf = (x: number[]): Node => {
    let node = root
    while (node.left) node = x[node.feature!] <= node.threshold! ? node.left : node.right!
    return node
  }
  return {
    root,
    nLeaves: stats.leaves,
    depth: stats.depth,
    predict: (x) => leafOf(x).value,
    leafOf,
  }
}

export function fitTree(X: number[][], y: number[], opts: TreeOpts = {}): Tree {
  const nClasses = Math.max(2, Math.max(...y) + 1)
  const n = X.length
  const p: Problem = {
    X, y,
    w: opts.weights ?? new Array(n).fill(1),
    nClasses,
    regression: false,
    crit: opts.criterion ?? 'gini',
  }
  const stats = { leaves: 0, depth: 0 }
  const root = build(p, presort(X), 0, {
    maxDepth: opts.maxDepth ?? Infinity,
    minSamplesLeaf: opts.minSamplesLeaf ?? 1,
    minSamplesSplit: opts.minSamplesSplit ?? 2,
    maxFeatures: opts.maxFeatures ?? X[0].length,
  }, new Rng(opts.seed ?? 0), stats)
  return wrap(root, stats)
}

export function fitTreeReg(X: number[][], y: number[], opts: TreeOpts = {}): Tree {
  const n = X.length
  const p: Problem = {
    X, y,
    w: opts.weights ?? new Array(n).fill(1),
    nClasses: 1,
    regression: true,
    crit: 'gini',
  }
  const stats = { leaves: 0, depth: 0 }
  const root = build(p, presort(X), 0, {
    maxDepth: opts.maxDepth ?? Infinity,
    minSamplesLeaf: opts.minSamplesLeaf ?? 1,
    minSamplesSplit: opts.minSamplesSplit ?? 2,
    maxFeatures: opts.maxFeatures ?? X[0].length,
  }, new Rng(opts.seed ?? 0), stats)
  return wrap(root, stats)
}

/** P(y = 1 | x), the field every classification panel shades. */
export function proba1(t: Tree, x: number, y: number): number {
  return t.predict([x, y])[1] ?? 0
}

export function accuracy(t: Tree, X: number[][], y: number[]): number {
  let ok = 0
  for (let i = 0; i < X.length; i++) {
    const p = t.predict(X[i])
    let arg = 0
    for (let k = 1; k < p.length; k++) if (p[k] > p[arg]) arg = k
    if (arg === y[i]) ok++
  }
  return ok / X.length
}

/** All the leaf rectangles of a 2D tree, for the "every leaf is a box" slide. */
export function leafBoxes(
  t: Tree,
  domain: [number, number, number, number],
): { x0: number; x1: number; y0: number; y1: number; node: Node }[] {
  const out: { x0: number; x1: number; y0: number; y1: number; node: Node }[] = []
  const walk = (node: Node, x0: number, x1: number, y0: number, y1: number) => {
    if (!node.left) {
      out.push({ x0, x1, y0, y1, node })
      return
    }
    const t_ = node.threshold!
    if (node.feature === 0) {
      walk(node.left, x0, Math.min(x1, t_), y0, y1)
      walk(node.right!, Math.max(x0, t_), x1, y0, y1)
    } else {
      walk(node.left, x0, x1, y0, Math.min(y1, t_))
      walk(node.right!, x0, x1, Math.max(y0, t_), y1)
    }
  }
  walk(t.root, domain[0], domain[1], domain[2], domain[3])
  return out
}
