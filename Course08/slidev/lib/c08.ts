// Course08: everything the model-selection slides recompute in the browser.
// The generators follow scripts/make_figures_c08.py; the samples are drawn
// with lib/rng.ts, so apart from Bishop's ten points they differ from the
// printed figures' (numpy's generator) but follow the same models.
import { Rng } from './rng'
import { drawClass, drawMvn, type Cov, type Pt } from './gmm'

// ---------------------------------------------------------------------------
// Bishop's curve-fitting example
// ---------------------------------------------------------------------------
export const truth = (x: number) => Math.sin(2 * Math.PI * x)

/** the ten noise draws of the printed deck (numpy, seed 6, sd 0.22) */
const BISHOP_EPS = [0.2317, 1.0336, 0.4231, 0.8357, 0.565, -0.0445, -0.7222, -0.6554, -0.579, 0.1213]
  .map((t, i) => t - truth(i / 9))

export const linspace = (a: number, b: number, n: number) =>
  Array.from({ length: n }, (_, i) => (n === 1 ? a : a + ((b - a) * i) / (n - 1)))

export interface Sample { x: number[]; t: number[] }

/** n points of sin(2 pi x) plus Gaussian noise, x evenly spaced on [0, 1].
 *  Seed 0 with n = 10 is the printed deck's sample, its noise rescaled. */
export function sinData(n: number, seed: number, noise = 0.22): Sample {
  const x = linspace(0, 1, n)
  if (seed === 0 && n === 10) return { x, t: x.map((v, i) => truth(v) + (noise / 0.22) * BISHOP_EPS[i]) }
  const rng = new Rng(seed * 7919 + n)
  return { x, t: x.map((v) => truth(v) + rng.normal(0, noise)) }
}

/** a large fresh sample, x drawn uniformly: the stand-in for the true risk */
export function freshSin(n: number, seed: number, noise = 0.22): Sample {
  const rng = new Rng(seed)
  const x = Array.from({ length: n }, () => rng.next())
  return { x, t: x.map((v) => truth(v) + rng.normal(0, noise)) }
}

/** Least squares by Householder QR: the polynomial basis on [0, 1] is far too
 *  ill-conditioned at M = 9 for the normal equations. */
export function lstsq(A: number[][], b: number[]): number[] {
  const m = A.length
  const n = A[0].length
  const R = A.map((r) => [...r])
  const y = [...b]
  for (let k = 0; k < n; k++) {
    let norm = 0
    for (let i = k; i < m; i++) norm += R[i][k] ** 2
    norm = Math.sqrt(norm)
    if (norm < 1e-300) continue
    const alpha = R[k][k] > 0 ? -norm : norm
    const v = new Array(m).fill(0)
    for (let i = k; i < m; i++) v[i] = R[i][k]
    v[k] -= alpha
    let vv = 0
    for (let i = k; i < m; i++) vv += v[i] ** 2
    if (vv < 1e-300) continue
    for (let j = k; j < n; j++) {
      let s = 0
      for (let i = k; i < m; i++) s += v[i] * R[i][j]
      s = (2 * s) / vv
      for (let i = k; i < m; i++) R[i][j] -= s * v[i]
    }
    let s = 0
    for (let i = k; i < m; i++) s += v[i] * y[i]
    s = (2 * s) / vv
    for (let i = k; i < m; i++) y[i] -= s * v[i]
  }
  // back substitution; a rank-deficient column (more coefficients than
  // points) gets the minimum-effort answer 0
  const w = new Array(n).fill(0)
  for (let k = Math.min(n, m) - 1; k >= 0; k--) {
    let s = y[k]
    for (let j = k + 1; j < n; j++) s -= R[k][j] * w[j]
    w[k] = Math.abs(R[k][k]) > 1e-12 ? s / R[k][k] : 0
  }
  return w
}

export function design(x: number[], M: number): number[][] {
  return x.map((v) => {
    const r = new Array(M + 1)
    let p = 1
    for (let j = 0; j <= M; j++) { r[j] = p; p *= v }
    return r
  })
}

