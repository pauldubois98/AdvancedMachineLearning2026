<!-- degeneracy: one component sits on a single point and shrinks. The
     log-likelihood grows like log(1/sigma), without bound. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace, loglik1, mixPdf1 } from '../lib/gmm'
import { Rng } from '../lib/rng'
import { curve, fmt } from '../lib/charts'
import { INK, MUTED, RED } from '../lib/theme'

const rng = new Rng(7)
const x = [...Array.from({ length: 60 }, () => rng.normal(-1.6, 0.7)), ...Array.from({ length: 60 }, () => rng.normal(1.7, 0.8))]
const spike = Math.max(...x)
const mean = x.reduce((a, b) => a + b, 0) / x.length
const logS = ref(Math.log10(0.3))
const s2 = computed(() => 10 ** logS.value)
const m = computed(() => ({ p: [0.95, 0.05], mu: [mean, spike], sd: [1.7, s2.value] }))
const grid = computed(() => {
  // dense near the spike, so the needle is drawn as it is
  const g = linspace(-4.5, 4.5, 600)
  const fine = linspace(spike - 6 * s2.value, spike + 6 * s2.value, 200)
  return [...g, ...fine].sort((a, b) => a - b)
})
const ll = computed(() => loglik1(x, m.value))
const trace = computed(() => linspace(-3, Math.log10(1.5), 60).map((ls) => [ls, loglik1(x, { p: [0.95, 0.05], mu: [mean, spike], sd: [1.7, 10 ** ls] })] as [number, number]))
const yr = computed(() => [Math.min(...trace.value.map((p) => p[1])) - 5, Math.max(...trace.value.map((p) => p[1])) + 5] as [number, number])
</script>

<template>
  <div class="wrap">
    <div class="note top">Put one component on a single point and the likelihood climbs without end</div>
    <div class="body">
      <LineChart
        :series="[{ points: curve(grid, (v) => Math.min(mixPdf1(v, m), 0.42)), color: INK, width: 2 }]"
        :dots="x.map((v) => ({ x: v, y: -0.02, color: MUTED, r: 1.6 }))"
        :x-domain="[-4.5, 4.5]" :y-domain="[-0.05, 0.42]" :x-ticks="[]" :y-ticks="[]"
        :title="`σ₂ = ${s2 < 0.01 ? s2.toExponential(1) : s2.toFixed(3)}: ℓ = ${fmt(ll)}`" :title-color="RED"
      />
      <LineChart
        :series="[{ points: trace, color: RED, width: 2.2 }]"
        :dots="[{ x: logS, y: ll, color: RED, r: 5 }]"
        :x-domain="[-3, Math.log10(1.5)]" :y-domain="yr" x-label="log₁₀ σ₂" y-label="ℓ_obs"
        :x-ticks="[-3, -2, -1, 0]" :y-ticks="[]" title="the log-likelihood as σ₂ shrinks"
      />
      <div class="side">
        <div class="h" :style="{ color: RED }">Growing likelihood, unbounded</div>
        <p>— set μ<sub>k</sub> = x<sub>i</sub>, let σ<sub>k</sub> → 0</p>
        <p>— ℓ<sub>obs</sub> then grows like log(1/σ<sub>k</sub>), without any bound</p>
        <p>— the global maximum is a useless spike sitting on one point</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="logS" :min="-3" :max="Math.log10(1.5)" :step="0.01" :label="'log₁₀ σ₂'" :digits="2" :color="RED" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.3fr 1fr 1fr; gap: 1.5rem; min-height: 0; }
.side { align-self: center; }
</style>
