<!-- good_clustering: four labellings of one cloud, scored by J_w and J_b. The
     slider picks K for the k-means panel, the buttons pick a deliberately bad
     labelling, and the two numbers say which is which. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { blobs } from '../lib/data4'
import { jwJb, kmeans } from '../lib/cluster'
import { Rng } from '../lib/rng'
import { GOLD, GREEN, RED } from '../lib/theme'

const k = ref(3)
const data = blobs([[-1.9, -1.0], [1.9, -0.8], [0.0, 1.9]], 0.52, 50, 5)
const dom: [number, number, number, number] = [-4.4, 4.4, -3.2, 3.8]

const found = computed(() => kmeans(data.X, k.value, 0, 8).labels)
const tooFew = data.X.map((p) => (p[0] > 0 ? 1 : 0))
const tooMany = computed(() => kmeans(data.X, 8, 2, 8).labels)
const atRandom = (() => {
  const rng = new Rng(41)
  return data.X.map(() => Math.floor(rng.next() * 3))
})()

const score = (labels: number[]) => jwJb(data.X, labels)
const panels = computed(() => [
  { labels: found.value, title: `k-means, K = ${k.value}`, color: k.value === 3 ? GREEN : GOLD },
  { labels: tooFew, title: 'too few clusters', color: GOLD },
  { labels: tooMany.value, title: 'too many clusters', color: GOLD },
  { labels: atRandom, title: 'clusters at random', color: RED },
])
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <div v-for="(p, i) in panels" :key="i" class="col">
        <ClusterPlot
          :X="data.X" :labels="p.labels" :domain="dom" :point-size="2.6"
          :title="p.title" :title-color="p.color"
        />
        <div class="note">
          J<sub>w</sub> = {{ score(p.labels).jw.toFixed(0) }} &nbsp;
          J<sub>b</sub> = {{ score(p.labels).jb.toFixed(0) }}
        </div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="k" :min="1" :max="10" :step="1" label="K for the first panel" :digits="0" :color="GREEN" />
      <Readout
        :items="[
          { label: 'J<sub>w</sub> + J<sub>b</sub>', value: (score(found).jw + score(found).jb).toFixed(0) },
          { label: 'is the same for every labelling', value: 'it is the total inertia' },
        ]"
      />
      <span class="note">so only the split between them says anything: small J<sub>w</sub>, large J<sub>b</sub></span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.col .note { text-align: center; }
.controls { display: flex; gap: 1.4rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 13rem; }
</style>
