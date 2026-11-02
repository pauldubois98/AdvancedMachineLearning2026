// Gradient boosting, the way the lecture tells it: start from a constant, fit
// the next tree to the negative gradient of the loss at the current prediction,
// and add a fraction eta of it.
//
// Squared loss makes the gradient the plain residual, so the trees are fitted
// to residuals and used as they come. Log loss needs the Newton step sklearn
// also takes: the tree chooses the PARTITION on the residuals, then each leaf
// value is replaced by sum(g)/sum(h) over its rows.
import { Node, Tree, fitTreeReg } from './tree'

export type Loss = 'squared' | 'log'

export interface BoostOpts {
  nTrees?: number
  eta?: number
  maxDepth?: number
  minSamplesLeaf?: number
  loss?: Loss
  seed?: number
  /** rows drawn per tree, as a fraction (sklearn's subsample) */
  subsample?: number
}

export interface Booster {
  f0: number
  eta: number
  loss: Loss
  trees: Tree[]
  /** F_m(x); m defaults to every tree */
  raw(x: number[], m?: number): number
  /** sigma(F) for log loss, F itself for squared loss */
  predict(x: number[], m?: number): number
  /** F_m for every row and every stage: rows of length nTrees + 1 */
  stages(X: number[][]): Float64Array[]
}

const sigmoid = (z: number) => 1 / (1 + Math.exp(-z))

/** Replace every leaf value by the Newton step over its own rows. */
function newtonLeaves(t: Tree, X: number[][], g: number[], h: number[], rows: number[]) {
  const bucket = new Map<Node, number[]>()
  for (const i of rows) {
    const leaf = t.leafOf(X[i])
    const arr = bucket.get(leaf)
    if (arr) arr.push(i)
    else bucket.set(leaf, [i])
  }
  for (const [leaf, idx] of bucket) {
    let gs = 0
    let hs = 0
    for (const i of idx) {
      gs += g[i]
      hs += h[i]
    }
    leaf.value = [hs > 1e-12 ? gs / hs : 0]
  }
}

export function fitBooster(X: number[][], y: number[], o: BoostOpts = {}): Booster {
  const nTrees = o.nTrees ?? 100
  const eta = o.eta ?? 0.1
  const loss: Loss = o.loss ?? 'squared'
  const n = X.length
  const mean = y.reduce((a, b) => a + b, 0) / n
  const f0 = loss === 'squared' ? mean : Math.log(Math.max(1e-9, mean) / Math.max(1e-9, 1 - mean))
  const F = new Array(n).fill(f0)
  const trees: Tree[] = []
  const rows = X.map((_, i) => i)

  for (let m = 0; m < nTrees; m++) {
    const g = new Array(n)
    const h = new Array(n)
    for (let i = 0; i < n; i++) {
      if (loss === 'squared') {
        g[i] = y[i] - F[i]
        h[i] = 1
      } else {
        const p = sigmoid(F[i])
        g[i] = y[i] - p
        h[i] = Math.max(1e-6, p * (1 - p))
      }
    }
    const t = fitTreeReg(X, g, {
      maxDepth: o.maxDepth ?? 3,
      minSamplesLeaf: o.minSamplesLeaf ?? 1,
      seed: (o.seed ?? 0) + m + 1,
    })
    if (loss === 'log') newtonLeaves(t, X, g, h, rows)
    for (let i = 0; i < n; i++) F[i] += eta * t.predict(X[i])[0]
    trees.push(t)
  }

  const raw = (x: number[], m?: number) => {
    const k = m === undefined ? trees.length : Math.max(0, Math.min(m, trees.length))
    let s = f0
    for (let t = 0; t < k; t++) s += eta * trees[t].predict(x)[0]
    return s
  }
  return {
    f0, eta, loss, trees, raw,
    predict: (x, m) => (loss === 'log' ? sigmoid(raw(x, m)) : raw(x, m)),
    stages(Xs: number[][]) {
      const out: Float64Array[] = []
      const cur = new Float64Array(Xs.length).fill(f0)
      out.push(cur.slice())
      for (const t of trees) {
        for (let i = 0; i < Xs.length; i++) cur[i] += eta * t.predict(Xs[i])[0]
        out.push(cur.slice())
      }
      return out
    },
  }
}

/** One round, exposed on its own: the stages slide needs the residuals and the
 *  tree that was fitted to them, not just the sum. */
export interface Round {
  residual: number[]
  tree: Tree
  /** F after this round, at the training rows */
  F: number[]
}

export function boostRounds(
  X: number[][],
  y: number[],
  o: BoostOpts = {},
): { f0: number; rounds: Round[] } {
  const nTrees = o.nTrees ?? 4
  const eta = o.eta ?? 0.8
  const n = X.length
  const f0 = o.loss === 'log' ? 0 : y.reduce((a, b) => a + b, 0) / n
  let F = new Array(n).fill(f0)
  const rounds: Round[] = []
  for (let m = 0; m < nTrees; m++) {
    const r = F.map((f, i) => y[i] - f)
    const tree = fitTreeReg(X, r, {
      maxDepth: o.maxDepth ?? 2,
      minSamplesLeaf: o.minSamplesLeaf ?? 1,
      seed: (o.seed ?? 0) + m + 1,
    })
    const next = F.map((f, i) => f + eta * tree.predict(X[i])[0])
    rounds.push({ residual: r, tree, F: next })
    F = next
  }
  return { f0, rounds }
}

export function mse(pred: number[], y: number[]): number {
  let s = 0
  for (let i = 0; i < y.length; i++) s += (y[i] - pred[i]) ** 2
  return s / y.length
}

export function errorRate(F: ArrayLike<number>, y: number[]): number {
  let bad = 0
  for (let i = 0; i < y.length; i++) if ((F[i] > 0 ? 1 : 0) !== y[i]) bad++
  return bad / y.length
}