/** order-M polynomial by least squares, ridge-penalised when lam > 0 */
export function polyFit(x: number[], t: number[], M: number, lam = 0): number[] {
  const A = design(x, M)
  const b = [...t]
  if (lam > 0) {
    const s = Math.sqrt(lam)
    for (let j = 0; j <= M; j++) {
      const r = new Array(M + 1).fill(0)
      r[j] = s
      A.push(r)
      b.push(0)
    }
  }
  return lstsq(A, b)
}

export function polyEval(w: number[], x: number): number {
  let s = 0
  for (let j = w.length - 1; j >= 0; j--) s = s * x + w[j]
  return s
}

export function mse(w: number[], s: Sample): number {
  let e = 0
  for (let i = 0; i < s.x.length; i++) e += (polyEval(w, s.x[i]) - s.t[i]) ** 2
  return e / s.x.length
}
export const rms = (w: number[], s: Sample) => Math.sqrt(mse(w, s))

export function permutation(n: number, rng: Rng): number[] {
  const idx = Array.from({ length: n }, (_, i) => i)
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(rng.next() * (i + 1))
    ;[idx[i], idx[j]] = [idx[j], idx[i]]
  }
  return idx
}

/** K index sets: a random split into K near-equal parts */
export function folds(n: number, K: number, seed: number): number[][] {
  const idx = permutation(n, new Rng(seed))
  const out: number[][] = []
  for (let k = 0; k < K; k++) {
    const a = Math.floor((k * n) / K)
    const b = Math.floor(((k + 1) * n) / K)
    out.push(idx.slice(a, b).sort((u, v) => u - v))
  }
  return out
}

export const pick = (s: Sample, idx: number[]): Sample => ({ x: idx.map((i) => s.x[i]), t: idx.map((i) => s.t[i]) })

/** the lecture's R_CV for the polynomial of order M */
export function cvPoly(s: Sample, M: number, K: number, seed: number, lam = 0): number {
  const n = s.x.length
  let tot = 0
  for (const f of folds(n, K, seed)) {
    const inF = new Set(f)
    const tr = Array.from({ length: n }, (_, i) => i).filter((i) => !inF.has(i))
    tot += mse(polyFit(pick(s, tr).x, pick(s, tr).t, M, lam), pick(s, f))
  }
  return tot / K
}

// ---------------------------------------------------------------------------
// classification data
// ---------------------------------------------------------------------------
export interface Labelled { X: number[][]; y: number[] }

/** sklearn's make_moons shape, labels +-1 */
export function moons(n: number, noise: number, seed: number): Labelled {
  const rng = new Rng(seed)
  const nOut = Math.ceil(n / 2)
  const nIn = n - nOut
  const X: number[][] = []
  const y: number[] = []
  for (let i = 0; i < nOut; i++) {
    const a = (Math.PI * i) / (nOut - 1)
    X.push([Math.cos(a) + rng.normal(0, noise), Math.sin(a) + rng.normal(0, noise)])
    y.push(-1)
  }
  for (let i = 0; i < nIn; i++) {
    const a = (Math.PI * i) / (nIn - 1)
    X.push([1 - Math.cos(a) + rng.normal(0, noise), 0.5 - Math.sin(a) + rng.normal(0, noise)])
    y.push(1)
  }
  return { X, y }
}

/** knob_rigid_vs_flexible: two Gaussians sharing one correlated covariance */
export const RF_S: Cov = [1.0, 0.75, 1.0]
export const RF_MU: [Pt, Pt] = [[-1.0, -0.6], [1.0, 0.6]]
export function twoGauss(nPer: number, seed: number): Labelled {
  const rng = new Rng(seed)
  const X: number[][] = []
  const y: number[] = []
  for (let c = 0; c < 2; c++) for (let i = 0; i < nPer; i++) { X.push(drawMvn(rng, RF_MU[c], RF_S)); y.push(c) }
  return { X, y }
}

export type GaussKind = 'nb' | 'lda' | 'qda'

