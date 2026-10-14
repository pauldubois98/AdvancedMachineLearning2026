<!-- boosting_overfit: harmless in a forest, a real risk in boosting. Both
     curves are measured on held-out rows and averaged over three draws of the
     data, because a single split's test error is too jumpy to read a turning
     point off. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { split, treeToy } from '../lib/databis'
import { errorRate, fitBooster } from '../lib/boost'
import { fitForest, vote } from '../lib/forest'
import { GOLD, GREEN, MUTED, RED } from '../lib/theme'

const rounds = ref(40)
const eta = ref(0.05)
const depth = ref(3)
const flip = ref(0.2)
const MAX = 200
const SEEDS = [0, 1, 2]

const curves = computed(() => {
  const train = new Array(MAX).fill(0)
  const test = new Array(MAX).fill(0)
  const forest = new Array(MAX).fill(0)
  for (const s of SEEDS) {
    const d = treeToy(s, 400, flip.value)
    const sp = split(d, 0.5, s)
    const b = fitBooster(sp.Xtr, sp.ytr, {
      nTrees: MAX, eta: eta.value, maxDepth: Math.round(depth.value), loss: 'log', seed: s,
    })
    b.stages(sp.Xtr).slice(1).forEach((F, m) => (train[m] += errorRate(F, sp.ytr) / SEEDS.length))
    b.stages(sp.Xte).slice(1).forEach((F, m) => (test[m] += errorRate(F, sp.yte) / SEEDS.length))
    // the forest on the same rows: its test error flattens, it never turns up
    const f = fitForest(sp.Xtr, sp.ytr, { nTrees: MAX, maxFeatures: 1, seed: s })
    const counts = sp.Xte.map(() => [0, 0])
    for (let t = 0; t < MAX; t++) {
      for (let i = 0; i < sp.Xte.length; i++) counts[i][vote(f.trees[t].predict(sp.Xte[i]))]++
      let bad = 0
      for (let i = 0; i < sp.Xte.length; i++)
        if ((counts[i][1] > counts[i][0] ? 1 : 0) !== sp.yte[i]) bad++
      forest[t] += bad / sp.Xte.length / SEEDS.length
    }
  }
  const pts = (a: number[]) => a.map((v, i) => [i + 1, v] as [number, number])
  return { train: pts(train), test: pts(test), forest: pts(forest), raw: { train, test } }
})
const best = computed(() => curves.value.test.reduce((a, b) => (b[1] < a[1] ? b : a)))
const at = computed(() => {
  const m = Math.round(rounds.value)
  return { train: curves.value.raw.train[m - 1], test: curves.value.raw.test[m - 1] }
})
const overshoot = computed(() => at.value.test - best.value[1])
const yDomain = computed<[number, number]>(() => {
  const hi = Math.max(...curves.value.raw.test, ...curves.value.forest.map((p) => p[1]))
  return [0, hi * 1.25]
})
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="[
        { points: curves.train, color: GOLD, width: 1.5, dash: '5,4' },
        { points: curves.test, color: GOLD, width: 2.4 },
        { points: curves.forest, color: GREEN, width: 2.2 },
      ]"
      :vlines="[{ x: rounds, color: '#1b1b1b', dash: '' }]"
      :dots="[
        { x: rounds, y: at.test, color: '#1b1b1b', r: 5 },
        { x: best[0], y: best[1], color: RED, r: 7, hollow: true },
      ]"
      :x-domain="[1, MAX]" :y-domain="yDomain" log-x
      :x-ticks="[1, 10, 100]" :y-ticks="[0, 0.1, 0.2, 0.3]"
      x-label="number of trees" y-label="error rate"
      title="adding trees to a forest is free; adding them to a boosting run is not"
      :labels="[
        { x: 1.15, y: yDomain[1] * 0.96, text: 'boosting, test', color: GOLD, size: 11.5 },
        { x: 1.15, y: yDomain[1] * 0.89, text: 'boosting, train', color: GOLD, size: 11.5 },
        { x: 1.15, y: yDomain[1] * 0.82, text: 'forest, test', color: GREEN, size: 11.5 },
        { x: best[0] * 1.2, y: best[1] - yDomain[1] * 0.08, text: 'early stopping goes here', color: RED, size: 11.5 },
      ]"
    />
    <div class="controls">
      <div class="knobs">
        <Knob v-model="rounds" :min="1" :max="MAX" :step="1" label="rounds" :digits="0" />
        <Knob v-model="eta" :min="0.02" :max="1" log label="η" :color="GOLD" />
        <Knob v-model="depth" :min="1" :max="6" :step="1" label="depth" :digits="0" :color="MUTED" />
        <Knob v-model="flip" :min="0.05" :max="0.35" label="label noise" :digits="2" :color="MUTED" />
      </div>
      <Readout
        :items="[
          { label: 'train', value: (at.train * 100).toFixed(1) + '%', color: GOLD },
          { label: 'test', value: (at.test * 100).toFixed(1) + '%', color: RED },
          { label: 'best at', value: `${best[0]} rounds`, color: GREEN },
          { label: 'paid for carrying on', value: (overshoot * 100).toFixed(1) + ' pts', color: overshoot > 0.01 ? RED : GREEN },
        ]"
      />
      <p class="note">
        the training error keeps falling whatever you do, and reaches zero. The test
        curve has a bottom, and climbs back out of it. Raise η or the depth and that
        bottom arrives sooner: every knob that makes a round count for more also
        makes over-fitting arrive earlier.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.35rem; }
.knobs { display: flex; gap: 1.4rem; align-items: center; flex-wrap: wrap; }
.knobs > * { min-width: 9.5rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
