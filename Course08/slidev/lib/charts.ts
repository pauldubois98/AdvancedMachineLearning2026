// Small builders for LineChart's props: histograms (plain or stacked by
// class) and curves sampled on a grid.
import { histogram } from './gmm'

export interface Bar { x: number; y: number; w: number; color?: string; alpha?: number; y0?: number }

/** one bar per bin; `density` scales so the bars integrate to one */
export function bars(
  x: ArrayLike<number>, edges: number[],
  opts: { density?: boolean; color?: string; alpha?: number; total?: number } = {},
): Bar[] {
  const { density = false, color = '#cccfd2', alpha = 0.55, total } = opts
  const h = histogram(x, edges)
  const n = total ?? x.length
  return h.map((c, j) => {
    const w = edges[j + 1] - edges[j]
    return { x: (edges[j] + edges[j + 1]) / 2, w: w * 0.96, y: density ? c / (n * w) : c, color, alpha }
  })
}

/** bars stacked by class: the colours the generator knows */
export function stacked(
  groups: number[][], edges: number[], colors: readonly string[],
  opts: { density?: boolean; alpha?: number } = {},
): Bar[] {
  const { density = false, alpha = 0.75 } = opts
  const n = groups.reduce((a, g) => a + g.length, 0)
  const base = new Array(edges.length - 1).fill(0)
  const out: Bar[] = []
  groups.forEach((g, k) => {
    histogram(g, edges).forEach((c, j) => {
      if (!c) return
      const w = edges[j + 1] - edges[j]
      const v = density ? c / (n * w) : c
      out.push({ x: (edges[j] + edges[j + 1]) / 2, w: w * 0.96, y0: base[j], y: base[j] + v, color: colors[k], alpha })
      base[j] += v
    })
  })
  return out
}

export const curve = (xs: number[], f: (x: number) => number): [number, number][] =>
  xs.map((x) => [x, f(x)])

/** a range of bin edges with a fixed width */
export function edges(a: number, b: number, w: number): number[] {
  const out: number[] = []
  for (let v = a; v <= b + 1e-9; v += w) out.push(+v.toFixed(9))
  return out
}

export const fmt = (v: number, d = 0) =>
  v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }).replace('-', '−')
