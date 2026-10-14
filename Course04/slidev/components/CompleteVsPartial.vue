<!-- complete_vs_partial: every point assigned, or only the ones that fit. The
     slider is the radius beyond which a point is left out. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { BLUE, GREEN, MUTED } from '../lib/theme'

const radius = ref(1.0)
const centres = [[-1.4, -0.5], [1.3, -0.3], [0.0, 1.5]]
const X = (() => {
  const rng = new Rng(17)
  const out: number[][] = []
  for (const c of centres) for (let i = 0; i < 55; i++) out.push([rng.normal(c[0], 0.42), rng.normal(c[1], 0.42)])
  for (let i = 0; i < 22; i++) out.push([rng.uniform(-3, 3), rng.uniform(-2, 2.8)])
  return out
})()
const near = X.map((p) => {
  let best = 0
  let bd = Infinity
  centres.forEach((c, k) => {
    const d = Math.hypot(p[0] - c[0], p[1] - c[1])
    if (d < bd) { bd = d; best = k }
  })
  return { k: best, d: bd }
})
const full = near.map((n) => n.k)
const partial = computed(() => near.map((n) => (n.d < radius.value ? n.k : -1)))
const left = computed(() => partial.value.filter((l) => l < 0).length)
const dom: [number, number, number, number] = [-3.8, 3.8, -2.8, 3.6]
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot :X="X" :labels="full" :domain="dom" :point-size="2.9" title="complete" :title-color="BLUE" />
      <ClusterPlot
        :X="X" :labels="partial" :domain="dom" :point-size="2.9"
        :circles="centres.map((c) => ({ x: c[0], y: c[1], r: radius, color: GREEN, alpha: 0.06, dash: [5, 4] }))"
        title="partial" :title-color="GREEN"
      />
      <div class="side">
        <p><em class="hl-blue">complete</em><br />
          <span class="note">every point is assigned, whether it fits or not</span></p>
        <p><em class="hl-green">partial</em><br />
          <span class="note">points that fit nowhere stay unassigned</span></p>
        <p class="note">DBSCAN and HDBSCAN are partial by construction: their
          leftovers are called noise.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="radius" :min="0.3" :max="3" label="how near a point must sit" :color="GREEN" />
      <Readout
        :items="[
          { label: 'assigned, complete', value: `${X.length} of ${X.length}`, color: BLUE },
          { label: 'assigned, partial', value: `${X.length - left} of ${X.length}`, color: GREEN },
          { label: 'left out', value: String(left), color: MUTED },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr 0.8fr; gap: 1rem; min-height: 0; }
.side { font-size: 0.85rem; align-self: center; }
.side p { margin: 0 0 0.7rem; line-height: 1.5; }
.controls { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 16rem; }
</style>
