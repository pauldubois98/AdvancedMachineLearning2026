<!-- loglik_landscape: the observed log-likelihood over (mu1, mu2), the other
     parameters held fixed. Click anywhere on the map to put the two means
     there; the fit it stands for is drawn on the right. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, ANIMAL_FIT, linspace, loglik1, mixPdf1, weighted1 } from '../lib/gmm'
import { bars, curve, edges, fmt } from '../lib/charts'
import { BLUE, COMP, INK, MUTED, RED } from '../lib/theme'

const sd = ref(1.55)
const mu1 = ref(88)
const mu2 = ref(91)
const LO = 83.5, HI = 95
// the log-likelihood depends on the data only through the 16 distinct
// lengths: weight each by its count, so the map is cheap to recompute
const LEN = [...new Set(ANIMALS)]
const CNT = LEN.map((l) => ANIMALS.filter((v) => v === l).length)
function ll(a: number, b: number, s: number) {
  let t = 0
  for (let i = 0; i < LEN.length; i++) {
    const f = mixPdf1(LEN[i], { p: [0.5, 0.5], mu: [a, b], sd: [s, s] })
    t += CNT[i] * Math.log(Math.max(f, 1e-300))
  }
  return t
}
const span = computed(() => {
  // the colour scale: from the 55th percentile to the top, as the figure does
  const vals: number[] = []
  for (const a of linspace(LO, HI, 40)) for (const b of linspace(LO, HI, 40)) vals.push(ll(a, b, sd.value))
  vals.sort((x, y) => x - y)
  return [vals[Math.floor(0.55 * vals.length)], vals[vals.length - 1]]
})
const field = computed(() => {
  const s = sd.value
  return (a: number, b: number) => ll(a, b, s)
})
function blues(v: number): [number, number, number] {
  const [lo, hi] = span.value
  const t = Math.min(1, Math.max(0, (v - lo) / (hi - lo)))
  // matplotlib "Blues", white to deep blue
  return [Math.round(247 - t * (247 - 8)), Math.round(251 - t * (251 - 48)), Math.round(255 - t * (255 - 107))]
}
const m = computed(() => ({ p: [0.5, 0.5], mu: [mu1.value, mu2.value], sd: [sd.value, sd.value] }))
const here = computed(() => ll(mu1.value, mu2.value, sd.value))
const grid = linspace(79, 101, 300)
const hist = bars(ANIMALS, edges(81.5, 98.5, 1), { density: true })
const best = ANIMAL_FIT.mu
</script>

<template>
  <div class="wrap">
    <div class="note top">Observed log-likelihood over (μ₁, μ₂), with p = ½ and both widths held fixed. Click the map.</div>
    <div class="body">
      <Plane
        :domain="[LO, HI, LO, HI]" :field="field" :field-color="blues" :field-res="70"
        :levels="[{ f: (a: number, b: number) => a - b, level: 0, color: MUTED, width: 1.2, dash: [2, 4] }]"
        :markers="[
          { at: [best[0], best[1]], color: RED, shape: 'star', size: 11 },
          { at: [best[1], best[0]], color: RED, shape: 'star', size: 11 },
          { at: [mu1, mu2], color: INK, shape: 'ring', size: 7 },
        ]"
        axes x-label="μ₁" y-label="μ₂" pickable @pick="(a: number, b: number) => { mu1 = a; mu2 = b }"
      />
      <div class="right">
        <LineChart
          :series="[
            ...[0, 1].map((k) => ({ points: curve(grid, (x) => weighted1(x, m)[k]), color: COMP[k], width: 1.8, dash: '6 4' })),
            { points: curve(grid, (x) => mixPdf1(x, m)), color: INK, width: 2.4 },
          ]"
          :bars="hist" :x-domain="[79, 101]" :y-domain="[0, 0.2]" x-label="length (mm)" :x-ticks="[80, 85, 90, 95, 100]" :y-ticks="[]"
          :title="`μ = (${mu1.toFixed(1)}, ${mu2.toFixed(1)}): ℓ = ${fmt(here)}`" :unit-height="260"
        />
        <div class="side">
          <p>— <b :style="{ color: RED }">Two maxima</b> (red stars), mirror images of one another</p>
          <p>— The dotted diagonal μ₁ = μ₂ is a ridge of saddle points</p>
          <p class="note">Non-concave, with as many maxima as relabellings; and these are only two of the five parameters.</p>
        </div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="mu1" :min="LO" :max="HI" :step="0.05" label="μ₁" :digits="1" :color="COMP[0]" />
      <Knob v-model="mu2" :min="LO" :max="HI" :step="0.05" label="μ₂" :digits="1" :color="COMP[1]" />
      <Knob v-model="sd" :min="0.8" :max="4" :step="0.05" label="width σ (both)" :color="BLUE" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 1.15fr; gap: 1.8rem; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; min-height: 0; }
.side { font-size: 0.8rem; }
</style>
