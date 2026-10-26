<!-- setup_cube: a hyperspectral scene is a cube, one image per wavelength.
     Pick a wavelength (a row of X, an image of the scene) and a pixel (a
     column of X, the spectrum read through the stack). -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { spectral } from '../lib/data5'
import { BLUE, INK } from '../lib/theme'

const { size, bands, X } = spectral
const b = ref(10)
const px = ref(10)
const py = ref(31)
const j = computed(() => py.value * size + px.value)
const slice = computed(() => X.a.subarray(b.value * X.c, (b.value + 1) * X.c))
const vmax = Math.max(...X.a)
const spectrum = computed(() => bands.map((w, i) => [w, X.a[i * X.c + j.value]] as [number, number]))
</script>

<template>
  <div class="wrap">
    <div class="note top">The scene is a cube; the matrix is that cube, unfolded.</div>
    <div class="body">
      <div class="col">
        <Tiles :items="[slice]" :side="size" ramp="x" :vmin="0" :vmax="vmax" :hi="null" :mark="[px, py]" :mark-color="BLUE" @pick="(x, y) => { px = x; py = y }" :title="`the image at ${bands[b].toFixed(2)} µm`" :title-color="BLUE" />
        <div class="cap">{{ size }} × {{ size }} pixels × {{ bands.length }} wavelengths: one image per wavelength; click a pixel to read its spectrum</div>
      </div>
      <div class="col">
        <LineChart
          :series="[{ points: spectrum, color: BLUE, width: 2.2 }]"
          :vlines="[{ x: bands[b], color: '#9aa0a6', dash: '4 3' }]"
          :x-domain="[0.4, 2.4]" :y-domain="[0, 0.85]" x-label="wavelength (µm)" :x-ticks="[0.5, 1, 1.5, 2]" :y-ticks="[]"
          :title="`pixel (${px}, ${py}) read through the stack`" :title-color="BLUE"
        />
        <div class="cap">one column x<sub>j</sub> of X</div>
      </div>
      <div class="col wide">
        <MatView :M="X" ramp="x" :border="BLUE" :hi-row="b" :hi-col="j" title="X" :title-color="BLUE" />
        <div class="cap">{{ X.c }} = {{ size }} × {{ size }} pixels, laid out in a row.<br><span :style="{ color: BLUE }">X is {{ X.r }} × {{ X.c }}: one column per pixel, one row per wavelength</span></div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="b" :min="0" :max="59" :step="1" label="wavelength" :digits="0" :color="INK" />
      <Knob v-model="px" :min="0" :max="size - 1" :step="1" label="pixel x" :digits="0" :color="BLUE" />
      <Knob v-model="py" :min="0" :max="size - 1" :step="1" label="pixel y" :digits="0" :color="BLUE" />
    </div>
    <div class="note bottom">The factorization never sees the geometry: which pixel sits next to which is only used to draw the result.</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top, .bottom { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 1.1fr 1.6fr; gap: 1.4rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; gap: 0.3rem; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.75rem; line-height: 1.4; }
</style>
