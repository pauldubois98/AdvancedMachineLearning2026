<!-- dendrogram_cut: one cut, one clustering. The slider is the cut height, and
     the number of clusters is read off, not chosen. -->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { treeData } from '../lib/data4'
import { Method, fclusterDist, linkage } from '../lib/hier'
import { BLUE, GREEN, MUTED, PURPLE, RED, clusterColor } from '../lib/theme'

const cut = ref(9)
const method = ref<Method>('ward')
const X = treeData(3, 260, 0)
const Z = computed(() => linkage(X, method.value))
const maxH = computed(() => Z.value[Z.value.length - 1].height)
const labels = computed(() => fclusterDist(Z.value, cut.value))
const nClusters = computed(() => new Set(labels.value).size)
/** the cut heights at which the number of clusters changes */
const steps = computed(() =>
  Z.value.map((m, r) => [m.height, Z.value.length + 1 - (r + 1)] as [number, number]),
)
// the trees of the four linkages live on completely different scales, so a cut
// in Ward units means nothing under single linkage: rescale it on a switch
watch(method, (now, before) => {
  const scale = linkage(X, now)[X.length - 2].height / linkage(X, before)[X.length - 2].height
  cut.value = Math.min(maxH.value, Math.max(0.2, cut.value * scale))
})

const colorOf = (id: number, h: number) => {
  if (h > cut.value) return MUTED
  const n = X.length
  let node = id
  while (node >= n) node = Z.value[node - n].a
  return clusterColor(labels.value[node])
}
</script>

<template>
  <div class="wrap">
    <div class="left">
      <Dendro
        :Z="Z" :color-of="colorOf" :y-max="maxH * 1.05"
        :cuts="[{ y: cut, color: RED, label: `cut at ${cut.toFixed(1)}` }]"
        :title="`${method} linkage: one cut, one clustering`" :title-color="BLUE"
      />
      <div class="note">lower the line for more clusters, raise it for fewer</div>
    </div>
    <div class="middle">
      <ClusterPlot
        :X="X" :labels="labels" :point-size="2.4"
        :title="`${nClusters} cluster${nClusters > 1 ? 's' : ''}`" :title-color="GREEN"
      />
      <div class="note">the choice of cut replaces the choice of K</div>
    </div>
    <div class="right">
      <LineChart
        :series="[{ points: steps, color: BLUE, width: 2, step: true }]"
        :vlines="[{ x: cut, color: RED, dash: '' }]"
        :dots="[{ x: cut, y: nClusters, color: RED, r: 4 }]"
        :x-domain="[0, maxH * 1.05]" :y-domain="[0, 12]"
        :y-ticks="[0, 4, 8, 12]"
        x-label="cut height" y-label="clusters"
        title="clusters against cut height" :title-color="BLUE"
      />
      <div class="controls">
        <Knob v-model="cut" :min="0.2" :max="maxH" label="cut height" :color="RED" />
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
            { label: 'clusters', value: String(nClusters), color: GREEN },
            { label: 'tallest merge', value: maxH.toFixed(1) },
          ]"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 0.78fr 0.85fr; gap: 1.1rem; height: 100%; min-height: 0; }
.left, .middle { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.left .note, .middle .note { text-align: center; }
.right { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
</style>
