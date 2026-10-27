<!-- responsibility_picture: where a point sits decides how it is shared. The
     width of the components sets how sharp the hand-over is. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace, mixPdf1, resp1, weighted1 } from '../lib/gmm'
import { curve } from '../lib/charts'
import { COMP, INK, MUTED } from '../lib/theme'

const scale = ref(1)
const x0 = ref(88.6)
const m = computed(() => ({ p: [0.45, 0.55], mu: [86.0, 92.2], sd: [1.5 * scale.value, 1.9 * scale.value] }))
const grid = linspace(80, 99, 500)
const marks = [84.5, 88.6, 89.4, 94.5]
const g0 = computed(() => resp1(x0.value, m.value))
const band = computed(() => grid.map((x) => [x, 0, resp1(x, m.value)[0]] as [number, number, number]))
const band2 = computed(() => grid.map((x) => [x, resp1(x, m.value)[0], 1] as [number, number, number]))
const top = computed(() => Math.max(...grid.map((x) => mixPdf1(x, m.value))) * 1.1)
</script>

<template>
  <div class="wrap">
    <div class="note top">Where a point sits decides how it is shared</div>
    <div class="body">
      <div class="left">
        <LineChart
          :series="[
            ...[0, 1].map((k) => ({ points: curve(grid, (x) => weighted1(x, m)[k]), color: COMP[k], width: 2, dash: '6 4' })),
            { points: curve(grid, (x) => mixPdf1(x, m)), color: INK, width: 2.4 },
          ]"
          :vlines="[...marks.map((v) => ({ x: v, color: MUTED, dash: '2 3' })), { x: x0, color: INK, dash: '5 3' }]"
          :x-domain="[80, 99]" :y-domain="[0, top]" :x-ticks="[]" :y-ticks="[]" y-label="the fit" :unit-height="190"
        />
        <LineChart
          :series="[]" :ribbons="[{ points: band, color: COMP[0], alpha: 0.75 }, { points: band2, color: COMP[1], alpha: 0.75 }]"
          :vlines="[{ x: x0, color: INK, dash: '5 3' }]" :dots="[{ x: x0, y: g0[0], color: INK, r: 4.5 }]"
          :x-domain="[80, 99]" :y-domain="[0, 1]" x-label="length (mm)" y-label="γ_ik" :x-ticks="[82, 86, 90, 94, 98]" :y-ticks="[0, 1]" :unit-height="190"
        />
      </div>
      <div class="side">
        <div class="h">Four points, and yours</div>
        <table class="plain">
          <tr><th>x</th><th :style="{ color: COMP[0] }">γ<sub>i1</sub></th><th :style="{ color: COMP[1] }">γ<sub>i2</sub></th></tr>
          <tr v-for="v in marks" :key="v"><td>{{ v }}</td><td :style="{ color: COMP[0] }">{{ resp1(v, m)[0].toFixed(2) }}</td><td :style="{ color: COMP[1] }">{{ resp1(v, m)[1].toFixed(2) }}</td></tr>
          <tr style="font-weight: 700"><td>{{ x0.toFixed(1) }}</td><td :style="{ color: COMP[0] }">{{ g0[0].toFixed(2) }}</td><td :style="{ color: COMP[1] }">{{ g0[1].toFixed(2) }}</td></tr>
        </table>
        <p class="note" style="margin-top: 0.6rem">On the extremes, the split is certain; in the middle, less so. Wider components hand over more slowly.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="x0" :min="80" :max="99" :step="0.1" label="your point x" :digits="1" :color="INK" />
      <Knob v-model="scale" :min="0.4" :max="2.5" :step="0.01" label="widths × " :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.7fr 1fr; gap: 2rem; min-height: 0; }
.left { display: grid; grid-template-rows: 1.2fr 1fr; gap: 0.2rem; min-height: 0; }
.side { align-self: center; }
</style>
