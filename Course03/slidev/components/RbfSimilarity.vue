<!-- svm_similarity: a kernel is a similarity, and the prediction is a vote of
     similarities, one bump per support vector. γ sets how far a point's
     influence reaches. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const gamma = ref(1)

const dGrid: number[] = []
for (let i = 0; i <= 200; i++) dGrid.push((3 * i) / 200)
const kCurve = computed(() => dGrid.map((d) => [d, Math.exp(-gamma.value * d * d)] as [number, number]))
const refCurves = [0.2, 1, 5].map((g, i) => ({
  points: dGrid.map((d) => [d, Math.exp(-g * d * d)] as [number, number]),
  color: [BLUE, GREEN, RED][i],
  width: 1.2,
  opacity: 0.35,
}))

const sv: [number, number][] = [[-2, 1], [-0.8, 1], [0.5, -1], [1.4, -1], [2.4, 1]]
const xGrid: number[] = []
for (let i = 0; i <= 400; i++) xGrid.push(-3.4 + (7 * i) / 400)

const bumps = computed(() =>
  sv.map(([x0, s]) => ({
    points: xGrid.map((x) => [x, s * Math.exp(-gamma.value * (x - x0) ** 2)] as [number, number]),
    color: s > 0 ? RED : BLUE,
    width: 1.2,
    opacity: 0.55,
  })),
)
const total = computed(() =>
  xGrid.map((x) => {
    let f = 0
    for (const [x0, s] of sv) f += s * Math.exp(-gamma.value * (x - x0) ** 2)
    return [x, f] as [number, number]
  }),
)
const reach = computed(() => Math.sqrt(1 / gamma.value)) // where k drops to 1/e
</script>

<template>
  <div class="wrap">
    <div class="charts">
      <LineChart
        :series="[...refCurves, { points: kCurve, color: INK, width: 2.8 }]"
        :x-domain="[0, 3]" :y-domain="[0, 1.05]"
        :x-ticks="[0, 1, 2, 3]" :y-ticks="[0, 0.5, 1]"
        x-label="distance ‖x − x′‖" y-label="k(x, x′)"
        title="RBF: k(x, x′) = exp(−γ‖x − x′‖²)"
        :vlines="[{ x: Math.min(3, reach), color: GREEN, dash: '3,3' }]"
      />
      <LineChart
        :series="[...bumps, { points: total, color: INK, width: 2.8 }]"
        :hlines="[{ y: 0, color: MUTED, dash: '5,4' }]"
        :dots="sv.map(([x, s]) => ({ x, y: 0, color: s > 0 ? RED : BLUE, r: 4, marker: s > 0 ? 'triangle' : 'circle' }))"
        :x-domain="[-3.4, 3.6]" :y-domain="[-1.6, 1.8]"
        :x-ticks="[-3, -2, -1, 0, 1, 2, 3]"
        x-label="x" title="f(x) = Σ αᵢyᵢ k(x, xᵢ) + b"
      />
    </div>
    <div class="side">
      <Knob v-model="gamma" :min="0.05" :max="20" log label="γ" :color="GREEN" />
      <Readout :items="[{ label: 'reach (k = 1/e)', value: reach.toFixed(2), color: GREEN }]" />
      <p class="note">
        <span :style="{ color: BLUE }">Small γ</span>: far points still count as similar;
        the sum is smooth, each support vector speaks for a wide region.
      </p>
      <p class="note">
        <span :style="{ color: RED }">Large γ</span>: only near neighbours count;
        the bumps stop overlapping and every point becomes its own island.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.charts { display: grid; grid-template-columns: 1fr 1.15fr; gap: 1.6rem; min-height: 0; }
.side { display: grid; grid-template-columns: auto auto 1fr 1fr; gap: 0 1.2rem; align-items: center; }
.note { font-size: 0.75rem; color: v-bind(MUTED); margin: 0; line-height: 1.4; }
</style>
