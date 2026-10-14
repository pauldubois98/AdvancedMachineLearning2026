<!-- hdbscan_result: a dataset with three densities. No single eps works for
     DBSCAN; HDBSCAN is asked for C_min instead. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { densityData, distances } from '../lib/data4'
import { dbscan, hdbscan } from '../lib/density'
import { GREEN, RED } from '../lib/theme'

const eps = ref(0.18)
const cmin = ref(10)
const minPts = ref(5)
const X = densityData(4)
const D = distances(X)

const db = computed(() => dbscan(X, eps.value, minPts.value, D))
const dbLoose = computed(() => dbscan(X, 1.0, minPts.value, D))
const hd = computed(() => hdbscan(X, cmin.value, minPts.value, D))
const count = (labels: number[]) => {
  const k = new Set(labels.filter((l) => l >= 0)).size
  return { k, noise: labels.filter((l) => l < 0).length, word: k === 1 ? 'cluster' : 'clusters' }
}
const dom: [number, number, number, number] = [-4.0, 4.4, -3.2, 3.6]
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <div class="col">
        <ClusterPlot
          :X="X" :labels="db.labels" :domain="dom" :point-size="2.6"
          :title="`DBSCAN, ε = ${eps.toFixed(2)}: ${count(db.labels).k} ${count(db.labels).word}, ${count(db.labels).noise} noise`"
          :title-color="RED"
        />
        <div class="note">tight enough for the dense blobs: the sparse cluster is gone</div>
      </div>
      <div class="col">
        <ClusterPlot
          :X="X" :labels="dbLoose.labels" :domain="dom" :point-size="2.6"
          :title="`DBSCAN, ε = 1.00: ${count(dbLoose.labels).k} ${count(dbLoose.labels).word}, ${count(dbLoose.labels).noise} noise`"
          :title-color="RED"
        />
        <div class="note">loose enough for the sparse one: it swallows the noise and merges clusters</div>
      </div>
      <div class="col">
        <ClusterPlot
          :X="X" :labels="hd.labels" :domain="dom" :point-size="2.6"
          :title="`HDBSCAN, C<sub>min</sub> = ${cmin}: ${count(hd.labels).k} ${count(hd.labels).word}, ${count(hd.labels).noise} noise`"
          :title-color="GREEN"
        />
        <div class="note">all three densities at once, and the strays stay noise</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="eps" :min="0.08" :max="1.2" label="ε of the first panel" :color="RED" />
      <Knob v-model="cmin" :min="3" :max="40" :step="1" label="C<sub>min</sub>" :digits="0" :color="GREEN" />
      <Knob v-model="minPts" :min="2" :max="15" :step="1" label="MinPts" :digits="0" :color="GREEN" />
      <Readout
        :items="[
          { label: 'best DBSCAN can do here', value: 'two of the three', color: RED },
          { label: 'HDBSCAN', value: `${count(hd.labels).k} ${count(hd.labels).word}`, color: GREEN },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.col .note { text-align: center; line-height: 1.4; }
.controls { display: flex; gap: 1.3rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 11rem; }
</style>
