<!-- lda_qda_cost: QDA estimates K covariance matrices, LDA one. Left, the
     parameter count; right, the price on a finite sample, simulated live. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { chol } from '../lib/stats'
import { draw, ldaQda, randomCov } from '../lib/nd'
import { GREEN, INK, PURPLE } from '../lib/theme'

const K = ref(3)
const d = ref(10)
const lda = (dd: number) => K.value * dd + (dd * (dd + 1)) / 2
const qda = (dd: number) => K.value * (dd + (dd * (dd + 1)) / 2)
const ds = Array.from({ length: 29 }, (_, i) => i + 2)
const SIZES = [40, 80, 160, 320, 800, 2000]
const curves = computed(() => {
  const D = d.value
  const rng = new Rng(57)
  const L0 = chol(randomCov(rng, D)), L1 = chol(randomCov(rng, D))
  const m0 = new Array(D).fill(0), m1 = new Array(D).fill(0.8 * Math.sqrt(10 / D))
  const T0 = draw(rng, 1000, m0, L0), T1 = draw(rng, 1000, m1, L1)
  return SIZES.map((n) => {
    let a = 0, b = 0
    const reps = n < 500 ? 8 : 3
    for (let r = 0; r < reps; r++) {
      const s = ldaQda(draw(rng, n >> 1, m0, L0), draw(rng, n - (n >> 1), m1, L1), T0, T1)
      a += s.lda / reps; b += s.qda / reps
    }
    return { n, lda: a, qda: b }
  })
})
const yr = computed(() => {
  const v = curves.value.flatMap((c) => [c.lda, c.qda])
  return [Math.floor(Math.min(...v) * 50) / 50, Math.min(1, Math.ceil(Math.max(...v) * 50) / 50 + 0.01)] as [number, number]
})
const yt = computed(() => { const out = []; for (let v = yr.value[0]; v <= yr.value[1] + 1e-9; v += 0.02) out.push(+v.toFixed(2)); return out })
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Left, exact:</b> the number of means and covariance entries to estimate. <b>Right, simulated:</b> two classes in d dimensions with different random covariances (so QDA is the right model); training sets of n points, test accuracy on 2000 new points, averaged over several draws.</div>
    <div class="r2">
      <LineChart :series="[{ points: ds.map((x) => [x, lda(x)]), color: GREEN }, { points: ds.map((x) => [x, qda(x)]), color: PURPLE }]"
        :x-domain="[2, 33]" :y-domain="[0, qda(30) * 1.05]" :x-ticks="[5, 10, 15, 20, 25, 30]" :y-ticks="[0, 500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 7000].filter((t) => t <= qda(30))"
        x-label="number of features d" y-label="parameters to estimate" :vlines="[{ x: d, color: INK }]"
        :dots="[{ x: d, y: lda(d), color: GREEN, r: 5 }, { x: d, y: qda(d), color: PURPLE, r: 5 }]"
        :labels="[{ x: 30.3, y: lda(30), text: 'LDA', color: GREEN }, { x: 30.3, y: qda(30), text: 'QDA', color: PURPLE }]" :title="`K = ${K} classes`" />
      <LineChart :series="[{ points: curves.map((c) => [c.n, c.lda]), color: GREEN }, { points: curves.map((c) => [c.n, c.qda]), color: PURPLE }]"
        :dots="curves.flatMap((c) => [{ x: c.n, y: c.lda, color: GREEN, r: 4 }, { x: c.n, y: c.qda, color: PURPLE, r: 4 }])"
        :x-domain="[30, 3600]" log-x :y-domain="yr" :x-ticks="[100, 1000]" :y-ticks="yt" x-label="training samples n" y-label="test accuracy"
        :labels="[{ x: 2200, y: curves[5].lda, text: 'LDA', color: GREEN }, { x: 2200, y: curves[5].qda, text: 'QDA', color: PURPLE }]" :title="`d = ${d}, K = 2`" />
    </div>
    <div class="foot">at d = {{ d }}: LDA estimates <b :style="{ color: GREEN }">{{ lda(d) }}</b> numbers, QDA <b :style="{ color: PURPLE }">{{ qda(d) }}</b>. With few samples QDA's extra parameters are noise and LDA wins; with many, QDA's flexibility pays.</div>
    <div class="controls">
      <Knob v-model="K" :min="2" :max="10" :step="1" :digits="0" label="classes K (left)" :color="INK" />
      <Knob v-model="d" :min="2" :max="20" :step="1" :digits="0" label="features d" :color="INK" />
    </div>
  </div>
</template>
