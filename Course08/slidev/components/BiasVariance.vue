<!-- bias_variance: twenty samples, one order-M fit per sample. The spread of
     the fits is the variance; the distance of their mean to the truth is the
     bias. Right: both measured for every order. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace, polyEval, polyFit, polyPoints, sinData, truth, truthPoints } from '../lib/c08'
import { GOLD, GREEN, INK, PURPLE, RED } from '../lib/theme'

const M = ref(3)
const N = ref(10)
const S = 20
const XS = linspace(0, 1, 120)
function decompose(m: number, n: number) {
  const fits = Array.from({ length: S }, (_, s) => { const d = sinData(n, 300 + s); return polyFit(d.x, d.t, m) })
  let b2 = 0, v = 0
  const meanCurve: [number, number][] = XS.map((x) => {
    const ys = fits.map((w) => polyEval(w, x))
    const mu = ys.reduce((a, b) => a + b, 0) / S
    b2 += (mu - truth(x)) ** 2
    v += ys.reduce((a, y) => a + (y - mu) ** 2, 0) / S
    return [x, mu]
  })
  return { fits, meanCurve, bias2: b2 / XS.length, variance: v / XS.length }
}
const cur = computed(() => decompose(M.value, N.value))
const table = computed(() => Array.from({ length: 10 }, (_, m) => {
  const d = decompose(m, N.value)
  return { m, b: d.bias2, v: d.variance }
}))
const color = computed(() => (M.value <= 2 || M.value >= 7 ? RED : GREEN))
const ymax = 0.5
</script>

<template>
  <div class="wrap">
    <div class="note top">Twenty different samples of {{ N }} points</div>
    <div class="body">
      <LineChart
        :series="[
          ...cur.fits.map((w) => ({ points: polyPoints(w, 160), color: color, width: 1.2, opacity: 0.35 })),
          { points: cur.meanCurve, color: color, width: 3.4 },
          { points: truthPoints, color: INK, width: 2.4, dash: '6 4' },
        ]"
        :x-domain="[0, 1]" :y-domain="[-1.8, 1.8]" :axes="false"
        :title="`M = ${M}`" :title-color="color"
      />
      <div class="side">
        <LineChart
          :series="[
            { points: table.map((r) => [r.m, Math.min(r.b, ymax * 2)] as [number, number]), color: PURPLE, width: 2.4 },
            { points: table.map((r) => [r.m, Math.min(r.v, ymax * 2)] as [number, number]), color: GOLD, width: 2.4 },
          ]"
          :dots="[{ x: M, y: Math.min(cur.bias2, ymax), color: PURPLE, r: 6 }, { x: M, y: Math.min(cur.variance, ymax), color: GOLD, r: 6 }]"
          :vlines="[{ x: M, color: color, dash: '' }]"
          :labels="[{ x: 0.3, y: ymax * 0.9, text: 'bias²', color: PURPLE }, { x: 6.5, y: ymax * 0.9, text: 'variance', color: GOLD }]"
          :x-domain="[-0.3, 9.3]" :y-domain="[0, ymax]" :x-ticks="[0, 3, 6, 9]" :y-ticks="[0, 0.25, 0.5]"
          x-label="M" title="measured over the twenty" :unit-height="260"
        />
        <Readout :items="[
          { label: 'bias²', value: cur.bias2.toFixed(3), color: PURPLE },
          { label: 'variance', value: cur.variance.toFixed(3), color: GOLD },
        ]" />
      </div>
    </div>
    <div class="controls">
      <Knob v-model="M" :min="0" :max="9" :step="1" :digits="0" label="order M" :color="color" />
      <Knob v-model="N" :min="10" :max="100" :step="1" :digits="0" label="points per sample N" />
      <span class="note">thin: one fit per sample; thick: their mean; dashed: the truth</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.3rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; min-height: 0; }
.side { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
</style>
