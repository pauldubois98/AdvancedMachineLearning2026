<!-- the two equivalent views: turn the axis and watch the projected variance
     and the reconstruction error trade off; they always add up to the total. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { pca } from '../lib/sne'
import { GREEN, GRID, HIGH, MUTED, PCA_C, RED } from '../lib/theme'
import { linspace, type Pt } from '../lib/geom'

const theta = ref(20)
const r = new Rng(3)
const X: Pt[] = Array.from({ length: 300 }, () => {
  const u = r.normal(), v = r.normal()
  return [1.4 * u, 1.4 * (-0.75 * u + Math.sqrt(1 - 0.5625) * v) * 0.8]
})
const fit = pca(X, 2)
const n = X.length
const S = [[0, 0], [0, 0]]
for (const [x, y] of X) { S[0][0] += x * x / (n - 1); S[0][1] += x * y / (n - 1); S[1][1] += y * y / (n - 1) }
S[1][0] = S[0][1]
const total = S[0][0] + S[1][1]
const varAt = (deg: number) => { const a = (deg * Math.PI) / 180, c = Math.cos(a), s = Math.sin(a); return c * c * S[0][0] + 2 * c * s * S[0][1] + s * s * S[1][1] }
const pcaDeg = ((Math.atan2(fit.vectors[0][1], fit.vectors[0][0]) * 180) / Math.PI + 360) % 180
const u = computed<Pt>(() => [Math.cos((theta.value * Math.PI) / 180), Math.sin((theta.value * Math.PI) / 180)])
const proj = computed<Pt[]>(() => X.map(([x, y]) => { const t = x * u.value[0] + y * u.value[1]; return [t * u.value[0], t * u.value[1]] }))
const segs = computed(() => [
  { a: [-8 * u.value[0], -8 * u.value[1]] as Pt, b: [8 * u.value[0], 8 * u.value[1]] as Pt, color: PCA_C, width: 1.6 },
  ...X.filter((_, i) => i % 3 === 0).map((x, k) => ({ a: x, b: proj.value[k * 3], color: RED, width: 0.7 })),
])
const v = computed(() => varAt(theta.value))
const grid = linspace(0, 180, 181)
</script>

<template>
  <div class="cmp top">
    <div class="r2" style="text-align: center">
      <div><span class="cap" style="color: var(--red)">1. minimise the error</span>&nbsp; <Tex formula="\min_{P}\ \sum_i \| x_i - P P^T x_i \|^2" /></div>
      <div><span class="cap" style="color: var(--green)">2. maximise the variance</span>&nbsp; <Tex formula="\max_{\|p\| = 1}\ \| X p \|^2" /></div>
    </div>
    <div class="r2">
      <Plane :X="[...X, ...proj]" :colors="[...X.map(() => 'rgba(43,108,176,0.5)'), ...proj.map(() => PCA_C)]" :size="2"
        :segments="segs" :domain="[-4.5, 4.5, -3.5, 3.5]" :title="`an axis at ${theta.toFixed(0)}°: red = what is lost`" />
      <LineChart
        :series="[{ points: grid.map((d) => [d, varAt(d)]), color: GREEN, width: 2.4 }, { points: grid.map((d) => [d, total - varAt(d)]), color: RED, width: 2.4 }]"
        :vlines="[{ x: theta, color: PCA_C }, { x: pcaDeg, color: MUTED, dash: '4 4', label: 'PCA' }]"
        :dots="[{ x: theta, y: v, color: GREEN, r: 5 }, { x: theta, y: total - v, color: RED, r: 5 }]"
        :labels="[{ x: 4, y: total * 0.95, text: 'projected variance', color: GREEN, anchor: 'start' }, { x: 4, y: total * 0.86, text: 'reconstruction error', color: RED, anchor: 'start' }]"
        :x-domain="[0, 180]" :y-domain="[0, total * 1.02]" :x-ticks="[0, 45, 90, 135, 180]" :y-ticks="[]" x-label="angle of the axis (°)"
        title="variance + error = total, whatever the axis"
      />
    </div>
    <div class="foot">Variance <b style="color: var(--green)">{{ v.toFixed(2) }}</b> + error <b style="color: var(--red)">{{ (total - v).toFixed(2) }}</b> = {{ total.toFixed(2) }}:
      the axis that maximises one minimises the other; both are the top eigenvector of Σ.</div>
    <div class="controls">
      <Knob v-model="theta" :min="0" :max="180" :step="1" :digits="0" label="axis angle" unit="°" :color="PCA_C" />
      <button class="snap" @click="theta = Math.round(pcaDeg)">go to the PCA axis</button>
    </div>
  </div>
</template>

<style scoped>
.snap { border: 1px solid #d8dadd; border-radius: 0.3rem; padding: 0.16rem 0.6rem; font-size: 0.8rem; background: white; cursor: pointer; color: var(--purple); }
.snap:hover { border-color: var(--purple); }
</style>
