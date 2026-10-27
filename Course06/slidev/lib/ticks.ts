/** 1-2-5 ticks inside [lo, hi], for the log-scale loss curves */
export function logTicks(lo: number, hi: number): number[] {
  const out: number[] = []
  if (!(lo > 0) || !(hi > lo)) return out
  for (let e = Math.floor(Math.log10(lo)); e <= Math.ceil(Math.log10(hi)); e++) {
    for (const m of [1, 2, 5]) {
      const v = m * 10 ** e
      if (v >= lo && v <= hi) out.push(v)
    }
  }
  // too many: keep the powers of ten
  return out.length > 7 ? out.filter((v) => Math.abs(Math.log10(v) - Math.round(Math.log10(v))) < 1e-9) : out
}

/** about n round ticks inside [lo, hi], for a linear axis */
export function niceTicks(lo: number, hi: number, n = 5): number[] {
  const raw = (hi - lo) / n
  const p = 10 ** Math.floor(Math.log10(raw))
  const step = [1, 2, 5, 10].map((m) => m * p).find((s) => s >= raw) ?? raw
  const out: number[] = []
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-12; v += step) out.push(+v.toPrecision(12))
  return out
}
