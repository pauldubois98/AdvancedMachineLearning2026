// The datasets of Course04, one function per picture, all seeded so every
// machine shows the same cloud. The shapes mirror scripts/make_figures_c04.py:
// blobs, the two arms and a blob of the running example, moons and rings, and
// the three-density cloud the HDBSCAN slides are built on.
import { Rng } from './rng'

export type Pts = number[][]

export interface Labelled {
  X: Pts
  y: number[]
}

/** Gaussian blobs: one per centre, `spread` wide, `n` points each. */
export function blobs(
  centres: [number, number][],
  spread = 0.55,
  n = 60,
  seed = 1,
): Labelled {
  const rng = new Rng(seed)
  const X: Pts = []
  const y: number[] = []
  centres.forEach((c, k) => {
    for (let i = 0; i < n; i++) {
      X.push([rng.normal(c[0], spread), rng.normal(c[1], spread)])
      y.push(k)
    }
  })
  return { X, y }
}

/** Blobs with one spread per centre (the "unequal spreads" picture). */
export function blobsVaried(
  centres: [number, number][],
  spreads: number[],
  n = 80,
  seed = 1,
): Labelled {
  const rng = new Rng(seed)
  const X: Pts = []
  const y: number[] = []
  centres.forEach((c, k) => {
    for (let i = 0; i < n; i++) {
      X.push([rng.normal(c[0], spreads[k]), rng.normal(c[1], spreads[k])])
      y.push(k)
    }
  })
  return { X, y }
}

/** Two elongated arms and a blob, plus scattered noise: the running example. */
export function treeData(seed = 3, n = 260, noise = 40): Pts {
  const rng = new Rng(seed)
  const X: Pts = []
  const half = Math.floor(n / 2)
  for (let i = 0; i < half; i++) {
    const t = rng.next()
    X.push([-2.4 + 3.0 * t + rng.normal(0, 0.18), 1.9 - 1.4 * t + rng.normal(0, 0.18)])
  }
  for (let i = 0; i < half; i++) {
    const t = rng.next()
    X.push([-2.2 + 3.1 * t + rng.normal(0, 0.18), -1.9 + 1.5 * t + rng.normal(0, 0.18)])
  }
  for (let i = 0; i < Math.floor(n / 3); i++) {
    X.push([rng.normal(2.6, 0.42), rng.normal(0.1, 0.42)])
  }
  for (let i = 0; i < noise; i++) {
    X.push([rng.uniform(-3.6, 4.2), rng.uniform(-3.0, 3.0)])
  }
  return X
}

/** sklearn's make_moons. */
export function moons(n = 220, noise = 0.06, seed = 0, scale = 1): Labelled {
  const rng = new Rng(seed + 991)
  const nOut = Math.ceil(n / 2)
  const nIn = Math.floor(n / 2)
  const X: Pts = []
  const y: number[] = []
  for (let i = 0; i < nOut; i++) {
    const t = (Math.PI * i) / (nOut - 1)
    X.push([
      scale * (Math.cos(t) + rng.normal(0, noise)),
      scale * (Math.sin(t) + rng.normal(0, noise)),
    ])
    y.push(0)
  }
  for (let i = 0; i < nIn; i++) {
    const t = (Math.PI * i) / (nIn - 1)
    X.push([
      scale * (1 - Math.cos(t) + rng.normal(0, noise)),
      scale * (0.5 - Math.sin(t) + rng.normal(0, noise)),
    ])
    y.push(1)
  }
  return { X, y }
}

/** sklearn's make_circles. */
export function circles(n = 260, noise = 0.05, factor = 0.45, seed = 0, scale = 1): Labelled {
  const rng = new Rng(seed + 77)
  const nOut = Math.ceil(n / 2)
  const nIn = Math.floor(n / 2)
  const X: Pts = []
  const y: number[] = []
  for (let i = 0; i < nOut; i++) {
    const t = (2 * Math.PI * i) / nOut
    X.push([
      scale * (Math.cos(t) + rng.normal(0, noise)),
      scale * (Math.sin(t) + rng.normal(0, noise)),
    ])
    y.push(0)
  }
  for (let i = 0; i < nIn; i++) {
    const t = (2 * Math.PI * i) / nIn
    X.push([
      scale * (factor * Math.cos(t) + rng.normal(0, noise)),
      scale * (factor * Math.sin(t) + rng.normal(0, noise)),
    ])
    y.push(1)
  }
  return { X, y }
}

/** Three blobs put through a shear: clusters that are no longer round. */
export function anisotropic(n = 300, seed = 7): Labelled {
  const base = blobs(
    [
      [-2.6, -1.4],
      [0.3, 2.3],
      [2.9, -0.7],
    ],
    0.85,
    Math.floor(n / 3),
    seed,
  )
  const M = [
    [0.6, -0.6],
    [-0.4, 0.8],
  ]
  return {
    X: base.X.map(([a, b]) => [a * M[0][0] + b * M[1][0], a * M[0][1] + b * M[1][1]]),
    y: base.y,
  }
}

/** The cloud the DBSCAN slides use: two moons plus uniform junk. */
export function dbscanToy(seed = 5, nNoise = 25): Pts {
  const rng = new Rng(seed)
  const X = moons(220, 0.06, 0, 2.0).X
  for (let i = 0; i < nNoise; i++) X.push([rng.uniform(-3.0, 4.0), rng.uniform(-3.0, 4.0)])
  return X
}

