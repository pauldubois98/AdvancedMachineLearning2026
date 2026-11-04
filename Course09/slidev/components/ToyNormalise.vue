<!-- sne_normalise: the similarities divided by their sum: p_{j|i}. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { TOY, TOY_D, TOY_DOMAIN, TOY_N, nearest } from '../lib/data'
import { rowP } from '../lib/sne'
import { COMP, MUTED, RED } from '../lib/theme'
import type { Pt } from '../lib/geom'

const i = ref(TOY.star)
const sigma = ref(0.6)
const row = computed(() => rowP(TOY_D, TOY_N, i.value, 1 / (2 * sigma.value ** 2)))
const order = computed(() => Array.from({ length: TOY_N }, (_, j) => j).filter((j) => j !== i.value).sort((a, b) => TOY_D[i.value * TOY_N + a] - TOY_D[i.value * TOY_N + b]))
const bars = computed(() => order.value.map((j, k) => ({ x: k, y: row.value.p[j], w: 0.8, color: COMP[TOY.g[j]], alpha: 1 })))
const k90 = computed(() => { let s = 0; for (let k = 0; k < order.value.length; k++) { s += row.value.p[order.value[k]]; if (s > 0.9) return k + 1 } return 44 })
const pmax = computed(() => Math.max(...order.value.map((j) => row.value.p[j])))
const sizes = computed(() => TOY.X.map((_, j) => (j === i.value ? 0 : 1.5 + 30 * Math.sqrt(row.value.p[j]))))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Plane :X="TOY.X" :colors="TOY.g.map((k) => COMP[k])" :sizes="sizes" :alpha="0.8" pickable @pick="(x, y) => (i = nearest(TOY.X, x, y))"
        :markers="[{ at: TOY.X[i] as Pt, color: RED, shape: 'star', size: 11 }]" :domain="TOY_DOMAIN" title="area ∝ pⱼ|ᵢ" />
      <LineChart :series="[]" :bars="bars" :vlines="[{ x: k90 - 0.5, color: MUTED, dash: '4 4' }]"
        :labels="[{ x: k90 + 0.5, y: pmax * 0.9, text: `${k90} points hold 90%`, color: MUTED, anchor: 'start' }]"
        :x-domain="[-1, 44]" :y-domain="[0, pmax * 1.08]" :x-ticks="[]" :y-ticks="[]" x-label="the other 44 points, nearest first"
        title="pⱼ|ᵢ = similarity / sum of the similarities" />
    </div>
    <div class="foot">Divided by their sum, the similarities of the star become a distribution over its neighbours.
      Its perplexity, <b>{{ (2 ** row.H).toFixed(1) }}</b>, counts them smoothly.</div>
    <div class="controls"><Knob v-model="sigma" :min="0.1" :max="4" log label="width σ" :color="RED" /></div>
  </div>
</template>
