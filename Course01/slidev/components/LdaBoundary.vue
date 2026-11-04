<!-- lda_boundary: the discriminant δₖ is linear in x, so the boundary is a
     line; the priors only shift it. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { classStats, discriminant, twoGaussians, inv2, mulv } from '../lib/stats'
import { boundary, classColors, regionColor } from '../lib/cls'
import { GREEN, MUTED } from '../lib/theme'

const pi1 = ref(0.5)
const data = twoGaussians(new Rng(15), 200)
const st = classStats(data.X, data.y)
const g = computed(() => discriminant(st.mu, [st.pooled, st.pooled], [pi1.value, 1 - pi1.value]))
const g0 = discriminant(st.mu, [st.pooled, st.pooled], [0.5, 0.5])
const Si = inv2(st.pooled)
const w = mulv(Si, [st.mu[1][0] - st.mu[0][0], st.mu[1][1] - st.mu[0][1]])
const shift = computed(() => Math.log(pi1.value / (1 - pi1.value)))
</script>

<template>
  <div class="cmp">
    <div class="r23" style="align-items: center">
      <div style="text-align: center">
        <p class="cap">the discriminant function</p>
        <p :style="{ color: GREEN }" style="font-size: 1.15rem"><Tex display formula="\delta_k(x) = x^T\Sigma^{-1}\mu_k - \tfrac12\mu_k^T\Sigma^{-1}\mu_k + \log\pi_k" /></p>
        <p>is linear in x, so δ₂ − δ₁ = 0 is a line</p>
        <p class="note" style="margin-top: 1rem">here w = Σ⁻¹(μ₂ − μ₁) = ({{ w[0].toFixed(2) }}, {{ w[1].toFixed(2) }}): the line is perpendicular to w; log(π₁/π₂) = {{ shift.toFixed(2) }} slides it along w</p>
      </div>
      <Plane :X="data.X" :colors="classColors(data.y)" :size="2.8" :domain="[-4.2, 4.6, -3.4, 3.6]" :field="g" :field-color="regionColor"
        :levels="[boundary(g0, MUTED, 1.4, [5, 4]), boundary(g)]" caption="dashed: the boundary with equal priors" />
    </div>
    <div class="foot">changing the priors moves the line but never turns it: the slope is set by Σ and the means only.</div>
    <div class="controls"><Knob v-model="pi1" :min="0.01" :max="0.99" :step="0.01" label="prior π₁ (blue)" color="#2b6cb0" /></div>
  </div>
</template>
