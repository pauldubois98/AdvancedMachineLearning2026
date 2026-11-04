<!-- variance: the same unbiased estimator, the sample mean, on small and on
     large samples. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { histBars } from '../lib/hist'
import { pvar } from '../lib/stats'
import { GREEN, INK, RED } from '../lib/theme'

const nA = ref(8)
const nB = ref(1)
const sd = ref(1)
const r = new Rng(5)
const Z = Array.from({ length: 4000 }, () => r.normal())
const Z2 = Array.from({ length: 4000 }, () => r.normal())
const A = computed(() => Z.map((z) => 1 + (sd.value * z) / Math.sqrt(nA.value)))
const B = computed(() => Z2.map((z) => 1 + (sd.value * z) / Math.sqrt(nB.value)))
const ba = computed(() => histBars(A.value, -2.6, 4.6, 90, GREEN, 0.45))
const bb = computed(() => histBars(B.value, -2.6, 4.6, 90, RED, 0.45))
const top = computed(() => Math.max(...ba.value.map((b) => b.y), ...bb.value.map((b) => b.y)) * 1.15)
const ticks = [-2, -1, 0, 1, 2, 3, 4]
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> the same estimator on both sides, the sample mean x̄ of n points from N(θ₀ = 1, σ²), over 4000 samples. It is unbiased on both sides; only n differs.</div>
    <div class="r2">
      <LineChart :series="[]" :bars="ba" :x-domain="[-2.6, 4.6]" :y-domain="[0, top]" :x-ticks="ticks" :y-ticks="[]" x-label="θ̂"
        :vlines="[{ x: 1, color: INK, dash: '' }]" :title="`n = ${nA}: Var(θ̂) = ${pvar(A).toFixed(3)}`" :title-color="GREEN" />
      <LineChart :series="[]" :bars="bb" :x-domain="[-2.6, 4.6]" :y-domain="[0, top]" :x-ticks="ticks" :y-ticks="[]" x-label="θ̂"
        :vlines="[{ x: 1, color: INK, dash: '' }]" :title="`n = ${nB}: Var(θ̂) = ${pvar(B).toFixed(3)}`" :title-color="RED" />
    </div>
    <div class="foot">Var(θ̂) = E[(θ̂ − E[θ̂])²] = σ² / n: how much θ̂ moves from one sample to the next. The black line is θ₀.</div>
    <div class="controls">
      <Knob v-model="nA" :min="1" :max="100" :step="1" :digits="0" label="n, left" :color="GREEN" />
      <Knob v-model="nB" :min="1" :max="100" :step="1" :digits="0" label="n, right" :color="RED" />
      <Knob v-model="sd" :min="0.2" :max="2" :step="0.05" label="noise σ" :color="INK" />
    </div>
  </div>
</template>
