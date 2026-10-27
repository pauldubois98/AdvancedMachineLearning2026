<!-- identifiability: swap the labels. The curve does not move; only the
     colours do. K! parameter vectors give the same density. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace, mixPdf1, normPdf } from '../lib/gmm'
import { curve } from '../lib/charts'
import { COMP, INK, RED } from '../lib/theme'

const swapped = ref(false)
const p = [0.35, 0.65]
const mu = [-1.4, 1.1]
const sd = [0.75, 0.95]
const order = computed(() => (swapped.value ? [1, 0] : [0, 1]))
const grid = linspace(-4.5, 4.5, 400)
const m = { p, mu, sd }
</script>

<template>
  <div class="wrap">
    <div class="body">
      <div class="col">
        <LineChart
          :series="[
            ...order.map((k, slot) => ({ points: curve(grid, (x) => p[k] * normPdf(x, mu[k], sd[k])), color: COMP[slot], width: 2, dash: '6 4' })),
            { points: curve(grid, (x) => mixPdf1(x, m)), color: INK, width: 2.6 },
          ]"
          :x-domain="[-4.5, 4.5]" :y-domain="[0, 0.3]" :x-ticks="[]" :y-ticks="[]"
          :title="swapped ? 'Component 1 is the right one' : 'Component 1 is the left one'"
        />
        <div class="cap">{{ swapped ? 'θ′ = (p₂, θ₂, p₁, θ₁)' : 'θ = (p₁, θ₁, p₂, θ₂)' }}: the same curve, only the colours moved</div>
      </div>
      <div class="side">
        <div class="h" :style="{ color: RED }">Label switching</div>
        <p>— K! parameter vectors give exactly the same density</p>
        <p>— The likelihood has K! identical maxima</p>
        <p>— Component numbers cannot be interpreted</p>
        <p class="note" style="margin-top: 0.8rem">Can be fixed by sorting the components (by μ<sub>k</sub>, or by p<sub>k</sub>).</p>
      </div>
    </div>
    <div class="controls">
      <Toggle v-model="swapped" label="swap the labels 1 ↔ 2" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.8rem; }
.side { align-self: center; }
</style>
