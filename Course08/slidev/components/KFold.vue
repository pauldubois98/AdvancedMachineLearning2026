<!-- kfold_idea: one random 70/30 split is a noisy judge (left, thin gold:
     one curve per split, and which order each one picks). K-fold
     cross-validation (right) validates every point exactly once and averages
     the K scores: the black curve. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmin, cvPoly, mse, permutation, pick, polyFit, sinData } from '../lib/c08'
import { Rng } from '../lib/rng'
import { BLUE, GOLD, GREEN, INK, MUTED } from '../lib/theme'

const data = sinData(60, 2)
const MS = Array.from({ length: 10 }, (_, m) => m)
const nSplits = ref(25)
const K = ref(5)
const round = ref(1)
const splits = computed(() => {
  const rng = new Rng(0)
  return Array.from({ length: nSplits.value }, () => {
    const idx = permutation(60, rng)
    const tr = pick(data, idx.slice(0, 42))
    const va = pick(data, idx.slice(42))
    return MS.map((m) => mse(polyFit(tr.x, tr.t, m), va))
  })
})
const picks = computed(() => {
  const c = new Map<number, number>()
  for (const e of splits.value) { const m = argmin(e); c.set(m, (c.get(m) ?? 0) + 1) }
  return [...c.entries()].sort((a, b) => a[0] - b[0])
})
const cv = computed(() => MS.map((m) => [m, cvPoly(data, m, K.value, 3)] as [number, number]))
const cvBest = computed(() => argmin(cv.value.map((p) => p[1])))
const r = computed(() => Math.min(round.value, K.value))
</script>

<template>
  <div class="wrap">
    <div class="body">
      <div class="left">
        <LineChart
          :series="[
            ...splits.map((e) => ({ points: MS.map((m) => [m, Math.min(e[m], 0.6)] as [number, number]), color: GOLD, width: 1, opacity: 0.45 })),
            { points: cv, color: INK, width: 3 },
          ]"
          :dots="[{ x: cvBest, y: cv[cvBest][1], color: GREEN, r: 9, hollow: true }]"
          :x-domain="[-0.3, 9.3]" :y-domain="[0, 0.45]" :x-ticks="[0, 2, 4, 6, 8]" :y-ticks="[0, 0.1, 0.2, 0.3, 0.4]"
          x-label="M" y-label="validation error" :title="`${nSplits} random 70/30 splits, and ${K}-fold CV (black)`" :unit-height="260"
        />
        <p class="msg">One split is a noisy judge. The splits pick
          <span v-for="([m, c], i) in picks" :key="m">{{ i ? ', ' : '' }}M = {{ m }} ({{ c }}×)</span>.
          K-fold CV picks <b :style="{ color: GREEN }">M = {{ cvBest }}</b>.</p>
      </div>
      <div class="right">
        <div class="legend"><span class="sq" :style="{ background: BLUE }" /> train <span class="sq" :style="{ background: GOLD }" /> validate</div>
        <div class="rounds">
          <div v-for="k in K" :key="k" class="row" :class="{ on: k === r }">
            <span class="lab">round {{ k }}</span>
            <span v-for="j in K" :key="j" class="cell" :style="{ background: j === k ? GOLD : BLUE }" />
          </div>
        </div>
        <p class="avg" :style="{ color: GREEN }">Average the K scores.</p>
      </div>
    </div>
    <div class="note msg">Every point is validated exactly once, so the answer no longer rests on one lucky split.</div>
    <div class="controls">
      <Knob v-model="K" :min="2" :max="10" :step="1" :digits="0" label="folds K" :color="GREEN" />
      <Knob v-model="round" :min="1" :max="10" :step="1" :digits="0" label="round" />
      <Knob v-model="nSplits" :min="1" :max="60" :step="1" :digits="0" label="random splits" :color="GOLD" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.3rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; min-height: 0; }
.left { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.msg { text-align: center; font-size: 0.8rem; color: #6b46c1; margin: 0.2rem 0; }
.right { align-self: center; border-left: 1px solid #cccfd2; padding-left: 1.5rem; }
.legend { display: flex; gap: 0.5rem; align-items: center; font-size: 0.85rem; margin-bottom: 0.5rem; }
.sq { display: inline-block; width: 1.2rem; height: 0.8rem; margin-left: 0.6rem; }
.rounds { display: grid; gap: 0.35rem; }
.row { display: flex; gap: 3px; align-items: center; opacity: 0.45; transition: opacity 0.15s; }
.row.on { opacity: 1; }
.lab { width: 4.5rem; color: #9aa0a6; font-size: 0.78rem; }
.cell { flex: 1; height: 1.25rem; }
.avg { text-align: center; margin-top: 0.6rem; }
</style>
