/** A seeded generator, so every slide shows the same cloud on every machine. */
export class Rng {
  private s: number

  constructor(seed = 1) {
    this.s = (seed >>> 0) || 1
  }

  /** mulberry32 */
  next(): number {
    this.s = (this.s + 0x6d2b79f5) >>> 0
    let t = this.s
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }

  uniform(lo = 0, hi = 1): number {
    return lo + (hi - lo) * this.next()
  }

  /** Box–Muller, one value at a time. */
  normal(mu = 0, sigma = 1): number {
    let u = 0
    while (u === 0) u = this.next()
    const v = this.next()
    return mu + sigma * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
  }
}
