<!-- mm_idea: ρ (Welsch, δ = 1.6) has a quadratic above it that touches it at
     the current residual. IRLS minimises that quadratic. Right: the same idea
     on a whole objective, F(θ) = Σ ρ(θ − xᵢ); each step goes to the bottom of
     the majorant, and F can only go down. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { fmt } from '../lib/reg'
import { BLUE, GOLD, GREEN, INK, MUTED, RED } from '../lib/theme'

const D = 1.6
const rho = (e: number) => 1 - Math.exp(-(e * e) / (2 * D * D))
const drho = (e: number) => (e / (D * D)) * Math.exp(-(e * e) / (2 * D * D))
const om = (e: number) => Math.exp(-(e * e) / (2 * D * D)) / (D * D)
const at = ref(3.4)
const maj = (e: number, a: number) => rho(a) + drho(a) * (e - a) + 0.5 * om(a) * (e - a) ** 2

const DATA = [-0.8, -0.3, 0, 0.2, 0.5, 0.9, 4.4, 4.9, 5.3]
const F = (t: number) => DATA.reduce((s, x) => s + rho(t - x), 0)
const Fmaj = (t: number, a: number) => DATA.reduce((s, x) => s + maj(t - x, a - x), 0)
const th0 = ref(3.2)
const k = ref(1)
const iters = computed(() => {
  const out = [th0.value]
  for (let i = 0; i < 30; i++) {
    const t = out[out.length - 1]
    const w = DATA.map((x) => om(t - x))
    out.push(DATA.reduce((s, x, j) => s + w[j] * x, 0) / w.reduce((a, b) => a + b, 0))
  }
  return out
})
const cur = computed(() => iters.value[k.value - 1])
const nxt = computed(() => iters.value[k.value])
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <LineChart :series="[{ points: curve(rho, -6, 6), color: INK, width: 2.6 }, { points: curve((e) => maj(e, at), -6, 6), color: GOLD, dash: '6,4' }]"
        :dots="[{ x: at, y: rho(at), color: GOLD, r: 6 }, { x: 0, y: maj(0, at), color: GREEN, r: 5 }]"
        :x-domain="[-6, 6]" :y-domain="[-0.1, 1.9]" :x-ticks="[-6, -3, 0, 3, 6]" :y-ticks="[]" x-label="residual e" title="ρ and a quadratic that sits above it" :title-color="GOLD" />
      <LineChart :series="[{ points: curve(F, -2, 7), color: INK, width: 2.6 }, { points: curve((t) => Fmaj(t, cur), -2, 7), color: GOLD, dash: '6,4' }]"
        :dots="[...DATA.map((x) => ({ x, y: 0.15, color: BLUE, r: 3.5 })), { x: cur, y: F(cur), color: GOLD, r: 6 }, { x: nxt, y: F(nxt), color: GREEN, r: 6 }]"
        :arrows="[{ x0: cur, y0: F(cur), x1: nxt, y1: F(nxt), color: GREEN, width: 1.8 }]"
        :x-domain="[-2, 7]" :y-domain="[0, 9.5]" :x-ticks="[-2, 0, 2, 4, 6]" :y-ticks="[]" x-label="θ" y-label="F(θ) = Σ ρ(θ − xᵢ)" title="next iteration: go to the bottom of the majorant" :title-color="GREEN" />
    </div>
    <div class="foot">they touch at e = {{ fmt(at) }}, and the quadratic is ≥ ρ everywhere. Step {{ k }}: θ = {{ fmt(cur, 3) }} → <b :style="{ color: GREEN }">{{ fmt(nxt, 3) }}</b>, F = {{ fmt(F(cur), 3) }} → {{ fmt(F(nxt), 3) }}. Non-convex ρ: start near the outliers and IRLS settles on them.</div>
    <div class="controls">
      <Knob v-model="at" :min="-5.5" :max="5.5" :step="0.01" label="touch point" :color="GOLD" />
      <Knob v-model="th0" :min="-1.5" :max="6.5" :step="0.01" label="start θ⁰" :color="RED" />
      <Knob v-model="k" :min="1" :max="15" :step="1" :digits="0" label="step k" :color="GREEN" />
    </div>
  </div>
</template>
