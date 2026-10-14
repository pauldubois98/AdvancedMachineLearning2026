<!-- dbscan_vs_kmeans: three shapes, both methods, one knob each. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { blobsVaried, circles, distances, moons } from '../lib/data4'
import { kmeans } from '../lib/cluster'
import { dbscan } from '../lib/density'
import { BLUE, GREEN, GOLD } from '../lib/theme'

const epsScale = ref(1)
const sets = [
  { name: 'two moons', X: moons(260, 0.06, 0, 2.0).X, k: 2, eps: 0.32 },
  { name: 'rings', X: circles(260, 0.05, 0.45, 0, 2.4).X, k: 2, eps: 0.55 },
  { name: 'unequal spreads', X: blobsVaried([[-2, 0], [2, 0.4], [0, 2.4]], [0.9, 0.3, 0.3], 86, 1).X, k: 3, eps: 0.55 },
].map((s) => ({ ...s, D: distances(s.X) }))

const runs = computed(() =>
  sets.map((s) => {
    const km = kmeans(s.X, s.k, 0, 8)
    const db = dbscan(s.X, s.eps * epsScale.value, 6, s.D)
    return {
      ...s,
      km: km.labels,
      mu: km.mu,
      db: db.labels,
      nDb: new Set(db.labels.filter((l) => l >= 0)).size,
      noise: db.labels.filter((l) => l < 0).length,
    }
  }),
)
</script>

<template>
  <div class="wrap">
    <div class="grid">
      <div class="rowlabel" :style="{ color: BLUE }">k-means</div>
      <ClusterPlot
        v-for="r in runs" :key="`k${r.name}`"
        :X="r.X" :labels="r.km" :point-size="1.9"
        :crosses="r.mu.map((m, i) => ({ x: m[0], y: m[1], color: ['#2b6cb0', '#c53030', '#00ab0e'][i % 3], size: 5 }))"
        :title="r.name"
      />
      <div class="rowlabel" :style="{ color: GREEN }">DBSCAN</div>
      <ClusterPlot
        v-for="r in runs" :key="`d${r.name}`"
        :X="r.X" :labels="r.db" :point-size="1.9"
        :title="`ε = ${(r.eps * epsScale).toFixed(2)}: ${r.nDb} cluster${r.nDb === 1 ? '' : 's'}, ${r.noise} noise`"
        :title-color="GREEN"
      />
    </div>
    <div class="controls">
      <Knob v-model="epsScale" :min="0.4" :max="2.2" label="ε, scaled on all three panels" :color="GREEN" />
      <Readout
        :items="[
          { label: 'k-means on the moons', value: 'cuts them in half', color: GOLD },
          { label: 'DBSCAN on the moons', value: `${runs[0].nDb} cluster${runs[0].nDb === 1 ? '' : 's'}, ${runs[0].noise} noise`, color: GREEN },
        ]"
      />
      <span class="note">k-means draws straight borders between centres, so it
        can only ever carve the plane into convex pieces</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.grid { display: grid; grid-template-columns: auto repeat(3, 1fr); grid-template-rows: 1fr 1fr; gap: 0.3rem 0.8rem; min-height: 0; }
.rowlabel { align-self: center; writing-mode: vertical-rl; transform: rotate(180deg); font-size: 0.82rem; font-weight: 600; }
.controls { display: flex; gap: 1.3rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 16rem; }
</style>
