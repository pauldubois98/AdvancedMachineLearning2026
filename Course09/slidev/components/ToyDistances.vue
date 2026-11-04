<!-- sne_distances: the distances from one point (click another one). -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { TOY, TOY_D, TOY_DOMAIN, TOY_N, nearest } from '../lib/data'
import { COMP, GRID, RED } from '../lib/theme'
import type { Pt } from '../lib/geom'

const i = ref(TOY.star)
const order = computed(() => Array.from({ length: TOY_N }, (_, j) => j).filter((j) => j !== i.value).sort((a, b) => TOY_D[i.value * TOY_N + a] - TOY_D[i.value * TOY_N + b]))
const segs = computed(() => order.value.map((j) => ({ a: TOY.X[i.value] as Pt, b: TOY.X[j] as Pt, color: GRID, width: 0.8 })))
const bars = computed(() => order.value.map((j, k) => ({ x: k, y: Math.sqrt(TOY_D[i.value * TOY_N + j]), w: 0.8, color: COMP[TOY.g[j]], alpha: 1 })))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Plane :X="TOY.X" :colors="TOY.g.map((k) => COMP[k])" :size="5" :segments="segs" pointsFirst
        :markers="[{ at: TOY.X[i] as Pt, color: RED, shape: 'star', size: 11 }]" :domain="TOY_DOMAIN" pickable
        @pick="(x, y) => (i = nearest(TOY.X, x, y))" title="click a point to follow it" />
      <LineChart :series="[]" :bars="bars" :x-domain="[-1, 44]" :y-domain="[0, 7]" :x-ticks="[]" :y-ticks="[0, 2, 4, 6]"
        x-label="the other 44 points, nearest first" y-label="‖xᵢ − xⱼ‖" title="distances from the star" />
    </div>
    <div class="foot">A distance says how far, not who is a neighbour.</div>
    <div />
  </div>
</template>
