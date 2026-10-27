<!-- choosing_k: the likelihood cannot choose K, a penalty can. Fit K = 1..8
     on a sample of the size you choose; BIC's penalty grows with log n. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { em2, kmeansStart, sampleMix2, THREE_BLOBS } from '../lib/gmm'
import { niceTicks } from '../lib/ticks'
import { BLUE, GOLD, GREEN, INK, RED } from '../lib/theme'

const n = ref(330)
const seed = ref(5)
const KS = [1, 2, 3, 4, 5, 6, 7, 8]
const res = computed(() => {
  const { X } = sampleMix2(THREE_BLOBS, n.value, seed.value)
  return KS.map((K) => {
    const L = em2(X, kmeansStart(X, K, 0, 1e-4, 3), 50).at(-1)!.ll
    const m = K * 6 - 1 // weights, means, covariances
    return { K, L, bic: -2 * L + m * Math.log(n.value), aic: -2 * L + 2 * m }
  })
})
const kb = computed(() => res.value.reduce((a, r) => (r.bic < a.bic ? r : a)).K)
const ka = computed(() => res.value.reduce((a, r) => (r.aic < a.aic ? r : a)).K)
const rng = (v: number[]) => { const lo = Math.min(...v), hi = Math.max(...v), pad = (hi - lo) * 0.08; return [lo - pad, hi + pad] as [number, number] }
const llDom = computed(() => rng(res.value.map((r) => r.L)))
const icDom = computed(() => rng(res.value.flatMap((r) => [r.bic, r.aic])))
</script>

<template>
  <div class="wrap">
    <div class="note top">The likelihood cannot choose K, a penalty can</div>
    <div class="body">
      <LineChart
        :series="[{ points: res.map((r) => [r.K, r.L]), color: BLUE, width: 2.4 }]"
        :dots="res.map((r) => ({ x: r.K, y: r.L, color: BLUE, r: 4 }))"
        :x-domain="[0.6, 8.4]" :y-domain="llDom" x-label="K" :x-ticks="KS" :y-ticks="niceTicks(llDom[0], llDom[1], 4).map((v) => Math.round(v))"
        title="ℓ_obs" :title-color="BLUE" :pad="{ l: 56, r: 10, t: 10, b: 34 }"
      />
      <LineChart
        :series="[{ points: res.map((r) => [r.K, r.bic]), color: GREEN, width: 2.4 }, { points: res.map((r) => [r.K, r.aic]), color: GOLD, width: 2.4 }]"
        :dots="[...res.map((r) => ({ x: r.K, y: r.bic, color: GREEN, r: 4 })), ...res.map((r) => ({ x: r.K, y: r.aic, color: GOLD, r: 4 })),
                { x: kb, y: res[kb - 1].bic, color: RED, r: 9, hollow: true }]"
        :labels="[{ x: 7.2, y: res[6].bic, text: 'BIC', color: GREEN, size: 13 }, { x: 7.2, y: res[6].aic, text: 'AIC', color: GOLD, size: 13 }]"
        :x-domain="[0.6, 8.4]" :y-domain="icDom" x-label="K" :x-ticks="KS" :y-ticks="niceTicks(icDom[0], icDom[1], 4).map((v) => Math.round(v))"
        title="BIC and AIC: lower is better" :pad="{ l: 56, r: 10, t: 10, b: 34 }"
      />
      <div class="side">
        <div class="h">Reading it</div>
        <p>— ℓ<sub>obs</sub> only ever rises with K</p>
        <p>— BIC is smallest at <b :style="{ color: GREEN }">K = {{ kb }}</b>; the data was made with 3</p>
        <p>— AIC is smallest at <b :style="{ color: GOLD }">K = {{ ka }}</b>; it penalises less, 2 per parameter against log n = {{ Math.log(n).toFixed(1) }}</p>
        <p class="note">Small samples: BIC can under-shoot; large ones: AIC drifts up.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="n" :min="30" :max="2000" log label="sample size n" :color="INK" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" label="seed" :digits="0" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 1fr 0.9fr; gap: 1.5rem; min-height: 0; }
.side { align-self: center; }
</style>
