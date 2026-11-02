<!-- xgb_split_search: where candidate splits come from, and how one is chosen.
     40 rows, log loss at the first tree, so every g is ±0.5 and every h is
     0.25; the gain is evaluated at every midpoint of every feature. Nothing
     here is clever: it is an exhaustive scan scored by one formula. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { exactScan, gainOf, splitDemo } from '../lib/gbm'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const cut = ref(0.5)
const lambda = ref(1)
const gamma = ref(0.5)
const demo = splitDemo()
const COLORS = [GREEN, MUTED, '#cbd2d9']

const scans = computed(() =>
  [0, 1, 2].map((f) =>
    exactScan(demo.X.map((r) => r[f]), demo.g, demo.h, lambda.value, gamma.value),
  ),
)
const best = computed(() => {
  let out = { f: 0, cut: 0, gain: -Infinity }
  scans.value.forEach((sc, f) =>
    sc.gains.forEach((g, i) => {
      if (g > out.gain) out = { f, cut: sc.cuts[i], gain: g }
    }),
  )
  return out
})
/** the gain of the split the slider is sitting on, in feature 1 */
const here = computed(() => {
  let GL = 0
  let HL = 0
  let G = 0
  let H = 0
  let nL = 0
  for (let i = 0; i < demo.X.length; i++) {
    G += demo.g[i]
    H += demo.h[i]
    if (demo.X[i][0] < cut.value) {
      GL += demo.g[i]
      HL += demo.h[i]
      nL++
    }
  }
  return {
    GL, HL, GR: G - GL, HR: H - HL, nL, nR: demo.X.length - nL,
    gain: gainOf(GL, HL, G - GL, H - HL, lambda.value, gamma.value),
  }
})
const strip = computed(() =>
  demo.X.map((r, i) => ({ x: r[0], y: -0.9 - (i % 5) * 0.13, color: demo.y[i] ? BLUE : RED, r: 3.4 })),
)
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="scans.map((sc, f) => ({
        points: sc.cuts.map((c, i) => [c, sc.gains[i]] as [number, number]),
        color: COLORS[f], width: f === best.f ? 2.6 : 1.5, step: true,
      }))"
      :dots="[
        ...strip,
        { x: best.cut, y: best.gain, color: GREEN, r: 6, marker: 'triangle' },
      ]"
      :vlines="[{ x: cut, color: INK, dash: '' }, { x: best.cut, color: GREEN, dash: '3,3' }]"
      :hlines="[{ y: 0, color: INK, dash: '' }]"
      :x-domain="[0, 1]" :y-domain="[-3.5, 11]"
      :x-ticks="[0, 0.25, 0.5, 0.75, 1]" :y-ticks="[0, 5, 10]"
      x-label="threshold" y-label="gain of that split"
      title="every midpoint of every feature is a candidate; the node takes the best"
      :labels="[
        { x: 0.02, y: -1.85, text: 'the 40 rows: blue y = 1, red y = 0', color: MUTED, size: 11 },
        { x: 0.02, y: -2.9, text: 'a gain below 0 buys less than the leaf costs (γ): that split is not made', color: MUTED, size: 11 },
        { x: 0.02, y: 10.4, text: 'x₁  (the only feature with signal)', color: GREEN, size: 11.5 },
        { x: 0.02, y: 9.4, text: 'x₂, x₃  (noise)', color: MUTED, size: 11.5 },
      ]"
    />
    <div class="controls">
      <div class="knobs">
        <Knob v-model="cut" :min="0.02" :max="0.98" label="split x₁ &lt;" :digits="2" />
        <Knob v-model="lambda" :min="0.01" :max="100" log label="λ" />
        <Knob v-model="gamma" :min="0" :max="6" label="γ" :digits="2" :color="RED" />
      </div>
      <Readout
        :items="[
          { label: 'rows left / right', value: `${here.nL} / ${here.nR}` },
          { label: 'G_L, H_L', value: `${here.GL.toFixed(1)}, ${here.HL.toFixed(2)}` },
          { label: 'G_R, H_R', value: `${here.GR.toFixed(1)}, ${here.HR.toFixed(2)}` },
          { label: 'gain here', value: here.gain.toFixed(2), color: here.gain > 0 ? GREEN : RED },
          { label: 'best split', value: `x${best.f + 1} < ${best.cut.toFixed(2)}, gain ${best.gain.toFixed(2)}`, color: GREEN },
        ]"
      />
      <p class="note">
        γ lifts the whole curve down by a constant: it is the toll for opening a leaf,
        and when no candidate clears it the node stays a leaf. λ flattens the peaks,
        because a split that only helps a handful of rows cannot pay for itself.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.35rem; }
.knobs { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.knobs > * { min-width: 10rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
