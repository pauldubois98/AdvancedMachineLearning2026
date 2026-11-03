// The algorithms of the lecture, written out once, the way
// scripts/make_figures_c06.py writes them: every live slide runs these.
// 1-D mixtures keep parameters as plain arrays; 2-D covariances are stored as
// [a, b, c] for the symmetric matrix [[a, b], [b, c]].
import { Rng } from './rng'

export const EPS = 1e-12

// ---------------------------------------------------------------------------
// one dimension
// ---------------------------------------------------------------------------
export interface Mix1 { p: number[]; mu: number[]; sd: number[] }
export interface Step1 extends Mix1 { ll: number }

export function normPdf(x: number, mu: number, sd: number): number {
  const z = (x - mu) / sd
  return Math.exp(-0.5 * z * z) / (sd * Math.sqrt(2 * Math.PI))
}

/** p_k f_k(x), one entry per component */
export function weighted1(x: number, m: Mix1): number[] {
  return m.p.map((pk, k) => pk * normPdf(x, m.mu[k], m.sd[k]))
}

export function mixPdf1(x: number, m: Mix1): number {
  return weighted1(x, m).reduce((a, b) => a + b, 0)
}

/** gamma_k(x) = P(Z = k | x): Bayes' rule, point by point */
export function resp1(x: number, m: Mix1): number[] {
  const w = weighted1(x, m)
  const s = Math.max(w.reduce((a, b) => a + b, 0), EPS)
  return w.map((v) => v / s)
}

export function loglik1(x: ArrayLike<number>, m: Mix1): number {
  let s = 0
  for (let i = 0; i < x.length; i++) s += Math.log(Math.max(mixPdf1(x[i], m), EPS))
  return s
}

const clone1 = (m: Mix1): Mix1 => ({ p: [...m.p], mu: [...m.mu], sd: [...m.sd] })

/** The M-step from a table of weights w[i][k] (responsibilities, or the
 *  share of drawn labels): weighted shares, means and widths. */
function mstep1(x: ArrayLike<number>, w: number[][], K: number, floor: number): Mix1 {
  const n = x.length
  const nk = new Array(K).fill(0)
  const sx = new Array(K).fill(0)
  for (let i = 0; i < n; i++) for (let k = 0; k < K; k++) { nk[k] += w[i][k]; sx[k] += w[i][k] * x[i] }
  const mu = sx.map((s, k) => s / Math.max(nk[k], EPS))
  const v = new Array(K).fill(0)
  for (let i = 0; i < n; i++) for (let k = 0; k < K; k++) v[k] += w[i][k] * (x[i] - mu[k]) ** 2
  return {
    p: nk.map((a) => a / n),
    mu,
    sd: v.map((a, k) => Math.max(Math.sqrt(a / Math.max(nk[k], EPS)), floor)),
  }
}

/** A random start: K sample points as centres, the sample's spread as width. */
export function start1(x: ArrayLike<number>, K: number, seed: number): Mix1 {
  const rng = new Rng(seed)
  const n = x.length
  let mean = 0
  for (let i = 0; i < n; i++) mean += x[i]
  mean /= n
  let v = 0
  for (let i = 0; i < n; i++) v += (x[i] - mean) ** 2
  const sd = Math.sqrt(v / n)
  const picked = new Set<number>()
  while (picked.size < Math.min(K, n)) picked.add(Math.floor(rng.next() * n))
  const mu = [...picked].map((i) => x[i]).sort((a, b) => a - b)
  return { p: new Array(K).fill(1 / K), mu, sd: new Array(K).fill(sd) }
}

