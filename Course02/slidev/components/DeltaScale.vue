<!-- delta_scale: δ is a number of residual scales. On raw residuals measured in
     euros it flags almost everyone; divided by σ̂ = 1.4826 MAD it marks the
     edge of the bulk, whatever the unit. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { histBars } from '../lib/hist'
import { fmt, madScale } from '../lib/reg'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const sigma = ref(4)
const nout = ref(8)
const d = ref(1.345)
const res = computed(() => {
  const rng = new Rng(5)
  const e = Array.from({ length: 400 }, () => rng.normal(0, sigma.value))
  for (let i = 0; i < nout.value; i++) e[i] += rng.normal(0, 7.5 * sigma.value)
  return e
})
const s = computed(() => madScale(res.value))
const sd = computed(() => Math.sqrt(res.value.reduce((a, v) => a + v * v, 0) / res.value.length))
const span = computed(() => 6.2 * sigma.value)
const flagged = (e: number[], t: number) => (100 * e.filter((v) => Math.abs(v) > t).length) / e.length
const scaled = computed(() => res.value.map((v) => v / s.value))
</script>

<template>
  <div class="cmp">
    <div class="r3" style="grid-template-columns: 1fr 1fr 0.8fr">
      <div class="col">
        <LineChart :series="[]" :bars="histBars(res, -span, span, 50, MUTED, 0.5, false)" :vlines="[{ x: -d, color: RED, dash: '' }, { x: d, color: RED, dash: '' }]"
          :x-domain="[-span, span]" :y-domain="[0, 70]" :x-ticks="[-Math.round(4 * sigma), 0, Math.round(4 * sigma)]" :y-ticks="[]"
          x-label="residuals, in euros" :title="`δ = ${d.toFixed(3)} on the raw residuals`" :title-color="RED" />
        <div class="note"><b :style="{ color: RED }">{{ fmt(flagged(res, d), 0) }} %</b> of the points declared outliers</div>
      </div>
      <div class="col">
        <LineChart :series="[]" :bars="histBars(scaled, -6.2, 6.2, 50, BLUE, 0.5, false)" :vlines="[{ x: -d, color: GREEN, dash: '' }, { x: d, color: GREEN, dash: '' }]"
          :x-domain="[-6.2, 6.2]" :y-domain="[0, 70]" :x-ticks="[-6, -3, 0, 3, 6]" :y-ticks="[]"
          x-label="residuals, divided by σ̂" :title="`δ = ${d.toFixed(3)} after scaling`" :title-color="GREEN" />
        <div class="note"><b :style="{ color: GREEN }">{{ fmt(flagged(scaled, d), 0) }} %</b> beyond δ: it marks the edge of the bulk</div>
      </div>
      <div class="side">
        <p class="h">a robust scale, from the data</p>
        <p :style="{ color: BLUE }"><Tex formula="\hat\sigma = 1.4826 \times \mathrm{MAD}" /></p>
        <p class="note"><Tex formula="\mathrm{MAD} = \mathrm{median}_i\,|e_i - \mathrm{median}(e)|" /></p>
        <p>σ̂ = <b :style="{ color: BLUE }">{{ fmt(s) }}</b> €, true σ = {{ fmt(sigma) }} €</p>
        <p class="note">the plain sd is {{ fmt(sd) }} €: outliers inflate it, not the MAD</p>
        <p class="h">usual choices</p>
        <p :style="{ color: BLUE }">Huber δ = 1.345</p>
        <p :style="{ color: RED }">Tukey δ = 4.685</p>
        <p class="note">95 % as efficient as least squares, if the noise is Gaussian</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="sigma" :min="0.3" :max="20" :step="0.1" :digits="1" label="noise σ, in €" :color="MUTED" />
      <Knob v-model="nout" :min="0" :max="80" :step="1" :digits="0" label="outliers" :color="RED" />
      <Knob v-model="d" :min="0.5" :max="5" :step="0.005" :digits="3" label="δ" :color="GREEN" />
    </div>
  </div>
</template>

<style scoped>
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; text-align: center; }
.cmp { grid-template-rows: 1fr auto; }
</style>
