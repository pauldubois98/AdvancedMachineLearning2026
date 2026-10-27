<!-- init_compare: five clusters, R random starts, a k-means start and a
     symmetric one. The gap to the best fit found, on a log scale, so both the
     symmetric start (hundreds below) and the near-ties show. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { em2, FIVE_BLOBS, kmeansStart, sampleMix2, start2, type Mix2 } from '../lib/gmm'
import { fmt } from '../lib/charts'
import { GOLD, GREEN, INK, RED } from '../lib/theme'

const K = 5
const T = 60
const { X } = sampleMix2(FIVE_BLOBS, 420, 2)
const R = ref(5)
const offset = ref(0)
const km = em2(X, kmeansStart(X, K, 0), T).map((h) => h.ll)
const mean: [number, number] = [X.reduce((a, x) => a + x[0], 0) / X.length, X.reduce((a, x) => a + x[1], 0) / X.length]
const C0 = start2(X, 1, 0).S[0]
const flat: Mix2 = { p: new Array(K).fill(1 / K), mu: new Array(K).fill(0).map((_, k) => [mean[0] + 1e-3 * k, mean[1]]), S: new Array(K).fill(0).map(() => [C0[0] / 0.6, C0[1] / 0.6, C0[2] / 0.6]) }
const sym = em2(X, flat, T).map((h) => h.ll)
const cache = new Map<number, number[]>()
const randRun = (s: number) => { if (!cache.has(s)) cache.set(s, em2(X, start2(X, K, 11 + 37 * s), T).map((h) => h.ll)); return cache.get(s)! }
const rand = computed(() => Array.from({ length: R.value }, (_, i) => randRun(offset.value + i)))
const best = computed(() => Math.max(km[T], sym[T], ...rand.value.map((r) => r[T])))
const FLOOR = 1e-3
const gap = (tr: number[]) => tr.map((v, i) => [i, Math.max(best.value - v, FLOOR)] as [number, number])
const finals = computed(() => rand.value.map((r) => r[T]))
const nBest = computed(() => finals.value.filter((v) => v > Math.max(...finals.value) - 0.5).length)
</script>

<template>
  <div class="wrap">
    <div class="note top">{{ R }} random start{{ R > 1 ? 's' : '' }}, a k-means start and a symmetric one: 5 clusters</div>
    <div class="body">
      <LineChart
        log-y
        :series="[
          ...rand.map((r) => ({ points: gap(r), color: GOLD, width: 1.4, opacity: 0.85 })),
          { points: gap(km), color: GREEN, width: 2.6 },
          { points: gap(sym), color: RED, width: 2.6 },
        ]"
        :x-domain="[0, T]" :y-domain="[FLOOR * 0.7, 3000]" x-label="pass t" y-label="ℓ* − ℓ_obs(θᵗ)"
        :x-ticks="[0, 10, 20, 30, 40, 50, 60]" :y-ticks="[1e-3, 0.01, 0.1, 1, 10, 100, 1000]"
      />
      <div class="side">
        <div class="h">Where each start lands</div>
        <table class="plain">
          <tr><td :style="{ color: GREEN, fontWeight: 700 }">k-means start</td><td class="num">{{ fmt(km[T], 1) }}</td></tr>
          <tr><td :style="{ color: GOLD, fontWeight: 700 }">random, best of {{ R }}</td><td class="num">{{ fmt(Math.max(...finals), 1) }}</td></tr>
          <tr><td :style="{ color: GOLD, fontWeight: 700 }">random, worst of {{ R }}</td><td class="num">{{ fmt(Math.min(...finals), 1) }}</td></tr>
          <tr><td :style="{ color: RED, fontWeight: 700 }">all components equal</td><td class="num">{{ fmt(sym[T], 1) }}</td></tr>
        </table>
        <p class="note">{{ nBest }} of the {{ R }} random starts reach the best random value; the symmetric start is stuck: one Gaussian, five times over. ℓ*: the best fit found.</p>
        <p :style="{ color: GREEN }">Rule of thumb: k-means to start, several random restarts to check, keep the best ℓ<sub>obs</sub>.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="R" :min="1" :max="12" :step="1" label="random starts" :digits="0" :color="GOLD" />
      <Knob v-model="offset" :min="0" :max="40" :step="1" label="first seed" :digits="0" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; font-size: 0.85rem; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
</style>
