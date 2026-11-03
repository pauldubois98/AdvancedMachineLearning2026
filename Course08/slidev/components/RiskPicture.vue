<!-- risk_picture: many samples of N points, every order fitted to each. Thin
     lines are single samples, thick ones their means: the expected training
     error only falls, the expected test error is U-shaped. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmin, freshSin, mse, polyFit, sinData } from '../lib/c08'
import { BLUE, GREEN, RED } from '../lib/theme'

const S = ref(40)
const N = ref(10)
const noise = ref(0.22)
const MS = Array.from({ length: 10 }, (_, m) => m)
const test = computed(() => freshSin(400, 99, noise.value))
const runs = computed(() => Array.from({ length: S.value }, (_, s) => {
  const d = sinData(N.value, 200 + s, noise.value)
  return MS.map((m) => { const w = polyFit(d.x, d.t, m); return { tr: mse(w, d), te: mse(w, test.value) } })
}))
const avg = (k: 'tr' | 'te') => MS.map((m) => [m, runs.value.reduce((a, r) => a + r[m][k], 0) / runs.value.length] as [number, number])
const tr = computed(() => avg('tr'))
const te = computed(() => avg('te'))
const best = computed(() => argmin(te.value.map((p) => p[1])))
const YMAX = 1
const clip = (v: number) => Math.min(v, YMAX * 3)
</script>

<template>
  <div class="wrap">
    <div class="note top">{{ S }} samples of {{ N }} points, every order fitted to each</div>
    <LineChart
      :series="[
        ...runs.map((r) => ({ points: MS.map((m) => [m, clip(r[m].tr)] as [number, number]), color: BLUE, width: 0.9, opacity: 0.22 })),
        ...runs.map((r) => ({ points: MS.map((m) => [m, clip(r[m].te)] as [number, number]), color: RED, width: 0.9, opacity: 0.22 })),
        { points: tr.map(([x, y]) => [x, clip(y)] as [number, number]), color: BLUE, width: 3.6 },
        { points: te.map(([x, y]) => [x, clip(y)] as [number, number]), color: RED, width: 3.6 },
      ]"
      :dots="[{ x: best, y: te[best][1], color: GREEN, r: 11, hollow: true }]"
      :labels="[{ x: 5.4, y: 0.9, text: 'expected test error', color: RED, size: 14 }, { x: 5.4, y: 0.8, text: 'expected training error', color: BLUE, size: 14 }]"
      :x-domain="[-0.3, 9.3]" :y-domain="[0, YMAX]" :x-ticks="[0, 2, 4, 6, 8]" :y-ticks="[0, 0.2, 0.4, 0.6, 0.8, 1]"
      x-label="model complexity M" y-label="squared error" :unit-height="280"
    />
    <div class="msg">High bias, low variance on the left. &nbsp; Low bias, high variance on the right.</div>
    <div class="controls">
      <Knob v-model="S" :min="1" :max="100" :step="1" :digits="0" label="samples" />
      <Knob v-model="N" :min="10" :max="80" :step="1" :digits="0" label="points per sample N" />
      <Knob v-model="noise" :min="0.02" :max="0.6" :step="0.01" label="noise σ" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.3rem; height: 100%; min-height: 0; }
.top, .msg { text-align: center; }
.msg { color: #6b46c1; font-size: 0.85rem; }
</style>
