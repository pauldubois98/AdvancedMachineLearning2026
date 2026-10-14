<!-- dbscan_knn_elbow: fix MinPts, sort the k-distances, and read eps off the
     knee. Both the knee and MinPts are sliders, so the reading is live. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { dbscanToy, distances } from '../lib/data4'
import { dbscan, kthNeighbourDistances } from '../lib/density'
import { BLUE, GREEN, RED } from '../lib/theme'

const k = ref(6)
const eps = ref(0.34)
const X = dbscanToy(5)
const D = distances(X)
const curve = computed(() => {
  const d = kthNeighbourDistances(X, k.value, D).slice().sort((a, b) => a - b)
  return d.map((v, i) => [i, v] as [number, number])
})
const run = computed(() => dbscan(X, eps.value, k.value, D))
const nClusters = computed(() => new Set(run.value.labels.filter((l) => l >= 0)).size)
const nNoise = computed(() => run.value.labels.filter((l) => l < 0).length)
/** How many points sit above the line. A point is a core point exactly when
 *  its kth-neighbour distance is at most eps, so this is the number of points
 *  that are not core. */
const above = computed(() => curve.value.filter((p) => p[1] > eps.value).length)
const notCore = computed(() => run.value.core.filter((c) => !c).length)
/** The knee: the point furthest from the chord across the curve. The last
 *  5% is left out, because the tail of a k-distance curve runs away and would
 *  otherwise always win. */
const knee = computed(() => {
  const c = curve.value
  const last = Math.floor(0.95 * (c.length - 1))
  const x0 = 0
  const y0 = c[0][1]
  const x1 = last
  const y1 = c[last][1]
  const len = Math.hypot(x1 - x0, y1 - y0)
  let best = 0
  let bv = -Infinity
  for (let i = 1; i < last; i++) {
    const d = Math.abs((y1 - y0) * i - (x1 - x0) * (c[i][1] - y0)) / len
    if (d > bv) { bv = d; best = i }
  }
  return c[best][1]
})
</script>

<template>
  <div class="wrap">
    <div class="left">
      <LineChart
        :series="[{ points: curve, color: BLUE, width: 2.4 }]"
        :hlines="[{ y: eps, color: RED, dash: '6,4' }, { y: knee, color: GREEN, dash: '2,3' }]"
        :vlines="[{ x: X.length - above, color: RED, dash: '2,3' }]"
        :x-domain="[0, X.length]" :y-domain="[0, Math.max(...curve.map((p) => p[1])) * 1.05]"
        :x-ticks="[0, 60, 120, 180, 240]"
        x-label="points, sorted" :y-label="`distance to the ${k}th neighbour`"
        title="fix MinPts, then read ε off the knee" :title-color="BLUE"
        :labels="[
          { x: 6, y: eps * 1.08, text: 'ε', color: RED, size: 12 },
          { x: 6, y: knee * 1.08, text: 'suggested knee', color: GREEN, size: 11 },
        ]"
      />
      <div class="note">below the line, ordinary points; above it, the sparse tail</div>
    </div>
    <div class="right">
      <ClusterPlot
        :X="X" :labels="run.labels" :point-size="2.4"
        :title="`ε = ${eps.toFixed(2)}, MinPts = ${k}: ${nClusters} cluster${nClusters === 1 ? '' : 's'}, ${nNoise} noise`"
        :title-color="GREEN"
      />
      <div class="controls">
        <Knob v-model="k" :min="3" :max="20" :step="1" label="MinPts" :digits="0" :color="BLUE" />
        <Knob v-model="eps" :min="0.05" :max="1.2" label="ε, the line" :color="RED" />
        <Readout
          :items="[
            { label: 'points above the line', value: String(above), color: RED },
            { label: 'not core points', value: String(notCore), color: RED },
            { label: 'of those, noise', value: String(nNoise), color: RED },
            { label: 'suggested ε', value: knee.toFixed(2), color: GREEN },
          ]"
        />
      </div>
      <p class="note">A point is a core point exactly when its kth-neighbour
        distance is at most ε, so the points above the line are precisely the
        ones that are not core. The ones that end up noise are those of them
        that have no core neighbour either, which is why the second count is
        the smaller one.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.05fr 1fr; gap: 1.5rem; height: 100%; min-height: 0; }
.left { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.left .note { text-align: center; }
.right { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
</style>
