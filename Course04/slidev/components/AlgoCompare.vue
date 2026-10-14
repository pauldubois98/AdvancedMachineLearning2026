<!-- algo_compare: five methods on four shapes. Every method keeps its own
     knob, so a panel that fails can be given its best chance before being
     written off. No method wins everywhere. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { anisotropic, blobsVaried, circles, distances, moons, standardise } from '../lib/data4'
import { kmeans } from '../lib/cluster'
import { dbscan, hdbscan } from '../lib/density'
import { fclusterMaxclust, linkage } from '../lib/hier'
import { subtractive } from '../lib/mountain'
import { BLUE, GOLD, GREEN, PURPLE, RED } from '../lib/theme'

const kShift = ref(0)
const eps = ref(0.3)
const cmin = ref(10)
const ra = ref(1.2)

const sets = [
  { name: 'moons', X: standardise(moons(200, 0.06, 0).X), k: 2 },
  { name: 'rings', X: standardise(circles(200, 0.05, 0.45, 0).X), k: 2 },
  { name: 'anisotropic', X: standardise(anisotropic(201, 170).X), k: 3 },
  { name: 'unequal spreads', X: standardise(blobsVaried([[-4, -2], [1, 3], [3, -3]], [1.0, 2.5, 0.5], 67, 170).X), k: 3 },
].map((s) => ({ ...s, D: distances(s.X), Z: linkage(s.X, 'ward') }))

const K = (base: number) => Math.max(2, base + Math.round(kShift.value))
const rows = computed(() => [
  { name: 'k-means', color: BLUE, labels: sets.map((s) => kmeans(s.X, K(s.k), 0, 4).labels) },
  { name: 'Ward', color: PURPLE, labels: sets.map((s) => fclusterMaxclust(s.Z, K(s.k))) },
  { name: 'DBSCAN', color: GOLD, labels: sets.map((s) => dbscan(s.X, eps.value, 8, s.D).labels) },
  { name: 'HDBSCAN', color: GREEN, labels: sets.map((s) => hdbscan(s.X, Math.round(cmin.value), undefined, s.D).labels) },
  { name: 'subtractive', color: RED, labels: sets.map((s) => subtractive(s.X, ra.value).labels) },
])
const found = (labels: number[]) => new Set(labels.filter((l) => l >= 0)).size
</script>

<template>
  <div class="wrap">
    <div class="grid">
      <div />
      <div v-for="s in sets" :key="s.name" class="colhead">{{ s.name }}</div>
      <template v-for="r in rows" :key="r.name">
        <div class="rowhead" :style="{ color: r.color }">{{ r.name }}</div>
        <div v-for="(labels, i) in r.labels" :key="`${r.name}${i}`" class="cell">
          <ClusterPlot :X="sets[i].X" :labels="labels" :point-size="1.3" :pad="0.35" />
          <span class="count" :style="{ color: r.color }">{{ found(labels) }}</span>
        </div>
      </template>
    </div>
    <div class="controls">
      <Knob v-model="kShift" :min="-1" :max="3" :step="1" label="K, shifted" :digits="0" :color="BLUE" />
      <Knob v-model="eps" :min="0.1" :max="0.8" label="ε, DBSCAN" :color="GOLD" />
      <Knob v-model="cmin" :min="4" :max="30" :step="1" label="C<sub>min</sub>, HDBSCAN" :digits="0" :color="GREEN" />
      <Knob v-model="ra" :min="0.5" :max="2.5" label="r<sub>a</sub>, subtractive" :color="RED" />
      <span class="note">the number over each panel is how many clusters that
        run found</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.grid {
  display: grid; grid-template-columns: auto repeat(4, 1fr);
  grid-template-rows: auto repeat(5, 1fr); gap: 0.15rem 0.3rem; min-height: 0;
}
.colhead { text-align: center; font-size: 0.8rem; }
.cell { position: relative; min-height: 0; }
.count {
  position: absolute; top: 0; right: 0; font-size: 0.72rem; font-weight: 600;
  background: rgba(255, 255, 255, 0.85); padding: 0 0.15rem; border-radius: 2px;
  font-variant-numeric: tabular-nums;
}
.rowhead { align-self: center; font-size: 0.78rem; font-weight: 600; text-align: right; padding-right: 0.2rem; }
.controls { display: flex; gap: 1.2rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 9.5rem; }
</style>