/** naive Bayes, LDA or QDA in two dimensions: the log-odds of class 1 */
export function gaussFit(d: Labelled, kind: GaussKind): (x: number, y: number) => number {
  const stats = [0, 1].map((c) => {
    const P = d.X.filter((_, i) => d.y[i] === c)
    const n = P.length
    const m = [P.reduce((a, p) => a + p[0], 0) / n, P.reduce((a, p) => a + p[1], 0) / n]
    let a = 0, b = 0, cc = 0
    for (const p of P) { a += (p[0] - m[0]) ** 2; b += (p[0] - m[0]) * (p[1] - m[1]); cc += (p[1] - m[1]) ** 2 }
    return { n, m, S: [a / n, b / n, cc / n] as Cov }
  })
  const N = stats[0].n + stats[1].n
  let covs: Cov[]
  if (kind === 'lda') {
    const T = [0, 1, 2].map((j) => (stats[0].n * stats[0].S[j] + stats[1].n * stats[1].S[j]) / N)
    covs = [T as Cov, T as Cov]
  } else if (kind === 'nb') covs = stats.map((s) => [s.S[0], 0, s.S[2]] as Cov)
  else covs = stats.map((s) => s.S)
  covs = covs.map((S) => [S[0] + 1e-9, S[1], S[2] + 1e-9] as Cov)
  const logp = (c: number, x: number, y: number) => {
    const [a, b, cc] = covs[c]
    const det = a * cc - b * b
    const dx = x - stats[c].m[0]
    const dy = y - stats[c].m[1]
    return -0.5 * (cc * dx * dx - 2 * b * dx * dy + a * dy * dy) / det - 0.5 * Math.log(det) + Math.log(stats[c].n / N)
  }
  return (x, y) => logp(1, x, y) - logp(0, x, y)
}

export function gaussAccuracy(f: (x: number, y: number) => number, d: Labelled): number {
  let ok = 0
  for (let i = 0; i < d.X.length; i++) if ((f(d.X[i][0], d.X[i][1]) > 0 ? 1 : 0) === d.y[i]) ok++
  return ok / d.X.length
}

// ---------------------------------------------------------------------------
// the three clusters lecture 6 left us with
// ---------------------------------------------------------------------------
const B_MU: Pt[] = [[-1.5, 0.9], [1.5, 1.0], [0.1, -1.3]]
const B_S: Cov[] = [[0.55, 0.30, 0.30], [0.40, -0.26, 0.55], [0.90, 0.05, 0.22]]
/** the draw whose DBSCAN behaves as the printed figure: 9, 3, 1 clusters at
 *  epsilon = 0.18, 0.40, 0.70 */
export const BLOB_SEED = 3
export function gmmBlobs(seed: number, n: number): { X: Pt[]; z: number[] } {
  const rng = new Rng(seed)
  const X: Pt[] = []
  const z: number[] = []
  for (let i = 0; i < n; i++) {
    const k = drawClass(rng, [0.38, 0.32, 0.30])
    X.push(drawMvn(rng, B_MU[k], B_S[k]))
    z.push(k)
  }
  return { X, z }
}

/** DBSCAN, O(n^2): labels from 0, noise -1 */
export function dbscan(X: Pt[], eps: number, minPts: number): { labels: number[]; core: boolean[] } {
  const n = X.length
  const e2 = eps * eps
  const nb: number[][] = X.map((p) => {
    const out: number[] = []
    for (let j = 0; j < n; j++) if ((p[0] - X[j][0]) ** 2 + (p[1] - X[j][1]) ** 2 <= e2) out.push(j)
    return out
  })
  const core = nb.map((l) => l.length >= minPts)
  const labels = new Array(n).fill(-1)
  let c = 0
  for (let i = 0; i < n; i++) {
    if (!core[i] || labels[i] !== -1) continue
    const stack = [i]
    labels[i] = c
    while (stack.length) {
      const p = stack.pop()!
      if (!core[p]) continue
      for (const q of nb[p]) if (labels[q] === -1) { labels[q] = c; stack.push(q) }
    }
    c++
  }
  return { labels, core }
}

// ---------------------------------------------------------------------------
// NMF: a rank-r toy matrix and Lee-Seung updates under a mask
// ---------------------------------------------------------------------------
export interface Mat { p: number; n: number; v: Float64Array }

