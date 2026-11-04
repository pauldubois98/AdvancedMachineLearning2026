<!-- sigma_effect: one width for every point, or one width per point set by
     the perplexity, on a dense and a sparse group. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { findSigma, rowP, sqdist } from '../lib/sne'
import { BLUE, GREEN, HIGH, RED } from '../lib/theme'
import type { Pt } from '../lib/geom'

const r = new Rng(5)
const X: Pt[] = [
  ...Array.from({ length: 70 }, () => [r.normal(-2, 0.35), r.normal(0, 0.35)] as Pt),
  ...Array.from({ length: 70 }, () => [r.normal(2.2, 1.3), r.normal(0, 1.3)] as Pt),
]
const n = X.length
const D = sqdist(X)
let iS = 70, bd = Infinity
for (let j = 70; j < n; j++) { const d = (X[j][0] - 2.2) ** 2 + X[j][1] ** 2; if (d < bd) { bd = d; iS = j } }
const stars = [0, iS]
const mode = ref('one')
const sigma = ref(0.6)
const perp = ref(10)
const rows = computed(() => stars.map((i) => {
  if (mode.value === 'one') return { p: rowP(D, n, i, 1 / (2 * sigma.value ** 2)).p, s: sigma.value }
  const f = findSigma(D, n, i, perp.value)
  return { p: f.p, s: f.sigma }
}))
const sizes = computed(() => X.map((_, j) => 1.2 + 26 * Math.sqrt(rows.value[0].p[j] + rows.value[1].p[j])))
const ells = computed(() => stars.map((i, k) => ({ mu: X[i], S: [rows.value[k].s ** 2, 0, rows.value[k].s ** 2] as [number, number, number], color: RED, nsig: [2], width: 1.3, dash: [5, 4] })))
const counts = computed(() => rows.value.map((rw) => 2 ** -rw.p.reduce((s, v) => s + (v > 1e-12 ? v * Math.log2(v) : 0), 0)))
</script>

<template>
  <div class="cmp">
    <Plane :X="X" :colors="X.map((_, j) => (j < 70 ? BLUE : HIGH))" :sizes="sizes" :alpha="0.7" :ellipses="ells"
      :markers="stars.map((i) => ({ at: X[i], color: RED, shape: 'star', size: 11 }))" :domain="[-3.6, 6.4, -3.4, 3.4]"
      :title="mode === 'one' ? `one width σ = ${sigma.toFixed(2)} for both stars` : `σ = ${rows[0].s.toFixed(2)} (dense) and ${rows[1].s.toFixed(2)} (sparse)`"
      :title-color="mode === 'one' ? RED : GREEN" />
    <div class="foot">Effective neighbours: <b>{{ counts[0].toFixed(1) }}</b> for the dense star, <b>{{ counts[1].toFixed(1) }}</b> for the sparse one.
      <span v-if="mode === 'one'">One width cannot suit both regions.</span><span v-else>A width per point gives every point about the same number of neighbours.</span></div>
    <div class="controls">
      <Choice v-model="mode" :options="[{ value: 'one', label: 'one σ for all', color: RED }, { value: 'perp', label: 'σᵢ from the perplexity', color: GREEN }]" />
      <Knob v-if="mode === 'one'" v-model="sigma" :min="0.1" :max="3" log label="σ" :color="RED" />
      <Knob v-else v-model="perp" :min="2" :max="60" :step="1" :digits="0" label="perplexity" :color="GREEN" />
    </div>
  </div>
</template>