/** EM for a 1-D Gaussian mixture; the whole history, iterate 0 first. */
export function em1(x: ArrayLike<number>, start: Mix1, iters: number, floor = 1e-2): Step1[] {
  let m = clone1(start)
  const K = m.p.length
  const hist: Step1[] = []
  // one density evaluation per point and pass: the E-step's normaliser is
  // the mixture density, so the log-likelihood of theta^t comes for free
  for (let t = 0; ; t++) {
    const g: number[][] = []
    let ll = 0
    for (let i = 0; i < x.length; i++) {
      const w = weighted1(x[i], m)
      const s = w.reduce((a, b) => a + b, 0)
      ll += Math.log(Math.max(s, EPS))
      g.push(w.map((v) => v / Math.max(s, EPS)))
    }
    hist.push({ ...clone1(m), ll })
    if (t === iters) break
    m = mstep1(x, g, K, floor)
  }
  return hist
}

/** Stochastic EM: N labels drawn per point (N = 1 is SEM), each class
 *  weighted by its share of the draws. hard = true takes the arg max
 *  instead: classification EM, which is k-means with widths. */
export function sem1(
  x: ArrayLike<number>, start: Mix1, iters: number,
  opts: { seed?: number; N?: number; hard?: boolean; floor?: number } = {},
): (Step1 & { z: Int32Array | null })[] {
  const { seed = 5, N = 1, hard = false, floor = 1e-2 } = opts
  const rng = new Rng(seed)
  let m = clone1(start)
  const K = m.p.length
  const n = x.length
  const hist: (Step1 & { z: Int32Array | null })[] = [{ ...clone1(m), ll: loglik1(x, m), z: null }]
  for (let t = 0; t < iters; t++) {
    const w: number[][] = []
    const z = new Int32Array(n)
    for (let i = 0; i < n; i++) {
      const g = resp1(x[i], m)
      const row = new Array(K).fill(0)
      if (hard) {
        const k = g.indexOf(Math.max(...g))
        row[k] = 1
        z[i] = k
      } else {
        for (let j = 0; j < N; j++) {
          const u = rng.next()
          let k = 0
          let c = g[0]
          while (k < K - 1 && c < u) { k++; c += g[k] }
          row[k] += 1 / N
          if (j === 0) z[i] = k
        }
      }
      w.push(row)
    }
    // an emptied class is restarted on two random points
    for (let k = 0; k < K; k++) {
      let s = 0
      for (let i = 0; i < n; i++) s += w[i][k]
      if (s < 2) for (let r = 0; r < 2; r++) w[Math.floor(rng.next() * n)][k] = 1
    }
    m = mstep1(x, w, K, floor)
    const ps = m.p.reduce((a, b) => a + b, 0)
    m.p = m.p.map((v) => v / ps)
    hist.push({ ...clone1(m), ll: loglik1(x, m), z })
  }
  return hist
}

// ---------------------------------------------------------------------------
// two dimensions
// ---------------------------------------------------------------------------
export type Pt = [number, number]
export type Cov = [number, number, number]
export interface Mix2 { p: number[]; mu: Pt[]; S: Cov[] }
export interface Step2 extends Mix2 { ll: number }
export type CovFamily = 'full' | 'diag' | 'spherical' | 'tied'

export function mvnPdf(x: Pt, mu: Pt, S: Cov): number {
  const [a, b, c] = S
  const det = Math.max(a * c - b * b, EPS)
  const dx = x[0] - mu[0]
  const dy = x[1] - mu[1]
  const q = (c * dx * dx - 2 * b * dx * dy + a * dy * dy) / det
  return Math.exp(-0.5 * q) / (2 * Math.PI * Math.sqrt(det))
}

export function mixPdf2(x: Pt, m: Mix2): number {
  let s = 0
  for (let k = 0; k < m.p.length; k++) s += m.p[k] * mvnPdf(x, m.mu[k], m.S[k])
  return s
}

export function resp2(x: Pt, m: Mix2): number[] {
  const w = m.p.map((pk, k) => pk * mvnPdf(x, m.mu[k], m.S[k]))
  const s = Math.max(w.reduce((a, b) => a + b, 0), EPS)
  return w.map((v) => v / s)
}

export function loglik2(X: Pt[], m: Mix2): number {
  let s = 0
  for (const x of X) s += Math.log(Math.max(mixPdf2(x, m), EPS))
  return s
}

