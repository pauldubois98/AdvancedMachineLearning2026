<!-- clustering_vs_dimred: both simplify the table, but along different axes.
     One slider takes columns away, the other takes rows away. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { blobs } from '../lib/data4'
import { kmeans } from '../lib/cluster'
import { BLUE, GREEN, clusterColor } from '../lib/theme'

const q = ref(2)
const k = ref(3)
const d = 8
const N = 12

const data = computed(() => blobs([[-1.5, -0.9], [1.6, -0.6], [0.1, 1.6]], 0.46, 45, 4))
const run = computed(() => kmeans(data.value.X, k.value, 2, 6))
const cells = computed(() =>
  Array.from({ length: N }, (_, i) => Array.from({ length: d }, (_, j) => (i * 7 + j * 3) % 5)),
)
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <div class="matrices">
        <div class="pair">
          <div>
            <div class="cap" :style="{ color: BLUE }">X ∈ ℝ<sup>N×d</sup></div>
            <table class="grid">
              <tr v-for="(row, i) in cells" :key="i">
                <td v-for="(v, j) in row" :key="j" :style="{ background: `rgba(43,108,176,${0.12 + 0.12 * v})` }" />
              </tr>
            </table>
          </div>
          <div class="arrow">→<div class="small" :style="{ color: GREEN }">q &lt; d</div></div>
          <div>
            <div class="cap" :style="{ color: BLUE }">Z ∈ ℝ<sup>N×q</sup></div>
            <table class="grid">
              <tr v-for="(row, i) in cells" :key="i">
                <td v-for="(v, j) in row.slice(0, q)" :key="j" :style="{ background: `rgba(43,108,176,${0.12 + 0.12 * v})` }" />
              </tr>
            </table>
          </div>
        </div>
        <div class="note mt-2">dimension reduction: fewer columns, same rows</div>
      </div>
      <ClusterPlot
        :X="data.X" :labels="run.labels" :point-size="3"
        :crosses="run.mu.map((m, i) => ({ x: m[0], y: m[1], color: clusterColor(i) }))"
        :tags="run.mu.map((m, i) => ({ x: m[0], y: m[1] + 1.15, text: `C${i + 1}`, color: clusterColor(i), size: 13 }))"
        title="clustering: fewer rows, same columns" :title-color="GREEN"
      />
    </div>
    <div class="controls">
      <Knob v-model="q" :min="1" :max="7" :step="1" label="q, columns kept" :digits="0" :color="BLUE" />
      <Knob v-model="k" :min="2" :max="6" :step="1" label="K, groups kept" :digits="0" :color="GREEN" />
      <Readout
        :items="[
          { label: 'table', value: `${N} × ${d}` },
          { label: 'after reduction', value: `${N} × ${q}`, color: BLUE },
          { label: 'after clustering', value: `${k} × ${d}`, color: GREEN },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1.15fr 1fr; gap: 2rem; min-height: 0; align-items: center; }
.matrices { display: flex; flex-direction: column; align-items: center; }
.pair { display: flex; align-items: center; gap: 1.1rem; }
.cap { font-size: 0.82rem; text-align: center; margin-bottom: 0.3rem; font-weight: 600; }
.grid { border-collapse: collapse; width: auto; }
.grid td { width: 15px; height: 13px; border: 1px solid #fff; padding: 0; }
.arrow { font-size: 1.4rem; color: #9aa0a6; text-align: center; }
.small { font-size: 0.78rem; }
.controls { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 12rem; }
</style>
