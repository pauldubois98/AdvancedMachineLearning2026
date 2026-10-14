// k-means: Lloyd's algorithm step by step, k-means++ seeding, and the two
// inertias the deck scores a clustering with. Written so a slide can show one
// iteration at a time rather than only the fixed point.
import { Pts } from './data4'
import { Rng } from './rng'

export function assign(X: Pts, mu: Pts): number[] {
  return X.map((p) => {
    let best = 0
    let bd = Infinity
    for (let k = 0; k < mu.length; k++) {
      let s = 0
      for (let j = 0; j < p.length; j++) s += (p[j] - mu[k][j]) ** 2
      if (s < bd) { bd = s; best = k }
    }
    return best
  })
}

/** Move each centre to the mean of its points; an empty cluster stays put. */
export function recentre(X: Pts, labels: number[], mu: Pts): Pts {
  const d = X[0].length
  const sums = mu.map(() => new Array(d).fill(0))
  const counts = mu.map(() => 0)
  X.forEach((p, i) => {
    const k = labels[i]
    counts[k]++
    for (let j = 0; j < d; j++) sums[k][j] += p[j]
  })
  return mu.map((m, k) => (counts[k] ? sums[k].map((s) => s / counts[k]) : m.slice()))
}

export function inertia(X: Pts, labels: number[], mu: Pts): number {
  let out = 0
  X.forEach((p, i) => {
    const m = mu[labels[i]]
    for (let j = 0; j < p.length; j++) out += (p[j] - m[j]) ** 2
  })
  return out
}

/** k-means++: the first centre at random, then each one far from the rest. */
export function kmeansPlusPlus(X: Pts, k: number, seed = 0): Pts {
  const rng = new Rng(seed + 1)
  const mu: Pts = [X[Math.floor(rng.next() * X.length)].slice()]
  const d2 = X.map((p) => sq(p, mu[0]))
  while (mu.length < k) {
    const total = d2.reduce((s, v) => s + v, 0)
    let t = rng.next() * total
    let pick = d2.length - 1
    for (let i = 0; i < d2.length; i++) {
      t -= d2[i]
      if (t <= 0) { pick = i; break }
    }
    mu.push(X[pick].slice())
    X.forEach((p, i) => { d2[i] = Math.min(d2[i], sq(p, X[pick])) })
  }
  return mu
}

function sq(a: number[], b: number[]): number {
  let s = 0
  for (let j = 0; j < a.length; j++) s += (a[j] - b[j]) ** 2
  return s
}

/** k random rows as the starting centres: the unlucky-start slides. */
export function randomInit(X: Pts, k: number, seed = 0): Pts {
  const rng = new Rng(seed + 31)
  const idx: number[] = []
  while (idx.length < k) {
    const i = Math.floor(rng.next() * X.length)
    if (!idx.includes(i)) idx.push(i)
  }
  return idx.map((i) => X[i].slice())
}

export interface KmeansRun {
  mu: Pts
  labels: number[]
  inertia: number
  iters: number
  /** the centres after each iteration, so a slide can replay the run */
  history: Pts[]
}

/** Lloyd's algorithm from given centres, at most `maxIter` sweeps. */
export function lloyd(X: Pts, start: Pts, maxIter = 60): KmeansRun {
  let mu = start.map((m) => m.slice())
  const history: Pts[] = [mu.map((m) => m.slice())]
  let labels = assign(X, mu)
  let iters = 0
  for (let t = 0; t < maxIter; t++) {
    const next = recentre(X, labels, mu)
    const moved = next.some((m, k) => sq(m, mu[k]) > 1e-14)
    mu = next
    labels = assign(X, mu)
    history.push(mu.map((m) => m.slice()))
    iters = t + 1
    if (!moved) break
  }
  return { mu, labels, inertia: inertia(X, labels, mu), iters, history }
}

/** `nInit` restarts, keeping the lowest inertia: sklearn's default behaviour. */
export function kmeans(X: Pts, k: number, seed = 0, nInit = 10): KmeansRun {
  let best: KmeansRun | null = null
  for (let r = 0; r < nInit; r++) {
    const run = lloyd(X, kmeansPlusPlus(X, k, seed * 100 + r))
    if (!best || run.inertia < best.inertia) best = run
  }
  return best!
}

/** The deck's two scores: within-cluster and between-cluster inertia. */
export function jwJb(X: Pts, labels: number[]): { jw: number; jb: number } {
  const d = X[0].length
  const keys = [...new Set(labels)].filter((k) => k >= 0)
  const grand = new Array(d).fill(0)
  for (const p of X) for (let j = 0; j < d; j++) grand[j] += p[j] / X.length
  let jw = 0
  let jb = 0
  for (const k of keys) {
    const pts = X.filter((_, i) => labels[i] === k)
    if (!pts.length) continue
    const m = new Array(d).fill(0)
    for (const p of pts) for (let j = 0; j < d; j++) m[j] += p[j] / pts.length
    for (const p of pts) for (let j = 0; j < d; j++) jw += (p[j] - m[j]) ** 2
    for (let j = 0; j < d; j++) jb += pts.length * (m[j] - grand[j]) ** 2
  }
  return { jw, jb }
}

/** Fuzzy c-means memberships for fixed centres: w_ik from the distances. */
export function fuzzyWeights(X: Pts, mu: Pts, m = 2): number[][] {
  const p = 2 / (m - 1)
  return X.map((x) => {
    const d = mu.map((c) => Math.sqrt(sq(x, c)) + 1e-9)
    const inv = d.map((v) => 1 / v ** p)
    const s = inv.reduce((a, b) => a + b, 0)
    return inv.map((v) => v / s)
  })
}
