<!-- high_dim: n = 40 points, d features of which 3 matter. As d grows the
     training error falls to 0 and the test error explodes near d = n; the
     fitted coefficients spread their weight over every feature. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { dot, fmt, lstsqMinNorm, mse } from '../lib/reg'
import { GREEN, GRID, INK, MUTED, RED } from '../lib/theme'

const N = 40
const d = ref(12)
const noise = ref(1)
function draw(rng: Rng, m: number, dd: number) {
  const beta = Array.from({ length: dd }, (_, j) => (j < 3 ? 2 : 0))
  const X = Array.from({ length: m }, () => Array.from({ length: dd }, () => rng.normal()))
  return { X, y: X.map((r) => dot(r, beta) + rng.normal(0, noise.value)), beta }
}
const DIMS = Array.from({ length: 30 }, (_, i) => 1 + 2 * i) // 1, 3, ..., 59
const curves = computed(() => {
  const rng = new Rng(31)
  const tr: [number, number][] = [], te: [number, number][] = []
  for (const dd of DIMS) {
    let a = 0, b = 0
    const reps = 8
    for (let r = 0; r < reps; r++) {
      const s = draw(rng, N, dd)
      const bh = lstsqMinNorm(s.X, s.y)
      const t = draw(rng, 200, dd)
      a += mse(s.X, s.y, bh) / reps
      b += mse(t.X, t.y, bh) / reps
    }
    tr.push([dd, a]); te.push([dd, Math.min(b, 30)])
  }
  return { tr, te }
})
const one = computed(() => {
  const rng = new Rng(77)
  const s = draw(rng, N, d.value)
  const bh = lstsqMinNorm(s.X, s.y)
  const t = draw(rng, 400, d.value)
  return { bh, train: mse(s.X, s.y, bh), test: mse(t.X, t.y, bh) }
})
const bars = computed(() => one.value.bh.map((v, j) => ({ x: j + 1, y: Math.max(-4, Math.min(4, v)), w: 0.75, color: j < 3 ? GREEN : GRID, alpha: 1 })))
const col = computed(() => (d.value >= N - 4 ? RED : INK))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <LineChart :series="[{ points: curves.tr, color: GREEN, width: 2.6 }, { points: curves.te, color: RED, width: 2.6 }]"
        :vlines="[{ x: N, color: MUTED, dash: '2,3' }, { x: d, color: col, dash: '5,3' }]"
        :labels="[{ x: 50, y: 0.6, text: 'training', color: GREEN }, { x: 22, y: 8.6, text: 'test', color: RED }, { x: N + 0.6, y: 9.4, text: 'd = n', color: MUTED, size: 11 }]"
        :x-domain="[1, 60]" :y-domain="[0, 10]" :x-ticks="[1, 10, 20, 30, 40, 50, 60]" :y-ticks="[0, 2, 4, 6, 8, 10]"
        x-label="number of features d (n = 40)" y-label="squared error" title="accuracy" :title-color="RED" />
      <LineChart :series="[]" :bars="bars" :hlines="[{ y: 0, color: INK }]" :x-domain="[0.3, Math.max(d, 12) + 0.7]" :y-domain="[-4, 4]"
        :x-ticks="d <= 20 ? Array.from({ length: d }, (_, j) => j + 1) : [1, 10, 20, 30, 40, 50, 60].filter((t) => t <= d)" :y-ticks="[-4, -2, 0, 2, 4]"
        x-label="feature" y-label="β̂ⱼ" :title="`interpretation: the ${d} fitted β̂ⱼ (green: the 3 that matter, true value 2)`" :title-color="GREEN" />
    </div>
    <div class="foot">one sample at d = <b :style="{ color: col }">{{ d }}</b>: training error <b :style="{ color: GREEN }">{{ fmt(one.train) }}</b>, test error <b :style="{ color: RED }">{{ fmt(one.test) }}</b>. Fits better and better, predicts worse and worse; past d = n the fit is no longer unique (minimum-norm solution shown).</div>
    <div class="controls">
      <Knob v-model="d" :min="1" :max="60" :step="1" :digits="0" label="features d" :color="col" />
      <Knob v-model="noise" :min="0.1" :max="3" :step="0.05" label="noise σ" :color="MUTED" />
    </div>
  </div>
</template>
