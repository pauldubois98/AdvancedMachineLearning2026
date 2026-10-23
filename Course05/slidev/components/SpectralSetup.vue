<!-- setup_spectral: one pixel's spectrum (a column of X) is a blend of the
     pure spectra (the columns of W), in the amounts of its column of H. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { spectral } from '../lib/data5'
import { BLUE, GOLD, GREEN, INK, RED } from '../lib/theme'

const { size, bands, spectra, maps, X } = spectral
const names = ['vegetation', 'roof', 'soil']
const mats = [GREEN, BLUE, RED]
const px = ref(10)
const py = ref(31)
const j = computed(() => py.value * size + px.value)
const n = size * size
const scene = (q: number): [number, number, number] => {
  const v = [maps.a[2 * n + q], maps.a[q], maps.a[n + q]] // soil red, vegetation green, roof blue
  return v.map((t) => 0.15 + 0.85 * t) as [number, number, number]
}
const xj = computed(() => bands.map((w, i) => [w, X.a[i * X.c + j.value]] as [number, number]))
const hj = computed(() => [0, 1, 2].map((k) => maps.a[k * n + j.value]))
</script>

<template>
  <div class="wrap">
    <div class="note top">What the three matrices hold, for a hyperspectral image</div>
    <div class="body">
      <div class="col">
        <div class="h">the scene</div>
        <RgbImage :width="size" :height="size" :rgb="scene" :mark="[px, py]" />
        <div class="cap">one pixel</div>
      </div>
      <div class="col">
        <LineChart :series="[{ points: xj, color: BLUE, width: 2.2 }]" :x-domain="[0.4, 2.4]" :y-domain="[0, 0.85]" x-label="wavelength" :x-ticks="[]" :y-ticks="[]" title="x<sub>j</sub>: a column of X" :title-color="BLUE" />
        <div class="cap">what that one pixel reflects, at each of 60 wavelengths</div>
      </div>
      <div class="col">
        <LineChart
          :series="spectra.map((s, k) => ({ points: bands.map((w, i) => [w, s[i]]), color: mats[k], width: 2 }))"
          :labels="names.map((nm, k) => ({ x: 2.38, y: 0.8 - 0.1 * k, text: nm, color: mats[k], size: 13, anchor: 'end' }))"
          :x-domain="[0.4, 2.4]" :y-domain="[0, 0.85]" x-label="wavelength" :x-ticks="[]" :y-ticks="[]" title="w<sub>k</sub>: a column of W" :title-color="'#6b46c1'"
        />
        <div class="cap">the spectrum of one pure material, the same all over the scene</div>
      </div>
      <div class="col">
        <LineChart
          :series="[]"
          :bars="hj.map((v, k) => ({ x: k, y: v, y0: 0, w: 0.6, color: mats[k] }))"
          :labels="[...hj.map((v, k) => ({ x: k, y: v + 0.07, text: v.toFixed(2), color: mats[k], size: 13 })), ...['veg.', 'roof', 'soil'].map((nm, k) => ({ x: k, y: -0.07, text: nm, color: '#1b1b1b', size: 12 }))]"
          :hlines="[{ y: 0, color: '#1b1b1b' }]"
          :x-domain="[-0.6, 2.6]" :y-domain="[-0.14, 1.12]" :axes="false" title="h<sub>j</sub>: a column of H" :title-color="GOLD"
        />
        <div class="cap">how much of each material sits inside that pixel</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="px" :min="0" :max="size - 1" :step="1" label="pixel x" :digits="0" :color="INK" />
      <Knob v-model="py" :min="0" :max="size - 1" :step="1" label="pixel y" :digits="0" :color="INK" />
    </div>
    <div class="bottom">The pixel reflects a blend of what it contains: light adds up, and a fraction is never negative.</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top, .bottom { text-align: center; }
.bottom { font-size: 0.9rem; }
.body { display: grid; grid-template-columns: 0.85fr 1fr 1fr 0.9fr; gap: 1.2rem; min-height: 0; }
.col { display: grid; grid-template-rows: auto 1fr auto; gap: 0.3rem; min-height: 0; }
.col:not(:first-child) { grid-template-rows: 1fr auto; }
.h { text-align: center; font-weight: 600; font-size: 0.82rem; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.75rem; line-height: 1.35; }
</style>
