// The three libraries' specifics: the second-order objective XGBoost scores a
// split with, LightGBM's histograms, leaf-wise growth and GOSS, and CatBoost's
// target statistics. Everything here works on (g, h) pairs, which is the only
// thing a gradient-boosted tree ever sees of the loss.
import { Rng } from './rng'

export const LAM = 1.0
export const GAM = 0.5

/** s(G, H) = G^2 / (H + lambda): the score of a set of rows. */
export function score(G: number, H: number, lambda = LAM): number {
  return (G * G) / (H + lambda)
}

/** The optimal value of leaf j, and the number its objective collapses to. */
export function leafValue(G: number, H: number, lambda = LAM): number {
  return -G / (H + lambda)
}

export function leafObjective(G: number, H: number, lambda = LAM, gamma = GAM): number {
  return -0.5 * score(G, H, lambda) + gamma
}

export function gainOf(
  GL: number, HL: number, GR: number, HR: number,
  lambda = LAM, gamma = GAM,
): number {
  return (
    0.5 * (score(GL, HL, lambda) + score(GR, HR, lambda) + -score(GL + GR, HL + HR, lambda)) -
    gamma
  )
}

/** The 40-row node the XGBoost and LightGBM slides share, so the numbers on
 *  one slide are the numbers on the next. Log loss at the very first tree:
 *  every prediction is 0.5, so g is +-0.5 and h is 0.25 for every row. */
export function splitDemo(n = 40, seed = 4) {
  const rng = new Rng(seed)
  const X: number[][] = []
  for (let i = 0; i < n; i++) X.push([rng.uniform(), rng.uniform(), rng.uniform()])
  const y = X.map((r) => (r[0] > 0.55 ? 1 : 0))
  // a little label noise, so the scan has something to trade off
  const order = X.map((_, i) => i)
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(rng.next() * (i + 1))
    const t = order[i]
    order[i] = order[j]
    order[j] = t
  }
  for (const i of order.slice(0, 5)) y[i] = 1 - y[i]
  const g = y.map((v) => 0.5 - v)
  const h = y.map(() => 0.25)
  return { X, y, g, h }
}

/** Every midpoint of one feature, with the gain that split would buy. */
export function exactScan(
  xs: number[], g: number[], h: number[],
  lambda = LAM, gamma = GAM,
): { cuts: number[]; gains: number[] } {
  const idx = xs.map((_, i) => i).sort((a, b) => xs[a] - xs[b])
  const G = g.reduce((a, b) => a + b, 0)
  const H = h.reduce((a, b) => a + b, 0)
  let GL = 0
  let HL = 0
  const cuts: number[] = []
  const gains: number[] = []
  for (let k = 0; k < idx.length - 1; k++) {
    GL += g[idx[k]]
    HL += h[idx[k]]
    const a = xs[idx[k]]
    const b = xs[idx[k + 1]]
    if (b <= a) continue
    cuts.push((a + b) / 2)
    gains.push(gainOf(GL, HL, G - GL, H - HL, lambda, gamma))
  }
  return { cuts, gains }
}

/** Gain of "x < cut" at an arbitrary list of cuts, weights included (GOSS). */
export function gainAt(
  xs: number[], g: number[], h: number[], cuts: number[],
  lambda = LAM, gamma = GAM,
): number[] {
  const G = g.reduce((a, b) => a + b, 0)
  const H = h.reduce((a, b) => a + b, 0)
  return cuts.map((c) => {
    let GL = 0
    let HL = 0
    for (let i = 0; i < xs.length; i++)
      if (xs[i] < c) {
        GL += g[i]
        HL += h[i]
      }
    return gainOf(GL, HL, G - GL, H - HL, lambda, gamma)
  })
}

// ------------------------------------------------------------- histograms
export interface Bins {
  edges: number[]
  /** bin index per row */
  idx: number[]
  /** per-bin sums, the three numbers LightGBM stores */
  sumG: number[]
  sumH: number[]
  count: number[]
}

export function binFeature(xs: number[], g: number[], h: number[], nBins: number): Bins {
  const lo = 0
  const hi = 1
  const edges: number[] = []
  for (let b = 0; b <= nBins; b++) edges.push(lo + ((hi - lo) * b) / nBins)
  const sumG = new Array(nBins).fill(0)
  const sumH = new Array(nBins).fill(0)
  const count = new Array(nBins).fill(0)
  const idx = xs.map((v) => {
    let b = Math.floor(((v - lo) / (hi - lo)) * nBins)
    b = Math.max(0, Math.min(nBins - 1, b))
    return b
  })
  for (let i = 0; i < xs.length; i++) {
    sumG[idx[i]] += g[i]
    sumH[idx[i]] += h[i]
    count[idx[i]]++
  }
  return { edges, idx, sumG, sumH, count }
}

