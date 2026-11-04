<!-- logistic_mm: f(x) = log(1 + eˣ) has a quadratic majorant tight at y, with
     curvature ω(y) = (σ(y) − ½)/y: the same IRLS machinery as robust regression. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { fmt, log1pexp, sigmoid } from '../lib/reg'
import { GOLD, GREEN, INK } from '../lib/theme'

const at = ref(-2.6)
const om = (z: number) => (Math.abs(z) < 1e-6 ? 0.25 : (sigmoid(z) - 0.5) / z)
const maj = computed(() => (x: number) => log1pexp(at.value) + sigmoid(at.value) * (x - at.value) + 0.5 * om(at.value) * (x - at.value) ** 2)
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <LineChart :series="[{ points: curve(log1pexp, -6, 6), color: INK, width: 2.6 }, { points: curve(maj, -6, 6), color: GOLD, dash: '6,4', width: 2.2 }]"
        :dots="[{ x: at, y: log1pexp(at), color: GOLD, r: 6 }]" :x-domain="[-6, 6]" :y-domain="[-0.3, 6.5]" :x-ticks="[-6, -3, 0, 3, 6]" :y-ticks="[]" x-label="x"
        title="f(x) = log(1 + eˣ) and its majorant, tight at y" :title-color="GOLD" />
      <LineChart :series="[{ points: curve(om, -6, 6), color: GREEN, width: 2.8 }]" :dots="[{ x: at, y: om(at), color: GOLD, r: 6 }]"
        :x-domain="[-6, 6]" :y-domain="[0, 0.3]" :x-ticks="[-6, -3, 0, 3, 6]" :y-ticks="[0, 0.1, 0.2]" x-label="y" y-label="ω(y)" title="the weight ω(y) = (1/y)(1/(1 + e^−y) − ½)" :title-color="GREEN" />
    </div>
    <div class="foot"><Tex formula="f(x) \leq f(y) + \dot f(y)(x-y) + \tfrac12\,\omega(y)(x-y)^2" />, here y = {{ fmt(at) }} and ω(y) = <b :style="{ color: GREEN }">{{ fmt(om(at), 4) }}</b> (at most ¼, at y = 0)</div>
    <div class="controls">
      <Knob v-model="at" :min="-5.5" :max="5.5" :step="0.01" label="tight at y" :color="GOLD" />
    </div>
  </div>
</template>
