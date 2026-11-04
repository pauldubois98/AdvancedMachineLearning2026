<!-- estimators_compare: S/(n−1), S/n and S/(n+1) on the same 4000 samples.
     The unbiased one is not the one with the smallest MSE. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { histBars } from '../lib/hist'
import { mean, pvar } from '../lib/stats'
import { BLUE, GREEN, INK, PURPLE } from '../lib/theme'

const n = ref(8)
const R = 4000
const MAXN = 40
const r = new Rng(8)
const Z = Array.from({ length: R }, () => Array.from({ length: MAXN }, () => r.normal()))
const S = computed(() => Z.map((row) => {
  const x = row.slice(0, n.value)
  return pvar(x) * x.length
}))
const divs = computed(() => [
  { name: 'unbiased', c: n.value - 1, color: BLUE },
  { name: 'MLE', c: n.value, color: GREEN },
  { name: 'shrunk', c: n.value + 1, color: PURPLE },
])
const rows = computed(() => divs.value.map((d, k) => {
  const e = S.value.map((s) => s / d.c)
  const m = mean(e)
  return { ...d, e, m, b2: (m - 1) ** 2, v: pvar(e), y0: (2 - k) * 1.0 }
}))
const hi = 3.2
const bars = computed(() => rows.value.flatMap((r) => {
  const b = histBars(r.e, 0, hi, 64, r.color, 0.35, true, r.y0)
  const peak = Math.max(...b.map((q) => q.y - r.y0))
  return b.map((q) => ({ ...q, y: r.y0 + ((q.y - r.y0) / peak) * 0.85 }))
}))
const mse = computed(() => rows.value.map((r) => r.b2 + r.v))
const top = computed(() => Math.max(...mse.value) * 1.25)
const best = computed(() => mse.value.indexOf(Math.min(...mse.value)))
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 4000 samples of n points from N(0, σ² = 1). Each sample gives its scatter S = Σ (xᵢ − x̄)², divided three ways. Left, the three histograms of the estimates (the line is the true σ² = 1, the ticks are the means); right, the error of each.</div>
    <div class="r23">
      <LineChart :series="[]" :bars="bars" :x-domain="[0, hi]" :y-domain="[0, 3]" :x-ticks="[0, 0.5, 1, 1.5, 2, 2.5, 3]" :y-ticks="[]" x-label="the estimate of σ²"
        :vlines="[{ x: 1, color: INK, dash: '' }]"
        :arrows="rows.map((r) => ({ x0: r.m, y0: r.y0 + 0.5, x1: r.m, y1: r.y0 + 0.02, color: r.color, width: 2 }))"
        :labels="rows.map((r) => ({ x: hi - 0.05, y: r.y0 + 0.55, text: `${r.name}, c = ${r.c}`, color: r.color, anchor: 'end' }))" />
      <LineChart :series="[]" :x-domain="[-0.6, 2.6]" :y-domain="[0, top]" :y-ticks="[]" title="bias² + Var = MSE"
        :bars="rows.flatMap((r, k) => [{ x: k, y: r.v, w: 0.6, color: r.color, alpha: 0.85 }, { x: k, y: r.v + r.b2, y0: r.v, w: 0.6, color: r.color, alpha: 0.35, label: mse[k].toFixed(3) }])"
        :labels="rows.map((r, k) => ({ x: k, y: top * 0.04, text: r.name, color: '#fff', anchor: 'middle', size: 11 }))" />
    </div>
    <div class="foot">solid: variance, pale: bias². Smallest MSE: <b :style="{ color: rows[best].color }">{{ rows[best].name }}</b>, S/(n + 1). Unbiased is not the same as best; the gap closes as n grows.</div>
    <div class="controls"><Knob v-model="n" :min="2" :max="40" :step="1" :digits="0" label="points per sample n" :color="INK" /></div>
  </div>
</template>
