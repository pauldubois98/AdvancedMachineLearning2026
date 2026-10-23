// NMF, written out once: the multiplicative updates for the three losses of
// the deck (with the weighted and the regularized variants), ALS and HALS,
// and the five initializations. A transcription of the algorithms in
// scripts/make_figures_c05.py, so a slider here moves the very method the
// printed figure ran.
import { Mat, clone, mat, mul, mult, norm, solveSPD, tmul, topSvd } from './mat'
import { Rng } from './rng'

export const EPS = 1e-10

export type Loss = 'fro' | 'kl' | 'is'
export type Init = 'random' | 'constant' | 'nndsvd' | 'cols' | 'kmeans'
export type Algo = 'mu' | 'als' | 'hals'

export interface Fit { W: Mat; H: Mat }

export interface MuOpts {
  loss?: Loss
  /** Σ: 1 where an entry counts, 0 where it is missing */
  mask?: Mat | null
  /** λ ‖H‖₁, μ/2 ‖H‖², ν/2 ‖W‖² */
  lam?: number
  mu?: number
  nu?: number
}

function meanOf(X: Mat): number {
  let s = 0
  for (const v of X.a) s += v
  return s / X.a.length
}

// ------------------------------------------------------------------ inits
export function init(X: Mat, r: number, how: Init = 'random', seed = 0): Fit {
  const { r: p, c: n } = X
  if (how === 'constant') {
    const v = Math.sqrt(Math.max(meanOf(X), EPS) / r)
    return { W: mat(p, r, v), H: mat(r, n, v) }
  }
  if (how === 'nndsvd') return nndsvd(X, r)
  const rng = new Rng(seed * 7919 + 13)
  if (how === 'cols') {
    const idx: number[] = []
    while (idx.length < r) {
      const j = Math.floor(rng.next() * n)
      if (!idx.includes(j)) idx.push(j)
    }
    const W = mat(p, r)
    for (let i = 0; i < p; i++) idx.forEach((j, k) => { W.a[i * r + k] = Math.max(X.a[i * n + j], 1e-4) })
    const H = mat(r, n)
    for (let i = 0; i < H.a.length; i++) H.a[i] = (0.5 + rng.next()) / r
    return { W, H }
  }
  if (how === 'kmeans') return kmeansInit(X, r, rng)
  const scale = meanOf(X) > 0 ? Math.sqrt(meanOf(X) / r) : 1
  const W = mat(p, r)
  const H = mat(r, n)
  for (let i = 0; i < W.a.length; i++) W.a[i] = rng.next() * scale + 1e-3
  for (let i = 0; i < H.a.length; i++) H.a[i] = rng.next() * scale + 1e-3
  return { W, H }
}

function nndsvd(X: Mat, r: number): Fit {
  const { r: p, c: n } = X
  const { U, s, V } = topSvd(X, r)
  const W = mat(p, r)
  const H = mat(r, n)
  for (let k = 0; k < r; k++) {
    const u = Array.from({ length: p }, (_, i) => U.a[i * r + k])
    const v = Array.from({ length: n }, (_, j) => V.a[j * r + k])
    const nrm = (a: number[]) => Math.sqrt(a.reduce((t, x) => t + x * x, 0))
    let uu: number[]
    let vv: number[]
    let sc: number
    if (k === 0) {
      uu = u.map(Math.abs); vv = v.map(Math.abs); sc = s[0]
      const nu = nrm(uu), nv = nrm(vv)
      uu = uu.map((x) => x / nu); vv = vv.map((x) => x / nv)
    } else {
      const up = u.map((x) => Math.max(x, 0)), un = u.map((x) => Math.max(-x, 0))
      const vp = v.map((x) => Math.max(x, 0)), vn = v.map((x) => Math.max(-x, 0))
      const mp = nrm(up) * nrm(vp), mn = nrm(un) * nrm(vn)
      if (mp >= mn) { uu = up.map((x) => x / (nrm(up) + EPS)); vv = vp.map((x) => x / (nrm(vp) + EPS)); sc = s[k] * mp }
      else { uu = un.map((x) => x / (nrm(un) + EPS)); vv = vn.map((x) => x / (nrm(vn) + EPS)); sc = s[k] * mn }
    }
    const g = Math.sqrt(sc)
    for (let i = 0; i < p; i++) W.a[i * r + k] = Math.max(g * uu[i], 1e-4)
    for (let j = 0; j < n; j++) H.a[k * n + j] = Math.max(g * vv[j], 1e-4)
  }
  return { W, H }
}

