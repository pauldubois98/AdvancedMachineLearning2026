<!-- sne_gaussian: a bell on the followed point; its width is the knob. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { TOY, TOY_D, TOY_DOMAIN, TOY_N, nearest } from '../lib/data'
import { linspace, type Pt } from '../lib/geom'
import { COMP, RED } from '../lib/theme'

const i = ref(TOY.star)
const sigma = ref(0.6)
const S = computed(() => [sigma.value ** 2, 0, sigma.value ** 2] as [number, number, number])
const grid = linspace(0, 7, 300)
const dots = computed(() => Array.from({ length: TOY_N }, (_, j) => j).filter((j) => j !== i.value).map((j) => {
  const d = Math.sqrt(TOY_D[i.value * TOY_N + j])
  return { x: d, y: Math.exp(-(d * d) / (2 * sigma.value ** 2)), color: COMP[TOY.g[j]], r: 4 }
}))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Plane :X="TOY.X" :colors="TOY.g.map((k) => COMP[k])" :size="5" pickable @pick="(x, y) => (i = nearest(TOY.X, x, y))"
        :ellipses="[{ mu: TOY.X[i] as Pt, S, color: RED, nsig: [1, 2, 3], width: 1.3 }]"
        :markers="[{ at: TOY.X[i] as Pt, color: RED, shape: 'star', size: 11 }]" :domain="TOY_DOMAIN" title="circles at σ, 2σ, 3σ" />
      <LineChart :series="[{ points: grid.map((d) => [d, Math.exp(-(d * d) / (2 * sigma ** 2))]), color: RED, width: 2.2 }]" :dots="dots"
        :x-domain="[0, 7]" :y-domain="[0, 1.05]" :x-ticks="[0, 1, 2, 3, 4, 5, 6, 7]" :y-ticks="[0, 0.5, 1]"
        x-label="distance ‖xᵢ − xⱼ‖" y-label="similarity" title="exp(−‖xᵢ − xⱼ‖² / 2σ²)" />
    </div>
    <div class="foot">Near points get a high similarity, far ones almost zero; σ sets where "near" ends.</div>
    <div class="controls"><Knob v-model="sigma" :min="0.1" :max="4" log label="width σ" :color="RED" /></div>
  </div>
</template>
