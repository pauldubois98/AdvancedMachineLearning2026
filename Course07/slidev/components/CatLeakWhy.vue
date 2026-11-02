<!-- cat_leak_why: the ramp is arithmetic, not luck. If your own label is one
     of the k values averaged, the encoding is a readout of it. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const k = ref(3)
const rows = computed(() => {
  const K = Math.round(k.value)
  return Array.from({ length: K + 1 }, (_, m) => ({
    m,
    enc: m / K,
    verdict: m === 0 ? 'must be 0' : m === K ? 'must be 1' : '0 or 1',
    p: m / K,
    color: m === 0 ? RED : m === K ? BLUE : MUTED,
  }))
})
const diag = computed(() => rows.value.map((r) => [r.enc, r.p] as [number, number]))
</script>

<template>
  <div class="wrap">
    <div class="left">
      <p class="eq">encoding = ( <span :style="{ color: RED }">y<sub>i</sub></span> + y<sub>j</sub> + … ) / {{ Math.round(k) }}
        &nbsp;&nbsp;<span class="note">with y<sub>i</sub> = my own Buy</span></p>
      <table class="plain">
        <thead>
          <tr><th>encoding</th><th>how many of the {{ Math.round(k) }} bought</th><th>so my own Buy</th><th>P(Buy = 1)</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.m">
            <td>{{ r.enc.toFixed(2) }}</td>
            <td :style="{ color: MUTED }">{{ r.m }}</td>
            <td :style="{ color: r.color }">{{ r.verdict }}</td>
            <td :style="{ color: GREEN, fontWeight: 600 }">{{ r.p.toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
      <Knob v-model="k" :min="2" :max="12" :step="1" label="customers in this category" :digits="0" />
    </div>
    <div class="right">
      <LineChart
        :series="[{ points: diag, color: GREEN, width: 2.4 }]"
        :dots="rows.map((r) => ({ x: r.enc, y: r.p, color: GREEN, r: 5 }))"
        :hlines="[{ y: 0.5, color: INK, dash: '4,4' }]"
        :x-domain="[-0.05, 1.05]" :y-domain="[-0.05, 1.05]"
        :x-ticks="[0, 0.5, 1]" :y-ticks="[0, 0.5, 1]"
        x-label="value of the encoded feature" y-label="share of y = 1 among those rows"
        title="the last two columns are the same number"
        :labels="[{ x: 0.02, y: 0.95, text: 'dashed: the base rate a useless feature would sit on', color: MUTED, size: 11 }]"
      />
      <p class="note">
        When P(Buy = 1 | encoding) equals the encoding itself, the feature is a readout
        of the label it was built from. A tree splitting on it scores beautifully on the
        training rows and knows nothing about a new customer, whose encoding is computed
        without their label, and so lands on the flat line instead.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1.1fr; gap: 1.8rem; height: 100%; min-height: 0; }
.left { display: flex; flex-direction: column; justify-content: center; gap: 0.7rem; }
.right { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; min-height: 0; }
.eq { font-size: 1rem; margin: 0; }
.note { font-size: 0.78rem; color: var(--muted); margin: 0; line-height: 1.5; }
td { font-variant-numeric: tabular-nums; }
</style>
