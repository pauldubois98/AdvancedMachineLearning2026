<!-- optuna_history: when to stop paying. A study's trials and the best score
     so far; over the last w trials, compare how much the best moved with the
     trial-to-trial spread. A gain below the spread is the signal to stop. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { std } from '../lib/c08'
import { GREEN, LIGHT, MUTED, PURPLE, RED } from '../lib/theme'

const n = ref(120)
const w = ref(50)
const noise = ref(0.014)
const seed = ref(6)
const vals = computed(() => {
  const rng = new Rng(seed.value)
  return Array.from({ length: n.value }, (_, i) => (i < 10
    ? 0.70 + rng.normal(0, 0.03)
    : 0.735 + 0.055 * (1 - Math.exp(-(i + 1) / 22)) + rng.normal(0, noise.value)))
})
const best = computed(() => { let b = -Infinity; return vals.value.map((v) => (b = Math.max(b, v))) })
const start = computed(() => Math.max(0, n.value - w.value))
const gain = computed(() => best.value[n.value - 1] - best.value[Math.max(0, start.value - 1)])
const spread = computed(() => std(vals.value.slice(start.value)))
const stop = computed(() => gain.value < spread.value)
</script>

<template>
  <div class="wrap">
    <div class="note top">when to stop paying</div>
    <div class="body">
      <LineChart
        :series="[{ points: best.map((b, i) => [i + 1, b] as [number, number]), color: RED, width: 2.6, step: true }]"
        :dots="vals.map((v, i) => ({ x: i + 1, y: v, color: MUTED, r: 2.6 }))"
        :bands="[{ x0: 0, x1: 10.5, color: '#9aa0a6', alpha: 0.15 }, { x0: start + 0.5, x1: n + 0.5, color: stop ? GREEN : RED, alpha: 0.1 }]"
        :labels="[{ x: n * 0.6, y: 0.665, text: '● trial', color: MUTED, size: 12 }, { x: n * 0.6, y: 0.65, text: '— best so far', color: RED, size: 12 }]"
        :x-domain="[0, n + 1]" :y-domain="[0.64, 0.83]" :y-ticks="[0.65, 0.7, 0.75, 0.8]"
        :x-ticks="[0, 1, 2, 3, 4].map((k) => Math.round((k * n) / 4))" x-label="trial" y-label="validation AUC"
      />
      <div class="side">
        <div class="h">Interpretation</div>
        <p>— the first ten trials are random start-up (grey): nothing is modelled yet</p>
        <p>— the best curve climbs as the search finds better settings</p>
        <p>— it ends flat: more budget is not improving any more</p>
        <p :style="{ color: stop ? GREEN : RED }">The last {{ Math.min(w, n) }} trials moved the best score by <b>{{ gain.toFixed(3) }}</b>,
          against a trial-to-trial spread of <b>{{ spread.toFixed(3) }}</b>:
          {{ stop ? 'that is the signal to stop.' : 'still worth paying for.' }}</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="n" :min="20" :max="300" :step="1" :digits="0" label="trials so far" />
      <Knob v-model="w" :min="5" :max="100" :step="1" :digits="0" label="window w" :color="PURPLE" />
      <Knob v-model="noise" :min="0.002" :max="0.04" :step="0.001" :digits="3" label="trial noise" />
      <Knob v-model="seed" :min="1" :max="30" :step="1" :digits="0" label="seed" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.3fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; border-left: 1px solid #cccfd2; padding-left: 1.6rem; font-size: 0.9rem; }
</style>
