// Agglomerative clustering: the Lance-Williams update, scipy's linkage matrix,
// the two ways of cutting it, and a dendrogram layout. Ward's coefficients are
// scipy's, so the trees match scipy.cluster.hierarchy.linkage.
import { Pts, distances } from './data4'

export type Method = 'single' | 'complete' | 'average' | 'ward' | 'weighted' | 'centroid'

/** One merge: the two clusters joined, the height, and the size of the union.
 *  Cluster i < n is the point i; cluster n + r is the result of merge r, which
 *  is scipy's numbering. */
export interface Merge {
  a: number
  b: number
  height: number
  size: number
}

export type Linkage = Merge[]

/** The Lance-Williams coefficients: D(i u j, k) from D(i,k), D(j,k), D(i,j). */
function update(
  method: Method,
  dik: number,
  djk: number,
  dij: number,
  ni: number,
  nj: number,
  nk: number,
): number {
  switch (method) {
    case 'single':
      return Math.min(dik, djk)
    case 'complete':
      return Math.max(dik, djk)
    case 'average':
      return (ni * dik + nj * djk) / (ni + nj)
    case 'weighted':
      return (dik + djk) / 2
    case 'ward':
      return Math.sqrt(
        ((ni + nk) * dik * dik + (nj + nk) * djk * djk - nk * dij * dij) / (ni + nj + nk),
      )
    case 'centroid':
      return Math.sqrt(
        (ni * dik * dik + nj * djk * djk) / (ni + nj) - (ni * nj * dij * dij) / (ni + nj) ** 2,
      )
  }
}

/** scipy's linkage, from the points or from a ready distance matrix. */
export function linkage(X: Pts, method: Method = 'average'): Linkage {
  return linkageFrom(distances(X), method)
}

export function linkageFrom(D0: Float64Array[] | number[][], method: Method = 'average'): Linkage {
  const n = D0.length
  // the working distance matrix, indexed by live cluster slot
  const D: Float64Array[] = Array.from({ length: n }, (_, i) => Float64Array.from(D0[i]))
  const id = Array.from({ length: n }, (_, i) => i) // slot -> cluster id
  const size = new Array(n).fill(1)
  const live = new Array(n).fill(true)
  const out: Linkage = []
  for (let step = 0; step < n - 1; step++) {
    let bi = -1
    let bj = -1
    let best = Infinity
    for (let i = 0; i < n; i++) {
      if (!live[i]) continue
      for (let j = i + 1; j < n; j++) {
        if (!live[j]) continue
        if (D[i][j] < best) { best = D[i][j]; bi = i; bj = j }
      }
    }
    const ni = size[bi]
    const nj = size[bj]
    out.push({
      a: Math.min(id[bi], id[bj]),
      b: Math.max(id[bi], id[bj]),
      height: best,
      size: ni + nj,
    })
    for (let k = 0; k < n; k++) {
      if (!live[k] || k === bi || k === bj) continue
      const v = update(method, D[bi][k], D[bj][k], best, ni, nj, size[k])
      D[bi][k] = v
      D[k][bi] = v
    }
    live[bj] = false
    size[bi] = ni + nj
    id[bi] = n + step
  }
  return out
}

/** The members of every cluster id, 0 .. 2n-2. */
export function members(Z: Linkage): number[][] {
  const n = Z.length + 1
  const out: number[][] = Array.from({ length: 2 * n - 1 }, () => [])
  for (let i = 0; i < n; i++) out[i] = [i]
  Z.forEach((m, r) => { out[n + r] = out[m.a].concat(out[m.b]) })
  return out
}

/** Cut the tree so that no merge above `height` is taken. Labels from 0. */
export function fclusterDist(Z: Linkage, height: number): number[] {
  const n = Z.length + 1
  const parent = Array.from({ length: 2 * n - 1 }, (_, i) => i)
  const find = (i: number): number => (parent[i] === i ? i : (parent[i] = find(parent[i])))
  Z.forEach((m, r) => {
    if (m.height <= height) {
      parent[find(m.a)] = n + r
      parent[find(m.b)] = n + r
      parent[n + r] = n + r
    }
  })
  return relabel(Array.from({ length: n }, (_, i) => find(i)))
}

