<!-- aic_vs_bic: the penalty per parameter (left) and the two criteria at work
     (right): polynomial orders fitted to N noisy sine points, a Gaussian
     likelihood with the variance fitted too (M + 2 parameters), each
     criterion in its minimise form. 10-fold CV is shown for reference. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmin, cvPoly, mse, polyFit, sinData } from '../lib/c08'
import { GOLD, GREEN, INK, PURPLE } from '../lib/theme'

const N = ref(1000)
const seed = ref(1)
const MS = Array.from({ length: 10 }, (_, m) => m)
const NN = Array.from({ length: 60 }, (_, i) => 10 ** (1 + (3 * i) / 59))
const crit = computed(() => {
  const s = sinData(Math.round(N.value), seed.value)
  const n = s.x.length
  return MS.map((m) => {
    const rss = mse(polyFit(s.x, s.t, m), s)
    const ll = -0.5 * n * (Math.log(2 * Math.PI * rss) + 1)
    const k = m + 2
    return { m, aic: -2 * ll + 2 * k, bic: -2 * ll + k * Math.log(n), cv: n <= 400 ? cvPoly(s, m, 10, seed.value) : NaN }
  })
})
const rel = (key: 'aic' | 'bic') => {
  const v = crit.value.map((c) => c[key])
  const lo = Math.min(...v)
  return v.map((x) => x - lo)
}
const aicM = computed(() => argmin(crit.value.map((c) => c.aic)))
const bicM = computed(() => argmin(crit.value.map((c) => c.bic)))
const cvM = computed(() => (Number.isNaN(crit.value[0].cv) ? null : argmin(crit.value.map((c) => c.cv))))
const YMAX = 40
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[
          { points: NN.map((n) => [n, 1] as [number, number]), color: GOLD, width: 3 },
          { points: NN.map((n) => [n, 0.5 * Math.log(n)] as [number, number]), color: GREEN, width: 3 },
        ]"
        :dots="[{ x: N, y: 1, color: GOLD, r: 6 }, { x: N, y: 0.5 * Math.log(N), color: GREEN, r: 6 }]"
        :vlines="[{ x: N, color: INK, dash: '' }]"
        :labels="[{ x: 13, y: 4.5, text: 'AIC: 1', color: GOLD, size: 13 }, { x: 13, y: 4.1, text: 'BIC: ½ log N', color: GREEN, size: 13 }]"
        log-x :x-domain="[10, 1e4]" :y-domain="[0.5, 5]" :x-ticks="[10, 100, 1000, 10000]" :y-ticks="[1, 2, 3, 4]"
        x-label="N" y-label="penalty per parameter" :title="`At N = ${Math.round(N)}: AIC pays 1 per parameter, BIC pays ${(0.5 * Math.log(N)).toFixed(1)}`"
      />
      <LineChart
        :series="[
          { points: MS.map((m) => [m, Math.min(rel('aic')[m], YMAX * 1.5)] as [number, number]), color: GOLD, width: 2.6 },
          { points: MS.map((m) => [m, Math.min(rel('bic')[m], YMAX * 1.5)] as [number, number]), color: GREEN, width: 2.6 },
        ]"
        :dots="[{ x: aicM, y: 0, color: GOLD, r: 10, hollow: true }, { x: bicM, y: 0, color: GREEN, r: 7 }]"
        :labels="[{ x: 5, y: YMAX * 0.9, text: `AIC picks M = ${aicM}`, color: GOLD, size: 13 }, { x: 5, y: YMAX * 0.8, text: `BIC picks M = ${bicM}`, color: GREEN, size: 13 },
                  ...(cvM !== null ? [{ x: 5, y: YMAX * 0.7, text: `10-fold CV picks M = ${cvM}`, color: PURPLE, size: 13 }] : [])]"
        :x-domain="[-0.3, 9.3]" :y-domain="[0, YMAX]" :x-ticks="[0, 3, 6, 9]" :y-ticks="[0, 10, 20, 30, 40]"
        x-label="polynomial order M" y-label="criterion − its minimum" :title="`orders fitted to ${Math.round(N)} sine points`"
      />
    </div>
    <div class="note msg">BIC charges ½ log N per parameter, so it is stricter as data accumulates; on a large sample it keeps fewer parameters.</div>
    <div class="controls">
      <Knob v-model="N" :min="10" :max="10000" log label="sample size N" />
      <Knob v-model="seed" :min="1" :max="30" :step="1" :digits="0" label="sample" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; min-height: 0; }
.msg { text-align: center; }
</style>
