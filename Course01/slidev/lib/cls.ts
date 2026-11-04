// The class pictures: colours per label, the pale two-class field and its
// boundary, as the printed figures draw them.
import type { Pt } from './geom'
import { CLASS, INK } from './theme'

export const classColors = (y: number[]) => y.map((k) => CLASS[k])
/** pale blue where f < 0, pale red where f > 0 */
export const regionColor = (v: number): [number, number, number] => (v > 0 ? [251, 236, 236] : [233, 240, 248])
export const boundary = (f: (x: number, y: number) => number, color = INK, width = 2.4, dash: number[] = []) => ({ f, level: 0, color, width, dash })
export const sub = (X: Pt[], y: number[], k: number) => X.filter((_, i) => y[i] === k)
