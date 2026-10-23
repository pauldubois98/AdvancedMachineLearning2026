<!-- app_spectral: NMF of the hyperspectral scene, run live. The spectra it
     finds are drawn over the true ones (dashed), and each component's row of
     H is drawn as a map. Change r, or the start, and watch what changes. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { spectral } from '../lib/data5'
import { col, row } from '../lib/mat'
import { type Fit, type Init, init, muStep, relErr } from '../lib/nmf'
import { useRun } from '../lib/runner'
import { BLUE, GOLD, GREEN, INK, MUTED, PURPLE, RED } from '../lib/theme'

const { size, bands, spectra, maps, X } = spectral
const names = ['vegetation', 'roof', 'soil']
const mats = [GREEN, BLUE, RED]
const n = size * size
const r = ref(3)
const start = ref<Init>('nndsvd')
const seed = ref(1)
const el = ref<HTMLElement | null>(null)
const PASSES = 600
const run = useRun<Fit>({
  el,
  key: () => [r.value, start.value, seed.value],
  make: () => init(X, r.value, start.value, seed.value),
  step: (f) => muStep(X, f),
  score: (f) => relErr(X, f),
  every: 20,
  passes: () => PASSES,
})
function corr(a: ArrayLike<number>, b: ArrayLike<number>) {
  const m = a.length
  let ma = 0, mb = 0
  for (let i = 0; i < m; i++) { ma += a[i] / m; mb += b[i] / m }
  let sab = 0, saa = 0, sbb = 0
  for (let i = 0; i < m; i++) { sab += (a[i] - ma) * (b[i] - mb); saa += (a[i] - ma) ** 2; sbb += (b[i] - mb) ** 2 }
  return sab / Math.sqrt(saa * sbb || 1)
}
const comps = computed(() => {
  void run.tick.value
  const f = run.state.value
  return Array.from({ length: r.value }, (_, k) => {
    const w = col(f.W, k)
    const c = spectra.map((s) => corr(s, w))
    const t = c.indexOf(Math.max(...c))
    const good = c[t] > 0.97
    // scale the found spectrum onto its material, for the overlay
    const s = spectra[t]
    const scale = s.reduce((acc, v, i) => acc + v * w[i], 0) / (w.reduce((acc, v) => acc + v * v, 0) || 1)
    const h = row(f.H, k)
    const hmax = Math.max(...h) || 1
    return { t, good, color: good ? mats[t] : [PURPLE, GOLD, MUTED][k % 3], w: Array.from(w, (v) => v * scale), map: Float64Array.from(h, (v) => v / hmax), name: good ? names[t] : `component ${k + 1}` }
  })
})
const err = computed(() => run.hist.value.at(-1)?.[1] ?? 1)
const scene = (q: number): [number, number, number] =>
  [maps.a[2 * n + q], maps.a[q], maps.a[n + q]].map((t) => 0.15 + 0.85 * t) as [number, number, number]
</script>

<template>
  <div ref="el" class="wrap">
    <div class="head">Hyperspectral unmixing: 60 wavelengths × {{ n }} pixels, r = {{ r }}</div>
    <div class="body">
      <div class="col">
        <div class="h" :style="{ color: BLUE }">the scene</div>
        <RgbImage :width="size" :height="size" :rgb="scene" />
        <div class="cap">three materials, blended at every border</div>
      </div>
      <div class="col">
        <LineChart
          :series="[
            ...comps.map((c) => ({ points: bands.map((b, i) => [b, c.w[i]]), color: c.color, width: 2.4 })),
            ...spectra.map((s) => ({ points: bands.map((b, i) => [b, s[i]]), color: '#1b1b1b', width: 1, dash: '3 3' })),
          ]"
          :x-domain="[0.4, 2.4]" :y-domain="[0, 1]" x-label="wavelength (µm)" :x-ticks="[0.5, 1, 1.5, 2]" :y-ticks="[]"
          title="W: the spectra found" :title-color="PURPLE"
        />
        <div class="cap">thick: NMF, dashed: truth</div>
      </div>
      <div class="col maps">
        <div class="h" :style="{ color: GOLD }">H: how much of it, in every pixel</div>
        <div class="maprow">
          <Tiles v-for="(c, k) in comps" :key="k" :items="[c.map]" :side="size" ramp="h" :vmin="0" :vmax="1" frame="#cccfd2" :title="c.name" :title-color="c.color" />
        </div>
        <div class="cap">NMF never saw the three materials: non-negativity is the whole prior</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="r" :min="2" :max="5" :step="1" label="r" :digits="0" :color="INK" />
      <Choice v-model="start" :options="[{ value: 'nndsvd', label: 'NNDSVD start' }, { value: 'random', label: 'random start' }]" />
      <Knob v-model="seed" :min="1" :max="20" :step="1" label="random seed" :digits="0" :color="GOLD" :disabled="start !== 'random'" />
      <Readout :items="[{ label: 'pass', value: `${run.pass.value}` }, { label: 'error', value: `${(100 * err).toFixed(2)}%`, color: GREEN }]" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.head { text-align: center; font-size: 0.95rem; }
.body { display: grid; grid-template-columns: 0.8fr 1.2fr 1.8fr; gap: 1.4rem; min-height: 0; }
.col { display: grid; grid-template-rows: auto 1fr auto; gap: 0.3rem; min-height: 0; }
.col:nth-child(2) { grid-template-rows: 1fr auto; }
.maprow { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; grid-template-rows: minmax(0, 1fr); gap: 0.6rem; min-height: 0; }
.h { text-align: center; font-weight: 600; font-size: 0.82rem; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.75rem; line-height: 1.35; }
</style>
