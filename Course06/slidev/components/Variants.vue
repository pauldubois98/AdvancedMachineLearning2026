<!-- em_variants: same data, same start. The distance to the best fit, on a
     log scale: EM goes straight down, the hard version stops short, SEM keeps
     jumping, and N-SEM jumps less as N grows. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, em1, sem1 } from '../lib/gmm'
import { BLUE, GOLD, GREEN, INK, PURPLE } from '../lib/theme'

const T = 60
const start = { p: [0.5, 0.5], mu: [87.5, 90.5], sd: [3, 3] }
const N = ref(5)
const seed = ref(5)
const em = em1(ANIMALS, start, T).map((h) => h.ll)
const best = Math.max(...em)
const FLOOR = 1e-4
const gap = (tr: number[]): [number, number][] => {
  const out: [number, number][] = []
  for (let i = 0; i < tr.length; i++) {
    const g = best - tr[i]
    if (g < FLOOR) { out.push([i, FLOOR]); break }
    out.push([i, g])
  }
  return out
}
const hard = sem1(ANIMALS, start, T, { hard: true }).map((h) => h.ll)
const sem = computed(() => sem1(ANIMALS, start, T, { seed: seed.value }).map((h) => h.ll))
const Nint = computed(() => Math.max(1, Math.round(N.value)))
const nsem = computed(() => sem1(ANIMALS, start, T, { seed: seed.value, N: Nint.value }).map((h) => h.ll))
const late = (tr: number[]) => tr.slice(30).reduce((a, v) => a + (best - v), 0) / (tr.length - 30)
</script>

<template>
  <div class="wrap">
    <div class="note top">Same data, same start: more draws per point, less noise, and N-SEM tends to EM</div>
    <div class="body">
      <LineChart
        log-y
        :series="[
          { points: gap(hard), color: BLUE, width: 1.8 },
          { points: gap(sem), color: GOLD, width: 1.7 },
          { points: gap(nsem), color: PURPLE, width: 1.9 },
          { points: gap(em), color: GREEN, width: 2.6 },
        ]"
        :x-domain="[0, T]" :y-domain="[FLOOR, 200]" x-label="pass t" y-label="ℓ* − ℓ_obs(θᵗ)"
        :x-ticks="[0, 10, 20, 30, 40, 50, 60]" :y-ticks="[1e-4, 1e-3, 0.01, 0.1, 1, 10, 100]"
      />
      <div class="side">
        <p><b :style="{ color: GREEN }">EM</b>: straight down</p>
        <p><b :style="{ color: BLUE }">hard (k-means)</b>: stops {{ (best - hard[T]).toFixed(2) }} below</p>
        <p><b :style="{ color: GOLD }">SEM (N = 1)</b>: keeps jumping, {{ late(sem).toFixed(3) }} below on average after pass 30</p>
        <p><b :style="{ color: PURPLE }">N-SEM (N = {{ Nint }})</b>: {{ late(nsem).toFixed(3) }} below on average</p>
        <p class="note" style="margin-top: 0.6rem">ℓ*: the best fit, found by EM. N labels per point; N → ∞ is EM.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="N" :min="1" :max="200" log label="draws per point N" :color="PURPLE" />
      <Knob v-model="seed" :min="1" :max="60" :step="1" label="seed" :digits="0" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.7fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
</style>
