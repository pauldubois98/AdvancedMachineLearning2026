<!-- loss_shapes: the cost of predicting y when the data is x, for the three
     losses; and what happens to that cost when x and y are scaled together. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { dIS, dKL, dQuad, range } from '../lib/losses'
import { BLUE, GOLD, GREEN, INK } from '../lib/theme'

const x = ref(1)
const y = ref(2)
const L = [
  { name: 'quadratic', color: BLUE, f: dQuad },
  { name: 'KL', color: GREEN, f: dKL },
  { name: 'Itakura–Saito', color: GOLD, f: dIS },
]
const ys = range(0.02, 3.2, 200)
const lams = range(0.3, 3, 120)
const left = computed(() => L.map((l) => ({ points: ys.map((v) => [v, l.f(x.value, v)] as [number, number]), color: l.color, width: 2.2 })))
const right = computed(() => L.map((l) => ({
  points: lams.map((s) => [s, l.f(s * x.value, s * y.value) / (l.f(x.value, y.value) || 1e-12)] as [number, number]),
  color: l.color, width: 2.2, dash: l.name === 'Itakura–Saito' ? '6 3' : undefined,
})))
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        :series="left" :vlines="[{ x: x, color: '#9aa0a6', dash: '4 3' }]" :dots="L.map((l) => ({ x: y, y: l.f(x, y), color: l.color, r: 4 }))"
        :labels="L.map((l, k) => ({ x: 3.15, y: 2.35 - 0.25 * k, text: l.name, color: l.color, size: 13, anchor: 'end' }))"
        :x-domain="[0, 3.2]" :y-domain="[0, 2.6]" x-label="y = [WH]ᵢⱼ" :x-ticks="[0, 0.5, 1, 1.5, 2, 2.5, 3]" :y-ticks="[0, 0.5, 1, 1.5, 2, 2.5]"
        :title="`Cost of predicting y when the data is x = ${x.toFixed(2)}`"
      />
      <LineChart
        :series="right" :hlines="[{ y: 1, color: '#cccfd2', dash: '3 3' }]"
        :x-domain="[0.3, 3]" :y-domain="[0, 3.2]" x-label="λ" y-label="d(λx, λy) / d(x, y)" :x-ticks="[0.5, 1, 1.5, 2, 2.5, 3]" :y-ticks="[0, 1, 2, 3]"
        :title="`Scaled by λ, at x = ${x.toFixed(2)}, y = ${y.toFixed(2)}`"
      />
    </div>
    <div class="caps"><span>too small costs much more than too big (except for the square)</span><span>only Itakura–Saito does not care about volume</span></div>
    <div class="controls">
      <Knob v-model="x" :min="0.2" :max="2.5" :step="0.05" label="data x" :color="INK" />
      <Knob v-model="y" :min="0.1" :max="3" :step="0.05" label="model y (dots, and right panel)" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; min-height: 0; }
.caps { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; text-align: center; color: #9aa0a6; font-size: 0.8rem; }
</style>
