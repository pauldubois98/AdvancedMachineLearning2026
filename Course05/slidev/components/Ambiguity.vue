<!-- eq_ambiguity: (WΛ)(Λ⁻¹H) = WH. Rescale a component, swap two, or mix
     them: the product, and so the loss, does not move. Only the mix can push
     an entry below zero, and then it is no longer a legal NMF. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { layers } from '../lib/data5'
import { col, mat, mul, row } from '../lib/mat'
import { BLUE, GOLD, GREEN, INK, PURPLE, RED } from '../lib/theme'

const { X, W, H } = layers
const s1 = ref(1)
const s2 = ref(1)
const swap = ref(false)
const mix = ref(0)
const colors = [PURPLE, GOLD, GREEN]
// Λ = Diag(s1, s2, 1) · Π · [[1, mix, 0], [0, 1, 0], [0, 0, 1]]
const pair = computed(() => {
  const r = 3
  const Lam = mat(r, r)
  Lam.a[0] = 1; Lam.a[1] = mix.value; Lam.a[4] = 1; Lam.a[8] = 1
  const D = [s1.value, s2.value, 1]
  for (let i = 0; i < r; i++) for (let j = 0; j < r; j++) Lam.a[i * r + j] *= D[j]
  if (swap.value) for (let i = 0; i < r; i++) { const t = Lam.a[i * r]; Lam.a[i * r] = Lam.a[i * r + 1]; Lam.a[i * r + 1] = t }
  // inverse of a 3 x 3 by cofactors
  const a = Lam.a
  const det = a[0] * (a[4] * a[8] - a[5] * a[7]) - a[1] * (a[3] * a[8] - a[5] * a[6]) + a[2] * (a[3] * a[7] - a[4] * a[6])
  const inv = mat(r, r)
  const c = (i: number, j: number) => a[i * 3 + j]
  const cof = [
    [c(1, 1) * c(2, 2) - c(1, 2) * c(2, 1), -(c(0, 1) * c(2, 2) - c(0, 2) * c(2, 1)), c(0, 1) * c(1, 2) - c(0, 2) * c(1, 1)],
    [-(c(1, 0) * c(2, 2) - c(1, 2) * c(2, 0)), c(0, 0) * c(2, 2) - c(0, 2) * c(2, 0), -(c(0, 0) * c(1, 2) - c(0, 2) * c(1, 0))],
    [c(1, 0) * c(2, 1) - c(1, 1) * c(2, 0), -(c(0, 0) * c(2, 1) - c(0, 1) * c(2, 0)), c(0, 0) * c(1, 1) - c(0, 1) * c(1, 0)],
  ]
  cof.forEach((rw, i) => rw.forEach((v, j) => { inv.a[i * 3 + j] = v / det }))
  const W2 = mul(W, Lam)
  const H2 = mul(inv, H)
  const Y = mul(W2, H2)
  let e = 0
  for (let i = 0; i < X.a.length; i++) e += (X.a[i] - Y.a[i]) ** 2
  const neg = [...W2.a, ...H2.a].filter((v) => v < -1e-9).length
  return { W2, H2, Y, err: Math.sqrt(e), neg }
})
const wMax = 2.6
const hMax = 2.6
</script>

<template>
  <div class="wrap">
    <div class="note top">If (W, H) is a solution, so is a whole family of others: WH = (WΛ)(Λ⁻¹H).</div>
    <div class="panels">
      <LineChart
        :series="[0, 1, 2].map((k) => ({ points: Array.from(col(pair.W2, k), (v, i) => [i, v]), color: colors[k], width: 2.2 }))"
        :hlines="[{ y: 0, color: '#9aa0a6' }]" :x-domain="[0, W.r - 1]" :y-domain="[-1, wMax]" :x-ticks="[]" :y-ticks="[0, 1, 2]"
        title="the columns of WΛ" :title-color="PURPLE"
      />
      <LineChart
        :series="[0, 1, 2].map((k) => ({ points: Array.from(row(pair.H2, k), (v, i) => [i, v]), color: colors[k], width: 2.2 }))"
        :hlines="[{ y: 0, color: '#9aa0a6' }]" :x-domain="[0, H.c - 1]" :y-domain="[-1, hMax]" :x-ticks="[]" :y-ticks="[0, 1, 2]"
        title="the rows of Λ⁻¹H" :title-color="GOLD"
      />
      <div class="col">
        <MatView :M="pair.Y" ramp="x" :vmax="1.05" :border="BLUE" title="their product" :title-color="BLUE" />
        <Readout :items="[{ label: '‖X − WH‖', value: pair.err.toFixed(4) }, { label: 'negative entries', value: `${pair.neg}`, color: pair.neg ? RED : GREEN }]" />
      </div>
    </div>
    <div class="controls">
      <Knob v-model="s1" :min="0.25" :max="2.5" :step="0.01" label="λ₁ (scale w₁)" :color="PURPLE" />
      <Knob v-model="s2" :min="0.25" :max="2.5" :step="0.01" label="λ₂ (scale w₂)" :color="GOLD" />
      <Toggle v-model="swap" label="swap components 1 and 2" color="#1b1b1b" />
      <Knob v-model="mix" :min="-0.6" :max="0.6" :step="0.01" label="mix w₁ into w₂" :color="RED" />
    </div>
    <div class="cols3 legend">
      <div><b :style="{ color: GREEN }">Λ diagonal</b>: always legal; the scale of a component is pure convention. Fixed by normalising ‖w<sub>k</sub>‖ = 1.</div>
      <div><b :style="{ color: GREEN }">Λ a permutation</b>: the components come back in another order, so "component 3" means nothing across two runs.</div>
      <div><b :style="{ color: RED }">Λ general</b>: legal while WΛ ≥ 0 and Λ⁻¹H ≥ 0 (a wider cone also fits the data). Not fixable.</div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.panels { display: grid; grid-template-columns: 1fr 1.2fr 0.9fr; gap: 1.4rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; gap: 0.3rem; min-height: 0; }
.legend { font-size: 0.75rem; color: #4a4a4a; line-height: 1.4; }
</style>
