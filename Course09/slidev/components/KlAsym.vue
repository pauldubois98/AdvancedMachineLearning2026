<!-- kl_asymmetry: the cost of one pair, p log(p/q), by its distance in the
     data and in the map. Click to read a pair's cost. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { rdbu } from '../lib/theme'
import type { Pt } from '../lib/geom'

const cost = (dx: number, dy: number) => Math.exp(-dx * dx) * (dy * dy - dx * dx)
const vmax = 9
const at = ref<Pt>([0.3, 2.6])
const c = computed(() => cost(at.value[0], at.value[1]))
const read = computed(() => {
  const [dx, dy] = at.value
  if (Math.abs(dx - dy) < 0.25) return 'about right'
  return dx < dy ? (c.value > 1 ? 'near in the data, far in the map: expensive' : 'too far in the map, but the pair was not close: cheap')
    : 'far in the data, near in the map: almost free'
})
</script>

<template>
  <div class="cmp">
    <Plane :field="(x: number, y: number) => cost(x, y)" :field-color="(v: number) => rdbu(0.5 + v / (2 * vmax))" :domain="[0, 3, 0, 3]" :equal="false"
      :segments="[{ a: [0, 0], b: [3, 3], color: '#1b1b1b', width: 0.8, dash: [4, 4] }]" :markers="[{ at, color: '#1b1b1b', shape: 'dot', size: 6 }]"
      axes x-label="distance in the data" y-label="distance in the map" pickable @pick="(x, y) => (at = [x, y])"
      :title="`p log(p/q) = ${c.toFixed(2)} at (${at[0].toFixed(2)}, ${at[1].toFixed(2)}): ${read}`" />
    <div class="foot">KL makes near points mapped far apart (top left) cost much more than far points mapped close together (bottom right).
      So SNE keeps the local structure. Click anywhere to read a pair's cost.</div>
    <div />
  </div>
</template>
