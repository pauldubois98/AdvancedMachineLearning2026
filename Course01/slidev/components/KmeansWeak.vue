<!-- kmeans_weaknesses: K must be given, outliers grab a centre, and the
     clusters it finds are convex. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { kmeans, moons } from '../lib/stats'
import type { Pt } from '../lib/geom'
import { BLUE, GOLD, GREEN, INK, PURPLE, RED } from '../lib/theme'
import { circle } from '../lib/hist'

const K = ref(5)
const far = ref(9)
const noise = ref(0.06)
const COLS = [BLUE, RED, GREEN, PURPLE, GOLD, '#17becf', '#8c564b', '#e377c2']
const r = new Rng(31)
const centres: Pt[] = [[-1.6, -1.0], [1.7, -0.7], [0.1, 1.7]]
const X: Pt[] = centres.flatMap((c) => Array.from({ length: 60 }, () => [c[0] + r.normal(0, 0.5), c[1] + r.normal(0, 0.5)] as Pt))
const a = computed(() => kmeans(X, K.value, 0))
const out = computed(() => {
  const d = far.value / Math.SQRT2
  const Xo: Pt[] = [...X, [d, d], [d + 0.5, d + 0.7]]
  return { X: Xo, k: kmeans(Xo, 3, 0), at: [d + 0.25, d + 0.35] as Pt }
})
const mo = computed(() => { const m = moons(new Rng(4), 300, noise.value); return { X: m.X, k: kmeans(m.X, 2, 0) } })
const dom = (X: Pt[]): [number, number, number, number] => {
  const xs = X.map((p) => p[0]), ys = X.map((p) => p[1])
  return [Math.min(...xs) - 0.8, Math.max(...xs) + 1.4, Math.min(...ys) - 0.8, Math.max(...ys) + 1.4]
}
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> k-means (best of 8 starts) on three data sets. Left, three round groups, with the K you choose. Middle, the same groups plus two far points, K = 3. Right, two interleaved half-moons, K = 2.</div>
    <div class="r3">
      <Plane :X="X" :colors="a.s.map((k) => COLS[k])" :size="3" :domain="[-3.2, 3.4, -2.6, 3.2]" :markers="a.mu.map((m) => ({ at: m, color: INK, shape: 'x', size: 6 }))"
        :title="`K must be known: K = ${K}`" :title-color="RED" />
      <Plane :X="out.X" :colors="out.k.s.map((k) => COLS[k])" :size="3" :domain="dom(out.X)" :segments="circle(out.at, 1.1, INK, 1.2, [4, 3])"
        :markers="out.k.mu.map((m) => ({ at: m, color: INK, shape: 'x', size: 6 }))" title="outliers: two points" :title-color="RED" />
      <Plane :X="mo.X" :colors="mo.k.s.map((k) => COLS[k])" :size="3" :domain="[-1.4, 2.4, -1, 1.5]" :markers="mo.k.mu.map((m) => ({ at: m, color: INK, shape: 'x', size: 6 }))"
        title="non-convex shapes" :title-color="RED" />
    </div>
    <div class="foot">k-means minimises the squared distances to K centres: it splits or merges groups to match K, a far point pulls a whole centre with it, and every cluster is the set of points nearest one centre, so it is convex.</div>
    <div class="controls">
      <Knob v-model="K" :min="1" :max="8" :step="1" :digits="0" label="K (left)" :color="RED" />
      <Knob v-model="far" :min="3" :max="16" :step="0.1" label="outlier distance" :color="RED" />
      <Knob v-model="noise" :min="0" :max="0.3" :step="0.005" :digits="3" label="moon noise" :color="RED" />
    </div>
  </div>
</template>