export function nmfToy(seed: number, p: number, n: number, r: number, noise: number): Mat {
  const rng = new Rng(seed)
  const W = Array.from({ length: p * r }, () => Math.abs(rng.normal()) ** 1.3)
  const H = Array.from({ length: r * n }, () => Math.abs(rng.normal()) ** 1.3)
  const v = new Float64Array(p * n)
  for (let i = 0; i < p; i++) for (let j = 0; j < n; j++) {
    let s = 0
    for (let k = 0; k < r; k++) s += W[i * r + k] * H[k * n + j]
    v[i * n + j] = Math.max(s + rng.normal(0, noise), 1e-4)
  }
  return { p, n, v }
}

/** multiplicative updates on the entries where mask = 1; returns W H */
export function nmfMasked(X: Mat, r: number, iters: number, seed: number, mask: Float64Array): Float64Array {
  const { p, n, v } = X
  const rng = new Rng(seed)
  let mean = 0
  for (let i = 0; i < v.length; i++) mean += v[i]
  const scale = Math.sqrt(Math.max(mean / v.length, 1e-10) / r)
  const W = Float64Array.from({ length: p * r }, () => rng.next() * scale + 1e-3)
  const H = Float64Array.from({ length: r * n }, () => rng.next() * scale + 1e-3)
  const R = new Float64Array(p * n)
  const recon = () => {
    for (let i = 0; i < p; i++) for (let j = 0; j < n; j++) {
      let s = 0
      for (let k = 0; k < r; k++) s += W[i * r + k] * H[k * n + j]
      R[i * n + j] = s
    }
  }
  for (let it = 0; it < iters; it++) {
    recon()
    for (let k = 0; k < r; k++) for (let j = 0; j < n; j++) {
      let num = 0, den = 0
      for (let i = 0; i < p; i++) {
        const m = mask[i * n + j]
        num += W[i * r + k] * m * v[i * n + j]
        den += W[i * r + k] * m * R[i * n + j]
      }
      H[k * n + j] *= num / Math.max(den, 1e-10)
    }
    recon()
    for (let i = 0; i < p; i++) for (let k = 0; k < r; k++) {
      let num = 0, den = 0
      for (let j = 0; j < n; j++) {
        const m = mask[i * n + j]
        num += m * v[i * n + j] * H[k * n + j]
        den += m * R[i * n + j] * H[k * n + j]
      }
      W[i * r + k] *= num / Math.max(den, 1e-10)
    }
  }
  recon()
  return R
}

// ---------------------------------------------------------------------------
// hyper-parameter optimisation: the surfaces, the surrogate, the acquisitions
// ---------------------------------------------------------------------------
/** a plausible validation-AUC surface over (log10 learning rate, depth) */
export const valSurface = (le: number, dep: number) =>
  0.86 - 0.055 * (le + 1.5) ** 2 - 0.0022 * (dep - 6.0) ** 2 - 0.010 * (le + 1.5) * (dep - 6.0)

/** the expensive unknown of the Bayesian-optimisation slides */
export const boTarget = (x: number) => Math.sin(3 * Math.PI * x) * 0.45 + (x - 0.55) ** 2 * 3.2

/** the Cholesky factor of a symmetric positive-definite S */
export function cholesky(S: number[][]): number[][] {
  const n = S.length
  const L = S.map(() => new Array(n).fill(0))
  for (let i = 0; i < n; i++) for (let j = 0; j <= i; j++) {
    let s = S[i][j]
    for (let k = 0; k < j; k++) s -= L[i][k] * L[j][k]
    L[i][j] = i === j ? Math.sqrt(Math.max(s, 1e-12)) : s / L[j][j]
  }
  return L
}

/** z = L^-1 b, forward substitution */
function forward(L: number[][], b: number[]): number[] {
  const z = new Array(b.length).fill(0)
  for (let i = 0; i < b.length; i++) { let s = b[i]; for (let k = 0; k < i; k++) s -= L[i][k] * z[k]; z[i] = s / L[i][i] }
  return z
}

