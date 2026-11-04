<!-- logistic_loss: the logistic loss is a smooth, convex stand-in for 0/1.
     Right: its surface in (β1, β2). Separate the classes and the minimum
     leaves for infinity. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve } from '../lib/hist'
import { blobs, fmt, log1pexp, logisticIrls } from '../lib/reg'
import { ramp, GREEN, INK, RED } from '../lib/theme'

const gap = ref(1.4)
const D = computed(() => blobs(new Rng(4), 60, gap.value, 1))
const hist = computed(() => logisticIrls(D.value.X, D.value.y, 25))
const bh = computed(() => hist.value.at(-1)!)
// F with β0 fixed, written out flat: no array is allocated per evaluation
const flat = computed(() => ({ x1: Float64Array.from(D.value.X.map((p) => p[0])), x2: Float64Array.from(D.value.X.map((p) => p[1])), y: Float64Array.from(D.value.y), b0: bh.value[0] }))
const F = computed(() => {
  const { x1, x2, y, b0 } = flat.value
  return (a: number, b: number) => {
    let s = 0
    for (let i = 0; i < x1.length; i++) { const z = b0 + a * x1[i] + b * x2[i]; s += (z > 0 ? z + Math.log1p(Math.exp(-z)) : Math.log1p(Math.exp(z))) - y[i] * z }
    return s
  }
})
const sep = computed(() => D.value.X.every((p, i) => ((bh.value[0] + bh.value[1] * p[0] + bh.value[2] * p[1] > 0 ? 1 : 0) === D.value.y[i])))
const Fmin = computed(() => F.value(bh.value[1], bh.value[2]))
const shade = ramp(['#00441b', '#238b45', '#74c476', '#c7e9c0', '#f7fcf5'])
const field = computed(() => (a: number, b: number) => Math.log1p(F.value(a, b) - Fmin.value))
const dom = computed<[number, number, number, number]>(() => {
  const cx = Math.max(-2, Math.min(bh.value[1], 14)), cy = Math.max(-6, Math.min(bh.value[2], 6))
  return [cx - 3.5, cx + 3.5, cy - 3.5, cy + 3.5]
})
const inDom = computed(() => bh.value[1] > dom.value[0] && bh.value[1] < dom.value[1] && bh.value[2] > dom.value[2] && bh.value[2] < dom.value[3])
const levels = computed(() => [0.3, 1, 3, 8, 20].map((l) => ({ f: F.value, level: Fmin.value + l, color: '#ffffff', width: 1 })))
const m = curve((v) => v, -3, 3).map((p) => p[0])
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <LineChart :series="[{ points: m.map((v) => [v, v < 0 ? 1 : 0]), color: INK, width: 2.2, step: true }, { points: m.map((v) => [v, log1pexp(-v) / Math.LN2]), color: GREEN, width: 2.8 }, { points: m.map((v) => [v, (1 - v) ** 2 / 4]), color: RED, dash: '6,4', width: 2.2 }]"
        :labels="[{ x: -2.6, y: 1.12, text: '0 / 1 loss', color: INK, size: 12 }, { x: 1.1, y: 0.55, text: 'logistic', color: GREEN, size: 12 }, { x: 1.7, y: 0.85, text: 'squared', color: RED, size: 12 }]"
        :x-domain="[-3, 3]" :y-domain="[-0.1, 2.6]" :x-ticks="[-3, -2, -1, 0, 1, 2, 3]" :y-ticks="[0, 1, 2]" x-label="margin yᵢ βᵀxᵢ" y-label="loss of one point" title="smooth & convex" />
      <Plane :field="field" :field-color="(v) => shade(v / 4)" :domain="dom" :equal="false" axes x-label="β₁" y-label="β₂"
        :levels="levels" :level-res="90" :field-res="80"
        :markers="inDom ? [{ at: [bh[1], bh[2]], color: RED, shape: 'dot', size: 6 }] : []"
        title="F(β) = Σ log(1 + e^(−yᵢβᵀxᵢ)), β₀ fixed at its optimum" />
    </div>
    <div class="foot" v-if="!sep">global minimum at β̂ = ({{ fmt(bh[1]) }}, {{ fmt(bh[2]) }}), F = {{ fmt(Fmin) }}, and gradients pointing at it</div>
    <div class="foot" v-else :style="{ color: RED }">the classes are separable: F keeps decreasing along a direction, ‖β̂‖ = {{ fmt(Math.hypot(bh[1], bh[2]), 1) }} after 25 Newton steps and still growing</div>
    <div class="controls">
      <Knob v-model="gap" :min="0.2" :max="4" :step="0.01" label="class separation" :color="INK" />
    </div>
  </div>
</template>
