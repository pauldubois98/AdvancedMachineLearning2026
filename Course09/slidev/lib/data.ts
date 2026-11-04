// The data every slide runs on. The toy, the blobs and the swiss roll are
// drawn here from a fixed seed (the same models as the printed figures, not
// the same numpy draws); the 600 digits and the MNIST maps are read from
// Course09/data, written by scripts/make_data_c09.py.
import digitsJson from '../../data/digits600.json'
import mnistJson from '../../data/mnist_maps.json'
import { Rng } from './rng'
import { conditionalP, jointP, sqdist, type Mat } from './sne'

// ---------------------------------------------------------------------------
// the toy of the SNE steps: 45 points in 2-D, three groups (tight, wide,
// medium), mapped onto a line
// ---------------------------------------------------------------------------
export const TOY_N = 45
export const TOY_PERP = 8

function makeToy() {
  const rng = new Rng(11)
  const centres = [[-3.0, 0.3], [1.4, 1.9], [1.9, -1.9]]
  const sd = [0.35, 0.95, 0.6]
  const X: number[][] = []
  const g: number[] = []
  for (let k = 0; k < 3; k++)
    for (let i = 0; i < 15; i++) {
      X.push([centres[k][0] + rng.normal(0, sd[k]), centres[k][1] + rng.normal(0, sd[k])])
      g.push(k)
    }
  // the point we follow: the one of the wide group nearest its centre
  const m = [0, 0]
  for (let i = 15; i < 30; i++) { m[0] += X[i][0] / 15; m[1] += X[i][1] / 15 }
  let star = 15
  let best = Infinity
  for (let i = 15; i < 30; i++) {
    const d = (X[i][0] - m[0]) ** 2 + (X[i][1] - m[1]) ** 2
    if (d < best) { best = d; star = i }
  }
  return { X, g, star }
}

export const TOY = makeToy()
export const TOY_D = sqdist(TOY.X)

const pCache = new Map<number, { Pc: Mat; sig: Float64Array; P: Mat }>()
/** the toy's P at a given perplexity (cached: the sliders come back) */
export function toyP(perp = TOY_PERP) {
  const key = Math.round(perp * 100) / 100
  let v = pCache.get(key)
  if (!v) {
    const { P: Pc, sig } = conditionalP(TOY_D, TOY_N, key)
    v = { Pc, sig, P: jointP(Pc, TOY_N) }
    pCache.set(key, v)
  }
  return v
}

// ---------------------------------------------------------------------------
// three clusters in 10-D: a wide one, a tight one, a tight one far away
// ---------------------------------------------------------------------------
export function blobs(opts: { wide?: number; near?: number; far?: number; seed?: number; n?: number } = {}) {
  const { wide = 2, near = 15, far = 60, seed = 2, n = 100 } = opts
  const rng = new Rng(seed)
  const d = 10
  const c = [0, near, far]
  const sd = [wide, 0.5, 0.5]
  const X: number[][] = []
  const g: number[] = []
  for (let k = 0; k < 3; k++)
    for (let i = 0; i < n; i++) {
      const r = Array.from({ length: d }, () => rng.normal(0, sd[k]))
      r[0] += c[k]
      X.push(r)
      g.push(k)
    }
  return { X, g }
}

// ---------------------------------------------------------------------------
// the swiss roll: scikit-learn's make_swiss_roll, stretched along its length
// ---------------------------------------------------------------------------
export function swissRoll(n = 600, stretch = 1.6, seed = 0) {
  const rng = new Rng(seed + 5)
  const X: number[][] = []
  const t: number[] = []
  for (let i = 0; i < n; i++) {
    const tt = 1.5 * Math.PI * (1 + 2 * rng.next())
    const h = 21 * rng.next() * stretch
    X.push([tt * Math.cos(tt) + rng.normal(0, 0.15), h + rng.normal(0, 0.15),
      tt * Math.sin(tt) + rng.normal(0, 0.15)])
    t.push(tt)
  }
  return { X, t }
}

// ---------------------------------------------------------------------------
// the 600 digits, and the MNIST maps
// ---------------------------------------------------------------------------
export const DIGITS = digitsJson as { X: number[][]; y: number[] }

const mj = mnistJson as unknown as Record<string, number[]> & { y: number[]; perps: number[] }
function unpack(v: number[]): [number, number][] {
  const out: [number, number][] = []
  for (let i = 0; i < v.length; i += 2) out.push([v[i] / 10, v[i + 1] / 10])
  return out
}
export const MNIST = {
  y: mj.y,
  perps: mj.perps,
  pca: unpack(mj.pca),
  tsne: Object.fromEntries(mj.perps.map((p) => [p, unpack(mj[`tsne${p}`])])) as Record<number, [number, number][]>,
}

/** the deterministic vertical jitter of the 1-D strips */
export const jitter = (i: number) => (((i * 7) % 5) - 2) * 0.07

/** the index of the point nearest (x, y) */
export function nearest(X: number[][], x: number, y: number): number {
  let best = 0, bd = Infinity
  X.forEach((p, i) => { const d = (p[0] - x) ** 2 + (p[1] - y) ** 2; if (d < bd) { bd = d; best = i } })
  return best
}

export const TOY_DOMAIN: [number, number, number, number] = [-4.6, 4.6, -4.0, 4.3]
