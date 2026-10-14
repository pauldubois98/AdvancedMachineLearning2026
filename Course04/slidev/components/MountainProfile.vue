<!-- eq_mountain: the two formulas, seen along one line. sigma sets how wide
     each point's hill is, beta how much ground the chosen centre clears. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const sigma = ref(0.45)
const beta = ref(0.75)
/** a line of points: a crowd on the left, a smaller group on the right */
const xs = [-2.1, -1.95, -1.8, -1.75, -1.6, -1.5, -1.35, -1.2, 1.3, 1.55, 1.7, 1.9]

const grid = Array.from({ length: 241 }, (_, i) => -3.5 + (7 * i) / 240)
const M = computed(() =>
  grid.map((v) => [v, xs.reduce((s, p) => s + Math.exp(-((v - p) ** 2) / (2 * sigma.value ** 2)), 0)] as [number, number]),
)
const peak = computed(() => M.value.reduce((a, b) => (b[1] > a[1] ? b : a)))
const after = computed(() =>
  M.value.map(([v, h]) => [
    v,
    h - peak.value[1] * Math.exp(-((v - peak.value[0]) ** 2) / (2 * beta.value ** 2)),
  ] as [number, number]),
)
const second = computed(() => after.value.reduce((a, b) => (b[1] > a[1] ? b : a)))
const ratio = computed(() => second.value[1] / peak.value[1])
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="[
        { points: M, color: BLUE, width: 2.4 },
        { points: after, color: GREEN, width: 2.2, dash: '6,4' },
      ]"
      :dots="[
        { x: peak[0], y: peak[1], color: RED, r: 5 },
        { x: second[0], y: second[1], color: GREEN, r: 5 },
      ]"
      :hlines="[{ y: 0, color: MUTED }]"
      :labels="[
        { x: -3.4, y: peak[1] * 0.98, text: 'M(v): the sum of the hills', color: BLUE, size: 12 },
        { x: -3.4, y: peak[1] * 0.84, text: 'after subtracting the first peak', color: GREEN, size: 12 },
      ]"
      :x-domain="[-3.5, 3.5]" :y-domain="[-0.6, Math.max(1, peak[1] * 1.08)]"
      :x-ticks="[-3, -2, -1, 0, 1, 2, 3]"
      x-label="v, along one line" y-label="M(v)"
    />
    <div class="right">
      <div class="eqs">
        <p><Tex display formula='M(v) = \sum_{i=1}^{n} \exp\left(-\frac{\|v - x_i\|^2}{2\sigma^2}\right)' /></p>
        <p><Tex display formula='M_{\text{new}}(v) = M(v) - M(c_1)\exp\left(-\frac{\|v - c_1\|^2}{2\beta^2}\right)' /></p>
      </div>
      <Knob v-model="sigma" :min="0.1" :max="1.4" label="σ, width of one hill" :color="BLUE" />
      <Knob v-model="beta" :min="0.2" :max="2.5" label="β, what a centre clears" :color="GREEN" />
      <Readout
        :items="[
          { label: 'first peak', value: peak[1].toFixed(2), color: RED },
          { label: 'next peak after clearing', value: second[1].toFixed(2), color: GREEN },
          { label: 'ratio', value: ratio.toFixed(2), color: ratio < 0.5 ? '#c53030' : GREEN },
        ]"
      />
      <p class="note">β &gt; σ keeps the next centre away from the one just
        taken. Stop when the tallest peak left is a small enough fraction of
        the first: with this ratio the run
        <em :class="ratio < 0.5 ? 'hl-red' : 'hl-green'">{{ ratio < 0.5 ? 'stops here' : 'takes another centre' }}</em>.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; }
.eqs { font-size: 0.8rem; }
.eqs p { margin: 0; }
</style>
