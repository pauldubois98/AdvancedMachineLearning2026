<!-- agglomerative_steps: start with one cluster per point, merge the nearest
     pair, repeat. The slider is the number of merges done so far. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { toyPoints } from '../lib/data4'
import { Method, fclusterMaxclust, linkage } from '../lib/hier'
import { BLUE, GREEN, INK, PURPLE, RED, clusterColor } from '../lib/theme'

const merges = ref(0)
const method = ref<Method>('average')
const { X, names } = toyPoints()
const Z = computed(() => linkage(X, method.value))
const labels = computed(() => fclusterMaxclust(Z.value, X.length - merges.value))
const edges = computed(() =>
  Z.value.slice(0, merges.value).map((m, r) => {
    // draw the merge as the segment between the two group centres
    const mem = membersAt(r)
    return {
      a: centre(mem.a) as [number, number],
      b: centre(mem.b) as [number, number],
      color: clusterColor(labels.value[mem.a[0]]),
      width: 1.6,
      alpha: 0.6,
      dash: [4, 3],
    }
  }),
)
function membersAt(r: number): { a: number[]; b: number[] } {
  const n = X.length
  const leaves: number[][] = Array.from({ length: 2 * n - 1 }, () => [])
  for (let i = 0; i < n; i++) leaves[i] = [i]
  Z.value.forEach((m, j) => { leaves[n + j] = leaves[m.a].concat(leaves[m.b]) })
  return { a: leaves[Z.value[r].a], b: leaves[Z.value[r].b] }
}
function centre(idx: number[]): number[] {
  return [
    idx.reduce((s, i) => s + X[i][0], 0) / idx.length,
    idx.reduce((s, i) => s + X[i][1], 0) / idx.length,
  ]
}
const left = computed(() => X.length - merges.value)
const lastHeight = computed(() => (merges.value ? Z.value[merges.value - 1].height : null))
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :labels="labels" :point-size="6" :edges="edges" :domain="[-0.03, 1.07, 0.02, 1.0]"
      :tags="names.map((nm, i) => ({ x: X[i][0], y: X[i][1] + 0.07, text: nm, color: INK, size: 11 }))"
      :title="merges === 0 ? 'start: 6 clusters' : `after ${merges} merge${merges > 1 ? 's' : ''}: ${left} cluster${left > 1 ? 's' : ''}`"
      :title-color="left === 1 ? GREEN : INK"
    />
    <div class="right">
      <Dendro
        :Z="Z" :leaf-labels="names"
        :color-of="(id) => (Z[id - X.length].height <= (lastHeight ?? -1) + 1e-12 ? GREEN : INK)"
        :cuts="lastHeight !== null ? [{ y: lastHeight, color: GREEN, label: 'merges done' }] : []"
        title="the merges, in order" :title-color="GREEN"
      />
      <div class="controls">
        <Knob v-model="merges" :min="0" :max="5" :step="1" label="merges done" :digits="0" :color="GREEN" />
        <Choice
          v-model="method" label="linkage"
          :options="[
            { value: 'single', label: 'single', color: BLUE },
            { value: 'complete', label: 'complete', color: RED },
            { value: 'average', label: 'average', color: GREEN },
            { value: 'ward', label: 'Ward', color: PURPLE },
          ]"
        />
        <Readout
          :items="[
            { label: 'clusters left', value: String(left) },
            { label: 'this merge cost', value: lastHeight === null ? 'nothing merged yet' : lastHeight.toFixed(3), color: GREEN },
          ]"
        />
      </div>
      <p class="note">Each step takes the cheapest pair under the chosen
        linkage, so n − 1 merges run from n clusters down to one.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 0.95fr 1.1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
</style>
