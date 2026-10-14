// The density family: DBSCAN with sklearn's semantics, the core distance and
// the mutual-reachability transform, Prim's spanning tree, and HDBSCAN's
// condensed tree with its stabilities and excess-of-mass selection.
import { Pts, distances } from './data4'
import { Linkage, relabel } from './hier'

export const NOISE = -1

export interface DbscanResult {
  labels: number[]
  core: boolean[]
  border: boolean[]
  noise: boolean[]
  /** how many points sit within eps of each point, itself included */
  counts: number[]
}

/** DBSCAN. `minPts` counts the point itself, and `eps` is inclusive, as in
 *  sklearn's DBSCAN(eps, min_samples). */
export function dbscan(X: Pts, eps: number, minPts: number, D?: Float64Array[]): DbscanResult {
  const n = X.length
  const dist = D ?? distances(X)
  const neigh: number[][] = []
  const counts: number[] = []
  for (let i = 0; i < n; i++) {
    const list: number[] = []
    for (let j = 0; j < n; j++) if (i !== j && dist[i][j] <= eps) list.push(j)
    neigh.push(list)
    counts.push(list.length + 1)
  }
  const core = counts.map((c) => c >= minPts)
  const labels = new Array(n).fill(NOISE)
  let k = 0
  for (let i = 0; i < n; i++) {
    if (!core[i] || labels[i] !== NOISE) continue
    // grow one cluster: core points pass their neighbourhood on, border
    // points join without theirs
    const stack = [i]
    labels[i] = k
    while (stack.length) {
      const p = stack.pop()!
      for (const q of neigh[p]) {
        if (labels[q] === NOISE) {
          labels[q] = k
          if (core[q]) stack.push(q)
        }
      }
    }
    k++
  }
  const border = labels.map((l, i) => l !== NOISE && !core[i])
  return { labels, core, border, noise: labels.map((l) => l === NOISE), counts }
}

/** Distance to the kth other point: HDBSCAN's core_k. Self excluded. */
export function coreDistances(X: Pts, k: number, D?: Float64Array[]): number[] {
  const dist = D ?? distances(X)
  return dist.map((row) => {
    const d = Array.from(row).sort((a, b) => a - b)
    return d[Math.min(k, d.length - 1)]
  })
}

/** Distance to the kth nearest neighbour counting the point itself, which is
 *  what sklearn's NearestNeighbors(n_neighbors=k).kneighbors()[:, -1] gives:
 *  the elbow curve of the epsilon slide. */
export function kthNeighbourDistances(X: Pts, k: number, D?: Float64Array[]): number[] {
  return coreDistances(X, Math.max(1, k - 1), D)
}

/** max(core(i), core(j), d(i, j)): sparse points get pushed away. */
export function mutualReachability(
  X: Pts,
  k: number,
  D?: Float64Array[],
): { mr: Float64Array[]; core: number[]; d: Float64Array[] } {
  const d = D ?? distances(X)
  const core = coreDistances(X, k, d)
  const n = X.length
  const mr: Float64Array[] = Array.from({ length: n }, () => new Float64Array(n))
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const v = Math.max(core[i], core[j], d[i][j])
      mr[i][j] = v
      mr[j][i] = v
    }
  }
  return { mr, core, d }
}

export interface Edge {
  i: number
  j: number
  w: number
}

/** Prim's algorithm: grow one tree, always taking its cheapest exit edge. */
export function primMst(D: Float64Array[] | number[][]): Edge[] {
  const n = D.length
  const inside = new Array(n).fill(false)
  const best = new Float64Array(n).fill(Infinity)
  const from = new Int32Array(n).fill(0)
  inside[0] = true
  for (let j = 1; j < n; j++) { best[j] = D[0][j]; from[j] = 0 }
  const edges: Edge[] = []
  for (let step = 1; step < n; step++) {
    let pick = -1
    for (let j = 0; j < n; j++) if (!inside[j] && (pick < 0 || best[j] < best[pick])) pick = j
    edges.push({ i: from[pick], j: pick, w: best[pick] })
    inside[pick] = true
    for (let j = 0; j < n; j++) {
      if (!inside[j] && D[pick][j] < best[j]) { best[j] = D[pick][j]; from[j] = pick }
    }
  }
  return edges
}

