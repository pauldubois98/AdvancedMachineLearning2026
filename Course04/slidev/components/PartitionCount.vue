<!-- eq_kmeans: how many partitions an exhaustive search would have to try.
     Both sliders push the count straight out of reach. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { GREEN, RED } from '../lib/theme'

const n = ref(100)
const K = ref(5)

/** log10 of the Stirling number S(n, K) times nothing else: the number of
 *  ways to split n labelled rows into exactly K non-empty groups. Summed in
 *  log space, because the terms overflow long before n = 100. */
const logP = computed(() => {
  const lg = (x: number) => lgamma(x + 1)
  // log of the term for k, in P(n, K) = (1/K!) sum_k (-1)^(K-k) C(K,k) k^n
  const term = (k: number) =>
    lg(K.value) - lg(k) - lg(K.value - k) + n.value * Math.log(k) - lg(K.value)
  let best = -Infinity
  for (let k = 1; k <= K.value; k++) best = Math.max(best, term(k))
  let sum = 0
  for (let k = 1; k <= K.value; k++) {
    sum += ((K.value - k) % 2 === 0 ? 1 : -1) * Math.exp(term(k) - best)
  }
  return (best + Math.log(Math.max(sum, 1e-300))) / Math.LN10
})

function lgamma(x: number): number {
  // Lanczos
  const g = [
    676.5203681218851, -1259.1392167224028, 771.32342877765313,
    -176.61502916214059, 12.507343278686905, -0.13857109526572012,
    9.9843695780195716e-6, 1.5056327351493116e-7,
  ]
  if (x < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * x)) - lgamma(1 - x)
  x -= 1
  let a = 0.99999999999980993
  const t = x + 7.5
  for (let i = 0; i < g.length; i++) a += g[i] / (x + i + 1)
  return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a)
}

const years = computed(() => {
  // a billion partitions a second
  const logSeconds = logP.value - 9
  return logSeconds - Math.log10(3.15e7)
})
const shown = computed(() => {
  const e = Math.floor(logP.value)
  const m = 10 ** (logP.value - e)
  return logP.value < 6 ? (10 ** logP.value).toFixed(0) : `${m.toFixed(1)} × 10<sup>${e}</sup>`
})
</script>

<template>
  <div class="box">
    <div class="controls">
      <Knob v-model="n" :min="4" :max="200" :step="1" label="rows n" :digits="0" :color="RED" />
      <Knob v-model="K" :min="2" :max="10" :step="1" label="clusters K" :digits="0" :color="RED" />
    </div>
    <div class="result">
      <span class="note">partitions to try:</span>
      <span class="big" :style="{ color: RED }" v-html="shown" />
    </div>
    <Readout
      :items="[
        { label: 'at a billion tried per second', value: years > 0 ? `10<sup>${years.toFixed(0)}</sup> years` : 'instant', color: RED },
        { label: 'k-means instead', value: 'O(t K N), a local minimum', color: GREEN },
      ]"
    />
  </div>
</template>

<style scoped>
.box { display: flex; flex-direction: column; gap: 0.55rem; align-items: center; margin-top: 0.4rem; }
.controls { display: flex; gap: 2rem; }
.controls > :deep(.knob) { min-width: 11rem; }
.result { display: flex; align-items: baseline; gap: 0.6rem; }
.big { font-size: 1.6rem; font-weight: 600; font-variant-numeric: tabular-nums; }
</style>
