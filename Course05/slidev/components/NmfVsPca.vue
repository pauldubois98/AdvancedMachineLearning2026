<!-- nmf_vs_pca: 300 faces, rank 16, two ways. PCA's components are signed
     (red adds, blue subtracts); NMF's are parts, all >= 0. Pick a face and how
     many components rebuild it, and read its two codes. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { SIDE, face, facesNmf, facesPca } from '../lib/data5'
import { BLUE, GREEN, INK, RED } from '../lib/theme'

const j = ref(6)
const k = ref(16)
const P = SIDE * SIDE
const pcaShow = facesPca.U.slice(1, 6)
const nmfShow = facesNmf.W.slice(0, 5)
const pcaCode = computed(() => facesPca.U.map((u) => u.reduce((s, v, q) => s + v * face(j.value)[q], 0)))
const nmfCode = computed(() => facesNmf.H.map((hrow) => hrow[j.value]))
function rebuild(basis: Float64Array[], code: number[], m: number) {
  const out = new Float64Array(P)
  for (let c = 0; c < m; c++) for (let q = 0; q < P; q++) out[q] += basis[c][q] * code[c]
  return out
}
const recP = computed(() => rebuild(facesPca.U, pcaCode.value, k.value))
const recN = computed(() => rebuild(facesNmf.W, nmfCode.value, k.value))
function err(rec: Float64Array) {
  const x = face(j.value)
  let a = 0, b = 0
  for (let q = 0; q < P; q++) { a += (x[q] - rec[q]) ** 2; b += x[q] ** 2 }
  return (100 * Math.sqrt(a / b)).toFixed(1)
}
// the first PCA coefficient is the mean face, far larger than the rest
const pcaBars = computed(() => pcaCode.value.slice(1).map((v, c) => ({
  x: c + 2, y: v, y0: 0, w: 0.7, color: c + 1 < k.value ? (v >= 0 ? RED : BLUE) : '#dfe2e5',
})))
const nmfBars = computed(() => nmfCode.value.map((v, c) => ({ x: c + 1, y: v, y0: 0, w: 0.7, color: c < k.value ? GREEN : '#dfe2e5' })))
const pMax = computed(() => Math.max(...pcaCode.value.slice(1).map(Math.abs)) * 1.1)
const nMax = computed(() => Math.max(...nmfCode.value) * 1.1)
</script>

<template>
  <div class="wrap">
    <div class="grid">
      <div class="lab"><b :style="{ color: BLUE }">PCA</b><span class="note">signed</span></div>
      <Tiles :items="pcaShow" :side="SIDE" ramp="rdbu" signed :cols="5" />
      <div class="codes">
        <LineChart :bars="pcaBars" :series="[]" :hlines="[{ y: 0, color: '#9aa0a6' }]" :x-domain="[1.2, 16.8]" :y-domain="[-pMax, pMax]" :axes="false" title="its code: red adds, blue subtracts" :title-color="BLUE" />
      </div>
      <Tiles class="rec" :items="[recP]" :side="SIDE" :vmin="0" :vmax="1" :caption="`${err(recP)}% error`" />

      <div class="lab"><b :style="{ color: GREEN }">NMF</b><span class="note">all ≥ 0</span></div>
      <Tiles :items="nmfShow" :side="SIDE" ramp="grayr" :cols="5" />
      <div class="codes">
        <LineChart :bars="nmfBars" :series="[]" :hlines="[{ y: 0, color: '#9aa0a6' }]" :x-domain="[0.2, 16.8]" :y-domain="[0, nMax]" :axes="false" title="its code: nothing to subtract" :title-color="GREEN" />
      </div>
      <Tiles class="rec" :items="[recN]" :side="SIDE" :vmin="0" :vmax="1" :caption="`${err(recN)}% error`" />
    </div>
    <div class="controls">
      <Knob v-model="j" :min="0" :max="299" :step="1" label="face" :digits="0" :color="INK" />
      <Knob v-model="k" :min="1" :max="16" :step="1" label="components used" :digits="0" :color="INK" />
      <Tiles class="orig" :items="[face(j)]" :side="SIDE" :vmin="0" :vmax="1" />
      <span class="note">300 faces, rank 16 for both. Five components of each are drawn; at the full rank PCA fits better, NMF reads better.</span>
    </div>
    <div class="credit">data: Olivetti faces, AT&amp;T Cambridge (shrunk to 32 × 32)</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.grid { display: grid; grid-template-columns: 4.5rem 1.6fr 1fr 6rem; grid-template-rows: 1fr 1fr; gap: 0.8rem 1.2rem; min-height: 0; align-items: stretch; }
.lab { display: flex; flex-direction: column; justify-content: center; align-items: flex-end; font-size: 1rem; }
.codes { min-height: 0; }
.rec { min-height: 0; }
.orig { width: 3.4rem; height: 3.4rem; }
</style>
