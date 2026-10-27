<!-- em_run_2d: the same run in the plane. The ellipses walk to the clusters;
     colours are the hard labels at the current pass. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmax, em2, resp2, sampleMix2, start2, TWO_BLOBS, type Mix2 } from '../lib/gmm'
import { fmt } from '../lib/charts'
import { COMP, GREEN, INK, MUTED } from '../lib/theme'

const { X } = sampleMix2(TWO_BLOBS, 300, 3)
const startKind = ref('deck')
const seed = ref(1)
const t = ref(0)
const T = 30
const DECK: Mix2 = { p: [0.5, 0.5], mu: [[-0.1, 0.9], [0.1, -0.9]], S: [[0.9, 0, 0.9], [0.9, 0, 0.9]] }
const hist = computed(() => em2(X, startKind.value === 'deck' ? DECK : start2(X, 2, seed.value), T))
const cur = computed(() => hist.value[t.value])
const colors = computed(() => X.map((x) => COMP[argmax(resp2(x, cur.value))]))
const lls = computed(() => hist.value.map((h, i) => [i, h.ll] as [number, number]))
const yr = computed(() => [Math.min(...lls.value.map((p) => p[1])) - 5, Math.max(...lls.value.map((p) => p[1])) + 5] as [number, number])
</script>

<template>
  <div class="wrap">
    <div class="note top">Ellipses walk to the clusters; colours are the hard labels, showing progress</div>
    <div class="body">
      <Plane
        :X="X" :colors="colors" :size="3" :domain="[-3.6, 3.6, -2.6, 2.8]"
        :ellipses="cur.mu.map((mu, k) => ({ mu, S: cur.S[k], color: COMP[k], width: 1.7 }))"
        :markers="cur.mu.map((mu, k) => ({ at: mu, color: COMP[k], shape: 'x', size: 6 }))"
        :title="`t = ${t}: ℓ = ${fmt(cur.ll)}`" :title-color="t ? INK : MUTED"
      />
      <LineChart
        :series="[{ points: lls, color: GREEN, width: 2.2 }]" :dots="[{ x: t, y: cur.ll, color: GREEN, r: 5 }]"
        :x-domain="[0, T]" :y-domain="yr" x-label="pass t" y-label="ℓ_obs" :x-ticks="[0, 10, 20, 30]" :y-ticks="[]"
        title="the log-likelihood"
      />
    </div>
    <div class="controls">
      <Knob v-model="t" :min="0" :max="T" :step="1" label="pass t" :digits="0" :color="GREEN" />
      <Choice v-model="startKind" :options="[{ value: 'deck', label: 'the deck\'s start' }, { value: 'random', label: 'random start' }]" label="start" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" label="seed" :digits="0" :color="INK" :disabled="startKind === 'deck'" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; min-height: 0; }
</style>
