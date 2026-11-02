<!-- lgbm_bins: step 1 of histogram split finding. Bin the feature once, up
     front, and keep three numbers per bin; everything after that reads the
     bins, never the rows. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { binFeature, splitDemo } from '../lib/gbm'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const nBins = ref(8)
const demo = splitDemo()
const xs = demo.X.map((r) => r[0])

const bins = computed(() => binFeature(xs, demo.g, demo.h, Math.round(nBins.value)))
const bars = computed(() => {
  const b = bins.value
  const w = b.edges[1] - b.edges[0]
  return b.sumG.map((g, i) => ({
    x: (b.edges[i] + b.edges[i + 1]) / 2,
    y: g,
    w: w * 0.84,
    color: g < 0 ? BLUE : RED,
    label: b.count[i] ? `n=${b.count[i]}` : '',
  }))
})
const strip = computed(() =>
  xs.map((x, i) => ({ x, y: (i % 5) * 0.55 - 1.1, color: demo.y[i] ? BLUE : RED, r: 3.2 })),
)
const edgeLines = computed(() => bins.value.edges.map((e) => ({ x: e, color: '#e8eaed', dash: '' })))
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <LineChart
        :series="[]" :bars="bars" :dots="strip" :vlines="edgeLines"
        :hlines="[{ y: 0, color: INK, dash: '' }]"
        :x-domain="[0, 1]" :y-domain="[-6, 6]" :x-ticks="[0, 0.5, 1]" :y-ticks="[-4, 0, 4]"
        x-label="feature value" y-label="Σ g in the bin"
        :title="`the same 40 rows, sorted once and cut into ${Math.round(nBins)} bins`"
      />
      <div class="store">
        <p class="h">keep per bin what the scan will need</p>
        <table class="plain">
          <thead><tr><th>bin</th><th>Σg</th><th>Σh</th><th>n</th></tr></thead>
          <tbody>
            <tr v-for="(c, i) in bins.count.slice(0, 7)" :key="i">
              <td>{{ i }}</td>
              <td :style="{ color: bins.sumG[i] < 0 ? BLUE : RED }">{{ bins.sumG[i].toFixed(2) }}</td>
              <td>{{ bins.sumH[i].toFixed(2) }}</td>
              <td>{{ c }}</td>
            </tr>
            <tr v-if="bins.count.length > 7"><td colspan="4" class="dots">⋮</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="nBins" :min="2" :max="40" :step="1" label="bins" :digits="0" :color="GREEN" />
        <Readout
          :items="[
            { label: 'numbers stored', value: `3 × ${Math.round(nBins)} = ${3 * Math.round(nBins)}`, color: GREEN },
            { label: 'instead of', value: `${demo.X.length} sorted rows per feature` },
          ]"
        />
      </div>
      <p class="note">
        One pass over the rows fills the histogram, and the pass is over whatever
        number of rows you have; the scan that follows is over bins, and LightGBM
        uses 255 of them whether there are a thousand rows or a billion.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.6rem; min-height: 0; }
.store { display: flex; flex-direction: column; justify-content: center; }
.h { font-size: 0.82rem; font-weight: 600; margin: 0 0 0.3rem; text-align: center; }
.dots { text-align: center; color: var(--muted); }
td { font-variant-numeric: tabular-nums; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child { min-width: 11rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
