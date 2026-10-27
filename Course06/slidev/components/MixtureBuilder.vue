<!-- eq_mixture, made live: two weighted bells and their sum. Every weighted
     bell is drawn dashed in its own colour; the mixture is the ink curve. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace, mixPdf1, weighted1 } from '../lib/gmm'
import { curve } from '../lib/charts'
import { COMP, INK, PURPLE } from '../lib/theme'

const p1 = ref(0.4)
const mu1 = ref(-1.2)
const sd1 = ref(0.7)
const mu2 = ref(1.3)
const sd2 = ref(1.0)
const m = computed(() => ({ p: [p1.value, 1 - p1.value], mu: [mu1.value, mu2.value], sd: [sd1.value, sd2.value] }))
const grid = linspace(-5, 5, 400)
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[
          ...[0, 1].map((k) => ({ points: curve(grid, (x) => weighted1(x, m)[k]), color: COMP[k], width: 2, dash: '6 4' })),
          { points: curve(grid, (x) => mixPdf1(x, m)), color: INK, width: 2.8 },
        ]"
        :x-domain="[-5, 5]" :y-domain="[0, 0.62]" x-label="x" :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[0, 0.2, 0.4, 0.6]"
        :labels="[
          { x: mu1, y: weighted1(mu1, m)[0] + 0.03, text: 'p₁ f₁', color: COMP[0], anchor: 'middle' },
          { x: mu2, y: weighted1(mu2, m)[1] + 0.03, text: 'p₂ f₂', color: COMP[1], anchor: 'middle' },
        ]"
      />
      <div class="side">
        <div class="h">What the pieces are</div>
        <p>— K classes, p<sub>k</sub> the chance of landing in class k</p>
        <p>— p<sub>k</sub> ≥ 0 and p<sub>1</sub> + ⋯ + p<sub>K</sub> = 1</p>
        <p>— f<sub>k</sub> the density inside class k</p>
        <p class="note" style="margin-top: 0.8rem">Gaussian mixture: every f<sub>k</sub> is a normal density. The ink curve still integrates to one.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="p1" :min="0" :max="1" :step="0.01" label="weight p₁" :color="PURPLE" />
      <Knob v-model="mu1" :min="-4" :max="4" :step="0.05" label="μ₁" :digits="1" :color="COMP[0]" />
      <Knob v-model="sd1" :min="0.2" :max="2.5" :step="0.05" label="σ₁" :color="COMP[0]" />
      <Knob v-model="mu2" :min="-4" :max="4" :step="0.05" label="μ₂" :digits="1" :color="COMP[1]" />
      <Knob v-model="sd2" :min="0.2" :max="2.5" :step="0.05" label="σ₂" :color="COMP[1]" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.6fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
.controls > .knob { min-width: 9.5rem; }
</style>
