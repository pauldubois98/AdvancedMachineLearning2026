// PCA by Jacobi's eigenvalue method: enough for the 64 pixels of the digits.
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

/** centre, then the eigen-decomposition of the covariance (ddof 1) */
export function pcaFit(X: number[][]) {
  const n = X.length, d = X[0].length
  const mu = new Array(d).fill(0)
  for (const r of X) for (let k = 0; k < d; k++) mu[k] += r[k] / n
  const S = Array.from({ length: d }, () => new Array(d).fill(0))
  for (const r of X) for (let a = 0; a < d; a++) { const va = r[a] - mu[a]; for (let b = a; b < d; b++) S[a][b] += (va * (r[b] - mu[b])) / (n - 1) }
  for (let a = 0; a < d; a++) for (let b = 0; b < a; b++) S[a][b] = S[b][a]
  const { values, vectors } = eigSym(S)
  return { mu, values: values.map((v) => Math.max(v, 0)), vectors }
}

/** x rebuilt from its first q components */
export function reconstruct(x: number[], fit: ReturnType<typeof pcaFit>, q: number) {
  const out = fit.mu.slice()
  for (let j = 0; j < q; j++) {
    const v = fit.vectors[j]
    let z = 0
    for (let k = 0; k < x.length; k++) z += v[k] * (x[k] - fit.mu[k])
    for (let k = 0; k < x.length; k++) out[k] += z * v[k]
  }
  return out
}
