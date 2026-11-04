<!-- eq_kl: two distributions, and KL term by term. Slide Q towards P. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, HIGH, INK, LOW, RED } from '../lib/theme'

const P = [0.40, 0.30, 0.15, 0.10, 0.04, 0.01]
const Q0 = [0.15, 0.20, 0.25, 0.20, 0.12, 0.08]
const a = ref(0)
const Q = computed(() => Q0.map((q, k) => (1 - a.value) * q + a.value * P[k]))
const terms = computed(() => P.map((p, k) => p * Math.log(p / Q.value[k])))
const kl = computed(() => terms.value.reduce((s, v) => s + v, 0))
const klr = computed(() => Q.value.reduce((s, q, k) => s + q * Math.log(q / P[k]), 0))
const pq = computed(() => [
  ...P.map((p, k) => ({ x: k + 1 - 0.19, y: p, w: 0.36, color: HIGH, alpha: 1 })),
  ...Q.value.map((q, k) => ({ x: k + 1 + 0.19, y: q, w: 0.36, color: LOW, alpha: 1 })),
])
const tb = computed(() => terms.value.map((v, k) => ({ x: k + 1, y: Math.max(v, 0), y0: Math.min(v, 0), w: 0.6, color: v > 0 ? RED : BLUE, alpha: 1 })))
</script>

<template>
  <div class="cmp top">
    <div class="formula" style="text-align: center"><Tex formula="\mathrm{KL}(P \,\|\, Q) = \sum_k p_k \log \frac{p_k}{q_k}" display /></div>
    <div class="r2">
      <LineChart :series="[]" :bars="pq" :x-domain="[0.4, 6.6]" :y-domain="[0, 0.45]" :x-ticks="[1, 2, 3, 4, 5, 6]" :y-ticks="[0, 0.2, 0.4]"
        :labels="[{ x: 5.2, y: 0.4, text: 'P (data)', color: HIGH }, { x: 5.2, y: 0.36, text: 'Q (map)', color: LOW }]" title="two distributions over the same items" />
      <LineChart :series="[{ points: [[0.4, 0], [6.6, 0]], color: INK, width: 0.8 }]" :bars="tb" :x-domain="[0.4, 6.6]" :y-domain="[-0.12, 0.42]"
        :x-ticks="[1, 2, 3, 4, 5, 6]" :y-ticks="[-0.1, 0, 0.1, 0.2, 0.3, 0.4]" :title="`each term p log(p/q): KL(P‖Q) = ${kl.toFixed(3)}`" />
    </div>
    <div class="foot">The big terms are where P puts weight but Q does not. KL ≥ 0, zero only when Q = P, and not symmetric:
      here KL(Q‖P) = <b>{{ klr.toFixed(3) }}</b>. In SNE the items are the pairs (i, j).</div>
    <div class="controls"><Knob v-model="a" :min="0" :max="1" :step="0.01" label="move Q towards P" :color="LOW" /></div>
  </div>
</template>
