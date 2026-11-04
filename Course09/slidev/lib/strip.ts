// A 1-D map drawn by LineChart: the points on a line, a little deterministic
// vertical jitter so they can be told apart, the followed point in red.
import { jitter } from './data'
import { COMP, RED } from './theme'

export function stripDots(y: number[], g: number[], star = -1, r = 4) {
  const d = y.map((v, i) => ({ x: v, y: jitter(i), color: COMP[g[i]], r }))
  if (star >= 0) d.push({ x: y[star], y: jitter(star), color: RED, r: r + 2.5 })
  return d
}

export function span(y: number[], pad = 0.06): [number, number] {
  let lo = Infinity, hi = -Infinity
  for (const v of y) { if (v < lo) lo = v; if (v > hi) hi = v }
  const p = pad * (hi - lo || 1)
  return [lo - p, hi + p]
}
