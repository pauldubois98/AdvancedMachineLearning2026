<!-- boosting_stages: watch the residuals flatten. Every round is fitted live,
     so the tree in the bottom panel really is the tree the top panel adds. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sine1d } from '../lib/databis'
import { boostRounds } from '../lib/boost'
import { BLUE, GOLD, GREEN, INK, MUTED, RED } from '../lib/theme'

const m = ref(1)
const eta = ref(0.8)
const depth = ref(2)
const MAX = 12
const data = sine1d(90, 0.18, 0)

const run = computed(() =>
  boostRounds(data.X, data.y, {
    nTrees: MAX, eta: eta.value, maxDepth: Math.round(depth.value), seed: 0,
  }),
)
const grid = computed(() => {
  const xs: number[] = []
  for (let i = 0; i <= 400; i++) xs.push(i / 400)
  return xs
})
/** F_m on the plotting grid: the constant, plus eta times each tree so far */
const Fm = computed(() => {
  const k = Math.round(m.value)
  return grid.value.map((x) => {
    let s = run.value.f0
    for (let t = 0; t < k; t++) s += eta.value * run.value.rounds[t].tree.predict([x])[0]
    return [x, s] as [number, number]
  })
})
const residual = computed(() => {
  const k = Math.round(m.value)
  const r = k === 0 ? data.y.map((v) => v - run.value.f0) : run.value.rounds[k - 1].residual.map((_, i) => data.y[i] - run.value.rounds[k - 1].F[i])
  return data.x.map((x, i) => ({ x, y: r[i], color: GOLD, r: 3 }))
})
const nextTree = computed(() => {
  const k = Math.round(m.value)
  if (k >= MAX) return []
  const t = run.value.rounds[k].tree
  return grid.value.map((x) => [x, t.predict([x])[0]] as [number, number])
})
const sub = (n: number) => String(n).split('').map((c) => '\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089'[Number(c)]).join('')
const truth = computed(() => grid.value.map((x) => [x, Math.sin(2 * Math.PI * x)] as [number, number]))
const rss = computed(() => {
  const k = Math.round(m.value)
  const F = k === 0 ? data.y.map(() => run.value.f0) : run.value.rounds[k - 1].F
  return data.y.reduce((s, v, i) => s + (v - F[i]) ** 2, 0) / data.y.length
})
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        :series="[
          { points: truth, color: MUTED, width: 1.4, dash: '6,4' },
          { points: Fm, color: RED, width: 2.4 },
        ]"
        :dots="data.x.map((x, i) => ({ x, y: data.y[i], color: BLUE, r: 2.6 }))"
        :x-domain="[0, 1]" :y-domain="[-1.9, 1.9]" :x-ticks="[0, 0.5, 1]" :y-ticks="[-1, 0, 1]"
        x-label="x" y-label="y"
        :title="`F${sub(Math.round(m))} : the sum of the first ${Math.round(m)} tree${Math.round(m) === 1 ? '' : 's'}`"
        :title-color="RED"
      />
      <LineChart
        :series="[{ points: nextTree, color: GREEN, width: 2.2, step: false }]"
        :dots="residual"
        :hlines="[{ y: 0, color: INK, dash: '' }]"
        :x-domain="[0, 1]" :y-domain="[-1.9, 1.9]" :x-ticks="[0, 0.5, 1]" :y-ticks="[-1, 0, 1]"
        x-label="x" y-label="residual"
        :title="m >= MAX ? 'nothing left to fit' : 'what is left over, and the tree fitted to it'"
        :title-color="GREEN"
      />
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="m" :min="0" :max="MAX" :step="1" label="trees so far, m" :digits="0" :color="RED" />
        <Knob v-model="eta" :min="0.05" :max="1" label="learning rate η" :digits="2" :color="GREEN" />
        <Knob v-model="depth" :min="1" :max="4" :step="1" label="depth of each tree" :digits="0" :color="MUTED" />
        <Readout :items="[{ label: 'training error', value: rss.toFixed(4), color: BLUE }]" />
      </div>
      <p class="note">
        Each tree is fitted to the residuals of the sum so far, never to y. Push m up
        and the right panel flattens onto zero: that is the whole algorithm.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.4rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap; }
.knobs > :nth-child(-n+3) { min-width: 10rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
