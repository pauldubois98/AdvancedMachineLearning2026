<!-- forest_ntrees: more trees never over-fits, it just stops helping. The
     curve is measured by voting the first M trees of a fitted forest, which
     is exactly what "add a tree" means. -->
<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { moons } from '../lib/data'
import { split } from '../lib/databis'
import { fitForest, vote } from '../lib/forest'
import { GREEN, MUTED, RED } from '../lib/theme'

const M = ref(10)
const MAX = 200
const SEEDS = [0, 1, 2]
const curves = ref<[number, number][][]>([])
let cancelled = false

onMounted(() => {
  const data = moons(900, 0.32, 7)
  const sp = split(data, 0.55, 0)
  let s = 0
  const one = () => {
    if (cancelled) return
    const f = fitForest(sp.Xtr, sp.ytr, { nTrees: MAX, maxFeatures: 1, seed: SEEDS[s] })
    // running vote counts, so every M is read off one pass over the trees
    const counts = sp.Xte.map(() => [0, 0])
    const pts: [number, number][] = []
    for (let t = 0; t < MAX; t++) {
      for (let i = 0; i < sp.Xte.length; i++) counts[i][vote(f.trees[t].predict(sp.Xte[i]))]++
      let bad = 0
      for (let i = 0; i < sp.Xte.length; i++)
        if ((counts[i][1] > counts[i][0] ? 1 : 0) !== sp.yte[i]) bad++
      pts.push([t + 1, bad / sp.Xte.length])
    }
    curves.value = [...curves.value, pts]
    if (++s < SEEDS.length) setTimeout(one, 0)
  }
  setTimeout(one, 0)
})
onBeforeUnmount(() => (cancelled = true))

const mean = computed(() => {
  if (!curves.value.length) return []
  return curves.value[0].map((_, i) => {
    const v = curves.value.reduce((s, c) => s + c[i][1], 0) / curves.value.length
    return [i + 1, v] as [number, number]
  })
})
const at = computed(() => {
  const m = Math.round(M.value)
  return mean.value.length ? mean.value[m - 1][1] : 0
})
const floorErr = computed(() => (mean.value.length ? mean.value[MAX - 1][1] : 0))
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="[
        ...curves.map((c) => ({ points: c, color: MUTED, width: 1, opacity: 0.6 })),
        { points: mean, color: GREEN, width: 2.8 },
      ]"
      :hlines="[{ y: floorErr, color: MUTED, dash: '3,4' }]"
      :vlines="[{ x: M, color: '#1b1b1b', dash: '' }]"
      :dots="[{ x: M, y: at, color: '#1b1b1b', r: 5 }]"
      :x-domain="[1, 200]" :y-domain="[0.08, 0.3]" log-x
      :x-ticks="[1, 10, 100]" :y-ticks="[0.1, 0.2, 0.3]"
      x-label="number of trees" y-label="test error"
      title="a budget knob, not a capacity knob"
      :labels="[
        { x: 1.2, y: 0.29, text: 'grey: one seed each', color: MUTED, size: 11 },
        { x: 1.2, y: 0.275, text: 'green: their mean', color: GREEN, size: 11 },
      ]"
    />
    <div class="controls">
      <div class="knobs">
        <Knob v-model="M" :min="1" :max="200" :step="1" label="number of trees" :digits="0" :color="GREEN" />
        <Readout
          :items="[
            { label: 'test error here', value: (at * 100).toFixed(1) + '%' },
            { label: 'at 200 trees', value: (floorErr * 100).toFixed(1) + '%', color: GREEN },
            { label: 'still improving by', value: ((at - floorErr) * 100).toFixed(2) + ' pts', color: at - floorErr > 0.01 ? RED : GREEN },
          ]"
        />
      </div>
      <p class="note">
        The curve flattens, it never turns back up: a tree added to a forest can
        only move the average, never fit the training rows harder. Flat is fine,
        you just pay for it in time.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child { min-width: 13rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
