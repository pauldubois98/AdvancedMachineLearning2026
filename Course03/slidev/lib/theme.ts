// The palette of the pptx deck (scripts/make_figures_c03.py), so the
// interactive figures and the printed ones speak the same visual language.
export const INK = '#1b1b1b'
export const MUTED = '#9aa0a6'
export const BLUE = '#2b6cb0'
export const GREEN = '#00ab0e'
export const RED = '#c53030'
export const PURPLE = '#6b46c1'
export const GOLD = '#b7791f'
export const LIGHT = '#edeef0'
export const GRID = '#cccfd2'

export const CLASS_COLORS = [BLUE, RED] as const

// matplotlib's RdBu, 11 ColorBrewer stops, reversed: 0 -> blue, 1 -> red.
const RDBU_R = [
  [5, 48, 97],
  [33, 102, 172],
  [67, 147, 195],
  [146, 197, 222],
  [209, 229, 240],
  [247, 247, 247],
  [253, 219, 199],
  [244, 165, 130],
  [214, 96, 77],
  [178, 24, 43],
  [103, 0, 31],
]

/** RdBu_r sampled at t in [0, 1]. */
export function rdbuR(t: number): [number, number, number] {
  const u = Math.min(1, Math.max(0, t)) * (RDBU_R.length - 1)
  const i = Math.min(RDBU_R.length - 2, Math.floor(u))
  const f = u - i
  const a = RDBU_R[i]
  const b = RDBU_R[i + 1]
  return [
    Math.round(a[0] + f * (b[0] - a[0])),
    Math.round(a[1] + f * (b[1] - a[1])),
    Math.round(a[2] + f * (b[2] - a[2])),
  ]
}

/** matplotlib's "Greens", light to dark. */
const GREENS = [
  [247, 252, 245],
  [229, 245, 224],
  [199, 233, 192],
  [161, 217, 155],
  [116, 196, 118],
  [65, 171, 93],
  [35, 139, 69],
  [0, 109, 44],
  [0, 68, 27],
]

export function greens(t: number): [number, number, number] {
  const u = Math.min(1, Math.max(0, t)) * (GREENS.length - 1)
  const i = Math.min(GREENS.length - 2, Math.floor(u))
  const f = u - i
  const a = GREENS[i]
  const b = GREENS[i + 1]
  return [
    Math.round(a[0] + f * (b[0] - a[0])),
    Math.round(a[1] + f * (b[1] - a[1])),
    Math.round(a[2] + f * (b[2] - a[2])),
  ]
}

export function rgb([r, g, b]: [number, number, number], alpha = 1): string {
  return alpha >= 1 ? `rgb(${r},${g},${b})` : `rgba(${r},${g},${b},${alpha})`
}
