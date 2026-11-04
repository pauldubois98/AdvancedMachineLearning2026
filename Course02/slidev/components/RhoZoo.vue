<!-- rho_zoo: the usual ρ, convex and not. One knob scales every δ: small δ
     means the losses leave the parabola early. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { rhoCauchy, rhoHuber, rhoTukey, rhoWelsch } from '../lib/reg'
import { BLUE, GOLD, GREEN, INK, MUTED, PURPLE, RED } from '../lib/theme'

const s = ref(1)
const ls = { points: curve((e) => 0.5 * e * e, -4.5, 4.5), color: MUTED, dash: '6,4', opacity: 0.6 }
const convex = computed(() => [
  { name: 'Huber', color: BLUE, f: (e: number) => rhoHuber(e, 1.5 * s.value) },
  { name: 'ℓ₁', color: GREEN, f: (e: number) => Math.abs(e) },
  { name: 'log cosh', color: GOLD, f: (e: number) => s.value * s.value * Math.log(Math.cosh(e / s.value)) },
])
const nonconvex = computed(() => [
  { name: 'Cauchy', color: PURPLE, f: (e: number) => s.value * s.value * rhoCauchy(e, Math.SQRT2 * s.value) },
  { name: 'Welsch', color: RED, f: (e: number) => (2 * s.value * s.value) * rhoWelsch(e, 1.5 * s.value) },
  { name: 'Tukey', color: INK, f: (e: number) => rhoTukey(e, 3 * s.value) / 2 },
])
const ser = (fam: { color: string; f: (e: number) => number }[]) => [ls, ...fam.map((c) => ({ points: curve(c.f, -4.5, 4.5), color: c.color, width: 2.4 }))]
const lab = (fam: { name: string; color: string; f: (e: number) => number }[]) => fam.map((c) => ({ x: 4.7, y: Math.min(c.f(4.5), 5.4) - 0.1, text: c.name, color: c.color, size: 13 }))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <div class="col">
        <LineChart :series="ser(convex)" :labels="[...lab(convex), { x: 2, y: 5.2, text: 'least squares', color: MUTED, anchor: 'end', size: 12 }]" :x-domain="[-4.6, 6.6]" :y-domain="[0, 5.6]" :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[]" x-label="residual e" title="convex" :title-color="BLUE" />
        <div class="note">dominated by large residuals</div>
      </div>
      <div class="col">
        <LineChart :series="ser(nonconvex)" :labels="[...lab(nonconvex), { x: 2, y: 5.2, text: 'least squares', color: MUTED, anchor: 'end', size: 12 }]" :x-domain="[-4.6, 6.6]" :y-domain="[0, 5.6]" :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[]" x-label="residual e" title="non-convex" :title-color="RED" />
        <div class="note">flat tails</div>
      </div>
    </div>
    <div class="foot">every δ multiplied by <b>{{ s.toFixed(2) }}</b>: Huber δ = {{ (1.5 * s).toFixed(2) }}, Tukey δ = {{ (3 * s).toFixed(2) }}, …</div>
    <div class="controls">
      <Knob v-model="s" :min="0.3" :max="2.5" :step="0.01" label="scale of every δ" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; text-align: center; }
</style>
