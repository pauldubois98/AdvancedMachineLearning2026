<!-- regression_vs_classification: predict a number, or predict a label. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve } from '../lib/hist'
import { classStats, discriminant, twoGaussians, accuracy } from '../lib/stats'
import { boundary, classColors } from '../lib/cls'
import { BLUE, INK, RED } from '../lib/theme'
import type { Pt } from '../lib/geom'

const noise = ref(0.35)
const sep = ref(1)
const r = new Rng(8)
const u = Array.from({ length: 90 }, () => r.uniform(-2.5, 2.5))
const e = Array.from({ length: 90 }, () => r.normal())
const f = (x: number) => 0.9 * x + 0.4 * Math.sin(2 * x)
const reg = computed<Pt[]>(() => u.map((x, i) => [x, f(x) + noise.value * e[i]]))
const base = twoGaussians(new Rng(9), 150)
const cls = computed(() => {
  const X = base.X.map(([a, b], i) => {
    const c = base.y[i] ? [1.3, 0.7] : [-1.1, -0.5]
    // the class centres move apart (or together); the clouds keep their shape
    return [a + (sep.value - 1) * c[0], b + (sep.value - 1) * c[1]] as Pt
  })
  const st = classStats(X, base.y)
  const g = discriminant(st.mu, [st.pooled, st.pooled], st.pi)
  return { X, g, acc: accuracy(g, X, base.y) }
})
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <LineChart :series="[{ points: curve(f, -2.5, 2.5), color: INK }]" :dots="reg.map(([x, y]) => ({ x, y, color: BLUE, r: 3 }))"
        :x-domain="[-2.7, 2.7]" :y-domain="[-3.2, 3.2]" :x-ticks="[-2, -1, 0, 1, 2]" :y-ticks="[-2, -1, 0, 1, 2]" x-label="x" y-label="y ∈ ℝ"
        title="regression: predict a number" :title-color="BLUE" />
      <Plane :X="cls.X" :colors="classColors(base.y)" :size="2.6" :levels="[boundary(cls.g)]" :domain="[-4.5, 4.5, -3.4, 3.6]" axes x-label="x₁" y-label="x₂"
        title="classification: predict a label" :title-color="RED" />
    </div>
    <div class="foot">left, the black curve is the function to learn and the noise hides it; right, a straight boundary fitted to two classes (training accuracy <b>{{ (100 * cls.acc).toFixed(0) }}%</b>). y ∈ ℝ, or y ∈ {0, 1}, or y ∈ {1, …, K}.</div>
    <div class="controls">
      <Knob v-model="noise" :min="0" :max="1.2" :step="0.01" label="regression noise" :color="BLUE" />
      <Knob v-model="sep" :min="0" :max="2" :step="0.01" label="class separation" :color="RED" />
    </div>
  </div>
</template>