/** Cut the tree into exactly `k` clusters (scipy's maxclust). */
export function fclusterMaxclust(Z: Linkage, k: number): number[] {
  const n = Z.length + 1
  const take = Math.max(0, n - k)
  const parent = Array.from({ length: 2 * n - 1 }, (_, i) => i)
  const find = (i: number): number => (parent[i] === i ? i : (parent[i] = find(parent[i])))
  for (let r = 0; r < take; r++) {
    parent[find(Z[r].a)] = n + r
    parent[find(Z[r].b)] = n + r
    parent[n + r] = n + r
  }
  return relabel(Array.from({ length: n }, (_, i) => find(i)))
}

/** Rewrite arbitrary group keys as 0, 1, 2, ... in order of first appearance. */
export function relabel(raw: number[]): number[] {
  const seen = new Map<number, number>()
  return raw.map((v) => {
    if (v < 0) return -1
    if (!seen.has(v)) seen.set(v, seen.size)
    return seen.get(v)!
  })
}

export interface DendroLink {
  /** the four corners of the staple, in (x, height) data coordinates */
  x: [number, number, number, number]
  y: [number, number, number, number]
  /** the cluster id of the merge this staple draws */
  id: number
  height: number
}

export interface Dendrogram {
  links: DendroLink[]
  /** leaf order, left to right, and the x of every cluster id */
  leaves: number[]
  pos: number[]
  maxHeight: number
}

/** scipy's dendrogram layout: leaves 10, 30, 50, ... in tree order. */
export function dendrogram(Z: Linkage): Dendrogram {
  const n = Z.length + 1
  const leaves: number[] = []
  const walk = (node: number) => {
    if (node < n) { leaves.push(node); return }
    walk(Z[node - n].a)
    walk(Z[node - n].b)
  }
  if (n > 1) walk(2 * n - 2)
  else leaves.push(0)
  const pos = new Array(2 * n - 1).fill(0)
  leaves.forEach((leaf, i) => { pos[leaf] = 5 + 10 * i })
  const links: DendroLink[] = []
  Z.forEach((m, r) => {
    const ha = m.a < n ? 0 : Z[m.a - n].height
    const hb = m.b < n ? 0 : Z[m.b - n].height
    pos[n + r] = (pos[m.a] + pos[m.b]) / 2
    links.push({
      x: [pos[m.a], pos[m.a], pos[m.b], pos[m.b]],
      y: [ha, m.height, m.height, hb],
      id: n + r,
      height: m.height,
    })
  })
  return { links, leaves, pos, maxHeight: Z.length ? Z[Z.length - 1].height : 1 }
}

/** The Ward cost of merging two groups: the inertia the merge adds. */
export function wardCost(ni: number, nj: number, d: number): number {
  return ((ni * nj) / (ni + nj)) * d * d
}

/** The four classic group-to-group distances, for the definitions slide. */
export function groupDistances(A: Pts, B: Pts): {
  single: number
  complete: number
  average: number
  centroid: number
  ward: number
  minPair: [number, number]
  maxPair: [number, number]
} {
  let single = Infinity
  let complete = -Infinity
  let sum = 0
  let minPair: [number, number] = [0, 0]
  let maxPair: [number, number] = [0, 0]
  A.forEach((a, i) => {
    B.forEach((b, j) => {
      const d = Math.hypot(a[0] - b[0], a[1] - b[1])
      sum += d
      if (d < single) { single = d; minPair = [i, j] }
      if (d > complete) { complete = d; maxPair = [i, j] }
    })
  })
  const mean = (P: Pts) => [
    P.reduce((s, p) => s + p[0], 0) / P.length,
    P.reduce((s, p) => s + p[1], 0) / P.length,
  ]
  const ma = mean(A)
  const mb = mean(B)
  const centroid = Math.hypot(ma[0] - mb[0], ma[1] - mb[1])
  return {
    single,
    complete,
    average: sum / (A.length * B.length),
    centroid,
    ward: Math.sqrt(((2 * A.length * B.length) / (A.length + B.length)) * centroid * centroid),
    minPair,
    maxPair,
  }
}
