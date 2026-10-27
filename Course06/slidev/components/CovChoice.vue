<!-- covariance_choice: same data, four covariance families, fitted live.
     A family that contains another always fits at least as well. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmax, em2, kmeansStart, resp2, sampleMix2, THREE_BLOBS, type CovFamily } from '../lib/gmm'
import { fmt } from '../lib/charts'
import { BLUE, COMP, GOLD, GREEN, INK, PURPLE } from '../lib/theme'

const { X } = sampleMix2(THREE_BLOBS, 240, 5)
const K = ref(3)
const FAMS: { fam: CovFamily; name: string; color: string }[] = [
  { fam: 'spherical', name: 'spherical', color: BLUE },
  { fam: 'diag', name: 'diagonal', color: GOLD },
  { fam: 'tied', name: 'tied', color: GREEN },
  { fam: 'full', name: 'full', color: PURPLE },
]
const npar = (fam: CovFamily, k: number) => k * 2 + (k - 1) + ({ spherical: k, diag: 2 * k, tied: 3, full: 3 * k } as Record<CovFamily, number>)[fam]
const fits = computed(() => FAMS.map((f) => {
  const m = em2(X, kmeansStart(X, K.value, 0), 150, { cov: f.fam }).at(-1)!
  return { ...f, m, z: X.map((x) => argmax(resp2(x, m))), np: npar(f.fam, K.value) }
}))
</script>

<template>
  <div class="wrap">
    <div class="note top">Same data, same K = {{ K }}</div>
    <div class="body">
      <div v-for="f in fits" :key="f.fam" class="col">
        <Plane
          :X="X" :colors="f.z.map((k) => COMP[k % COMP.length])" :size="2.6" :domain="[-3.4, 3.4, -2.6, 2.6]"
          :ellipses="f.m.mu.map((mu, k) => ({ mu, S: f.m.S[k], color: COMP[k % COMP.length], width: 1.3 }))"
          :title="f.name" :title-color="f.color"
        />
        <div class="cap">ℓ = {{ fmt(f.m.ll) }}, {{ f.np }} numbers</div>
      </div>
    </div>
    <div class="note bottom">A family that contains another always fits the training sample at least as well, so the choice is a model-selection question.</div>
    <div class="controls">
      <Knob v-model="K" :min="1" :max="6" :step="1" label="components K" :digits="0" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top, .bottom { text-align: center; }
.body { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.8rem; }
</style>
