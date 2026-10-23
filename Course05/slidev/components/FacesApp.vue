<!-- app_faces: NMF of 300 faces, run live. Every column of W is drawn as an
     image; the rank r and the face to rebuild are sliders. HALS from a random
     start, so the parts can be watched as they appear. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { SIDE, face, faces } from '../lib/data5'
import { col, mul, row } from '../lib/mat'
import { type Fit, halsStep, init, relErr } from '../lib/nmf'
import { useRun } from '../lib/runner'
import { BLUE, GREEN, INK, PURPLE } from '../lib/theme'

const X = faces(300)
const r = ref(36)
const j = ref(6)
const el = ref<HTMLElement | null>(null)
const PASSES = 80
const run = useRun<Fit>({
  el,
  key: () => r.value,
  make: () => init(X, r.value, 'random', 1),
  step: (f) => halsStep(X, f),
  score: (f) => relErr(X, f),
  every: 5,
  passes: () => PASSES,
})
const parts = computed(() => {
  void run.tick.value
  return Array.from({ length: r.value }, (_, k) => col(run.state.value.W, k))
})
const rec = computed(() => {
  void run.tick.value
  const f = run.state.value
  const h = { r: f.H.r, c: 1, a: Float64Array.from({ length: f.H.r }, (_, k) => row(f.H, k)[j.value]) }
  return mul(f.W, h).a
})
const err = computed(() => run.hist.value.at(-1)?.[1] ?? 1)
</script>

<template>
  <div ref="el" class="wrap">
    <div class="head">300 faces of 32 × 32 pixels, NMF with r = {{ r }}</div>
    <div class="body">
      <div class="pair">
        <Tiles :items="[face(j)]" :side="SIDE" :vmin="0" :vmax="1" title="a face x<sub>j</sub>" :title-color="BLUE" />
        <Tiles :items="[rec]" :side="SIDE" :vmin="0" :vmax="1" title="W h<sub>j</sub>" :title-color="GREEN" />
        <div class="cap">{{ r }} numbers instead of {{ SIDE * SIDE }}</div>
      </div>
      <Tiles :items="parts" :side="SIDE" ramp="grayr" :gap="2" :title="`the ${r} columns of W`" :title-color="PURPLE" />
      <div class="side">
        <div class="h" :style="{ color: BLUE }">each one is</div>
        <p class="note">non-negative, so it is something you add on, never something you take away</p>
        <p>a face is then a list of amounts</p>
        <Readout :items="[{ label: 'pass', value: `${run.pass.value} / ${PASSES}` }, { label: 'error', value: `${(100 * err).toFixed(1)}%`, color: GREEN }]" />
      </div>
    </div>
    <div class="controls">
      <Knob v-model="r" :min="2" :max="64" :step="1" label="r, parts" :digits="0" :color="INK" />
      <Knob v-model="j" :min="0" :max="299" :step="1" label="face j" :digits="0" :color="BLUE" />
    </div>
    <div class="credit">data: Olivetti faces, AT&amp;T Cambridge (shrunk to 32 × 32); HALS, random start</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.head { text-align: center; font-size: 0.95rem; }
.body { display: grid; grid-template-columns: 13rem 1fr 11rem; gap: 1.4rem; min-height: 0; }
.pair { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 9rem auto; gap: 0.6rem; align-content: center; }
.pair .cap { grid-column: 1 / 3; text-align: center; color: #9aa0a6; font-size: 0.75rem; }
.side { align-self: center; }
</style>
