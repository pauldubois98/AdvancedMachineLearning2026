// Small builders for Plane's segments: a fitted line across the frame.
import type { Pt } from './geom'
import type { Seg } from '../components/Plane.vue'

/** y = b0 + b1 x, from x0 to x1 */
export const lineSeg = (b: [number, number] | number[], x0: number, x1: number, color: string, width = 2.4, dash: number[] = []): Seg =>
  ({ a: [x0, b[0] + b[1] * x0] as Pt, b: [x1, b[0] + b[1] * x1] as Pt, color, width, dash })

/** a polyline as consecutive segments */
export const polyline = (pts: Pt[], color: string, width = 2, dash: number[] = []): Seg[] =>
  pts.slice(1).map((p, i) => ({ a: pts[i], b: p, color, width, dash }))
