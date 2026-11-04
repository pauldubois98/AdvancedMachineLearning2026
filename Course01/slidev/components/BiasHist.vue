<!-- bias: the distribution of an estimator over many samples, its mean, and
     the gap to the truth. The estimator is a shrunk mean, so the bias is live. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { histBars } from '../lib/hist'
import { mean } from '../lib/stats'
import { BLUE, INK, RED } from '../lib/theme'

const c = ref(1.35)
const n = ref(4)
const TH = 1
const r = new Rng(3)
// the standardised sample means of 4000 samples: x̄ = θ0 + z / √n
const Z = Array.from({ length: 4000 }, () => r.normal())
const est = computed(() => Z.map((z) => c.value * (TH + z / Math.sqrt(n.value))))
const m = computed(() => mean(est.value))
const bars = computed(() => histBars(est.value, -0.6, 3.2, 70, BLUE, 0.5))
const top = computed(() => Math.max(...bars.value.map((b) => b.y)) * 1.25)
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 4000 samples of n points from N(θ₀ = 1, 1). Each sample gives one estimate θ̂ = c · x̄, the sample mean scaled by c; the histogram shows the 4000 values.</div>
    <LineChart :series="[]" :bars="bars" :x-domain="[-0.6, 3.2]" :y-domain="[0, top]" :x-ticks="[-0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]" :y-ticks="[]"
      x-label="value taken by the estimator θ̂"
      :vlines="[{ x: TH, color: INK, dash: '' }, { x: m, color: BLUE, dash: '6,4' }]"
      :arrows="Math.abs(m - TH) > 0.03 ? [{ x0: TH, y0: top * 0.72, x1: m, y1: top * 0.72, color: RED, both: true }] : []"
      :labels="[{ x: TH - 0.04, y: top * 0.9, text: 'θ₀', anchor: 'end' }, { x: m + 0.05, y: top * 0.9, text: 'E[θ̂]', color: BLUE }, { x: (TH + m) / 2, y: top * 0.77, text: 'bias', color: RED, anchor: 'middle' }]" />
    <div class="foot">bias(θ̂) = E[θ̂] − θ₀ = <b :style="{ color: RED }">{{ (m - TH).toFixed(2) }}</b>, (c − 1) θ₀ in theory: more points make θ̂ steadier, but they do not move its centre.</div>
    <div class="controls">
      <Knob v-model="c" :min="0.4" :max="1.6" :step="0.01" label="scale c" :color="RED" />
      <Knob v-model="n" :min="1" :max="50" :step="1" :digits="0" label="points per sample n" :color="BLUE" />
    </div>
  </div>
</template>
