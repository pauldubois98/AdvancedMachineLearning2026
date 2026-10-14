<!-- core_distance: the cheapest density estimate there is, the distance to the
     kth neighbour. The slider is k, and the colour map is that distance. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { densityData, distances } from '../lib/data4'
import { coreDistances } from '../lib/density'
import { BLUE, GREEN, INK, RED, density, rgb } from '../lib/theme'

const k = ref(5)
const X = densityData(4)
const D = distances(X)
const core = computed(() => coreDistances(X, k.value, D))
const order = computed(() => core.value.map((v, i) => [v, i] as [number, number]).sort((a, b) => a[0] - b[0]))
const dense = computed(() => order.value[Math.floor(0.2 * order.value.length)][1])
const sparse = computed(() => order.value[Math.floor(0.93 * order.value.length)][1])
const cmax = computed(() => Math.max(...core.value))
const colors = computed(() => core.value.map((v) => rgb(density(v / cmax.value))))
const dom: [number, number, number, number] = [-3.8, 4.4, -3.0, 3.6]
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot
        :X="X" :point-size="2.4" :point-alpha="0.5" :colors="X.map(() => INK)" :domain="dom"
        :circles="[
          { x: X[dense][0], y: X[dense][1], r: core[dense], color: GREEN, alpha: 0.16 },
          { x: X[sparse][0], y: X[sparse][1], r: core[sparse], color: RED, alpha: 0.1 },
        ]"
        :tags="[
          { x: X[dense][0], y: X[dense][1] - core[dense] - 0.36, text: `dense: core = ${core[dense].toFixed(2)}`, color: GREEN, size: 11.5 },
          { x: X[sparse][0], y: X[sparse][1] - core[sparse] - 0.34, text: `sparse: core = ${core[sparse].toFixed(2)}`, color: RED, size: 11.5 },
        ]"
        :title="`core<sub>k</sub>(x<sub>i</sub>) = distance to the ${k}th neighbour`"
      />
      <ClusterPlot
        :X="X" :colors="colors" :point-size="3.4" :domain="dom"
        title="low density &rarr; large core distance" :title-color="BLUE"
      />
      <div class="side">
        <p class="note">Blue is crowded, red is out at sea.</p>
        <p class="note">Raising k smooths the estimate: the circles grow
          everywhere, but much faster where the data is thin, so the contrast
          between dense and sparse is kept.</p>
        <p class="note">This single number is the only density estimate HDBSCAN
          ever makes, and MinPts is the scale at which it is made.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="k" :min="2" :max="25" :step="1" label="MinPts, i.e. k" :digits="0" :color="BLUE" />
      <Readout
        :items="[
          { label: 'smallest core distance', value: core[order[0][1]].toFixed(3), color: GREEN },
          { label: 'largest', value: cmax.toFixed(3), color: RED },
          { label: 'ratio', value: `${(cmax / core[order[0][1]]).toFixed(0)}×` },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr 0.62fr; gap: 1.1rem; min-height: 0; }
.side { align-self: center; }
.side p { margin: 0 0 0.7rem; line-height: 1.5; }
.controls { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 13rem; }
</style>