function kmeansInit(X: Mat, r: number, rng: Rng): Fit {
  const { r: p, c: n } = X
  const colOf = (j: number) => Array.from({ length: p }, (_, i) => X.a[i * n + j])
  // k-means++ on the columns, then a few Lloyd sweeps
  let cent = [colOf(Math.floor(rng.next() * n))]
  const d2 = (a: number[], j: number) => a.reduce((s, v, i) => s + (v - X.a[i * n + j]) ** 2, 0)
  while (cent.length < r) {
    const dist = Array.from({ length: n }, (_, j) => Math.min(...cent.map((c) => d2(c, j))))
    let t = rng.next() * dist.reduce((s, v) => s + v, 0)
    let pick = n - 1
    for (let j = 0; j < n; j++) { t -= dist[j]; if (t <= 0) { pick = j; break } }
    cent.push(colOf(pick))
  }
  let lab = new Array(n).fill(0)
  for (let it = 0; it < 25; it++) {
    lab = Array.from({ length: n }, (_, j) => {
      let b = 0, bd = Infinity
      cent.forEach((c, k) => { const d = d2(c, j); if (d < bd) { bd = d; b = k } })
      return b
    })
    cent = cent.map((c, k) => {
      const m = lab.map((l, j) => (l === k ? j : -1)).filter((j) => j >= 0)
      if (!m.length) return c
      return Array.from({ length: p }, (_, i) => m.reduce((s, j) => s + X.a[i * n + j], 0) / m.length)
    })
  }
  const W = mat(p, r)
  for (let i = 0; i < p; i++) for (let k = 0; k < r; k++) W.a[i * r + k] = Math.max(cent[k][i], 1e-4)
  const H = mat(r, n, 1e-2)
  lab.forEach((k, j) => { H.a[k * n + j] = 1 })
  return { W, H }
}

// ----------------------------------------------------------------- losses
export function lossOf(X: Mat, f: Fit, loss: Loss = 'fro', mask: Mat | null = null): number {
  const Y = mul(f.W, f.H)
  let s = 0
  for (let i = 0; i < X.a.length; i++) {
    const x = X.a[i]
    const y = Math.max(Y.a[i], EPS)
    if (loss === 'fro') s += 0.5 * (mask ? mask.a[i] : 1) * (x - Y.a[i]) ** 2
    else if (loss === 'kl') s += (x > 0 ? x * Math.log(x / y) : 0) - x + y
    else { const q = Math.max(x, EPS) / y; s += q - Math.log(q) - 1 }
  }
  return s
}

export function relErr(X: Mat, f: Fit): number {
  const Y = mul(f.W, f.H)
  let s = 0
  for (let i = 0; i < X.a.length; i++) s += (X.a[i] - Y.a[i]) ** 2
  return Math.sqrt(s) / norm(X)
}

// ------------------------------------------------------- one pass of each
/** One pass of the multiplicative updates: H, then W. In place. */
export function muStep(X: Mat, f: Fit, o: MuOpts = {}) {
  const loss = o.loss ?? 'fro'
  const mask = o.mask ?? null
  const { W, H } = f
  if (loss !== 'fro') {
    let [A, B] = betaParts(X, W, H, loss)
    let num = tmul(W, A), den = tmul(W, B)
    for (let i = 0; i < H.a.length; i++) H.a[i] = Math.max((H.a[i] * num.a[i]) / Math.max(den.a[i], EPS), 1e-16)
    ;[A, B] = betaParts(X, W, H, loss)
    num = mult(A, H); den = mult(B, H)
    for (let i = 0; i < W.a.length; i++) W.a[i] = Math.max((W.a[i] * num.a[i]) / Math.max(den.a[i], EPS), 1e-16)
    return
  }
  const lam = o.lam ?? 0, mu = o.mu ?? 0, nu = o.nu ?? 0
  const MX = mask ? masked(X, mask) : X
  // H <- H . [W'(S.X) - lam]+ / (W'(S.WH) + mu H)
  let num = tmul(W, MX)
  let den = mask ? tmul(W, masked(mul(W, H), mask)) : mul(tmul(W, W), H)
  for (let i = 0; i < H.a.length; i++) {
    H.a[i] *= Math.max(num.a[i] - lam, 0) / Math.max(den.a[i] + mu * H.a[i], EPS)
  }
  // W <- W . (S.X)H' / ((S.WH)H' + nu W)
  num = mult(MX, H)
  den = mask ? mult(masked(mul(W, H), mask), H) : mul(W, mult(H, H))
  for (let i = 0; i < W.a.length; i++) W.a[i] *= num.a[i] / Math.max(den.a[i] + nu * W.a[i], EPS)
}

