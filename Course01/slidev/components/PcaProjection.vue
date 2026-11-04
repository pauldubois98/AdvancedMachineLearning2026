<!-- pca_projection: project a 2-D cloud on a direction; the direction of most
     variance keeps the most. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { histBars } from '../lib/hist'
import { mean, mvn, pvar } from '../lib/stats'
import { ellipseAxes, type Pt } from '../lib/geom'
import { BLUE, GREEN, GRID, MUTED, RED } from '../lib/theme'

const rho = ref(0.88)
const ang = ref(0)
const snap = ref(false)
const Z = mvn(new Rng(33), 300, [0, 0], [1, 0, 1])
const X = computed<Pt[]>(() => {
  const a = Math.sqrt(1.6), b = Math.sqrt(0.9), c = rho.value
  const P = Z.map(([u, v]) => [a * u, b * (c * u + Math.sqrt(1 - c * c) * v)] as Pt)
  const m = [mean(P.map((p) => p[0])), mean(P.map((p) => p[1]))]
  return P.map((p) => [p[0] - m[0], p[1] - m[1]] as Pt)
})
const cov = computed(() => {
  const x = X.value
  return [mean(x.map((p) => p[0] * p[0])), mean(x.map((p) => p[0] * p[1])), mean(x.map((p) => p[1] * p[1]))] as [number, number, number]
})
const pc = computed(() => ellipseAxes(cov.value))
const a = computed(() => (snap.value ? pc.value.angle : (ang.value * Math.PI) / 180))
const u = computed<Pt>(() => [Math.cos(a.value), Math.sin(a.value)])
const z = computed(() => X.value.map((p) => p[0] * u.value[0] + p[1] * u.value[1]))
const total = computed(() => cov.value[0] + cov.value[2])
const kept = computed(() => pvar(z.value) / total.value)
const best = computed(() => pc.value.r1 ** 2 / total.value)
const proj = computed<Pt[]>(() => z.value.map((t) => [t * u.value[0], t * u.value[1]]))
const segs = computed(() => [
  { a: [-5 * u.value[0], -5 * u.value[1]] as Pt, b: [5 * u.value[0], 5 * u.value[1]] as Pt, color: BLUE, width: 1.6 },
  ...X.value.filter((_, i) => i % 4 === 0).map((p, k) => ({ a: p, b: proj.value[k * 4], color: GRID, width: 0.7 })),
])
const dom: [number, number, number, number] = [-4.2, 4.2, -3, 3]
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 300 points from a 2-D Gaussian, centred; the slider sets the correlation. Pick a direction u (blue): each point is replaced by its coordinate z = uᵀx along it, and the grey segments are what is thrown away.</div>
    <div class="r3">
      <Plane :X="X" :colors="MUTED" :size="2.4" :domain="dom" title="the data" />
      <Plane :X="[...X, ...proj]" :colors="[...X.map(() => 'rgba(154,160,166,0.5)'), ...proj.map(() => BLUE)]" :size="2.2" :segments="segs" :domain="dom"
        :title="`the direction: ${(snap ? (pc.angle * 180) / Math.PI : ang).toFixed(0)}°`" :title-color="BLUE" />
      <LineChart :series="[]" :bars="histBars(z, -4.5, 4.5, 34, GREEN, 0.5)" :x-domain="[-4.5, 4.5]" :y-domain="[0, 0.75]" :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[]"
        x-label="z = Pᵀx ∈ ℝ" title="the projection" :title-color="GREEN" />
    </div>
    <div class="foot">variance kept: <b :style="{ color: kept > best - 0.005 ? GREEN : RED }">{{ (100 * kept).toFixed(1) }}%</b> of the total, at most {{ (100 * best).toFixed(1) }}% along the first principal axis. One number instead of two.</div>
    <div class="controls">
      <Knob v-model="ang" :min="-90" :max="90" :step="1" :digits="0" unit="°" label="direction" :color="BLUE" :disabled="snap" />
      <Toggle v-model="snap" label="snap to the most variance" :color="GREEN" />
      <Knob v-model="rho" :min="-0.97" :max="0.97" :step="0.01" label="correlation" color="#1b1b1b" />
    </div>
  </div>
</template>
