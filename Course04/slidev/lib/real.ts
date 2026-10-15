// The three real datasets of the use-case slides. The JSON files live in
// Course04/data, written by scripts/make_realdata_c04.py, and the printed
// figures read the very same files, so both decks show the same rows.
import flowerJson from '../../data/flower.json'
import newsJson from '../../data/newsgroups.json'
import httpJson from '../../data/http.json'
import { Pts } from './data4'
import { kmeans, KmeansRun } from './cluster'
import { Rng } from './rng'

// ------------------------------------------------------------------- flower
/** the photo, 160 x 107, one [r, g, b] in [0, 1] per pixel, row by row */
export const flower = (() => {
  const bin = atob(flowerJson.rgb)
  const px: Pts = []
  for (let i = 0; i < bin.length; i += 3) {
    px.push([bin.charCodeAt(i) / 255, bin.charCodeAt(i + 1) / 255, bin.charCodeAt(i + 2) / 255])
  }
  return { width: flowerJson.width, height: flowerJson.height, px }
})()

// --------------------------------------------------------------- newsgroups
export const news = {
  groups: newsJson.groups as string[],
  group: newsJson.group as number[],
  vocab: newsJson.vocab as string[],
  /** sparse rows of unit length: [term indices, weights] */
  rows: newsJson.rows as [number[], number[]][],
}

/**
 * k-means on the sparse TF-IDF rows, k-means++ seeded, best of `nInit`. A row
 * x has unit length, so |x - m|^2 = 1 + |m|^2 - 2 x.m needs only x's own terms.
 */
export function kmeansSparse(k: number, seed = 0, nInit = 4): { labels: number[]; mu: number[][] } {
  const { rows, vocab } = news
  const V = vocab.length
  const n = rows.length
  const dot = (r: [number[], number[]], m: number[]) => {
    let s = 0
    for (let t = 0; t < r[0].length; t++) s += r[1][t] * m[r[0][t]]
    return s
  }
  const dense = (r: [number[], number[]]) => {
    const m = new Array(V).fill(0)
    r[0].forEach((j, t) => { m[j] = r[1][t] })
    return m
  }
  let best: { labels: number[]; mu: number[][]; cost: number } | null = null
  for (let run = 0; run < nInit; run++) {
    const rng = new Rng(seed * 100 + run + 1)
    const mu = [dense(rows[Math.floor(rng.next() * n)])]
    const d2 = rows.map((r) => 2 - 2 * dot(r, mu[0]))
    while (mu.length < k) {
      let t = rng.next() * d2.reduce((s, v) => s + Math.max(v, 0), 0)
      let pick = n - 1
      for (let i = 0; i < n; i++) { t -= Math.max(d2[i], 0); if (t <= 0) { pick = i; break } }
      mu.push(dense(rows[pick]))
      rows.forEach((r, i) => { d2[i] = Math.min(d2[i], 2 - 2 * dot(r, mu[mu.length - 1])) })
    }
    let labels = new Array(n).fill(-1)
    let cost = 0
    for (let it = 0; it < 50; it++) {
      const norms = mu.map((m) => m.reduce((s, v) => s + v * v, 0))
      cost = 0
      let changed = false
      rows.forEach((r, i) => {
        let bl = 0
        let bd = Infinity
        for (let c = 0; c < k; c++) {
          const dd = 1 + norms[c] - 2 * dot(r, mu[c])
          if (dd < bd) { bd = dd; bl = c }
        }
        cost += bd
        if (labels[i] !== bl) { labels[i] = bl; changed = true }
      })
      if (!changed) break
      const sums = mu.map(() => new Array(V).fill(0))
      const counts = new Array(k).fill(0)
      rows.forEach((r, i) => {
        counts[labels[i]]++
        r[0].forEach((j, t) => { sums[labels[i]][j] += r[1][t] })
      })
      sums.forEach((s, c) => { if (counts[c]) mu[c] = s.map((v) => v / counts[c]) })
    }
    if (!best || cost < best.cost) best = { labels: labels.slice(), mu: mu.map((m) => m.slice()), cost }
  }
  return { labels: best!.labels, mu: best!.mu }
}

// --------------------------------------------------------------------- http
/** 1230 web-server connections: log duration, log bytes in, log bytes back */
export const http = {
  X: httpJson.X as Pts,
  attack: httpJson.attack as number[],
}

/**
 * k-means, then each connection's distance to the nearest centre of a cluster
 * holding at least 5% of the rows: a tight crowd of attacks would otherwise
 * earn a centre of its own, and look perfectly normal.
 */
export function anomalyScores(k: number): { run: KmeansRun; big: boolean[]; score: number[] } {
  const run = kmeans(http.X, k, 0, 10)
  const size = run.mu.map((_, c) => run.labels.filter((l) => l === c).length)
  const big = size.map((s) => s >= 0.05 * http.X.length)
  const score = http.X.map((p) => {
    let bd = Infinity
    run.mu.forEach((m, c) => {
      if (!big[c]) return
      bd = Math.min(bd, Math.hypot(...p.map((v, j) => v - m[j])))
    })
    return bd
  })
  return { run, big, score }
}
