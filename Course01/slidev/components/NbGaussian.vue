<!-- naive_bayes_gaussian: one Gaussian per feature and per class, fitted by
     maximum likelihood, multiplied. The data may be correlated; the model
     ignores it. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve } from '../lib/hist'
import { accuracy, classStats, discriminant, lognpdf, npdf, twoGaussians } from '../lib/stats'
import { boundary, classColors, regionColor } from '../lib/cls'
import { BLUE, MUTED, RED } from '../lib/theme'
import type { Cov } from '../lib/geom'

const rho = ref(0)
const sep = ref(1)
const fit = computed(() => {
  const c = rho.value * Math.sqrt(0.8 * 0.6)
  const S: Cov = [0.8, c, 0.6]
  const m1: [number, number] = [-1.1 * sep.value, -0.5 * sep.value], m2: [number, number] = [1.3 * sep.value, 0.7 * sep.value]
  const d = twoGaussians(new Rng(14), 180, m1, m2, S)
  const st = classStats(d.X, d.y)
  // naive Bayes: the diagonal of each class covariance only
  const sd = st.S.map((s) => [Math.sqrt(s[0]), Math.sqrt(s[2])])
  const nb = (x: number, y: number) =>
    lognpdf(x, st.mu[1][0], sd[1][0]) + lognpdf(y, st.mu[1][1], sd[1][1]) + Math.log(st.pi[1])
    - lognpdf(x, st.mu[0][0], sd[0][0]) - lognpdf(y, st.mu[0][1], sd[0][1]) - Math.log(st.pi[0])
  const truth = discriminant([m1, m2], [S, S], [0.5, 0.5])
  const test = twoGaussians(new Rng(77), 2000, m1, m2, S)
  return { d, st, sd, nb, truth, acc: accuracy(nb, test.X, test.y), best: accuracy(truth, test.X, test.y) }
})
const dom: [number, number, number, number] = [-4, 4.5, -3.2, 3.4]
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 180 points per class from two Gaussians with the same covariance; the slider sets the correlation ρ between x₁ and x₂ inside each class. Naive Bayes fits one Gaussian per feature and per class and multiplies them, as if ρ were 0.</div>
    <div class="r3">
      <Plane :X="fit.d.X" :colors="classColors(fit.d.y)" :size="2.6" :domain="dom" title="1. choose a density" caption="Gaussian, one per feature" />
      <LineChart :series="[0, 1].map((k) => ({ points: curve((t) => npdf(t, fit.st.mu[k][0], fit.sd[k][0]), -4, 4.5), color: k ? RED : BLUE }))"
        :x-domain="[-4, 4.5]" :y-domain="[0, 0.62]" :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[]" x-label="x₁" title="2. estimate it per class (here x₁)" />
      <Plane :X="fit.d.X" :colors="classColors(fit.d.y)" :size="2.6" :domain="dom" :field="fit.nb" :field-color="regionColor"
        :levels="[boundary(fit.nb), boundary(fit.truth, MUTED, 1.4, [5, 4])]" title="3. classify" caption="arg maxₖ πₖ ∏ⱼ fₖ(xⱼ); dashed: the best boundary" />
    </div>
    <div class="foot">test accuracy: naive Bayes <b>{{ (100 * fit.acc).toFixed(1) }}%</b>, best possible {{ (100 * fit.best).toFixed(1) }}%. The independence assumption is false as soon as ρ ≠ 0, and the classifier often works anyway.</div>
    <div class="controls">
      <Knob v-model="rho" :min="-0.9" :max="0.9" :step="0.01" label="correlation ρ inside a class" :color="RED" />
      <Knob v-model="sep" :min="0.2" :max="1.6" :step="0.01" label="class separation" :color="BLUE" />
    </div>
  </div>
</template>
