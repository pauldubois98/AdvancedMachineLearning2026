// A C-SVC trained with Platt's SMO, plus the eps-SVR variant.
// Small enough to refit on every slider move (n of a few hundred).
import { Rng } from './rng'

export type KernelType = 'linear' | 'poly' | 'rbf' | 'sigmoid'

export interface Kernel {
  type: KernelType
  gamma: number
  degree: number
  coef0: number
}

export function kernel(p: Partial<Kernel> = {}): Kernel {
  return { type: 'rbf', gamma: 1, degree: 3, coef0: 1, ...p }
}

function dot(x: number[], z: number[]): number {
  let s = 0
  for (let i = 0; i < x.length; i++) s += x[i] * z[i]
  return s
}

function sqdist(x: number[], z: number[]): number {
  let s = 0
  for (let i = 0; i < x.length; i++) {
    const d = x[i] - z[i]
    s += d * d
  }
  return s
}

export function makeKernel(k: Kernel): (x: number[], z: number[]) => number {
  switch (k.type) {
    case 'linear':
      return dot
    case 'poly':
      return (x, z) => (k.gamma * dot(x, z) + k.coef0) ** k.degree
    case 'sigmoid':
      return (x, z) => Math.tanh(k.gamma * dot(x, z) + k.coef0)
    case 'rbf':
    default:
      return (x, z) => Math.exp(-k.gamma * sqdist(x, z))
  }
}

function gramMatrix(X: number[][], kf: (x: number[], z: number[]) => number) {
  const n = X.length
  const K = new Float64Array(n * n)
  for (let i = 0; i < n; i++) {
    for (let j = i; j < n; j++) {
      const v = kf(X[i], X[j])
      K[i * n + j] = v
      K[j * n + i] = v
    }
  }
  return K
}

export interface Svc {
  alpha: Float64Array
  /** f(x) = sum_i alpha_i y_i k(x_i, x) - b */
  b: number
  y: number[]
  X: number[][]
  C: number
  kernel: Kernel
  /** indices with alpha_i > 0 */
  sv: number[]
  /** indices with 0 < alpha_i < C: the ones exactly on the margin */
  freeSv: number[]
  /** true when a full sweep finished with nothing left to fix */
  converged: boolean
  passes: number
  decision(x: number[]): number
  decisionAt(x: number, y: number): number
  predict(x: number[]): number
  /** linear kernel only */
  w: number[] | null
  /** 2/||w||, the width of the street; linear kernel only */
  marginWidth: number | null
}

/**
 * Platt's SMO for the C-SVC dual:
 *   max  sum a_i - 1/2 sum a_i a_j y_i y_j k(x_i, x_j)
 *   s.t. 0 <= a_i <= C,  sum a_i y_i = 0
 * `y` must be +/-1.
 */
