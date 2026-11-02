<!-- bagging_vs_boosting: two ways to spend M trees, and the two errors they
     attack. Both fits are live, on the same data, with the same M. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sine1d } from '../lib/databis'
import { forestReg } from '../lib/forest'
import { fitBooster } from '../lib/boost'
import { BLUE, GOLD, GREEN, MUTED, RED } from '../lib/theme'

const M = ref(12)
const data = sine1d(70, 0.3, 1)
const grid: number[] = []
for (let i = 0; i <= 300; i++) grid.push(i / 300)

const forest = computed(() =>
  forestReg(data.X, data.y, { nTrees: Math.round(M.value), maxDepth: 12, seed: 0 }),
)
const boost = computed(() =>
  fitBooster(data.X, data.y, {
    nTrees: Math.round(M.value), eta: 0.3, maxDepth: 1, loss: 'squared', seed: 0,
  }),
)
const truth = grid.map((x) => [x, Math.sin(2 * Math.PI * x)] as [number, number])
const fCurve = computed(() => grid.map((x) => [x, forest.value.predict([x])] as [number, number]))
const bCurve = computed(() => grid.map((x) => [x, boost.value.raw([x])] as [number, number]))

/** squared error against the noiseless curve, split into the part that is a
 *  systematic offset (bias) and the part that wiggles (variance) */
function errors(pred: (x: number) => number) {
  let bias = 0
  for (const x of grid) bias += (pred(x) - Math.sin(2 * Math.PI * x)) ** 2
  return bias / grid.length
}
const errF = computed(() => errors((x) => forest.value.predict([x])))
const errB = computed(() => errors((x) => boost.value.raw([x])))
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        :series="[
          { points: truth, color: MUTED, width: 1.4, dash: '6,4' },
          { points: fCurve, color: GREEN, width: 2.4 },
        ]"
        :dots="data.x.map((x, i) => ({ x, y: data.y[i], color: BLUE, r: 2.6 }))"
        :x-domain="[0, 1]" :y-domain="[-1.9, 1.9]" :x-ticks="[0, 0.5, 1]" :y-ticks="[-1, 0, 1]"
        x-label="x"
        :title="`forest: ${Math.round(M)} deep trees, averaged`" :title-color="GREEN"
      />
      <LineChart
        :series="[
          { points: truth, color: MUTED, width: 1.4, dash: '6,4' },
          { points: bCurve, color: GOLD, width: 2.4 },
        ]"
        :dots="data.x.map((x, i) => ({ x, y: data.y[i], color: BLUE, r: 2.6 }))"
        :x-domain="[0, 1]" :y-domain="[-1.9, 1.9]" :x-ticks="[0, 0.5, 1]" :y-ticks="[-1, 0, 1]"
        x-label="x"
        :title="`boosting: ${Math.round(M)} stumps, summed`" :title-color="GOLD"
      />
    </div>
    <div class="cols">
      <div>
        <h4 :style="{ color: GREEN }">forest, parallel</h4>
        <p class="note">
          Every tree is deep and fitted to a bootstrap sample of the data, so each one
          is already close on average and only noisy. Averaging attacks the
          <em class="hl-green">variance</em>; the first tree is as unbiased as the last.
        </p>
      </div>
      <div>
        <h4 :style="{ color: GOLD }">boosting, sequential</h4>
        <p class="note">
          Every tree is a stump fitted to what the sum so far got wrong, so the fit
          starts far too simple and is corrected round by round. Adding trees attacks
          the <em class="hl-gold">bias</em>.
        </p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="M" :min="1" :max="120" :step="1" label="trees, M" :digits="0" />
      <Readout
        :items="[
          { label: 'forest error vs the true curve', value: errF.toFixed(3), color: GREEN },
          { label: 'boosting', value: errB.toFixed(3), color: GOLD },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.4rem; min-height: 0; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 0 2.5rem; }
h4 { margin: 0; font-size: 0.9rem; }
.note { font-size: 0.78rem; margin: 0.1rem 0 0; color: var(--muted); line-height: 1.45; }
.controls { display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; }
.controls > :first-child { min-width: 12rem; }
</style>
