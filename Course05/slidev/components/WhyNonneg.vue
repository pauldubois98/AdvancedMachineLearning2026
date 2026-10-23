<!-- why_nonneg: two parts and their sum. With a negative weight a part can
     mean "undo that" and the sum cancels; with weights >= 0 parts only add. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, MUTED, PURPLE, RED } from '../lib/theme'

const a = ref(1.6)
const b = ref(-1.4)
const xs = Array.from({ length: 160 }, (_, i) => i / 159)
const A = xs.map((x) => Math.exp(-(((x - 0.3) / 0.12) ** 2)))
const B = xs.map((x) => Math.exp(-(((x - 0.5) / 0.12) ** 2)))
const signed = computed(() => a.value < 0 || b.value < 0)
const color = computed(() => (signed.value ? RED : GREEN))
const sum = computed(() => xs.map((x, i) => [x, a.value * A[i] + b.value * B[i]] as [number, number]))
const dips = computed(() => sum.value.some(([, y]) => y < -1e-3))
</script>

<template>
  <div class="wrap">
    <div class="note top">W ≥ 0 and H ≥ 0 are read entry by entry.</div>
    <div class="body">
      <div class="plot">
        <div class="title" :style="{ color }">{{ signed ? 'signed: parts cancel' : 'non-negative: parts only add' }}</div>
        <LineChart
          :series="[
            { points: xs.map((x, i) => [x, a * A[i]]), color: MUTED, width: 1.4 },
            { points: xs.map((x, i) => [x, b * B[i]]), color: MUTED, width: 1.4, dash: '5 4' },
            { points: sum, color, width: 2.6 },
          ]"
          :hlines="[{ y: 0, color: '#cccfd2' }]"
          :x-domain="[0, 1]" :y-domain="[-1.6, 2.2]" :axes="false"
        />
        <div class="cap">{{ dips ? 'a component can mean "undo that"' : 'a component is a piece of the whole' }}</div>
      </div>
      <div class="side">
        <div class="h" :style="{ color: BLUE }">Inherent positive cases:</div>
        <p>— pixel intensities</p>
        <p>— word counts</p>
        <p>— spectra, power</p>
        <p>— prices, ratings, durations</p>
        <p class="note">Data is already ≥ 0.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="a" :min="-1.5" :max="2" :step="0.05" label="weight of part 1 (solid)" :color="PURPLE" />
      <Knob v-model="b" :min="-1.5" :max="2" :step="0.05" label="weight of part 2 (dashed)" :color="PURPLE" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 15rem; gap: 2rem; min-height: 0; }
.plot { display: grid; grid-template-rows: auto 1fr auto; min-height: 0; }
.title { text-align: center; font-weight: 600; font-size: 0.95rem; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.8rem; }
.side { align-self: center; border-left: 1px solid #cccfd2; padding-left: 1.4rem; }
</style>
