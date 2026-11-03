<!-- curve_fitting: Bishop's running example. N points of sin(2 pi x) plus
     Gaussian noise; the default is the printed deck's ten points. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ringDots, sinData, truthPoints } from '../lib/c08'
import { BLUE, GREEN, INK } from '../lib/theme'

const N = ref(10)
const noise = ref(0.22)
const seed = ref(0)
const s = computed(() => sinData(N.value, seed.value, noise.value))
</script>

<template>
  <div class="wrap">
    <div class="note top">{{ N }} points drawn from a curve</div>
    <div class="body">
      <LineChart
        :series="[{ points: truthPoints, color: GREEN, width: 2.8 }]" :dots="ringDots(s, BLUE, N > 40 ? 3 : 4.5)"
        :x-domain="[-0.05, 1.05]" :y-domain="[-1.8, 1.8]" :x-ticks="[0, 0.5, 1]" :y-ticks="[-1, 0, 1]"
        x-label="x" y-label="t"
      />
      <div class="side">
        <div class="h" :style="{ color: INK }">The set-up</div>
        <p>— the green curve is <Tex formula="\sin(2\pi x)" />: the truth</p>
        <p>— the circles are <Tex formula="t_i = \sin(2\pi x_i) + \epsilon_i" />, with <Tex formula="\epsilon_i \sim \mathcal N(0, \sigma^2)" /></p>
        <div class="h" :style="{ color: GREEN }">Goal</div>
        <p>predict <Tex formula="t" /> at a new <Tex formula="x" /></p>
        <p class="note">Sample 0 with N = 10 is the printed deck's sample.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="N" :min="3" :max="100" :step="1" :digits="0" label="points N" />
      <Knob v-model="noise" :min="0" :max="0.6" :step="0.01" label="noise σ" />
      <Knob v-model="seed" :min="0" :max="30" :step="1" :digits="0" label="sample" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.3fr 1fr; gap: 2.5rem; min-height: 0; }
.side { align-self: center; border-left: 1px solid #cccfd2; padding-left: 2rem; font-size: 0.95rem; }
</style>
