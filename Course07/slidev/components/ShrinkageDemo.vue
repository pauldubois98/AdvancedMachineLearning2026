<!-- shrinkage: eta takes a fraction of each tree's correction. Both panels
     have the same number of trees, so the comparison is what M buys you. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sine1d } from '../lib/databis'
import { fitBooster } from '../lib/boost'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const eta = ref(0.1)
const M = ref(60)
const MAX = 120
const data = sine1d(70, 0.22, 0)
const grid: number[] = []
for (let i = 0; i <= 300; i++) grid.push(i / 300)
const truth = grid.map((x) => [x, Math.sin(2 * Math.PI * x)] as [number, number])

function fit(e: number) {
  return fitBooster(data.X, data.y, { nTrees: MAX, eta: e, maxDepth: 2, loss: 'squared', seed: 0 })
}
const whole = computed(() => fit(1))
const shrunk = computed(() => fit(eta.value))
const STAGES = [1, 3, 10, 60]
const SHADES = ['#cfe0f0', '#8fb8de', '#4a86c6', BLUE]

function curves(model: ReturnType<typeof fit>) {
  return STAGES.filter((s) => s <= M.value).map((s, i) => ({
    points: grid.map((x) => [x, model.raw([x], s)] as [number, number]),
    color: SHADES[i], width: 2.2,
  }))
}
function err(model: ReturnType<typeof fit>) {
  let s = 0
  for (const x of grid) s += (model.raw([x], Math.round(M.value)) - Math.sin(2 * Math.PI * x)) ** 2
  return s / grid.length
}
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        :series="[{ points: truth, color: MUTED, width: 1.4, dash: '6,4' }, ...curves(whole)]"
        :dots="data.x.map((x, i) => ({ x, y: data.y[i], color: MUTED, r: 2.6 }))"
        :x-domain="[0, 1]" :y-domain="[-1.9, 2.2]" :x-ticks="[0, 0.5, 1]" :y-ticks="[-1, 0, 1]"
        x-label="x" title="η = 1: add each tree whole" :title-color="RED"
      />
      <LineChart
        :series="[{ points: truth, color: MUTED, width: 1.4, dash: '6,4' }, ...curves(shrunk)]"
        :dots="data.x.map((x, i) => ({ x, y: data.y[i], color: MUTED, r: 2.6 }))"
        :x-domain="[0, 1]" :y-domain="[-1.9, 2.2]" :x-ticks="[0, 0.5, 1]" :y-ticks="[-1, 0, 1]"
        x-label="x" :title="`η = ${eta.toFixed(2)}: add a fraction of it`" :title-color="GREEN"
      />
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="eta" :min="0.02" :max="1" log label="learning rate η" :color="GREEN" />
        <Knob v-model="M" :min="1" :max="MAX" :step="1" label="trees" :digits="0" />
        <Readout
          :items="[
            { label: 'error vs the true curve, η = 1', value: err(whole).toFixed(4), color: RED },
            { label: `η = ${eta.toFixed(2)}`, value: err(shrunk).toFixed(4), color: GREEN },
          ]"
        />
      </div>
      <p class="note">
        F<sub>m</sub> = F<sub>m−1</sub> + η h<sub>m</sub>: η shrinks every correction.
        At η = 1 the fit lurches after every tree and ends up chasing the noise; at a
        tenth of that no single tree dominates, and the shades show the fit creeping
        up on the curve instead.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 1.8rem; align-items: center; flex-wrap: wrap; }
.knobs > :nth-child(-n+2) { min-width: 11rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.5; }
</style>
