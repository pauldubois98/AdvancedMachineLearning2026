<!-- mu_eta_surrogate: one entry H_kj, the others frozen. F is a parabola of
     curvature [WᵀW]_kk whose vertex may lie below zero; the surrogate G is
     stiffer, by the other entries' share of [WᵀWH̄]_kj / H̄_kj. Newton on F
     can land in the negatives; the minimum of G never does. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { range } from '../lib/losses'
import { GREEN, INK, PURPLE, RED } from '../lib/theme'

const hb = ref(1.2)
const vertex = ref(-0.4)
const other = ref(1.2)
const a = 1
const F = (h: number) => 0.5 * a * (h - vertex.value) ** 2
const Gcurv = computed(() => a + other.value / hb.value) // [WᵀWH̄]/H̄ = a + c/H̄
const G = (h: number) => F(hb.value) + a * (hb.value - vertex.value) * (h - hb.value) + 0.5 * Gcurv.value * (h - hb.value) ** 2
const newton = computed(() => vertex.value)
const muStep = computed(() => hb.value - (a * (hb.value - vertex.value)) / Gcurv.value)
const hs = range(-1.2, 2.6, 200)
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[{ points: hs.map((h) => [h, F(h)]), color: INK, width: 2.6 }, { points: hs.map((h) => [h, G(h)]), color: PURPLE, width: 2, dash: '6 4' }]"
        :bands="[{ x0: -1.2, x1: 0, color: '#edeef0', alpha: 1 }]"
        :dots="[{ x: hb, y: F(hb), color: INK, r: 5 }, { x: newton, y: F(newton), color: RED, r: 5 }, { x: muStep, y: F(muStep), color: GREEN, r: 5 }, { x: muStep, y: G(muStep), color: PURPLE, r: 4, hollow: true }]"
        :labels="[{ x: -0.6, y: 3.3, text: 'forbidden', color: '#9aa0a6', size: 12 }, { x: newton - 0.05, y: F(newton) + 0.3, text: 'Newton step', color: RED, size: 12, anchor: 'end' }, { x: muStep + 0.05, y: F(muStep) - 0.2, text: 'MU step', color: GREEN, size: 12, anchor: 'start' }, { x: 2.45, y: Math.min(F(2.45), 3.3), text: 'F  ', color: INK, size: 14, anchor: 'end' }, { x: hb + 0.05, y: F(hb) + 0.25, text: 'H̄_kj', color: INK, size: 13, anchor: 'start' }]"
        :x-domain="[-1.2, 2.6]" :y-domain="[0, 3.6]" x-label="one entry H_kj, the others frozen" :x-ticks="[0]" :y-ticks="[]"
        title="the surrogate is the steeper parabola"
      />
      <div class="side">
        <div class="h" :style="{ color: PURPLE }">The two curvatures</div>
        <Tex formula="G'' = \frac{[W^\top W\bar H]_{kj}}{\bar H_{kj}} \;\geq\; [W^\top W]_{kk} = F''" display />
        <Readout :items="[{ label: 'F″', value: a.toFixed(2) }, { label: 'G″', value: Gcurv.toFixed(2), color: PURPLE }]" />
        <div class="h" :style="{ color: GREEN }">The step is short</div>
        <p>MU lands at <b :style="{ color: GREEN }">{{ muStep.toFixed(2) }}</b>, always ≥ 0.</p>
        <p :style="{ color: RED }">Newton on F lands at {{ newton.toFixed(2) }}{{ newton < 0 ? ', in the negatives' : '' }}.</p>
        <p class="note">η is the step that lands on the minimum of an upper bound.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="hb" :min="0.05" :max="2.2" :step="0.01" label="current H̄_kj" :color="INK" />
      <Knob v-model="vertex" :min="-0.9" :max="1.8" :step="0.01" label="vertex of F" :color="RED" />
      <Knob v-model="other" :min="0" :max="3" :step="0.01" label="the other entries' share" :color="PURPLE" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.6fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
</style>
