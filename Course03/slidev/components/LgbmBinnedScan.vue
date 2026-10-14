<!-- lgbm_binned_scan: the scan now walks bin edges, so the winner it returns is
     the edge beside the exact one. The bins slider is the whole argument. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { exactScan, gainAt, splitDemo } from '../lib/gbm'
import { GREEN, INK, MUTED, RED } from '../lib/theme'

const nBins = ref(8)
const demo = splitDemo()
const xs = demo.X.map((r) => r[0])

const exact = exactScan(xs, demo.g, demo.h)
const bestExact = exact.cuts[exact.gains.indexOf(Math.max(...exact.gains))]
const maxExact = Math.max(...exact.gains)

const binned = computed(() => {
  const n = Math.round(nBins.value)
  const inner: number[] = []
  for (let b = 1; b < n; b++) inner.push(b / n)
  const gains = gainAt(xs, demo.g, demo.h, inner)
  const i = gains.indexOf(Math.max(...gains))
  return { cuts: inner, gains, best: inner[i], bestGain: gains[i] }
})
const lost = computed(() => maxExact - binned.value.bestGain)
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="[
        { points: exact.cuts.map((c, i) => [c, exact.gains[i]] as [number, number]), color: MUTED, width: 1.8, step: true },
        { points: binned.cuts.map((c, i) => [c, binned.gains[i]] as [number, number]), color: GREEN, width: 2.8, step: true },
      ]"
      :dots="binned.cuts.map((c, i) => ({ x: c, y: binned.gains[i], color: GREEN, r: 4 }))"
      :vlines="[
        { x: bestExact, color: MUTED, dash: '2,3' },
        { x: binned.best, color: GREEN, dash: '2,3' },
      ]"
      :hlines="[{ y: 0, color: INK, dash: '' }]"
      :x-domain="[0, 1]" :y-domain="[-3.5, 11]"
      :x-ticks="[0, 0.25, 0.5, 0.75, 1]" :y-ticks="[0, 5, 10]"
      x-label="threshold" y-label="gain"
      title="the exact winner is not on the grid, so the scan returns the edge beside it"
      :labels="[
        { x: 0.02, y: 10.4, text: `exact scan: ${exact.cuts.length} candidates, one per midpoint`, color: MUTED, size: 11.5 },
        { x: 0.02, y: 9.4, text: `binned scan: ${binned.cuts.length} candidates, one per bin edge`, color: GREEN, size: 11.5 },
        { x: bestExact - 0.015, y: -2.2, text: `${bestExact.toFixed(2)} exact`, color: MUTED, size: 11, anchor: 'end' },
        { x: binned.best + 0.015, y: -3, text: `${binned.best.toFixed(2)} binned`, color: GREEN, size: 11 },
      ]"
    />
    <div class="controls">
      <div class="knobs">
        <Knob v-model="nBins" :min="2" :max="60" :step="1" label="bins" :digits="0" :color="GREEN" />
        <Readout
          :items="[
            { label: 'exact winner', value: `${bestExact.toFixed(3)}, gain ${maxExact.toFixed(2)}`, color: MUTED },
            { label: 'binned winner', value: `${binned.best.toFixed(3)}, gain ${binned.bestGain.toFixed(2)}`, color: GREEN },
            { label: 'gain given up', value: lost.toFixed(3), color: lost > 0.3 ? RED : GREEN },
          ]"
        />
      </div>
      <p class="note">
        The binning is an approximation, and with a handful of bins it is a visible one.
        Push the slider up and the two curves close: at LightGBM's 255 bins the gap is
        invisible, and the scan is still over 255 candidates instead of n − 1.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child { min-width: 11rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
