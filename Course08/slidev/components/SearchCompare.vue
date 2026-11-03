<!-- search_compare: grid search, random search and Bayesian optimisation
     (a Gaussian-process surrogate and expected improvement, after five random
     starts) on the same surface with the same budget. Each trial is measured
     with optional noise; the best measured trial is kept, and its true AUC is
     reported. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmax, ei, gp, valSurface } from '../lib/c08'
import { Rng } from '../lib/rng'
import { GREEN, INK, viridis } from '../lib/theme'

const budget = ref(25)
const seed = ref(1)
const noise = ref(0)
const MAXB = 64
const LO = 0.375
const HI = 0.86
const field = (x: number, y: number) => (valSurface(x, y) - LO) / (HI - LO)
type P = [number, number]
const toU = (p: P): number[] => [(p[0] + 4) / 4, (p[1] - 2) / 12]
const fromU = (u: number[]): P => [u[0] * 4 - 4, u[1] * 12 + 2]

const grid = computed<P[]>(() => {
  const g = Math.max(1, Math.floor(Math.sqrt(budget.value)))
  const out: P[] = []
  for (let i = 0; i < g; i++) for (let j = 0; j < g; j++) out.push([-4 + (4 * (i + 0.5)) / g, 2 + (12 * (j + 0.5)) / g])
  return out
})
const random = computed<P[]>(() => {
  const rng = new Rng(seed.value)
  return Array.from({ length: MAXB }, () => [rng.uniform(-4, 0), rng.uniform(2, 14)] as P)
})
const CANDS: number[][] = []
for (let i = 0; i <= 28; i++) for (let j = 0; j <= 28; j++) CANDS.push([i / 28, j / 28])
const measure = (p: P, rng: Rng) => valSurface(p[0], p[1]) + rng.normal(0, noise.value)
// one Bayesian-optimisation run to the largest budget; the slider shows a prefix
const bo = computed(() => {
  const rng = new Rng(1000 + seed.value)
  const pts: P[] = []
  const ys: number[] = []
  for (let t = 0; t < MAXB; t++) {
    let next: P
    if (t < 5) next = [rng.uniform(-4, 0), rng.uniform(2, 14)]
    else {
      const m = ys.reduce((a, b) => a + b, 0) / ys.length
      const s = Math.sqrt(ys.reduce((a, b) => a + (b - m) ** 2, 0) / ys.length) || 1
      // minimise the standardised negative AUC
      const z = ys.map((y) => -(y - m) / s)
      const post = gp(pts.map(toU), z, CANDS, [0.22, 0.22], 0.05, 1)
      const best = Math.min(...z)
      next = fromU(CANDS[argmax(post.mu.map((mu, i) => ei(mu, post.sd[i], best, 0.01)))])
    }
    pts.push(next)
    ys.push(measure(next, rng))
  }
  return { pts, ys }
})
function result(pts: P[], ys: number[]) {
  const k = argmax(ys)
  return { pts, best: valSurface(pts[k][0], pts[k][1]), at: pts[k] }
}
const panels = computed(() => {
  const rg = new Rng(77 + seed.value)
  const gy = grid.value.map((p) => measure(p, rg))
  const rr = random.value.slice(0, budget.value)
  const rng = new Rng(99 + seed.value)
  return [
    { name: `grid search (${grid.value.length} trials)`, ...result(grid.value, gy) },
    { name: 'random search', ...result(rr, rr.map((p) => measure(p, rng))) },
    { name: 'Bayesian optimisation', ...result(bo.value.pts.slice(0, budget.value), bo.value.ys.slice(0, budget.value)) },
  ]
})
const winner = computed(() => argmax(panels.value.map((p) => p.best)))
</script>

<template>
  <div class="wrap">
    <div class="note top">The same surface, the same budget of {{ budget }} trials</div>
    <div class="body">
      <Plane
        v-for="(p, i) in panels" :key="i"
        :domain="[-4, 0, 2, 14]" :equal="false" axes x-label="log₁₀ η" :y-label="i ? '' : 'max depth'"
        :field="field" :field-color="viridis" :field-res="80"
        :markers="[
          ...p.pts.map((q) => ({ at: q, color: '#ffffff', shape: 'dot' as const, size: 3.6 })),
          ...p.pts.map((q) => ({ at: q, color: INK, shape: 'ring' as const, size: 3.6 })),
          { at: p.at, color: i === winner ? GREEN : '#ffffff', shape: 'star' as const, size: 9 },
        ]"
        :title="`${p.name}<br>best AUC ${p.best.toFixed(4)}`" :title-color="i === winner ? GREEN : INK"
      />
    </div>
    <div class="controls">
      <Knob v-model="budget" :min="4" :max="MAXB" :step="1" :digits="0" label="budget (trials)" />
      <Knob v-model="noise" :min="0" :max="0.03" :step="0.001" :digits="3" label="measurement noise" />
      <Knob v-model="seed" :min="1" :max="30" :step="1" :digits="0" label="seed" />
      <span class="note">the true optimum is 0.8600; star: the trial each method would keep</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.2rem; min-height: 0; }
</style>
