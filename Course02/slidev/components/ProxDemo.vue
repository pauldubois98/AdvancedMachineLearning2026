<!-- eq_prox, live: proximal gradient on a 2-D problem. Each iteration is a
     gradient step on the smooth loss (blue), then the closed-form proximal step
     for the penalty (red). Push θ past 2/‖XᵀX‖ and the iterates blow up. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { fmt, hard, soft } from '../lib/reg'
import type { Pt } from '../lib/geom'
import type { Seg } from './Plane.vue'
import { BLUE, GREEN, GRID, INK, MUTED, RED } from '../lib/theme'

const pen = ref('l1')
const lam = ref(0.6)
const frac = ref(0.5) // θ as a fraction of 2/‖A‖
const K = ref(8)
const A = [[1.0, 0.75], [0.75, 1.3]]
const bls: Pt = [1.55, 1.05]
const Lmax = (A[0][0] + A[1][1]) / 2 + Math.sqrt(((A[0][0] - A[1][1]) / 2) ** 2 + A[0][1] ** 2)
const theta = computed(() => (2 / Lmax) * frac.value)
const loss = (x: number, y: number) => { const u = x - bls[0], v = y - bls[1]; return 0.5 * (A[0][0] * u * u + 2 * A[0][1] * u * v + A[1][1] * v * v) }
const R = (p: Pt) => (pen.value === 'l1' ? Math.abs(p[0]) + Math.abs(p[1]) : (p[0] ? 1 : 0) + (p[1] ? 1 : 0))
const run = computed(() => {
  let b: Pt = [-0.6, 1.9]
  const segs: Seg[] = []
  const pts: Pt[] = [b]
  const th = theta.value, t = lam.value * th
  for (let k = 0; k < K.value; k++) {
    const u = b[0] - bls[0], v = b[1] - bls[1]
    const g: Pt = [A[0][0] * u + A[0][1] * v, A[0][1] * u + A[1][1] * v]
    const bar: Pt = [b[0] - th * g[0], b[1] - th * g[1]]
    const nb: Pt = pen.value === 'l1' ? [soft(bar[0], t), soft(bar[1], t)] : [hard(bar[0], t), hard(bar[1], t)]
    segs.push({ a: b, b: bar, color: BLUE, width: 1.8, arrow: true }, { a: bar, b: nb, color: RED, width: 1.8, arrow: true })
    b = nb
    pts.push(b)
  }
  return { segs, pts, b }
})
const obj = computed(() => loss(run.value.b[0], run.value.b[1]) + lam.value * R(run.value.b))
const diverge = computed(() => frac.value >= 1)
const dom: [number, number, number, number] = [-1.2, 2.6, -1, 2.3]
const axes: Seg[] = [{ a: [-5, 0], b: [5, 0], color: GRID, width: 1 }, { a: [0, -5], b: [0, 5], color: GRID, width: 1 }]
const levels = [0.02, 0.15, 0.5, 1.1, 2].map((l) => ({ f: loss, level: l, color: MUTED, width: 1 }))
</script>

<template>
  <div class="prox">
    <Plane :domain="dom" :segments="[...axes, ...run.segs]" :levels="levels" :X="run.pts" :colors="INK" :size="3"
      :markers="[{ at: bls, color: INK, shape: 'x', size: 6 }, { at: run.b, color: GREEN, shape: 'dot', size: 6 }]"
      :texts="[{ at: [bls[0] + 0.08, bls[1] + 0.12], text: 'least squares', color: MUTED, size: 12 }]" />
    <div class="side">
      <Choice v-model="pen" :options="[{ value: 'l1', label: 'R = ‖β‖₁', color: GREEN }, { value: 'l0', label: 'R = ‖β‖₀', color: RED }]" />
      <p style="margin-top: 0.6rem"><span :style="{ color: BLUE }">blue</span>: gradient step, <span :style="{ color: RED }">red</span>: proximal step</p>
      <p>θ = {{ fmt(theta, 3) }}, and 2/‖XᵀX‖ = {{ fmt(2 / Lmax, 3) }}</p>
      <p>after {{ K }} iterations: β = ({{ fmt(run.b[0], 3) }}, {{ fmt(run.b[1], 3) }})</p>
      <p>objective L(β) + λR(β) = <b>{{ Number.isFinite(obj) && obj < 1e6 ? fmt(obj, 4) : '∞' }}</b></p>
      <p v-if="diverge" :style="{ color: RED, fontWeight: 600 }">θ ≥ 2/‖XᵀX‖: no convergence</p>
      <p v-else-if="run.b[0] === 0 || run.b[1] === 0" :style="{ color: GREEN }">a coefficient is exactly 0</p>
      <div class="knobs">
        <Knob v-model="lam" :min="0" :max="1.5" :step="0.01" label="λ" :color="INK" />
        <Knob v-model="frac" :min="0.05" :max="1.1" :step="0.01" label="θ × ‖XᵀX‖/2" :color="diverge ? RED : BLUE" />
        <Knob v-model="K" :min="0" :max="40" :step="1" :digits="0" label="iterations" :color="MUTED" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.prox { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.5rem; min-height: 0; height: 100%; }
.knobs { display: grid; gap: 0.6rem; margin-top: 0.8rem; }
</style>
