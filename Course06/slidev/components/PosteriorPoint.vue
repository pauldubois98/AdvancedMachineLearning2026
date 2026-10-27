<!-- posterior_pointwise: once the mixture is known, every point gets class
     probabilities. Slide x0: the bar at x0 is p1 f1(x0) stacked on p2 f2(x0);
     the shares of the bar are the probabilities. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMAL_FIT, linspace, mixPdf1, weighted1 } from '../lib/gmm'
import { curve } from '../lib/charts'
import { COMP, INK } from '../lib/theme'

const x0 = ref(89)
const grid = linspace(80, 99, 400)
const a = computed(() => weighted1(x0.value, ANIMAL_FIT))
const post = computed(() => a.value.map((v) => v / (a.value[0] + a.value[1])))
const top = Math.max(...grid.map((x) => mixPdf1(x, ANIMAL_FIT)))
</script>

<template>
  <div class="wrap">
    <div class="note top">Once the mixture is known, every point gets class probabilities</div>
    <div class="body">
      <LineChart
        :series="[
          ...[0, 1].map((k) => ({ points: curve(grid, (x) => weighted1(x, ANIMAL_FIT)[k]), color: COMP[k], width: 2, dash: '6 4' })),
          { points: curve(grid, (x) => mixPdf1(x, ANIMAL_FIT)), color: INK, width: 2.4 },
        ]"
        :bars="[{ x: x0, y: a[0], w: 0.28, color: COMP[0], alpha: 1 }, { x: x0, y0: a[0], y: a[0] + a[1], w: 0.28, color: COMP[1], alpha: 1 }]"
        :dots="[{ x: x0, y: a[0] + a[1], color: INK, r: 4 }]"
        :labels="[{ x: 95.5, y: top * 0.9, text: 'f(x)', color: INK }, { x: 95.5, y: top * 0.78, text: 'p₁ f₁(x)', color: COMP[0] }, { x: 95.5, y: top * 0.66, text: 'p₂ f₂(x)', color: COMP[1] }]"
        :x-domain="[80, 99]" :y-domain="[0, top * 1.1]" x-label="length (mm)" :x-ticks="[82, 86, 90, 94, 98]" :y-ticks="[]"
      />
      <div class="side">
        <Tex display formula="P(Z = k \mid X = x) = \frac{P(Z = k)\, f(x \mid Z = k)}{f(x)}" />
        <p class="note" style="text-align: center">Bayes' rule</p>
        <Tex display formula="\qquad = \frac{p_k\, f_k(x)}{\sum_l p_l\, f_l(x)}" />
        <p class="note" style="text-align: center">prior times density, over the mixture (total probability)</p>
        <p class="big">x₀ = {{ x0.toFixed(1) }}: <b :style="{ color: COMP[0] }">{{ post[0].toFixed(2) }}</b> for class 1, <b :style="{ color: COMP[1] }">{{ post[1].toFixed(2) }}</b> for class 2</p>
        <p class="note">the blue share and the gold share of the bar. No label is needed: only the fitted p<sub>k</sub>, μ<sub>k</sub>, σ<sub>k</sub>.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="x0" :min="81" :max="98" :step="0.1" label="x₀" :digits="1" unit=" mm" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
.big { font-size: 1.05rem; text-align: center; margin: 0.7rem 0 0.3rem; }
</style>
