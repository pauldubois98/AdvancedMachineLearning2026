// The regression machinery of the lecture, the way scripts/make_figures_c02.py
// writes it: least squares, ridge and lasso, the robust losses and their
// weights, IRLS, and logistic regression by Newton / IRLS. Small and explicit.
import { Rng } from './rng'

export type Vec = number[]
export type Mat = number[][]

// --- linear algebra -------------------------------------------------------------
/** solve A x = b by Gaussian elimination with partial pivoting */
export function solve(A0: Mat, b0: Vec): Vec {
  const n = A0.length
  const M = A0.map((r, i) => [...r, b0[i]])
  for (let c = 0; c < n; c++) {
    let p = c
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r
    ;[M[c], M[p]] = [M[p], M[c]]
    const piv = Math.abs(M[c][c]) < 1e-14 ? 1e-14 : M[c][c]
    for (let r = c + 1; r < n; r++) {
      const f = M[r][c] / piv
      if (f) for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]
    }
  }
  const x = new Array(n).fill(0)
  for (let r = n - 1; r >= 0; r--) {
    let s = M[r][n]
    for (let k = r + 1; k < n; k++) s -= M[r][k] * x[k]
    x[r] = s / (Math.abs(M[r][r]) < 1e-14 ? 1e-14 : M[r][r])
  }
  return x
}

/** X^T W X and X^T W y, w = 1 when absent */
export function normal(X: Mat, y: Vec, w?: Vec) {
  const d = X[0].length
  const G = Array.from({ length: d }, () => new Array(d).fill(0))
  const r = new Array(d).fill(0)
  for (let i = 0; i < X.length; i++) {
    const wi = w ? w[i] : 1
    const xi = X[i]
    for (let a = 0; a < d; a++) {
      r[a] += wi * xi[a] * y[i]
      for (let b = a; b < d; b++) G[a][b] += wi * xi[a] * xi[b]
    }
  }
  for (let a = 0; a < d; a++) for (let b = 0; b < a; b++) G[a][b] = G[b][a]
  return { G, r }
}

/** (X^T W X + lam I)^{-1} X^T W y */
export function wls(X: Mat, y: Vec, w?: Vec, lam = 0): Vec {
  const { G, r } = normal(X, y, w)
  for (let a = 0; a < G.length; a++) G[a][a] += lam + 1e-12
  return solve(G, r)
}

/** the minimum-norm least squares solution, also when d > n:
 *  X^T (X X^T)^{-1} y, with a whisper of ridge */
export function lstsqMinNorm(X: Mat, y: Vec): Vec {
  const n = X.length, d = X[0].length
  if (d < n) return wls(X, y, undefined, 1e-10)
  const K = X.map((a) => X.map((b) => a.reduce((s, v, k) => s + v * b[k], 0)))
  for (let i = 0; i < n; i++) K[i][i] += 1e-8
  const a = solve(K, y)
  const beta = new Array(d).fill(0)
  for (let i = 0; i < n; i++) for (let k = 0; k < d; k++) beta[k] += a[i] * X[i][k]
  return beta
}

export const dot = (a: Vec, b: Vec) => a.reduce((s, v, i) => s + v * b[i], 0)
export const predict = (X: Mat, b: Vec) => X.map((r) => dot(r, b))
export const mse = (X: Mat, y: Vec, b: Vec) => X.reduce((s, r, i) => s + (y[i] - dot(r, b)) ** 2, 0) / X.length

/** intercept and slope of the least squares line */
export function fitLine(x: Vec, y: Vec, w?: Vec): [number, number] {
  let sw = 0, sx = 0, sy = 0, sxx = 0, sxy = 0
  for (let i = 0; i < x.length; i++) {
    const wi = w ? w[i] : 1
    sw += wi; sx += wi * x[i]; sy += wi * y[i]; sxx += wi * x[i] * x[i]; sxy += wi * x[i] * y[i]
  }
  const det = sw * sxx - sx * sx
  const b1 = Math.abs(det) < 1e-14 ? 0 : (sw * sxy - sx * sy) / det
  return [(sy - b1 * sx) / Math.max(sw, 1e-14), b1]
}

