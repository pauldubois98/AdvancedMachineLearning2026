<!-- qda_vs_lda: when the classes have different covariances, LDA still
     draws a line; QDA fits one Σ per class and bends. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { accuracy, classStats, discriminant, twoGaussians } from '../lib/stats'
import { boundary, classColors, regionColor } from '../lib/cls'
import type { Cov } from '../lib/geom'
import { GREEN, PURPLE } from '../lib/theme'

const turn = ref(90)
const ratio = ref(3)
const n = ref(240)
const fit = computed(() => {
  // class 2: an ellipse with axes ratio:1, turned by `turn` degrees
  const t = (turn.value * Math.PI) / 180, l1 = 0.4 * ratio.value, l2 = 0.4
  const c = Math.cos(t), s = Math.sin(t)
  const S2: Cov = [l1 * c * c + l2 * s * s, (l1 - l2) * c * s, l1 * s * s + l2 * c * c]
  const d = twoGaussians(new Rng(17), Math.round(n.value), [-1.0, -0.3], [1.4, 0.6], [1.4, 0.75, 0.7], S2)
  const st = classStats(d.X, d.y)
  const lda = discriminant(st.mu, [st.pooled, st.pooled], st.pi)
  const qda = discriminant(st.mu, st.S, st.pi)
  return { d, st, lda, qda, aL: accuracy(lda, d.X, d.y), aQ: accuracy(qda, d.X, d.y) }
})
const dom: [number, number, number, number] = [-4.5, 4.8, -3.6, 4.0]
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> two Gaussian classes with different covariances: class 1 is fixed, class 2 is an ellipse whose length ratio and angle are the sliders. Both models are fitted to the same points.</div>
    <div class="r2">
      <Plane :X="fit.d.X" :colors="classColors(fit.d.y)" :size="2.4" :domain="dom" :field="fit.lda" :field-color="regionColor" :levels="[boundary(fit.lda)]"
        title="LDA: one shared Σ" :title-color="GREEN" :caption="`training accuracy ${(100 * fit.aL).toFixed(1)}%`" />
      <Plane :X="fit.d.X" :colors="classColors(fit.d.y)" :size="2.4" :domain="dom" :field="fit.qda" :field-color="regionColor" :levels="[boundary(fit.qda)]"
        :ellipses="[{ mu: fit.st.mu[0], S: fit.st.S[0], color: '#2b6cb0', nsig: [1] }, { mu: fit.st.mu[1], S: fit.st.S[1], color: '#c53030', nsig: [1] }]"
        title="QDA: one Σ per class" :title-color="PURPLE" :caption="`training accuracy ${(100 * fit.aQ).toFixed(1)}%`" />
    </div>
    <div class="foot">QDA has K times more covariance parameters to estimate: it pays off when the shapes really differ and the classes have enough points.</div>
    <div class="controls">
      <Knob v-model="ratio" :min="1" :max="8" :step="0.05" label="class 2: length ratio" :color="PURPLE" />
      <Knob v-model="turn" :min="0" :max="180" :step="1" :digits="0" unit="°" label="class 2: angle" :color="PURPLE" />
      <Knob v-model="n" :min="10" :max="500" log :step="0.01" label="points per class" :color="GREEN" />
    </div>
  </div>
</template>
