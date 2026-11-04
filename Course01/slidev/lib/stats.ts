// The statistics the live figures run on: densities, 2-D Gaussians and their
// discriminants, logistic regression, k-means. Small and explicit, in the
// spirit of the lab notebooks.
import { Rng } from './rng'
import type { Cov, Pt } from './geom'

export const SQ2PI = Math.sqrt(2 * Math.PI)
export const npdf = (x: number, mu = 0, sd = 1) => Math.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * SQ2PI)
export const lognpdf = (x: number, mu = 0, sd = 1) => -0.5 * ((x - mu) / sd) ** 2 - Math.log(sd * SQ2PI)

export const mean = (x: ArrayLike<number>) => { let s = 0; for (let i = 0; i < x.length; i++) s += x[i]; return s / x.length }
/** the variance with divisor n (ddof 0), as numpy's std() */
export function pvar(x: ArrayLike<number>) {
  const m = mean(x); let s = 0
  for (let i = 0; i < x.length; i++) s += (x[i] - m) ** 2
  return s / x.length
}

export const normals = (rng: Rng, n: number, mu = 0, sd = 1) => Array.from({ length: n }, () => rng.normal(mu, sd))

/** n draws of N(mu, S) */
export function mvn(rng: Rng, n: number, mu: Pt, S: Cov): Pt[] {
  const [a, b, c] = S
  const l11 = Math.sqrt(a), l21 = b / l11, l22 = Math.sqrt(Math.max(c - l21 * l21, 1e-12))
  return Array.from({ length: n }, () => {
    const u = rng.normal(), v = rng.normal()
    return [mu[0] + l11 * u, mu[1] + l21 * u + l22 * v] as Pt
  })
}

/** two labelled Gaussian classes, as _two_gaussians in make_figures_c01.py */
export function twoGaussians(rng: Rng, n: number, mu1: Pt = [-1.1, -0.5], mu2: Pt = [1.3, 0.7],
  cov1: Cov = [1.0, 0.35, 0.7], cov2: Cov = cov1, n2 = n) {
  const X = [...mvn(rng, n, mu1, cov1), ...mvn(rng, n2, mu2, cov2)]
  const y = [...Array(n).fill(0), ...Array(n2).fill(1)] as number[]
  return { X, y }
}

// --- 2 x 2 algebra ----------------------------------------------------------
export const det2 = ([a, b, c]: Cov) => a * c - b * b
export const inv2 = ([a, b, c]: Cov): Cov => { const d = a * c - b * b; return [c / d, -b / d, a / d] }
export const quad = ([a, b, c]: Cov, x: number, y: number) => a * x * x + 2 * b * x * y + c * y * y
export const mulv = ([a, b, c]: Cov, v: Pt): Pt => [a * v[0] + b * v[1], b * v[0] + c * v[1]]

/** the class means, covariances (ddof 1), the pooled one and the priors */
export function classStats(X: Pt[], y: number[], K = 2) {
  const mu: Pt[] = [], S: Cov[] = [], n: number[] = []
  const pooled: Cov = [0, 0, 0]
  for (let k = 0; k < K; k++) {
    const P = X.filter((_, i) => y[i] === k)
    const m: Pt = [mean(P.map((p) => p[0])), mean(P.map((p) => p[1]))]
    const s: Cov = [0, 0, 0]
    for (const p of P) {
      const dx = p[0] - m[0], dy = p[1] - m[1]
      s[0] += dx * dx; s[1] += dx * dy; s[2] += dy * dy
    }
    for (let j = 0; j < 3; j++) { pooled[j] += s[j]; s[j] /= Math.max(P.length - 1, 1) }
    mu.push(m); S.push(s); n.push(P.length)
  }
  const N = X.length
  for (let j = 0; j < 3; j++) pooled[j] /= Math.max(N - K, 1)
  return { mu, S, pooled, pi: n.map((v) => v / N), n }
}

/** log( f_k(x) pi_k ) for a Gaussian class */
export function gaussScore(mu: Pt, S: Cov, pi: number) {
  const Si = inv2(S), ld = Math.log(det2(S))
  return (x: number, y: number) => -0.5 * quad(Si, x - mu[0], y - mu[1]) - 0.5 * ld + Math.log(pi)
}

/** delta_2 - delta_1: positive where class 2 (index 1) wins */
export function discriminant(mu: Pt[], S: Cov[], pi: number[]) {
  const a = gaussScore(mu[0], S[0], pi[0]), b = gaussScore(mu[1], S[1], pi[1])
  return (x: number, y: number) => b(x, y) - a(x, y)
}

export const accuracy = (f: (x: number, y: number) => number, X: Pt[], y: number[]) =>
  X.reduce((s, p, i) => s + ((f(p[0], p[1]) > 0 ? 1 : 0) === y[i] ? 1 : 0), 0) / X.length