/** Single linkage read off a spanning tree: add edges cheapest first. This is
 *  exactly scipy's linkage(..., 'single') on the same distances. */
export function mstToLinkage(edges: Edge[], n: number): Linkage {
  const order = [...edges].sort((a, b) => a.w - b.w)
  const parent = Array.from({ length: 2 * n - 1 }, (_, i) => i)
  const top = new Array(2 * n - 1).fill(0).map((_, i) => i)
  const find = (i: number): number => (parent[i] === i ? i : (parent[i] = find(parent[i])))
  const size = new Array(2 * n - 1).fill(1)
  const out: Linkage = []
  order.forEach((e, r) => {
    const ra = find(e.i)
    const rb = find(e.j)
    const ca = top[ra]
    const cb = top[rb]
    out.push({
      a: Math.min(ca, cb),
      b: Math.max(ca, cb),
      height: e.w,
      size: size[ca] + size[cb],
    })
    parent[rb] = ra
    top[ra] = n + r
    size[n + r] = size[ca] + size[cb]
  })
  return out
}

export interface CondensedCluster {
  parent: number | null
  lamBirth: number
  lamDeath: number
  /** the lambda at which each point fell out of this cluster, sorted */
  falls: number[]
  children: number[]
  /** how many points the cluster held when it was born */
  size0: number
  stability: number
}

export interface Condensed {
  clusters: Map<number, CondensedCluster>
  /** the condensed cluster each point sat in when it left the tree */
  pointParent: number[]
  /** the lambda at which it left */
  pointLambda: number[]
}

/** The leaves under every node of a linkage tree. */
export function leavesOf(Z: Linkage): number[][] {
  const n = Z.length + 1
  const out: number[][] = Array.from({ length: 2 * n - 1 }, () => [])
  for (let i = 0; i < n; i++) out[i] = [i]
  Z.forEach((m, r) => { out[n + r] = out[m.a].concat(out[m.b]) })
  return out
}

/** HDBSCAN's condensed tree. Walking the single-linkage tree down from the
 *  root, a split only counts as a split when both sides still hold `minSize`
 *  points; otherwise the small side is a handful of points falling out of a
 *  cluster that carries on. */
export function condense(Z: Linkage, minSize: number): Condensed {
  const n = Z.length + 1
  const size = new Array(2 * n - 1).fill(1)
  Z.forEach((m, r) => { size[n + r] = m.size })
  const leaves = leavesOf(Z)
  const clusters = new Map<number, CondensedCluster>()
  const pointParent = new Array(n).fill(0)
  const pointLambda = new Array(n).fill(0)
  const make = (parent: number | null, lamBirth: number, size0: number): CondensedCluster => ({
    parent, lamBirth, lamDeath: lamBirth, falls: [], children: [], size0, stability: 0,
  })
  clusters.set(0, make(null, 0, size[2 * n - 2]))
  let next = 0
  const stack: [number, number][] = [[2 * n - 2, 0]]
  while (stack.length) {
    const [node, cid] = stack.pop()!
    if (node < n) continue
    const m = Z[node - n]
    const lam = m.height > 0 ? 1 / m.height : Infinity
    const bigA = size[m.a] >= minSize
    const bigB = size[m.b] >= minSize
    const c = clusters.get(cid)!
    if (bigA && bigB) {
      c.lamDeath = lam
      for (const child of [m.a, m.b]) {
        next++
        clusters.set(next, make(cid, lam, size[child]))
        c.children.push(next)
        stack.push([child, next])
      }
    } else if (bigA || bigB) {
      const keep = bigA ? m.a : m.b
      const drop = bigA ? m.b : m.a
      for (const i of leaves[drop]) {
        c.falls.push(lam)
        pointParent[i] = cid
        pointLambda[i] = lam
      }
      stack.push([keep, cid])
    } else {
      for (const i of leaves[node]) {
        c.falls.push(lam)
        pointParent[i] = cid
        pointLambda[i] = lam
      }
      c.lamDeath = lam
    }
  }
  for (const c of clusters.values()) {
    c.falls.sort((a, b) => a - b)
    const stay = c.size0 - c.falls.length
    c.stability = c.falls.reduce((s, l) => s + (l - c.lamBirth), 0)
    if (stay) c.stability += stay * (c.lamDeath - c.lamBirth)
  }
  return { clusters, pointParent, pointLambda }
}

