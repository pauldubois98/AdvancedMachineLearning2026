<!-- em_estep: with theta frozen, every point is split between the components.
     Move the current theta; the split and the soft class sizes follow. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, linspace, resp1, weighted1 } from '../lib/gmm'
import { bars, curve, edges } from '../lib/charts'
import { BLUE, COMP, GOLD, MUTED } from '../lib/theme'

const mu1 = ref(88)
const mu2 = ref(91)
const sd = ref(2.2)
const m = computed(() => ({ p: [0.5, 0.5], mu: [mu1.value, mu2.value], sd: [sd.value, sd.value] }))
const grid = linspace(80, 99, 500)
const hist = bars(ANIMALS, edges(81.5, 98.5, 1), { density: true })
const nk = computed(() => [0, 1].map((k) => ANIMALS.reduce((a, x) => a + resp1(x, m.value)[k], 0)))
</script>

<template>
  <div class="wrap">
    <div class="note top" :style="{ color: BLUE }">E-step: with θ frozen, every point is split between the components</div>
    <div class="body">
      <div class="left">
        <LineChart
          :series="[0, 1].map((k) => ({ points: curve(grid, (x) => weighted1(x, m)[k]), color: COMP[k], width: 2.2 }))"
          :bars="hist" :x-domain="[80, 99]" :y-domain="[0, 0.17]" :x-ticks="[]" :y-ticks="[]"
          title="the current θᵗ" :title-color="MUTED" :unit-height="190"
        />
        <LineChart
          :series="[]" :ribbons="[
            { points: grid.map((x) => [x, 0, resp1(x, m)[0]] as [number, number, number]), color: COMP[0], alpha: 0.75 },
            { points: grid.map((x) => [x, resp1(x, m)[0], 1] as [number, number, number]), color: COMP[1], alpha: 0.75 },
          ]"
          :x-domain="[80, 99]" :y-domain="[0, 1]" x-label="length (mm)" y-label="γ_ik" :x-ticks="[82, 86, 90, 94, 98]" :y-ticks="[0, 1]" :unit-height="190"
        />
      </div>
      <div class="side">
        <div class="h" :style="{ color: BLUE }">Computes</div>
        <Tex display formula="\gamma_{ik} = \dfrac{p_k f_k(x_i)}{\sum_l p_l f_l(x_i)}" />
        <p>an n × K table of weights, each row summing to one</p>
        <p class="big" :style="{ color: GOLD }">soft class sizes: n₁ = {{ nk[0].toFixed(0) }}, n₂ = {{ nk[1].toFixed(0) }}</p>
        <p class="note">No θ has moved yet.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="mu1" :min="82" :max="97" :step="0.1" label="μ₁" :digits="1" :color="COMP[0]" />
      <Knob v-model="mu2" :min="82" :max="97" :step="0.1" label="μ₂" :digits="1" :color="COMP[1]" />
      <Knob v-model="sd" :min="0.6" :max="5" :step="0.05" label="σ (both)" :color="BLUE" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.6fr 1fr; gap: 2rem; min-height: 0; }
.left { display: grid; grid-template-rows: 1.2fr 1fr; gap: 0.2rem; min-height: 0; }
.side { align-self: center; }
.big { margin: 0.6rem 0; }
</style>
