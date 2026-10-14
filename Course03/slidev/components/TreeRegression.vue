<!-- tree_regression: a leaf is a constant, so the fit is flat inside every box.
     The depth slider turns two steps into a staircase into memorisation. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sine1d } from '../lib/databis'
import { fitTreeReg } from '../lib/tree'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const depth = ref(3)
const noise = ref(0.18)
const n = ref(80)

const data = computed(() => sine1d(Math.round(n.value), noise.value, 0))
const tree = computed(() =>
  fitTreeReg(data.value.X, data.value.y, { maxDepth: depth.value, seed: 0 }),
)

const grid = computed(() => {
  const pts: [number, number][] = []
  for (let i = 0; i <= 600; i++) {
    const x = i / 600
    pts.push([x, tree.value.predict([x])[0]])
  }
  return pts
})
const truth = computed(() => {
  const pts: [number, number][] = []
  for (let i = 0; i <= 200; i++) pts.push([i / 200, Math.sin(2 * Math.PI * (i / 200))])
  return pts
})
const trainMse = computed(() => {
  const d = data.value
  let s = 0
  for (let i = 0; i < d.X.length; i++) s += (tree.value.predict(d.X[i])[0] - d.y[i]) ** 2
  return s / d.X.length
})
/** error against the noiseless curve: the part that is not memorised noise */
const truthMse = computed(() => {
  let s = 0
  for (let i = 0; i <= 400; i++) {
    const x = i / 400
    s += (tree.value.predict([x])[0] - Math.sin(2 * Math.PI * x)) ** 2
  }
  return s / 401
})
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="[
        { points: truth, color: MUTED, width: 1.6, dash: '6,4' },
        { points: grid, color: RED, width: 2.4, step: false },
      ]"
      :dots="data.x.map((x, i) => ({ x, y: data.y[i], color: BLUE, r: 3 }))"
      :x-domain="[0, 1]" :y-domain="[-2, 2]"
      :x-ticks="[0, 0.5, 1]" :y-ticks="[-1, 0, 1]"
      x-label="x" y-label="y"
      :title="`max_depth = ${depth}, ${tree.nLeaves} constant pieces`"
    />
    <div class="controls">
      <div class="knobs">
        <Knob v-model="depth" :min="1" :max="14" :step="1" label="max_depth" :digits="0" :color="RED" />
        <Knob v-model="noise" :min="0" :max="0.6" label="noise" :digits="2" :color="MUTED" />
        <Knob v-model="n" :min="20" :max="200" :step="1" label="rows" :digits="0" :color="BLUE" />
      </div>
      <Readout
        :items="[
          { label: 'leaves', value: String(tree.nLeaves) },
          { label: 'error on the training rows', value: trainMse.toFixed(4), color: BLUE },
          { label: 'error against the true curve', value: truthMse.toFixed(4), color: truthMse > 0.05 ? RED : GREEN },
        ]"
      />
      <p class="note">
        The training error falls all the way to zero; the error against the dashed
        curve turns around, because past some depth the staircase is fitting noise.
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
