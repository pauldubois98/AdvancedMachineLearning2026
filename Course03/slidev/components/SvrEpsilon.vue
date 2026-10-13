<!-- svr_epsilon: what the width of the tube buys and costs. A wider tube means
     fewer support vectors and a flatter fit. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sineRidge } from '../lib/data'
import { kernel } from '../lib/svm'
import { fitSvr } from '../lib/svr'
import { GOLD, GREEN, MUTED, RED } from '../lib/theme'

const eps = ref(0.35)
const data = sineRidge(70, 6)
const K = kernel({ type: 'rbf', gamma: 0.5 })

const model = computed(() => fitSvr(data.X, data.y, 10, eps.value, K))
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
const tone = computed(() => (eps.value < 0.15 ? RED : eps.value > 0.8 ? GOLD : GREEN))
const label = computed(() => (eps.value < 0.15 ? 'tight' : eps.value > 0.8 ? 'loose' : 'balanced'))

/** how the support set thins out as the tube widens */
const sweep = (() => {
  const pts: [number, number][] = []
  const flat: [number, number][] = []
  for (let i = 0; i <= 28; i++) {
    const e = 0.02 + (1.5 * i) / 28
    const m = fitSvr(data.X, data.y, 10, e, K)
    pts.push([e, m.sv.length])
    let amp = 0
    for (const x of grid) amp = Math.max(amp, Math.abs(m.predict1(x)))
    flat.push([e, amp])
  }
  return { pts, flat }
})()
const nowSv = computed(() => model.value.sv.length)
</script>

<template>
  <div class="wrap">
    <div class="charts">
      <LineChart
        :series="[{ points: curve, color: tone, width: 2.6 }]"
        :ribbons="[{ points: tube, color: tone, alpha: 0.16 }]"
        :dots="data.x.map((x, i) => ({
          x, y: data.y[i],
          color: isSv[i] ? tone : MUTED,
          r: isSv[i] ? 4.5 : 3, hollow: isSv[i],
        }))"
        :x-domain="[-3.3, 3.3]" :y-domain="[-2.6, 2.6]"
        :x-ticks="[-3, -2, -1, 0, 1, 2, 3]" :y-ticks="[-2, -1, 0, 1, 2]"
        x-label="x" :title="`${label} — ε = ${eps.toFixed(2)}`" :title-color="tone"
      />
      <LineChart
        :series="[{ points: sweep.pts, color: GREEN, width: 2.4 }]"
        :vlines="[{ x: eps, color: tone, dash: '' }]"
        :dots="[{ x: eps, y: nowSv, color: tone, r: 5 }]"
        :x-domain="[0, 1.55]" :y-domain="[0, 70]"
        :x-ticks="[0, 0.5, 1, 1.5]" :y-ticks="[0, 20, 40, 60]"
        x-label="ε" y-label="support vectors"
        title="a wider tube needs fewer points to hold it up"
      />
    </div>
    <div class="controls">
      <Knob v-model="eps" :min="0.02" :max="1.5" :step="0.01" label="ε" :color="tone" />
      <Readout
        :items="[
          { label: 'support vectors', value: `${nowSv} / ${data.x.length}`, color: tone },
        ]"
      />
      <p class="note">
        a wider tube means fewer support vectors and a flatter fit — ε buys
        sparsity, and pays for it in resolution.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.charts { display: grid; grid-template-columns: 1.25fr 1fr; gap: 1.6rem; min-height: 0; }
.controls { display: grid; grid-template-columns: 1fr 1fr 1.6fr; gap: 0 1.4rem; align-items: center; }
.note { font-size: 0.76rem; color: v-bind(MUTED); margin: 0; line-height: 1.4; }
</style>
