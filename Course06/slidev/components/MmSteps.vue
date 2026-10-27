<!-- mm_picture: repeat: touch, climb, touch again. A staircase that never
     descends; each dashed curve is F(., q^t), one per pass. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace } from '../lib/gmm'
import { curve } from '../lib/charts'
import { argmaxG, G, L, T_HI, T_LO } from '../lib/toy'
import { BLUE, GOLD, GREEN, INK, PURPLE, RED } from '../lib/theme'

const steps = ref(3)
const t0 = ref(-0.75)
const t = linspace(T_LO, T_HI, 400)
const COL = [BLUE, GOLD, GREEN, PURPLE, RED]
const path = computed(() => {
  const out = [t0.value]
  for (let s = 0; s < steps.value; s++) out.push(argmaxG(out[out.length - 1]))
  return out
})
const surrogates = computed(() => path.value.slice(0, -1).map((tb, s) => ({
  points: curve(t.filter((v) => Math.abs(v - tb) < 0.85), (v) => G(v, tb)), color: COL[s % 5], width: 1.7, dash: '6 4',
})))
const arrows = computed(() => path.value.slice(0, -1).map((tb, s) => ({
  points: [[tb, L(tb)], [path.value[s + 1], G(path.value[s + 1], tb)]] as [number, number][], color: COL[s % 5], width: 2,
})))
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[{ points: curve(t, L), color: INK, width: 2.6 }, ...surrogates, ...arrows]"
        :dots="path.map((v, s) => ({ x: v, y: L(v), color: s ? COL[(s - 1) % 5] : INK, r: 5.5 }))"
        :labels="[{ x: 2.5, y: L(2.5) + 0.12, text: 'ℓ_obs', color: INK, size: 14 }]"
        :x-domain="[T_LO, T_HI]" :y-domain="[-2.5, 0.6]" x-label="θ" :x-ticks="[]" :y-ticks="[]"
      />
      <div class="side">
        <div class="h">Minorize, then maximize</div>
        <div class="h" :style="{ color: BLUE }">Minorize</div>
        <p>build F(θ, qᵗ) ≤ ℓ<sub>obs</sub>(θ), touching at θᵗ (the E-step)</p>
        <div class="h" :style="{ color: GREEN }">Maximize</div>
        <p>θᵗ⁺¹ = argmax<sub>θ</sub> F(θ, qᵗ), then start again (the M-step)</p>
        <Readout :items="path.map((v, s) => ({ label: `ℓ(θ<sub>${s}</sub>)`, value: L(v).toFixed(3) }))" />
      </div>
    </div>
    <div class="controls">
      <Knob v-model="steps" :min="0" :max="10" :step="1" label="passes" :digits="0" :color="INK" />
      <Knob v-model="t0" :min="-0.85" :max="2.9" :step="0.01" label="start θ₀" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
</style>
