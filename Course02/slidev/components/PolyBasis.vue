<!-- linreg_basis: the same least squares, on the columns (x, x², ..., x^d).
     Raise the degree: the fit follows the curve, then the noise. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve } from '../lib/hist'
import { fmt, wls, type Vec } from '../lib/reg'
import { BLUE, GREEN, INK, MUTED, PURPLE, RED } from '../lib/theme'

const deg = ref(3)
const noise = ref(0.2)
const n = ref(45)
const seed = ref(0)
const truth = (x: number) => Math.sin(2 * Math.PI * x)
function sample(rng: Rng, m: number) {
  const x = Array.from({ length: m }, () => rng.uniform(0, 1)).sort((a, b) => a - b)
  return { x, y: x.map((v) => truth(v) + rng.normal(0, noise.value)) }
}
const train = computed(() => sample(new Rng(seed.value + 1), n.value))
const test = computed(() => sample(new Rng(seed.value + 1001), 400))
// Legendre polynomials on t = 2x - 1: the same span as the monomials, and far
// better conditioned at degree 15
function basis(x: number, d: number): Vec {
  const t = 2 * x - 1
  const P = [1, t]
  for (let k = 1; k < d; k++) P.push(((2 * k + 1) * t * P[k] - k * P[k - 1]) / (k + 1))
  return P.slice(0, d + 1)
}
const fitAt = (d: number) => wls(train.value.x.map((v) => basis(v, d)), train.value.y, undefined, 1e-9)
const err = (b: Vec, d: number, s: { x: Vec; y: Vec }) => s.x.reduce((a, v, i) => a + (s.y[i] - basis(v, d).reduce((q, c, k) => q + c * b[k], 0)) ** 2, 0) / s.x.length
const beta = computed(() => fitAt(deg.value))
const f = (x: number) => basis(x, deg.value).reduce((q, c, k) => q + c * beta.value[k], 0)
const errs = computed(() => {
  const tr: [number, number][] = [], te: [number, number][] = []
  for (let d = 0; d <= 15; d++) {
    const b = fitAt(d)
    tr.push([d, err(b, d, train.value)])
    te.push([d, err(b, d, test.value)])
  }
  return { tr, te }
})
const cap = (v: number) => Math.min(v, 1.2)
</script>

<template>
  <div class="cmp">
    <div class="r23" style="grid-template-columns: 1.5fr 1fr">
      <LineChart :series="[{ points: curve(truth, 0, 1), color: MUTED, dash: '5,4', width: 1.6 }, { points: curve(f, 0, 1, 400), color: PURPLE, width: 2.6 }]"
        :dots="train.x.map((v, i) => ({ x: v, y: train.y[i], color: BLUE, r: 3.5 }))"
        :x-domain="[0, 1]" :y-domain="[-2, 2]" :x-ticks="[0, 0.5, 1]" :y-ticks="[-2, -1, 0, 1, 2]" x-label="x" y-label="y"
        :title="`columns 1, x, …, x^${deg}`" />
      <LineChart :series="[{ points: errs.tr.map(([d, v]) => [d, cap(v)]), color: GREEN }, { points: errs.te.map(([d, v]) => [d, cap(v)]), color: RED }]"
        :dots="[{ x: deg, y: cap(errs.tr[deg][1]), color: GREEN, r: 5 }, { x: deg, y: cap(errs.te[deg][1]), color: RED, r: 5 }]"
        :labels="[{ x: 12.5, y: cap(errs.tr[12][1]) + 0.06, text: 'training', color: GREEN }, { x: 9.5, y: Math.min(cap(errs.te[9][1]) + 0.08, 1.12), text: 'test', color: RED }]"
        :x-domain="[0, 15]" :y-domain="[0, 1.2]" :x-ticks="[0, 3, 6, 9, 12, 15]" :y-ticks="[0, 0.5, 1]" x-label="degree d" y-label="mean squared error" title="error against the degree" />
    </div>
    <div class="foot">still <b>linear in the weights</b>: ŷ = Σₖ βₖ φₖ(x), solved by the same least squares. Train error <b :style="{ color: GREEN }">{{ fmt(errs.tr[deg][1], 3) }}</b>, test error <b :style="{ color: RED }">{{ fmt(errs.te[deg][1], 3) }}</b></div>
    <div class="controls">
      <Knob v-model="deg" :min="0" :max="15" :step="1" :digits="0" label="degree d" :color="PURPLE" />
      <Knob v-model="noise" :min="0" :max="0.8" :step="0.01" label="noise σ" :color="MUTED" />
      <Knob v-model="n" :min="10" :max="200" :step="1" :digits="0" label="n" :color="BLUE" />
      <Knob v-model="seed" :min="0" :max="40" :step="1" :digits="0" label="new sample" :color="INK" />
    </div>
  </div>
</template>
