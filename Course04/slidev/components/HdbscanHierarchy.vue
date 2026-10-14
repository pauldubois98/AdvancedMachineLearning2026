<!-- hdbscan_hierarchy: one dendrogram under d_mreach is DBSCAN at every eps at
     once. The slider is the horizontal cut, i.e. one DBSCAN run. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { densityData, distances } from '../lib/data4'
import { mstToLinkage, mutualReachability, primMst } from '../lib/density'
import { fclusterDist } from '../lib/hier'
import { BLUE, GOLD, GREEN, MUTED, RED, clusterColor } from '../lib/theme'

const cut = ref(0.75)
const minSize = ref(10)
const k = ref(5)
const X = densityData(7, 45, 28, 12)
const D = distances(X)
const Z = computed(() => mstToLinkage(primMst(mutualReachability(X, k.value, D).mr), X.length))
const maxH = computed(() => Z.value[Z.value.length - 1].height)
const raw = computed(() => fclusterDist(Z.value, cut.value))
/** DBSCAN's reading of a cut: groups below C_min are leftovers, not clusters */
const read = computed(() => {
  const counts = new Map<number, number>()
  raw.value.forEach((l) => counts.set(l, (counts.get(l) ?? 0) + 1))
  const keep = [...counts.entries()].filter(([, c]) => c >= minSize.value).map(([l]) => l)
  const rank = new Map(keep.map((l, i) => [l, i]))
  const labels = raw.value.map((l) => rank.get(l) ?? -1)
  return { labels, kept: keep.length, left: labels.filter((l) => l < 0).length }
})
const colorOf = (id: number, h: number) => {
  if (h > cut.value) return MUTED
  const n = X.length
  let node = id
  while (node >= n) node = Z.value[node - n].a
  const l = read.value.labels[node]
  return l < 0 ? MUTED : clusterColor(l)
}
const three = computed(() =>
  [1.5, 0.75, 0.4].map((e, i) => {
    const r = fclusterDist(Z.value, e)
    const counts = new Map<number, number>()
    r.forEach((l) => counts.set(l, (counts.get(l) ?? 0) + 1))
    const kept = [...counts.values()].filter((c) => c >= minSize.value).length
    const left = [...counts.values()].filter((c) => c < minSize.value).reduce((s, c) => s + c, 0)
    return { eps: e, kept, left, color: [RED, GOLD, GREEN][i] }
  }),
)
</script>

<template>
  <div class="wrap">
    <div class="left">
      <Dendro
        :Z="Z" :color-of="colorOf" :width="0.9" :y-max="maxH * 1.05"
        :cuts="[{ y: cut, color: '#1b1b1b', label: `ε = ${cut.toFixed(2)}` }, ...three.map((t) => ({ y: t.eps, color: t.color, dash: '3,3' }))]"
        y-label="d_mreach at the merge"
        title="single linkage on the transformed space" :title-color="BLUE"
      />
      <div class="note">one dendrogram gives DBSCAN for every ε at once</div>
    </div>
    <ClusterPlot
      :X="X" :labels="read.labels" :point-size="2.6"
      :title="`cut at ε = ${cut.toFixed(2)}: ${read.kept} cluster${read.kept === 1 ? '' : 's'}, ${read.left} left over`"
      :title-color="GREEN"
    />
    <div class="right">
      <div class="head" :style="{ color: BLUE }">a horizontal cut is a DBSCAN run</div>
      <table class="plain narrow">
        <tr><th>ε</th><th>clusters</th><th>left over</th></tr>
        <tr v-for="t in three" :key="t.eps">
          <td :style="{ color: t.color, fontWeight: 600 }">{{ t.eps.toFixed(2) }}</td>
          <td>{{ t.kept }}</td>
          <td>{{ t.left }}</td>
        </tr>
      </table>
      <div class="controls">
        <Knob v-model="cut" :min="0.1" :max="maxH" label="ε, the cut" :color="'#1b1b1b'" />
        <Knob v-model="minSize" :min="2" :max="30" :step="1" label="C<sub>min</sub>" :digits="0" :color="GREEN" />
        <Knob v-model="k" :min="2" :max="15" :step="1" label="MinPts" :digits="0" :color="BLUE" />
      </div>
      <p class="note">No single cut is right everywhere. Low, and the loose
        cluster is mostly left over; high, and the two tight ones have already
        merged. Even the best cut here has to throw away points that belong to
        the loose cluster, because it is only complete at a height where the
        others are gone.</p>
      <p class="note">So pick a different height per branch, which is what the
        condensed tree does.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.05fr 0.8fr 0.8fr; gap: 1.1rem; height: 100%; min-height: 0; }
.left { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.left .note { text-align: center; }
.right { display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; }
.head { font-size: 0.84rem; font-weight: 600; }
.controls { display: flex; flex-direction: column; gap: 0.35rem; }
</style>
