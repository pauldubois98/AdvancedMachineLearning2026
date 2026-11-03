<!-- holdout_idea: split D at random into three parts, fit every order on
     D_train, choose with D_val, report on D_test. The sliders move the cuts;
     the five steps are carried out live on 60 noisy sine points. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmin, freshSin, mse, permutation, pick, polyFit, sinData } from '../lib/c08'
import { Rng } from '../lib/rng'
import { BLUE, GOLD, GREEN, MUTED, RED } from '../lib/theme'

const N = 60
const trainPct = ref(60)
const valPct = ref(20)
const seed = ref(1)
const data = sinData(N, 2)
const truthTest = freshSin(3000, 99)
const testPct = computed(() => Math.max(0, 100 - trainPct.value - valPct.value))
const parts = computed(() => {
  const idx = permutation(N, new Rng(seed.value))
  const a = Math.round((trainPct.value / 100) * N)
  const b = Math.min(N, a + Math.round((valPct.value / 100) * N))
  return { tr: pick(data, idx.slice(0, a)), va: pick(data, idx.slice(a, b)), te: pick(data, idx.slice(b)) }
})
const MS = Array.from({ length: 10 }, (_, m) => m)
const ok = computed(() => parts.value.tr.x.length >= 3 && parts.value.va.x.length >= 2)
const scores = computed(() => MS.map((m) => {
  const p = parts.value
  const w = polyFit(p.tr.x, p.tr.t, Math.min(m, p.tr.x.length - 1))
  return { m, val: mse(w, p.va), test: p.te.x.length ? mse(w, p.te) : NaN, truth: mse(w, truthTest) }
}))
const chosen = computed(() => argmin(scores.value.map((s) => s.val)))
</script>

<template>
  <div class="wrap">
    <div class="note top">Never score on the data you fitted on</div>
    <div class="bar">
      <span :style="{ background: BLUE, flex: trainPct }"><Tex formula="\mathcal D_\text{train}" /> {{ parts.tr.x.length }}</span>
      <span :style="{ background: GOLD, flex: valPct }"><Tex formula="\mathcal D_\text{val}" /> {{ parts.va.x.length }}</span>
      <span v-if="testPct > 0" :style="{ background: RED, flex: testPct }"><Tex formula="\mathcal D_\text{test}" /> {{ parts.te.x.length }}</span>
    </div>
    <div class="body">
      <ol class="steps">
        <li :style="{ '--c': BLUE }">Split <Tex formula="\mathcal D" /> at random into three parts</li>
        <li :style="{ '--c': BLUE }">Fit every candidate (orders 0 to 9) on <Tex formula="\mathcal D_\text{train}" /></li>
        <li :style="{ '--c': GOLD }">Score each on <Tex formula="\mathcal D_\text{val}" /></li>
        <li :style="{ '--c': GREEN }">Keep the best validation score: <b v-if="ok" :style="{ color: GREEN }">M = {{ chosen }}</b></li>
        <li :style="{ '--c': RED }">Report its error on <Tex formula="\mathcal D_\text{test}" />:
          <b v-if="ok && testPct > 0" :style="{ color: RED }">{{ scores[chosen].test.toFixed(3) }}</b>
          <b v-else :style="{ color: RED }">no test set left!</b>
        </li>
      </ol>
      <LineChart
        v-if="ok"
        :series="[{ points: scores.map((s) => [s.m, s.val] as [number, number]), color: GOLD, width: 2.4 }, { points: scores.map((s) => [s.m, s.truth] as [number, number]), color: MUTED, width: 1.6, dash: '4 3' }]"
        :dots="[{ x: chosen, y: scores[chosen].val, color: GREEN, r: 9, hollow: true }]"
        :labels="[{ x: 0.2, y: 0.47, text: 'validation error', color: GOLD, size: 12 }, { x: 0.2, y: 0.42, text: 'true risk (unknown)', color: MUTED, size: 12 }]"
        :x-domain="[-0.3, 9.3]" :y-domain="[0, 0.5]" :x-ticks="[0, 3, 6, 9]" :y-ticks="[0, 0.25, 0.5]" x-label="M" :unit-height="260"
      />
    </div>
    <div class="cards">
      <div class="box gold">Validation: selection metric</div>
      <div class="box red">Test: reporting metric</div>
    </div>
    <div class="controls">
      <Knob v-model="trainPct" :min="10" :max="90" :step="5" :digits="0" label="train %" :color="BLUE" />
      <Knob v-model="valPct" :min="5" :max="60" :step="5" :digits="0" label="validation %" :color="GOLD" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" :digits="0" label="shuffle" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.bar { display: flex; gap: 3px; }
.bar span { color: white; text-align: center; padding: 0.4rem 0; font-size: 0.85rem; overflow: hidden; white-space: nowrap; }
.body { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; min-height: 0; }
.steps { font-size: 0.92rem; line-height: 1.9; margin: 0; align-self: center; }
.steps li::marker { color: var(--c); font-weight: 700; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; }
.cards .box { padding: 0.4rem; }
</style>
