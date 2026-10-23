<!-- completion_demo: hide more and more of the ratings table, fill it back
     with weighted NMF, and score the hidden cells, against predicting the
     mean rating. r is a slider: too small underfits, too large has nothing
     to stand on once most of the table is gone. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ratings } from '../lib/data5'
import { mat, mul } from '../lib/mat'
import { fit, init } from '../lib/nmf'
import { Rng } from '../lib/rng'
import { GREEN, INK, MUTED } from '../lib/theme'
import { logTicks } from '../lib/ticks'

const r = ref(3)
const full = ratings.full
const levels = [0.1, 0.3, 0.5, 0.65, 0.78, 0.88]
const draws = (() => { const rng = new Rng(11); return levels.map(() => Float64Array.from({ length: full.a.length }, () => rng.next())) })()
const curves = computed(() => {
  const err: [number, number][] = []
  const base: [number, number][] = []
  levels.forEach((hv, li) => {
    const m = mat(full.r, full.c)
    m.a.forEach((_, i) => { m.a[i] = draws[li][i] > hv ? 1 : 0 })
    const f = fit(full, init(full, r.value, 'nndsvd'), 400, 'mu', { mask: m })
    const Y = mul(f.W, f.H)
    let e = 0, n = 0, s = 0, ns = 0
    m.a.forEach((v, i) => { if (v) { s += full.a[i]; ns++ } })
    let b = 0
    m.a.forEach((v, i) => { if (!v) { e += Math.abs(Y.a[i] - full.a[i]); b += Math.abs(s / ns - full.a[i]); n++ } })
    err.push([100 * hv, e / n])
    base.push([100 * hv, b / n])
  })
  return { err, base }
})
const ymax = computed(() => Math.max(...curves.value.err.map((p) => p[1]), ...curves.value.base.map((p) => p[1])) * 2.5)
</script>

<template>
  <div class="wrap">
    <div class="note top">{{ full.c }} users × {{ full.r }} items, ratings from 1 to 5</div>
    <LineChart
      :series="[{ points: curves.err, color: GREEN, width: 2.4 }, { points: curves.base, color: MUTED, width: 1.6, dash: '5 4' }]"
      :dots="[...curves.err.map(([x, y]) => ({ x, y, color: GREEN, r: 4.5 })), ...curves.base.map(([x, y]) => ({ x, y, color: MUTED, r: 3.5 }))]"
      :labels="[{ x: 12, y: ymax * 0.8, text: `weighted NMF, r = ${r}`, color: GREEN, size: 13, anchor: 'start' }, { x: 12, y: ymax * 0.55, text: 'predict the global mean', color: MUTED, size: 13, anchor: 'start' }]"
      log-y :x-domain="[5, 92]" :y-domain="[0.25, ymax]" :y-ticks="logTicks(0.25, ymax)" x-label="% of the table hidden" y-label="mean error on the hidden entries (stars)" :x-ticks="[10, 20, 30, 40, 50, 60, 70, 80, 90]"
    />
    <div class="controls">
      <Knob v-model="r" :min="1" :max="8" :step="1" label="r" :digits="0" :color="INK" />
      <span class="note">Each point is a fresh weighted NMF (400 passes) with the hidden cells at weight 0.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
</style>
