<!-- sparsity_demo: the l1 penalty on H, run live on faces. Raise λ: more of
     H is exactly zero, the fit gets worse, and the parts get more local. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { SIDE, faces } from '../lib/data5'
import { col } from '../lib/mat'
import { type Fit, init, muStep, relErr } from '../lib/nmf'
import { useRun } from '../lib/runner'
import { GOLD, INK, PURPLE, RED } from '../lib/theme'

const X = faces(100)
const lam = ref(0)
const R = 16
const PASSES = 250
const el = ref<HTMLElement | null>(null)
const start = init(X, R, 'nndsvd')
const run = useRun<Fit>({
  el, key: () => lam.value,
  make: () => ({ W: { ...start.W, a: start.W.a.slice() }, H: { ...start.H, a: start.H.a.slice() } }),
  step: (f) => muStep(X, f, { lam: lam.value }),
  passes: () => PASSES,
})
const stats = computed(() => {
  void run.tick.value
  const f = run.state.value
  let hmax = 0
  for (const v of f.H.a) hmax = Math.max(hmax, v)
  const zeros = f.H.a.filter((v) => v < 1e-6 * Math.max(hmax, 1e-12)).length / f.H.a.length
  return { zeros, err: relErr(X, f), parts: Array.from({ length: R }, (_, k) => col(f.W, k)) }
})
</script>

<template>
  <div ref="el" class="wrap">
    <div class="note top">100 faces, r = 16, λ‖H‖₁ added to the loss</div>
    <div class="body">
      <div class="side">
        <Readout :items="[{ label: '% of H at zero', value: `${(100 * stats.zeros).toFixed(0)}%`, color: GOLD }, { label: 'relative error', value: `${(100 * stats.err).toFixed(1)}%`, color: RED }]" />
        <p class="note">pass {{ run.pass.value }} / {{ PASSES }}, from the same NNDSVD start for every λ.</p>
        <div class="h" :style="{ color: GOLD }">λ up</div>
        <p>more zeros in H, a worse fit</p>
        <p>each face is built from fewer parts, so each part has to carry more of a face</p>
      </div>
      <Tiles :items="stats.parts" :side="SIDE" ramp="grayr" :cols="8" :gap="3" title="the 16 columns of W" :title-color="PURPLE" />
    </div>
    <div class="controls">
      <Knob v-model="lam" :min="0" :max="20" :step="0.25" label="λ" :color="GOLD" />
    </div>
    <div class="credit">data: Olivetti faces, AT&amp;T Cambridge (shrunk to 32 × 32)</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 14rem 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
</style>
