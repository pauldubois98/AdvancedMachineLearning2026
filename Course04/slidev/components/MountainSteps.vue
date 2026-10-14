<!-- mountain_steps: take a peak, flatten it, repeat. The round slider walks
     the four pictures of the printed figure, and sigma and beta decide how
     many peaks are worth taking at all. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { gridOver, mountainData } from '../lib/data4'
import { mountainField, mountainPeaks, surface } from '../lib/mountain'
import { BLUE, GOLD, GREEN, INK, RED } from '../lib/theme'

const sigma = ref(0.45)
const beta = ref(0.75)
const round = ref(0)
const ratio = ref(0.5)

const X = mountainData()
const grid = computed(() => gridOver(X, 0.22, 0.9))
const M0 = computed(() => mountainField(grid.value.V, X, sigma.value))
const vmax = computed(() => Math.max(...Array.from(M0.value)))
const run = computed(() => mountainPeaks(grid.value.V, M0.value, 5, beta.value))
const taken = computed(() => run.value.steps.slice(0, round.value).map((s) => ({ peak: s.peak, height: s.height })))
const field = computed(() => ({
  f: surface(X, sigma.value, taken.value, beta.value),
  vmax: vmax.value,
  levels: 14,
}))
/** the rule that stops the method: a peak below `ratio` of the first is noise */
const kept = computed(() => run.value.steps.filter((s) => s.height >= ratio.value * vmax.value).length)
const nextPeak = computed(() => run.value.steps[round.value])
const dom: [number, number, number, number] = [-3.4, 3.3, -2.6, 3.2]
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :field="field" :point-size="1.8" :point-alpha="0.4" :domain="dom"
      :colors="X.map(() => INK)"
      :crosses="run.steps.slice(0, round + 1).map((s, i) => ({
        x: s.peak[0], y: s.peak[1], color: i === round ? RED : GOLD, size: 6.5,
      }))"
      :title="round === 0 ? 'no peak subtracted' : `${round} peak${round > 1 ? 's' : ''} subtracted`"
      :title-color="BLUE"
    />
    <div class="right">
      <LineChart
        :series="[{ points: run.steps.map((s, i) => [i + 1, s.height] as [number, number]), color: BLUE, width: 2.2 }]"
        :bars="run.steps.map((s, i) => ({ x: i + 1, y: s.height, w: 0.5, color: i < kept ? GREEN : '#cccfd2', alpha: 0.75, label: s.height.toFixed(1) }))"
        :hlines="[{ y: ratio * vmax, color: RED, dash: '6,4' }]"
        :dots="[{ x: round + 1, y: nextPeak ? nextPeak.height : 0, color: RED, r: 5 }]"
        :x-domain="[0.4, 5.6]" :y-domain="[0, vmax * 1.12]"
        :x-ticks="[1, 2, 3, 4, 5]"
        x-label="round" y-label="height of the peak taken"
        title="how tall each summit was" :title-color="BLUE"
        :labels="[{ x: 4.4, y: ratio * vmax * 1.06, text: 'stop below here', color: RED, size: 11 }]"
      />
      <div class="controls">
        <Knob v-model="round" :min="0" :max="4" :step="1" label="peaks subtracted" :digits="0" :color="RED" />
        <Knob v-model="sigma" :min="0.2" :max="1" label="σ" :color="BLUE" />
        <Knob v-model="beta" :min="0.3" :max="2" label="β" :color="GREEN" />
        <Knob v-model="ratio" :min="0.1" :max="0.9" label="stop below this fraction" :color="RED" />
        <Readout
          :items="[
            { label: 'clusters the rule keeps', value: String(kept), color: GREEN },
            { label: 'next summit', value: nextPeak ? nextPeak.height.toFixed(1) : 'none', color: RED },
          ]"
        />
      </div>
      <p class="note">The number of clusters is not asked for: it is where the
        summits stop being tall.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1.15fr; gap: 1.4rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; min-height: 0; }
.controls { display: grid; grid-template-columns: 1fr 1fr; gap: 0.3rem 1rem; }
.controls > :deep(.readout) { grid-column: 1 / -1; }
</style>
