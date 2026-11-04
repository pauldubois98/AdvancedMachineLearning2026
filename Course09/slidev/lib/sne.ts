// SNE and t-SNE, the way scripts/make_figures_c09.py writes them: a Gaussian
// per data point, its width found by bisection on the perplexity, the
// symmetrised P, and gradient descent with momentum, per-coordinate gains and
// early exaggeration. The map kernel is Gaussian (SNE) or Student-t (t-SNE).
import { Rng } from './rng'

export const EPS = 1e-12
export type Mat = Float64Array // n x n, row-major

/** squared Euclidean distances between the rows of X */
export function sqdist(X: number[][]): Mat {
  const n = X.length
  const D = new Float64Array(n * n)
  for (let i = 0; i < n; i++) {
    const a = X[i]
    for (let j = i + 1; j < n; j++) {
      const b = X[j]
      let s = 0
      for (let k = 0; k < a.length; k++) {
        const d = a[k] - b[k]
        s += d * d
      }
      D[i * n + j] = s
      D[j * n + i] = s
    }
  }
  return D
}

/** p_{j|i} for one row (self left out) at precision beta = 1/(2 sigma^2),
 *  and its entropy H in bits */
export function rowP(D: Mat, n: number, i: number, beta: number): { p: Float64Array; H: number } {
  const p = new Float64Array(n)
  let mn = Infinity
  for (let j = 0; j < n; j++) if (j !== i && D[i * n + j] < mn) mn = D[i * n + j]
  let s = 0
  for (let j = 0; j < n; j++) {
    if (j === i) continue
    const w = Math.exp(-(D[i * n + j] - mn) * beta)
    p[j] = w
    s += w
  }
  let H = 0
  for (let j = 0; j < n; j++) {
    p[j] /= s
    if (p[j] > EPS) H -= p[j] * Math.log2(p[j])
  }
  return { p, H }
}

export const perplexityOf = (D: Mat, n: number, i: number, sigma: number) =>
  2 ** rowP(D, n, i, 1 / (2 * sigma * sigma)).H

export interface Bisection { sigma: number; perp: number }

/** the width of point i that gives the target perplexity: the bisection of
 *  the lecture, each try recorded */
export function findSigma(D: Mat, n: number, i: number, perp: number, tol = 1e-5) {
  const target = Math.log2(perp)
  let med = 0
  {
    const row: number[] = []
    for (let j = 0; j < n; j++) if (j !== i) row.push(D[i * n + j])
    row.sort((a, b) => a - b)
    med = row[row.length >> 1]
  }
  let lo = 0
  let hi = Infinity
  let beta = 1 / Math.max(med, EPS)
  const trace: Bisection[] = []
  let p = new Float64Array(n)
  for (let it = 0; it < 100; it++) {
    const r = rowP(D, n, i, beta)
    p = r.p
    trace.push({ sigma: 1 / Math.sqrt(2 * beta), perp: 2 ** r.H })
    if (Math.abs(r.H - target) < tol) break
    if (r.H > target) {
      lo = beta
      beta = hi === Infinity ? beta * 2 : (beta + hi) / 2
    } else {
      hi = beta
      beta = (beta + lo) / 2
    }
  }
  return { p, sigma: 1 / Math.sqrt(2 * beta), trace }
}

/** every p_{j|i} (row i sums to one) and every sigma_i */
export function conditionalP(D: Mat, n: number, perp: number) {
  const P = new Float64Array(n * n)
  const sig = new Float64Array(n)
  for (let i = 0; i < n; i++) {
    const r = findSigma(D, n, i, perp)
    P.set(r.p, i * n)
    sig[i] = r.sigma
  }
  return { P, sig }
}

/** p_ij = (p_{j|i} + p_{i|j}) / 2n */
export function jointP(Pc: Mat, n: number): Mat {
  const P = new Float64Array(n * n)
  for (let i = 0; i < n; i++)
    for (let j = 0; j < n; j++)
      P[i * n + j] = i === j ? EPS : Math.max((Pc[i * n + j] + Pc[j * n + i]) / (2 * n), EPS)
  return P
}

export type Kernel = 'sne' | 't'

