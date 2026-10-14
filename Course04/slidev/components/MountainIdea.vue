<!-- mountain_idea: every point raises the ground around it, and where points
     are crowded the hills add up. sigma is how wide one point's hill is. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { gridOver, mountainData } from '../lib/data4'
import { mountainField, surface } from '../lib/mountain'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const sigma = ref(0.45)
const step = ref(0.22)
const X = mountainData()

const grid = computed(() => gridOver(X, step.value, 0.9))
const M = computed(() => mountainField(grid.value.V, X, sigma.value))
const top = computed(() => {
  let best = 0
  for (let i = 1; i < M.value.length; i++) if (M.value[i] > M.value[best]) best = i
  return { v: grid.value.V[best], h: M.value[best] }
})
const field = computed(() => ({
  f: surface(X, sigma.value),
  vmax: top.value.h,
  levels: 14,
}))
const dom: [number, number, number, number] = [-3.4, 3.3, -2.6, 3.2]
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot
        :X="X" :grid="grid.V" :point-size="2.8" :point-alpha="0.75" :domain="dom"
        :colors="X.map(() => INK)"
        title="grid over the data" :title-color="INK"
      />
      <ClusterPlot
        :X="X" :field="field" :point-size="2" :point-alpha="0.45" :domain="dom"
        :colors="X.map(() => INK)"
        :crosses="[{ x: top.v[0], y: top.v[1], color: RED }]"
        title="build mountains" :title-color="BLUE"
      />
      <div class="side">
        <p><span class="note">Every data point raises the ground around it.</span></p>
        <p><span class="note">Where points are crowded, the hills add up.</span></p>
        <p><em class="hl-green">Take the summit, flatten it, repeat.</em></p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="sigma" :min="0.12" :max="1.5" label="σ, width of one hill" :color="BLUE" />
      <Knob v-model="step" :min="0.12" :max="0.6" label="grid step" :color="MUTED" />
      <Readout
        :items="[
          { label: 'candidate centres', value: `${grid.nx} × ${grid.ny} = ${grid.V.length}` },
          { label: 'highest peak', value: top.h.toFixed(1), color: RED },
          { label: 'at', value: `(${top.v[0].toFixed(2)}, ${top.v[1].toFixed(2)})`, color: RED },
        ]"
      />
      <span class="note">the first centre is the highest node, so a coarser
        grid moves it</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr 0.68fr; gap: 1rem; min-height: 0; }
.side { align-self: center; font-size: 0.88rem; }
.side p { margin: 0 0 0.9rem; line-height: 1.5; }
.controls { display: flex; gap: 1.3rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 12rem; }
</style>
