<!-- clustering_setting: the same cloud, twice. Left what the algorithm is
     given, right what it is asked to produce. The slider pulls the groups
     apart, which is the whole difficulty in one knob. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { blobs } from '../lib/data4'
import { kmeans } from '../lib/cluster'
import { BLUE, GREEN, INK, MUTED } from '../lib/theme'

const spread = ref(0.62)
const k = ref(3)

const data = computed(() => {
  const centres: [number, number][] = [
    [-1.7, -1.0],
    [1.8, -0.6],
    [0.2, 1.9],
  ]
  return blobs(centres, spread.value, 55, 1)
})
const found = computed(() => kmeans(data.value.X, k.value, 3, 6))
/** how often the found grouping agrees with the one that generated the data */
const agreement = computed(() => {
  if (k.value !== 3) return null
  const n = data.value.X.length
  let best = 0
  const perms = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]]
  for (const p of perms) {
    let hit = 0
    for (let i = 0; i < n; i++) if (p[found.value.labels[i]] === data.value.y[i]) hit++
    best = Math.max(best, hit)
  }
  return best / n
})
const dom: [number, number, number, number] = [-4.6, 4.6, -3.4, 4.0]
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot :X="data.X" :domain="dom" :point-size="3" title="given" :title-color="INK" />
      <ClusterPlot
        :X="data.X" :labels="found.labels" :domain="dom" :point-size="3"
        :crosses="found.mu.map((m, i) => ({ x: m[0], y: m[1], color: ['#2b6cb0', '#c53030', '#00ab0e', '#6b46c1', '#b7791f'][i % 5] }))"
        title="goal" :title-color="GREEN"
      />
      <div class="side">
        <p><em class="hl-blue">understand</em><br />
          <span class="note">biology, finance, text, web traffic</span></p>
        <p><em class="hl-green">use</em><br />
          <span class="note">the cluster becomes a feature</span></p>
        <p class="note">No labels are given: nothing says how many groups there are,
          or which point belongs where.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="spread" :min="0.2" :max="1.6" label="spread of each group" :color="BLUE" />
      <Knob v-model="k" :min="2" :max="6" :step="1" label="K asked for" :digits="0" :color="GREEN" />
      <Readout
        :items="[
          { label: 'inertia', value: found.inertia.toFixed(0) },
          { label: 'recovers the true groups', value: agreement === null ? 'K is not 3' : `${(agreement * 100).toFixed(0)}%`,
            color: agreement === null ? MUTED : agreement > 0.9 ? GREEN : '#c53030' },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr 0.72fr; gap: 1rem; min-height: 0; }
.side { font-size: 0.85rem; align-self: center; }
.side p { margin: 0 0 0.75rem; line-height: 1.5; }
.controls { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 13rem; }
</style>
