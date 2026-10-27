<!-- em_run: thirty passes on the animal lengths, from a start you choose. The
     slider walks through the passes. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, em1, linspace, weighted1 } from '../lib/gmm'
import { bars, curve, edges, fmt } from '../lib/charts'
import { BLUE, COMP, GREEN, INK, MUTED } from '../lib/theme'

const mu1 = ref(87.5)
const mu2 = ref(90.5)
const t = ref(0)
const T = 30
const hist = computed(() => em1(ANIMALS, { p: [0.5, 0.5], mu: [mu1.value, mu2.value], sd: [3, 3] }, T))
const cur = computed(() => hist.value[t.value])
const grid = linspace(80, 99, 400)
const H = bars(ANIMALS, edges(81.5, 98.5, 1), { density: true })
const lls = computed(() => hist.value.map((h, i) => [i, h.ll] as [number, number]))
const yr = computed(() => [Math.min(...lls.value.map((p) => p[1])) - 5, Math.max(...lls.value.map((p) => p[1])) + 5] as [number, number])
</script>

<template>
  <div class="wrap">
    <div class="note top">Thirty passes on the animal lengths, from a deliberately bad start</div>
    <div class="body">
      <LineChart
        :series="[0, 1].map((k) => ({ points: curve(grid, (x) => weighted1(x, cur)[k]), color: COMP[k], width: 2.4 }))"
        :bars="H" :x-domain="[80, 99]" :y-domain="[0, 0.16]" x-label="length (mm)" :x-ticks="[82, 86, 90, 94, 98]" :y-ticks="[]"
        :title="`t = ${t}: ℓ = ${fmt(cur.ll)}`" :title-color="t ? INK : MUTED"
      />
      <div class="right">
        <LineChart
          :series="[{ points: lls, color: GREEN, width: 2.2 }]" :dots="[{ x: t, y: cur.ll, color: GREEN, r: 5 }]"
          :x-domain="[0, T]" :y-domain="yr" x-label="pass t" y-label="ℓ_obs" :x-ticks="[0, 10, 20, 30]" :y-ticks="[]"
          title="the log-likelihood, pass by pass" :unit-height="260"
        />
        <p class="note">p = ({{ cur.p.map((v) => v.toFixed(2)).join(', ') }}), μ = ({{ cur.mu.map((v) => v.toFixed(1)).join(', ') }}), σ = ({{ cur.sd.map((v) => v.toFixed(1)).join(', ') }})<span v-if="t === T">: the two regions, recovered without a single label.</span></p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="t" :min="0" :max="T" :step="1" label="pass t" :digits="0" :color="GREEN" />
      <Knob v-model="mu1" :min="82" :max="97" :step="0.1" label="start μ₁" :digits="1" :color="COMP[0]" />
      <Knob v-model="mu2" :min="82" :max="97" :step="0.1" label="start μ₂" :digits="1" :color="COMP[1]" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
</style>
