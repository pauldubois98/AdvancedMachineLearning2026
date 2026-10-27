<!-- em_mstep: with gamma frozen, re-fit each component to its weighted share.
     Move theta^t; one M-step later, the right panel. Press "step" to keep
     going: the M-step output becomes the next pass's theta^t. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, em1, linspace, loglik1, weighted1, type Mix1 } from '../lib/gmm'
import { bars, curve, edges, fmt } from '../lib/charts'
import { BLUE, COMP, GOLD, GREEN, MUTED, PURPLE } from '../lib/theme'

const mu1 = ref(88)
const mu2 = ref(91)
const sd = ref(2.2)
const before = computed<Mix1>(() => ({ p: [0.5, 0.5], mu: [mu1.value, mu2.value], sd: [sd.value, sd.value] }))
const after = computed(() => em1(ANIMALS, before.value, 1)[1])
const grid = linspace(80, 99, 400)
const hist = bars(ANIMALS, edges(81.5, 98.5, 1), { density: true })
</script>

<template>
  <div class="wrap">
    <div class="note top" :style="{ color: GREEN }">M-step: with γ frozen, re-fit each component to its weighted share</div>
    <div class="body">
      <div class="col">
        <LineChart
          :series="[0, 1].map((k) => ({ points: curve(grid, (x) => weighted1(x, before)[k]), color: COMP[k], width: 2.2 }))"
          :bars="hist" :x-domain="[80, 99]" :y-domain="[0, 0.17]" x-label="length (mm)" :x-ticks="[82, 86, 90, 94, 98]" :y-ticks="[]"
          title="before: θᵗ" :title-color="MUTED"
        />
        <div class="cap">ℓ = {{ fmt(loglik1(ANIMALS, before)) }}</div>
      </div>
      <div class="col">
        <LineChart
          :series="[0, 1].map((k) => ({ points: curve(grid, (x) => weighted1(x, after)[k]), color: COMP[k], width: 2.2 }))"
          :bars="hist" :x-domain="[80, 99]" :y-domain="[0, 0.17]" x-label="length (mm)" :x-ticks="[82, 86, 90, 94, 98]" :y-ticks="[]"
          title="after: θᵗ⁺¹" :title-color="GREEN"
        />
        <div class="cap">ℓ = <b :style="{ color: GREEN }">{{ fmt(after.ll) }}</b></div>
      </div>
      <div class="side">
        <Tex display formula="{\color{#6b46c1} p_k \leftarrow n_k / n}" />
        <Tex display formula="{\color{#2b6cb0} \mu_k \leftarrow \tfrac{1}{n_k} \textstyle\sum_i \gamma_{ik} x_i}" />
        <Tex display formula="{\color{#b7791f} \sigma_k^2 \leftarrow \tfrac{1}{n_k} \textstyle\sum_i \gamma_{ik} (x_i - \mu_k)^2}" />
        <p class="note">complete-data formulas, with γ<sub>ik</sub> in place of 𝟙<sub>z<sub>i</sub> = k</sub></p>
        <p class="note">θᵗ⁺¹: p = ({{ after.p.map((v) => v.toFixed(2)).join(', ') }}), μ = ({{ after.mu.map((v) => v.toFixed(1)).join(', ') }}), σ = ({{ after.sd.map((v) => v.toFixed(2)).join(', ') }})</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="mu1" :min="82" :max="97" :step="0.1" label="μ₁ᵗ" :digits="1" :color="COMP[0]" />
      <Knob v-model="mu2" :min="82" :max="97" :step="0.1" label="μ₂ᵗ" :digits="1" :color="COMP[1]" />
      <Knob v-model="sd" :min="0.6" :max="5" :step="0.05" label="σᵗ (both)" :color="BLUE" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 1fr 0.95fr; gap: 1.5rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.85rem; }
.side { align-self: center; font-size: 0.85rem; }
</style>
