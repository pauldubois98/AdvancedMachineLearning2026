<!-- why_not_least_squares: a straight line through 0/1 labels leaves [0, 1],
     and a few far, very obvious points drag its cut. The sigmoid barely moves. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve } from '../lib/hist'
import { fitLine, fmt, logisticIrls, sigmoid } from '../lib/reg'
import { BLUE, GOLD, GREEN, GRID, RED } from '../lib/theme'

const rng = new Rng(17)
const x0 = [...Array.from({ length: 25 }, () => rng.normal(-1.5, 1.1)), ...Array.from({ length: 25 }, () => rng.normal(1.5, 1.1))]
const y0 = [...Array(25).fill(0), ...Array(25).fill(1)] as number[]
const xf = ref(9)
const nf = ref(5)
const far = computed(() => Array.from({ length: nf.value }, (_, i) => xf.value + 0.35 * i))
const xs = computed(() => [...x0, ...far.value])
const ys = computed(() => [...y0, ...far.value.map(() => 1)])
const ls = computed(() => fitLine(xs.value, ys.value))
const lg = computed(() => logisticIrls(xs.value.map((v) => [v]), ys.value, 10).at(-1)!)
const cutLS = computed(() => (0.5 - ls.value[0]) / ls.value[1])
const cutLG = computed(() => -lg.value[0] / lg.value[1])
const err = (cut: number) => x0.reduce((s, v, i) => s + ((v > cut ? 1 : 0) !== y0[i] ? 1 : 0), 0)
const dots = computed(() => xs.value.map((v, i) => ({ x: v, y: ys.value[i], color: i >= 50 ? GOLD : ys.value[i] ? RED : BLUE, r: i >= 50 ? 5 : 3.5 })))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <LineChart :series="[{ points: [[-4, ls[0] - 4 * ls[1]], [16, ls[0] + 16 * ls[1]]], color: RED, width: 2.6 }]" :dots="dots"
        :hlines="[{ y: 0.5, color: GRID, dash: '5,4' }]" :vlines="[{ x: cutLS, color: RED, dash: '2,3' }]" :x-domain="[-4, 16]" :y-domain="[-0.45, 1.45]" :y-ticks="[0, 0.5, 1]"
        title="a straight line through 0 / 1 labels" :title-color="RED" />
      <LineChart :series="[{ points: curve((v) => sigmoid(lg[0] + lg[1] * v), -4, 16, 400), color: GREEN, width: 2.6 }]" :dots="dots"
        :hlines="[{ y: 0.5, color: GRID, dash: '5,4' }]" :vlines="[{ x: cutLG, color: GREEN, dash: '2,3' }]" :x-domain="[-4, 16]" :y-domain="[-0.45, 1.45]" :y-ticks="[0, 0.5, 1]"
        title="logistic regression" :title-color="GREEN" />
    </div>
    <div class="foot">least squares: predictions below 0 and above 1, cut at x = <b :style="{ color: RED }">{{ fmt(cutLS) }}</b>, {{ err(cutLS) }} of the 50 ordinary points misclassified. Logistic: predictions between 0 and 1, cut at <b :style="{ color: GREEN }">{{ fmt(cutLG) }}</b>, {{ err(cutLG) }} misclassified.</div>
    <div class="controls">
      <Knob v-model="xf" :min="2" :max="14" :step="0.05" label="far points at x =" :color="GOLD" />
      <Knob v-model="nf" :min="0" :max="10" :step="1" :digits="0" label="how many" :color="GOLD" />
    </div>
  </div>
</template>
