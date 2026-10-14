<!-- tree_split: how the first question is chosen. Every midpoint of every
     feature is a candidate; the slider walks them, the curve scores them. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { treeToy } from '../lib/databis'
import { Criterion, impurityOf, scanFeature } from '../lib/tree'
import { BLUE, GOLD, GREEN, MUTED, RED } from '../lib/theme'

const threshold = ref(0.5)
const feature = ref('0')
const crit = ref<Criterion>('gini')
const data = treeToy(0, 240)

const scans = computed(() => [
  scanFeature(data.X, data.y, 0, crit.value),
  scanFeature(data.X, data.y, 1, crit.value),
])

const series = computed(() => [
  { points: scans.value[0].thresholds.map((t, i) => [t, scans.value[0].scores[i]] as [number, number]), color: BLUE, width: 2.4 },
  { points: scans.value[1].thresholds.map((t, i) => [t, scans.value[1].scores[i]] as [number, number]), color: GOLD, width: 2.4 },
])

/** the best candidate over both features, which is what CART would take */
const best = computed(() => {
  let out = { f: 0, t: 0.5, s: Infinity }
  scans.value.forEach((sc, f) =>
    sc.scores.forEach((s, i) => {
      if (s < out.s) out = { f, t: sc.thresholds[i], s }
    }),
  )
  return out
})

/** the score of the candidate the slider is sitting on */
const here = computed(() => {
  const f = Number(feature.value)
  const n = data.X.length
  const L = { c: [0, 0], n: 0 }
  const R = { c: [0, 0], n: 0 }
  for (let i = 0; i < n; i++) {
    const side = data.X[i][f] <= threshold.value ? L : R
    side.c[data.y[i]]++
    side.n++
  }
  const score =
    (L.n / n) * impurityOf(L.c, L.n, crit.value) + (R.n / n) * impurityOf(R.c, R.n, crit.value)
  const parent = impurityOf([n - data.y.reduce((s, v) => s + v, 0), data.y.reduce((s, v) => s + v, 0)], n, crit.value)
  return { score, drop: parent - score, L, R }
})

const cut = computed(() =>
  Number(feature.value) === 0
    ? [{ from: [threshold.value, 0] as [number, number], to: [threshold.value, 1] as [number, number], color: GREEN, width: 2.6 }]
    : [{ from: [0, threshold.value] as [number, number], to: [1, threshold.value] as [number, number], color: GREEN, width: 2.6 }],
)
function takeBest() {
  feature.value = String(best.value.f)
  threshold.value = best.value.t
}
const atBest = computed(() => Math.abs(here.value.score - best.value.s) < 1e-9)
</script>

<template>
  <div class="wrap">
    <FieldPlot
      :X="data.X" :y="data.y" :domain="[0, 1, 0, 1]" :segments="cut" :point-size="12"
      title="one candidate at a time"
    />
    <div class="right">
      <LineChart
        :series="series"
        :vlines="[{ x: threshold, color: GREEN, dash: '' }]"
        :dots="[{ x: best.t, y: best.s, color: GREEN, r: 5 }]"
        :x-domain="[0, 1]" :y-domain="[0, 0.66]"
        :x-ticks="[0, 0.25, 0.5, 0.75, 1]" :y-ticks="[0, 0.2, 0.4, 0.6]"
        x-label="threshold" y-label="weighted impurity after the split"
        title="greedy: take the biggest drop in impurity"
        :labels="[
          { x: 0.02, y: 0.635, text: 'split on x₁', color: BLUE, size: 12 },
          { x: 0.02, y: 0.585, text: 'split on x₂', color: GOLD, size: 12 },
          { x: best.t + 0.02, y: best.s - 0.04, text: 'best of all', color: GREEN, size: 12 },
        ]"
      />
      <div class="controls">
        <div class="row">
          <Choice
            v-model="feature" label="split on"
            :options="[{ value: '0', label: 'x₁', color: BLUE }, { value: '1', label: 'x₂', color: GOLD }]"
          />
          <Choice
            v-model="crit" label="impurity"
            :options="[
              { value: 'gini', label: 'Gini' },
              { value: 'entropy', label: 'entropy' },
              { value: 'misclass', label: 'misclass.' },
            ]"
          />
          <button class="take" @click="takeBest">take the best</button>
        </div>
        <Knob v-model="threshold" :min="0.02" :max="0.98" label="threshold" :digits="2" :color="GREEN" />
        <Readout
          :items="[
            { label: 'rows left / right', value: `${here.L.n} / ${here.R.n}` },
            { label: 'impurity after', value: here.score.toFixed(3) },
            { label: 'drop', value: here.drop.toFixed(3), color: here.drop > 0 ? GREEN : RED },
            { label: '', value: atBest ? 'this is the winning split' : '', color: GREEN },
          ]"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 0.85fr 1.15fr; gap: 1.4rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.row { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.take {
  border: 1px solid #00ab0e; color: #00ab0e; background: white;
  border-radius: 0.3rem; padding: 0.16rem 0.5rem; font-size: 0.8rem; cursor: pointer;
}
.take:hover { background: #f0fbf1; }
</style>
