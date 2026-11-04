<!-- lda_fit_steps: labelled data, one Gaussian per class with a shared
     covariance, and the rule. The class shares set the priors. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { classStats, discriminant, twoGaussians } from '../lib/stats'
import { boundary, classColors, regionColor } from '../lib/cls'
import { BLUE, RED } from '../lib/theme'

const share = ref(0.5)
const n = ref(160)
const fit = computed(() => {
  const N = Math.round(n.value)
  const n1 = Math.max(3, Math.round(2 * N * share.value)), n2 = Math.max(3, 2 * N - n1)
  const d = twoGaussians(new Rng(41), n1, undefined, undefined, undefined, undefined, n2)
  const st = classStats(d.X, d.y)
  return { d, st, g: discriminant(st.mu, [st.pooled, st.pooled], st.pi) }
})
const dom: [number, number, number, number] = [-4.2, 4.6, -3.4, 3.6]
const mk = computed(() => fit.value.st.mu.map((m, k) => ({ at: m, color: k ? RED : BLUE, shape: 'x' as const, size: 7 })))
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 2n labelled points from two Gaussians with the same covariance; the first slider sets the share that belongs to class 1. LDA estimates the two means, one pooled covariance and the priors π̂ₖ = Nₖ / N.</div>
    <div class="r3">
      <Plane :X="fit.d.X" :colors="classColors(fit.d.y)" :size="2.6" :domain="dom" title="1. labelled data" />
      <Plane :X="fit.d.X" :colors="classColors(fit.d.y)" :size="2" :domain="dom" :markers="mk"
        :ellipses="[{ mu: fit.st.mu[0], S: fit.st.pooled, color: BLUE }, { mu: fit.st.mu[1], S: fit.st.pooled, color: RED }]"
        title="2. one Gaussian per class, one shared Σ" :caption="`π̂₁ = ${fit.st.pi[0].toFixed(2)}, π̂₂ = ${fit.st.pi[1].toFixed(2)}: same shape per class, only the centres differ`" />
      <Plane :X="fit.d.X" :colors="classColors(fit.d.y)" :size="2" :domain="dom" :field="fit.g" :field-color="regionColor" :levels="[boundary(fit.g)]"
        title="3. classification rule" caption="predict k with the largest fₖ(x) πₖ" />
    </div>
    <div class="foot">a rarer class gets a smaller prior, and the boundary moves towards it: in doubt, LDA bets on the common class.</div>
    <div class="controls">
      <Knob v-model="share" :min="0.05" :max="0.95" :step="0.01" label="share of class 1" :color="BLUE" />
      <Knob v-model="n" :min="10" :max="400" log :step="0.01" label="points per class (on average) n" :color="RED" />
    </div>
  </div>
</template>