export interface EmbedOpts {
  kind?: Kernel
  dim?: number
  seed?: number
  lr?: number
  exag?: number
  exagIters?: number
  /** the start; otherwise N(0, scale^2) */
  Y0?: number[][]
  scale?: number
}

/** the map, and one move at a time: Y, Q and KL are those *before* the next
 *  move, as the printed figures record them */
export class Embedding {
  n: number
  dim: number
  kind: Kernel
  P: Mat
  Y: Float64Array
  V: Float64Array
  gains: Float64Array
  Q: Mat
  W: Mat
  it = 0
  kl = 0
  lr: number
  exag: number
  exagIters: number

  constructor(P: Mat, n: number, o: EmbedOpts = {}) {
    this.n = n
    this.P = P
    this.kind = o.kind ?? 't'
    this.dim = o.dim ?? 2
    this.exag = o.exag ?? 12
    this.exagIters = o.exagIters ?? 250
    this.lr = o.lr ?? (this.kind === 't' ? Math.max(n / this.exag / 4, 50) : 10)
    this.Y = new Float64Array(n * this.dim)
    if (o.Y0) o.Y0.forEach((r, i) => r.forEach((v, k) => (this.Y[i * this.dim + k] = v)))
    else {
      const rng = new Rng(o.seed ?? 1)
      const s = o.scale ?? 1e-4
      for (let k = 0; k < this.Y.length; k++) this.Y[k] = rng.normal(0, s)
    }
    this.V = new Float64Array(n * this.dim)
    this.gains = new Float64Array(n * this.dim).fill(1)
    this.Q = new Float64Array(n * n)
    this.W = new Float64Array(n * n)
    this.measure()
  }

  /** Q and KL(P || Q) for the current map */
  measure() {
    const { n, dim, Y, W, Q, P } = this
    const t = this.kind === 't'
    let s = 0
    for (let i = 0; i < n; i++) {
      W[i * n + i] = 0
      for (let j = i + 1; j < n; j++) {
        let d2 = 0
        for (let k = 0; k < dim; k++) {
          const d = Y[i * dim + k] - Y[j * dim + k]
          d2 += d * d
        }
        const w = t ? 1 / (1 + d2) : Math.exp(-d2)
        W[i * n + j] = w
        W[j * n + i] = w
        s += 2 * w
      }
    }
    let kl = 0
    for (let i = 0; i < n; i++) {
      Q[i * n + i] = EPS
      for (let j = i + 1; j < n; j++) {
        const q = Math.max(W[i * n + j] / s, EPS)
        Q[i * n + j] = q
        Q[j * n + i] = q
        kl += P[i * n + j] * Math.log(P[i * n + j] / q) + P[j * n + i] * Math.log(P[j * n + i] / q)
      }
    }
    this.kl = kl
  }

  /** one gradient step, then measure the new map. P, Q and W are symmetric,
   *  so each pair is visited once and pushes both of its points. */
  step() {
    const { n, dim, Y, V, gains, P, Q, W } = this
    const ex = this.it < this.exagIters ? this.exag : 1
    const mom = this.it < this.exagIters ? 0.5 : 0.8
    const t = this.kind === 't'
    const G = new Float64Array(n * dim)
    if (dim === 2) {
      for (let i = 0; i < n; i++) {
        const xi = Y[2 * i], yi = Y[2 * i + 1]
        let gx = 0, gy = 0
        const row = i * n
        for (let j = i + 1; j < n; j++) {
          let m = ex * P[row + j] - Q[row + j]
          if (t) m *= W[row + j]
          m *= 4
          const dx = m * (xi - Y[2 * j]), dy = m * (yi - Y[2 * j + 1])
          gx += dx; gy += dy
          G[2 * j] -= dx; G[2 * j + 1] -= dy
        }
        G[2 * i] += gx; G[2 * i + 1] += gy
      }
    } else {
      for (let i = 0; i < n; i++)
        for (let j = i + 1; j < n; j++) {
          let m = ex * P[i * n + j] - Q[i * n + j]
          if (t) m *= W[i * n + j]
          for (let k = 0; k < dim; k++) {
            const d = 4 * m * (Y[i * dim + k] - Y[j * dim + k])
            G[i * dim + k] += d
            G[j * dim + k] -= d
          }
        }
    }
    const mean = new Float64Array(dim)
    for (let a = 0; a < n * dim; a++) {
      const g = G[a]
      gains[a] = Math.sign(g) !== Math.sign(V[a]) ? gains[a] + 0.2 : Math.max(gains[a] * 0.8, 0.01)
      V[a] = mom * V[a] - this.lr * gains[a] * g
      Y[a] += V[a]
      mean[a % dim] += Y[a] / n
    }
    for (let a = 0; a < n * dim; a++) Y[a] -= mean[a % dim]
    this.it++
    this.measure()
  }

