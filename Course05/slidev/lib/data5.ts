// The data of the deck. The JSON files live in Course05/data, written by
// scripts/make_data_c05.py from the same generators as the printed figures,
// so both decks show the same matrices.
import facesJson from '../../data/faces.json'
import topicsJson from '../../data/topics.json'
import spectralJson from '../../data/spectral.json'
import musicJson from '../../data/music.json'
import layersJson from '../../data/layers.json'
import ratingsJson from '../../data/ratings.json'
import armsJson from '../../data/arms.json'
import initJson from '../../data/init.json'
import choosingJson from '../../data/choosing.json'
import { Mat, f32, fromRows, mat, mul } from './mat'
import { Rng } from './rng'

// ------------------------------------------------------------------ faces
/** Olivetti faces at 32 x 32: one face per column, pixels in [0, 1] */
export const SIDE = facesJson.side
const facePixels = (() => {
  const bin = atob(facesJson.pixels)
  const out = new Float64Array(bin.length)
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i) / 255
  return out // face-major: face f, pixel q at f * SIDE² + q
})()

/** the first n faces as X, pixels x faces */
export function faces(n: number): Mat {
  const p = SIDE * SIDE
  const X = mat(p, n)
  for (let f = 0; f < n; f++) for (let q = 0; q < p; q++) X.a[q * n + f] = facePixels[f * p + q]
  return X
}

export function face(j: number): Float64Array {
  const p = SIDE * SIDE
  return facePixels.subarray(j * p, (j + 1) * p)
}

/** 16 PCA components and a rank-16 NMF (HALS) of the first 300 faces */
export const facesPca = { U: rows(f32(facesJson.pca), 16), s: facesJson.pcaS as number[], V: rows(f32(facesJson.pcaV), 16) }
export const facesNmf = { W: rows(f32(facesJson.nmfW), 16), H: rows(f32(facesJson.nmfH), 16) }

function rows(a: Float64Array, k: number): Float64Array[] {
  const m = a.length / k
  return Array.from({ length: k }, (_, i) => a.subarray(i * m, (i + 1) * m))
}

// ----------------------------------------------------------------- topics
export const topics = (() => {
  const vocab = topicsJson.vocab as string[]
  const rowsT = topicsJson.rows as [number[], number[]][]
  const X = mat(vocab.length, rowsT.length) // words x posts
  rowsT.forEach(([idx, val], j) => idx.forEach((w, t) => { X.a[w * rowsT.length + j] = val[t] }))
  return { X, vocab, groups: topicsJson.groups as string[], group: topicsJson.group as number[] }
})()

// --------------------------------------------------------------- spectral
export const spectral = (() => {
  const size = spectralJson.size
  const bands = spectralJson.bands as number[]
  const spectra = spectralJson.spectra as number[][] // 3 x 60
  const maps = f32(spectralJson.maps) // 3 x size²
  const n = size * size
  const S = mat(bands.length, 3)
  spectra.forEach((sp, k) => sp.forEach((v, b) => { S.a[b * 3 + k] = v }))
  const A = { r: 3, c: n, a: maps }
  const X = mul(S, A)
  const rng = new Rng(11)
  for (let i = 0; i < X.a.length; i++) X.a[i] = Math.max(X.a[i] + rng.normal(0, 0.002), 1e-4)
  return { size, bands, spectra, maps: A, X }
})()

// ------------------------------------------------------------------ music
export const music = {
  freqs: musicJson.freqs as number[],
  t: musicJson.t as number[],
  notes: musicJson.notes as number[][],
  env: musicJson.env as number[][],
  X: { r: musicJson.p, c: musicJson.n, a: f32(musicJson.X) } as Mat,
}

// ----------------------------------------------------------------- layers
export const layers = { X: fromRows(layersJson.X), W: fromRows(layersJson.W), H: fromRows(layersJson.H) }
// W was stored one column per row
layers.W = (() => { const t = layers.W; const o = mat(t.c, t.r); for (let i = 0; i < t.r; i++) for (let j = 0; j < t.c; j++) o.a[j * t.r + i] = t.a[i * t.c + j]; return o })()

// ---------------------------------------------------------------- ratings
/** items x users, 1 to 5; `u` hides a cell when u <= hide */
export const ratings = { full: fromRows(ratingsJson.full), u: fromRows(ratingsJson.u) }

export function ratingsMask(hide: number): Mat {
  const m = mat(ratings.full.r, ratings.full.c)
  for (let i = 0; i < m.a.length; i++) m.a[i] = ratings.u.a[i] > hide ? 1 : 0
  return m
}

// ------------------------------------------------------------------- misc
export const arms = fromRows(armsJson.X) // 2 x 140
export const initRace = initJson as { faces: number; r: number; traces: Record<string, number[]> }

// --------------------------------------------------------------- choosing
/** rank-r HALS fits of the 300 small faces, r = 2 ... 48, precomputed: the
 *  relative error, the parts (W columns), the weights (H rows), and each
 *  part's cosine with its match in a fit from another start */
export const choosing = choosingJson.fits.map((f) => {
  const bin = atob(f.W)
  const p = SIDE * SIDE
  const W = Array.from({ length: f.r }, (_, k) => {
    const out = new Float64Array(p)
    for (let q = 0; q < p; q++) out[q] = bin.charCodeAt(k * p + q) / 255
    return out
  })
  return { r: f.r, err: f.err, W, H: rows(f32(f.H), f.r), match: f.match as number[] }
})
