<!-- psi_and_weights: the influence ψ = ρ̇ and the weight ω = ρ̇/e of least
     squares (unbounded), Huber (bounded) and Tukey (redescending). -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { psiHuber, psiTukey, wHuber, wTukey } from '../lib/reg'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const dh = ref(1.5)
const dt = ref(4)
const curves = computed(() => [
  { name: 'least squares', color: MUTED, psi: (e: number) => e, w: (_: number) => 1, dash: '6,4' },
  { name: `Huber, δ = ${dh.value.toFixed(2)}`, color: BLUE, psi: (e: number) => psiHuber(e, dh.value), w: (e: number) => wHuber(e, dh.value), dash: '' },
  { name: `Tukey, δ = ${dt.value.toFixed(2)}`, color: RED, psi: (e: number) => psiTukey(e, dt.value), w: (e: number) => wTukey(e, dt.value), dash: '' },
])
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <LineChart :series="curves.map((c) => ({ points: curve(c.psi, -8, 8, 601), color: c.color, width: 2.6, dash: c.dash }))" :hlines="[{ y: 0 }]"
        :labels="[{ x: -1.2, y: 4.4, text: 'unbounded', color: MUTED, size: 12, anchor: 'end' }, { x: 6.6, y: dh + 0.4, text: 'bounded', color: BLUE, size: 12, anchor: 'middle' }, { x: dt + 1.6, y: -0.6, text: 'redescending', color: RED, size: 12, anchor: 'middle' }]"
        :x-domain="[-8, 8]" :y-domain="[-5, 5]" :x-ticks="[-8, -4, 0, 4, 8]" :y-ticks="[-4, 0, 4]" x-label="residual e" title="influence ψ(e) = ρ̇(e): residual pull strength" />
      <LineChart :series="curves.map((c) => ({ points: curve(c.w, -8, 8, 601), color: c.color, width: 2.6, dash: c.dash }))"
        :labels="curves.map((c, i) => ({ x: 3.6, y: 1.18 - 0.12 * i, text: c.name, color: c.color, size: 12 }))"
        :x-domain="[-8, 8]" :y-domain="[-0.05, 1.25]" :x-ticks="[-8, -4, 0, 4, 8]" :y-ticks="[0, 0.5, 1]" x-label="residual e" title="weight ω(e) = ρ̇(e)/e" :title-color="GREEN" />
    </div>
    <div class="foot">point i pushes the fit through the term ψ(eᵢ) xᵢ′</div>
    <div class="controls">
      <Knob v-model="dh" :min="0.2" :max="5" :step="0.01" label="Huber δ" :color="BLUE" />
      <Knob v-model="dt" :min="1" :max="8" :step="0.01" label="Tukey δ" :color="RED" />
    </div>
  </div>
</template>
