// Pairwise distances for the "no map is perfect" slides: every pair of a
// small cloud, a Shepard plot (data distance against map distance), and how
// many of each point's nearest neighbours a map keeps.
import type { Pt } from './geom'

/** the distances of every pair i < j, in that order */
export function pairDists(X: number[][]): number[] {
  const out: number[] = []
  for (let i = 0; i < X.length; i++)
    for (let j = i + 1; j < X.length; j++) {
      let s = 0
      for (let k = 0; k < X[i].length; k++) { const d = X[i][k] - X[j][k]; s += d * d }
      out.push(Math.sqrt(s))
    }
  return out
}

/** (data distance, map distance) for every pair */
export const shepard = (X: number[][], Y: number[][]): Pt[] => {
  const a = pairDists(X), b = pairDists(Y)
  return a.map((v, k) => [v, b[k]])
}

/** the indices of the k nearest neighbours of every point */
export function knn(X: number[][], k: number): number[][] {
  const n = X.length
  const D = pairDists(X)
  const at = (i: number, j: number) => {
    const [a, b] = i < j ? [i, j] : [j, i]
    return D[a * n - (a * (a + 1)) / 2 + (b - a - 1)]
  }
  return Array.from({ length: n }, (_, i) => {
    const idx = Array.from({ length: n }, (_, j) => j).filter((j) => j !== i)
    idx.sort((p, q) => at(i, p) - at(i, q))
    return idx.slice(0, k)
  })
}

/** the share of each point's k data neighbours that are also its k map
 *  neighbours, averaged over the points */
export function kept(X: number[][], Y: number[][], k = 10): number {
  const a = knn(X, k), b = knn(Y, k)
  let s = 0
  a.forEach((nb, i) => { const B = new Set(b[i]); s += nb.filter((j) => B.has(j)).length / k })
  return s / X.length
}

/** a circle of radius r around c, as segments for Plane */
export function circle(c: Pt, r: number, color: string, width = 1.6, dash?: number[]) {
  const n = 72
  return Array.from({ length: n }, (_, s) => {
    const a = (2 * Math.PI * s) / n, b = (2 * Math.PI * (s + 1)) / n
    return { a: [c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)] as Pt, b: [c[0] + r * Math.cos(b), c[1] + r * Math.sin(b)] as Pt, color, width, dash }
  })
}
