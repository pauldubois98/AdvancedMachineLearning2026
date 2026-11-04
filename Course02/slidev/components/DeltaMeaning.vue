<!-- delta_meaning: Huber's δ is the residual size at which a point stops
     counting as ordinary: squared inside, straight outside. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { psiHuber, rhoHuber, wHuber } from '../lib/reg'
import { BLUE, GOLD, GREEN, INK } from '../lib/theme'

const d = ref(1.5)
const panels = computed(() => [
  { color: INK, title: 'the loss ρ(e)', f: (e: number) => rhoHuber(e, d.value), y: [-0.2, 8] as [number, number], remark: 'squared inside, straight outside' },
  { color: BLUE, title: 'the influence ψ(e)', f: (e: number) => psiHuber(e, d.value), y: [-3.3, 3.3] as [number, number], remark: 'a point can never push harder than δ' },
  { color: GREEN, title: 'the weight ω(e)', f: (e: number) => wHuber(e, d.value), y: [0, 1.1] as [number, number], remark: 'full weight inside, δ/|e| outside' },
])
</script>

<template>
  <div class="cmp">
    <div class="r3">
      <div v-for="p in panels" :key="p.title" class="col">
        <LineChart :series="[{ points: curve(p.f, -5, 5, 501), color: p.color, width: 2.8 }]" :bands="[{ x0: -d, x1: d, color: GOLD, alpha: 0.1 }]"
          :vlines="[{ x: -d, color: GOLD, dash: '5,3' }, { x: d, color: GOLD, dash: '5,3' }]" :x-domain="[-5, 5]" :y-domain="p.y" :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[]"
          x-label="residual e" :title="p.title" :title-color="p.color" />
        <div class="note">{{ p.remark }}</div>
      </div>
    </div>
    <div class="foot">δ = <b :style="{ color: GOLD }">{{ d.toFixed(2) }}</b> is the residual size at which a point stops counting as ordinary</div>
    <div class="controls">
      <Knob v-model="d" :min="0.1" :max="4.5" :step="0.01" label="Huber δ" :color="GOLD" />
    </div>
  </div>
</template>

<style scoped>
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; text-align: center; }
</style>
