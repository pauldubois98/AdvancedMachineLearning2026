<!-- dr_obstacles, curvature: on a spiral the straight line between two points
     says little about the distance along the data. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace, type Pt } from '../lib/geom'
import { GREEN, GRID, INK, RED } from '../lib/theme'

const T0 = 0.5 * Math.PI, T1 = 4.7 * Math.PI
const posA = ref(1)    // turns from the start of the spiral
const gap = ref(1)     // turns from A to B
const pt = (t: number): Pt => [t * Math.cos(t), t * Math.sin(t)]
// arc length of the spiral r = theta from 0 to t
const S = (t: number) => 0.5 * (t * Math.sqrt(1 + t * t) + Math.asinh(t))
const tA = computed(() => T0 + 2 * Math.PI * posA.value)
const maxGap = computed(() => (T1 - tA.value) / (2 * Math.PI))
const tB = computed(() => tA.value + 2 * Math.PI * Math.min(gap.value, maxGap.value))
const path = (a: number, b: number, color: string, width: number) => {
  const s = linspace(a, b, Math.max(2, Math.ceil((b - a) * 30)))
  return s.slice(1).map((t, i) => ({ a: pt(s[i]), b: pt(t), color, width }))
}
const segs = computed(() => [...path(T0, T1, GRID, 2), ...path(tA.value, tB.value, GREEN, 2.6),
  { a: pt(tA.value), b: pt(tB.value), color: RED, width: 2, dash: [5, 4] }])
// the two distances from A, as B moves along the spiral
const curve = computed(() => {
  const ts = linspace(tA.value, T1, 240)
  const a = pt(tA.value)
  return {
    along: ts.map((t) => [S(t) - S(tA.value), S(t) - S(tA.value)] as [number, number]),
    chord: ts.map((t) => { const b = pt(t); return [S(t) - S(tA.value), Math.hypot(b[0] - a[0], b[1] - a[1])] as [number, number] }),
  }
})
const arc = computed(() => S(tB.value) - S(tA.value))
const chord = computed(() => { const a = pt(tA.value), b = pt(tB.value); return Math.hypot(b[0] - a[0], b[1] - a[1]) })
const xmax = S(T1) - S(T0)
const ticks = [0, 25, 50, 75, 100, 125, 150].filter((t) => t <= xmax)
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> a spiral, a curved 1-D shape drawn in the plane, and two of its points A and B. Green: the distance from A to B along the spiral, the way the data runs. Red, dashed: the straight-line distance, which is what PCA, or any map that keeps distances, sees. <b>Right:</b> both distances as B slides along the spiral away from A.</div>
    <div class="r2">
      <Plane :segments="segs" :markers="[{ at: pt(tA), color: INK, shape: 'dot', size: 5 }, { at: pt(tB), color: INK, shape: 'dot', size: 5 }]"
        :domain="[-16, 16, -16, 16]" title="A and B: along the spiral (green), straight (red)" />
      <LineChart :series="[{ points: curve.along, color: GREEN, width: 2.2 }, { points: curve.chord, color: RED, width: 2.2, dash: '5 4' }]"
        :dots="[{ x: arc, y: arc, color: GREEN, r: 5 }, { x: arc, y: chord, color: RED, r: 5 }]"
        :x-domain="[0, xmax]" :y-domain="[0, xmax]" :x-ticks="ticks" :y-ticks="ticks" x-label="distance from A along the spiral" y-label="distance"
        title="as B moves away from A" />
    </div>
    <div class="foot">A and B are <b>{{ arc.toFixed(1) }}</b> apart along the spiral but only <b>{{ chord.toFixed(1) }}</b> in a straight line:
      a map that keeps straight-line distances folds the turns onto each other.</div>
    <div class="controls">
      <Knob v-model="posA" :min="0" :max="3" :step="0.01" label="A along the spiral (turns)" :color="INK" />
      <Knob v-model="gap" :min="0" :max="2" :step="0.01" label="B after A (turns)" :color="GREEN" />
    </div>
  </div>
</template>
