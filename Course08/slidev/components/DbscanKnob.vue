<!-- knob_dbscan_eps: DBSCAN on the same three clusters, refitted as epsilon
     and MinPts move. Right: the number of clusters and the share of noise
     across the whole range of epsilon. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLOB_SEED, dbscan, gmmBlobs } from '../lib/c08'
import { comp, GREEN, INK, MUTED, RED } from '../lib/theme'

const X = gmmBlobs(BLOB_SEED, 400).X
const eps = ref(0.4)
const minPts = ref(8)
const r = computed(() => dbscan(X, eps.value, minPts.value))
const nClusters = computed(() => Math.max(-1, ...r.value.labels) + 1)
const noise = computed(() => r.value.labels.filter((l) => l < 0).length / X.length)
const inliers = computed(() => X.filter((_, i) => r.value.labels[i] >= 0))
const inColors = computed(() => r.value.labels.filter((l) => l >= 0).map((l) => comp(l)))
const noiseMarks = computed(() => X.filter((_, i) => r.value.labels[i] < 0).map((p) => ({ at: p, color: MUTED, shape: 'x' as const, size: 3 })))

const GRID = Array.from({ length: 50 }, (_, i) => 0.05 + i * 0.025)
const sweep = computed(() => GRID.map((e) => {
  const s = dbscan(X, e, minPts.value)
  return { e, k: Math.max(-1, ...s.labels) + 1, noise: s.labels.filter((l) => l < 0).length / X.length }
}))
const verdict = computed(() =>
  noise.value > 0.3 ? { t: 'too small: almost everything is noise', c: RED }
    : nClusters.value < 3 ? { t: 'too large: populations merged', c: RED }
      : nClusters.value > 3 ? { t: 'populations split', c: RED } : { t: 'about right', c: GREEN })
</script>

<template>
  <div class="wrap">
    <div class="body">
      <Plane
        :X="inliers" :colors="inColors" :size="3" :alpha="0.85" :markers="noiseMarks" :domain="[-4, 4, -3.2, 3.2]"
        :title="`ε = ${eps.toFixed(2)}: ${verdict.t}`" :title-color="verdict.c"
        :caption="`${nClusters} cluster${nClusters === 1 ? '' : 's'} · ${(100 * noise).toFixed(0)}% noise`"
      />
      <div class="side">
        <LineChart
          :series="[{ points: sweep.map((s) => [s.e, s.k] as [number, number]), color: INK, width: 2.2, step: true }]"
          :x-domain="[0.05, 1.3]" :y-domain="[0, 12]" :x-ticks="[0.2, 0.4, 0.6, 0.8, 1, 1.2]" :y-ticks="[0, 3, 6, 9, 12]"
          :vlines="[{ x: eps, color: verdict.c, dash: '' }]" :hlines="[{ y: 3, color: GREEN, dash: '3 3' }]"
          y-label="clusters" title="clusters found" :unit-height="200"
        />
        <LineChart
          :series="[{ points: sweep.map((s) => [s.e, 100 * s.noise] as [number, number]), color: MUTED, width: 2.2 }]"
          :x-domain="[0.05, 1.3]" :y-domain="[0, 100]" :x-ticks="[0.2, 0.4, 0.6, 0.8, 1, 1.2]" :y-ticks="[0, 50, 100]"
          :vlines="[{ x: eps, color: verdict.c, dash: '' }]"
          x-label="ε" y-label="noise %" title="share called noise" :unit-height="200"
        />
      </div>
    </div>
    <div class="controls">
      <Knob v-model="eps" :min="0.05" :max="1.3" :step="0.01" label="radius ε" :color="verdict.c" />
      <Knob v-model="minPts" :min="2" :max="30" :step="1" :digits="0" label="MinPts" />
      <span class="note">Too small and almost every point is noise; too large and the populations merge.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; min-height: 0; }
.side { display: grid; grid-template-rows: 1fr 1fr; gap: 0.4rem; min-height: 0; }
</style>
