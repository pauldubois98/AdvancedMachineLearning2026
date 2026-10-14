// The mountain method and its gridless cousin, subtractive clustering: a hill
// per point, take the summit, flatten it, repeat.
import { Pts } from './data4'

/** M(v) = sum_i exp(-||v - x_i||^2 / 2 sigma^2), on a list of candidates. */
export function mountainField(V: Pts, X: Pts, sigma: number): Float64Array {
  const out = new Float64Array(V.length)
  const denom = 2 * sigma * sigma
  for (let v = 0; v < V.length; v++) {
    let s = 0
    for (const p of X) s += Math.exp(-(((V[v][0] - p[0]) ** 2 + (V[v][1] - p[1]) ** 2) / denom))
    out[v] = s
  }
  return out
}

export interface MountainStep {
  /** the summit taken at this round, and how high it was */
  peak: [number, number]
  height: number
  /** the surface left after subtracting it */
  surface: Float64Array
}

/** k rounds of "take the peak, then subtract a hill of width beta round it". */
export function mountainPeaks(
  V: Pts,
  M0: Float64Array,
  k: number,
  beta: number,
): { steps: MountainStep[]; surfaces: Float64Array[] } {
  let M = Float64Array.from(M0)
  const steps: MountainStep[] = []
  const surfaces: Float64Array[] = [Float64Array.from(M0)]
  const denom = 2 * beta * beta
  for (let r = 0; r < k; r++) {
    let best = 0
    for (let i = 1; i < M.length; i++) if (M[i] > M[best]) best = i
    const peak = V[best] as [number, number]
    const height = M[best]
    const next = Float64Array.from(M)
    for (let i = 0; i < M.length; i++) {
      next[i] -= height * Math.exp(-(((V[i][0] - peak[0]) ** 2 + (V[i][1] - peak[1]) ** 2) / denom))
    }
    M = next
    steps.push({ peak, height, surface: Float64Array.from(M) })
    surfaces.push(Float64Array.from(M))
  }
  return { steps, surfaces }
}

/** The potential Chiu's subtractive clustering puts on each data point. */
export function potential(X: Pts, ra: number): Float64Array {
  const out = new Float64Array(X.length)
  const denom = ra * ra
  for (let i = 0; i < X.length; i++) {
    let s = 0
    for (const p of X) s += Math.exp((-4 * ((X[i][0] - p[0]) ** 2 + (X[i][1] - p[1]) ** 2)) / denom)
    out[i] = s
  }
  return out
}

/** Subtractive clustering: peaks of the potential, then nearest-centre labels. */
export function subtractive(
  X: Pts,
  ra: number,
  ratio = 0.5,
  kmax = 6,
): { labels: number[]; centres: Pts; heights: number[]; first: number } {
  const rb = 1.5 * ra
  const P = potential(X, ra)
  const first = Math.max(...Array.from(P))
  const centres: Pts = []
  const heights: number[] = []
  let cur = Float64Array.from(P)
  for (let r = 0; r < kmax; r++) {
    let best = 0
    for (let i = 1; i < cur.length; i++) if (cur[i] > cur[best]) best = i
    if (cur[best] < ratio * first) break
    centres.push(X[best].slice())
    heights.push(cur[best])
    const h = cur[best]
    const c = X[best]
    const denom = rb * rb
    const next = Float64Array.from(cur)
    for (let i = 0; i < cur.length; i++) {
      next[i] -= h * Math.exp((-4 * ((X[i][0] - c[0]) ** 2 + (X[i][1] - c[1]) ** 2)) / denom)
    }
    cur = next
  }
  if (!centres.length) return { labels: X.map(() => 0), centres: [X[0]], heights: [first], first }
  const labels = X.map((p) => {
    let best = 0
    let bd = Infinity
    centres.forEach((c, k) => {
      const d = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2
      if (d < bd) { bd = d; best = k }
    })
    return best
  })
  return { labels, centres, heights, first }
}

/** The surface as a function of position: the hills of every point, less the
 *  peaks already subtracted. Handy for painting it at screen resolution. */
export function surface(
  X: Pts,
  sigma: number,
  taken: { peak: [number, number]; height: number }[] = [],
  beta = 0.75,
): (x: number, y: number) => number {
  const ds = 2 * sigma * sigma
  const db = 2 * beta * beta
  return (x: number, y: number) => {
    let s = 0
    for (const p of X) s += Math.exp(-(((x - p[0]) ** 2 + (y - p[1]) ** 2) / ds))
    for (const t of taken) {
      s -= t.height * Math.exp(-(((x - t.peak[0]) ** 2 + (y - t.peak[1]) ** 2) / db))
    }
    return s
  }
}
