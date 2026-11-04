<!-- mom_idea: the sample moments of the data against the moments of the
     model. Move the model until they agree: that is the estimate. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve, histBars } from '../lib/hist'
import { mean, normals, npdf } from '../lib/stats'
import { BLUE, GREEN, PURPLE } from '../lib/theme'

const mu = ref(0.5)
const sd = ref(1.6)
const x = normals(new Rng(4), 400, 2, 1)
const U1 = mean(x)
const U2 = mean(x.map((v) => v * v))
const m1 = computed(() => mu.value)
const m2 = computed(() => sd.value ** 2 + mu.value ** 2)
const bars = histBars(x, -1.6, 5.6, 26, BLUE, 0.45)
const model = computed(() => curve((t) => npdf(t, mu.value, sd.value), -1.6, 5.6))
const ok = computed(() => Math.abs(m1.value - U1) < 0.05 && Math.abs(m2.value - U2) < 0.15)
const ticks = [-1, 0, 1, 2, 3, 4, 5]
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 400 points drawn from N(2, 1), whose parameters we pretend not to know. The model is N(μ, σ²): set μ and σ so that its first two moments equal those of the data.</div>
    <div class="r2">
      <LineChart :series="[]" :bars="bars" :x-domain="[-1.6, 5.6]" :y-domain="[0, 0.6]" :x-ticks="ticks" :y-ticks="[]" x-label="the data"
        :vlines="[{ x: U1, color: BLUE, dash: '' }]" title="sample moments" :title-color="BLUE" />
      <LineChart :series="[{ points: model, color: GREEN }]" :x-domain="[-1.6, 5.6]" :y-domain="[0, 0.6]" :x-ticks="ticks" :y-ticks="[]" x-label="the model P_θ"
        :bars="bars.map((b) => ({ ...b, alpha: 0.12 }))" :vlines="[{ x: mu, color: GREEN, dash: '' }]" title="theoretical moments" :title-color="GREEN" />
    </div>
    <div class="foot">
      U₁ = <b :style="{ color: BLUE }">{{ U1.toFixed(2) }}</b> vs m₁ = E[x] = <b :style="{ color: GREEN }">{{ m1.toFixed(2) }}</b>
      &nbsp;·&nbsp; U₂ = <b :style="{ color: BLUE }">{{ U2.toFixed(2) }}</b> vs m₂ = σ² + μ² = <b :style="{ color: GREEN }">{{ m2.toFixed(2) }}</b>
      &nbsp;·&nbsp; <span :style="{ color: ok ? GREEN : PURPLE }">{{ ok ? 'matched: this is the estimate' : 'set them equal, solve for θ' }}</span>
    </div>
    <div class="controls">
      <Knob v-model="mu" :min="-0.5" :max="4.5" :step="0.01" label="model μ" :color="GREEN" />
      <Knob v-model="sd" :min="0.4" :max="2.5" :step="0.01" label="model σ" :color="GREEN" />
    </div>
  </div>
</template>
