<!-- forest_correlation: rho is not a metaphor. Measured on the same sweep as
     the previous slide, against the strength of a single tree. -->
<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import { MF_KS, MfPoint, mfSweep } from '../lib/sweeps'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const k = ref(5)
const points = ref<MfPoint[]>([])
const stop = mfSweep((p) => (points.value = p))
onBeforeUnmount(stop)

const nearestK = computed(() =>
  MF_KS.reduce((a, b) => (Math.abs(b - k.value) < Math.abs(a - k.value) ? b : a)),
)
const at = computed(() => points.value.find((p) => p.k === nearestK.value) ?? null)
const rhoCurve = computed(() => points.value.map((p) => [p.k, p.rho] as [number, number]))
const soloCurve = computed(() => points.value.map((p) => [p.k, p.solo] as [number, number]))
const tradeoff = computed(() => points.value.map((p) => [p.rho, p.err] as [number, number]))
const errDomain = computed<[number, number]>(() => {
  if (!points.value.length) return [0, 0.15]
  const es = points.value.map((p) => p.err)
  const lo = Math.min(...es)
  const hi = Math.max(...es)
  const pad = Math.max(0.004, (hi - lo) * 0.5)
  return [Math.max(0, lo - pad), hi + pad * 1.4]
})
const rhoDomain = computed<[number, number]>(() => {
  if (!points.value.length) return [0, 1]
  const rs = points.value.map((p) => p.rho)
  return [Math.min(...rs) - 0.04, Math.max(...rs) + 0.04]
})
const best = computed(() =>
  points.value.length ? points.value.reduce((a, b) => (b.err < a.err ? b : a)) : null,
)
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        :series="[
          { points: rhoCurve, color: RED, width: 2.6 },
          { points: soloCurve, color: BLUE, width: 2.2, dash: '5,4' },
        ]"
        :vlines="[{ x: nearestK, color: MUTED, dash: '' }]"
        :x-domain="[0, 26]" :y-domain="[0, 0.8]"
        :x-ticks="[1, 5, 10, 15, 20, 25]" :y-ticks="[0, 0.25, 0.5, 0.75]"
        x-label="max_features, out of 25"
        title="the two effects pull apart"
        :labels="[
          { x: 1, y: 0.77, text: 'ρ, how alike the trees are', color: RED, size: 11.5 },
          { x: 1, y: 0.71, text: 'error of ONE tree', color: BLUE, size: 11.5 },
        ]"
      />
      <LineChart
        :series="[{ points: tradeoff, color: MUTED, width: 1.4 }]"
        :dots="[
          ...points.map((p) => ({ x: p.rho, y: p.err, color: GREEN, r: 5 })),
          ...(best ? [{ x: best.rho, y: best.err, color: RED, r: 7, hollow: true }] : []),
          ...(at ? [{ x: at.rho, y: at.err, color: '#1b1b1b', r: 4 }] : []),
        ]"
        :labels="points.map((p) => ({ x: p.rho, y: p.err + (errDomain[1] - errDomain[0]) * 0.07, text: String(p.k), color: '#1b1b1b', size: 10, anchor: 'middle' }))"
        :x-domain="rhoDomain" :y-domain="errDomain"
        :x-ticks="[Number(rhoDomain[0].toFixed(2)), Number(((rhoDomain[0] + rhoDomain[1]) / 2).toFixed(2)), Number(rhoDomain[1].toFixed(2))]"
        :y-ticks="[Number(errDomain[0].toFixed(3)), Number(errDomain[1].toFixed(3))]"
        x-label="ρ   (labels: max_features)" y-label="test error of the forest"
        title="the best forest is not the most diverse"
      />
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="k" :min="1" :max="25" :step="1" label="max_features" :digits="0" />
        <Readout
          v-if="at"
          :items="[
            { label: 'ρ', value: at.rho.toFixed(3), color: RED },
            { label: 'one tree', value: (at.solo * 100).toFixed(1) + '%', color: BLUE },
            { label: 'the forest', value: (at.err * 100).toFixed(1) + '%', color: GREEN },
          ]"
        />
      </div>
      <p class="note">
        more columns allowed: stronger trees, and more alike. Too diverse or too
        alike both lose, and the winner sits in between.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child { min-width: 12rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
