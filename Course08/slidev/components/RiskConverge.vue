<!-- eq_empirical_risk: R_N(f) is an average over N points. For a model fixed
     in advance (the printed deck's order-M fit) it converges to R(f) as N
     grows, whichever sample is drawn. For f-hat fitted on the same N points
     it sits below: the training error is optimistic. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { freshSin, mean, mse, polyFit, sinData } from '../lib/c08'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const M = ref(3)
const showFit = ref(true)
const base = sinData(10, 0)
const f = computed(() => polyFit(base.x, base.t, M.value))
const R = computed(() => mse(f.value, freshSin(20000, 4242)))
const NS = [5, 7, 10, 15, 20, 30, 50, 70, 100, 150, 200, 300, 500, 700, 1000, 2000]
const STREAMS = 6
const streams = computed(() => Array.from({ length: STREAMS }, (_, s) => {
  const d = freshSin(2000, 300 + s)
  const out: [number, number][] = []
  let acc = 0, j = 0
  for (const n of NS) {
    for (; j < n; j++) acc += (f.value.reduce((a, w, k) => a + w * d.x[j] ** k, 0) - d.t[j]) ** 2
    out.push([n, acc / n])
  }
  return out
}))
// f-hat refitted on each N points, scored on those same points
const optimistic = computed(() => NS.filter((n) => n > M.value + 1).map((n) => {
  const errs = Array.from({ length: 20 }, (_, r) => {
    const d = freshSin(n, 9000 + r)
    return mse(polyFit(d.x, d.t, M.value), d)
  })
  return [n, mean(errs)] as [number, number]
}))
const ymax = computed(() => Math.max(0.2, R.value * 2.6))
</script>

<template>
  <div class="live">
    <LineChart
      :series="[
        ...streams.map((p) => ({ points: p, color: BLUE, width: 1.3, opacity: 0.55 })),
        ...(showFit ? [{ points: optimistic, color: RED, width: 2.6 }] : []),
      ]"
      :hlines="[{ y: R, color: GREEN, dash: '6 4' }]"
      :labels="[
        { x: 600, y: R + ymax * 0.05, text: 'R(f)', color: GREEN, size: 14 },
        { x: 6, y: ymax * 0.92, text: 'R_N(f): fresh points, six samples', color: BLUE, size: 12 },
        ...(showFit ? [{ x: 6, y: ymax * 0.82, text: 'R_N(f̂): f̂ fitted on the same N points', color: RED, size: 12 }] : []),
      ]"
      log-x :x-domain="[5, 2000]" :y-domain="[0, ymax]" :x-ticks="[10, 100, 1000]" :y-ticks="[0, ymax / 2, ymax].map((v) => +v.toFixed(2))"
      x-label="N (log scale)" y-label="mean squared error" :unit-height="300"
    />
    <div class="controls">
      <Knob v-model="M" :min="0" :max="9" :step="1" :digits="0" label="order M of f" />
      <Toggle v-model="showFit" label="show the training error of f̂" :color="RED" />
    </div>
  </div>
</template>

<style scoped>
.live { display: grid; grid-template-rows: 1fr auto; gap: 0.3rem; min-height: 0; height: 100%; }
</style>
