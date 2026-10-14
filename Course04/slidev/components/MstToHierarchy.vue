<!-- mst_to_hierarchy: removing the edges heaviest first is reading the
     dendrogram from the top. The slider does both at once. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { distances, mstToy } from '../lib/data4'
import { mstToLinkage, primMst } from '../lib/density'
import { BLUE, GOLD, GREEN, INK, MUTED, RED, clusterColor } from '../lib/theme'

const cuts = ref(1)
const { X, names } = mstToy()
const D = distances(X)
const edges = primMst(D).sort((a, b) => b.w - a.w)
const Z = mstToLinkage(primMst(D), X.length)

const removed = computed(() => edges.slice(0, cuts.value))
const kept = computed(() => edges.slice(cuts.value))
const labels = computed(() => {
  const parent = X.map((_, i) => i)
  const find = (i: number): number => (parent[i] === i ? i : (parent[i] = find(parent[i])))
  for (const e of kept.value) parent[find(e.i)] = find(e.j)
  const seen = new Map<number, number>()
  return X.map((_, i) => {
    const r = find(i)
    if (!seen.has(r)) seen.set(r, seen.size)
    return seen.get(r)!
  })
})
const cutLines = computed(() =>
  removed.value.map((e, i) => ({
    y: e.w,
    color: [RED, GOLD, '#6b46c1', MUTED][i % 4],
    label: `cut ${i + 1}: ${e.w.toFixed(2)}`,
  })),
)
const threshold = computed(() => (cuts.value ? removed.value[removed.value.length - 1].w : Infinity))

/** the first leaf under a cluster id, used to pick the colour of a staple */
function firstLeaf(id: number): number {
  const n = X.length
  while (id >= n) id = Z[id - n].a
  return id
}
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :labels="labels" :point-size="7" :domain="[-0.7, 4.4, -0.6, 3.2]"
      :edges="[
        ...kept.map((e) => ({ a: X[e.i] as [number, number], b: X[e.j] as [number, number], color: BLUE, width: 1.8 })),
        ...removed.map((e, i) => ({ a: X[e.i] as [number, number], b: X[e.j] as [number, number], color: [RED, GOLD, '#6b46c1', MUTED][i % 4], width: 2.6, dash: [5, 4] })),
      ]"
      :tags="[
        ...names.map((nm, i) => ({ x: X[i][0], y: X[i][1] + 0.22, text: nm, color: INK, size: 11 })),
        ...edges.map((e, i) => ({
          x: (X[e.i][0] + X[e.j][0]) / 2, y: (X[e.i][1] + X[e.j][1]) / 2 + 0.2,
          text: e.w.toFixed(2), color: i < cuts ? [RED, GOLD, '#6b46c1', MUTED][i % 4] : MUTED, size: 10.5,
        })),
      ]"
      title="a tree with its edge weights: cut the heaviest first" :title-color="INK"
    />
    <div class="right">
      <Dendro
        :Z="Z" :leaf-labels="names" :cuts="cutLines"
        :color-of="(id, h) => (h >= threshold ? MUTED : clusterColor(labels[firstLeaf(id)]))"
        y-label="height of the merge"
        title="the same tree, drawn as a dendrogram" :title-color="GREEN"
      />
      <div class="controls">
        <Knob v-model="cuts" :min="0" :max="6" :step="1" label="heaviest edges cut" :digits="0" :color="RED" />
        <Readout
          :items="[
            { label: 'clusters', value: String(new Set(labels).size), color: GREEN },
            { label: 'sizes', value: [...new Set(labels)].map((l) => labels.filter((v) => v === l).length).sort((a, b) => b - a).join(' / ') },
          ]"
        />
      </div>
      <p class="note">Each cut is one horizontal line, so a dendrogram is the
        whole family of single-linkage clusterings at once. HDBSCAN's trick is
        to stop taking the same line everywhere.</p>
    </div>
  </div>
</template>


<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1.1fr; gap: 1.5rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
</style>
