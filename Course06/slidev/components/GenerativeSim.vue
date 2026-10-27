<!-- generative_sim: coin flip, then a bell. Draw n animals; the colours are
     what the generator knows, the grey histogram is what the experiment
     hands over. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace, mixPdf1, normPdf } from '../lib/gmm'
import { Rng } from '../lib/rng'
import { bars, curve, edges, stacked } from '../lib/charts'
import { COMP, GRID, INK, PURPLE, BLUE } from '../lib/theme'

const p1 = ref(0.45)
const n = ref(300)
const seed = ref(4)
const showColors = ref(true)
const mu = [86.0, 92.2]
const sd = [1.5, 1.6]
const m = computed(() => ({ p: [p1.value, 1 - p1.value], mu, sd }))
const sample = computed(() => {
  const rng = new Rng(seed.value * 7919 + 13)
  const g: number[][] = [[], []]
  for (let i = 0; i < n.value; i++) {
    const k = rng.next() < p1.value ? 0 : 1
    g[k].push(rng.normal(mu[k], sd[k]))
  }
  return g
})
const grid = linspace(79, 100, 300)
const E = edges(79, 100, 1)
const histBars = computed(() => showColors.value
  ? stacked(sample.value, E, COMP, { density: true })
  : bars([...sample.value[0], ...sample.value[1]], E, { density: true, color: GRID, alpha: 0.9 }))
</script>

<template>
  <div class="wrap">
    <div class="note top">Coin flip, then a bell</div>
    <div class="body">
      <LineChart
        :series="[]" :bars="[0, 1].map((k) => ({ x: k, y: m.p[k], w: 0.55, color: COMP[k], alpha: 0.85 }))"
        :x-domain="[-0.6, 1.6]" :y-domain="[0, 1]" :x-ticks="[]" :y-ticks="[0, 0.5, 1]" y-label="pₖ"
        :labels="[{ x: 0, y: -0.07, text: 'Z = 1', anchor: 'middle', size: 12 }, { x: 1, y: -0.07, text: 'Z = 2', anchor: 'middle', size: 12 }]"
        title="1. draw the class" :title-color="PURPLE"
      />
      <LineChart
        :series="[0, 1].map((k) => ({ points: curve(grid, (x) => normPdf(x, mu[k], sd[k])), color: COMP[k], width: 2.2 }))"
        :x-domain="[79, 100]" :y-domain="[0, 0.3]" x-label="length (mm)" :x-ticks="[80, 85, 90, 95, 100]" :y-ticks="[]"
        title="2. draw from the corresponding bell" :title-color="BLUE"
      />
      <LineChart
        :series="[{ points: curve(grid, (x) => mixPdf1(x, m)), color: INK, width: 2.4 }]" :bars="histBars"
        :x-domain="[79, 100]" :y-domain="[0, 0.25]" x-label="length (mm)" :x-ticks="[80, 85, 90, 95, 100]" :y-ticks="[]"
        :title="`3. repeat: ${sample[0].length} + ${sample[1].length} animals`"
      />
    </div>
    <div class="note bottom">The colours are what the generator knows; the experiment hands the grey histogram (colours removed).</div>
    <div class="controls">
      <Knob v-model="p1" :min="0.05" :max="0.95" :step="0.01" label="p₁" :color="PURPLE" />
      <Knob v-model="n" :min="20" :max="2000" :step="10" label="n" :digits="0" :color="INK" />
      <Knob v-model="seed" :min="1" :max="50" :step="1" label="seed" :digits="0" :color="INK" />
      <Toggle v-model="showColors" label="show the generator's colours" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top, .bottom { text-align: center; }
.body { display: grid; grid-template-columns: 0.7fr 1fr 1fr; gap: 1.5rem; min-height: 0; }
</style>
