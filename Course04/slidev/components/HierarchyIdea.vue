<!-- hierarchy_idea: six points, their nested groups, and the dendrogram that
     records them. The linkage buttons change the tree, not the points. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { toyPoints } from '../lib/data4'
import { Method, fclusterMaxclust, linkage } from '../lib/hier'
import { BLUE, GREEN, INK, PURPLE, RED, clusterColor } from '../lib/theme'

const method = ref<Method>('average')
const k = ref(3)
const { X, names } = toyPoints()

const Z = computed(() => linkage(X, method.value))
const labels = computed(() => fclusterMaxclust(Z.value, k.value))
/** a dashed ring round each group, from the spread of its members */
const rings = computed(() => {
  const out: { x: number; y: number; rx: number; ry: number; color: string }[] = []
  const groups = new Map<number, number[]>()
  labels.value.forEach((l, i) => {
    if (!groups.has(l)) groups.set(l, [])
    groups.get(l)!.push(i)
  })
  for (const [l, idx] of groups) {
    const cx = idx.reduce((s, i) => s + X[i][0], 0) / idx.length
    const cy = idx.reduce((s, i) => s + X[i][1], 0) / idx.length
    const rx = Math.max(...idx.map((i) => Math.abs(X[i][0] - cx))) + 0.11
    const ry = Math.max(...idx.map((i) => Math.abs(X[i][1] - cy))) + 0.11
    out.push({ x: cx, y: cy, rx, ry, color: clusterColor(l) })
  }
  return out
})
const cutHeight = computed(() => {
  const Zs = Z.value
  const n = Zs.length + 1
  // the cut that leaves exactly k clusters sits between two merge heights
  const take = n - k.value
  if (take <= 0) return 0
  const lo = Zs[take - 1].height
  const hi = take < Zs.length ? Zs[take].height : lo * 1.25
  return (lo + hi) / 2
})
const colorOf = (id: number) => {
  const n = X.length
  // a staple is coloured when the whole merge sits under the cut
  return Z.value[id - n].height <= cutHeight.value ? clusterColor(labels.value[memberOf(id)]) : INK
}
function memberOf(id: number): number {
  const n = X.length
  while (id >= n) id = Z.value[id - n].a
  return id
}
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :labels="labels" :point-size="5.5" :ellipses="rings" :domain="[-0.06, 1.1, 0.0, 1.0]"
      :tags="names.map((nm, i) => ({ x: X[i][0] + 0.055, y: X[i][1], text: nm, color: INK, size: 12, anchor: 'left' as CanvasTextAlign }))"
      title="nested groups: a cluster is the union of its children" :title-color="INK"
    />
    <div class="right">
      <Dendro
        :Z="Z" :leaf-labels="names" :color-of="colorOf"
        :cuts="[{ y: cutHeight, color: RED, label: `${k} clusters` }]"
        title="the dendrogram" :title-color="GREEN"
      />
      <div class="controls">
        <Choice
          v-model="method" label="linkage"
          :options="[
            { value: 'single', label: 'single', color: BLUE },
            { value: 'complete', label: 'complete', color: RED },
            { value: 'average', label: 'average', color: GREEN },
            { value: 'ward', label: 'Ward', color: PURPLE },
          ]"
        />
        <Knob v-model="k" :min="1" :max="6" :step="1" label="clusters kept" :digits="0" :color="RED" />
        <Readout
          :items="[
            { label: 'merge heights', value: Z.map((m) => m.height.toFixed(2)).join(', ') },
            { label: 'last merge', value: Z[Z.length - 1].height.toFixed(2) },
          ]"
        />
      </div>
      <p class="note">Branch height is how far apart the two halves were, so
        the tree carries every K at once: pick the height instead of the K.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 0.95fr 1.1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
</style>
