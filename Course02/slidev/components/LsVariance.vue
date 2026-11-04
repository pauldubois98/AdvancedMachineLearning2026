<!-- ls_variance: 60 samples, 60 fitted lines. Spread the x out and the lines
     agree; bunch them together and the slope is guessed. The cloud of
     estimates follows Var(β̂) = σ²(XᵀX)⁻¹ (the ellipses). -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { fitLine, fmt } from '../lib/reg'
import { lineSeg } from '../lib/draw'
import type { Cov, Pt } from '../lib/geom'
import { BLUE, INK, MUTED, RED } from '../lib/theme'

const spread = ref(0.7)
const sigma = ref(0.9)
const n = ref(25)
function sim(s: number, seed: number) {
  const rng = new Rng(seed)
  const betas: Pt[] = []
  let last = { x: [] as number[], y: [] as number[] }
  for (let r = 0; r < 60; r++) {
    const x = Array.from({ length: n.value }, () => rng.uniform(-s, s))
    const y = x.map((v) => 0.6 + 1.1 * v + rng.normal(0, sigma.value))
    betas.push(fitLine(x, y))
    last = { x, y }
  }
  return { betas, last }
}
const cur = computed(() => sim(spread.value, 21))
const ref_ = computed(() => sim(2.6, 22))
// the theory, for x uniform on [-s, s]: XᵀX ≈ n diag(1, s²/3)
const cov = (s: number): Cov => [sigma.value ** 2 / n.value, 0, (3 * sigma.value ** 2) / (n.value * s * s)]
const sd1 = computed(() => Math.sqrt(cov(spread.value)[2]))
const col = computed(() => (spread.value < 1.5 ? RED : BLUE))
</script>

<template>
  <div class="cmp">
    <div class="r3" style="grid-template-columns: 1fr 1fr 1fr">
      <Plane :X="ref_.last.x.map((v, i) => [v, ref_.last.y[i]])" :colors="INK" :alpha="0.6" :size="2.5" :domain="[-3.6, 3.6, -5.5, 6.5]" :equal="false"
        :segments="[...ref_.betas.map((b) => lineSeg(b, -3.4, 3.4, BLUE, 0.9)), lineSeg([0.6, 1.1], -3.4, 3.4, INK, 2, [6, 4])]"
        title="x spread out (s = 2.6)" :title-color="BLUE" caption="60 samples" />
      <Plane :X="cur.last.x.map((v, i) => [v, cur.last.y[i]])" :colors="INK" :alpha="0.6" :size="2.5" :domain="[-3.6, 3.6, -5.5, 6.5]" :equal="false"
        :segments="[...cur.betas.map((b) => lineSeg(b, -3.4, 3.4, col, 0.9)), lineSeg([0.6, 1.1], -3.4, 3.4, INK, 2, [6, 4])]"
        :title="`x on [−s, s], s = ${spread.toFixed(2)}`" :title-color="col" caption="60 samples" />
      <Plane :X="[...ref_.betas, ...cur.betas]" :colors="[...ref_.betas.map(() => BLUE), ...cur.betas.map(() => col)]" :alpha="0.6" :size="3"
        :ellipses="[{ mu: [0.6, 1.1], S: cov(2.6), color: BLUE, nsig: [2], width: 1.2, dash: [4, 3] }, { mu: [0.6, 1.1], S: cov(spread), color: col, nsig: [2], width: 1.2, dash: [4, 3] }]"
        :markers="[{ at: [0.6, 1.1], color: INK, shape: 'x', size: 7 }]" :domain="[-0.4, 1.6, -1.2, 3.4]" :equal="false" axes x-label="β̂₀" y-label="β̂₁"
        title="Var(β̂) = σ² (XᵀX)⁻¹" />
    </div>
    <div class="foot">the sd of the slope is about σ √3 / (s √n) = <b :style="{ color: col }">{{ fmt(sd1, 3) }}</b>; dashed: 2 sd ellipses from the formula</div>
    <div class="controls">
      <Knob v-model="spread" :min="0.2" :max="3" :step="0.01" label="spread s" :color="col" />
      <Knob v-model="sigma" :min="0.1" :max="2" :step="0.01" label="noise σ" :color="MUTED" />
      <Knob v-model="n" :min="5" :max="200" :step="1" :digits="0" label="n" :color="INK" />
    </div>
  </div>
</template>
