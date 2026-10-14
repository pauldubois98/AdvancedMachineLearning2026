<!-- homogeneous_vs_heterogeneous: clusters that look alike, or clusters whose
     size, shape and density all differ. Two sliders set how unlike they get. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { BLUE, GREEN } from '../lib/theme'

const sizeRatio = ref(3.2)
const stretch = ref(2.0)

const same = (() => {
  const rng = new Rng(19)
  const X: number[][] = []
  const y: number[] = []
  ;[[-1.5, -0.6], [1.5, -0.6], [0, 1.6]].forEach((c, k) => {
    for (let i = 0; i < 55; i++) { X.push([rng.normal(c[0], 0.42), rng.normal(c[1], 0.42)]); y.push(k) }
  })
  return { X, y }
})()

const other = computed(() => {
  const rng = new Rng(23)
  const X: number[][] = []
  const y: number[] = []
  const wide = 0.32 * sizeRatio.value
  for (let i = 0; i < 80; i++) { X.push([rng.normal(-1.4, wide), rng.normal(-0.3, wide)]); y.push(0) }
  for (let i = 0; i < 25; i++) { X.push([rng.normal(1.7, 0.17), rng.normal(1.5, 0.17)]); y.push(1) }
  for (let i = 0; i < 60; i++) {
    const a = rng.normal(0, 0.28)
    const b = rng.normal(0, 0.28)
    X.push([1.9 + a * stretch.value, -1.4 + b * 0.45])
    y.push(2)
  }
  return { X, y }
})
const dom: [number, number, number, number] = [-4.6, 4.6, -3.2, 3.6]
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot :X="same.X" :labels="same.y" :domain="dom" :point-size="2.8" title="homogeneous" :title-color="BLUE" />
      <ClusterPlot :X="other.X" :labels="other.y" :domain="dom" :point-size="2.8" title="heterogeneous" :title-color="GREEN" />
      <div class="side">
        <p><em class="hl-blue">homogeneous</em><br />
          <span class="note">same size, same shape, same density</span></p>
        <p><em class="hl-green">heterogeneous</em><br />
          <span class="note">sizes, shapes and densities that differ</span></p>
        <p class="note">k-means assumes the left panel. HDBSCAN is built for
          the right one.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="sizeRatio" :min="1" :max="6" label="how much wider the loose blob is" :color="GREEN" />
      <Knob v-model="stretch" :min="1" :max="4" label="how stretched the third one is" :color="GREEN" />
      <Readout
        :items="[
          { label: 'widest / tightest spread', value: `${(0.32 * sizeRatio / 0.17).toFixed(1)}×`, color: GREEN },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr 0.8fr; gap: 1rem; min-height: 0; }
.side { font-size: 0.85rem; align-self: center; }
.side p { margin: 0 0 0.7rem; line-height: 1.5; }
.controls { display: flex; gap: 1.3rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 15rem; }
</style>
