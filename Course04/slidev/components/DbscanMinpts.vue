<!-- dbscan_minpts: eps held, MinPts moving. MinPts decides how much of the
     data is called noise. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { dbscanToy, distances } from '../lib/data4'
import { dbscan } from '../lib/density'
import { BLUE, GOLD, GREEN, RED } from '../lib/theme'

const minPts = ref(6)
const eps = ref(0.45)
const X = dbscanToy(5)
const D = distances(X)
const run = computed(() => dbscan(X, eps.value, minPts.value, D))
const nClusters = computed(() => new Set(run.value.labels.filter((l) => l >= 0)).size)
const nNoise = computed(() => run.value.labels.filter((l) => l < 0).length)
const sweep = computed(() =>
  Array.from({ length: 29 }, (_, i) => {
    const mp = i + 2
    const r = dbscan(X, eps.value, mp, D)
    return {
      mp,
      k: new Set(r.labels.filter((l) => l >= 0)).size,
      noise: r.labels.filter((l) => l < 0).length,
    }
  }),
)
const verdict = computed(() => {
  if (nClusters.value === 2 && nNoise.value < X.length / 3) {
    return { text: 'about right', color: GREEN }
  }
  if (nClusters.value > 2) return { text: 'too small: strays become clusters of their own', color: RED }
  if (nNoise.value > X.length / 3) return { text: 'too large: dense regions are called noise', color: GOLD }
  return { text: 'the two moons are joined', color: GOLD }
})
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :labels="run.labels" :point-size="2.4"
      :title="`MinPts = ${minPts}: ${nClusters} cluster${nClusters === 1 ? '' : 's'}, ${nNoise} noise`"
      :title-color="verdict.color"
    />
    <div class="right">
      <LineChart
        :series="[{ points: sweep.map((s) => [s.mp, s.k] as [number, number]), color: BLUE, width: 2.2, step: true }]"
        :bars="sweep.map((s) => ({ x: s.mp, y: (s.noise / X.length) * 10, w: 0.7, color: RED, alpha: 0.18 }))"
        :vlines="[{ x: minPts, color: GREEN, dash: '' }]"
        :x-domain="[1.5, 30.5]" :y-domain="[0, 10.5]"
        :x-ticks="[2, 6, 10, 14, 18, 22, 26, 30]" :y-ticks="[0, 2, 4, 6, 8, 10]"
        x-label="MinPts" y-label="clusters   (bars: noise, in tenths)"
        title="MinPts decides how much is noise" :title-color="BLUE"
      />
      <div class="controls">
        <Knob v-model="minPts" :min="2" :max="30" :step="1" label="MinPts" :digits="0" :color="GREEN" />
        <Knob v-model="eps" :min="0.1" :max="1.2" label="ε (held in the printed figure)" :color="GOLD" />
        <Readout
          :items="[
            { label: 'clusters', value: String(nClusters), color: verdict.color },
            { label: 'noise', value: `${nNoise} of ${X.length}`, color: RED },
            { label: '', value: verdict.text, color: verdict.color },
          ]"
        />
      </div>
      <p class="note">A rule of thumb is MinPts ≈ 2d for d columns, then ε from
        the elbow of the k-distance curve on the next slide.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1.1fr; gap: 1.5rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
</style>
