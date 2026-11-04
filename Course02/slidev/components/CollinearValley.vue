<!-- collinear_valley: the loss over (β1, β2) when x2 = 2 x1 + ε z. At ε = 0 the
     valley floor is flat and XᵀX is singular; a little ε gives a unique
     minimum at the bottom of a long, shallow trough. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { fmt, solve } from '../lib/reg'
import { ramp, BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const x1 = [1, 2, 3, 4]
const y = [1.1, 1.9, 3.2, 3.8]
const z = [0.3, -0.5, 0.4, -0.2]
const eps = ref(0)
const x2 = computed(() => x1.map((v, i) => 2 * v + eps.value * z[i]))
const G = computed(() => {
  const a = x1.reduce((s, v) => s + v * v, 0), b = x1.reduce((s, v, i) => s + v * x2.value[i], 0), c = x2.value.reduce((s, v) => s + v * v, 0)
  return [a, b, c]
})
const det = computed(() => G.value[0] * G.value[2] - G.value[1] ** 2)
const loss = (b1: number, b2: number) => 0.5 * x1.reduce((s, v, i) => s + (y[i] - b1 * v - b2 * x2.value[i]) ** 2, 0)
const best = x1.reduce((s, v, i) => s + v * y[i], 0) / x1.reduce((s, v) => s + v * v, 0)
const bhat = computed(() => {
  if (det.value < 1e-9) return null
  const r = [x1.reduce((s, v, i) => s + v * y[i], 0), x2.value.reduce((s, v, i) => s + v * y[i], 0)]
  return solve([[G.value[0], G.value[1]], [G.value[1], G.value[2]]], r)
})
// the eigen-directions of XᵀX: the valley runs along the small one
const eig = computed(() => {
  const [a, b, c] = G.value, tr = (a + c) / 2, disc = Math.sqrt(((a - c) / 2) ** 2 + b * b)
  const lmin = tr - disc, lmax = tr + disc
  const v = Math.abs(b) < 1e-12 ? [1, 0] : [b, lmin - a]
  const L = Math.hypot(v[0], v[1])
  return { lmin: Math.max(lmin, 0), lmax, v: [v[0] / L, v[1] / L] }
})
const centre = computed(() => bhat.value ?? [best / 5, (2 * best) / 5])
const along = computed(() => curve((t) => loss(centre.value[0] + t * eig.value.v[0], centre.value[1] + t * eig.value.v[1]), -1.1, 1.1))
const across = computed(() => curve((t) => loss(centre.value[0] - t * eig.value.v[1], centre.value[1] + t * eig.value.v[0]), -1.1, 1.1))
const shade = ramp(['#08306b', '#2171b5', '#6baed6', '#c6dbef', '#f7fbff'])
const field = computed(() => (b1: number, b2: number) => Math.log1p(loss(b1, b2)))
const lmin = computed(() => (bhat.value ? loss(bhat.value[0], bhat.value[1]) : 0.5 * x1.reduce((s, v, i) => s + (y[i] - best * v) ** 2, 0)))
const levels = computed(() => [0.05, 0.3, 1, 3, 8].map((l) => ({ f: (a: number, b: number) => loss(a, b), level: l + lmin.value, color: '#ffffff', width: 1 })))
const markers = computed(() => bhat.value
  ? [{ at: bhat.value as [number, number], color: GREEN, shape: 'star' as const, size: 9 }]
  : [])
const valley = computed(() => (bhat.value ? [] : [{ a: [best + 2.0, -1.0] as [number, number], b: [best - 3.2, 1.6] as [number, number], color: RED, width: 2.6 }]))
</script>

<template>
  <div class="cmp">
    <div class="r3" style="grid-template-columns: 1.1fr 1fr 0.8fr">
      <Plane :field="field" :field-color="(v) => shade(v / 3.2)" :levels="levels" :domain="[-1.2, 2.6, -1, 1.6]" :equal="false" axes x-label="β₁" y-label="β₂"
        :markers="markers" :segments="valley" title="loss" />
      <LineChart :series="[{ points: along, color: RED, width: 2.8 }, { points: across, color: INK, dash: '6,4' }]" :x-domain="[-1.1, 1.1]" :y-domain="[0, Math.max(6, along[0][1])]"
        :x-ticks="[-1, 0, 1]" :y-ticks="[]" x-label="how far you move" y-label="loss" title="along the valley (red), across it (dashed)" />
      <div class="side" style="align-self: center">
        <p><Tex formula="X^TX" /> =</p>
        <table class="plain" style="width: 80%; font-size: 1rem"><tr><td>{{ fmt(G[0], 1) }}</td><td>{{ fmt(G[1], 1) }}</td></tr><tr><td>{{ fmt(G[1], 1) }}</td><td>{{ fmt(G[2], 1) }}</td></tr></table>
        <p :style="{ color: det < 1e-9 ? RED : INK }">det(XᵀX) = <b>{{ det < 1e-9 ? '0' : fmt(det, 3) }}</b></p>
        <p>eigenvalues {{ fmt(eig.lmax, 1) }} and {{ fmt(eig.lmin, 3) }}</p>
        <p v-if="!bhat" :style="{ color: RED }">so (XᵀX)⁻¹ does not exist: a whole line of minimisers</p>
        <p v-else :style="{ color: GREEN }">unique minimum β̂ = ({{ fmt(bhat[0]) }}, {{ fmt(bhat[1]) }}), but the floor is almost flat</p>
      </div>
    </div>
    <div class="foot">x₂ = 2x₁ + ε·z, a tiny perturbation z of the second column</div>
    <div class="controls">
      <Knob v-model="eps" :min="0" :max="1" :step="0.01" label="ε" :color="BLUE" />
    </div>
  </div>
</template>
