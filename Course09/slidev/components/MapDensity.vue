<!-- dr_obstacles, density: a dense and a sparse group. With one radius, a
     point of the dense group has many neighbours and one of the sparse group
     almost none. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace, type Pt } from '../lib/geom'
import { circle } from '../lib/pairs'
import { Rng } from '../lib/rng'
import { BLUE, GOLD } from '../lib/theme'

const rad = ref(0.4)
const spread = ref(0.9)
const N = 80
const r = new Rng(6)
const zd = Array.from({ length: N }, () => [r.normal(0, 1), r.normal(0, 1)])
const zs = Array.from({ length: N }, () => [r.normal(0, 1), r.normal(0, 1)])
const X = computed<Pt[]>(() => [
  ...zd.map(([a, b]) => [-1.6 + 0.15 * a, 0.15 * b] as Pt),
  ...zs.map(([a, b]) => [1.4 + spread.value * a, spread.value * b] as Pt),
])
const cols = [...Array(N).fill(BLUE), ...Array(N).fill(GOLD)]
// the point of each group nearest its centre
const centreOf = (lo: number) => { let best = lo, bd = Infinity; const z = lo ? zs : zd
  z.forEach(([a, b], i) => { const d = a * a + b * b; if (d < bd) { bd = d; best = lo + i } }); return best }
const iD = centreOf(0), iS = centreOf(N)
const count = (i: number, rr: number, P: Pt[]) => P.filter((p, j) => j !== i && Math.hypot(p[0] - P[i][0], p[1] - P[i][1]) <= rr).length
// the mean number of neighbours within r, for each group
const RS = linspace(0, 2.5, 60)
const mean = (lo: number, rr: number, P: Pt[]) => { let s = 0; for (let i = lo; i < lo + N; i++) s += count(i, rr, P); return s / N }
const curves = computed(() => [0, N].map((lo) => RS.map((rr) => [rr, mean(lo, rr, X.value)] as [number, number])))
const nd = computed(() => count(iD, rad.value, X.value))
const ns = computed(() => count(iS, rad.value, X.value))
const segs = computed(() => [...circle(X.value[iD], rad.value, BLUE, 1.6, [5, 4]), ...circle(X.value[iS], rad.value, GOLD, 1.6, [5, 4])])
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> two groups of 80 points in 2-D, a tight one (blue, std 0.15) and a spread one (gold). A circle of the same radius is drawn around the most central point of each group. <b>Right:</b> how many points lie within that radius of a point, on average over each group, as the radius grows.</div>
    <div class="r2">
      <Plane :X="X" :colors="cols" :size="3" :segments="segs" :domain="[-2.6, 4.4, -2.6, 2.6]"
        :markers="[{ at: X[iD], color: '#1b1b1b', shape: 'x', size: 5 }, { at: X[iS], color: '#1b1b1b', shape: 'x', size: 5 }]"
        title="one radius around a point of each group" />
      <LineChart :series="[{ points: curves[0], color: BLUE, width: 2.2 }, { points: curves[1], color: GOLD, width: 2.2 }]"
        :vlines="[{ x: rad, color: '#9aa0a6', dash: '4 4' }]" :x-domain="[0, 2.5]" :y-domain="[0, 102]"
        :x-ticks="[0, 0.5, 1, 1.5, 2, 2.5]" :y-ticks="[0, 20, 40, 60, 80, 100]" x-label="radius"
        y-label="neighbours within the radius" title="dense group (blue), sparse group (gold)" />
    </div>
    <div class="foot">Within radius {{ rad.toFixed(2) }}, the dense point has <b>{{ nd }}</b> neighbours and the sparse one <b>{{ ns }}</b>:
      no single scale suits both, which is why SNE gives every point its own width σᵢ.</div>
    <div class="controls">
      <Knob v-model="rad" :min="0.05" :max="2.5" :step="0.01" label="radius (one for all)" :color="BLUE" />
      <Knob v-model="spread" :min="0.2" :max="1.4" :step="0.01" label="spread of the sparse group" :color="GOLD" />
    </div>
  </div>
</template>