export function fitSvc(
  X: number[][],
  y: number[],
  C: number,
  kern: Kernel,
  opts: { tol?: number; eps?: number; maxPasses?: number } = {},
): Svc {
  const tol = opts.tol ?? 1e-3
  const eps = opts.eps ?? 1e-8
  const maxPasses = opts.maxPasses ?? 5000
  const n = X.length
  const kf = makeKernel(kern)
  const K = gramMatrix(X, kf)
  const alpha = new Float64Array(n)
  const err = new Float64Array(n) // E_i = f(x_i) - y_i, exact while alpha = 0
  for (let i = 0; i < n; i++) err[i] = -y[i]
  let b = 0
  const rng = new Rng(11)

  const kAt = (i: number, j: number) => K[i * n + j]

  const takeStep = (i1: number, i2: number): boolean => {
    if (i1 === i2) return false
    const a1o = alpha[i1]
    const a2o = alpha[i2]
    const y1 = y[i1]
    const y2 = y[i2]
    const e1 = err[i1]
    const e2 = err[i2]
    const s = y1 * y2
    let L: number
    let H: number
    if (s < 0) {
      L = Math.max(0, a2o - a1o)
      H = Math.min(C, C + a2o - a1o)
    } else {
      L = Math.max(0, a1o + a2o - C)
      H = Math.min(C, a1o + a2o)
    }
    if (H - L < 1e-12) return false

    const k11 = kAt(i1, i1)
    const k12 = kAt(i1, i2)
    const k22 = kAt(i2, i2)
    const eta = k11 + k22 - 2 * k12
    let a2: number
    if (eta > 1e-12) {
      a2 = a2o + (y2 * (e1 - e2)) / eta
      a2 = Math.min(H, Math.max(L, a2))
    } else {
      // Non-positive curvature: compare the dual objective at both ends.
      const f1 = y1 * (e1 + b) - a1o * k11 - s * a2o * k12
      const f2 = y2 * (e2 + b) - s * a1o * k12 - a2o * k22
      const l1 = a1o + s * (a2o - L)
      const h1 = a1o + s * (a2o - H)
      const lObj =
        l1 * f1 + L * f2 + 0.5 * l1 * l1 * k11 + 0.5 * L * L * k22 + s * L * l1 * k12
      const hObj =
        h1 * f1 + H * f2 + 0.5 * h1 * h1 * k11 + 0.5 * H * H * k22 + s * H * h1 * k12
      if (lObj < hObj - 1e-9) a2 = L
      else if (lObj > hObj + 1e-9) a2 = H
      else a2 = a2o
    }
    if (Math.abs(a2 - a2o) < 1e-8 * (a2 + a2o + 1e-8)) return false
    if (a2 < eps) a2 = 0
    else if (a2 > C - eps) a2 = C
    const a1 = a1o + s * (a2o - a2)

    const d1 = y1 * (a1 - a1o)
    const d2 = y2 * (a2 - a2o)
    const b1 = e1 + d1 * k11 + d2 * k12 + b
    const b2 = e2 + d1 * k12 + d2 * k22 + b
    let bNew: number
    if (a1 > 0 && a1 < C) bNew = b1
    else if (a2 > 0 && a2 < C) bNew = b2
    else bNew = (b1 + b2) / 2

    for (let i = 0; i < n; i++)
      err[i] += d1 * kAt(i1, i) + d2 * kAt(i2, i) + (b - bNew)

    alpha[i1] = a1
    alpha[i2] = a2
    b = bNew
    return true
  }

  const examine = (i2: number): boolean => {
    const y2 = y[i2]
    const a2 = alpha[i2]
    const e2 = err[i2]
    const r2 = e2 * y2
    if (!((r2 < -tol && a2 < C) || (r2 > tol && a2 > 0))) return false

    // second choice: the non-bound point with the largest |E1 - E2|
    let best = -1
    let bestDelta = 0
    for (let i = 0; i < n; i++) {
      if (alpha[i] <= 0 || alpha[i] >= C || i === i2) continue
      const d = Math.abs(err[i] - e2)
      if (d > bestDelta) {
        bestDelta = d
        best = i
      }
    }
    if (best >= 0 && takeStep(best, i2)) return true

    const start = Math.floor(rng.next() * n)
    for (let k = 0; k < n; k++) {
      const i = (start + k) % n
      if (alpha[i] > 0 && alpha[i] < C && takeStep(i, i2)) return true
    }
    for (let k = 0; k < n; k++) {
      const i = (start + k) % n
      if (takeStep(i, i2)) return true
    }
    return false
  }

  // Platt's outer loop: alternate full sweeps with sweeps over the
  // non-bound points, and stop when a full sweep changes nothing.
  let changed = 0
  let examineAll = true
  let passes = 0
  let converged = false
  while ((changed > 0 || examineAll) && passes < maxPasses) {
    changed = 0
    if (examineAll) {
      for (let i = 0; i < n; i++) if (examine(i)) changed++
      examineAll = false
      if (changed === 0) converged = true
    } else {
      for (let i = 0; i < n; i++)
        if (alpha[i] > 0 && alpha[i] < C && examine(i)) changed++
      if (changed === 0) examineAll = true
    }
    passes++
  }

  const svTol = 1e-7 * Math.max(1, C)
  const sv: number[] = []
  const freeSv: number[] = []
  for (let i = 0; i < n; i++) {
    if (alpha[i] > svTol) {
      sv.push(i)
      if (alpha[i] < C - svTol) freeSv.push(i)
    }
  }

  // b, exactly as libsvm recovers it. A free support vector sits on the
  // margin, so y_i (f_i - b) = 1 pins b down. When every multiplier is at a
  // bound - which happens in the degenerate corners of a C/gamma grid - the
  // KKT conditions only bracket b, and libsvm takes the middle of the bracket.
  const rawF = (i: number) => {
    let f = 0
    for (const j of sv) f += alpha[j] * y[j] * kAt(j, i)
    return f
  }
  if (freeSv.length) {
    let acc = 0
    for (const i of freeSv) acc += rawF(i) - y[i]
    b = acc / freeSv.length
  } else {
    let lo = -Infinity
    let hi = Infinity
    for (let i = 0; i < n; i++) {
      const f = rawF(i)
      const atUpper = alpha[i] >= C - svTol
      if (atUpper) {
        // y_i (f_i - b) <= 1
        if (y[i] > 0) lo = Math.max(lo, f - 1)
        else hi = Math.min(hi, f + 1)
      } else {
        // alpha_i = 0, so y_i (f_i - b) >= 1
        if (y[i] > 0) hi = Math.min(hi, f - 1)
        else lo = Math.max(lo, f + 1)
      }
    }
    if (Number.isFinite(lo) && Number.isFinite(hi)) b = (lo + hi) / 2
    else if (Number.isFinite(lo)) b = lo
    else if (Number.isFinite(hi)) b = hi
  }

  const coef = sv.map((i) => alpha[i] * y[i])
  const svX = sv.map((i) => X[i])
  const decision = (x: number[]) => {
    let f = -b
    for (let s = 0; s < svX.length; s++) f += coef[s] * kf(svX[s], x)
    return f
  }

  let w: number[] | null = null
  let marginWidth: number | null = null
  if (kern.type === 'linear') {
    const d = X[0].length
    w = new Array(d).fill(0)
    for (let s = 0; s < sv.length; s++)
      for (let j = 0; j < d; j++) w[j] += coef[s] * svX[s][j]
    const norm = Math.hypot(...w)
    marginWidth = norm > 0 ? 2 / norm : null
  }

  return {
    alpha,
    b,
    y,
    X,
    C,
    kernel: kern,
    sv,
    freeSv,
    converged,
    passes,
    decision,
    decisionAt: (a, c) => decision([a, c]),
    predict: (x) => (decision(x) >= 0 ? 1 : -1),
    w,
    marginWidth,
  }
}

