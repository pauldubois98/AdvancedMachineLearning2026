// The two-bump posterior of the cost slides, on a grid: a mixture of two
// Gaussian bumps, normalised to sum to one over the grid.
import { curve } from './hist'

export function postGrid(w: number, m1: number, s1: number, m2: number, s2: number, lo = -1.5, hi = 6, n = 600) {
  const f = (t: number) => w * Math.exp(-0.5 * ((t - m1) / s1) ** 2) + (1 - w) * Math.exp(-0.5 * ((t - m2) / s2) ** 2)
  const grid = Array.from({ length: n }, (_, i) => lo + ((hi - lo) * i) / (n - 1))
  const raw = grid.map(f)
  const Z = raw.reduce((a, b) => a + b, 0)
  const p = raw.map((v) => v / Z)
  const dx = (hi - lo) / (n - 1)
  const c = curve((t) => f(t) / (Z * dx), lo, hi, 300)
  const top = Math.max(...c.map((q) => q[1]))
  const mean = grid.reduce((s, t, i) => s + t * p[i], 0)
  let acc = 0, median = grid[0]
  for (let i = 0; i < n; i++) { acc += p[i]; if (acc >= 0.5) { median = grid[i]; break } }
  const mode = grid[raw.indexOf(Math.max(...raw))]
  return { grid, p, curve: c, top, mean, median, mode }
}
