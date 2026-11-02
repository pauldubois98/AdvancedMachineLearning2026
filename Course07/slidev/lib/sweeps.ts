// The two measured curves of the forest section are the only computations in
// the deck that take more than a frame: a forest per value of max_features, on
// 25 columns. They are computed once, in the background, one point at a time,
// and shared by both slides that draw them.
import { classif, split } from './databis'
import { fitForest, forestAccuracy, soloError, treeCorrelation } from './forest'

export interface MfPoint {
  k: number
  /** test error of the forest */
  err: number
  /** mean pairwise correlation of its trees */
  rho: number
  /** test error of the average single tree */
  solo: number
}

export const MF_KS = [1, 2, 3, 5, 8, 12, 18, 25]
const N_TREES = 50

const points: MfPoint[] = []
const listeners = new Set<(p: MfPoint[]) => void>()
let started = false

function step() {
  const data = classif({ n: 600, p: 25, informative: 12, redundant: 8, classSep: 0.7, flipY: 0.05, seed: 0 })
  const { Xtr, ytr, Xte, yte } = split(data, 0.5, 0)
  let i = 0
  const one = () => {
    const k = MF_KS[i]
    const f = fitForest(Xtr, ytr, { nTrees: N_TREES, maxFeatures: k, seed: 0 })
    points.push({
      k,
      err: 1 - forestAccuracy(f, Xte, yte),
      rho: treeCorrelation(f, Xte),
      solo: soloError(f, Xte, yte),
    })
    listeners.forEach((l) => l(points.slice()))
    if (++i < MF_KS.length) setTimeout(one, 0)
  }
  setTimeout(one, 0)
}

/** Subscribe to the sweep; what is already computed arrives immediately. */
export function mfSweep(on: (p: MfPoint[]) => void): () => void {
  listeners.add(on)
  on(points.slice())
  if (!started) {
    started = true
    step()
  }
  return () => listeners.delete(on)
}
