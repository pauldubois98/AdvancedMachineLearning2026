<!-- A small pictogram for each row of the "Use cases" slide: what the data
     looks like, and what a cluster of it is, in that row's colour. -->
<script setup lang="ts">
import { BLUE, GOLD, GREEN, MUTED, PURPLE, RED } from '../lib/theme'

defineProps<{ kind: 'market' | 'image' | 'text' | 'anomaly' }>()

// customers: two segments of people, one per colour
const people = [
  { x: 8, c: BLUE }, { x: 19, c: BLUE }, { x: 30, c: BLUE },
  { x: 46, c: MUTED }, { x: 57, c: MUTED },
]
// a 8 x 5 scan, the tumour a blob of cells in the middle
const blob = new Set(['3,1', '4,1', '2,2', '3,2', '4,2', '5,2', '3,3', '4,3'])
const cells = Array.from({ length: 40 }, (_, i) => ({ c: i % 8, r: Math.floor(i / 8) }))
// a tight crowd of transactions and one that fits nowhere
const crowd = [
  [14, 20], [18, 15], [21, 23], [24, 17], [17, 27], [27, 24], [12, 24],
  [22, 11], [28, 19], [15, 31], [25, 29],
].map(([x, y]) => [20 + 1.3 * (x - 20), 21 + 1.3 * (y - 21)])
</script>

<template>
  <svg class="icon" viewBox="0 0 64 40" aria-hidden="true">
    <template v-if="kind === 'market'">
      <g v-for="(p, i) in people" :key="i" :style="{ fill: p.c }">
        <circle :cx="p.x" cy="12" r="4.2" />
        <path :d="`M${p.x - 6},34 Q${p.x - 6},19 ${p.x},19 Q${p.x + 6},19 ${p.x + 6},34 Z`" />
      </g>
      <rect x="1.5" y="4" width="36" height="33" rx="5" :style="{ fill: 'none', stroke: BLUE, strokeWidth: 1.4, strokeDasharray: '3,2' }" />
    </template>
    <template v-else-if="kind === 'image'">
      <rect
        v-for="(q, i) in cells" :key="i"
        :x="1 + q.c * 7.8" :y="1 + q.r * 7.8" width="7" height="7" rx="1"
        :style="{ fill: blob.has(`${q.c},${q.r}`) ? GREEN : '#dfe2e5' }"
      />
    </template>
    <template v-else-if="kind === 'text'">
      <g v-for="(d, i) in [{ x: 4, c: PURPLE }, { x: 14, c: PURPLE }, { x: 36, c: GOLD }, { x: 46, c: GOLD }]" :key="i">
        <path
          :d="`M${d.x},6 h9 l4,4 v22 h-13 Z`"
          :style="{ fill: '#fff', stroke: d.c, strokeWidth: 1.4, strokeLinejoin: 'round' }"
        />
        <line v-for="k in 4" :key="k" :x1="d.x + 2.5" :x2="d.x + 10.5" :y1="12 + k * 4" :y2="12 + k * 4" :style="{ stroke: d.c, strokeWidth: 1.1 }" />
      </g>
      <path d="M2,36 h28" :style="{ stroke: PURPLE, strokeWidth: 2, strokeLinecap: 'round' }" />
      <path d="M34,36 h28" :style="{ stroke: GOLD, strokeWidth: 2, strokeLinecap: 'round' }" />
    </template>
    <template v-else>
      <circle v-for="(p, i) in crowd" :key="i" :cx="p[0]" :cy="p[1]" r="2.4" :style="{ fill: MUTED }" />
      <circle cx="52" cy="10" r="2.8" :style="{ fill: RED }" />
      <circle cx="52" cy="10" r="7" :style="{ fill: 'none', stroke: GOLD, strokeWidth: 1.5 }" />
    </template>
  </svg>
</template>

<style scoped>
.icon { display: block; width: 4.8em; height: 3em; overflow: visible; }
</style>
