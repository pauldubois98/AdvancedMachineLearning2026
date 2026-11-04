<!-- lda_why_linear: with one shared covariance, the problem is 1-D along
     w = Σ⁻¹(μ₂ − μ₁): project, and cut halfway. Any other direction overlaps more. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { histBars, curve } from '../lib/hist'
import { inv2, mean, mulv, npdf, pvar, twoGaussians } from '../lib/stats'
import { classColors } from '../lib/cls'
import type { Cov, Pt } from '../lib/geom'
import { BLUE, GREEN, INK, RED } from '../lib/theme'

const COV: Cov = [1.0, 0.35, 0.7]
const M0: Pt = [-1.1, -0.5], M1: Pt = [1.3, 0.7]
const data = twoGaussians(new Rng(43), 200, M0, M1, COV)
const wv = mulv(inv2(COV), [M1[0] - M0[0], M1[1] - M0[1]])
const wAng = (Math.atan2(wv[1], wv[0]) * 180) / Math.PI
const ang = ref(60)
const snap = ref(false)
const a = computed(() => ((snap.value ? wAng : ang.value) * Math.PI) / 180)
const u = computed<Pt>(() => [Math.cos(a.value), Math.sin(a.value)])
const z = computed(() => data.X.map(([x, y]) => x * u.value[0] + y * u.value[1]))
const parts = computed(() => [0, 1].map((k) => z.value.filter((_, i) => data.y[i] === k)))
const ms = computed(() => parts.value.map(mean))
const within = computed(() => Math.sqrt((pvar(parts.value[0]) + pvar(parts.value[1])) / 2))
const cut = computed(() => (ms.value[0] + ms.value[1]) / 2)
const err = computed(() => {
  const s = Math.sign(ms.value[1] - ms.value[0])
  return z.value.reduce((e, v, i) => e + ((s * (v - cut.value) > 0 ? 1 : 0) !== data.y[i] ? 1 : 0), 0) / z.value.length
})
const ratio = computed(() => Math.abs(ms.value[1] - ms.value[0]) / within.value)
const c: Pt = [(M0[0] + M1[0]) / 2, (M0[1] + M1[1]) / 2]
const dom: [number, number, number, number] = [-4.2, 4.6, -3.4, 3.6]
const lo = -5.5, hi = 5.5
const line = computed(() => {
  // the cut in the plane: perpendicular to u, through the projected threshold
  const p: Pt = [u.value[0] * cut.value, u.value[1] * cut.value]
  const t: Pt = [-u.value[1], u.value[0]]
  return { a: [p[0] - 8 * t[0], p[1] - 8 * t[1]] as Pt, b: [p[0] + 8 * t[0], p[1] + 8 * t[1]] as Pt, color: INK, width: 2.4 }
})
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 200 points per class, same covariance Σ. Pick a direction (the green arrow): every point is projected on it, the right panel shows the two projected classes, and the cut is halfway between their means.</div>
    <div class="r2">
      <Plane :X="data.X" :colors="classColors(data.y)" :size="2.4" :domain="dom"
        :ellipses="[{ mu: M0, S: COV, color: BLUE }, { mu: M1, S: COV, color: RED }]"
        :segments="[line, { a: c, b: [c[0] + 1.6 * u[0], c[1] + 1.6 * u[1]], color: GREEN, width: 3, arrow: true }]"
        title="same shape for both classes" />
      <LineChart :series="[0, 1].map((k) => ({ points: curve((t) => npdf(t, ms[k], within), lo, hi), color: k ? RED : BLUE }))"
        :bars="[...histBars(parts[0], lo, hi, 44, BLUE, 0.3), ...histBars(parts[1], lo, hi, 44, RED, 0.3)]"
        :x-domain="[lo, hi]" :y-domain="[0, 0.62 / Math.max(within, 0.6)]" :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[]" x-label="projection uᵀx"
        :vlines="[{ x: cut, color: INK, dash: '' }]" title="the projected classes" />
    </div>
    <div class="foot">separation (gap between the means / spread inside a class) = <b :style="{ color: GREEN }">{{ ratio.toFixed(2) }}</b> · training error <b>{{ (100 * err).toFixed(1) }}%</b>. It is largest along w = Σ⁻¹(μ₂ − μ₁), at {{ wAng.toFixed(0) }}°, which is not the direction between the means: then the cut is LDA's straight boundary.</div>
    <div class="controls">
      <Knob v-model="ang" :min="-90" :max="90" :step="1" :digits="0" unit="°" label="direction" :color="GREEN" :disabled="snap" />
      <Toggle v-model="snap" label="snap to w = Σ⁻¹(μ₂ − μ₁)" :color="GREEN" />
    </div>
  </div>
</template>
