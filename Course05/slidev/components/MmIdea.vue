<!-- mm_idea: majorize, then minimize. Each step builds a parabola G(.|h̄) that
     lies above F and touches it at h̄, jumps to its minimum, and starts again.
     The curvature of G is a knob: any value above F's own is a valid bound. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { range } from '../lib/losses'
import { GOLD, GREEN, INK, PURPLE, BLUE } from '../lib/theme'

// a smooth convex F with F'' <= 1.6 everywhere
const sp = (u: number) => Math.log1p(Math.exp(u))
const F = (h: number) => 0.5 * (h - 2) ** 2 * 0.6 + 0.6 * sp(2 * (h - 3))
const dF = (h: number) => 0.6 * (h - 2) + 1.2 / (1 + Math.exp(-2 * (h - 3)))
const FMAX2 = 0.6 + 0.6
const start = ref(4)
const L = ref(2.2)
const steps = ref(3)
const colors = [PURPLE, GOLD, GREEN, BLUE, PURPLE, GOLD, GREEN, BLUE]
const hs = range(0.8, 4.6, 200)
const path = computed(() => {
  const out = [start.value]
  for (let t = 0; t < steps.value; t++) { const h = out[out.length - 1]; out.push(h - dF(h) / L.value) }
  return out
})
const surrogates = computed(() => path.value.slice(0, -1).map((hb, t) => ({
  points: hs.map((h) => [h, F(hb) + dF(hb) * (h - hb) + 0.5 * L.value * (h - hb) ** 2] as [number, number]),
  color: colors[t], width: 1.6, dash: '6 4',
})))
</script>

<template>
  <div class="wrap">
    <div class="note top">G(h | h̄) is a function of h alone: the bar side is the point we sit at now, frozen.</div>
    <div class="body">
      <LineChart
        :series="[{ points: hs.map((h) => [h, F(h)]), color: INK, width: 2.6 }, ...surrogates]"
        :dots="path.map((h, t) => ({ x: h, y: F(h), color: t ? colors[t - 1] : INK, r: t ? 4.5 : 5.5 }))"
        :labels="[{ x: 4.3, y: Math.min(F(4.3), 2.9), text: 'F  ', color: INK, size: 15, anchor: 'end' }]"
        :x-domain="[0.8, 4.6]" :y-domain="[0, 3.1]" x-label="h" :x-ticks="[1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5]" :y-ticks="[]"
        title="the surrogate touches, and lies above"
      />
      <div class="side">
        <div class="h" :style="{ color: PURPLE }">Majorize</div>
        <p>build G(h | h̄) ≥ F(h), with G(h̄ | h̄) = F(h̄)</p>
        <div class="h" :style="{ color: GREEN }">Minimize</div>
        <p>h⁺ = argmin<sub>h</sub> G(h | h̄), then start again from h⁺</p>
        <p class="note">The point: G is chosen to be easy (separable) and minimized in closed form.</p>
        <Readout :items="path.map((h, t) => ({ label: `F(h<sub>${t}</sub>)`, value: F(h).toFixed(3) }))" />
      </div>
    </div>
    <div class="controls">
      <Knob v-model="steps" :min="0" :max="8" :step="1" label="MM steps" :digits="0" :color="INK" />
      <Knob v-model="start" :min="1" :max="4.5" :step="0.01" label="start h₀" :color="INK" />
      <Knob v-model="L" :min="FMAX2" :max="6" :step="0.05" label="curvature of G" :color="PURPLE" />
      <span class="note">A flatter G takes longer steps; a steeper one shorter. Both go downhill at every step.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.6fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
</style>
