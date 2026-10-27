<!-- density_vs_clustering: a fitted mixture is two things at once. Slide a
     point along the axis: read its density on the left, its label
     probabilities on the right. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, ANIMAL_FIT, linspace, mixPdf1, resp1 } from '../lib/gmm'
import { bars, curve, edges } from '../lib/charts'
import { COMP, INK, PURPLE, MUTED } from '../lib/theme'

const x0 = ref(88.5)
const grid = linspace(79, 101, 300)
const hist = bars(ANIMALS, edges(81.5, 98.5, 1), { density: true })
const g = computed(() => resp1(x0.value, ANIMAL_FIT))
</script>

<template>
  <div class="wrap">
    <div class="body">
      <div class="col">
        <LineChart
          :series="[{ points: curve(grid, (x) => mixPdf1(x, ANIMAL_FIT)), color: INK, width: 2.6 }]"
          :bars="hist" :vlines="[{ x: x0, color: MUTED, dash: '4 3' }]"
          :dots="[{ x: x0, y: mixPdf1(x0, ANIMAL_FIT), color: INK, r: 5 }]"
          :x-domain="[79, 101]" :y-domain="[0, 0.16]" x-label="length (mm)" y-label="density"
          :x-ticks="[80, 85, 90, 95, 100]" :y-ticks="[0, 0.05, 0.1, 0.15]" title="a density"
        />
        <div class="cap">density estimation: f({{ x0.toFixed(1) }}) = {{ mixPdf1(x0, ANIMAL_FIT).toFixed(3) }}</div>
      </div>
      <div class="col">
        <LineChart
          :series="[0, 1].map((k) => ({ points: curve(grid, (x) => resp1(x, ANIMAL_FIT)[k]), color: COMP[k], width: 2.6 }))"
          :hlines="[{ y: 0.5, dash: '2 3' }]" :vlines="[{ x: x0, color: MUTED, dash: '4 3' }]"
          :dots="[0, 1].map((k) => ({ x: x0, y: g[k], color: COMP[k], r: 5 }))"
          :x-domain="[79, 101]" :y-domain="[-0.04, 1.04]" x-label="length (mm)" y-label="P(Z = k | x)"
          :x-ticks="[80, 85, 90, 95, 100]" :y-ticks="[0, 0.5, 1]" title="a label" :title-color="PURPLE"
        />
        <div class="cap">soft clustering: P(Z = 1 | x) = <b :style="{ color: COMP[0] }">{{ g[0].toFixed(2) }}</b>, P(Z = 2 | x) = <b :style="{ color: COMP[1] }">{{ g[1].toFixed(2) }}</b></div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="x0" :min="80" :max="99" :step="0.1" label="a length x" :digits="1" unit=" mm" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.8rem; }
</style>