/** The bar tree alone, for the slides that only draw it. */
export function condensedTree(Z: Linkage, minSize: number): Map<number, CondensedCluster> {
  return condense(Z, minSize).clusters
}

/** Excess of mass: keep a cluster unless its children are worth more together.
 *  Returns the selected ids and, per cluster, the score of its whole subtree. */
export function selectClusters(
  clusters: Map<number, CondensedCluster>,
): { selected: number[]; score: Map<number, number>; chosen: Map<number, boolean> } {
  const score = new Map<number, number>()
  const chosen = new Map<number, boolean>()
  const visit = (cid: number): number => {
    const c = clusters.get(cid)!
    if (!c.children.length) {
      score.set(cid, c.stability)
      chosen.set(cid, true)
      return c.stability
    }
    const kids = c.children.reduce((s, k) => s + visit(k), 0)
    if (kids > c.stability) {
      score.set(cid, kids)
      chosen.set(cid, false)
      return kids
    }
    score.set(cid, c.stability)
    chosen.set(cid, true)
    return c.stability
  }
  visit(0)
  // the root is never a cluster of its own: everything would be one cluster
  const selected: number[] = []
  const walk = (cid: number) => {
    if (cid !== 0 && chosen.get(cid)) { selected.push(cid); return }
    clusters.get(cid)!.children.forEach(walk)
  }
  walk(0)
  return { selected, score, chosen }
}

/** Which condensed cluster each node of the single-linkage tree belongs to, so
 *  the raw dendrogram can be painted in the colours it condenses to. */
export function condensedOwners(Z: Linkage, minSize: number): Map<number, number> {
  const n = Z.length + 1
  const size = new Array(2 * n - 1).fill(1)
  Z.forEach((m, r) => { size[n + r] = m.size })
  const owner = new Map<number, number>([[2 * n - 2, 0]])
  let next = 0
  const stack: [number, number][] = [[2 * n - 2, 0]]
  while (stack.length) {
    const [node, cid] = stack.pop()!
    if (node < n) continue
    const m = Z[node - n]
    if (size[m.a] >= minSize && size[m.b] >= minSize) {
      for (const child of [m.a, m.b]) {
        next++
        owner.set(child, next)
        stack.push([child, next])
      }
    } else if (Math.max(size[m.a], size[m.b]) >= minSize) {
      const keep = size[m.a] >= minSize ? m.a : m.b
      owner.set(keep, cid)
      stack.push([keep, cid])
    }
  }
  return owner
}

/** HDBSCAN end to end. A point carries the label of the nearest selected
 *  cluster at or above the condensed cluster it was sitting in when it left
 *  the tree, as sklearn's HDBSCAN does; whatever hangs off the root is noise. */
export function hdbscan(
  X: Pts,
  minClusterSize = 10,
  minPts?: number,
  D?: Float64Array[],
): {
  labels: number[]
  Z: Linkage
  clusters: Map<number, CondensedCluster>
  selected: number[]
} {
  const k = Math.max(1, (minPts ?? minClusterSize) - 1)
  const { mr } = mutualReachability(X, k, D)
  const Z = mstToLinkage(primMst(mr), X.length)
  const { clusters, pointParent } = condense(Z, minClusterSize)
  const { selected } = selectClusters(clusters)
  const rank = new Map<number, number>()
  selected.forEach((cid, i) => rank.set(cid, i))
  const labels = X.map((_, i) => {
    let cid: number | null = pointParent[i]
    while (cid !== null && !rank.has(cid)) cid = clusters.get(cid)!.parent
    return cid === null ? NOISE : rank.get(cid)!
  })
  return { labels: relabel(labels), Z, clusters, selected }
}