/** logistic regression by Newton's method (IRLS), with a whisper of ridge */
export function logistic(X: Pt[], y: number[], iters = 25) {
  let w = [0, 0, 0] // bias, w1, w2
  for (let it = 0; it < iters; it++) {
    const g = [0, 0, 0]
    const H = [[1e-4, 0, 0], [0, 1e-4, 0], [0, 0, 1e-4]]
    for (let i = 0; i < X.length; i++) {
      const f = [1, X[i][0], X[i][1]]
      const p = 1 / (1 + Math.exp(-(w[0] + w[1] * f[1] + w[2] * f[2])))
      const r = p * (1 - p)
      for (let a = 0; a < 3; a++) {
        g[a] += (p - y[i]) * f[a]
        for (let b = 0; b < 3; b++) H[a][b] += r * f[a] * f[b]
      }
    }
    const step = solve3(H, g)
    w = w.map((v, a) => v - step[a])
  }
  return (x: number, yy: number) => w[0] + w[1] * x + w[2] * yy
}

export function solve3(A: number[][], b: number[]): number[] {
  const M = A.map((r, i) => [...r, b[i]])
  for (let c = 0; c < 3; c++) {
    let p = c
    for (let r = c + 1; r < 3; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r
    ;[M[c], M[p]] = [M[p], M[c]]
    for (let r = 0; r < 3; r++) if (r !== c) {
      const f = M[r][c] / M[c][c]
      for (let k = c; k < 4; k++) M[r][k] -= f * M[c][k]
    }
  }
  return M.map((r, i) => r[3] / r[i])
}

// --- k-means ---------------------------------------------------------------------
export const nearestCentre = (p: Pt, mu: Pt[]) => {
  let best = 0, bd = Infinity
  mu.forEach((m, k) => { const d = (p[0] - m[0]) ** 2 + (p[1] - m[1]) ** 2; if (d < bd) { bd = d; best = k } })
  return best
}
export const assign = (X: Pt[], mu: Pt[]) => X.map((p) => nearestCentre(p, mu))
export function update(X: Pt[], s: number[], mu: Pt[]): Pt[] {
  return mu.map((m, k) => {
    const P = X.filter((_, i) => s[i] === k)
    return P.length ? [mean(P.map((p) => p[0])), mean(P.map((p) => p[1]))] as Pt : m
  })
}
export const inertia = (X: Pt[], s: number[], mu: Pt[]) =>
  X.reduce((t, p, i) => t + (p[0] - mu[s[i]][0]) ** 2 + (p[1] - mu[s[i]][1]) ** 2, 0)

/** k-means++ starts, then Lloyd to convergence; the best of `restarts` */
export function kmeans(X: Pt[], K: number, seed = 0, restarts = 8) {
  const rng = new Rng(seed + 1)
  let best = { s: [] as number[], mu: [] as Pt[], J: Infinity }
  for (let r = 0; r < restarts; r++) {
    const mu: Pt[] = [X[Math.floor(rng.next() * X.length)]]
    while (mu.length < K) {
      const d = X.map((p) => Math.min(...mu.map((m) => (p[0] - m[0]) ** 2 + (p[1] - m[1]) ** 2)))
      let u = rng.next() * d.reduce((a, b) => a + b, 0), i = 0
      while (i < X.length - 1 && (u -= d[i]) > 0) i++
      mu.push(X[i])
    }
    let c = mu, s = assign(X, c)
    for (let it = 0; it < 100; it++) {
      const c2 = update(X, s, c)
      const s2 = assign(X, c2)
      c = c2
      if (s2.every((v, i) => v === s[i])) { s = s2; break }
      s = s2
    }
    const J = inertia(X, s, c)
    if (J < best.J) best = { s, mu: c, J }
  }
  return best
}

/** scikit-learn's make_moons, with our generator */
export function moons(rng: Rng, n: number, noise: number) {
  const a = Math.ceil(n / 2), b = n - a
  const X: Pt[] = []
  const y: number[] = []
  for (let i = 0; i < a; i++) { const t = (Math.PI * i) / (a - 1); X.push([Math.cos(t), Math.sin(t)]); y.push(0) }
  for (let i = 0; i < b; i++) { const t = (Math.PI * i) / (b - 1); X.push([1 - Math.cos(t), 1 - Math.sin(t) - 0.5]); y.push(1) }
  return { X: X.map(([u, v]) => [u + rng.normal(0, noise), v + rng.normal(0, noise)] as Pt), y }
}

// --- n-D Gaussians, for the LDA/QDA learning curve ---------------------------------
/** Cholesky of a symmetric positive definite matrix */
export function chol(A: number[][]): number[][] {
  const d = A.length
  const L = A.map(() => new Array(d).fill(0))
  for (let i = 0; i < d; i++)
    for (let j = 0; j <= i; j++) {
      let s = A[i][j]
      for (let k = 0; k < j; k++) s -= L[i][k] * L[j][k]
      L[i][j] = i === j ? Math.sqrt(Math.max(s, 1e-12)) : s / L[j][j]
    }
  return L
}
/** solve L z = v (forward substitution) */
export function fwd(L: number[][], v: number[]): number[] {
  const z = new Array(v.length).fill(0)
  for (let i = 0; i < v.length; i++) {
    let s = v[i]
    for (let k = 0; k < i; k++) s -= L[i][k] * z[k]
    z[i] = s / L[i][i]
  }
  return z
}
