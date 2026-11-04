<!-- eq_perplexity: the bisection that finds sigma_i, one try at a time. -->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { TOY, TOY_D, TOY_DOMAIN, TOY_N, nearest } from '../lib/data'
import { findSigma, perplexityOf, rowP } from '../lib/sne'
import { COMP, GREEN, HIGH, RED } from '../lib/theme'
import type { Pt } from '../lib/geom'

const i = ref(TOY.star)
const target = ref(8)
const step = ref(1)
const res = computed(() => findSigma(TOY_D, TOY_N, i.value, target.value))
watch([i, target], () => (step.value = 1))
const k = computed(() => Math.min(step.value, res.value.trace.length))
const cur = computed(() => res.value.trace[k.value - 1])
const ss = Array.from({ length: 160 }, (_, j) => 10 ** (-1.3 + (2.1 * j) / 159))
const curve = computed(() => ss.map((s) => [s, perplexityOf(TOY_D, TOY_N, i.value, s)] as [number, number]))
const dots = computed(() => res.value.trace.slice(0, k.value).map((t, j) => ({ x: t.sigma, y: t.perp, color: RED, r: j === k.value - 1 ? 6 : 3.5 })))
const labels = computed(() => res.value.trace.slice(0, Math.min(k.value, 6)).map((t, j) => ({ x: t.sigma * 1.1, y: t.perp + 1.5, text: String(j + 1), color: RED, anchor: 'start' })))
const p = computed(() => rowP(TOY_D, TOY_N, i.value, 1 / (2 * cur.value.sigma ** 2)).p)
const sizes = computed(() => TOY.X.map((_, j) => (j === i.value ? 0 : 1.5 + 30 * Math.sqrt(p.value[j]))))
const verdict = computed(() => {
  const d = cur.value.perp - target.value
  if (Math.abs(d) < 0.01) return 'on target: this is σᵢ'
  return d > 0 ? 'too many neighbours: shrink σᵢ' : 'too few neighbours: widen σᵢ'
})
</script>

<template>
  <div class="cmp top">
    <div class="formula" style="text-align: center"><Tex formula="\mathrm{Perp}(P_i) = 2^{H(P_i)}, \qquad H(P_i) = -\sum_j p_{j|i} \log_2 p_{j|i}" /></div>
    <div class="r23">
      <Plane :X="TOY.X" :colors="TOY.g.map((g) => COMP[g])" :sizes="sizes" :alpha="0.8" pickable @pick="(x, y) => (i = nearest(TOY.X, x, y))"
        :markers="[{ at: TOY.X[i] as Pt, color: RED, shape: 'star', size: 11 }]" :domain="TOY_DOMAIN" :title="`try ${k}: σ = ${cur.sigma.toFixed(3)}`" />
      <LineChart :series="[{ points: curve, color: HIGH, width: 2.2 }]" :hlines="[{ y: target, color: GREEN, dash: '5 4' }]" :dots="dots" :labels="labels"
        :x-domain="[0.05, 6.3]" :y-domain="[0, 46]" logX :x-ticks="[0.1, 1]" :y-ticks="[0, 10, 20, 30, 40]"
        x-label="σᵢ (log scale)" y-label="Perp" :title="`Perp = ${cur.perp.toFixed(2)}, target ${target}: ${verdict}`" />
    </div>
    <div class="foot">Try a width, compute the perplexity of p<sub>·|i</sub>; shrink σᵢ if it is too high, widen it if too low,
      and halve the step until the target is met. Usual targets: 5 to 50.</div>
    <div class="controls">
      <Knob v-model="target" :min="2" :max="40" :step="1" :digits="0" label="target perplexity" :color="GREEN" />
      <Knob v-model="step" :min="1" :max="res.trace.length" :step="1" :digits="0" label="bisection try" :color="RED" />
    </div>
  </div>
</template>
