<!-- em_monotone: every pass increases the observed log-likelihood. The gap to
     the best value, on a log scale: a straight line means the gap shrinks by
     a fixed factor per pass. Your own start is the purple curve. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, em1 } from '../lib/gmm'
import { logTicks } from '../lib/ticks'
import { BLUE, GOLD, GREEN, PURPLE, RED } from '../lib/theme'

const start = (a: number, b: number) => ({ p: [0.5, 0.5], mu: [a, b], sd: [3, 3] })
const best = em1(ANIMALS, start(84, 95), 400).at(-1)!.ll
const T = 40
const FIXED = [
  { name: 'a mediocre start', color: BLUE, mu: [87.5, 90.5] },
  { name: 'a good start', color: GOLD, mu: [84, 95] },
  { name: 'a symmetric start', color: GREEN, mu: [89, 89.5] },
].map((r) => ({ ...r, tr: em1(ANIMALS, start(r.mu[0], r.mu[1]), T).map((h) => h.ll) }))
const mu1 = ref(83)
const mu2 = ref(86)
const mine = computed(() => em1(ANIMALS, start(mu1.value, mu2.value), T).map((h) => h.ll))
const FLOOR = 1e-9
function gapSeries(tr: number[]): [number, number][] {
  const out: [number, number][] = []
  for (let i = 0; i < tr.length; i++) {
    const g = best - tr[i]
    if (g < FLOOR) { out.push([i, FLOOR]); break }
    out.push([i, g])
  }
  return out
}
const series = computed(() => [
  ...FIXED.map((r) => ({ points: gapSeries(r.tr), color: r.color, width: 2.2 })),
  { points: gapSeries(mine.value), color: PURPLE, width: 2.2, dash: '6 3' },
])
const stuck = computed(() => best - mine.value[T] > 1)
</script>

<template>
  <div class="wrap">
    <div class="note top">Every pass increases the observed log-likelihood</div>
    <div class="body">
      <LineChart
        :series="series" log-y
        :labels="FIXED.map((r) => ({ x: 26, y: r.name === 'a symmetric start' ? 200 : r.name === 'a good start' ? 1e-7 : 1e-4, text: r.name, color: r.color, size: 12 }))"
        :x-domain="[0, T]" :y-domain="[FLOOR, 2000]" x-label="pass t" y-label="ℓ* − ℓ_obs(θᵗ)"
        :x-ticks="[0, 10, 20, 30, 40]" :y-ticks="[1e-9, 1e-6, 1e-3, 1, 1000]"
      />
      <div class="side">
        <div class="h" :style="{ color: GREEN }">Guaranteed</div>
        <p>— ℓ<sub>obs</sub>(θᵗ⁺¹) ≥ ℓ<sub>obs</sub>(θᵗ)</p>
        <p>— the sequence is bounded above</p>
        <p>— hence it converges, to a stationary point of ℓ<sub>obs</sub></p>
        <div class="h" :style="{ color: RED }">Not guaranteed</div>
        <p>— the limit is the global maximum</p>
        <p>— it can get stuck at a saddle (green run)</p>
        <p class="note">ℓ*: the best value reached. Your start (purple, dashed) {{ stuck ? 'ends below it: a different fixed point' : 'reaches it' }}.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="mu1" :min="82" :max="97" :step="0.1" label="your start μ₁" :digits="1" :color="PURPLE" />
      <Knob v-model="mu2" :min="82" :max="97" :step="0.1" label="your start μ₂" :digits="1" :color="PURPLE" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
</style>
