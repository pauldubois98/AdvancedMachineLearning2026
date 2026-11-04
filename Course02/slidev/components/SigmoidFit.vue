<!-- sigmoid: p = σ(β0 + β1 x). Move the two weights by hand and read the
     log-likelihood, or snap to the maximum likelihood fit. -->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Rng } from '../lib/rng'
import { curve } from '../lib/hist'
import { fmt, logisticIrls, logisticLoss, sigmoid } from '../lib/reg'
import { BLUE, GREEN, GRID, INK, MUTED, RED } from '../lib/theme'

const rng = new Rng(9)
const x = [...Array.from({ length: 40 }, () => rng.normal(-1.3, 1.6)), ...Array.from({ length: 40 }, () => rng.normal(1.3, 1.6))]
const y = [...Array(40).fill(0), ...Array(40).fill(1)] as number[]
const X = x.map((v) => [v])
const mle = logisticIrls(X, y, 12).at(-1)!
const b0 = ref(0)
const b1 = ref(3)
const snap = ref(false)
watch(snap, (v) => { if (v) { b0.value = +mle[0].toFixed(2); b1.value = +mle[1].toFixed(2) } })
watch([b0, b1], () => { if (Math.abs(b0.value - mle[0]) > 0.006 || Math.abs(b1.value - mle[1]) > 0.006) snap.value = false })
const nll = computed(() => logisticLoss(X, y, [b0.value, b1.value]))
const col = computed(() => (snap.value ? GREEN : INK))
const cut = computed(() => (Math.abs(b1.value) > 1e-6 ? -b0.value / b1.value : NaN))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <LineChart :series="[{ points: curve(sigmoid, -6, 6), color: GREEN, width: 2.8 }]" :hlines="[{ y: 0.5, color: GRID, dash: '5,4' }]" :vlines="[{ x: 0, color: INK, dash: '' }]"
        :labels="[{ x: -5.8, y: 0.55, text: 'p = 0.5', color: MUTED, size: 12 }]" :x-domain="[-6, 6]" :y-domain="[0, 1]" :x-ticks="[-6, -3, 0, 3, 6]" :y-ticks="[0, 0.5, 1]"
        x-label="the score β₀ + βᵀx" y-label="Pr(G = 1 | x)" title="p = σ(β₀ + βᵀx) = 1 / (1 + e^−(β₀ + βᵀx)), inverse of the log-odds" :title-color="GREEN" />
      <LineChart :series="[{ points: curve((v) => sigmoid(b0 + b1 * v), -5, 5, 400), color: col, width: 2.8 }]"
        :dots="x.map((v, i) => ({ x: v, y: y[i], color: y[i] ? RED : BLUE, r: 3.5 }))" :vlines="Number.isFinite(cut) ? [{ x: cut, color: col, dash: '5,3' }] : []"
        :x-domain="[-5, 5]" :y-domain="[-0.05, 1.05]" :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[0, 0.5, 1]" x-label="x" y-label="probability / label" title="fitted to data" />
    </div>
    <div class="foot">−log-likelihood Σ log(1 + e^(β₀+β₁xᵢ)) − yᵢ(β₀+β₁xᵢ) = <b :style="{ color: col }">{{ fmt(nll) }}</b>; its minimum is {{ fmt(logisticLoss(X, y, mle)) }} at β̂ = ({{ fmt(mle[0]) }}, {{ fmt(mle[1]) }})</div>
    <div class="controls">
      <Knob v-model="b0" :min="-3" :max="3" :step="0.01" label="β₀" :color="col" />
      <Knob v-model="b1" :min="-1" :max="6" :step="0.01" label="β₁" :color="col" />
      <Toggle v-model="snap" label="maximum likelihood" :color="GREEN" />
    </div>
  </div>
</template>