/** Accuracy of a fitted model on (X, y) with y in {+1, -1}. */
export function accuracy(model: Svc, X: number[][], y: number[]): number {
  let ok = 0
  for (let i = 0; i < X.length; i++) if (model.predict(X[i]) === y[i]) ok++
  return ok / X.length
}

/**
 * k-fold cross-validated accuracy, stratified by class, as sklearn does
 * for a classifier. Unstratified folds would be useless here: the toy datasets
 * are generated one class after the other, so a block fold could hold a
 * single class.
 */
export function crossValScore(
  X: number[][],
  y: number[],
  C: number,
  kern: Kernel,
  folds = 4,
): number {
  const n = X.length
  const fold = new Int32Array(n)
  // sklearn's StratifiedKFold: within each class, contiguous blocks
  const byClass = new Map<number, number[]>()
  for (let i = 0; i < n; i++) {
    if (!byClass.has(y[i])) byClass.set(y[i], [])
    byClass.get(y[i])!.push(i)
  }
  for (const idx of byClass.values())
    idx.forEach((i, k) => {
      fold[i] = Math.min(folds - 1, Math.floor((k * folds) / idx.length))
    })
  let total = 0
  for (let f = 0; f < folds; f++) {
    const trX: number[][] = []
    const trY: number[] = []
    const teX: number[][] = []
    const teY: number[] = []
    for (let i = 0; i < n; i++) {
      if (fold[i] === f) {
        teX.push(X[i])
        teY.push(y[i])
      } else {
        trX.push(X[i])
        trY.push(y[i])
      }
    }
    if (!teX.length) continue
    total += accuracy(fitSvc(trX, trY, C, kern), teX, teY) / folds
  }
  return total
}
