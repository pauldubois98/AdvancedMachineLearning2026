<!-- discriminative_vs_generative: logistic regression models p(y|x)
     directly; LDA models p(x|y) and p(y). On small samples the generative
     model, when right, needs fewer points. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { accuracy, classStats, discriminant, logistic, twoGaussians } from '../lib/stats'
import { boundary, classColors } from '../lib/cls'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const n = ref(10)
const seed = ref(9)
const N = computed(() => Math.round(n.value))
const test = twoGaussians(new Rng(999), 2000)
const truth = discriminant([[-1.1, -0.5], [1.3, 0.7]], [[1, 0.35, 0.7], [1, 0.35, 0.7]], [0.5, 0.5])
const bayes = accuracy(truth, test.X, test.y)
const fit = computed(() => {
  const d = twoGaussians(new Rng(seed.value), N.value)
  const lr = logistic(d.X, d.y)
  const st = classStats(d.X, d.y)
  const lda = discriminant(st.mu, [st.pooled, st.pooled], st.pi)
  return { d, lr, lda, st, aLr: accuracy(lr, test.X, test.y), aLda: accuracy(lda, test.X, test.y) }
})
const dom: [number, number, number, number] = [-4, 4.2, -3.2, 3.4]
const tb = boundary(truth, MUTED, 1.4, [5, 4])
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> n points per class from two Gaussians with the same covariance. Both models are fitted to the same points and scored on 4000 new ones. The dashed grey line is the best possible boundary.</div>
    <div class="r2">
      <Plane :X="fit.d.X" :colors="classColors(fit.d.y)" :size="3" :levels="[tb, boundary(fit.lr, INK, 2.6)]" :domain="dom"
        title="discriminative: logistic regression" :title-color="BLUE" :caption="`model p(y | x) directly · test accuracy ${(100 * fit.aLr).toFixed(1)}%`" />
      <Plane :X="fit.d.X" :colors="classColors(fit.d.y)" :size="3" :levels="[tb, boundary(fit.lda, INK, 2.6)]" :domain="dom"
        :ellipses="[{ mu: fit.st.mu[0], S: fit.st.pooled, color: BLUE }, { mu: fit.st.mu[1], S: fit.st.pooled, color: RED }]"
        title="generative: LDA" :title-color="RED" :caption="`model p(x | y) and p(y) · test accuracy ${(100 * fit.aLda).toFixed(1)}%`" />
    </div>
    <div class="foot">the best possible accuracy here is {{ (100 * bayes).toFixed(1) }}%. With few points the generative model, whose assumptions hold, is usually closer to it; with many, both get there, and the discriminative one assumes less.</div>
    <div class="controls">
      <Knob v-model="n" :min="3" :max="500" log :step="0.01" label="points per class n" :color="GREEN" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" :digits="0" label="new sample" :color="INK" />
    </div>
  </div>
</template>
