<!-- init_faces: the same W₀ built five ways, r = 6 columns drawn as images,
     then the multiplicative updates run from each, live. Five starts, five
     different stationary points. -->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { SIDE, faces } from '../lib/data5'
import { clone, col } from '../lib/mat'
import { type Fit, type Init, init, lossOf, muStep } from '../lib/nmf'
import { useRun } from '../lib/runner'
import { BLUE, GOLD, GREEN, INK, PURPLE, RED } from '../lib/theme'

const X = faces(100)
const R = 6
const passes = ref(0)
const el = ref<HTMLElement | null>(null)
const rows: { name: string; color: string; how: Init; why: string }[] = [
  { name: 'constants', color: RED, how: 'constant', why: 'every column identical' },
  { name: 'random', color: GOLD, how: 'random', why: 'pure noise' },
  { name: 'NNDSVD', color: GREEN, how: 'nndsvd', why: 'singular vectors, positive part kept' },
  { name: 'r columns of X', color: BLUE, how: 'cols', why: 'six real faces' },
  { name: 'k-means', color: PURPLE, how: 'kmeans', why: 'six centroids' },
]
const starts = rows.map((rw) => init(X, R, rw.how, 0))
const run = useRun<Fit[]>({
  el, key: () => 0,
  make: () => starts.map((s) => ({ W: clone(s.W), H: clone(s.H) })),
  step: (fs) => fs.forEach((f) => muStep(X, f)),
  passes: () => passes.value,
})
// moving the slider back restarts from W₀
watch(passes, (now, before) => { if (now < before) run.restart() })
const view = computed(() => {
  void run.tick.value
  return run.state.value.map((f) => ({ cols: Array.from({ length: R }, (_, k) => col(f.W, k)), loss: lossOf(X, f) }))
})
</script>

<template>
  <div ref="el" class="wrap">
    <div class="note top">The same W, built five ways: r = 6 columns drawn as 32 × 32 images</div>
    <div class="rows">
      <template v-for="(rw, i) in rows" :key="rw.name">
        <div class="name" :style="{ color: rw.color }">{{ rw.name }}</div>
        <Tiles :items="view[i].cols" :side="SIDE" ramp="grayr" :vmin="0" :cols="R" :gap="3" />
        <div class="why">{{ rw.why }}<br><span class="note">loss {{ view[i].loss.toFixed(1) }}</span></div>
      </template>
    </div>
    <div class="controls">
      <Knob v-model="passes" :min="0" :max="100" :step="1" label="MU passes" :digits="0" :color="INK" />
      <span class="note">pass {{ run.pass.value }}. Five different starts, five different stationary points: the start is part of the model.</span>
    </div>
    <div class="credit">data: Olivetti faces, AT&amp;T Cambridge (100 faces, shrunk to 32 × 32)</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.rows { display: grid; grid-template-columns: 9rem 1fr 14rem; grid-auto-rows: 1fr; gap: 0.35rem 1rem; align-items: center; min-height: 0; }
.rows > * { min-height: 0; height: 100%; }
.name { text-align: right; font-weight: 600; font-size: 0.9rem; display: flex; align-items: center; justify-content: flex-end; }
.why { font-size: 0.8rem; display: flex; flex-direction: column; justify-content: center; }
</style>
