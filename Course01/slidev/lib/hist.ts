// Histograms as LineChart bars, and circles as Plane segments.
import type { Pt } from './geom'

export interface Bar { x: number; y: number; w: number; color?: string; alpha?: number; y0?: number }

/** a histogram of x over [lo, hi] in nb bins; density=true scales it to area 1 */
export function histBars(x: ArrayLike<number>, lo: number, hi: number, nb: number, color: string,
  alpha = 0.45, density = true, y0 = 0): Bar[] {
  const w = (hi - lo) / nb
  const h = new Array(nb).fill(0)
  for (let i = 0; i < x.length; i++) {
    const j = Math.floor((x[i] - lo) / w)
    if (j >= 0 && j < nb) h[j]++
  }
  const s = density ? 1 / (x.length * w) : 1
  return h.map((c, j) => ({ x: lo + (j + 0.5) * w, y: y0 + c * s, y0, w: w * 0.98, color, alpha }))
}

export const curve = (f: (x: number) => number, lo: number, hi: number, n = 300): [number, number][] =>
  Array.from({ length: n }, (_, i) => { const x = lo + ((hi - lo) * i) / (n - 1); return [x, f(x)] })

export function circle(c: Pt, r: number, color: string, width = 1.2, dash: number[] = [], n = 72) {
  const out = []
  for (let i = 0; i < n; i++) {
    const a = (2 * Math.PI * i) / n, b = (2 * Math.PI * (i + 1)) / n
    out.push({ a: [c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)] as Pt, b: [c[0] + r * Math.cos(b), c[1] + r * Math.sin(b)] as Pt, color, width, dash })
  }
  return out
}

/** "1.2e-23" as "1.2 × 10⁻²³" */
const SUP: Record<string, string> = { '-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹' }
export function sci(v: number, digits = 1): string {
  if (v === 0) return '0'
  const [m, e] = v.toExponential(digits).split('e')
  const k = Number(e)
  if (k > -3 && k < 4) return v.toPrecision(digits + 1)
  return `${m} × 10${String(k).split('').map((c) => SUP[c] ?? '').join('')}`
}
