<!-- more_data: the same order-M polynomial on a growing sample. Ten
     coefficients held down by more points: the affordable order grows with
     the training set. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { freshSin, polyFit, polyPoints, ringDots, rms, sinData, truthPoints } from '../lib/c08'
import { BLUE, GREEN, RED } from '../lib/theme'

const N = ref(15)
const M = ref(9)
const seed = ref(0)
const test = freshSin(400, 99)
const s = computed(() => sinData(N.value, seed.value))
const w = computed(() => polyFit(s.value.x, s.value.t, M.value))
const te = computed(() => rms(w.value, test))
const curve = computed(() => {
  const ns = [10, 12, 15, 20, 30, 50, 75, 100, 150, 200]
  return ns.map((n) => {
    const d = sinData(n, seed.value)
    return [n, rms(polyFit(d.x, d.t, M.value), test)] as [number, number]
  })
})
</script>

<template>
  <div class="wrap">
    <div class="note top">The same order-{{ M }} polynomial, {{ N }} points</div>
    <div class="body">
      <LineChart
        :series="[{ points: truthPoints, color: GREEN, width: 2.4 }, { points: polyPoints(w), color: RED, width: 3 }]"
        :dots="ringDots(s, BLUE, N > 40 ? 2.8 : 4)" :x-domain="[-0.03, 1.03]" :y-domain="[-1.8, 1.8]" :axes="false"
        :title="`N = ${N}: test ${te.toFixed(2)}`"
      />
      <LineChart
        :series="[{ points: curve, color: RED, width: 2.4 }]"
        :dots="[...curve.map(([x, y]) => ({ x, y, color: RED, r: 3.5 })), { x: N, y: Math.min(te, 1.2), color: RED, r: 8, hollow: true }]"
        log-x :x-domain="[9, 220]" :y-domain="[0.15, 1.2]" :x-ticks="[10, 20, 50, 100, 200]" :y-ticks="[0.2, 0.4, 0.6, 0.8, 1.0]"
        :hlines="[{ y: 0.22, color: GREEN, dash: '3 3' }]" :labels="[{ x: 60, y: 0.27, text: 'noise level σ', color: GREEN, size: 12 }]"
        x-label="N (log scale)" y-label="test RMS" title="test error as N grows"
      />
    </div>
    <div class="note msg">Ten coefficients, held down by more points: the affordable order grows with the training set.</div>
    <div class="controls">
      <Knob v-model="N" :min="10" :max="200" :step="1" :digits="0" label="points N" />
      <Knob v-model="M" :min="1" :max="9" :step="1" :digits="0" label="order M" />
      <Knob v-model="seed" :min="0" :max="30" :step="1" :digits="0" label="sample" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top, .msg { text-align: center; }
.body { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; min-height: 0; }
</style>