// --- the penalties ---------------------------------------------------------------
/** lasso by cyclic coordinate descent, objective (1/2n)||y - Xb||^2 + lam ||b||_1
 *  (scikit-learn's scaling), warm-started from b0 */
export function lasso(X: Mat, y: Vec, lam: number, b0?: Vec, iters = 200): Vec {
  const n = X.length, d = X[0].length
  const b = b0 ? b0.slice() : new Array(d).fill(0)
  const col2 = new Array(d).fill(0)
  for (let k = 0; k < d; k++) for (let i = 0; i < n; i++) col2[k] += X[i][k] ** 2 / n
  const r = y.map((v, i) => v - dot(X[i], b))
  for (let it = 0; it < iters; it++) {
    let moved = 0
    for (let k = 0; k < d; k++) {
      let rho = 0
      for (let i = 0; i < n; i++) rho += X[i][k] * (r[i] + X[i][k] * b[k])
      rho /= n
      const nb = soft(rho, lam) / col2[k]
      const delta = nb - b[k]
      if (delta) {
        for (let i = 0; i < n; i++) r[i] -= X[i][k] * delta
        moved = Math.max(moved, Math.abs(delta))
        b[k] = nb
      }
    }
    if (moved < 1e-7) break
  }
  return b
}
/** ridge with the plain scaling: (X^T X + lam I)^{-1} X^T y */
export const ridge = (X: Mat, y: Vec, lam: number) => wls(X, y, undefined, lam)

export const soft = (v: number, t: number) => Math.sign(v) * Math.max(Math.abs(v) - t, 0)
export const hard = (v: number, t: number) => (v * v >= 2 * t ? v : 0)

// --- the robust losses -----------------------------------------------------------
export const rhoLS = (e: number) => 0.5 * e * e
export const rhoHuber = (e: number, d = 1) => (Math.abs(e) <= d ? 0.5 * e * e : d * (Math.abs(e) - 0.5 * d))
export const psiHuber = (e: number, d = 1) => Math.max(-d, Math.min(d, e))
export const wHuber = (e: number, d = 1) => (Math.abs(e) <= d ? 1 : d / Math.max(Math.abs(e), 1e-12))
export const rhoTukey = (e: number, d = 3) => (Math.abs(e) <= d ? (d * d / 6) * (1 - (1 - (e / d) ** 2) ** 3) : d * d / 6)
export const psiTukey = (e: number, d = 3) => (Math.abs(e) <= d ? e * (1 - (e / d) ** 2) ** 2 : 0)
export const wTukey = (e: number, d = 3) => (Math.abs(e) <= d ? (1 - (e / d) ** 2) ** 2 : 0)
export const rhoL1 = (e: number) => Math.abs(e)
export const rhoLogcosh = (e: number) => Math.abs(e) + Math.log1p(Math.exp(-2 * Math.abs(e))) - Math.LN2
export const rhoCauchy = (e: number, d = Math.SQRT2) => Math.log1p((e / d) ** 2)
export const rhoWelsch = (e: number, d = 1.5) => 1 - Math.exp(-(e * e) / (2 * d * d))

export const median = (v: Vec) => {
  const s = [...v].sort((a, b) => a - b), m = s.length >> 1
  return s.length % 2 ? s[m] : 0.5 * (s[m - 1] + s[m])
}
/** sigma-hat = 1.4826 MAD */
export const madScale = (e: Vec) => {
  const m = median(e)
  return Math.max(1.4826 * median(e.map((v) => Math.abs(v - m))), 1e-6)
}

export type WeightFn = (e: number) => number
export interface IrlsStep { beta: [number, number]; w: Vec; scale: number }

/** IRLS on a line, residuals scaled by the MAD at every pass, as _irls does:
 *  history[k] is beta^k with the weights that produced it (all ones at k = 0) */
