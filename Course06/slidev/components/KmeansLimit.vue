<!-- eq_kmeans_limit, drawn: equal weights, equal widths sigma. As sigma
     shrinks, the softmax of -distance^2 / 2 sigma^2 turns into an arg min. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace } from '../lib/gmm'
import { curve } from '../lib/charts'
import { COMP, INK, MUTED } from '../lib/theme'

const C = [-2, 0.3, 2.6]
const logS = ref(0)
const s = computed(() => 10 ** logS.value)
function gam(x: number, k: number) {
  const e = C.map((c) => -((x - c) ** 2) / (2 * s.value ** 2))
  const m = Math.max(...e)
  const w = e.map((v) => Math.exp(v - m))
  return w[k] / w.reduce((a, b) => a + b, 0)
}
const grid = linspace(-4, 4.5, 500)
const mids = [(C[0] + C[1]) / 2, (C[1] + C[2]) / 2]
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="C.map((_, k) => ({ points: curve(grid, (x) => gam(x, k)), color: COMP[k], width: 2.4 }))"
      :vlines="mids.map((v) => ({ x: v, color: MUTED, dash: '3 3' }))"
      :dots="C.map((c, k) => ({ x: c, y: -0.04, color: COMP[k], r: 6 }))"
      :x-domain="[-4, 4.5]" :y-domain="[-0.08, 1.04]" x-label="x" y-label="γ_k(x)" :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[0, 0.5, 1]"
      :title="`σ = ${s < 0.1 ? s.toFixed(3) : s.toFixed(2)}: ${s < 0.15 ? 'a hard assignment, nearest centre' : s > 1.5 ? 'very soft' : 'soft'}`" :title-color="INK" :unit-height="240"
    />
    <div class="controls">
      <Knob v-model="logS" :min="-1.5" :max="0.6" :step="0.01" label="log₁₀ σ" :digits="2" :color="INK" />
      <span class="note">dots: the three centres μ<sub>k</sub>; dotted: the k-means boundaries, halfway between centres</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.3rem; height: 100%; min-height: 0; }
</style>