export function argmax(v: number[]): number {
  let b = 0
  for (let k = 1; k < v.length; k++) if (v[k] > v[b]) b = k
  return b
}

const clone2 = (m: Mix2): Mix2 => ({
  p: [...m.p], mu: m.mu.map((v) => [...v] as Pt), S: m.S.map((v) => [...v] as Cov),
})

function sampleCov(X: Pt[]): Cov {
  const n = X.length
  let mx = 0, my = 0
  for (const [x, y] of X) { mx += x; my += y }
  mx /= n; my /= n
  let a = 0, b = 0, c = 0
  for (const [x, y] of X) { a += (x - mx) ** 2; b += (x - mx) * (y - my); c += (y - my) ** 2 }
  return [a / n, b / n, c / n]
}

/** K sample points as centres, a shrunk copy of the sample covariance as
 *  every component's shape: the random start of the deck. */
export function start2(X: Pt[], K: number, seed: number, reg = 1e-4): Mix2 {
  const rng = new Rng(seed)
  const picked = new Set<number>()
  while (picked.size < Math.min(K, X.length)) picked.add(Math.floor(rng.next() * X.length))
  const C = sampleCov(X)
  const S0: Cov = [C[0] * 0.6 + reg, C[1] * 0.6, C[2] * 0.6 + reg]
  return {
    p: new Array(K).fill(1 / K),
    mu: [...picked].map((i) => [...X[i]] as Pt),
    S: new Array(K).fill(0).map(() => [...S0] as Cov),
  }
}

/** The weighted M-step, then the covariance family's constraint. */
export function mstep2(X: Pt[], g: number[][], K: number, cov: CovFamily = 'full', reg = 1e-4): Mix2 {
  const n = X.length
  const nk = new Array(K).fill(0)
  const mu: Pt[] = new Array(K).fill(0).map(() => [0, 0])
  for (let i = 0; i < n; i++) for (let k = 0; k < K; k++) {
    nk[k] += g[i][k]
    mu[k][0] += g[i][k] * X[i][0]
    mu[k][1] += g[i][k] * X[i][1]
  }
  for (let k = 0; k < K; k++) { const d = Math.max(nk[k], EPS); mu[k][0] /= d; mu[k][1] /= d }
  let S: Cov[] = new Array(K).fill(0).map(() => [0, 0, 0] as Cov)
  for (let i = 0; i < n; i++) for (let k = 0; k < K; k++) {
    const dx = X[i][0] - mu[k][0]
    const dy = X[i][1] - mu[k][1]
    S[k][0] += g[i][k] * dx * dx
    S[k][1] += g[i][k] * dx * dy
    S[k][2] += g[i][k] * dy * dy
  }
  S = S.map((s, k) => {
    const d = Math.max(nk[k], EPS)
    return [s[0] / d + reg, s[1] / d, s[2] / d + reg] as Cov
  })
  if (cov === 'diag') S = S.map((s) => [s[0], 0, s[2]] as Cov)
  else if (cov === 'spherical') S = S.map((s) => { const v = (s[0] + s[2]) / 2; return [v, 0, v] as Cov })
  else if (cov === 'tied') {
    const T: Cov = [0, 0, 0]
    for (let k = 0; k < K; k++) for (let j = 0; j < 3; j++) T[j] += (nk[k] / n) * S[k][j]
    S = S.map(() => [...T] as Cov)
  }
  return { p: nk.map((a) => a / n), mu, S }
}

export function em2(
  X: Pt[], start: Mix2, iters: number, opts: { cov?: CovFamily; reg?: number } = {},
): Step2[] {
  const { cov = 'full', reg = 1e-4 } = opts
  let m = clone2(start)
  const K = m.p.length
  const hist: Step2[] = []
  for (let t = 0; ; t++) {
    let ll = 0
    const g = X.map((x) => {
      const w = m.p.map((pk, k) => pk * mvnPdf(x, m.mu[k], m.S[k]))
      const s = w.reduce((a, b) => a + b, 0)
      ll += Math.log(Math.max(s, EPS))
      return w.map((v) => v / Math.max(s, EPS))
    })
    hist.push({ ...clone2(m), ll })
    if (t === iters) break
    m = mstep2(X, g, K, cov, reg)
  }
  return hist
}

