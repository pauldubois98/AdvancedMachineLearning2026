// The palette of the pptx deck (scripts/make_figures_c09.py), so the
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

// the convention of this deck: the original, high-dimensional space is blue,
// the low-dimensional map is gold, PCA is purple and t-SNE is green
export const HIGH = BLUE
export const LOW = GOLD
export const PCA_C = PURPLE
export const TSNE_C = GREEN

/** the toy's three groups, and the blob clusters */
export const COMP = [BLUE, GOLD, GREEN, PURPLE, RED] as const

/** the ten digit classes: matplotlib's tab10 */
export const DIGIT = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'] as const

export function rgb([r, g, b]: [number, number, number], alpha = 1): string {
  return alpha >= 1 ? `rgb(${r},${g},${b})` : `rgba(${r},${g},${b},${alpha})`
}

function hexRgb(c: string): [number, number, number] {
  const m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(c)!
  return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)]
}

/** a LinearSegmentedColormap over hex stops, sampled at t in [0, 1] */
export function ramp(stops: string[]): (t: number) => [number, number, number] {
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

/** the probability matrices: white is zero (the deck's H_CMAP) */
export const heat = ramp(['#ffffff', '#9cc0e4', BLUE, '#0b2a55'])
/** matplotlib's viridis, for "position along the roll" */
export const viridis = ramp(['#440154', '#3b528b', '#21918c', '#5ec962', '#fde725'])
/** matplotlib's RdBu_r: blue negative, red positive */
export const rdbu = ramp(['#053061', '#4393c3', '#f7f7f7', '#d6604d', '#67001f'])
export const hex = (c: [number, number, number]) => rgb(c)
