<!-- distance_zoo: the unit ball of the Lq distance as q moves from Manhattan
     through Euclidean to Chebyshev, and Mahalanobis, whose shape the data sets. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { BLUE, GOLD, GREEN, GRID, MUTED, PURPLE } from '../lib/theme'

const q = ref(2)
const rho = ref(0.78)

/** the set { x : ||x||_q = 1 }, in polar form */
const ball = computed(() => {
  const pts: [number, number][] = []
  for (let i = 0; i <= 720; i++) {
    const t = (2 * Math.PI * i) / 720
    const c = Math.cos(t)
    const s = Math.sin(t)
    const r = (Math.abs(c) ** q.value + Math.abs(s) ** q.value) ** (-1 / q.value)
    pts.push([r * c, r * s])
  }
  return pts
})
const color = computed(() => (q.value < 1.3 ? GREEN : q.value > 4 ? GOLD : BLUE))

/** the curve as segments, plus the two axes, for the equal-aspect panel */
const ballEdges = computed(() => {
  const out: { a: [number, number]; b: [number, number]; color: string; width: number }[] = [
    { a: [-1.6, 0], b: [1.6, 0], color: GRID, width: 1 },
    { a: [0, -1.6], b: [0, 1.6], color: GRID, width: 1 },
  ]
  for (let i = 0; i < ball.value.length - 1; i++) {
    out.push({ a: ball.value[i], b: ball.value[i + 1], color: color.value, width: 2.6 })
  }
  return out
})

const name = computed(() =>
  q.value < 1.15 ? 'Manhattan, q = 1' : q.value < 2.2 && q.value > 1.8 ? 'Euclidean, q = 2'
    : q.value > 7 ? 'Chebyshev, q → ∞' : `q = ${q.value.toFixed(1)}`,
)
/** the distance from the origin to (1, 1) in this norm: what changes with q */
const diag = computed(() => 2 ** (1 / q.value))

const cloud = computed(() => {
  const rng = new Rng(3)
  const X: number[][] = []
  const r = rho.value
  for (let i = 0; i < 220; i++) {
    const a = rng.normal(0, 1)
    const b = rng.normal(0, 1)
    X.push([a, r * a + Math.sqrt(Math.max(1e-9, 1 - r * r)) * b * 0.9])
  }
  return X
})
/** the two Mahalanobis contours, as an ellipse of the covariance */
const ell = computed(() => {
  const r = rho.value
  const sxx = 1
  const syy = 0.81 + r * r * 0.19
  const sxy = r * 0.9 + r * (1 - 0.9) * 0
  const tr = sxx + syy
  const det = sxx * syy - sxy * sxy
  const l1 = tr / 2 + Math.sqrt(Math.max(0, (tr / 2) ** 2 - det))
  const l2 = tr / 2 - Math.sqrt(Math.max(0, (tr / 2) ** 2 - det))
  const angle = (Math.atan2(2 * sxy, sxx - syy) / 2) * (180 / Math.PI)
  return [1, 2].map((s) => ({
    x: 0, y: 0, rx: s * Math.sqrt(l1), ry: s * Math.sqrt(Math.max(1e-6, l2)),
    angle, color: PURPLE, dash: [] as number[], width: 2,
  }))
})
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <div class="col">
        <ClusterPlot
          :X="ball" :points="false" :domain="[-1.7, 1.7, -1.7, 1.7]" :edges="ballEdges"
          :title="name" :title-color="color"
        />
        <div class="note">points at distance 1 from the origin</div>
      </div>
      <div class="col">
        <ClusterPlot
          :X="cloud" :point-size="2.2" :point-alpha="0.5" :ellipses="ell"
          :domain="[-3.4, 3.4, -3, 3]"
          title="Mahalanobis: (x − y)ᵀ Σ⁻¹ (x − y)" :title-color="PURPLE"
        />
        <div class="note">the data sets the shape</div>
      </div>
      <div class="side">
        <table class="plain">
          <tr><th>q</th><th>name</th><th>‖(1,1)‖</th></tr>
          <tr><td>1</td><td>Manhattan</td><td>2.00</td></tr>
          <tr><td>2</td><td>Euclidean</td><td>1.41</td></tr>
          <tr><td>∞</td><td>Chebyshev</td><td>1.00</td></tr>
          <tr><td :style="{ color }">{{ q.toFixed(1) }}</td><td :style="{ color }">now</td><td :style="{ color }">{{ diag.toFixed(2) }}</td></tr>
        </table>
        <p class="note mt-3">Σ is the covariance of the cloud: correlated
          columns make the circle an ellipse, and distance follows the data.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="q" :min="1" :max="12" label="q of the Lq distance" :color="color" />
      <Knob v-model="rho" :min="-0.95" :max="0.95" label="correlation in the cloud" :color="PURPLE" />
      <Readout :items="[{ label: 'distance from (0,0) to (1,1)', value: diag.toFixed(3), color }]" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1.05fr 0.78fr; gap: 1.2rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.col .note { text-align: center; }
.side { align-self: center; font-size: 0.85rem; }
.controls { display: flex; gap: 1.4rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 13rem; }
</style>
