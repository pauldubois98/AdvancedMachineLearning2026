<!-- kmeans_algorithm: initialise, assign, re-estimate, repeat, one half-step
     per tick of the slider; the inertia only ever goes down. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { assign, inertia, update } from '../lib/stats'
import type { Pt } from '../lib/geom'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const t = ref(0)
const start = ref(0) // 0: the bad start of the printed figure; k > 0: random points
const COLS = [BLUE, RED, GREEN]
const r = new Rng(23)
const centres: Pt[] = [[-1.6, -1.0], [1.7, -0.7], [0.1, 1.7]]
const X: Pt[] = centres.flatMap((c) => Array.from({ length: 70 }, () => [c[0] + r.normal(0, 0.55), c[1] + r.normal(0, 0.55)] as Pt))
const STEPS = 16
const run = computed(() => {
  let mu: Pt[]
  if (start.value === 0) mu = [[-2.4, 1.6], [-1.9, 1.2], [-2.1, 0.7]]
  else { const g = new Rng(start.value * 7 + 1); mu = [0, 1, 2].map(() => X[Math.floor(g.next() * X.length)]) }
  const out: { mu: Pt[]; s: number[] | null; J: number | null; what: string }[] = [{ mu, s: null, J: null, what: 'initialise: K centres' }]
  let s = assign(X, mu)
  for (let k = 1; k <= STEPS; k++) {
    if (k % 2) { s = assign(X, mu); out.push({ mu, s, J: inertia(X, s, mu), what: 'assign each point to its nearest centre' }) }
    else { mu = update(X, s, mu); out.push({ mu, s, J: inertia(X, s, mu), what: 'move each centre to the mean of its points' }) }
  }
  return out
})
const cur = computed(() => run.value[t.value])
const colors = computed(() => (cur.value.s ? cur.value.s.map((k) => COLS[k]) : MUTED))
// converged: an assignment half-step that changes no label
const done = computed(() => {
  const R = run.value
  for (let k = 3; k < R.length; k += 2) if (R[k].s!.every((v, i) => v === R[k - 2].s![i])) return k
  return -1
})
const Js = computed(() => run.value.slice(1).map((p, k) => [k + 1, p.J!] as [number, number]))
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> three groups of 70 points; K = 3. The slider runs the algorithm one half-step at a time. "Start" 0 is a deliberately bad start in a corner; other values pick 3 data points at random.</div>
    <div class="r23">
      <Plane :X="X" :colors="colors" :size="3" :domain="[-3.4, 3.4, -2.8, 3.2]"
        :markers="cur.mu.map((m, k) => ({ at: m, color: COLS[k], shape: 'x', size: 8 }))" :title="`step ${t}: ${cur.what}`" />
      <LineChart :series="[{ points: Js, color: INK, width: 2 }]" :dots="Js.map(([x, y]) => ({ x, y, color: x === t ? RED : INK, r: x === t ? 6 : 3 }))"
        :x-domain="[0.5, STEPS + 0.5]" :y-domain="[0, Math.max(...Js.map((p) => p[1])) * 1.08]" :x-ticks="[1, 4, 8, 12, 16]" :y-ticks="[]" x-label="half-step" title="inertia J<sub>w</sub> = Σ<sub>k</sub> Σ<sub>xᵢ ∈ Cₖ</sub> ‖xᵢ − μₖ‖²" />
    </div>
    <div class="foot">J<sub>w</sub> = <b>{{ cur.J === null ? 'not defined yet' : cur.J.toFixed(1) }}</b>. Both half-steps can only lower it, so the loop stops{{ done > 0 ? ` (here at step ${done})` : '' }}, at a local minimum that depends on the start.</div>
    <div class="controls">
      <Knob v-model="t" :min="0" :max="STEPS" :step="1" :digits="0" label="step" :color="RED" />
      <Knob v-model="start" :min="0" :max="30" :step="1" :digits="0" label="start" :color="INK" />
    </div>
  </div>
</template>