function masked(A: Mat, mask: Mat): Mat {
  const out = mat(A.r, A.c)
  for (let i = 0; i < A.a.length; i++) out.a[i] = mask.a[i] * A.a[i]
  return out
}

/** the two halves of the beta gradient: (WH)^(b-2).X and (WH)^(b-1),
 *  b = 1 (KL) or 0 (Itakura-Saito) */
function betaParts(X: Mat, W: Mat, H: Mat, loss: Loss): [Mat, Mat] {
  const Y = mul(W, H)
  const A = mat(X.r, X.c)
  const B = mat(X.r, X.c)
  for (let i = 0; i < X.a.length; i++) {
    const y = Math.max(Y.a[i], EPS)
    if (loss === 'kl') { A.a[i] = X.a[i] / y; B.a[i] = 1 }
    else { A.a[i] = X.a[i] / (y * y); B.a[i] = 1 / y }
  }
  return [A, B]
}

/** One HALS pass: every column of W, then every row of H, each exactly. */
export function halsStep(X: Mat, f: Fit) {
  const { W, H } = f
  const r = W.c
  const p = W.r
  const n = H.c
  const A = mult(X, H) // X Hᵀ, p x r
  const B = mult(H, H) // H Hᵀ, r x r
  for (let k = 0; k < r; k++) {
    const bkk = Math.max(B.a[k * r + k], EPS)
    for (let i = 0; i < p; i++) {
      let wb = 0
      for (let l = 0; l < r; l++) wb += W.a[i * r + l] * B.a[l * r + k]
      W.a[i * r + k] = Math.max(W.a[i * r + k] + (A.a[i * r + k] - wb) / bkk, EPS)
    }
  }
  const C = tmul(W, X) // r x n
  const D = tmul(W, W) // r x r
  for (let k = 0; k < r; k++) {
    const dkk = Math.max(D.a[k * r + k], EPS)
    for (let j = 0; j < n; j++) {
      let dh = 0
      for (let l = 0; l < r; l++) dh += D.a[k * r + l] * H.a[l * n + j]
      H.a[k * n + j] = Math.max(H.a[k * n + j] + (C.a[k * n + j] - dh) / dkk, EPS)
    }
  }
}

/** One ALS pass: the unconstrained least squares of each half, clipped. */
export function alsStep(X: Mat, f: Fit) {
  const Hn = solveSPD(tmul(f.W, f.W), tmul(f.W, X))
  for (let i = 0; i < Hn.a.length; i++) Hn.a[i] = Math.max(Hn.a[i], EPS)
  f.H.a.set(Hn.a)
  const Wt = solveSPD(mult(f.H, f.H), mult(f.H, X)) // r x p
  for (let i = 0; i < f.W.r; i++) for (let k = 0; k < f.W.c; k++) f.W.a[i * f.W.c + k] = Math.max(Wt.a[k * f.W.r + i], EPS)
}

export function step(algo: Algo, X: Mat, f: Fit, o: MuOpts = {}) {
  if (algo === 'hals') halsStep(X, f)
  else if (algo === 'als') alsStep(X, f)
  else muStep(X, f, o)
}

/** Run `iters` passes from a start, returning the fit (the start is copied). */
export function fit(X: Mat, start: Fit, iters: number, algo: Algo = 'mu', o: MuOpts = {}): Fit {
  const f = { W: clone(start.W), H: clone(start.H) }
  for (let t = 0; t < iters; t++) step(algo, X, f, o)
  return f
}

/** Components sorted by how much of X they explain, so a redraw is stable. */
export function order(f: Fit): Fit {
  const r = f.W.c
  const e = Array.from({ length: r }, (_, k) => {
    let a = 0, b = 0
    for (let i = 0; i < f.W.r; i++) a += f.W.a[i * r + k] ** 2
    for (let j = 0; j < f.H.c; j++) b += f.H.a[k * f.H.c + j] ** 2
    return Math.sqrt(a * b)
  })
  const idx = e.map((_, k) => k).sort((a, b) => e[b] - e[a])
  const W = mat(f.W.r, r)
  const H = mat(r, f.H.c)
  idx.forEach((k, kk) => {
    for (let i = 0; i < f.W.r; i++) W.a[i * r + kk] = f.W.a[i * r + k]
    H.a.set(f.H.a.subarray(k * f.H.c, (k + 1) * f.H.c), kk * f.H.c)
  })
  return { W, H }
}
