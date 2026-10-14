<!-- hinge_loss: the margin is the penalty, the hinge is the loss.
     Slide the margin of one point and read what each loss charges for it. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GOLD, GREEN, INK, MUTED } from '../lib/theme'

const m = ref(0.4)

const grid: number[] = []
for (let i = 0; i <= 300; i++) grid.push(-2.5 + (5.5 * i) / 300)

const hinge = (v: number) => Math.max(0, 1 - v)
const logistic = (v: number) => Math.log1p(Math.exp(-v)) / Math.LN2
const squared = (v: number) => (1 - v) ** 2
const zeroOne = (v: number) => (v < 0 ? 1 : 0)

const series = [
  { points: grid.map((v) => [v, hinge(v)] as [number, number]), color: GREEN, width: 2.8 },
  { points: grid.map((v) => [v, logistic(v)] as [number, number]), color: BLUE, width: 2.2, dash: '6,4' },
  { points: grid.map((v) => [v, squared(v)] as [number, number]), color: GOLD, width: 2.2, dash: '8,3,2,3' },
  { points: grid.map((v) => [v, zeroOne(v)] as [number, number]), color: INK, width: 1.8, step: true, opacity: 0.7 },
]
const dots = computed(() => [
  { x: m.value, y: hinge(m.value), color: GREEN, r: 5 },
  { x: m.value, y: logistic(m.value), color: BLUE, r: 4 },
  { x: m.value, y: squared(m.value), color: GOLD, r: 4 },
  { x: m.value, y: zeroOne(m.value), color: INK, r: 4 },
])
const state = computed(() =>
  m.value < 0 ? 'on the wrong side' : m.value < 1 ? 'right, but inside the street' : 'right, and clear of the street',
)
const stateColor = computed(() => (m.value < 0 ? '#c53030' : m.value < 1 ? GOLD : GREEN))
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="series" :dots="dots"
      :vlines="[{ x: 1, color: '#cccfd2', dash: '2,3' }, { x: m, color: stateColor, dash: '' }]"
      :x-domain="[-2.5, 3]" :y-domain="[-0.1, 3]"
      :x-ticks="[-2, -1, 0, 1, 2, 3]" :y-ticks="[0, 1, 2, 3]"
      x-label="margin  y·f(x)" y-label="loss of one point"
      title="the hinge loss" :title-color="GREEN"
      :labels="[
        { x: 0.9, y: 0.08, text: '0 / 1', color: INK, size: 11 },
        { x: 1.05, y: 2.75, text: 'margin', color: MUTED, size: 11 },
      ]"
    />
    <div class="side">
      <Knob v-model="m" :min="-2.5" :max="3" :step="0.01" label="margin of one point" :color="stateColor" />
      <p class="state" :style="{ color: stateColor }">{{ state }}</p>
      <table>
        <thead>
          <tr><th>model</th><th>penalty</th><th>+ loss</th><th>charge here</th></tr>
        </thead>
        <tbody>
          <tr :style="{ color: GREEN }">
            <td>SVM</td><td>½‖w‖²</td><td>hinge</td><td class="num">{{ hinge(m).toFixed(2) }}</td>
          </tr>
          <tr :style="{ color: BLUE }">
            <td>logistic + ridge</td><td>λ/2 ‖w‖²</td><td>log loss</td><td class="num">{{ logistic(m).toFixed(2) }}</td>
          </tr>
          <tr :style="{ color: GOLD }">
            <td>ridge regression</td><td>λ/2 ‖w‖²</td><td>squared loss</td><td class="num">{{ squared(m).toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
      <p class="note">
        The hinge is the only one that charges <em>nothing</em> once the point is
        past the margin; that is what makes most α<sub>i</sub> zero.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; align-items: center; }
.side { display: flex; flex-direction: column; gap: 0.5rem; }
.state { font-size: 0.85rem; font-weight: 600; margin: 0; }
table { font-size: 0.78rem; border-collapse: collapse; }
th { color: v-bind(MUTED); font-weight: 400; text-align: left; padding: 0 0.7rem 0.2rem 0; border-bottom: 1px solid #e3e5e8; }
td { padding: 0.14rem 0.7rem 0.14rem 0; }
.num { font-variant-numeric: tabular-nums; font-weight: 600; text-align: right; }
.note { font-size: 0.76rem; color: v-bind(MUTED); margin: 0; line-height: 1.45; }
em { font-style: italic; }
</style>
