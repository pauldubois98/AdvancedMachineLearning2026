<!-- kmeans_limits: four clouds k-means cannot do much with, and the knob that
     makes each failure worse or better. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { blobs, blobsVaried, moons } from '../lib/data4'
import { kmeans } from '../lib/cluster'
import { BLUE, GREEN, RED } from '../lib/theme'

const K = ref(2)
const which = ref('moons')

const mo = moons(260, 0.06, 0, 2.0)
const varied = computed(() =>
  blobsVaried([[-2.2, 0], [2.2, 0], [0, 2.4]], [0.9, 0.3, 0.3], 80, 1),
)
const outliers = computed(() => {
  const rng = new Rng(31)
  const X: number[][] = []
  for (let i = 0; i < 90; i++) X.push([rng.normal(-1.6, 0.5), rng.normal(0, 0.5)])
  for (let i = 0; i < 90; i++) X.push([rng.normal(1.6, 0.5), rng.normal(0, 0.5)])
  for (let i = 0; i < 6; i++) X.push([rng.uniform(-7, 7), rng.uniform(-7, 7)])
  return X
})
const four = computed(() => blobs([[-2, -2], [2, -2], [-2, 2], [2, 2]], 0.6, 60, 4))

const sets = computed(() => ({
  moons: { X: mo.X, label: 'non-convex shapes', truth: 2 },
  spreads: { X: varied.value.X, label: 'unequal spreads', truth: 3 },
  outliers: { X: outliers.value, label: 'outliers', truth: 2 },
  four: { X: four.value.X, label: 'wrong K', truth: 4 },
}))
const cur = computed(() => sets.value[which.value as keyof typeof sets.value])
const run = computed(() => kmeans(cur.value.X, K.value, 0, 8))
const right = computed(() => K.value === cur.value.truth)

/** For the outlier panel: how many clusters hold nothing but strays. The six
 *  strays are the last six rows of that dataset. */
const wasted = computed(() => {
  if (which.value !== 'outliers') return null
  const n = cur.value.X.length
  const labels = run.value.labels
  let count = 0
  for (let k = 0; k < K.value; k++) {
    const members = labels.map((l, i) => (l === k ? i : -1)).filter((i) => i >= 0)
    if (members.length && members.every((i) => i >= n - 6)) count++
  }
  return count
})
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot
        v-for="(s, key) in sets" :key="key"
        :X="s.X" :labels="kmeans(s.X, K, 0, 6).labels" :point-size="2"
        :title="s.label" :title-color="RED"
      />
    </div>
    <div class="row">
      <ClusterPlot
        class="big"
        :X="cur.X" :labels="run.labels" :point-size="3"
        :crosses="run.mu.map((m, k) => ({ x: m[0], y: m[1], color: ['#2b6cb0', '#c53030', '#00ab0e', '#6b46c1', '#b7791f'][k % 5] }))"
        :title="`${cur.label}, K = ${K}`" :title-color="right ? GREEN : RED"
      />
      <div class="controls">
        <Choice
          v-model="which" label="look at"
          :options="[
            { value: 'moons', label: 'moons', color: BLUE },
            { value: 'spreads', label: 'spreads', color: BLUE },
            { value: 'outliers', label: 'outliers', color: BLUE },
            { value: 'four', label: 'four blobs', color: BLUE },
          ]"
        />
        <Knob v-model="K" :min="2" :max="8" :step="1" label="K" :digits="0" :color="GREEN" />
        <Readout
          :items="[
            { label: 'inertia', value: run.inertia.toFixed(0) },
            { label: 'groups in the data', value: String(cur.truth) },
            { label: wasted === null ? '' : 'clusters spent on the 6 strays', value: wasted === null ? '' : String(wasted), color: wasted ? '#c53030' : '#1b1b1b' },
          ]"
        />
        <p class="note">Every panel is drawn with the same K. Only the last one
          is cured by choosing it better: the first three break assumptions
          k-means cannot drop, round clusters of similar spread and no outliers.</p>
        <p v-if="wasted !== null" class="note">Raise K on the outlier set and
          the extra cluster does not go to the data: it is spent on two stray
          points, because squared distance makes them expensive to leave in.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 0.9fr 1.1fr; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; min-height: 0; }
.row { display: grid; grid-template-columns: 0.8fr 1.2fr; gap: 1.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.45rem; justify-content: center; }
</style>
