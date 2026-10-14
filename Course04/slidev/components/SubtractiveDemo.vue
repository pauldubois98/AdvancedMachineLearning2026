<!-- subtractive_clustering: Chiu's gridless version. The potential lives on
     the data points themselves, and r_a is the only real knob. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { mountainData } from '../lib/data4'
import { potential, subtractive } from '../lib/mountain'
import { BLUE, GREEN, INK, density, rgb } from '../lib/theme'

const ra = ref(1.1)
const ratio = ref(0.5)
const X = mountainData()

const P = computed(() => potential(X, ra.value))
const pmax = computed(() => Math.max(...Array.from(P.value)))
const colors = computed(() => Array.from(P.value).map((v) => rgb(density(v / pmax.value))))
const sizes = computed(() => Array.from(P.value).map((v) => 1.6 + 4.2 * (v / pmax.value)))
const run = computed(() => subtractive(X, ra.value, ratio.value, 8))
const dom: [number, number, number, number] = [-3.4, 3.3, -2.6, 3.2]
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot
        :X="X" :colors="colors" :sizes="sizes" :domain="dom"
        title="potential at the data points" :title-color="BLUE"
      />
      <ClusterPlot
        :X="X" :labels="run.labels" :point-size="2.6" :domain="dom"
        :circles="run.centres.map((c) => ({ x: c[0], y: c[1], r: ra / 2, color: GREEN, alpha: 0.1 }))"
        :crosses="run.centres.map((c) => ({ x: c[0], y: c[1], color: GREEN }))"
        :title="`centres kept: ${run.centres.length}`" :title-color="GREEN"
      />
      <div class="side">
        <p><Tex display formula='P_i = \sum_j \exp\left(-\frac{4\|x_i - x_j\|^2}{r_a^2}\right)' /></p>
        <p class="note">r<sub>a</sub>: the neighbourhood radius.
          r<sub>b</sub> = 1.5 r<sub>a</sub> is what a chosen centre clears.</p>
        <p class="note">No grid, so nothing grows as m<sup>d</sup>: the
          candidates are the rows themselves.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="ra" :min="0.4" :max="2.6" label="r<sub>a</sub>" :color="BLUE" />
      <Knob v-model="ratio" :min="0.1" :max="0.98" label="keep peaks above this fraction" :color="GREEN" />
      <Readout
        :items="[
          { label: 'clusters found', value: String(run.centres.length), color: GREEN },
          { label: 'highest potential', value: run.first.toFixed(1) },
          { label: 'cutoff', value: (ratio * run.first).toFixed(1), color: GREEN },
          { label: 'heights taken', value: run.heights.map((h) => h.toFixed(1)).join(', ') },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr 0.8fr; gap: 1rem; min-height: 0; }
.side { align-self: center; font-size: 0.8rem; }
.side p { margin: 0 0 0.7rem; line-height: 1.5; }
.controls { display: flex; gap: 1.4rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 12rem; }
</style>
