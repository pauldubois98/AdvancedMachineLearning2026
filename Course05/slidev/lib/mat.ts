// Dense matrices for NMF in the browser: row-major Float64Array, and only the
// handful of products the multiplicative updates, ALS and HALS need. Written
// as plain loops with the inner index contiguous, which is what makes a
// 1024 x 300 matrix refit fast enough to animate.

export interface Mat {
  r: number
  c: number
  a: Float64Array
}

export function mat(r: number, c: number, fill = 0): Mat {
  const a = new Float64Array(r * c)
  if (fill) a.fill(fill)
  return { r, c, a }
}

export function fromRows(rows: number[][]): Mat {
  const m = mat(rows.length, rows[0].length)
  rows.forEach((row, i) => row.forEach((v, j) => { m.a[i * m.c + j] = v }))
  return m
}

export function clone(m: Mat): Mat {
  return { r: m.r, c: m.c, a: m.a.slice() }
}

export function get(m: Mat, i: number, j: number): number {
  return m.a[i * m.c + j]
}

/** A B */
export function mul(A: Mat, B: Mat): Mat {
  const out = mat(A.r, B.c)
  const { a } = out
  for (let i = 0; i < A.r; i++) {
    const oi = i * B.c
    for (let k = 0; k < A.c; k++) {
      const v = A.a[i * A.c + k]
      if (v === 0) continue
      const bk = k * B.c
      for (let j = 0; j < B.c; j++) a[oi + j] += v * B.a[bk + j]
    }
  }
  return out
}

/** Aᵀ B */
export function tmul(A: Mat, B: Mat): Mat {
  const out = mat(A.c, B.c)
  const { a } = out
  for (let k = 0; k < A.r; k++) {
    const ak = k * A.c
    const bk = k * B.c
    for (let i = 0; i < A.c; i++) {
      const v = A.a[ak + i]
      if (v === 0) continue
      const oi = i * B.c
      for (let j = 0; j < B.c; j++) a[oi + j] += v * B.a[bk + j]
    }
  }
  return out
}

/** A Bᵀ */
export function mult(A: Mat, B: Mat): Mat {
  const out = mat(A.r, B.r)
  const { a } = out
  for (let i = 0; i < A.r; i++) {
    const ai = i * A.c
    for (let j = 0; j < B.r; j++) {
      const bj = j * B.c
      let s = 0
      for (let k = 0; k < A.c; k++) s += A.a[ai + k] * B.a[bj + k]
      a[i * B.r + j] = s
    }
  }
  return out
}

export function transpose(A: Mat): Mat {
  const out = mat(A.c, A.r)
  for (let i = 0; i < A.r; i++) for (let j = 0; j < A.c; j++) out.a[j * A.r + i] = A.a[i * A.c + j]
  return out
}

export function norm(A: Mat): number {
  let s = 0
  for (const v of A.a) s += v * v
  return Math.sqrt(s)
}

export function maxOf(A: Mat | Float64Array): number {
  const a = 'a' in A ? A.a : A
  let m = -Infinity
  for (const v of a) if (v > m) m = v
  return m
}

/** column j of A, as a fresh array */
export function col(A: Mat, j: number): Float64Array {
  const out = new Float64Array(A.r)
  for (let i = 0; i < A.r; i++) out[i] = A.a[i * A.c + j]
  return out
}

/** row i of A, as a view */
export function row(A: Mat, i: number): Float64Array {
  return A.a.subarray(i * A.c, (i + 1) * A.c)
}

/** Solve S x = b for every column b of B, S symmetric positive definite
 *  (r x r, small): a Cholesky factorization, with a tiny ridge for safety. */
export function solveSPD(S: Mat, B: Mat): Mat {
  const n = S.r
  const L = new Float64Array(n * n)
  const ridge = 1e-10 * (S.a.reduce((s, v, i) => (i % (n + 1) === 0 ? s + v : s), 0) / n + 1)
  for (let i = 0; i < n; i++) {
    for (let j = 0; j <= i; j++) {
      let s = S.a[i * n + j] + (i === j ? ridge : 0)
      for (let k = 0; k < j; k++) s -= L[i * n + k] * L[j * n + k]
      L[i * n + j] = i === j ? Math.sqrt(Math.max(s, 1e-300)) : s / L[j * n + j]
    }
  }
  const out = mat(n, B.c)
  const y = new Float64Array(n)
  for (let c = 0; c < B.c; c++) {
    for (let i = 0; i < n; i++) {
      let s = B.a[i * B.c + c]
      for (let k = 0; k < i; k++) s -= L[i * n + k] * y[k]
      y[i] = s / L[i * n + i]
    }
    for (let i = n - 1; i >= 0; i--) {
      let s = y[i]
      for (let k = i + 1; k < n; k++) s -= L[k * n + i] * out.a[k * B.c + c]
      out.a[i * B.c + c] = s / L[i * n + i]
    }
  }
  return out
}

/**
 * The top r singular triplets of X (p x n), by subspace iteration on the
 * smaller Gram matrix. Enough for NNDSVD and for a PCA picture; not a general
 * SVD.
 */
export function topSvd(X: Mat, r: number, iters = 60): { U: Mat; s: number[]; V: Mat } {
  const tall = X.r >= X.c
  const G = tall ? tmul(X, X) : mult(X, X) // the small side
  const m = G.r
  let Q = mat(m, r)
  let seed = 7
  for (let i = 0; i < Q.a.length; i++) {
    seed = (seed * 16807) % 2147483647
    Q.a[i] = seed / 2147483647 - 0.5
  }
  for (let t = 0; t < iters; t++) Q = orthonormalColumns(mul(G, Q))
  // Rayleigh–Ritz is skipped: after enough sweeps the columns are the vectors
  const lam = Array.from({ length: r }, (_, k) => {
    const q = col(Q, k)
    const gq = col(mul(G, colMat(q)), 0)
    return q.reduce((s, v, i) => s + v * gq[i], 0)
  })
  const order = lam.map((_, k) => k).sort((a, b) => lam[b] - lam[a])
  const s = order.map((k) => Math.sqrt(Math.max(lam[k], 0)))
  const small = mat(m, r)
  order.forEach((k, kk) => { for (let i = 0; i < m; i++) small.a[i * r + kk] = Q.a[i * r + k] })
  // the other side: X v / s (or Xᵀ u / s)
  const big = tall ? mul(X, small) : tmul(X, small)
  for (let k = 0; k < r; k++) for (let i = 0; i < big.r; i++) big.a[i * r + k] /= s[k] || 1
  return tall ? { U: big, s, V: small } : { U: small, s, V: big }
}

function colMat(v: Float64Array): Mat {
  return { r: v.length, c: 1, a: v.slice() }
}

function orthonormalColumns(A: Mat): Mat {
  const { r: m, c } = A
  const Q = clone(A)
  for (let k = 0; k < c; k++) {
    for (let j = 0; j < k; j++) {
      let d = 0
      for (let i = 0; i < m; i++) d += Q.a[i * c + k] * Q.a[i * c + j]
      for (let i = 0; i < m; i++) Q.a[i * c + k] -= d * Q.a[i * c + j]
    }
    let nn = 0
    for (let i = 0; i < m; i++) nn += Q.a[i * c + k] ** 2
    nn = Math.sqrt(nn) || 1
    for (let i = 0; i < m; i++) Q.a[i * c + k] /= nn
  }
  return Q
}

/** base64 little-endian float32 (the data files) -> Float64Array */
export function f32(b64: string): Float64Array {
  const bin = atob(b64)
  const bytes = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
  return Float64Array.from(new Float32Array(bytes.buffer))
}
