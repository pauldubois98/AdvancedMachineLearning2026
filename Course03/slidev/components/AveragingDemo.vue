<!-- forest_idea: averaging many noisy but unbiased guesses. The histogram is
     simulated live, so the spread you read off is the spread of the draw. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { varianceOfAverage } from '../lib/forest'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const M = ref(50)
const rho = ref(0)
const N = 4000

/** Each tree's error at one test point: a shared part (how alike the trees
 *  are) plus an independent part. Averaging kills only the second. */
const sim = computed(() => {
  const rng = new Rng(11)
  const m = Math.round(M.value)
  const a = Math.sqrt(rho.value)
  const b = Math.sqrt(1 - rho.value)
  const single: number[] = []
  const avg: number[] = []
  for (let i = 0; i < N; i++) {
    const common = rng.normal(0, 1)
    let s = 0
    let first = 0
    for (let t = 0; t < m; t++) {
      const e = a * common + b * rng.normal(0, 1)
      if (t === 0) first = e
      s += e
    }
    single.push(first)
    avg.push(s / m)
  }
  return { single, avg }
})

function hist(v: number[], color: string) {
  const lo = -3.5
  const hi = 3.5
  const nb = 56
  const counts = new Array(nb).fill(0)
  for (const x of v) {
    const b = Math.floor(((x - lo) / (hi - lo)) * nb)
    if (b >= 0 && b < nb) counts[b]++
  }
  const w = (hi - lo) / nb
  return counts.map((c, i) => ({ x: lo + (i + 0.5) * w, y: c / v.length / w, w: w * 0.9, color, alpha: 0.8 }))
}
const sd = (v: number[]) => {
  const m = v.reduce((a, b) => a + b, 0) / v.length
  return Math.sqrt(v.reduce((a, b) => a + (b - m) ** 2, 0) / v.length)
}
const yMax = computed(() => {
  const peak = (b: { y: number }[]) => b.reduce((m, x) => Math.max(m, x.y), 0)
  return Math.max(peak(hist(sim.value.single, BLUE)), peak(hist(sim.value.avg, GREEN))) * 1.08
})
const predicted = computed(() => Math.sqrt(varianceOfAverage(Math.round(M.value), rho.value)))
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        :series="[]" :bars="hist(sim.single, BLUE)"
        :vlines="[{ x: 0, color: INK, dash: '' }]"
        :x-domain="[-3.5, 3.5]" :y-domain="[0, yMax]" :x-ticks="[-2, 0, 2]" :y-ticks="[]"
        x-label="prediction error at one test point"
        :title="`one tree: spread ${sd(sim.single).toFixed(2)}`" :title-color="BLUE"
      />
      <LineChart
        :series="[]" :bars="hist(sim.avg, GREEN)"
        :vlines="[{ x: 0, color: INK, dash: '' }]"
        :x-domain="[-3.5, 3.5]" :y-domain="[0, yMax]" :x-ticks="[-2, 0, 2]" :y-ticks="[]"
        x-label="prediction error at one test point"
        :title="`${Math.round(M)} trees, averaged: spread ${sd(sim.avg).toFixed(2)}`" :title-color="GREEN"
      />
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="M" :min="1" :max="200" :step="1" label="trees averaged, M" :digits="0" :color="GREEN" />
        <Knob v-model="rho" :min="0" :max="0.9" label="how alike the trees are, ρ" :digits="2" :color="RED" />
        <Readout
          :items="[
            { label: 'measured spread', value: sd(sim.avg).toFixed(3), color: GREEN },
            { label: 'formula says', value: predicted.toFixed(3), color: MUTED },
          ]"
        />
      </div>
      <p class="note">
        Both histograms are centred on zero: averaging leaves the bias exactly where
        it was, and only shrinks the spread. Push ρ up and the shrinking stops.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 1.8rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child, .knobs > :nth-child(2) { min-width: 13rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