/** Lloyd's k-means, best of nInit random starts by inertia. */
export function kmeans(X: Pt[], K: number, seed = 0, nInit = 10, iters = 100) {
  const rng = new Rng(seed)
  let best = { centers: [] as Pt[], labels: new Int32Array(X.length), inertia: Infinity }
  for (let r = 0; r < nInit; r++) {
    const picked = new Set<number>()
    while (picked.size < K) picked.add(Math.floor(rng.next() * X.length))
    let C = [...picked].map((i) => [...X[i]] as Pt)
    const lab = new Int32Array(X.length)
    for (let t = 0; t < iters; t++) {
      let moved = false
      X.forEach((x, i) => {
        let bk = 0, bd = Infinity
        C.forEach((c, k) => { const d = (x[0] - c[0]) ** 2 + (x[1] - c[1]) ** 2; if (d < bd) { bd = d; bk = k } })
        if (lab[i] !== bk || t === 0) { moved = moved || lab[i] !== bk; lab[i] = bk }
      })
      const next = C.map(() => [0, 0, 0])
      X.forEach((x, i) => { next[lab[i]][0] += x[0]; next[lab[i]][1] += x[1]; next[lab[i]][2]++ })
      C = next.map((s, k) => (s[2] ? [s[0] / s[2], s[1] / s[2]] : C[k]) as Pt)
      if (!moved && t > 0) break
    }
    let inertia = 0
    X.forEach((x, i) => { inertia += (x[0] - C[lab[i]][0]) ** 2 + (x[1] - C[lab[i]][1]) ** 2 })
    if (inertia < best.inertia) best = { centers: C, labels: lab, inertia }
  }
  return best
}

/** The deck's recommended start: k-means centroids, its clusters' shares and
 *  covariances. */
export function kmeansStart(X: Pt[], K: number, seed = 0, reg = 1e-4, nInit = 10): Mix2 {
  const km = kmeans(X, K, seed, nInit)
  const g = X.map((_, i) => { const r = new Array(K).fill(0); r[km.labels[i]] = 1; return r })
  return mstep2(X, g, K, 'full', reg)
}

/** The axes of the ellipse {x : (x - mu)' S^-1 (x - mu) = 1}: half-lengths
 *  and the angle of the long one. */
export function ellipseAxes(S: Cov): { r1: number; r2: number; angle: number } {
  const [a, b, c] = S
  const tr = (a + c) / 2
  const disc = Math.sqrt(((a - c) / 2) ** 2 + b * b)
  const l1 = tr + disc
  const l2 = Math.max(tr - disc, 0)
  const angle = Math.abs(b) < 1e-12 ? (a >= c ? 0 : Math.PI / 2) : Math.atan2(l1 - a, b)
  return { r1: Math.sqrt(l1), r2: Math.sqrt(l2), angle }
}

// ---------------------------------------------------------------------------
// samples
// ---------------------------------------------------------------------------
/** The table of the 2023 lecture: lengths of small animals collected in two
 *  regions, and how many animals had each length. */
export const ANIMAL_LENGTH = [82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 98]
export const ANIMAL_COUNT = [5, 3, 12, 36, 55, 45, 21, 13, 15, 34, 59, 48, 16, 12, 6, 1]

/** the same table, one number per animal */
export const ANIMALS: number[] = ANIMAL_LENGTH.flatMap((l, i) => new Array(ANIMAL_COUNT[i]).fill(l))

