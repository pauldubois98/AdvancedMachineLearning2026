<!-- xgb_gh: where g and h come from. Both are read off the loss at one row,
     at wherever the current prediction for that row happens to be. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, INK, MUTED, PURPLE, RED } from '../lib/theme'

const F = ref(0)
const loss = ref('log')
const y = ref('1')

const lossAt = (f: number) =>
  loss.value === 'log'
    ? Number(y.value) === 1 ? Math.log(1 + Math.exp(-f)) : Math.log(1 + Math.exp(f))
    : 0.5 * (Number(y.value) - f) ** 2
const gAt = (f: number) =>
  loss.value === 'log' ? 1 / (1 + Math.exp(-f)) - Number(y.value) : f - Number(y.value)
const hAt = (f: number) => {
  if (loss.value !== 'log') return 1
  const p = 1 / (1 + Math.exp(-f))
  return p * (1 - p)
}

const curve = computed(() => {
  const pts: [number, number][] = []
  for (let i = 0; i <= 240; i++) {
    const f = -3.4 + (6.8 * i) / 240
    pts.push([f, lossAt(f)])
  }
  return pts
})
const tangent = computed(() => {
  const g = gAt(F.value)
  const l = lossAt(F.value)
  return [[F.value - 1.9, l - 1.9 * g], [F.value + 1.9, l + 1.9 * g]] as [number, number][]
})
const quad = computed(() => {
  const g = gAt(F.value)
  const h = hAt(F.value)
  const l = lossAt(F.value)
  const pts: [number, number][] = []
  for (let i = -100; i <= 100; i++) {
    const d = (i / 100) * 2.1
    pts.push([F.value + d, l + g * d + 0.5 * h * d * d])
  }
  return pts
})
const p = computed(() => 1 / (1 + Math.exp(-F.value)))
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="[
        { points: curve, color: INK, width: 2.4 },
        { points: tangent, color: BLUE, width: 2, dash: '6,4' },
        { points: quad, color: PURPLE, width: 2 },
      ]"
      :dots="[{ x: F, y: lossAt(F), color: INK, r: 6 }]"
      :vlines="[{ x: F, color: MUTED, dash: '2,3' }]"
      :x-domain="[-3.4, 3.4]" :y-domain="[-0.35, 3.4]"
      :x-ticks="[-2, 0, 2]" :y-ticks="[0, 1, 2, 3]"
      x-label="prediction for row i, Fₘ₋₁(xᵢ)" y-label="that row's loss ℓ"
      title="both are read off the loss at one row"
      :labels="[
        { x: 0.3, y: 3.2, text: 'the row\'s loss ℓ', color: INK, size: 11.5 },
        { x: 0.3, y: 2.95, text: 'slope here → gᵢ', color: BLUE, size: 11.5 },
        { x: 0.3, y: 2.7, text: 'curvature here → hᵢ', color: PURPLE, size: 11.5 },
      ]"
    />
    <div class="right">
      <table class="plain">
        <thead>
          <tr><th>loss ℓ(yᵢ, F)</th><th>gᵢ = ∂ℓ/∂F</th><th>hᵢ = ∂²ℓ/∂F²</th></tr>
        </thead>
        <tbody>
          <tr :class="{ on: loss === 'squared' }">
            <td>squared ½(yᵢ − F)²</td>
            <td :style="{ color: BLUE }">F − yᵢ</td>
            <td :style="{ color: PURPLE }">1</td>
          </tr>
          <tr :class="{ on: loss === 'log' }">
            <td>log loss</td>
            <td :style="{ color: BLUE }">pᵢ − yᵢ</td>
            <td :style="{ color: PURPLE }">pᵢ(1 − pᵢ)</td>
          </tr>
        </tbody>
      </table>
      <div class="knobs">
        <Choice
          v-model="loss" label="loss"
          :options="[{ value: 'log', label: 'log loss' }, { value: 'squared', label: 'squared' }]"
        />
        <Choice
          v-model="y" :options="[{ value: '1', label: 'yᵢ = 1' }, { value: '0', label: 'yᵢ = 0' }]"
          label="this row"
        />
        <Knob v-model="F" :min="-3.4" :max="3.4" label="Fₘ₋₁(xᵢ)" :digits="2" />
      </div>
      <Readout
        :items="[
          { label: 'pᵢ = σ(F)', value: p.toFixed(3), color: MUTED },
          { label: 'gᵢ', value: gAt(F).toFixed(3), color: BLUE },
          { label: 'hᵢ', value: hAt(F).toFixed(3), color: PURPLE },
        ]"
      />
      <p class="note">
        One g and one h per row, recomputed once for each new tree. A row the model
        already has right has a small g: it barely pulls the next tree at all.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 0.9fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; justify-content: center; gap: 0.7rem; }
.knobs { display: flex; flex-direction: column; gap: 0.35rem; }
tr.on td { font-weight: 600; background: #f6f8fa; }
.note { font-size: 0.78rem; color: var(--muted); margin: 0; line-height: 1.5; }
</style>
