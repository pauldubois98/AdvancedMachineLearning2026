<!-- mu_convergence: the multiplicative updates on faces, run live, for the
     Frobenius norm and for KL. Both curves only ever go down, and both
     flatten long before they stop. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { faces } from '../lib/data5'
import { type Fit, init, lossOf, muStep } from '../lib/nmf'
import { useRun } from '../lib/runner'
import { BLUE, GREEN, INK } from '../lib/theme'
import { logTicks } from '../lib/ticks'

const X = faces(100)
const r = ref(10)
const seed = ref(1)
const PASSES = 300
const el = ref<HTMLElement | null>(null)
const mk = (loss: 'fro' | 'kl') => useRun<Fit>({
  el, key: () => [r.value, seed.value],
  make: () => init(X, r.value, 'random', seed.value),
  step: (f) => muStep(X, f, { loss }),
  score: (f) => lossOf(X, f, loss),
  every: 3,
  passes: () => PASSES,
})
const fro = mk('fro')
const kl = mk('kl')
const dom = (h: [number, number][]) => {
  const ys = h.map((p) => p[1])
  return [Math.min(...ys) * 0.8, Math.max(...ys) * 1.3] as [number, number]
}
const rises = (h: [number, number][]) => h.slice(1).filter((p, i) => p[1] > h[i][1] * (1 + 1e-9)).length
const fd = computed(() => dom(fro.hist.value))
const kd = computed(() => dom(kl.hist.value))
</script>

<template>
  <div ref="el" class="wrap">
    <div class="note top">Monotone by construction</div>
    <div class="panels">
      <LineChart :series="[{ points: fro.hist.value, color: BLUE, width: 2.2 }]" log-y :x-domain="[0, PASSES]" :y-domain="fd" :y-ticks="logTicks(...fd)" x-label="pass" y-label="loss" :x-ticks="[0, 100, 200, 300]" title="Frobenius, ½‖X − WH‖²" :title-color="BLUE" />
      <LineChart :series="[{ points: kl.hist.value, color: GREEN, width: 2.2 }]" log-y :x-domain="[0, PASSES]" :y-domain="kd" :y-ticks="logTicks(...kd)" x-label="pass" :x-ticks="[0, 100, 200, 300]" title="KL, KL(X, WH)" :title-color="GREEN" />
    </div>
    <div class="controls">
      <Knob v-model="r" :min="2" :max="30" :step="1" label="r" :digits="0" :color="INK" />
      <Knob v-model="seed" :min="1" :max="20" :step="1" label="random start" :digits="0" :color="INK" />
      <Readout :items="[{ label: 'pass', value: `${fro.pass.value}` }, { label: 'passes that went up', value: `${rises(fro.hist.value) + rises(kl.hist.value)}`, color: GREEN }]" />
      <span class="note">100 faces, live. Fast at first, then a long, slow tail.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; min-height: 0; }
</style>
