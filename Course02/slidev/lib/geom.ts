// The small geometry the plots need: points, 2-D covariances and their
// ellipses, histograms and grids.
export type Pt = [number, number]
export type Cov = [number, number, number] // [s_xx, s_xy, s_yy]

/** the principal axes of a 2-D covariance, as an ellipse */
export function ellipseAxes(S: Cov): { r1: number; r2: number; angle: number } {
  const [a, b, c] = S
  const tr = (a + c) / 2
  const disc = Math.sqrt(((a - c) / 2) ** 2 + b * b)
  const l1 = tr + disc
  const l2 = Math.max(tr - disc, 0)
  const angle = Math.abs(b) < 1e-12 ? (a >= c ? 0 : Math.PI / 2) : Math.atan2(l1 - a, b)
  return { r1: Math.sqrt(l1), r2: Math.sqrt(l2), angle }
}

export function histogram(x: ArrayLike<number>, edges: number[]): number[] {
  const h = new Array(edges.length - 1).fill(0)
  const lo = edges[0]
  const hi = edges[edges.length - 1]
  for (let i = 0; i < x.length; i++) {
    const v = x[i]
    if (v < lo || v > hi) continue
    let j = 0
    while (j < h.length - 1 && v >= edges[j + 1]) j++
    h[j]++
  }
  return h
}

export const linspace = (a: number, b: number, n: number): number[] =>
  Array.from({ length: n }, (_, i) => a + ((b - a) * i) / (n - 1))