/** a two-component fit of the animals, from the start the deck uses */
export const ANIMAL_FIT: Mix1 = (() => {
  const h = em1(ANIMALS, { p: [0.5, 0.5], mu: [84, 95], sd: [3, 3] }, 300)
  const m = h[h.length - 1]
  return { p: m.p, mu: m.mu, sd: m.sd }
})()

export function drawMvn(rng: Rng, mu: Pt, S: Cov): Pt {
  // Cholesky of [[a, b], [b, c]]
  const l11 = Math.sqrt(S[0])
  const l21 = S[1] / l11
  const l22 = Math.sqrt(Math.max(S[2] - l21 * l21, 0))
  const u = rng.normal()
  const v = rng.normal()
  return [mu[0] + l11 * u, mu[1] + l21 * u + l22 * v]
}

export function drawClass(rng: Rng, p: readonly number[]): number {
  const u = rng.next()
  let c = 0
  for (let k = 0; k < p.length; k++) { c += p[k]; if (u < c) return k }
  return p.length - 1
}

/** n points from a 2-D mixture, with the labels the generator knows */
export function sampleMix2(m: Mix2, n: number, seed: number): { X: Pt[]; z: number[] } {
  const rng = new Rng(seed)
  const X: Pt[] = []
  const z: number[] = []
  for (let i = 0; i < n; i++) {
    const k = drawClass(rng, m.p)
    z.push(k)
    X.push(drawMvn(rng, m.mu[k], m.S[k]))
  }
  return { X, z }
}

/** Two elongated, overlapping clusters: the shape EM separates and k-means
 *  cannot. */
export const TWO_BLOBS: Mix2 = {
  p: [0.55, 0.45],
  mu: [[-1.05, -0.35], [1.15, 0.55]],
  S: [[0.95, 0.52, 0.40], [0.70, -0.46, 0.52]],
}

export const THREE_BLOBS: Mix2 = {
  p: [0.38, 0.32, 0.30],
  mu: [[-1.5, 0.9], [1.5, 1.0], [0.1, -1.3]],
  S: [[0.55, 0.30, 0.30], [0.40, -0.26, 0.55], [0.90, 0.05, 0.22]],
}

/** five clusters, two of them close: a random start sometimes merges a pair */
export const FIVE_BLOBS: Mix2 = {
  p: [0.30, 0.20, 0.20, 0.20, 0.10],
  mu: [[-2.2, 1.2], [-1.9, -1.0], [0.4, 1.6], [1.9, -0.6], [2.4, 1.4]],
  S: [[0.35, 0.20, 0.25], [0.50, -0.30, 0.40], [0.25, 0, 0.50], [0.60, 0.25, 0.30], [0.20, 0, 0.20]],
}

/** a skewed, heavy-shouldered target no single Gaussian reaches: a gamma
 *  bump and a narrow normal one */
export function skewedSample(n: number, seed: number): number[] {
  const rng = new Rng(seed)
  const out: number[] = []
  const n1 = Math.floor(0.7 * n)
  for (let i = 0; i < n1; i++) {
    // gamma(2, 0.9) as the sum of two exponentials
    out.push(-0.9 * (Math.log(1 - rng.next()) + Math.log(1 - rng.next())))
  }
  for (let i = n1; i < n; i++) out.push(rng.normal(7.5, 0.55))
  return out
}

/** evenly spaced values, both ends included */
export function linspace(a: number, b: number, n: number): number[] {
  return Array.from({ length: n }, (_, i) => a + ((b - a) * i) / (n - 1))
}

/** a histogram, normalised to a density when `density` is set */
export function histogram(x: ArrayLike<number>, edges: number[], density = false): number[] {
  const h = new Array(edges.length - 1).fill(0)
  for (let i = 0; i < x.length; i++) {
    for (let j = 0; j < h.length; j++) {
      if (x[i] >= edges[j] && x[i] < edges[j + 1]) { h[j]++; break }
    }
  }
  if (!density) return h
  return h.map((c, j) => c / (x.length * (edges[j + 1] - edges[j])))
}
