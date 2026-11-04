<!-- outlier_demo: move one point of 27 (sliders, or click in the right panel)
     and watch the least squares line follow it. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { fitLine, fmt, outlierBase } from '../lib/reg'
import { lineSeg } from '../lib/draw'
import { BLUE, GREEN, RED } from '../lib/theme'

const base = outlierBase(7)
const ox = ref(2.35)
const oy = ref(-5.4)
const clean = fitLine(base.x, base.y)
const dirty = computed(() => fitLine([...base.x, ox.value], [...base.y, oy.value]))
const X = base.x.map((v, i) => [v, base.y[i]] as [number, number])
const dom: [number, number, number, number] = [-3.5, 3.5, -8, 8]
function pick(x: number, y: number) { ox.value = Math.max(-3.4, Math.min(3.4, +x.toFixed(2))); oy.value = Math.max(-8, Math.min(8, +y.toFixed(2))) }
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Plane :X="X" :colors="BLUE" :size="4" :alpha="0.75" :domain="dom" :equal="false" :segments="[lineSeg(clean, -3.5, 3.5, GREEN, 2.4)]"
        title="clean data" :title-color="GREEN" :caption="`β̂₁ = ${fmt(clean[1])}`" />
      <Plane :X="X" :colors="BLUE" :size="4" :alpha="0.75" :domain="dom" :equal="false" pickable @pick="pick"
        :segments="[lineSeg(clean, -3.5, 3.5, GREEN, 1.6, [5, 4]), lineSeg(dirty, -3.5, 3.5, RED, 2.8)]"
        :markers="[{ at: [ox, oy], color: RED, shape: 'dot', size: 7 }]"
        title="one point moved (click to move it)" :title-color="RED" :caption="`β̂₁ = ${fmt(dirty[1])}`" />
    </div>
    <div class="foot">one point out of 27 is enough to tilt the least squares line</div>
    <div class="controls">
      <Knob v-model="ox" :min="-3.4" :max="3.4" :step="0.01" label="its x" :color="RED" />
      <Knob v-model="oy" :min="-8" :max="8" :step="0.01" label="its y" :color="RED" />
    </div>
  </div>
</template>
