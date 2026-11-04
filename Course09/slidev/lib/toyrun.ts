// The toy's 1-D SNE run, every move kept: the step-3 slides walk through it.
// No early exaggeration and a small rate, so the moves are slow enough to
// follow (as in the printed figures).
import { TOY, TOY_N, TOY_PERP, toyP } from './data'
import { Embedding, pca } from './sne'

export const TOY_ITERS = 300

export interface ToyRun { Y: number[][]; kl: number[]; emb: (t: number) => Embedding }

const cache = new Map<string, ToyRun>()

export function toyRun(seed = 1, init: 'random' | 'pca' = 'random', lr = 0.3, perp = TOY_PERP): ToyRun {
  const key = `${seed}|${init}|${lr}|${perp}`
  const hit = cache.get(key)
  if (hit) return hit
  const { P } = toyP(perp)
  const make = () => {
    let Y0: number[][] | undefined
    if (init === 'pca') {
      const Z = pca(TOY.X, 1).Z.map((r) => r[0])
      const sd = Math.sqrt(Z.reduce((s, v) => s + v * v, 0) / Z.length)
      Y0 = Z.map((v) => [(v / sd) * 1e-4])
    }
    return new Embedding(P, TOY_N, { kind: 'sne', dim: 1, seed, lr, exag: 1, exagIters: 0, Y0, scale: 1e-4 })
  }
  const e = make()
  const Y: number[][] = [Array.from(e.Y)]
  const kl: number[] = [e.kl]
  for (let t = 0; t < TOY_ITERS; t++) {
    e.step()
    Y.push(Array.from(e.Y))
    kl.push(e.kl)
  }
  /** the run's state at move t, Q and all (replayed, cheap at n = 45) */
  const emb = (t: number) => {
    const f = make()
    for (let k = 0; k < t; k++) f.step()
    return f
  }
  const run = { Y, kl, emb }
  cache.set(key, run)
  return run
}
