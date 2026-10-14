<!-- lgbm_subtract: the free half of the work. One child's histogram is the
     parent's minus its sibling's, so only the smaller child is ever filled. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { binFeature, splitDemo } from '../lib/gbm'
import { BLUE, GREEN, INK, MUTED } from '../lib/theme'

const cutBin = ref(5)
const N_BINS = 8
const demo = splitDemo()
const xs = demo.X.map((r) => r[0])
const all = binFeature(xs, demo.g, demo.h, N_BINS)

function barsFor(rows: boolean[], color: string) {
  const sum = new Array(N_BINS).fill(0)
  for (let i = 0; i < xs.length; i++) if (rows[i]) sum[all.idx[i]] += demo.g[i]
  const w = all.edges[1] - all.edges[0]
  return sum.map((v, i) => ({
    x: (all.edges[i] + all.edges[i + 1]) / 2, y: v, w: w * 0.84, color,
  }))
}
const cut = computed(() => all.edges[Math.round(cutBin.value)])
const parent = computed(() => barsFor(xs.map(() => true), MUTED))
const right = computed(() => barsFor(xs.map((x) => x >= cut.value), BLUE))
const left = computed(() => barsFor(xs.map((x) => x < cut.value), GREEN))
const counts = computed(() => {
  const nL = xs.filter((x) => x < cut.value).length
  return { nL, nR: xs.length - nL }
})
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        :series="[]" :bars="parent" :hlines="[{ y: 0, color: INK, dash: '' }]"
        :vlines="[{ x: cut, color: INK, dash: '4,3' }]"
        :x-domain="[0, 1]" :y-domain="[-6, 6]" :x-ticks="[0, 0.5, 1]" :y-ticks="[-4, 0, 4]"
        x-label="feature value" y-label="Σ g per bin"
        title="the parent's histogram chose this split" :title-color="MUTED"
      />
      <span class="op">−</span>
      <LineChart
        :series="[]" :bars="right" :hlines="[{ y: 0, color: INK, dash: '' }]"
        :vlines="[{ x: cut, color: INK, dash: '4,3' }]"
        :x-domain="[0, 1]" :y-domain="[-6, 6]" :x-ticks="[0, 0.5, 1]" :y-ticks="[]"
        x-label="feature value"
        :title="`right child (${counts.nR} rows): filled by one pass`" :title-color="BLUE"
      />
      <span class="op">=</span>
      <LineChart
        :series="[]" :bars="left" :hlines="[{ y: 0, color: INK, dash: '' }]"
        :vlines="[{ x: cut, color: INK, dash: '4,3' }]"
        :x-domain="[0, 1]" :y-domain="[-6, 6]" :x-ticks="[0, 0.5, 1]" :y-ticks="[]"
        x-label="feature value"
        :title="`left child (${counts.nL} rows): free`" :title-color="GREEN"
      />
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="cutBin" :min="1" :max="N_BINS - 1" :step="1" label="split after bin" :digits="0" />
        <Readout
          :items="[
            { label: 'rows to pass over', value: `${Math.min(counts.nL, counts.nR)} of ${demo.X.length}`, color: GREEN },
            { label: 'the other child', value: 'one subtraction per bin' },
          ]"
        />
      </div>
      <p class="note">
        the two children's histograms add up to the parent's, bin by bin. LightGBM
        fills whichever child has fewer rows and subtracts for the other, so a level
        costs the smaller halves only.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap: 0 0.5rem; min-height: 0; align-items: center; }
.op { font-size: 1.5rem; color: var(--ink); }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child { min-width: 12rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
