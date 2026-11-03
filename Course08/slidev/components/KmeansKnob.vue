<!-- knob_kmeans_k: k-means on the three clusters of lecture 6, refitted as K
     moves. Right: the inertia against K, which only ever falls: the
     objective cannot choose K, only the elbow hints at it. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLOB_SEED, gmmBlobs } from '../lib/c08'
import { kmeans } from '../lib/gmm'
import { comp, GREEN, INK, RED } from '../lib/theme'

const seed = ref(BLOB_SEED)
const data = computed(() => gmmBlobs(seed.value, 400).X)
const K = ref(3)
// one fit per K, forgotten when the sample changes
const cache = computed(() => (data.value, new Map<number, ReturnType<typeof kmeans>>()))
function fitK(k: number) {
  const c = cache.value
  if (!c.has(k)) c.set(k, kmeans(data.value, k, 0, 10))
  return c.get(k)!
}
const m = computed(() => fitK(K.value))
const KS = Array.from({ length: 10 }, (_, i) => i + 1)
const curve = computed(() => KS.map((k) => [k, fitK(k).inertia] as [number, number]))
const ymax = computed(() => Math.ceil(curve.value[0][1] / 200) * 200)
const verdict = computed(() => (K.value < 3 ? { t: 'two populations merged', c: RED } : K.value > 3 ? { t: 'a population cut into pieces', c: RED } : { t: 'about right', c: GREEN }))
</script>

<template>
  <div class="wrap">
    <div class="body">
      <Plane
        :X="data" :colors="Array.from(m.labels, (l) => comp(l))" :size="3" :alpha="0.8" :domain="[-4, 4, -3.2, 3.2]"
        :markers="m.centers.map((c) => ({ at: c, color: INK, shape: 'x', size: 7 }))"
        :title="`K = ${K}: ${verdict.t}`" :title-color="verdict.c" :caption="`inertia ${m.inertia.toFixed(0)}`"
      />
      <div class="side">
        <LineChart
          :series="[{ points: curve, color: INK, width: 2.2 }]"
          :dots="curve.map(([x, y]) => ({ x, y, color: x === K ? verdict.c : INK, r: x === K ? 6 : 3.5 }))"
          :x-domain="[0.5, 10.5]" :y-domain="[0, ymax]" :x-ticks="KS" :y-ticks="[0, ymax / 2, ymax]"
          x-label="K" y-label="inertia" title="the objective keeps falling" :unit-height="320"
        />
        <p class="note">Inertia falls with every extra centre, so it cannot pick K by itself. The bend (the "elbow") is a hint, not a rule.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="K" :min="1" :max="10" :step="1" :digits="0" label="clusters K" :color="verdict.c" />
      <Knob v-model="seed" :min="1" :max="30" :step="1" :digits="0" label="sample" />
      <span class="note">Lloyd's algorithm, best of 10 random starts.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; min-height: 0; }
.side { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
</style>
