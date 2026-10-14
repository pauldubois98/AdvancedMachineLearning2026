<!-- tree_instability: change a tenth of the rows and get a different tree.
     Two bootstrap samples of the same 300 points, side by side; the slider
     walks them, and the toggle draws eight more boundaries on top. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { moons } from '../lib/data'
import { resample } from '../lib/databis'
import { fitTree } from '../lib/tree'
import { dataDomain, logit } from '../lib/plot'
import { GREEN, MUTED, RED } from '../lib/theme'

const which = ref(1)
const depth = ref(14)
const overlay = ref(false)
const data = moons(300, 0.22, 0)
const domain = dataDomain(data.X, 0.35)

const cap = () => (depth.value >= 14 ? Infinity : depth.value)
function treeOn(seed: number) {
  const d = resample(data, seed * 31)
  const t = fitTree(d.X, d.y, { maxDepth: cap(), seed: 0 })
  return { d, t, field: (x: number, y: number) => logit(t.predict([x, y])[1]) }
}
const left = computed(() => treeOn(which.value))
const right = computed(() => treeOn(which.value + 1))

/** eight more boundaries at once: the spread the forest is about to average */
const others = computed(() => {
  if (!overlay.value) return []
  const out: ((x: number, y: number) => number)[] = []
  for (let k = 3; k <= 10; k++) out.push(treeOn(k).field)
  return out
})

const agreement = computed(() => {
  let same = 0
  for (const x of data.X)
    same += (left.value.t.predict(x)[1] > 0.5) === (right.value.t.predict(x)[1] > 0.5) ? 1 : 0
  return same / data.X.length
})
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <FieldPlot
        :X="left.d.X" :y="left.d.y" :decision="left.field" :domain="domain" :margins="false"
        :point-size="9" :field-alpha="0.6" :extra-contours="others" :res="110"
        :title="`resample #${which}: ${left.t.nLeaves} leaves`"
      />
      <FieldPlot
        :X="right.d.X" :y="right.d.y" :decision="right.field" :domain="domain" :margins="false"
        :point-size="9" :field-alpha="0.6" :extra-contours="others" :res="110"
        :title="`resample #${which + 1}: ${right.t.nLeaves} leaves`"
      />
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="which" :min="1" :max="8" :step="1" label="resample pair" :digits="0" :color="RED" />
        <Knob v-model="depth" :min="2" :max="14" :step="1" label="max_depth" :digits="0" :color="GREEN" />
        <Toggle v-model="overlay" label="draw eight more boundaries" :color="MUTED" />
        <Readout
          :items="[{ label: 'the two trees agree on', value: (agreement * 100).toFixed(1) + '% of rows', color: agreement < 0.92 ? RED : GREEN }]"
        />
      </div>
      <p class="note">
        same 300 points, a different draw of them: the boundary moves a long way for
        a change of a few rows. A shallow tree twitches less, and fits less; that is
        the trade the next section buys its way out of.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child, .knobs > :nth-child(2) { min-width: 10rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
