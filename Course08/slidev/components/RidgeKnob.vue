<!-- knob_ridge_lambda: the order-M polynomial on Bishop's ten points, with a
     ridge penalty lambda. Right: training and test RMS against lambda, the
     knob that runs backwards (capacity falls as it grows). -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { freshSin, polyFit, polyPoints, ringDots, rms, sci, sinData, truthPoints } from '../lib/c08'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const train = sinData(10, 0)
const test = freshSin(400, 11)
const M = ref(9)
const lam = ref(2e-5)
const LO = 1e-12
const w = computed(() => polyFit(train.x, train.t, M.value, lam.value <= LO * 1.01 ? 0 : lam.value))
const tr = computed(() => rms(w.value, train))
const te = computed(() => rms(w.value, test))
const norm = computed(() => Math.sqrt(w.value.reduce((a, v) => a + v * v, 0)))

const grid = Array.from({ length: 57 }, (_, i) => 10 ** (-12 + i / 4))
const sweep = computed(() => grid.map((l) => {
  const ww = polyFit(train.x, train.t, M.value, l)
  return { l, tr: rms(ww, train), te: rms(ww, test) }
}))
const best = computed(() => sweep.value.reduce((a, b) => (b.te < a.te ? b : a)))
const verdict = computed(() => {
  const r = Math.log10(lam.value) - Math.log10(best.value.l)
  return M.value < 3
    ? { t: 'order too low for any λ to matter', c: RED }
    : r < -3 ? { t: 'too small: overfits', c: RED } : r > 3 ? { t: 'too large: underfits', c: RED } : { t: 'about right', c: GREEN }
})
const lamText = computed(() => (lam.value <= LO * 1.01 ? '0' : sci(lam.value)))
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[{ points: truthPoints, color: MUTED, width: 2, dash: '2 5' }, { points: polyPoints(w), color: verdict.c, width: 2.8 }]"
        :dots="ringDots(train, BLUE)" :x-domain="[-0.03, 1.03]" :y-domain="[-1.8, 1.8]"
        :x-ticks="[0, 0.5, 1]" :y-ticks="[-1, 0, 1]"
        :title="`order M = ${M}, λ = ${lamText}: ${verdict.t}`" :title-color="verdict.c"
      />
      <div class="side">
        <LineChart
          :series="[
            { points: sweep.map((s) => [s.l, s.tr] as [number, number]), color: BLUE, width: 2.4 },
            { points: sweep.map((s) => [s.l, s.te] as [number, number]), color: RED, width: 2.4 },
          ]"
          log-x :x-domain="[1e-12, 100]" :y-domain="[0, 1]" :x-ticks="[1e-12, 1e-8, 1e-4, 1]" :y-ticks="[0, 0.25, 0.5, 0.75, 1]"
          :vlines="[{ x: Math.max(lam, LO), color: INK, dash: '' }, { x: best.l, color: GREEN }]"
          :labels="[{ x: 1e-11, y: 0.92, text: 'test', color: RED }, { x: 1e-11, y: 0.84, text: 'training', color: BLUE }]"
          x-label="λ (log scale)" y-label="RMS error" :unit-height="320"
        />
        <Readout :items="[
          { label: 'train', value: tr.toFixed(2), color: BLUE },
          { label: 'test', value: te.toFixed(2), color: RED },
          { label: '‖w‖', value: sci(norm), color: INK },
        ]" />
      </div>
    </div>
    <div class="note msg">This knob runs backwards: capacity falls as λ grows, so the small-λ end is the overfitted one.</div>
    <div class="controls">
      <Knob v-model="lam" :min="LO" :max="100" log label="penalty λ" :color="verdict.c" />
      <Knob v-model="M" :min="0" :max="9" :step="1" :digits="0" label="order M" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; min-height: 0; }
.side { display: grid; grid-template-rows: 1fr auto; gap: 0.3rem; min-height: 0; }
.msg { text-align: center; color: #6b46c1; }
</style>
