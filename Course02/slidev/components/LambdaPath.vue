<!-- lambda_path: every coefficient as a function of λ. Ridge shrinks them all
     and none reaches 0; the lasso drops them one by one. Dark lines: the 3
     features that carry information. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { fmt, lasso, ridge, sparseDesign } from '../lib/reg'
import { logTicks } from '../lib/ticks'
import { BLUE, GREEN, INK, MUTED } from '../lib/theme'

const noise = ref(1.5)
const seed = ref(41)
const lr = ref(10)
const ll = ref(0.3)
const D = computed(() => sparseDesign(new Rng(seed.value), 60, 10, 3, noise.value))
const logspace = (a: number, b: number, n: number) => Array.from({ length: n }, (_, i) => 10 ** (a + ((b - a) * i) / (n - 1)))
const RL = logspace(-2, 3, 80)
const ridgePath = computed(() => RL.map((l) => ridge(D.value.X, D.value.y, l)))
const lmax = computed(() => Math.max(...D.value.X[0].map((_, k) => Math.abs(D.value.X.reduce((s, r, i) => s + r[k] * D.value.y[i], 0)) / 60)))
const LL = computed(() => logspace(Math.log10(lmax.value) - 3, Math.log10(lmax.value) + 0.2, 80))
const lassoPath = computed(() => {
  const out: number[][] = new Array(80)
  let b: number[] | undefined
  for (let i = 79; i >= 0; i--) { b = lasso(D.value.X, D.value.y, LL.value[i], b); out[i] = b }
  return out
})
const series = (lams: number[], path: number[][]) => D.value.beta.map((bt, j) => ({
  points: lams.map((l, i) => [l, path[i][j]] as [number, number]),
  color: bt ? INK : MUTED, width: 1.8, opacity: bt ? 1 : 0.5,
}))
const atR = computed(() => ridge(D.value.X, D.value.y, lr.value))
const atL = computed(() => lasso(D.value.X, D.value.y, ll.value))
const nz = computed(() => atL.value.filter((v) => Math.abs(v) > 1e-8).length)
const yr = computed(() => { const m = Math.max(...D.value.beta.map(Math.abs)) + 0.8; return [-m, m] as [number, number] })
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <LineChart :series="series(RL, ridgePath)" :vlines="[{ x: lr, color: BLUE, dash: '5,3' }]" :hlines="[{ y: 0 }]"
        :dots="atR.map((v) => ({ x: lr, y: v, color: BLUE, r: 3.5 }))" logX :x-domain="[0.01, 1000]" :y-domain="yr"
        :x-ticks="[0.01, 0.1, 1, 10, 100, 1000]" :y-ticks="[-2, 0, 2]" x-label="λ" y-label="β̂ⱼ" title="ridge" :title-color="BLUE" />
      <LineChart :series="series(LL, lassoPath)" :vlines="[{ x: ll, color: GREEN, dash: '5,3' }]" :hlines="[{ y: 0 }]"
        :dots="atL.map((v) => ({ x: ll, y: v, color: GREEN, r: 3.5 }))" logX :x-domain="[LL[0], LL[79]]" :y-domain="yr"
        :x-ticks="logTicks(LL[0], LL[79])" :y-ticks="[-2, 0, 2]" x-label="λ" title="lasso" :title-color="GREEN" />
    </div>
    <div class="foot">ridge at λ = {{ fmt(lr, 2) }}: everything shrinks, nothing ever reaches zero (smallest |β̂ⱼ| = {{ fmt(Math.min(...atR.map(Math.abs)), 3) }}). Lasso at λ = {{ fmt(ll, 3) }}: <b :style="{ color: GREEN }">{{ nz }} of 10</b> coefficients non-zero; they hit zero one by one. Dark lines: features actually carrying information.</div>
    <div class="controls">
      <Knob v-model="lr" :min="0.01" :max="1000" log label="ridge λ" :color="BLUE" />
      <Knob v-model="ll" :min="LL[0]" :max="LL[79]" log label="lasso λ" :color="GREEN" />
      <Knob v-model="noise" :min="0.2" :max="4" :step="0.05" label="noise σ" :color="MUTED" />
      <Knob v-model="seed" :min="1" :max="60" :step="1" :digits="0" label="new sample" :color="INK" />
    </div>
  </div>
</template>
