// Random forests: bootstrap the rows, draw max_features columns at every node,
// then average. Nothing else; the whole point of the section is that these two
// injections of randomness are all there is.
import { Rng } from './rng'
import { Tree, fitTree, fitTreeReg } from './tree'

export interface ForestOpts {
  nTrees?: number
  maxDepth?: number
  maxFeatures?: number
  minSamplesLeaf?: number
  seed?: number
  bootstrap?: boolean
}

export interface Forest {
  trees: Tree[]
  /** out-of-bag row mask per tree, for the OOB readouts */
  oob: boolean[][]
  predict(x: number[]): number[]
  /** the average of the first `m` trees only: what the M slider shows */
  predictUpTo(x: number[], m: number): number[]
}

function bootstrapIdx(n: number, rng: Rng): number[] {
  const idx = new Array(n)
  for (let i = 0; i < n; i++) idx[i] = Math.floor(rng.next() * n)
  return idx
}

export function fitForest(X: number[][], y: number[], o: ForestOpts = {}): Forest {
  const nTrees = o.nTrees ?? 100
  const n = X.length
  const nClasses = Math.max(2, Math.max(...y) + 1)
  const rng = new Rng(o.seed ?? 0)
  const trees: Tree[] = []
  const oob: boolean[][] = []
  for (let m = 0; m < nTrees; m++) {
    const idx = o.bootstrap === false ? X.map((_, i) => i) : bootstrapIdx(n, rng)
    const seen = new Array(n).fill(false)
    for (const i of idx) seen[i] = true
    oob.push(seen.map((v) => !v))
    // each tree gets its own stream, so tree m is the same whatever M is
    trees.push(
      fitTree(idx.map((i) => X[i]), idx.map((i) => y[i]), {
        maxDepth: o.maxDepth ?? Infinity,
        maxFeatures: o.maxFeatures,
        minSamplesLeaf: o.minSamplesLeaf ?? 1,
        seed: (o.seed ?? 0) * 7919 + m + 1,
      }),
    )
  }
  const avg = (x: number[], m: number) => {
    const out = new Array(nClasses).fill(0)
    const k = Math.max(1, Math.min(m, trees.length))
    for (let t = 0; t < k; t++) {
      const p = trees[t].predict(x)
      for (let c = 0; c < nClasses; c++) out[c] += (p[c] ?? 0) / k
    }
    return out
  }
  return {
    trees,
    oob,
    predict: (x) => avg(x, trees.length),
    predictUpTo: (x, m) => avg(x, m),
  }
}

export function forestReg(X: number[][], y: number[], o: ForestOpts = {}) {
  const nTrees = o.nTrees ?? 100
  const rng = new Rng(o.seed ?? 0)
  const trees: Tree[] = []
  for (let m = 0; m < nTrees; m++) {
    const idx = o.bootstrap === false ? X.map((_, i) => i) : bootstrapIdx(X.length, rng)
    trees.push(
      fitTreeReg(idx.map((i) => X[i]), idx.map((i) => y[i]), {
        maxDepth: o.maxDepth ?? Infinity,
        maxFeatures: o.maxFeatures,
        minSamplesLeaf: o.minSamplesLeaf ?? 1,
        seed: (o.seed ?? 0) * 7919 + m + 1,
      }),
    )
  }
  return {
    trees,
    predict: (x: number[]) =>
      trees.reduce((s, t) => s + t.predict(x)[0], 0) / trees.length,
  }
}

export function vote(p: number[]): number {
  let arg = 0
  for (let k = 1; k < p.length; k++) if (p[k] > p[arg]) arg = k
  return arg
}

export function forestAccuracy(f: Forest, X: number[][], y: number[], m?: number) {
  let ok = 0
  for (let i = 0; i < X.length; i++)
    if (vote(f.predictUpTo(X[i], m ?? f.trees.length)) === y[i]) ok++
  return ok / X.length
}

/** Mean pairwise correlation of the trees' predictions: the rho of the
 *  variance formula, measured rather than asserted. */
export function treeCorrelation(f: Forest, X: number[][]): number {
  const preds = f.trees.map((t) => X.map((x) => vote(t.predict(x))))
  const M = preds.length
  const centred = preds.map((p) => {
    const mu = p.reduce((a, b) => a + b, 0) / p.length
    const c = p.map((v) => v - mu)
    const sd = Math.sqrt(c.reduce((a, b) => a + b * b, 0) / c.length) || 1e-12
    return c.map((v) => v / sd)
  })
  let s = 0
  let k = 0
  for (let a = 0; a < M; a++)
    for (let b = a + 1; b < M; b++) {
      let d = 0
      for (let i = 0; i < X.length; i++) d += centred[a][i] * centred[b][i]
      s += d / X.length
      k++
    }
  return k ? s / k : 0
}

/** Error of the average single tree of the forest. */
export function soloError(f: Forest, X: number[][], y: number[]): number {
  let s = 0
  for (const t of f.trees) {
    let bad = 0
    for (let i = 0; i < X.length; i++) if (vote(t.predict(X[i])) !== y[i]) bad++
    s += bad / X.length
  }
  return s / f.trees.length
}

/** Var(mean of M trees) / sigma^2, the formula of the eq_forest_variance slide. */
export function varianceOfAverage(M: number, rho: number): number {
  return 1 / M + ((M - 1) / M) * rho
}

/** How many independent trees M correlated ones are worth. */
export function effectiveTrees(M: number, rho: number): number {
  return M / (1 + (M - 1) * rho)
}
