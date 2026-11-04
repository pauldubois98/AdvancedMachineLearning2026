<!-- collinear_example: x2 = 2 x1, so only β1 + 2β2 is seen by the data. Slide
     along that line: every recipe gives the same predictions and the same loss. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { fmt } from '../lib/reg'
import { BLUE, GREEN, INK, MUTED, PURPLE, RED } from '../lib/theme'

const HOURS = [1, 2, 3, 4]
const SCORE = [1.1, 1.9, 3.2, 3.8]
const best = HOURS.reduce((s, h, i) => s + h * SCORE[i], 0) / HOURS.reduce((s, h) => s + h * h, 0)
const b2 = ref(0.5)
const off = ref(0)
const b1 = computed(() => best - 2 * b2.value + off.value)
const pred = computed(() => HOURS.map((h) => b1.value * h + b2.value * 2 * h))
const loss = computed(() => 0.5 * HOURS.reduce((s, h, i) => s + (SCORE[i] - pred.value[i]) ** 2, 0))
const lossBest = 0.5 * HOURS.reduce((s, h, i) => s + (SCORE[i] - best * h) ** 2, 0)
const col = computed(() => (Math.abs(off.value) < 0.005 ? GREEN : RED))
</script>

<template>
  <div class="cmp">
    <div class="r2" style="align-items: center; grid-template-columns: 1fr 1.4fr">
      <table class="plain big">
        <tr><th>x₁ 1st feature</th><th>x₂ 2nd feature</th><th>y score</th></tr>
        <tr v-for="(h, i) in HOURS" :key="i"><td>{{ h }}</td><td>{{ 2 * h }}</td><td>{{ SCORE[i].toFixed(1) }}</td></tr>
      </table>
      <table class="plain big">
        <tr><th>β̂₁</th><th>β̂₂</th><th>β̂₁ + 2β̂₂</th><th>predictions β̂₁x₁ + β̂₂x₂</th><th>loss</th></tr>
        <tr v-for="(c, i) in [[1, 0, BLUE], [0, 0.5, GREEN], [2, -0.5, PURPLE]]" :key="i" :style="{ color: c[2] }">
          <td>{{ (+c[0]).toFixed(1) }}</td><td>{{ (+c[1]).toFixed(1) }}</td><td>{{ (+c[0] + 2 * +c[1]).toFixed(1) }}</td>
          <td>{{ HOURS.map((h) => (+c[0] * h + +c[1] * 2 * h).toFixed(1)).join(', ') }}</td>
          <td>{{ fmt(0.5 * HOURS.reduce((s, h, j) => s + (SCORE[j] - (+c[0] + 2 * +c[1]) * h) ** 2, 0)) }}</td>
        </tr>
        <tr :style="{ color: col, fontWeight: 600 }">
          <td>{{ fmt(b1) }}</td><td>{{ fmt(b2) }}</td><td>{{ fmt(b1 + 2 * b2) }}</td>
          <td>{{ pred.map((v) => v.toFixed(2)).join(', ') }}</td><td>{{ fmt(loss, 3) }}</td>
        </tr>
      </table>
    </div>
    <div class="foot">two features represent the same information, x₂ = 2x₁: <b :style="{ color: RED }">the data pins down β̂₁ + 2β̂₂ only</b> (best value {{ fmt(best, 3) }}, loss {{ fmt(lossBest, 3) }}); any β₂ will do</div>
    <div class="controls">
      <Knob v-model="b2" :min="-3" :max="3" :step="0.01" label="β₂ (β₁ follows)" :color="GREEN" />
      <Knob v-model="off" :min="-0.4" :max="0.4" :step="0.005" :digits="3" label="leave the line: β₁ + 2β₂ − best" :color="col" />
    </div>
  </div>
</template>

<style scoped>
.big { font-size: 1rem; }
.big td, .big th { text-align: center; }
</style>