/** Running totals over the bins: every candidate split is one column of these. */
export function prefix(bins: Bins) {
  const cg: number[] = []
  const ch: number[] = []
  let a = 0
  let b = 0
  for (let k = 0; k < bins.sumG.length; k++) {
    a += bins.sumG[k]
    b += bins.sumH[k]
    cg.push(a)
    ch.push(b)
  }
  return { cg, ch, G: a, H: b }
}

// -------------------------------------------------------------------- GOSS
export function goss(g: number[], a: number, b: number, seed = 7) {
  const n = g.length
  const rng = new Rng(seed)
  const order = g.map((_, i) => i).sort((p, q) => Math.abs(g[q]) - Math.abs(g[p]))
  const nTop = Math.max(1, Math.round(a * n))
  const top = order.slice(0, nTop)
  const rest = order.slice(nTop)
  for (let i = rest.length - 1; i > 0; i--) {
    const j = Math.floor(rng.next() * (i + 1))
    const t = rest[i]
    rest[i] = rest[j]
    rest[j] = t
  }
  const samp = rest.slice(0, Math.max(1, Math.round(b * rest.length)))
  const keep = top.concat(samp)
  const amp = b > 0 ? (1 - a) / b : 1
  const w = keep.map((_, i) => (i < nTop ? 1 : amp))
  return { keep, w, nTop, amp, sorted: order }
}

// --------------------------------------------------- target statistics
export function catDemo(n = 600, levels = 200, seed = 5) {
  const rng = new Rng(seed)
  const cat: number[] = []
  for (let i = 0; i < n; i++) cat.push(i % levels)
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(rng.next() * (i + 1))
    const t = cat[i]
    cat[i] = cat[j]
    cat[j] = t
  }
  // the label is a coin flip: the category carries NO signal, by construction
  const y = cat.map(() => (rng.next() < 0.5 ? 1 : 0))
  const catTe: number[] = []
  const yTe: number[] = []
  for (let i = 0; i < n; i++) {
    catTe.push(Math.floor(rng.next() * levels))
    yTe.push(rng.next() < 0.5 ? 1 : 0)
  }
  return { cat, y, catTe, yTe }
}

/** Mean target per category over ALL rows: the row's own label included. */
export function greedyTs(cat: number[], y: number[], levels: number, a = 0): number[] {
  const tot = new Array(levels).fill(0)
  const cnt = new Array(levels).fill(0)
  for (let i = 0; i < cat.length; i++) {
    tot[cat[i]] += y[i]
    cnt[cat[i]]++
  }
  const prior = y.reduce((s, v) => s + v, 0) / y.length
  return tot.map((t, c) => (cnt[c] + a > 0 ? (t + a * prior) / (cnt[c] + a) : prior))
}

/** CatBoost's ordered target statistic: only the rows before this one count. */
export function orderedTs(
  cat: number[], y: number[], levels: number, a = 1, seed = 0,
): { enc: number[]; order: number[] } {
  const rng = new Rng(seed + 1)
  const order = cat.map((_, i) => i)
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(rng.next() * (i + 1))
    const t = order[i]
    order[i] = order[j]
    order[j] = t
  }
  const prior = y.reduce((s, v) => s + v, 0) / y.length
  const tot = new Array(levels).fill(0)
  const cnt = new Array(levels).fill(0)
  const enc = new Array(cat.length).fill(prior)
  for (const i of order) {
    const c = cat[i]
    enc[i] = (tot[c] + a * prior) / (cnt[c] + a)
    tot[c] += y[i] // the row joins the history only after it is encoded
    cnt[c] += 1
  }
  return { enc, order }
}

export function correlation(a: number[], b: number[]): number {
  const n = a.length
  const ma = a.reduce((s, v) => s + v, 0) / n
  const mb = b.reduce((s, v) => s + v, 0) / n
  let sab = 0
  let sa = 0
  let sb = 0
  for (let i = 0; i < n; i++) {
    sab += (a[i] - ma) * (b[i] - mb)
    sa += (a[i] - ma) ** 2
    sb += (b[i] - mb) ** 2
  }
  return sab / Math.sqrt((sa || 1e-12) * (sb || 1e-12))
}

/** Share of y = 1 among the rows whose encoding falls in each bucket: what a
 *  tree would actually exploit, and what a leak-free feature keeps flat. */
export function encodingRate(enc: number[], y: number[], nBuckets = 5) {
  const out: { at: number; rate: number; n: number }[] = []
  for (let b = 0; b < nBuckets; b++) {
    const lo = b / nBuckets
    const hi = (b + 1) / nBuckets
    const rows = enc.map((_, i) => i).filter((i) => enc[i] >= lo && (enc[i] < hi || (b === nBuckets - 1 && enc[i] <= hi)))
    if (!rows.length) continue
    out.push({
      at: rows.reduce((s, i) => s + enc[i], 0) / rows.length,
      rate: rows.reduce((s, i) => s + y[i], 0) / rows.length,
      n: rows.length,
    })
  }
  return out
}

