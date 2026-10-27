<!-- one_gaussian_fails: drag the single bell's mean and width as you like;
     its log-likelihood never reaches the two-component mixture's. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, ANIMAL_FIT, linspace, loglik1, mixPdf1, normPdf, weighted1 } from '../lib/gmm'
import { bars, curve, edges, fmt } from '../lib/charts'
import { COMP, GREEN, RED } from '../lib/theme'

const n = ANIMALS.length
const mean = ANIMALS.reduce((a, b) => a + b, 0) / n
const sdMle = Math.sqrt(ANIMALS.reduce((a, b) => a + (b - mean) ** 2, 0) / n)
const mu = ref(+mean.toFixed(1))
const sd = ref(+sdMle.toFixed(1))
const grid = linspace(79, 101, 300)
const E = edges(81.5, 98.5, 1)
const hist = bars(ANIMALS, E, { density: true })
const ll1 = computed(() => loglik1(ANIMALS, { p: [1], mu: [mu.value], sd: [sd.value] }))
const ll2 = loglik1(ANIMALS, ANIMAL_FIT)
const best1 = loglik1(ANIMALS, { p: [1], mu: [mean], sd: [sdMle] })
</script>

<template>
  <div class="wrap">
    <div class="note top">No bell can fit the sample: move it, widen it, it still misses both peaks.</div>
    <div class="body">
      <div class="col">
        <LineChart
          :series="[{ points: curve(grid, (x) => normPdf(x, mu, sd)), color: RED, width: 2.6 }]"
          :bars="hist" :x-domain="[79, 101]" :y-domain="[0, 0.2]" x-label="length (mm)" y-label="density"
          :x-ticks="[80, 85, 90, 95, 100]" :y-ticks="[0, 0.1, 0.2]" title="One Gaussian" :title-color="RED"
        />
        <div class="cap">one mean, one width: log-likelihood <b :style="{ color: RED }">{{ fmt(ll1) }}</b> (best possible {{ fmt(best1) }})</div>
      </div>
      <div class="col">
        <LineChart
          :series="[
            ...[0, 1].map((k) => ({ points: curve(grid, (x) => weighted1(x, ANIMAL_FIT)[k]), color: COMP[k], width: 1.8, dash: '6 4' })),
            { points: curve(grid, (x) => mixPdf1(x, ANIMAL_FIT)), color: GREEN, width: 2.6 },
          ]"
          :bars="hist" :x-domain="[79, 101]" :y-domain="[0, 0.2]" x-label="length (mm)"
          :x-ticks="[80, 85, 90, 95, 100]" :y-ticks="[0, 0.1, 0.2]" title="Two Gaussians mixed" :title-color="GREEN"
        />
        <div class="cap">two of each, plus a weight: log-likelihood <b :style="{ color: GREEN }">{{ fmt(ll2) }}</b></div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="mu" :min="82" :max="97" :step="0.1" label="mean μ" :digits="1" :color="RED" />
      <Knob v-model="sd" :min="0.8" :max="8" :step="0.05" label="width σ" :digits="2" :color="RED" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.8rem; }
</style>
