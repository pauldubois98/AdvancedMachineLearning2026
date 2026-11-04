// LDA and QDA in d dimensions, for the learning curve of lda_qda_cost: two
// Gaussian classes, fitted by maximum likelihood, scored on a test set.
import { Rng } from './rng'
import { chol, fwd } from './stats'

type M = number[][]
const zeros = (d: number): M => Array.from({ length: d }, () => new Array(d).fill(0))

export function randomCov(rng: Rng, d: number): M {
  const A = Array.from({ length: d }, () => Array.from({ length: d }, () => rng.normal()))
  const S = zeros(d)
  for (let i = 0; i < d; i++) for (let j = 0; j < d; j++) {
    let s = 0
    for (let k = 0; k < d; k++) s += A[i][k] * A[j][k]
    S[i][j] = s / d + (i === j ? 0.5 : 0)
  }
  return S
}

export function draw(rng: Rng, n: number, mu: number[], L: M): number[][] {
  const d = mu.length
  return Array.from({ length: n }, () => {
    const z = Array.from({ length: d }, () => rng.normal())
    return mu.map((m, i) => { let s = m; for (let k = 0; k <= i; k++) s += L[i][k] * z[k]; return s })
  })
}

function fitClass(X: number[][]) {
  const n = X.length, d = X[0].length
  const mu = new Array(d).fill(0)
  for (const x of X) for (let i = 0; i < d; i++) mu[i] += x[i] / n
  const S = zeros(d)
  for (const x of X) for (let i = 0; i < d; i++) for (let j = 0; j <= i; j++) S[i][j] += (x[i] - mu[i]) * (x[j] - mu[j])
  for (let i = 0; i < d; i++) for (let j = 0; j <= i; j++) S[j][i] = S[i][j]
  return { mu, S, n }
}

function scorer(mu: number[], S: M, logpi: number) {
  const L = chol(S)
  let ld = 0
  for (let i = 0; i < L.length; i++) ld += 2 * Math.log(L[i][i])
  return (x: number[]) => {
    const z = fwd(L, x.map((v, i) => v - mu[i]))
    return -0.5 * z.reduce((s, v) => s + v * v, 0) - 0.5 * ld + logpi
  }
}

/** test accuracy of LDA and QDA (with a small ridge, as scikit-learn's reg_param) */
export function ldaQda(X0: number[][], X1: number[][], T0: number[][], T1: number[][], reg = 1e-3) {
  const a = fitClass(X0), b = fitClass(X1)
  const d = a.mu.length, N = a.n + b.n
  const pooled = zeros(d), Sa = zeros(d), Sb = zeros(d)
  for (let i = 0; i < d; i++) for (let j = 0; j < d; j++) {
    pooled[i][j] = (a.S[i][j] + b.S[i][j]) / (N - 2) + (i === j ? 1e-9 : 0)
    Sa[i][j] = a.S[i][j] / Math.max(a.n - 1, 1) * (1 - reg) + (i === j ? reg : 0)
    Sb[i][j] = b.S[i][j] / Math.max(b.n - 1, 1) * (1 - reg) + (i === j ? reg : 0)
  }
  const pa = Math.log(a.n / N), pb = Math.log(b.n / N)
  const l0 = scorer(a.mu, pooled, pa), l1 = scorer(b.mu, pooled, pb)
  const q0 = scorer(a.mu, Sa, pa), q1 = scorer(b.mu, Sb, pb)
  let lda = 0, qda = 0
  for (const x of T0) { if (l0(x) >= l1(x)) lda++; if (q0(x) >= q1(x)) qda++ }
  for (const x of T1) { if (l1(x) > l0(x)) lda++; if (q1(x) > q0(x)) qda++ }
  const T = T0.length + T1.length
  return { lda: lda / T, qda: qda / T }
}
