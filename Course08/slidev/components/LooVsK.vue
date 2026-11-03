<!-- loo_vs_k: what actually changes with K, measured. One order-M model, many
     resamples of N points: R_CV for each K (mean and spread over the
     resamples) against the risk of the model fitted on all N points. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { niceTicks } from '../lib/ticks'
import { cvPoly, freshSin, mean, mse, polyFit, sinData, std } from '../lib/c08'
import { BLUE, GOLD, GREEN, INK } from '../lib/theme'

const N = ref(40)
const M = ref(5)
const REPS = 40
const test = freshSin(2000, 99)
const res = computed(() => {
  const Ks = [2, 3, 5, 10, N.value]
  const truth: number[] = []
  const est: number[][] = Ks.map(() => [])
  for (let d = 0; d < REPS; d++) {
    const s = sinData(N.value, 500 + d)
    truth.push(mse(polyFit(s.x, s.t, M.value), test))
    Ks.forEach((K, i) => est[i].push(cvPoly(s, M.value, K, 7 + d)))
  }
  const T = mean(truth)
  return { T, rows: Ks.map((K, i) => ({ K, mu: mean(est[i]), sd: std(est[i]) })) }
})
// equally spaced positions for 2, 3, 5, 10, N
const X = [1, 2, 3, 4, 5]
// three times the true risk: the K = 2 bar may run off the top, as in print
const ymax = computed(() => 3 * res.value.T)
const yt = computed(() => niceTicks(0, ymax.value, 4))
const rowColor = [BLUE, INK, INK, GOLD, GREEN]
</script>

<template>
  <div class="wrap">
    <div class="note top">order {{ M }}, {{ N }} points, {{ REPS }} resamples</div>
    <div class="body">
      <LineChart
        :series="[
          { points: res.rows.map((r, i) => [X[i], r.mu] as [number, number]), color: GOLD, width: 2.6 },
          ...res.rows.map((r, i) => ({ points: [[X[i], Math.max(0, r.mu - r.sd)], [X[i], r.mu + r.sd]] as [number, number][], color: GOLD, width: 2 })),
        ]"
        :dots="res.rows.map((r, i) => ({ x: X[i], y: r.mu, color: GOLD, r: 5 }))"
        :hlines="[{ y: res.T, color: INK, dash: '6 4' }]"
        :labels="[
          { x: 2.2, y: res.T - ymax * 0.06, text: 'the risk of the model you actually ship', color: INK, size: 12 },
          ...['K = 2', '3', '5', '10', 'N'].map((t, i) => ({ x: X[i], y: -ymax * 0.07, text: t, color: INK, size: 12, anchor: 'middle' })),
        ]"
        :x-domain="[0.5, 5.5]" :y-domain="[0, ymax]" :x-ticks="[]" :y-ticks="yt"
        y-label="R_CV (mean ± sd)"
      />
      <div class="side">
        <Tex display formula="R_\text{CV} = \frac1K \sum_k (\text{score of fold } k)" />
        <p class="note">each fold is scored by the model fitted without it</p>
        <table class="plain">
          <tbody>
          <tr><th>K</th><th>bias of R_CV</th><th>spread</th></tr>
          <tr v-for="(r, i) in res.rows" :key="i">
            <td :style="{ color: rowColor[i] }">{{ i === 4 ? `N = ${r.K}` : r.K }}</td>
            <td>{{ r.mu - res.T >= 0 ? '+' : '−' }}{{ Math.abs(r.mu - res.T).toFixed(3) }}</td>
            <td>{{ r.sd.toFixed(3) }}</td>
          </tr>
        </tbody>
        </table>
        <p class="note">Small K fits on fewer points, so R_CV is pessimistic; K = N costs N fits. K = 10 is the usual balance.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="N" :min="15" :max="120" :step="5" :digits="0" label="points N" />
      <Knob v-model="M" :min="1" :max="9" :step="1" :digits="0" label="order M" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.3rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; border-left: 1px solid #cccfd2; padding-left: 1.6rem; font-size: 0.9rem; }
</style>
