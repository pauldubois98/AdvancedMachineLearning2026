<!-- dbscan_epsilon: too small, about right, too large, on one slider. The
     curve under the panel counts the clusters at every eps, so the plateau
     where the answer is stable is visible. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { dbscanToy, distances } from '../lib/data4'
import { dbscan } from '../lib/density'
import { BLUE, GOLD, GREEN, RED } from '../lib/theme'

const eps = ref(0.45)
const minPts = ref(6)
const X = dbscanToy(5)
const D = distances(X)
const run = computed(() => dbscan(X, eps.value, minPts.value, D))
const nClusters = computed(() => new Set(run.value.labels.filter((l) => l >= 0)).size)
const nNoise = computed(() => run.value.labels.filter((l) => l < 0).length)

/** one DBSCAN per eps on a grid, recomputed when MinPts moves */
const sweep = computed(() => {
  const out: { eps: number; k: number; noise: number }[] = []
  for (let i = 0; i <= 44; i++) {
    const e = 0.05 + (1.25 * i) / 44
    const r = dbscan(X, e, minPts.value, D)
    out.push({
      eps: e,
      k: new Set(r.labels.filter((l) => l >= 0)).size,
      noise: r.labels.filter((l) => l < 0).length,
    })
  }
  return out
})
const verdict = computed(() => {
  if (nClusters.value === 2) return { text: 'about right', color: GREEN }
  if (nClusters.value > 2) {
    return { text: 'too small: the moons break into pieces', color: RED }
  }
  return nClusters.value === 1
    ? { text: 'too large: the two moons merge', color: GOLD }
    : { text: 'far too small: nothing is dense enough', color: RED }
})
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :labels="run.labels" :point-size="2.4"
      :title="`ε = ${eps.toFixed(2)}: ${nClusters} cluster${nClusters === 1 ? '' : 's'}, ${nNoise} noise point${nNoise === 1 ? '' : 's'}`"
      :title-color="verdict.color"
    />
    <div class="right">
      <LineChart
        :series="[
          { points: sweep.map((s) => [s.eps, s.k] as [number, number]), color: BLUE, width: 2.2, step: true },
          { points: sweep.map((s) => [s.eps, (s.noise / X.length) * 10] as [number, number]), color: RED, width: 1.8, dash: '5,4' },
        ]"
        :vlines="[{ x: eps, color: GREEN, dash: '' }]"
        :x-domain="[0.05, 1.3]" :y-domain="[0, 10.5]"
        :x-ticks="[0.2, 0.4, 0.6, 0.8, 1, 1.2]" :y-ticks="[0, 2, 4, 6, 8, 10]"
        x-label="ε" y-label="clusters   (and noise, in tenths)"
        title="clusters found, and how much is called noise" :title-color="BLUE"
        :labels="[
          { x: 0.72, y: 9.4, text: 'share called noise', color: RED, size: 11 },
          { x: 0.72, y: 3.2, text: 'clusters', color: BLUE, size: 11 },
        ]"
      />
      <div class="controls">
        <Knob v-model="eps" :min="0.05" :max="1.3" label="ε" :color="GREEN" />
        <Knob v-model="minPts" :min="2" :max="20" :step="1" label="MinPts" :digits="0" :color="GOLD" />
        <Readout
          :items="[
            { label: 'clusters', value: String(nClusters), color: verdict.color },
            { label: 'noise', value: `${nNoise} of ${X.length}`, color: RED },
            { label: '', value: verdict.text, color: verdict.color },
          ]"
        />
      </div>
      <p class="note">The two moons are a plateau on the blue curve: any ε in
        it gives the same answer, which is what "about right" means.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1.1fr; gap: 1.5rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
</style>
