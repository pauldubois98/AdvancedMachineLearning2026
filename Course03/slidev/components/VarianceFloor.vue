<!-- forest_variance: averaging buys a floor, not zero, and the floor is rho. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { effectiveTrees, varianceOfAverage } from '../lib/forest'
import { BLUE, GOLD, GREEN, MUTED, RED } from '../lib/theme'

const M = ref(100)
const rho = ref(0.2)
const RHOS = [
  { r: 0, c: GREEN },
  { r: 0.2, c: BLUE },
  { r: 0.5, c: GOLD },
  { r: 0.9, c: RED },
]
const Ms: number[] = []
for (let i = 0; i <= 120; i++) Ms.push(10 ** ((i / 120) * 3.9))

const curves = computed(() =>
  RHOS.map(({ r, c }) => ({
    points: Ms.map((m) => [m, varianceOfAverage(m, r)] as [number, number]),
    color: c, width: 2,
  })),
)
const floors = computed(() => RHOS.filter((x) => x.r > 0).map(({ r, c }) => ({ y: r, color: c, dash: '2,3' })))
const effCurves = computed(() =>
  RHOS.map(({ r, c }) => ({
    points: Ms.map((m) => [m, Math.max(1, effectiveTrees(m, r))] as [number, number]),
    color: c, width: 2,
  })),
)
const live = computed(() => ({
  v: varianceOfAverage(Math.round(M.value), rho.value),
  eff: effectiveTrees(Math.round(M.value), rho.value),
}))
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        :series="[...curves, { points: Ms.map((m) => [m, varianceOfAverage(m, rho)] as [number, number]), color: '#1b1b1b', width: 2.6 }]"
        :hlines="floors"
        :vlines="[{ x: M, color: '#1b1b1b', dash: '' }]"
        :dots="[{ x: M, y: live.v, color: '#1b1b1b', r: 5 }]"
        :x-domain="[1, 8000]" :y-domain="[0, 1.05]" log-x
        :x-ticks="[1, 10, 100, 1000]" :y-ticks="[0, 0.5, 1]"
        x-label="number of trees M" y-label="variance of the average, in units of σ²"
        title="it stops falling at the floor ρσ²"
        :labels="RHOS.map((x, i) => ({ x: 2000, y: x.r + 0.04, text: `ρ = ${x.r}`, color: x.c, size: 11 }))"
      />
      <LineChart
        :series="[...effCurves, { points: Ms.map((m) => [m, Math.max(1, effectiveTrees(m, rho))] as [number, number]), color: '#1b1b1b', width: 2.6 }]"
        :vlines="[{ x: M, color: '#1b1b1b', dash: '' }]"
        :dots="[{ x: M, y: live.eff, color: '#1b1b1b', r: 5 }]"
        :x-domain="[1, 8000]" :y-domain="[1, 3000]" log-x log-y
        :x-ticks="[1, 10, 100, 1000]" :y-ticks="[1, 10, 100, 1000]"
        x-label="number of trees M" y-label="trees that count: M / (1 + (M−1)ρ)"
        title="a thousand correlated trees are worth a handful"
      />
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="M" :min="1" :max="4000" :step="1" log label="trees, M" :digits="0" />
        <Knob v-model="rho" :min="0" :max="0.95" label="correlation, ρ" :digits="2" :color="RED" />
        <Readout
          :items="[
            { label: 'variance of the average', value: live.v.toFixed(3) },
            { label: 'the floor it is heading for', value: rho.toFixed(3), color: RED },
            { label: 'worth this many independent trees', value: live.eff.toFixed(1), color: GREEN },
          ]"
        />
      </div>
      <p class="note">
        the black curve is the ρ on the slider; the coloured ones are fixed values.
        Past a few hundred trees, more trees buy nothing: what is left is the floor.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 1.8rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child, .knobs > :nth-child(2) { min-width: 11rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
