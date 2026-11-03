<!-- train_vs_test: E_RMS on the training points and on a fresh test sample,
     for every order. The default is the printed deck's ten points. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmin, freshSin, polyFit, rms, sinData } from '../lib/c08'
import { BLUE, GREEN, RED } from '../lib/theme'

const N = ref(10)
const noise = ref(0.22)
const seed = ref(0)
const MS = Array.from({ length: 10 }, (_, m) => m)
const test = computed(() => freshSin(400, 99, noise.value))
const rows = computed(() => {
  const s = sinData(N.value, seed.value, noise.value)
  return MS.map((m) => { const w = polyFit(s.x, s.t, m); return { tr: rms(w, s), te: rms(w, test.value) } })
})
const best = computed(() => argmin(rows.value.map((r) => r.te)))
const ymax = computed(() => Math.min(1.5, Math.max(1, ...rows.value.map((r) => r.te)) * 1.05))
const tr = computed(() => MS.map((m) => [m, rows.value[m].tr] as [number, number]))
const te = computed(() => MS.map((m) => [m, Math.min(rows.value[m].te, ymax.value * 1.5)] as [number, number]))
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[{ points: tr, color: BLUE, width: 2.8 }, { points: te, color: RED, width: 2.8 }]"
        :dots="[
          ...tr.map(([x, y]) => ({ x, y, color: BLUE, r: 4 })),
          ...te.map(([x, y]) => ({ x, y, color: RED, r: 4 })),
          { x: best, y: rows[best].te, color: GREEN, r: 11, hollow: true },
        ]"
        :labels="[{ x: 6.6, y: ymax * 0.93, text: 'test', color: RED }, { x: 6.6, y: ymax * 0.85, text: 'training', color: BLUE }]"
        :x-domain="[-0.4, 9.4]" :y-domain="[0, ymax]" :x-ticks="[0, 2, 4, 6, 8]" :y-ticks="[0, 0.2, 0.4, 0.6, 0.8, 1.0]"
        x-label="M" y-label="E_RMS"
      />
      <div class="side">
        <div class="h">Interpretation</div>
        <p>— the blue one never rises: more freedom always fits the sample better</p>
        <p>— the red one turns up after <b :style="{ color: GREEN }">M = {{ best }}</b>: the fit starts chasing the noise</p>
        <p class="note">With more points the turn comes later; with more noise, earlier.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="N" :min="10" :max="100" :step="1" :digits="0" label="points N" />
      <Knob v-model="noise" :min="0.02" :max="0.6" :step="0.01" label="noise σ" />
      <Knob v-model="seed" :min="0" :max="30" :step="1" :digits="0" label="sample" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.3fr 1fr; gap: 2.5rem; min-height: 0; }
.side { align-self: center; border-left: 1px solid #cccfd2; padding-left: 2rem; font-size: 0.95rem; }
</style>
