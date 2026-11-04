<!-- dr_obstacles, more true dimensions than the map: a box of points seen
     from one side. The deeper the box, the more far-apart points land on top
     of each other, whatever the angle. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { kept, shepard } from '../lib/pairs'
import { GRID, MUTED, rgb, viridis } from '../lib/theme'
import type { Pt } from '../lib/geom'

const depth = ref(1)
const turn = ref(0)
const N = 300
const r = new Rng(3)
const U = Array.from({ length: N }, () => [r.next(), r.next(), r.next()])
const cols = U.map((u) => rgb(viridis(u[2])))
const X = computed(() => U.map(([x, y, z]) => [x, y, depth.value * z]))
const view = computed<Pt[]>(() => {
  const a = (turn.value * Math.PI) / 180, c = Math.cos(a), s = Math.sin(a)
  return X.value.map(([x, y, z]) => [(x - 0.5) * c + (z - depth.value / 2) * s, y])
})
// a fixed sample of the pairs keeps the Shepard plot light
const pick = (() => { const q = new Rng(9); return Array.from({ length: 1500 }, () => Math.floor(q.next() * N * (N - 1) / 2)) })()
const pairs = computed(() => { const all = shepard(X.value, view.value); return pick.map((k) => all[k]) })
const share = computed(() => kept(X.value, view.value, 10))
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 300 points drawn uniformly in a 3-D box of size 1 × 1 × depth, coloured by depth. The map is the box seen from one side, i.e. its projection onto a plane, as any linear map to 2-D would make. <b>Right:</b> for 1500 pairs, the distance in 3-D against the distance in the view; projecting can only shrink distances, so every pair falls below the diagonal.</div>
    <div class="r2">
      <Plane :X="view" :colors="cols" :size="3" :domain="[-0.85, 0.85, -0.05, 1.05]"
        title="the box seen from one side (colour = depth)" />
      <Plane :X="pairs" :colors="MUTED" :size="2" axes :equal="false" :domain="[0, 1.75, 0, 1.75]"
        :segments="[{ a: [0, 0], b: [1.75, 1.75], color: GRID, width: 1.2, dash: [5, 4] }]"
        x-label="distance in 3-D" y-label="distance in the view" title="pairs of points" />
    </div>
    <div class="foot">Only <b>{{ (100 * share).toFixed(0) }}%</b> of each point's 10 nearest neighbours in the view are true neighbours in 3-D:
      a map with fewer dimensions than the data must put far points on top of each other.</div>
    <div class="controls">
      <Knob v-model="depth" :min="0" :max="1" :step="0.01" label="depth of the box" :color="MUTED" />
      <Knob v-model="turn" :min="0" :max="90" :step="1" :digits="0" unit="°" label="turn the view" :color="MUTED" />
    </div>
  </div>
</template>
