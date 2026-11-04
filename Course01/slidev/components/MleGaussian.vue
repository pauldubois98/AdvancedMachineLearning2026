<!-- mle_gaussian: the fitted Gaussian and the log-likelihood surface over
     (μ, σ). Move a candidate around the surface. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve, histBars } from '../lib/hist'
import { mean, normals, npdf, pvar } from '../lib/stats'
import { ramp, GREEN, LIGHT, PURPLE, RED } from '../lib/theme'

const mu = ref(1.5)
const sd = ref(1.5)
const x = normals(new Rng(5), 300, 2, 1.2)
const xm = mean(x), xs = Math.sqrt(pvar(x))
const n = x.length
let S2 = 0; for (const v of x) S2 += v * v
// ℓ(μ, σ) = −n log σ − Σ (x − μ)² / 2σ² (+ const), from the sufficient statistics
const ll = (m: number, s: number) => -n * Math.log(s) - (S2 - 2 * m * n * xm + n * m * m) / (2 * s * s)
const best = ll(xm, xs)
const purples = ramp(['#fcfbfd', '#dadaeb', '#9e9ac8', '#6a51a3', '#3f007d'])
const field = (m: number, s: number) => ll(m, s)
const fc = (v: number) => purples(Math.max(0, 1 + (v - best) / 60))
const bars = histBars(x, -2.5, 6.5, 26, LIGHT, 1)
const levels = [5, 15, 30, 50].map((d) => ({ f: field, level: best - d, color: 'rgba(255,255,255,0.7)', width: 1 }))
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 300 points from N(2, 1.2²). The candidate N(μ, σ²) (green, left) is the dot on the surface (right); the red dot is the maximum, μ̂ = x̄ and σ̂² = (1/n) Σ (xᵢ − x̄)².</div>
    <div class="r2">
      <LineChart :series="[{ points: curve((t) => npdf(t, mu, sd), -2.5, 6.5), color: GREEN }, { points: curve((t) => npdf(t, xm, xs), -2.5, 6.5), color: RED, width: 1.4, dash: '5,3' }]"
        :bars="bars" :x-domain="[-2.5, 6.5]" :y-domain="[0, 0.5]" :x-ticks="[-2, 0, 2, 4, 6]" :y-ticks="[]" x-label="x" title="the data and the candidate" :title-color="GREEN" />
      <Plane :field="field" :field-color="fc" :levels="levels" :domain="[1.2, 2.8, 0.85, 1.7]" :equal="false" axes x-label="μ" y-label="σ"
        :markers="[{ at: [xm, xs], color: RED, size: 6 }, { at: [mu, sd], color: GREEN, shape: 'ring', size: 7 }]" title="the log-likelihood surface" title-color="#6b46c1" />
    </div>
    <div class="foot">ℓ(μ, σ) − ℓ(μ̂, σ̂) = <b :style="{ color: PURPLE }">{{ (ll(mu, sd) - best).toFixed(1) }}</b> &nbsp;·&nbsp; μ̂ = {{ xm.toFixed(2) }}, σ̂ = {{ xs.toFixed(2) }}: the same answer as the method of moments in the Gaussian case</div>
    <div class="controls">
      <Knob v-model="mu" :min="1.2" :max="2.8" :step="0.01" label="μ" :color="GREEN" />
      <Knob v-model="sd" :min="0.86" :max="1.69" :step="0.01" label="σ" :color="GREEN" />
    </div>
  </div>
</template>