export function irls(x: Vec, y: Vec, wf: WeightFn, iters = 12, scaled = true): IrlsStep[] {
  let beta = fitLine(x, y)
  let w = x.map(() => 1)
  const out: IrlsStep[] = [{ beta, w, scale: 1 }]
  for (let k = 0; k < iters; k++) {
    const e = x.map((v, i) => y[i] - beta[0] - beta[1] * v)
    const s = scaled ? madScale(e) : 1
    w = e.map((v) => wf(v / s))
    if (w.reduce((a, b) => a + b, 0) < 1e-9) w = w.map(() => 1e-9)
    beta = fitLine(x, y, w)
    out.push({ beta, w, scale: s })
  }
  return out
}

// --- the logistic model ------------------------------------------------------------
export const sigmoid = (z: number) => 1 / (1 + Math.exp(-z))
export const log1pexp = (z: number) => (z > 0 ? z + Math.log1p(Math.exp(-z)) : Math.log1p(Math.exp(z)))

/** Newton / IRLS from beta = 0; history[k] is beta^k. X has no intercept column. */
export function logisticIrls(X: Mat, y: Vec, iters = 8): Vec[] {
  const D = X.map((r) => [1, ...r])
  let beta = new Array(D[0].length).fill(0)
  const hist = [beta.slice()]
  for (let it = 0; it < iters; it++) {
    const p = D.map((r) => sigmoid(dot(r, beta)))
    const w = p.map((v) => Math.max(v * (1 - v), 1e-6))
    const { G } = normal(D, y, w)
    for (let a = 0; a < G.length; a++) G[a][a] += 1e-8
    const g = new Array(beta.length).fill(0)
    D.forEach((r, i) => r.forEach((v, a) => (g[a] += v * (y[i] - p[i]))))
    const step = solve(G, g)
    beta = beta.map((v, a) => v + step[a])
    hist.push(beta.slice())
  }
  return hist
}
export const logisticLoss = (X: Mat, y: Vec, b: Vec) =>
  X.reduce((s, r, i) => { const z = b[0] + dot(r, b.slice(1)); return s + log1pexp(z) - y[i] * z }, 0)

// --- the running data sets ------------------------------------------------------------
/** _line_data: y = 0.6 + 1.1 x + noise, x uniform */
export function lineData(rng: Rng, n = 60, noise = 0.9, slope = 1.1, icpt = 0.6, lo = -3, hi = 3) {
  const x = Array.from({ length: n }, () => rng.uniform(lo, hi))
  return { x, y: x.map((v) => icpt + slope * v + rng.normal(0, noise)) }
}
/** _outlier_data: 26 points on a line, x evenly spaced */
export function outlierBase(seed = 7, n = 26, noise = 0.55) {
  const rng = new Rng(seed)
  const x = Array.from({ length: n }, (_, i) => -3 + (6 * i) / (n - 1))
  return { x, y: x.map((v) => 0.6 + 1.1 * v + rng.normal(0, noise)) }
}
/** _blobs: two classes in 2-D */
export function blobs(rng: Rng, n = 120, gap = 1.6, spread = 1.0) {
  const X: Mat = [], y: Vec = []
  for (let i = 0; i < n; i++) { X.push([rng.normal(-gap, spread), rng.normal(-0.4, spread)]); y.push(0) }
  for (let i = 0; i < n; i++) { X.push([rng.normal(gap, spread), rng.normal(0.5, spread)]); y.push(1) }
  return { X, y }
}
/** _sparse_design: k informative features out of d */
export function sparseDesign(rng: Rng, n = 60, d = 12, k = 3, noise = 1.0) {
  const X = Array.from({ length: n }, () => Array.from({ length: d }, () => rng.normal()))
  const pool = [-2.5, -1.8, 1.9, 2.6]
  const beta = Array.from({ length: d }, (_, j) => (j < k ? pool[Math.floor(rng.next() * 4)] : 0))
  const y = X.map((r) => dot(r, beta) + rng.normal(0, noise))
  return { X, y, beta }
}

export const fmt = (v: number, d = 2) => (Object.is(Math.round(v * 10 ** d), -0) ? (0).toFixed(d) : v.toFixed(d))
