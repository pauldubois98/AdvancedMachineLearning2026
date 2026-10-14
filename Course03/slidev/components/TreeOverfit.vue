<!-- tree_overfit: an unpruned tree always reaches zero training error. The two
     curves are refitted whenever the data knobs move; the slider on max_depth
     walks along them. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { split, treeToy } from '../lib/databis'
import { accuracy, fitTree } from '../lib/tree'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const depth = ref(6)
const flip = ref(0.06)
const minLeaf = ref(1)
const DEPTHS = Array.from({ length: 20 }, (_, i) => i + 1)

const curves = computed(() => {
  const d = treeToy(0, 700, flip.value)
  const sp = split(d, 0.6, 0)
  const tr: [number, number][] = []
  const te: [number, number][] = []
  for (const k of DEPTHS) {
    const t = fitTree(sp.Xtr, sp.ytr, { maxDepth: k, minSamplesLeaf: minLeaf.value, seed: 0 })
    tr.push([k, 1 - accuracy(t, sp.Xtr, sp.ytr)])
    te.push([k, 1 - accuracy(t, sp.Xte, sp.yte)])
  }
  const best = te.reduce((a, b) => (b[1] < a[1] ? b : a))
  return { tr, te, best }
})
const at = computed(() => ({
  train: curves.value.tr[depth.value - 1][1],
  test: curves.value.te[depth.value - 1][1],
}))
const gap = computed(() => at.value.test - at.value.train)
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="[
        { points: curves.tr, color: BLUE, width: 2.4 },
        { points: curves.te, color: RED, width: 2.4 },
      ]"
      :vlines="[{ x: depth, color: MUTED, dash: '' }]"
      :dots="[
        { x: depth, y: at.train, color: BLUE, r: 5 },
        { x: depth, y: at.test, color: RED, r: 5 },
        { x: curves.best[0], y: curves.best[1], color: GREEN, r: 6, hollow: true },
      ]"
      :x-domain="[1, 20]" :y-domain="[0, 0.45]"
      :x-ticks="[1, 5, 10, 15, 20]" :y-ticks="[0, 0.1, 0.2, 0.3, 0.4]"
      x-label="max_depth" y-label="error rate"
      title="an unpruned tree always reaches zero training error"
      :labels="[
        { x: 13, y: 0.42, text: 'training error', color: BLUE, size: 12 },
        { x: 13, y: 0.38, text: 'test error', color: RED, size: 12 },
        { x: curves.best[0] + 0.3, y: curves.best[1] - 0.045, text: 'best depth', color: GREEN, size: 12 },
      ]"
    />
    <div class="controls">
      <div class="knobs">
        <Knob v-model="depth" :min="1" :max="20" :step="1" label="max_depth" :digits="0" />
        <Knob v-model="flip" :min="0" :max="0.3" label="label noise" :digits="2" :color="MUTED" />
        <Knob v-model="minLeaf" :min="1" :max="40" :step="1" label="min_samples_leaf" :digits="0" :color="GREEN" />
      </div>
      <Readout
        :items="[
          { label: 'train error', value: (at.train * 100).toFixed(1) + '%', color: BLUE },
          { label: 'test error', value: (at.test * 100).toFixed(1) + '%', color: RED },
          { label: 'gap', value: (gap * 100).toFixed(1) + ' pts', color: gap > 0.1 ? RED : GREEN },
          { label: 'best depth here', value: String(curves.best[0]), color: GREEN },
        ]"
      />
      <p class="note">
        more label noise pushes the best depth left: the noisier the labels, the
        less of the data is worth fitting. min_samples_leaf prunes from the other end.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0 1.6rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
