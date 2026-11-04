<!-- ls_residuals: try a line, read its residuals and their squares; the loss
     is the total area of the squares, smallest at the least squares line. -->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Rng } from '../lib/rng'
import { fitLine, fmt, lineData } from '../lib/reg'
import { lineSeg } from '../lib/draw'
import type { Poly, Seg } from './Plane.vue'
import { BLUE, GREEN, INK, RED } from '../lib/theme'

const data = lineData(new Rng(11), 22, 1.1)
const best = fitLine(data.x, data.y)
const b0 = ref(-0.6)
const b1 = ref(0.3)
const snap = ref(false)
watch(snap, (v) => { if (v) { b0.value = +best[0].toFixed(2); b1.value = +best[1].toFixed(2) } })
watch([b0, b1], () => { if (Math.abs(b0.value - best[0]) > 0.006 || Math.abs(b1.value - best[1]) > 0.006) snap.value = false })
const X = data.x.map((v, i) => [v, data.y[i]] as [number, number])
const e = computed(() => data.x.map((v, i) => data.y[i] - b0.value - b1.value * v))
const L = computed(() => 0.5 * e.value.reduce((s, v) => s + v * v, 0))
const Lbest = 0.5 * data.x.reduce((s, v, i) => s + (data.y[i] - best[0] - best[1] * v) ** 2, 0)
const resid = computed<Seg[]>(() => data.x.map((v, i) => ({ a: [v, data.y[i]], b: [v, b0.value + b1.value * v], color: RED, width: 1.6 })))
const squares = computed<Poly[]>(() => data.x.map((v, i) => {
  const f = b0.value + b1.value * v, a = Math.abs(e.value[i]), lo = Math.min(f, data.y[i])
  return { pts: [[v, lo], [v + a, lo], [v + a, lo + a], [v, lo + a]], fill: RED, alpha: 0.16, stroke: RED, width: 0.8 }
}))
const dom: [number, number, number, number] = [-3.6, 3.6, -4.6, 4.9]
const col = computed(() => (snap.value ? GREEN : INK))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Plane :X="X" :colors="BLUE" :size="4" :domain="dom" :segments="[lineSeg([b0, b1], -3.6, 3.6, col, 2.4), ...resid]" pointsFirst title="Residuals" caption="eᵢ = yᵢ − xᵢ′ᵀβ" />
      <Plane :X="X" :colors="BLUE" :size="4" :domain="dom" :polys="squares" :segments="[lineSeg([b0, b1], -3.6, 3.6, col, 2.4)]" title="Square error" :title-color="RED" caption="L(β) = ½ Σ eᵢ² = ½ ‖Xβ − y‖²" />
    </div>
    <div class="foot">L(β) = <b :style="{ color: RED }">{{ fmt(L) }}</b>; the least squares line reaches <b :style="{ color: GREEN }">{{ fmt(Lbest) }}</b> at β̂ = ({{ fmt(best[0]) }}, {{ fmt(best[1]) }})</div>
    <div class="controls">
      <Knob v-model="b0" :min="-2" :max="3" :step="0.01" label="intercept β₀" :color="col" />
      <Knob v-model="b1" :min="-1" :max="2.5" :step="0.01" label="slope β₁" :color="col" />
      <Toggle v-model="snap" label="least squares" :color="GREEN" />
    </div>
  </div>
</template>
