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

// ---------------------------------------------------------------------------
// clustering palette: the colour cycle CLUSTER_COLORS of make_figures_c04.py,
// plus the two colour maps that deck uses for density and for the mountains.
// ---------------------------------------------------------------------------
export const TEAL = '#0f9b8e'
export const MAGENTA = '#b5179e'

/** one colour per cluster; label -1 (noise) is drawn in MUTED instead */
export const CLUSTER_COLORS = [BLUE, RED, GREEN, PURPLE, GOLD, TEAL, MAGENTA] as const

export function clusterColor(k: number): string {
  return k < 0 ? MUTED : CLUSTER_COLORS[k % CLUSTER_COLORS.length]
}

function hexRgb(c: string): [number, number, number] {
  const m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(c)!
  return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)]
}

/** A LinearSegmentedColormap over hex stops, sampled at t in [0, 1]. */
function ramp(stops: string[]): (t: number) => [number, number, number] {
  const rgbs = stops.map(hexRgb)
  return (t: number) => {
    const u = Math.min(1, Math.max(0, t)) * (rgbs.length - 1)
    const i = Math.min(rgbs.length - 2, Math.floor(u))
    const f = u - i
    const a = rgbs[i]
    const b = rgbs[i + 1]
    return [
      Math.round(a[0] + f * (b[0] - a[0])),
      Math.round(a[1] + f * (b[1] - a[1])),
      Math.round(a[2] + f * (b[2] - a[2])),
    ]
  }
}

/** blue -> gold -> red: the deck's "crowded to out at sea" scale */
export const density = ramp([BLUE, GOLD, RED])

/** white -> blue: the mountain surfaces */
export const mountain = ramp(['#ffffff', '#e8eef6', '#bed4ea', '#7ba7d1', BLUE])

/** n variations of one colour, light to dark, for sub-clusters */
export function shades(color: string, n: number): string[] {
  const base = hexRgb(color)
  const out: string[] = []
  for (let i = 0; i < n; i++) {
    const f = n === 1 ? 1 : 0.55 + (0.45 * i) / (n - 1)
    out.push(
      `rgb(${Math.round(base[0] * f + 255 * (1 - f))},` +
        `${Math.round(base[1] * f + 255 * (1 - f))},` +
        `${Math.round(base[2] * f + 255 * (1 - f))})`,
    )
  }
  return out
}

/** mix two colours, t = 0 gives a, t = 1 gives b */
export function mix(a: string, b: string, t: number): string {
  const A = hexRgb(a)
  const B = hexRgb(b)
  return `rgb(${Math.round(A[0] + t * (B[0] - A[0]))},${Math.round(
    A[1] + t * (B[1] - A[1]),
  )},${Math.round(A[2] + t * (B[2] - A[2]))})`
}
