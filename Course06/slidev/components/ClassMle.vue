<!-- eq_complete_mle, right panel: the three numbers read off a labelled
     sample. Dashed line: the class mean; arrow: one standard deviation. -->
<script setup lang="ts">
import { ANIMALS, ANIMAL_FIT, resp1 } from '../lib/gmm'
import { edges, stacked } from '../lib/charts'
import { COMP } from '../lib/theme'

const z = ANIMALS.map((x) => (resp1(x, ANIMAL_FIT)[0] > 0.5 ? 0 : 1))
const groups = [ANIMALS.filter((_, i) => z[i] === 0), ANIMALS.filter((_, i) => z[i] === 1)]
const st = groups.map((g) => {
  const m = g.reduce((a, b) => a + b, 0) / g.length
  return { p: g.length / ANIMALS.length, m, s: Math.sqrt(g.reduce((a, b) => a + (b - m) ** 2, 0) / g.length) }
})
</script>

<template>
  <LineChart
    :series="[]"
    :arrows="st.map((s, k) => ({ x0: s.m - s.s, y0: 66, x1: s.m + s.s, y1: 66, color: COMP[k], width: 1.8, both: true }))"
    :bars="stacked(groups, edges(81.5, 98.5, 1), COMP, { alpha: 0.8 })"
    :vlines="st.map((s, k) => ({ x: s.m, color: COMP[k], dash: '6 4' }))"
    :labels="st.map((s, k) => ({ x: s.m + 1.9, y: 72, text: `p̂${k ? '₂' : '₁'} = ${s.p.toFixed(2)}`, color: COMP[k], anchor: 'middle', size: 13 }))"
    :x-domain="[81, 99]" :y-domain="[0, 85]" x-label="length (mm)" :x-ticks="[82, 86, 90, 94, 98]" :y-ticks="[]"
    title="dashed line: μ̂ₖ, arrow: ± σ̂ₖ" :unit-height="260"
  />
</template>
