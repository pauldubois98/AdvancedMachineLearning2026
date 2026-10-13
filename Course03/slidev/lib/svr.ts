// eps-SVR, solved on the difference beta_i = alpha_i - alpha_i^*.
//
//   max  -1/2 beta' K beta + y' beta - eps * sum |beta_i|
//   s.t. sum beta_i = 0,  |beta_i| <= C
//
// Pairwise ascent: a step beta_i += d, beta_j -= d keeps the sum constraint,
// and the objective along d is piecewise quadratic with kinks where beta_i + d
// or beta_j - d changes sign. Each piece is maximised exactly, so no smoothing
// of the eps-insensitive kink is needed.
import { Kernel, makeKernel } from './svm'
import { Rng } from './rng'

export interface Svr {
  beta: Float64Array
  b: number
  sv: number[]
  /** indices with 0 < |beta_i| < C: the points sitting on the tube */
  freeSv: number[]
  epsilon: number
  C: number
  decision(x: number[]): number
  predict1(x: number): number
}

export function fitSvr(
  X: number[][],
  y: number[],
  C: number,
  epsilon: number,
  kern: Kernel,
  opts: { sweeps?: number; tol?: number } = {},
): Svr {
  const sweeps = opts.sweeps ?? 200
  const tol = opts.tol ?? 1e-9
  const n = X.length
  const kf = makeKernel(kern)
  const K = new Float64Array(n * n)
  for (let i = 0; i < n; i++)
    for (let j = i; j < n; j++) {
      const v = kf(X[i], X[j])
      K[i * n + j] = v
      K[j * n + i] = v
    }

  const beta = new Float64Array(n)
  const Kb = new Float64Array(n) // (K beta)_i, kept in step with beta
  const rng = new Rng(5)

  /** change in the objective for a step of d on the pair (i, j) */
  const delta = (i: number, j: number, d: number, gi: number, gj: number, eta: number) => {
    const pen =
      Math.abs(beta[i] + d) - Math.abs(beta[i]) +
      Math.abs(beta[j] - d) - Math.abs(beta[j])
    return (gi - gj) * d - 0.5 * eta * d * d - epsilon * pen
  }

  const step = (i: number, j: number): boolean => {
    if (i === j) return false
    const eta = K[i * n + i] + K[j * n + j] - 2 * K[i * n + j]
    const gi = y[i] - Kb[i]
    const gj = y[j] - Kb[j]
    const lo = Math.max(-C - beta[i], beta[j] - C)
    const hi = Math.min(C - beta[i], C + beta[j])
    if (hi - lo < 1e-14) return false

    // candidate maximisers: the interval ends, the kinks, and the vertex of
    // each quadratic piece
    const breaks = [-beta[i], beta[j]].filter((v) => v > lo && v < hi)
    const edges = [lo, ...breaks.sort((a, b) => a - b), hi]
    const cands: number[] = [...edges]
    for (let p = 0; p < edges.length - 1; p++) {
      const a0 = edges[p]
      const a1 = edges[p + 1]
      if (a1 - a0 < 1e-15) continue
      const mid = (a0 + a1) / 2
      const si = Math.sign(beta[i] + mid)
      const sj = Math.sign(beta[j] - mid)
      const slope = gi - gj - epsilon * si + epsilon * sj
      if (eta > 1e-14) {
        const v = slope / eta
        if (v > a0 && v < a1) cands.push(v)
      }
    }

    let bestD = 0
    let bestGain = 0
    for (const d of cands) {
      if (d === 0) continue
      const g = delta(i, j, d, gi, gj, eta)
      if (g > bestGain) {
        bestGain = g
        bestD = d
      }
    }
    if (bestGain <= tol) return false

    let bi = beta[i] + bestD
    let bj = beta[j] - bestD
    if (Math.abs(bi) < 1e-12) bi = 0
    if (Math.abs(bj) < 1e-12) bj = 0
    const di = bi - beta[i]
    const dj = bj - beta[j]
    beta[i] = bi
    beta[j] = bj
    for (let m = 0; m < n; m++) Kb[m] += di * K[m * n + i] + dj * K[m * n + j]
    return true
  }

  for (let s = 0; s < sweeps; s++) {
    let changed = 0
    for (let i = 0; i < n; i++) {
      // partner with the point whose gradient differs most: that is where the
      // pair step has the most to gain
      const gi = y[i] - Kb[i]
      let best = -1
      let bestGap = 0
      for (let j = 0; j < n; j++) {
        if (j === i) continue
        const gap = Math.abs(gi - (y[j] - Kb[j]))
        if (gap > bestGap) {
          bestGap = gap
          best = j
        }
      }
      if (best >= 0 && step(i, best)) changed++
      else {
        const j = Math.floor(rng.next() * n)
        if (step(i, j)) changed++
      }
    }
    if (changed === 0) break
  }

  const svTol = 1e-8 * Math.max(1, C)
  const sv: number[] = []
  const freeSv: number[] = []
  for (let i = 0; i < n; i++) {
    const a = Math.abs(beta[i])
    if (a > svTol) {
      sv.push(i)
      if (a < C - svTol) freeSv.push(i)
    }
  }

  // b from the points on the tube: y_i - f(x_i) = eps * sign(beta_i)
  let b = 0
  if (freeSv.length) {
    let acc = 0
    for (const i of freeSv) acc += y[i] - Kb[i] - epsilon * Math.sign(beta[i])
    b = acc / freeSv.length
  } else {
    let acc = 0
    for (let i = 0; i < n; i++) acc += y[i] - Kb[i]
    b = acc / n
  }

  const coef = sv.map((i) => beta[i])
  const svX = sv.map((i) => X[i])
  const decision = (x: number[]) => {
    let f = b
    for (let s = 0; s < svX.length; s++) f += coef[s] * kf(svX[s], x)
    return f
  }

  return {
    beta,
    b,
    sv,
    freeSv,
    epsilon,
    C,
    decision,
    predict1: (x) => decision([x]),
  }
}
