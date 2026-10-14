<!-- cat_ordered_ts: what "the leak is gone" means, measured. The category is
     independent of the label by construction, so anything the encoded feature
     seems to know is leakage and nothing else. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { catDemo, correlation, encodingRate, greedyTs, orderedTs } from '../lib/gbm'
import { GREEN, INK, MUTED, RED } from '../lib/theme'

const levels = ref(200)
const a = ref(1)
const n = 600

const data = computed(() => catDemo(n, Math.round(levels.value), 5))
const greedy = computed(() => {
  const d = data.value
  const map = greedyTs(d.cat, d.y, Math.round(levels.value))
  return d.cat.map((c) => map[c])
})
const ordered = computed(() => {
  const d = data.value
  return orderedTs(d.cat, d.y, Math.round(levels.value), a.value, 0).enc
})
const fresh = computed(() => {
  const d = data.value
  const map = greedyTs(d.cat, d.y, Math.round(levels.value))
  return d.catTe.map((c) => map[c])
})
const base = computed(() => data.value.y.reduce((s, v) => s + v, 0) / n)

function bars(enc: number[], y: number[], color: string) {
  return encodingRate(enc, y).map((b) => ({ x: b.at, y: b.rate, w: 0.13, color, alpha: 0.85 }))
}
const panels = computed(() => [
  { bars: bars(greedy.value, data.value.y, RED), r: correlation(greedy.value, data.value.y),
    title: 'GREEDY, on the training rows', note: 'each row helped build its own encoding', color: RED },
  { bars: bars(ordered.value, data.value.y, GREEN), r: correlation(ordered.value, data.value.y),
    title: 'ORDERED, on the same rows', note: 'no row is in its own encoding any more', color: GREEN },
  { bars: bars(fresh.value, data.value.yTe, MUTED), r: correlation(fresh.value, data.value.yTe),
    title: 'either one, on fresh rows', note: 'what a leak-free feature always looked like', color: MUTED },
])
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        v-for="(p, i) in panels" :key="i"
        :series="[]" :bars="p.bars"
        :hlines="[{ y: base, color: INK, dash: '4,4' }]"
        :x-domain="[-0.09, 1.09]" :y-domain="[0, 1.15]"
        :x-ticks="[0, 0.5, 1]" :y-ticks="i === 0 ? [0, 0.5, 1] : []"
        x-label="value of the encoded feature"
        :y-label="i === 0 ? 'share of y = 1 among those rows' : ''"
        :title="`${p.title}; corr(encoding, y) = ${p.r >= 0 ? '+' : ''}${p.r.toFixed(2)}`"
        :title-color="p.color"
        :labels="[{ x: 0.5, y: 1.06, text: p.note, color: '#1b1b1b', size: 11, anchor: 'middle' }]"
      />
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="levels" :min="5" :max="300" :step="1" label="categories" :digits="0" />
        <Knob v-model="a" :min="0.2" :max="20" log label="prior weight a" :color="GREEN" />
        <Readout
          :items="[
            { label: 'rows per category', value: (n / Math.round(levels)).toFixed(1) },
            { label: 'base rate', value: base.toFixed(2) },
          ]"
        />
      </div>
      <p class="note">
        read one bar: of the rows whose encoding lands there, what share actually
        bought? A feature that knows nothing keeps every bar on the dashed base rate.
        The leak gets worse the rarer the category: drop the slider to 5 categories,
        with 120 rows each, and even the greedy encoding has almost nothing left to leak.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 1.8rem; align-items: center; flex-wrap: wrap; }
.knobs > :nth-child(-n+2) { min-width: 11rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