// ------------------------------------------- level-wise vs leaf-wise growth
export interface GbmNode {
  id: number
  rows: number[]
  G: number
  H: number
  depth: number
  /** filled when the node was split */
  feature?: number
  threshold?: number
  gain?: number
  order?: number
  left?: GbmNode
  right?: GbmNode
}

export interface GrownTree {
  root: GbmNode
  leaves: GbmNode[]
  /** the splits in the order the policy made them */
  splits: GbmNode[]
  predict(x: number[]): number
}

/** Grow a second-order tree under a budget of leaves, either level-wise
 *  (finish a level before starting the next) or leaf-wise (always split the
 *  leaf that offers the most, anywhere in the tree). Same candidates and the
 *  same gain in both: only the queue differs. */
export function growTree(
  X: number[][], g: number[], h: number[],
  opts: {
    mode: 'level' | 'leaf'
    maxLeaves: number
    maxDepth?: number
    lambda?: number
    gamma?: number
    minRows?: number
  },
): GrownTree {
  const lambda = opts.lambda ?? LAM
  const gamma = opts.gamma ?? GAM
  const minRows = opts.minRows ?? 5
  const maxDepth = opts.maxDepth ?? 12
  let nextId = 0
  const mk = (rows: number[], depth: number): GbmNode => ({
    id: nextId++,
    rows,
    G: rows.reduce((s, i) => s + g[i], 0),
    H: rows.reduce((s, i) => s + h[i], 0),
    depth,
  })

  const best = (node: GbmNode) => {
    let out: { feature: number; threshold: number; gain: number } | null = null
    for (let f = 0; f < X[0].length; f++) {
      const idx = node.rows.slice().sort((a, b) => X[a][f] - X[b][f])
      let GL = 0
      let HL = 0
      for (let k = 0; k < idx.length - 1; k++) {
        GL += g[idx[k]]
        HL += h[idx[k]]
        const a = X[idx[k]][f]
        const b = X[idx[k + 1]][f]
        if (b <= a) continue
        if (k + 1 < minRows || idx.length - k - 1 < minRows) continue
        const gn = gainOf(GL, HL, node.G - GL, node.H - HL, lambda, gamma)
        if (!out || gn > out.gain) out = { feature: f, threshold: (a + b) / 2, gain: gn }
      }
    }
    return out
  }

  const root = mk(X.map((_, i) => i), 0)
  const leaves: GbmNode[] = [root]
  const cand = new Map<number, { feature: number; threshold: number; gain: number } | null>()
  cand.set(root.id, best(root))
  const splits: GbmNode[] = []

  while (leaves.length < opts.maxLeaves) {
    const open = leaves.filter(
      (l) => l.depth < maxDepth && (cand.get(l.id)?.gain ?? -Infinity) > 0,
    )
    if (!open.length) break
    let pick: GbmNode
    if (opts.mode === 'leaf') {
      pick = open.reduce((a, b) => (cand.get(b.id)!.gain > cand.get(a.id)!.gain ? b : a))
    } else {
      // shallowest first, and left to right inside a level
      const d = Math.min(...open.map((l) => l.depth))
      pick = open.filter((l) => l.depth === d).reduce((a, b) => (b.id < a.id ? b : a))
    }
    const c = cand.get(pick.id)!
    pick.feature = c.feature
    pick.threshold = c.threshold
    pick.gain = c.gain
    pick.order = splits.length + 1
    const L: number[] = []
    const R: number[] = []
    for (const i of pick.rows) (X[i][c.feature] <= c.threshold ? L : R).push(i)
    pick.left = mk(L, pick.depth + 1)
    pick.right = mk(R, pick.depth + 1)
    leaves.splice(leaves.indexOf(pick), 1, pick.left, pick.right)
    cand.set(pick.left.id, best(pick.left))
    cand.set(pick.right.id, best(pick.right))
    splits.push(pick)
  }

  const predict = (x: number[]) => {
    let node = root
    while (node.left) node = x[node.feature!] <= node.threshold! ? node.left : node.right!
    return leafValue(node.G, node.H, lambda)
  }
  return { root, leaves, splits, predict }
}

/** Total objective of a grown tree: what the two growth policies are judged by. */
export function treeObjective(t: GrownTree, lambda = LAM, gamma = GAM): number {
  return t.leaves.reduce((s, l) => s + leafObjective(l.G, l.H, lambda, gamma), 0)
}
