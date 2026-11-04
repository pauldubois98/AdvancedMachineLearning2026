<!-- near_collinear: 150 fresh samples, 150 fits. As the two columns carry the
     same information, the estimates scatter along a line; ridge pulls them in. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { fmt, solve } from '../lib/reg'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const rho = ref(0.999)
const lam = ref(5)
const n = ref(40)
const refit = computed(() => {
  const rng = new Rng(12)
  const ols: [number, number][] = [], rid: [number, number][] = []
  const s = Math.sqrt(1 - rho.value ** 2)
  for (let r = 0; r < 150; r++) {
    let a = 0, b = 0, c = 0, u = 0, v = 0
    for (let i = 0; i < n.value; i++) {
      const x1 = rng.normal(), x2 = rho.value * x1 + s * rng.normal()
      const y = x1 + x2 + rng.normal(0, 0.4)
      a += x1 * x1; b += x1 * x2; c += x2 * x2; u += x1 * y; v += x2 * y
    }
    ols.push(solve([[a + 1e-10, b], [b, c + 1e-10]], [u, v]) as [number, number])
    rid.push(solve([[a + lam.value, b], [b, c + lam.value]], [u, v]) as [number, number])
  }
  return { ols, rid }
})
const sd = (P: [number, number][]) => { const m = P.reduce((s, p) => s + p[0], 0) / P.length; return Math.sqrt(P.reduce((s, p) => s + (p[0] - m) ** 2, 0) / P.length) }
const dom: [number, number, number, number] = [-4.5, 6.5, -4.5, 6.5]
const axes = [{ a: [-4.5, 0] as [number, number], b: [6.5, 0] as [number, number], color: '#cccfd2', width: 1 }, { a: [0, -4.5] as [number, number], b: [0, 6.5] as [number, number], color: '#cccfd2', width: 1 }]
const truth = [{ at: [1, 1] as [number, number], color: MUTED, shape: 'x' as const, size: 8 }]
const col = computed(() => (rho.value > 0.9 ? RED : BLUE))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Plane :X="refit.ols" :colors="col" :alpha="0.5" :size="3" :domain="dom" :segments="axes" :markers="truth" axes x-label="β̂₁" y-label="β̂₂"
        :title="`least squares, ρ(x₁, x₂) = ${rho.toFixed(3)}`" :title-color="col" :caption="`spread ± ${fmt(sd(refit.ols))} on β̂₁`" />
      <Plane :X="refit.rid" :colors="GREEN" :alpha="0.5" :size="3" :domain="dom" :segments="axes" :markers="truth" axes x-label="β̂₁" y-label="β̂₂"
        :title="`ridge, λ = ${fmt(lam, 1)}`" :title-color="GREEN" :caption="`spread ± ${fmt(sd(refit.rid))} on β̂₁`" />
    </div>
    <div class="foot">each dot: one sample of n points, y = x₁ + x₂ + noise, one fit; the cross is the truth (1, 1). <b>Ridge stabilizes coefficients</b>, at the price of a pull towards 0.</div>
    <div class="controls">
      <Knob v-model="rho" :min="0" :max="0.999" :step="0.001" :digits="3" label="correlation ρ" :color="col" />
      <Knob v-model="lam" :min="0" :max="40" :step="0.5" :digits="1" label="ridge λ" :color="GREEN" />
      <Knob v-model="n" :min="10" :max="200" :step="1" :digits="0" label="n" :color="BLUE" />
    </div>
  </div>
</template>
