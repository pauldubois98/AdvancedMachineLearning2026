<!-- tuning_delta: Huber's fit as δ moves. Small δ is close to least absolute
     deviations; large δ walks back to least squares and to the outliers. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { fitLine, fmt, irls, outlierBase, wHuber } from '../lib/reg'
import { lineSeg } from '../lib/draw'
import { BLUE, INK, MUTED, PURPLE, RED } from '../lib/theme'

const base = outlierBase(7)
const X = [...base.x, 2.35, -2.2]
const far = ref(1)
const Y = computed(() => [...base.y, -5.4 * far.value, 5.0 * far.value])
const d = ref(1.345)
const huber = (dd: number) => irls(X, Y.value, (e) => wHuber(e, dd), 20).at(-1)!.beta
const cur = computed(() => huber(d.value))
const ls = computed(() => fitLine(X, Y.value))
const DS = Array.from({ length: 60 }, (_, i) => 0.1 + (11.9 * i) / 59)
const path = computed(() => DS.map((dd) => [dd, huber(dd)[1]] as [number, number]))
const ylo = computed(() => Math.min(...path.value.map((p) => p[1]), 1.1) - 0.05)
const yhi = computed(() => Math.max(...path.value.map((p) => p[1]), 1.1) + 0.05)
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Plane :X="X.map((v, i) => [v, Y[i]])" :colors="MUTED" :size="3.5" :domain="[-3.5, 3.5, -8, 8]" :equal="false"
        :segments="[lineSeg(ls, -3.5, 3.5, RED, 1.8, [6, 4]), lineSeg(cur, -3.5, 3.5, PURPLE, 2.6)]"
        title="the data and the Huber fit" :caption="`dashed: least squares; purple: Huber with δ = ${d.toFixed(3)}, β̂₁ = ${fmt(cur[1])}`" />
      <LineChart :series="[{ points: path, color: PURPLE, width: 2.6 }]" :hlines="[{ y: 1.1, color: INK, dash: '6,4' }, { y: ls[1], color: RED, dash: '2,3' }]"
        :vlines="[{ x: 1.345, color: BLUE }]" :dots="[{ x: d, y: cur[1], color: PURPLE, r: 6 }]"
        :labels="[{ x: 11.8, y: 1.1 + (yhi - ylo) * 0.03, text: 'the truth', color: INK, anchor: 'end', size: 12 }, { x: 11.8, y: ls[1] + (yhi - ylo) * 0.03, text: 'least squares', color: RED, anchor: 'end', size: 12 }, { x: 1.5, y: ylo + (yhi - ylo) * 0.05, text: '1.345', color: BLUE, size: 12 }]"
        :x-domain="[0, 12]" :y-domain="[ylo, yhi]" :x-ticks="[0, 2, 4, 6, 8, 10, 12]" :y-ticks="[]" x-label="Huber's δ" y-label="β̂₁" title="the slope against δ" />
    </div>
    <div class="foot">large δ walks back to least squares; δ is measured in units of the residual scale (σ̂ = 1.4826 MAD)</div>
    <div class="controls">
      <Knob v-model="d" :min="0.1" :max="12" :step="0.005" :digits="3" label="δ" :color="PURPLE" />
      <Knob v-model="far" :min="0" :max="1.6" :step="0.01" label="how far the outliers are" :color="RED" />
    </div>
  </div>
</template>
