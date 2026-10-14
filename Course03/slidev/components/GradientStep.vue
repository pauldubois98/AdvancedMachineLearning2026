<!-- eq_boosting: the residual a tree is fitted to is the negative gradient of
     the loss at the current prediction. Pick a loss, move the prediction, and
     read both off the same curve. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GOLD, GREEN, INK, MUTED, RED } from '../lib/theme'

const F = ref(0.4)
const loss = ref('squared')
const y = 1

const lossAt = (f: number) =>
  loss.value === 'squared' ? 0.5 * (y - f) ** 2
  : loss.value === 'absolute' ? Math.abs(y - f)
  : Math.log(1 + Math.exp(-f)) // log loss of a positive row, in log-odds
const gradAt = (f: number) =>
  loss.value === 'squared' ? f - y
  : loss.value === 'absolute' ? Math.sign(f - y)
  : -1 / (1 + Math.exp(f))

const curve = computed(() => {
  const pts: [number, number][] = []
  for (let i = 0; i <= 200; i++) {
    const f = -3 + (6 * i) / 200
    pts.push([f, lossAt(f)])
  }
  return pts
})
const slope = computed(() => {
  const g = gradAt(F.value)
  const l = lossAt(F.value)
  return [
    [F.value - 1.4, l - 1.4 * g],
    [F.value + 1.4, l + 1.4 * g],
  ] as [number, number][]
})
const residualCurve = computed(() => {
  const pts: [number, number][] = []
  for (let i = 0; i <= 200; i++) {
    const f = -3 + (6 * i) / 200
    pts.push([f, -gradAt(f)])
  }
  return pts
})
const r = computed(() => -gradAt(F.value))
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        :series="[
          { points: curve, color: INK, width: 2.4 },
          { points: slope, color: BLUE, width: 1.8, dash: '6,4' },
        ]"
        :dots="[{ x: F, y: lossAt(F), color: INK, r: 5 }]"
        :vlines="[{ x: F, color: MUTED, dash: '2,3' }]"
        :x-domain="[-3, 3]" :y-domain="[0, 4]" :x-ticks="[-2, 0, 2]" :y-ticks="[0, 2, 4]"
        x-label="current prediction for this row, F(xᵢ)" y-label="the row's loss"
        title="the loss at one row, and its slope there" :title-color="INK"
      />
      <LineChart
        :series="[{ points: residualCurve, color: GOLD, width: 2.4 }]"
        :dots="[{ x: F, y: r, color: GOLD, r: 5 }]"
        :hlines="[{ y: 0, color: INK, dash: '' }]"
        :vlines="[{ x: F, color: MUTED, dash: '2,3' }]"
        :x-domain="[-3, 3]" :y-domain="[-1.6, 2.6]" :x-ticks="[-2, 0, 2]" :y-ticks="[-1, 0, 1, 2]"
        x-label="current prediction for this row, F(xᵢ)" y-label="what the next tree is fitted to"
        title="the pseudo-residual: minus that slope" :title-color="GOLD"
      />
    </div>
    <div class="controls">
      <div class="knobs">
        <Choice
          v-model="loss" label="loss"
          :options="[
            { value: 'squared', label: 'squared', color: BLUE },
            { value: 'absolute', label: 'absolute', color: GOLD },
            { value: 'log', label: 'log loss', color: GREEN },
          ]"
        />
        <Knob v-model="F" :min="-3" :max="3" label="F(xᵢ)" :digits="2" />
        <Readout
          :items="[
            { label: 'slope', value: gradAt(F).toFixed(3), color: BLUE },
            { label: 'pseudo-residual rᵢ', value: r.toFixed(3), color: GOLD },
          ]"
        />
      </div>
      <p class="note">
        this row's true answer is y = 1. With squared loss the pseudo-residual is
        exactly y − F, the plain residual; with the other losses it is not, and that
        is the only thing that changes. The tree is always fitted to r, and added as
        F<sub>m</sub> = F<sub>m−1</sub> + η h<sub>m</sub>.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 1.8rem; align-items: center; flex-wrap: wrap; }
.knobs > :nth-child(2) { min-width: 11rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.5; }
</style>