  /** the map as points */
  points(): number[][] {
    const out: number[][] = []
    for (let i = 0; i < this.n; i++) out.push(Array.from(this.Y.subarray(i * this.dim, (i + 1) * this.dim)))
    return out
  }
}

/** the force of each other point on point i: minus the gradient, pair by pair
 *  (1-D maps only) */
export function forcesOn(e: Embedding, i: number): number[] {
  const { n, P, Q, W, Y } = e
  const f: number[] = []
  for (let j = 0; j < n; j++) {
    if (j === i) { f.push(0); continue }
    let m = P[i * n + j] - Q[i * n + j]
    if (e.kind === 't') m *= W[i * n + j]
    f.push(-4 * m * (Y[i] - Y[j]))
  }
  return f
}

// ---------------------------------------------------------------------------
// PCA: Jacobi's eigenvalue method, enough for d <= 64
// ---------------------------------------------------------------------------
export function eigSym(A0: number[][]): { values: number[]; vectors: number[][] } {
  const d = A0.length
  const A = A0.map((r) => r.slice())
  const V = A.map((_, i) => A.map((__, j) => (i === j ? 1 : 0)))
  for (let sweep = 0; sweep < 60; sweep++) {
    let off = 0
    for (let p = 0; p < d; p++) for (let q = p + 1; q < d; q++) off += A[p][q] * A[p][q]
    if (off < 1e-18) break
    for (let p = 0; p < d; p++) {
      for (let q = p + 1; q < d; q++) {
        if (Math.abs(A[p][q]) < 1e-15) continue
        const th = (A[q][q] - A[p][p]) / (2 * A[p][q])
        const t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1))
        const c = 1 / Math.sqrt(t * t + 1)
        const s = t * c
        for (let k = 0; k < d; k++) {
          const akp = A[k][p], akq = A[k][q]
          A[k][p] = c * akp - s * akq
          A[k][q] = s * akp + c * akq
        }
        for (let k = 0; k < d; k++) {
          const apk = A[p][k], aqk = A[q][k]
          A[p][k] = c * apk - s * aqk
          A[q][k] = s * apk + c * aqk
        }
        for (let k = 0; k < d; k++) {
          const vkp = V[k][p], vkq = V[k][q]
          V[k][p] = c * vkp - s * vkq
          V[k][q] = s * vkp + c * vkq
        }
      }
    }
  }
  const order = A.map((_, i) => i).sort((a, b) => A[b][b] - A[a][a])
  return {
    values: order.map((i) => A[i][i]),
    vectors: order.map((i) => V.map((r) => r[i])), // each a unit eigenvector
  }
}

/** centre, then project on the top q eigenvectors of the covariance */
export function pca(X: number[][], q = 2) {
  const n = X.length
  const d = X[0].length
  const mu = new Array(d).fill(0)
  for (const r of X) for (let k = 0; k < d; k++) mu[k] += r[k] / n
  const Xc = X.map((r) => r.map((v, k) => v - mu[k]))
  const S = Array.from({ length: d }, () => new Array(d).fill(0))
  for (const r of Xc) for (let a = 0; a < d; a++) for (let b = a; b < d; b++) S[a][b] += (r[a] * r[b]) / (n - 1)
  for (let a = 0; a < d; a++) for (let b = 0; b < a; b++) S[a][b] = S[b][a]
  const { values, vectors } = eigSym(S)
  const Z = Xc.map((r) => vectors.slice(0, q).map((v) => v.reduce((s, x, k) => s + x * r[k], 0)))
  return { Z, values, vectors, mu }
}