/** Clusters of three different densities, plus noise: the HDBSCAN example. */
export function densityData(seed = 4, nDense = 70, nSparse = 45, nNoise = 18): Pts {
  const rng = new Rng(seed + 5)
  const X: Pts = []
  for (let i = 0; i < nDense; i++) X.push([rng.normal(-1.9, 0.26), rng.normal(-0.6, 0.26)])
  for (let i = 0; i < nDense; i++) X.push([rng.normal(0.6, 0.17), rng.normal(1.5, 0.17)])
  for (let i = 0; i < nSparse; i++) X.push([rng.normal(2.2, 0.8), rng.normal(-0.9, 0.8)])
  for (let i = 0; i < nNoise; i++) X.push([rng.uniform(-3.4, 4.0), rng.uniform(-2.6, 3.2)])
  return X
}

/** The data under the mountain function: three blobs of unequal weight. */
export function mountainData(seed = 21): Pts {
  const rng = new Rng(seed)
  const X: Pts = []
  for (let i = 0; i < 60; i++) X.push([rng.normal(-1.8, 0.42), rng.normal(-0.7, 0.42)])
  for (let i = 0; i < 40; i++) X.push([rng.normal(1.7, 0.34), rng.normal(-0.5, 0.34)])
  for (let i = 0; i < 35; i++) X.push([rng.normal(0.1, 0.3), rng.normal(1.6, 0.3)])
  return X
}

/** Six labelled points, small enough to follow a dendrogram by eye. */
export function toyPoints(): { X: Pts; names: string[] } {
  return {
    X: [
      [0.2, 0.85],
      [0.32, 0.72],
      [0.8, 0.8],
      [0.92, 0.66],
      [0.55, 0.15],
      [0.72, 0.22],
    ],
    names: ['P₁', 'P₂', 'P₃', 'P₄', 'P₅', 'P₆'],
  }
}

/** Seven labelled points, small enough to follow the MST edge by edge. */
export function mstToy(): { X: Pts; names: string[] } {
  return {
    X: [
      [0.1, 2.2],
      [1.05, 2.65],
      [0.55, 1.35],
      [1.95, 1.75],
      [3.4, 2.3],
      [3.6, 1.15],
      [3.05, 0.3],
    ],
    names: ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
  }
}

/** A tight crowd plus two stragglers: the mutual-reachability worked example. */
export function mreachToy(): { X: Pts; names: string[] } {
  return {
    X: [
      [0.0, 0.0],
      [0.42, 0.22],
      [0.18, 0.5],
      [0.58, -0.26],
      [1.85, 0.8],
      [2.55, 1.35],
    ],
    names: ['A', 'B', 'C', 'D', 'P', 'Q'],
  }
}

/** Two blobs joined by a line of stray points: the chaining picture. */
export function bridgeData(nBridge = 5, seed = 5, spread = 0.3): { X: Pts; bridge: number[] } {
  const rng = new Rng(seed)
  const X: Pts = []
  for (let i = 0; i < 40; i++) X.push([rng.normal(-1.6, spread), rng.normal(0, spread)])
  for (let i = 0; i < 40; i++) X.push([rng.normal(1.6, spread), rng.normal(0, spread)])
  const bridge: number[] = []
  for (let i = 0; i < nBridge; i++) {
    const t = nBridge === 1 ? 0.5 : i / (nBridge - 1)
    bridge.push(X.length)
    X.push([-0.95 + 1.9 * t, 0])
  }
  return { X, bridge }
}

/** A grid of candidate centres over a cloud: the mountain method's nodes. */
export function gridOver(
  X: Pts,
  step = 0.22,
  pad = 0.9,
): { V: Pts; nx: number; ny: number; x0: number; y0: number; step: number } {
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity
  for (const p of X) {
    x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0])
    y0 = Math.min(y0, p[1]); y1 = Math.max(y1, p[1])
  }
  x0 -= pad; x1 += pad; y0 -= pad; y1 += pad
  const nx = Math.floor((x1 - x0) / step) + 1
  const ny = Math.floor((y1 - y0) / step) + 1
  const V: Pts = []
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) V.push([x0 + i * step, y0 + j * step])
  return { V, nx, ny, x0, y0, step }
}

/** Centre and scale every column: sklearn's StandardScaler. */
export function standardise(X: Pts): Pts {
  const n = X.length
  const d = X[0].length
  const mu = new Array(d).fill(0)
  const sd = new Array(d).fill(0)
  for (const p of X) for (let j = 0; j < d; j++) mu[j] += p[j] / n
  for (const p of X) for (let j = 0; j < d; j++) sd[j] += (p[j] - mu[j]) ** 2 / n
  for (let j = 0; j < d; j++) sd[j] = Math.sqrt(sd[j]) || 1
  return X.map((p) => p.map((v, j) => (v - mu[j]) / sd[j]))
}

/** The full pairwise Euclidean distance matrix. */
export function distances(X: Pts): Float64Array[] {
  const n = X.length
  const D: Float64Array[] = Array.from({ length: n }, () => new Float64Array(n))
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      let s = 0
      for (let k = 0; k < X[i].length; k++) s += (X[i][k] - X[j][k]) ** 2
      const d = Math.sqrt(s)
      D[i][j] = d
      D[j][i] = d
    }
  }
  return D
}
