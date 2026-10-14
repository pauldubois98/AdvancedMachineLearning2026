<!-- exclusive_vs_overlapping: one label per point, or a shared zone. The
     slider sets how wide the "belongs to both" band is. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { BLUE, GREEN, RED, GRID } from '../lib/theme'

const band = ref(0.45)
const centres: [number, number][] = [[-0.95, 0], [0.95, 0]]
const X = (() => {
  const rng = new Rng(11)
  const out: number[][] = []
  for (const c of centres) for (let i = 0; i < 70; i++) out.push([rng.normal(c[0], 0.72), rng.normal(c[1], 0.72)])
  return out
})()

const dists = X.map((p) => centres.map((c) => Math.hypot(p[0] - c[0], p[1] - c[1])))
const hard = dists.map((d) => (d[0] <= d[1] ? 0 : 1))
const shared = computed(() => dists.map((d) => Math.abs(d[0] - d[1]) < band.value))
const colors = computed(() =>
  X.map((_, i) => (shared.value[i] ? '#6b46c1' : hard[i] === 0 ? BLUE : RED)),
)
const nShared = computed(() => shared.value.filter(Boolean).length)
const dom: [number, number, number, number] = [-3.2, 3.2, -2.3, 2.3]
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot
        :X="X" :labels="hard" :domain="dom" :point-size="3"
        :edges="[{ a: [0, -2.2], b: [0, 2.2], color: GRID, width: 1.6, dash: [5, 4] }]"
        title="exclusive" :title-color="BLUE"
      />
      <ClusterPlot
        :X="X" :colors="colors" :domain="dom" :point-size="3"
        :ellipses="centres.map((c) => ({ x: c[0], y: c[1], rx: 1.45 + band / 2, ry: 1.2 + band / 2, color: GRID }))"
        title="overlapping" :title-color="GREEN"
      />
      <div class="side">
        <p><em class="hl-blue">exclusive</em><br />
          <span class="note">one point, one cluster: a sharp border</span></p>
        <p><em class="hl-green">overlapping</em><br />
          <span class="note">a point may belong to several clusters at once</span></p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="band" :min="0" :max="1.4" label="width of the shared zone" :color="'#6b46c1'" />
      <Readout
        :items="[
          { label: 'in both clusters', value: `${nShared} of ${X.length}`, color: '#6b46c1' },
          { label: 'in exactly one', value: String(X.length - nShared), color: BLUE },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr 0.8fr; gap: 1rem; min-height: 0; }
.side { font-size: 0.85rem; align-self: center; }
.side p { margin: 0 0 0.8rem; line-height: 1.5; }
.controls { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 16rem; }
</style>
