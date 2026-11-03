<!-- knob_gmm_k: Gaussian mixtures with K = 1 ... 8 components, fitted by EM
     on n points of the three clusters, then scored per point on the fitted
     sample and on a fresh one. Right: the fitted mixture for the current K. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLOB_SEED, gmmBlobs } from '../lib/c08'
import { em2, kmeansStart, loglik2, type Mix2 } from '../lib/gmm'
import { useSweep } from '../lib/sweep'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const n = ref(400)
const K = ref(3)
const KS = Array.from({ length: 8 }, (_, i) => i + 1)
const fresh = gmmBlobs(9, 1500).X
const data = computed(() => gmmBlobs(BLOB_SEED, n.value).X)
const sweep = useSweep(() => KS, (k) => {
  const m = em2(data.value, kmeansStart(data.value, k, 0, 1e-3, 4), 120, { reg: 1e-3 }).at(-1)! as Mix2
  return { m, fit: loglik2(data.value, m) / data.value.length, fresh: loglik2(fresh, m) / fresh.length }
}, [n])
const pts = (key: 'fit' | 'fresh') => KS.map((k, i) => [k, sweep.value[i]?.[key]] as [number, number | undefined])
  .filter((p) => p[1] !== undefined) as [number, number][]
const fitPts = computed(() => pts('fit'))
const freshPts = computed(() => pts('fresh'))
const best = computed(() => (freshPts.value.length === KS.length ? freshPts.value.reduce((a, b) => (b[1] > a[1] ? b : a))[0] : null))
const cur = computed(() => sweep.value[K.value - 1])
const color = computed(() => (best.value === null ? BLUE : K.value === best.value ? GREEN : RED))
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[{ points: fitPts, color: BLUE, width: 2.6 }, { points: freshPts, color: RED, width: 2.6 }]"
        :dots="[
          ...fitPts.map(([x, y]) => ({ x, y, color: BLUE, r: 4 })),
          ...freshPts.map(([x, y]) => ({ x, y, color: RED, r: 4 })),
          ...(best ? [{ x: best, y: freshPts[best - 1][1], color: GREEN, r: 11, hollow: true }] : []),
        ]"
        :vlines="[{ x: K, color: color, dash: '' }]"
        :labels="[{ x: 5.6, y: -2.62, text: 'fitted sample', color: BLUE }, { x: 5.6, y: -3.08, text: 'fresh sample', color: RED }]"
        :x-domain="[0.5, 8.5]" :y-domain="[-3.5, -2.55]" :x-ticks="KS" :y-ticks="[-3.4, -3.2, -3.0, -2.8, -2.6]"
        x-label="K" y-label="log-likelihood / point"
      />
      <Plane
        :X="data" :colors="MUTED" :size="2.2" :alpha="0.6" :domain="[-4, 4, -3.2, 3.2]"
        :ellipses="cur ? cur.m.mu.map((mu, k) => ({ mu, S: cur!.m.S[k], color: color, nsig: [1.6], width: 2 })) : []"
        :title="`K = ${K}`" :title-color="color"
        :caption="cur ? `fitted ${cur.fit.toFixed(3)} · fresh ${cur.fresh.toFixed(3)}` : 'fitting …'"
      />
    </div>
    <div class="note msg">The fitted score rises with every component; the fresh one peaks<span v-if="best"> at K = {{ best }}</span>.</div>
    <div class="controls">
      <Knob v-model="K" :min="1" :max="8" :step="1" :digits="0" label="components K" :color="color" />
      <Knob v-model="n" :min="60" :max="1200" :step="20" :digits="0" label="sample size n" />
      <span class="note">EM from a k-means start; the fresh sample has 1500 points.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.1fr 1fr; gap: 2rem; min-height: 0; }
.msg { text-align: center; }
</style>
