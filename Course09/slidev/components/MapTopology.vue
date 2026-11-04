<!-- dr_obstacles, topology: a loop opened onto a line. However it is opened,
     the two points on either side of the cut, neighbours on the loop, end up
     at opposite ends of the map. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { shepard } from '../lib/pairs'
import { GRID, MUTED, RED, rgb, viridis } from '../lib/theme'
import type { Pt } from '../lib/geom'

const N = 40
const open = ref(0.6)
const cut = ref(90)
const cols = Array.from({ length: N }, (_, k) => rgb(viridis(k / (N - 1))))
// the data: a unit circle, point k at angle cut + 2 pi (k + 1/2) / N, so that
// points 0 and N - 1 sit on either side of the cut
const data = computed<Pt[]>(() => Array.from({ length: N }, (_, k) => {
  const a = (cut.value * Math.PI) / 180 + (2 * Math.PI * (k + 0.5)) / N
  return [Math.cos(a), Math.sin(a)]
}))
// the map: the same arc length 2 pi, bent less and less. At open = 0 it is
// the circle, at open = 1 a straight line; it is turned so that the middle of
// the arc stays where it was on the circle.
const map = computed<Pt[]>(() => {
  const phi = 2 * Math.PI * (1 - open.value)
  const R = phi > 1e-6 ? (2 * Math.PI) / phi : Infinity
  const rot = (cut.value * Math.PI) / 180 + Math.PI // the middle of the arc
  const c = Math.cos(rot), s = Math.sin(rot)
  return Array.from({ length: N }, (_, k) => {
    const u = -Math.PI + (2 * Math.PI * (k + 0.5)) / N // arc length from the middle
    // in a frame where the middle of the arc is at (1, 0) and the arc runs up
    const x = R === Infinity ? 1 : 1 - R + R * Math.cos(u / R)
    const y = R === Infinity ? u : R * Math.sin(u / R)
    return [x * c - y * s, x * s + y * c]
  })
})
const pairs = computed(() => shepard(data.value, map.value))
const ends = computed(() => {
  const a = data.value[0], b = data.value[N - 1], p = map.value[0], q = map.value[N - 1]
  return { d: Math.hypot(a[0] - b[0], a[1] - b[1]), m: Math.hypot(p[0] - q[0], p[1] - q[1]) }
})
const ring = Array.from({ length: 96 }, (_, s) => {
  const a = (2 * Math.PI * s) / 96, b = (2 * Math.PI * (s + 1)) / 96
  return { a: [Math.cos(a), Math.sin(a)] as Pt, b: [Math.cos(b), Math.sin(b)] as Pt, color: GRID, width: 1.2 }
})
const cutPair = computed<Pt>(() => [ends.value.d, ends.value.m])
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 40 points evenly spaced on a circle, coloured by their position on the loop. The map keeps them as a chain, 1 step apart, cuts the chain between its purple and yellow ends and bends it open until it lies flat on a line. <b>Right:</b> each pair's distance in the data against its distance in the map; a pair on the dashed diagonal keeps its distance.</div>
    <div class="r2">
      <Plane :X="map" :colors="cols" :size="5" :domain="[-3.6, 3.6, -3.6, 3.6]"
        :segments="[...ring, { a: map[0], b: map[N - 1], color: RED, width: 1.8, dash: [5, 4] }]"
        title="the loop (grey) and its map, opened at the cut" />
      <Plane :X="pairs" :colors="MUTED" :size="2.2" axes :equal="false" :domain="[0, 2.1, 0, 6.6]"
        :segments="[{ a: [0, 0], b: [2.1, 2.1], color: GRID, width: 1.2, dash: [5, 4] }]"
        :markers="[{ at: cutPair, color: RED, shape: 'dot', size: 6 }]"
        x-label="distance on the loop" y-label="distance in the map" title="every pair (red: the two ends)" />
    </div>
    <div class="foot">The two ends, <b>{{ ends.d.toFixed(2) }}</b> apart on the loop, are <b>{{ ends.m.toFixed(2) }}</b> apart in the map:
      a loop cannot be laid flat without tearing two neighbours apart.</div>
    <div class="controls">
      <Knob v-model="open" :min="0" :max="1" :step="0.01" label="open the loop" :color="RED" />
      <Knob v-model="cut" :min="0" :max="360" :step="1" :digits="0" unit="°" label="cut at" :color="MUTED" />
    </div>
  </div>
</template>
