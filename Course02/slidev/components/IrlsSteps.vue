<!-- irls_steps: the IRLS loop on the outlier data, one pass at a time: the
     residuals give weights, the weights give a weighted least squares line. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { fmt, irls, outlierBase, wHuber, wTukey } from '../lib/reg'
import { lineSeg } from '../lib/draw'
import { BLUE, GREEN, GRID, INK, MUTED, RED } from '../lib/theme'

const base = outlierBase(7)
const X = [...base.x, 2.35, -2.2]
const far = ref(1)
const Y = computed(() => [...base.y, -5.4 * far.value, 5.0 * far.value])
const k = ref(0)
const kind = ref('huber')
const hist = computed(() => irls(X, Y.value, kind.value === 'huber' ? (e) => wHuber(e, 1.345) : (e) => wTukey(e, 4.685), 12))
const st = computed(() => hist.value[k.value])
const ghosts = computed(() => hist.value.slice(0, k.value).map((h) => lineSeg(h.beta, -3.5, 3.5, GRID, 1.2)))
const traj = computed(() => hist.value.map((h, i) => [i, h.beta[1]] as [number, number]))
const lo = computed(() => Math.min(...traj.value.map((p) => p[1]), 1.1) - 0.05)
const hi = computed(() => Math.max(...traj.value.map((p) => p[1]), 1.1) + 0.05)
const col = computed(() => (kind.value === 'huber' ? BLUE : RED))
</script>

<template>
  <div class="cmp">
    <div class="r2" style="grid-template-columns: 1.6fr 1fr">
      <Plane :X="X.map((v, i) => [v, Y[i]])" :colors="BLUE" :sizes="st.w.map((v) => 2.5 + 5.5 * v)" :alphas="st.w.map((v) => 0.2 + 0.75 * v)"
        :domain="[-3.5, 3.5, -8, 8]" :equal="false" :segments="[...ghosts, lineSeg(st.beta, -3.5, 3.5, k === 12 ? GREEN : INK, 2.6)]"
        :title="k === 0 ? 'k = 0: least squares, every weight 1' : `k = ${k}: weights from the residuals of step ${k - 1}`" />
      <LineChart :series="[{ points: traj, color: col, width: 2.2 }]" :dots="[...traj.map(([i, v]) => ({ x: i, y: v, color: i === k ? col : MUTED, r: i === k ? 6 : 3 }))]"
        :hlines="[{ y: 1.1, color: INK, dash: '6,4' }]" :x-domain="[-0.3, 12.3]" :y-domain="[lo, hi]" :x-ticks="[0, 2, 4, 6, 8, 10, 12]" :y-ticks="[]"
        x-label="iteration k" y-label="β̂₁" title="the slope, pass after pass (dashed: truth)" />
    </div>
    <div class="foot">β̂₁ = <b :style="{ color: col }">{{ fmt(st.beta[1], 3) }}</b>; weights of the two far points: {{ fmt(st.w[26]) }} and {{ fmt(st.w[27]) }}. Pale and small points have smaller weights; grey lines are the earlier passes.</div>
    <div class="controls">
      <Knob v-model="k" :min="0" :max="12" :step="1" :digits="0" label="iteration k" :color="col" />
      <Choice v-model="kind" :options="[{ value: 'huber', label: 'Huber δ = 1.345', color: BLUE }, { value: 'tukey', label: 'Tukey δ = 4.685', color: RED }]" />
      <Knob v-model="far" :min="0" :max="1.6" :step="0.01" label="how far the outliers are" :color="RED" />
    </div>
  </div>
</template>
