<!-- mle_idea: the data is fixed, the model slides over it; read the
     log-likelihood as a function of μ and take its argmax, where the slope is 0. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve } from '../lib/hist'
import { mean, normals, npdf } from '../lib/stats'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const mu = ref(0.4)
const seed = ref(11)
const x = computed(() => normals(new Rng(seed.value), 12, 1.8, 1))
const ll = (m: number) => x.value.reduce((s, v) => s - 0.5 * (v - m) ** 2, 0)
const slope = (m: number) => x.value.reduce((s, v) => s + (v - m), 0)
const xbar = computed(() => mean(x.value))
const llc = computed(() => curve(ll, -1, 4.6))
const lo = computed(() => Math.min(...llc.value.map((p) => p[1])))
const hi = computed(() => ll(xbar.value))
const tangent = computed(() => {
  const m = mu.value, y = ll(m), s = slope(m)
  return [[m - 0.9, y - 0.9 * s], [m + 0.9, y + 0.9 * s]] as [number, number][]
})
const at = computed(() => Math.abs(mu.value - xbar.value) < 0.04)
const col = computed(() => (at.value ? GREEN : RED))
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 12 points (blue ticks) from N(1.8, 1). The model N(μ, 1) slides over them: each position μ gets a log-likelihood ℓ(μ) = −½ Σ (xᵢ − μ)² + const.</div>
    <div class="r3">
      <LineChart :series="[{ points: curve((t) => npdf(t, mu, 1), -2.5, 6), color: col }]" :x-domain="[-2.5, 6]" :y-domain="[-0.03, 0.45]" :x-ticks="[-2, 0, 2, 4, 6]" :y-ticks="[]" x-label="x"
        :dots="x.map((v) => ({ x: v, y: -0.012, color: BLUE, r: 3 }))" title="1. the data is fixed" />
      <LineChart :series="[{ points: llc, color: GREEN }, { points: tangent, color: col, width: 1.6, dash: '5,3' }]" :x-domain="[-1, 4.6]" :y-domain="[lo, hi + (hi - lo) * 0.08]" :x-ticks="[0, 2, 4]" :y-ticks="[]" x-label="μ" y-label="ℓ(x; μ)"
        :dots="[{ x: mu, y: ll(mu), color: col, r: 6 }]" title="2. ℓ as a function of μ, and its slope" />
      <LineChart :series="[{ points: curve(slope, -1, 4.6), color: INK }]" :x-domain="[-1, 4.6]" :y-domain="[slope(4.6), slope(-1)]" :x-ticks="[0, 2, 4]" :y-ticks="[]" x-label="μ" y-label="ℓ′(μ)"
        :hlines="[{ y: 0, color: MUTED }]" :vlines="[{ x: xbar, color: GREEN, dash: '4,3' }]" :dots="[{ x: mu, y: slope(mu), color: col, r: 6 }]" title="3. take the argmax: ℓ′ = 0" />
    </div>
    <div class="foot">slope ℓ′(μ) = Σ (xᵢ − μ) = <b :style="{ color: col }">{{ slope(mu).toFixed(2) }}</b>; it is zero at μ̂ = x̄ = <b :style="{ color: GREEN }">{{ xbar.toFixed(2) }}</b>, and ℓ″ = −n &lt; 0 there, so that point is the maximum.</div>
    <div class="controls">
      <Knob v-model="mu" :min="-1" :max="4.6" :step="0.01" label="model μ" :color="col" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" :digits="0" label="new sample" :color="BLUE" />
    </div>
  </div>
</template>