/** x = L^-T z, back substitution */
function backward(L: number[][], z: number[]): number[] {
  const n = z.length
  const x = new Array(n).fill(0)
  for (let i = n - 1; i >= 0; i--) { let s = z[i]; for (let k = i + 1; k < n; k++) s -= L[k][i] * x[k]; x[i] = s / L[i][i] }
  return x
}

/** A Gaussian-process posterior: the mean, and amp * the posterior sd.
 *  The same squared-exponential kernel as the printed figures. */
export function gp(
  xs: number[][], ys: number[], grid: number[][], ell: number[], sig = 0.09, amp = 0.55,
): { mu: number[]; sd: number[] } {
  const k = (a: number[], b: number[]) => {
    let s = 0
    for (let d = 0; d < a.length; d++) s += ((a[d] - b[d]) / ell[d]) ** 2
    return Math.exp(-s / 2)
  }
  const n = xs.length
  if (!n) return { mu: grid.map(() => 0), sd: grid.map(() => amp) }
  const L = cholesky(xs.map((a, i) => xs.map((b, j) => k(a, b) + (i === j ? sig * sig : 0))))
  const alpha = backward(L, forward(L, ys))
  const mu: number[] = []
  const sd: number[] = []
  for (const g of grid) {
    const kv = xs.map((a) => k(g, a))
    let m = 0
    for (let i = 0; i < n; i++) m += kv[i] * alpha[i]
    // k' K^-1 k = |L^-1 k|^2
    const v = forward(L, kv)
    let q = 0
    for (let i = 0; i < n; i++) q += v[i] * v[i]
    mu.push(m)
    sd.push(amp * Math.sqrt(Math.max(1 - q, 1e-6)))
  }
  return { mu, sd }
}

export const normPdf = (z: number) => Math.exp(-0.5 * z * z) / Math.sqrt(2 * Math.PI)
/** Abramowitz and Stegun 7.1.26 */
export function normCdf(z: number): number {
  const t = 1 / (1 + 0.3275911 * Math.abs(z) / Math.SQRT2)
  const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t
    * Math.exp(-(z * z) / 2)
  return z >= 0 ? 0.5 * (1 + y) : 0.5 * (1 - y)
}

/** expected improvement below the best (lowest) score so far */
export function ei(mu: number, sd: number, best: number, xi = 0): number {
  const s = Math.max(sd, 1e-9)
  const z = (best - mu - xi) / s
  return (best - mu - xi) * normCdf(z) + s * normPdf(z)
}

/** lower confidence bound, negated so that larger is better, as UCB */
export const ucb = (mu: number, sd: number, kappa: number) => -(mu - kappa * sd)

export function argmax(v: number[]): number {
  let b = 0
  for (let i = 1; i < v.length; i++) if (v[i] > v[b]) b = i
  return b
}
export function argmin(v: number[]): number {
  let b = 0
  for (let i = 1; i < v.length; i++) if (v[i] < v[b]) b = i
  return b
}

export const mean = (v: number[]) => v.reduce((a, b) => a + b, 0) / v.length
export const std = (v: number[]) => { const m = mean(v); return Math.sqrt(mean(v.map((x) => (x - m) ** 2))) }

/** a fitted polynomial as a LineChart series, sampled on [0, 1] */
export const polyPoints = (w: number[], n = 300): [number, number][] =>
  linspace(0, 1, n).map((x) => [x, polyEval(w, x)])
export const truthPoints: [number, number][] = linspace(0, 1, 300).map((x) => [x, truth(x)])
export const ringDots = (s: Sample, color: string, r = 4.5) =>
  s.x.map((x, i) => ({ x, y: s.t[i], color, r, hollow: true }))

/** a value in plain words: 2.0e-5 as 2·10⁻⁵ */
const SUP: Record<string, string> = { '-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹' }
export function sci(v: number, digits = 1): string {
  if (v === 0) return '0'
  const e = Math.floor(Math.log10(Math.abs(v)))
  if (e >= -2 && e <= 3) return v.toFixed(Math.max(0, digits - e))
  const m = v / 10 ** e
  const ms = Math.abs(m - 1) < 0.05 ? '' : `${m.toFixed(digits)}·`
  return `${ms}10${String(e).split('').map((c) => SUP[c]).join('')}`
}
