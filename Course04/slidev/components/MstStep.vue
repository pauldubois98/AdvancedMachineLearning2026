<!-- mst_step: the cheapest set of edges that still connects everything, under
     d_mreach. The slider drops the heaviest edges, which is how the hierarchy
     is read off it. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { densityData, distances } from '../lib/data4'
import { mutualReachability, primMst } from '../lib/density'
import { GREEN, INK, MUTED, density, rgb } from '../lib/theme'

const k = ref(5)
const drop = ref(0)
const X = densityData(7, 45, 28, 12)
const D = distances(X)
const edges = computed(() => {
  const mr = mutualReachability(X, k.value, D).mr
  return primMst(mr).sort((a, b) => a.w - b.w)
})
const kept = computed(() => edges.value.slice(0, edges.value.length - Math.round(drop.value)))
const wmax = computed(() => Math.max(...edges.value.map((e) => e.w)))
const drawn = computed(() =>
  kept.value.map((e) => ({
    a: X[e.i] as [number, number],
    b: X[e.j] as [number, number],
    color: rgb(density(e.w / wmax.value)),
    width: 1.3,
  })),
)
/** connected components of what is left: the clusters at this cut */
const comps = computed(() => {
  const parent = X.map((_, i) => i)
  const find = (i: number): number => (parent[i] === i ? i : (parent[i] = find(parent[i])))
  for (const e of kept.value) parent[find(e.i)] = find(e.j)
  const groups = new Map<number, number>()
  const labels = X.map((_, i) => {
    const r = find(i)
    if (!groups.has(r)) groups.set(r, groups.size)
    return groups.get(r)!
  })
  const sizes = [...new Set(labels)].map((l) => labels.filter((v) => v === l).length).sort((a, b) => b - a)
  return { labels, sizes }
})
const possible = (X.length * (X.length - 1)) / 2
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :labels="drop > 0 ? comps.labels : null" :colors="drop > 0 ? null : X.map(() => INK)"
      :point-size="2.4" :edges="drawn"
      :title="drop === 0 ? 'minimum spanning tree under d<sub>mreach</sub>' : `the ${drop} heaviest edge${drop > 1 ? 's' : ''} removed`"
      :title-color="drop === 0 ? INK : GREEN"
    />
    <div class="right">
      <LineChart
        :series="[{ points: edges.map((e, i) => [i, e.w] as [number, number]), color: '#2b6cb0', width: 2 }]"
        :vlines="[{ x: edges.length - drop - 0.5, color: GREEN, dash: '' }]"
        :x-domain="[0, edges.length]" :y-domain="[0, wmax * 1.05]"
        x-label="edges, cheapest first" y-label="d_mreach of the edge"
        title="the edge weights of the tree" :title-color="'#2b6cb0'"
      />
      <div class="controls">
        <Knob v-model="k" :min="2" :max="20" :step="1" label="k" :digits="0" :color="'#2b6cb0'" />
        <Knob v-model="drop" :min="0" :max="12" :step="1" label="heaviest edges removed" :digits="0" :color="GREEN" />
        <Readout
          :items="[
            { label: 'points', value: String(X.length) },
            { label: 'possible edges', value: String(possible), color: MUTED },
            { label: 'edges kept', value: String(kept.length), color: GREEN },
            { label: 'pieces', value: comps.sizes.length + (comps.sizes.length > 1 ? ` (${comps.sizes.slice(0, 3).join('/')}…)` : ''), color: GREEN },
          ]"
        />
      </div>
      <p class="note">"the cheapest set of edges that still connects
        everything": n − 1 of them out of {{ possible }}, and cutting them
        heaviest first is exactly reading the dendrogram from the top.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.5rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
</style>
