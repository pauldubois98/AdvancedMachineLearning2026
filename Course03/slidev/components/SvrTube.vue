<!-- svr: the same margin idea with a continuous target. Everything inside the
     tube is free; only what sticks out supports the fit. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sineRidge } from '../lib/data'
import { kernel } from '../lib/svm'
import { fitSvr } from '../lib/svr'
import { BLUE, GOLD, GREEN, INK, MUTED, RED } from '../lib/theme'

const eps = ref(0.35)
const C = ref(10)
const gamma = ref(0.5)

const data = sineRidge(70, 6)
const model = computed(() =>
  fitSvr(data.X, data.y, C.value, eps.value, kernel({ type: 'rbf', gamma: gamma.value })),
)

const grid: number[] = []
for (let i = 0; i <= 200; i++) grid.push(-3.2 + (6.4 * i) / 200)
const curve = computed(() => grid.map((x) => [x, model.value.predict1(x)] as [number, number]))
const tube = computed(() =>
  grid.map((x) => {
    const f = model.value.predict1(x)
    return [x, f - eps.value, f + eps.value] as [number, number, number]
  }),
)
const isSv = computed(() => {
  const s = new Set(model.value.sv)
  return data.x.map((_, i) => s.has(i))
})
const dots = computed(() =>
  data.x.map((x, i) => ({
    x, y: data.y[i],
    color: isSv.value[i] ? GREEN : MUTED,
    r: isSv.value[i] ? 4.5 : 3,
    hollow: isSv.value[i],
  })),
)
// the ε-insensitive loss, next to the squared and Huber losses
const resid: number[] = []
for (let i = 0; i <= 200; i++) resid.push(-2.2 + (4.4 * i) / 200)
const lossCurves = computed(() => [
  { points: resid.map((e) => [e, Math.max(0, Math.abs(e) - eps.value)] as [number, number]), color: GREEN, width: 2.8 },
  { points: resid.map((e) => [e, 0.5 * e * e] as [number, number]), color: GOLD, width: 2, dash: '6,4' },
  { points: resid.map((e) => [e, Math.abs(e) <= 1 ? 0.5 * e * e : Math.abs(e) - 0.5] as [number, number]), color: BLUE, width: 2, dash: '2,3' },
])
</script>

<template>
  <div class="wrap">
    <div class="charts">
      <LineChart
        :series="[{ points: curve, color: GREEN, width: 2.6 }]"
        :ribbons="[{ points: tube, color: GREEN, alpha: 0.16 }]"
        :dots="dots"
        :x-domain="[-3.3, 3.3]" :y-domain="[-2.6, 2.6]"
        :x-ticks="[-3, -2, -1, 0, 1, 2, 3]" :y-ticks="[-2, -1, 0, 1, 2]"
        x-label="x" y-label="y"
        title="a tube of width 2ε around the fit" :title-color="GREEN"
      />
      <LineChart
        :series="lossCurves"
        :bands="[{ x0: -eps, x1: eps, color: GREEN, alpha: 0.12 }]"
        :x-domain="[-2.2, 2.2]" :y-domain="[-0.1, 2.3]"
        :x-ticks="[-2, -1, 0, 1, 2]" :y-ticks="[0, 1, 2]"
        x-label="residual e" y-label="loss of one point"
        title="a loss that is flat near zero"
        :labels="[
          { x: 1.2, y: 0.3, text: 'ε-insensitive', color: GREEN, size: 11 },
          { x: 1.0, y: 1.6, text: 'squared', color: GOLD, size: 11 },
          { x: -2.1, y: 1.05, text: 'Huber', color: BLUE, size: 11 },
        ]"
      />
    </div>
    <div class="controls">
      <Knob v-model="eps" :min="0.02" :max="1.5" :step="0.01" label="ε" :color="GREEN" />
      <Knob v-model="C" :min="0.1" :max="1000" log label="C" :color="INK" />
      <Knob v-model="gamma" :min="0.05" :max="10" log label="γ" :color="BLUE" />
      <Readout
        :items="[
          { label: 'support vectors', value: `${model.sv.length} / ${data.x.length}`, color: GREEN },
          { label: 'inside the tube (free)', value: String(data.x.length - model.sv.length), color: MUTED },
        ]"
      />
    </div>
    <p class="note">
      Close enough is free: a point inside the tube costs nothing and gets no
      multiplier. Only the circled points hold the fit up.
    </p>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.charts { display: grid; grid-template-columns: 1.3fr 1fr; gap: 1.6rem; min-height: 0; }
.controls { display: grid; grid-template-columns: repeat(3, 1fr) 1.4fr; gap: 0 1.4rem; align-items: center; }
.note { font-size: 0.76rem; color: v-bind(MUTED); margin: 0; }
</style>
