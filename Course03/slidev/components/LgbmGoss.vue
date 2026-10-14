<!-- lgbm_goss: keep the big gradients, subsample the rest, reweight, and the
     gain curve barely moves. The reweighting is the whole trick: drop it and
     the curve walks away. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { gainAt, goss } from '../lib/gbm'
import { GREEN, INK, MUTED, RED } from '../lib/theme'

const a = ref(0.2)
const b = ref(0.1)
const reweight = ref(true)
const N = 2000

const data = (() => {
  const rng = new Rng(7)
  const x: number[] = []
  const y: number[] = []
  for (let i = 0; i < N; i++) {
    const v = rng.uniform()
    x.push(v)
    y.push(Math.sin(2 * Math.PI * v) + rng.normal(0, 0.35))
  }
  // squared loss at F = 0: g is minus the target, h is 1
  return { x, g: y.map((v) => -v), h: y.map(() => 1) }
})()

const cuts: number[] = []
for (let i = 0; i < 60; i++) cuts.push(0.03 + (0.94 * i) / 59)
const full = gainAt(data.x, data.g, data.h, cuts)

const sample = computed(() => goss(data.g, a.value, b.value, 7))
const sampled = computed(() => {
  const s = sample.value
  const w = reweight.value ? s.w : s.w.map(() => 1)
  return gainAt(
    s.keep.map((i) => data.x[i]),
    s.keep.map((i, j) => data.g[i] * w[j]),
    s.keep.map((i, j) => data.h[i] * w[j]),
    cuts,
  )
})
const mags = computed(() => {
  const s = sample.value
  return s.sorted.map((i, k) => [k, Math.abs(data.g[i])] as [number, number])
})
const worst = computed(() => {
  let m = 0
  for (let i = 0; i < cuts.length; i++) m = Math.max(m, Math.abs(full[i] - sampled.value[i]))
  return m
})
const peak = Math.max(...full)
const bestFull = cuts[full.indexOf(peak)]
const bestSamp = computed(() => cuts[sampled.value.indexOf(Math.max(...sampled.value))])
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        :series="[{ points: mags, color: MUTED, width: 1.4 }]"
        :bands="[{ x0: 0, x1: sample.nTop, color: GREEN, alpha: 0.22 }]"
        :vlines="[{ x: sample.nTop, color: INK, dash: '2,3' }]"
        :x-domain="[0, N]" :y-domain="[0, 1.6]"
        :x-ticks="[0, 1000, 2000]" :y-ticks="[0, 0.5, 1, 1.5]"
        x-label="rows, sorted by how badly they are still fitted" y-label="|gᵢ|"
        :title="`use ${sample.keep.length} rows instead of ${N}`" :title-color="GREEN"
        :labels="[
          { x: 60, y: 1.45, text: `keep all of the top ${(a * 100).toFixed(0)}%`, color: GREEN, size: 11.5 },
          { x: sample.nTop + 90, y: 1.2, text: `sample ${(b * 100).toFixed(0)}% of the rest,`, color: MUTED, size: 11.5 },
          { x: sample.nTop + 90, y: 1.05, text: `and scale their g, h by ${sample.amp.toFixed(1)}`, color: MUTED, size: 11.5 },
        ]"
      />
      <LineChart
        :series="[
          { points: cuts.map((c, i) => [c, full[i]] as [number, number]), color: MUTED, width: 3 },
          { points: cuts.map((c, i) => [c, sampled[i]] as [number, number]), color: reweight ? GREEN : RED, width: 2, dash: '6,4' },
        ]"
        :x-domain="[0, 1]" :y-domain="[-0.06 * peak, peak * 1.18]"
        :x-ticks="[0, 0.5, 1]" :y-ticks="[0, Math.round(peak / 2), Math.round(peak)]"
        x-label="threshold" y-label="gain"
        title="the reweighting is what keeps the two curves together"
        :labels="[
          { x: 0.03, y: peak * 1.1, text: `gain on all ${N} rows`, color: MUTED, size: 11.5 },
          { x: 0.03, y: peak * 1.02, text: `gain on the ${sample.keep.length} GOSS rows`, color: reweight ? GREEN : RED, size: 11.5 },
        ]"
      />
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="a" :min="0.02" :max="0.6" label="top_rate a" :digits="2" :color="GREEN" />
        <Knob v-model="b" :min="0.02" :max="0.5" label="other_rate b" :digits="2" />
        <Toggle v-model="reweight" label="reweight the sampled rows by (1−a)/b" :color="GREEN" />
        <Readout
          :items="[
            { label: 'rows used', value: `${sample.keep.length} / ${N}`, color: GREEN },
            { label: 'worst gain error', value: worst.toFixed(1), color: worst > 0.08 * peak ? RED : GREEN },
            { label: 'winner moved', value: Math.abs(bestSamp - bestFull) < 1e-9 ? 'not at all' : `${(bestSamp - bestFull).toFixed(2)}`, color: Math.abs(bestSamp - bestFull) < 0.02 ? GREEN : RED },
          ]"
        />
      </div>
      <p class="note">
        Rows with a small gradient are already fitted, so dropping most of them costs
        little; but dropping them changes the class balance of the sample, which is
        what the (1−a)/b factor puts back. Switch it off and the gain curve, and the
        split it picks, drift away.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.knobs > :nth-child(-n+2) { min-width: 10rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
