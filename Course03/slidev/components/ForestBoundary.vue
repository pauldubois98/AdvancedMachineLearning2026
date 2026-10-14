<!-- forest_boundary: one tree, then M of them. The per-tree fields are kept,
     so the M slider is a running average rather than a refit. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { moons } from '../lib/data'
import { fitForest, forestAccuracy } from '../lib/forest'
import { dataDomain, equalise, logit, sampleField } from '../lib/plot'
import { GREEN, MUTED, RED } from '../lib/theme'

const M = ref(40)
const mf = ref('1')
const data = moons(260, 0.22, 0)
const RES = 100
const MAX = 120
// a fixed domain, because the fields are sampled once and reused
const domain = equalise(dataDomain(data.X, 0.5), 580, 460)

/** every tree's probability field, sampled once */
const cache = computed(() => {
  const f = fitForest(data.X, data.y, {
    nTrees: MAX, maxFeatures: Number(mf.value), seed: 0,
  })
  const grids = f.trees.map((t) =>
    Float32Array.from(sampleField((x, y) => t.predict([x, y])[1], domain, RES)),
  )
  return { f, grids }
})

function averaged(m: number): Float64Array {
  const { grids } = cache.value
  const k = Math.max(1, Math.min(m, grids.length))
  const out = new Float64Array(RES * RES)
  for (let t = 0; t < k; t++) {
    const g = grids[t]
    for (let i = 0; i < out.length; i++) out[i] += g[i]
  }
  for (let i = 0; i < out.length; i++) out[i] = logit(out[i] / k)
  return out
}
const one = computed(() => averaged(1))
const many = computed(() => averaged(Math.round(M.value)))
const acc = computed(() => ({
  one: forestAccuracy(cache.value.f, data.X, data.y, 1),
  many: forestAccuracy(cache.value.f, data.X, data.y, Math.round(M.value)),
}))
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <FieldPlot
        :X="data.X" :y="data.y" :grid="one" :grid-res="RES" :domain="domain" aspect="auto"
        :margins="false" :point-size="10" :field-alpha="0.65"
        title="1 tree" :title-color="RED"
      />
      <FieldPlot
        :X="data.X" :y="data.y" :grid="many" :grid-res="RES" :domain="domain" aspect="auto"
        :margins="false" :point-size="10" :field-alpha="0.65"
        :title="`${Math.round(M)} tree${Math.round(M) > 1 ? 's' : ''}, averaged`" :title-color="GREEN"
      />
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="M" :min="1" :max="120" :step="1" label="trees, M" :digits="0" :color="GREEN" />
        <Choice
          v-model="mf" label="max_features"
          :options="[{ value: '1', label: '1' }, { value: '2', label: 'both (bagging)' }]"
        />
        <Readout
          :items="[
            { label: 'one tree', value: (acc.one * 100).toFixed(1) + '%', color: RED },
            { label: 'the average', value: (acc.many * 100).toFixed(1) + '%', color: GREEN },
          ]"
        />
      </div>
      <p class="note">
        same bias, less and less variance: the staircase does not become a curve,
        a hundred staircases averaged do. Allowing both columns makes the trees
        more alike, and the averaging buys less.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 1.8rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child { min-width: 12rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
