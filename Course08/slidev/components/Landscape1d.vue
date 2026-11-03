<!-- landscape_1d: a validation loss against lambda on a log scale, measured
     with noise at a grid of probes. The band marks every lambda within a
     tolerance of the best: it spans orders of magnitude. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { argmin, sci } from '../lib/c08'
import { BLUE, GREEN, MUTED, PURPLE, RED } from '../lib/theme'

const noise = ref(0.012)
const probes = ref(22)
const tol = ref(0.02)
const seed = ref(2)
const loss = (l: number) => 0.30 + 0.052 * (Math.log10(l) + 1.6) ** 2
const curve = Array.from({ length: 200 }, (_, i) => { const l = 10 ** (-5 + (7 * i) / 199); return [l, loss(l)] as [number, number] })
const meas = computed(() => {
  const rng = new Rng(seed.value)
  return Array.from({ length: probes.value }, (_, i) => {
    const l = 10 ** (-5 + (7 * i) / Math.max(probes.value - 1, 1))
    return [l, loss(l) + rng.normal(0, noise.value)] as [number, number]
  })
})
const pickM = computed(() => meas.value[argmin(meas.value.map((p) => p[1]))])
// the lambdas whose true loss is within tol of the minimum 0.30
const half = computed(() => Math.sqrt(tol.value / 0.052))
const band = computed(() => [10 ** (-1.6 - half.value), 10 ** (-1.6 + half.value)])
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[{ points: curve, color: BLUE, width: 2.8 }]"
        :bands="[{ x0: band[0], x1: band[1], color: GREEN, alpha: 0.13 }]"
        :dots="[...meas.map(([x, y]) => ({ x, y, color: RED, r: 4.2 })), { x: pickM[0], y: pickM[1], color: GREEN, r: 10, hollow: true }]"
        :vlines="[{ x: 10 ** -1.6, color: MUTED, dash: '4 3' }]"
        :labels="[{ x: 2e-5, y: 1.0, text: 'true validation loss', color: BLUE, size: 12 }, { x: 2e-5, y: 0.94, text: 'measured validation loss', color: RED, size: 12 }]"
        log-x :x-domain="[5e-6, 200]" :y-domain="[0.14, 1.05]" :x-ticks="[1e-5, 1e-3, 1e-1, 10]" :y-ticks="[0.2, 0.4, 0.6, 0.8, 1.0]"
        x-label="λ (log scale)" y-label="validation loss"
      />
      <div class="side">
        <div class="h">Interpretation</div>
        <p>— smooth on a log scale</p>
        <p>— flat near the optimum: every λ in the green band is within <b>{{ tol.toFixed(3) }}</b> of the best, from
          <b :style="{ color: GREEN }">{{ sci(band[0]) }}</b> to <b :style="{ color: GREEN }">{{ sci(band[1]) }}</b>
          ({{ (2 * half).toFixed(1) }} decades)</p>
        <p>— the probes' best (ring) is at <b>{{ sci(pickM[0]) }}</b>: with noise, the exact minimum is a coin toss</p>
        <p :style="{ color: PURPLE }">Aim for the right order of magnitude, not the exact minimum.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="noise" :min="0" :max="0.08" :step="0.001" :digits="3" label="measurement noise" :color="RED" />
      <Knob v-model="probes" :min="4" :max="60" :step="1" :digits="0" label="probes" />
      <Knob v-model="tol" :min="0.002" :max="0.1" :step="0.002" :digits="3" label="tolerance" :color="GREEN" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" :digits="0" label="seed" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.3fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; border-left: 1px solid #cccfd2; padding-left: 1.6rem; font-size: 0.92rem; }
</style>
