<!-- pca_gaussian: a 2-D Gaussian, its principal axes, the projection on the
     first one and the decorrelated components. The cloud's shape is live. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { pca } from '../lib/sne'
import { GOLD, GRID, HIGH, LOW, PCA_C } from '../lib/theme'
import type { Pt } from '../lib/geom'

const rho = ref(-0.8)
const s2 = ref(0.75)
const r = new Rng(1)
const Z0 = Array.from({ length: 400 }, () => [r.normal(), r.normal()])
const X = computed<Pt[]>(() => {
  const a = Math.sqrt(1.8), b = s2.value * Math.sqrt(1.8)
  const c = rho.value
  // Cholesky of [[a^2, c a b], [c a b, b^2]]
  return Z0.map(([u, v]) => [a * u, b * (c * u + Math.sqrt(1 - c * c) * v)])
})
const fit = computed(() => pca(X.value, 2))
const share = computed(() => fit.value.values[0] / (fit.value.values[0] + fit.value.values[1]))
const axes = computed(() => fit.value.vectors.map((v, k) => {
  const L = 2 * Math.sqrt(Math.max(fit.value.values[k], 0))
  return { a: [0, 0] as Pt, b: [v[0] * L, v[1] * L] as Pt, color: k ? GOLD : PCA_C, width: 2.6, arrow: true }
}))
const proj = computed(() => {
  const p = fit.value.vectors[0]
  return X.value.map(([x, y]) => { const t = x * p[0] + y * p[1]; return [t * p[0], t * p[1]] as Pt })
})
const projSegs = computed(() => X.value.filter((_, i) => i % 5 === 0).map((x, k) => ({ a: x, b: proj.value[k * 5], color: GRID, width: 0.7 })))
const p1line = computed(() => { const p = fit.value.vectors[0]; return [{ a: [-7 * p[0], -7 * p[1]] as Pt, b: [7 * p[0], 7 * p[1]] as Pt, color: PCA_C, width: 1.3 }] })
const comps = computed<Pt[]>(() => fit.value.Z.map((z) => [z[0], z[1]]))
const dom: [number, number, number, number] = [-5, 5, -4, 4]
</script>

<template>
  <div class="cmp">
    <div class="r3">
      <Plane :X="X" :colors="HIGH" :alpha="0.45" :size="2.2" :segments="axes" :domain="dom" title="data and principal axes" />
      <Plane :X="[...X, ...proj]" :colors="[...X.map(() => 'rgba(43,108,176,0.35)'), ...proj.map(() => PCA_C)]" :size="2"
        :segments="[...p1line, ...projSegs]" :domain="dom" title="projection on the first axis" />
      <Plane :X="comps" :colors="LOW" :alpha="0.6" :size="2.2" :domain="dom"
        :segments="[{ a: [-5, 0], b: [5, 0], color: GRID }, { a: [0, -4], b: [0, 4], color: GRID }]" title="principal components" />
    </div>
    <div class="foot">The first axis keeps <b>{{ (100 * share).toFixed(0) }}%</b> of the variance; the components are decorrelated.</div>
    <div class="controls">
      <Knob v-model="rho" :min="-0.97" :max="0.97" :step="0.01" label="correlation ρ" :color="HIGH" />
      <Knob v-model="s2" :min="0.2" :max="1.4" :step="0.01" label="σ₂ / σ₁" :color="HIGH" />
    </div>
  </div>
</template>
