// The datasets of the printed deck, regenerated here so the sliders can
// refit on them. Shapes and spreads follow scripts/make_figures_c03.py.
import { Rng } from './rng'

export interface Dataset {
  X: number[][]
  /** 0 / 1 labels, as in the figures. */
  y: number[]
}

/** Two clearly separable clouds; `gap` is how far apart their centres are. */
export function sepBlobs(n = 90, gap = 2.6, seed = 3, sd = 0.62): Dataset {
  const rng = new Rng(seed)
  const half = Math.floor(n / 2)
  const X: number[][] = []
  const y: number[] = []
  for (let i = 0; i < half; i++) {
    X.push([rng.normal(-gap / 2, sd), rng.normal(-gap / 2 + 0.3, sd)])
    y.push(0)
  }
  for (let i = 0; i < half; i++) {
    X.push([rng.normal(gap / 2, sd), rng.normal(gap / 2 - 0.3, sd)])
    y.push(1)
  }
  return { X, y }
}

/** sklearn's make_moons, including its default shuffling. */
export function moons(n = 260, noise = 0.22, seed = 0): Dataset {
  const rng = new Rng(seed + 7)
  const nOut = Math.ceil(n / 2)
  const nIn = n - nOut
  const X: number[][] = []
  const y: number[] = []
  for (let i = 0; i < nOut; i++) {
    const t = (Math.PI * i) / (nOut - 1)
    X.push([Math.cos(t) + rng.normal(0, noise), Math.sin(t) + rng.normal(0, noise)])
    y.push(0)
  }
  for (let i = 0; i < nIn; i++) {
    const t = (Math.PI * i) / (nIn - 1)
    X.push([
      1 - Math.cos(t) + rng.normal(0, noise),
      1 - Math.sin(t) - 0.5 + rng.normal(0, noise),
    ])
    y.push(1)
  }
  return shuffle({ X, y }, rng)
}

/** Fisher–Yates, so the two classes are interleaved as sklearn returns them. */
function shuffle(d: Dataset, rng: Rng): Dataset {
  const order = d.X.map((_, i) => i)
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(rng.next() * (i + 1))
    ;[order[i], order[j]] = [order[j], order[i]]
  }
  return { X: order.map((i) => d.X[i]), y: order.map((i) => d.y[i]) }
}

/** A disc inside a ring: the slide where a circle beats every line. */
export function rings(n = 150, seed = 1): Dataset {
  const rng = new Rng(seed)
  const half = Math.floor(n / 2)
  const X: number[][] = []
  const y: number[] = []
  for (let i = 0; i < 2 * half; i++) {
    const t = rng.uniform(0, 2 * Math.PI)
    const r = i < half ? rng.normal(0.85, 0.16) : rng.normal(2.1, 0.2)
    X.push([r * Math.cos(t), r * Math.sin(t)])
    y.push(i < half ? 0 : 1)
  }
  return { X, y }
}

export function xor(): Dataset {
  return {
    X: [[1, 1], [-1, -1], [1, -1], [-1, 1]],
    y: [1, 1, 0, 0],
  }
}

/** Three clouds, for the one-against-all / one-against-one slide. */
export function threeBlobs(seed = 13, per = 45): { X: number[][]; y: number[] } {
  const rng = new Rng(seed)
  const centres = [[-2.2, -1.4], [2.3, -1.2], [0.1, 2.4]]
  const X: number[][] = []
  const y: number[] = []
  centres.forEach((c, k) => {
    for (let i = 0; i < per; i++) {
      X.push([rng.normal(c[0], 0.85), rng.normal(c[1], 0.85)])
      y.push(k)
    }
  })
  return { X, y }
}

/** The regression target of the SVR slides: sin(x) + 0.35x + noise. */
export function sineRidge(n = 70, seed = 6, noise = 0.18) {
  const rng = new Rng(seed)
  const xs: number[] = []
  for (let i = 0; i < n; i++) xs.push(rng.uniform(-3, 3))
  xs.sort((a, b) => a - b)
  const y = xs.map((x) => Math.sin(x) + 0.35 * x + rng.normal(0, noise))
  return { x: xs, X: xs.map((v) => [v]), y }
}

/** Two features that separate equally well, one measured in a silly unit. */
export function unscaled(scale = 400, n = 140, seed = 4): Dataset {
  const rng = new Rng(seed)
  const half = Math.floor(n / 2)
  const X: number[][] = []
  const y: number[] = []
  for (let i = 0; i < 2 * half; i++) {
    const first = i < half
    const x1 = rng.normal(first ? -0.7 : 0.7, 0.55)
    const x2 = rng.normal(first ? -0.6 : 0.6, 0.6) * scale
    X.push([x1, x2])
    y.push(first ? 0 : 1)
  }
  return { X, y }
}

export function standardize(X: number[][]): number[][] {
  const d = X[0].length
  const mean = new Array(d).fill(0)
  const sd = new Array(d).fill(0)
  for (const row of X) for (let j = 0; j < d; j++) mean[j] += row[j] / X.length
  for (const row of X)
    for (let j = 0; j < d; j++) sd[j] += (row[j] - mean[j]) ** 2 / X.length
  for (let j = 0; j < d; j++) sd[j] = Math.sqrt(sd[j]) || 1
  return X.map((row) => row.map((v, j) => (v - mean[j]) / sd[j]))
}

/** sklearn's gamma="scale": 1 / (d * Var(X)). */
export function gammaScale(X: number[][]): number {
  const d = X[0].length
  let mean = 0
  let n = 0
  for (const row of X) for (const v of row) { mean += v; n++ }
  mean /= n
  let varr = 0
  for (const row of X) for (const v of row) varr += (v - mean) ** 2
  varr /= n
  return 1 / (d * (varr || 1))
}

export function toPm1(y: number[]): number[] {
  return y.map((v) => (v === 1 ? 1 : -1))
}
