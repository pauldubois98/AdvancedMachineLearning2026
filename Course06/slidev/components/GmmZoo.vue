<!-- gmm_zoo: the six mixtures of the 2023 lecture (Marron and Wand's
     test densities). Pick one; show its weighted components if you like. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace, mixPdf1, weighted1, type Mix1 } from '../lib/gmm'
import { curve } from '../lib/charts'
import { COMP, INK, MUTED } from '../lib/theme'

const j = [-2, -1, 0, 1, 2]
const k8 = [0, 1, 2, 3, 4, 5, 6, 7]
const DENS: { name: string; m: Mix1 }[] = [
  { name: 'asymmetric unimodal', m: { p: [1 / 5, 1 / 5, 3 / 5], mu: [0, 1 / 2, 13 / 15], sd: [1, 2 / 3, 5 / 9] } },
  { name: 'strongly asymmetric unimodal', m: { p: k8.map(() => 1 / 8), mu: k8.map((k) => 3 * ((2 / 3) ** k - 1)), sd: k8.map((k) => (2 / 3) ** k) } },
  { name: 'bimodal', m: { p: [0.5, 0.5], mu: [-1, 1], sd: [2 / 3, 2 / 3] } },
  { name: 'asymmetric bimodal', m: { p: [3 / 4, 1 / 4], mu: [0, 1.5], sd: [1, 1 / 3] } },
  { name: 'tri-modal', m: { p: [9 / 20, 9 / 20, 1 / 10], mu: [-6 / 5, 6 / 5, 0], sd: [3 / 5, 3 / 5, 1 / 4] } },
  { name: 'more complex', m: { p: [0.5, ...j.map((v) => 2 ** (1 - v) / 31)], mu: [0, ...j.map((v) => v + 0.5)], sd: [1, ...j.map((v) => 2 ** -v / 10)] } },
]
const pick = ref('0')
const showParts = ref(true)
const d = computed(() => DENS[+pick.value])
const range = computed(() => {
  const m = d.value.m
  return [Math.min(...m.mu.map((u, k) => u - 3.5 * m.sd[k])), Math.max(...m.mu.map((u, k) => u + 3.5 * m.sd[k]))] as [number, number]
})
const grid = computed(() => linspace(range.value[0], range.value[1], 700))
const top = computed(() => Math.max(...grid.value.map((x) => mixPdf1(x, d.value.m))) * 1.12)
const parts = computed(() => !showParts.value ? [] : d.value.m.p.map((_, k) => ({
  points: curve(grid.value, (x) => weighted1(x, d.value.m)[k]), color: COMP[k % COMP.length], width: 1.4, dash: '5 4',
})))
const thumbs = DENS.map((dd) => {
  const lo = Math.min(...dd.m.mu.map((u, k) => u - 3.5 * dd.m.sd[k]))
  const hi = Math.max(...dd.m.mu.map((u, k) => u + 3.5 * dd.m.sd[k]))
  const g = linspace(lo, hi, 120)
  const ys = g.map((x) => mixPdf1(x, dd.m))
  const mx = Math.max(...ys)
  return g.map((x, i) => `${(((x - lo) / (hi - lo)) * 100).toFixed(1)},${(30 - (ys[i] / mx) * 28).toFixed(1)}`).join(' ')
})
</script>

<template>
  <div class="wrap">
    <div class="note top">Six mixtures of normals: asymmetric, heavy-shouldered, multi-modal, spiky...</div>
    <div class="body">
      <div class="thumbs">
        <button v-for="(dd, i) in DENS" :key="i" :class="{ on: pick === String(i) }" @click="pick = String(i)">
          <svg viewBox="0 0 100 31" preserveAspectRatio="none"><polyline :points="thumbs[i]" :style="{ fill: 'none', stroke: pick === String(i) ? COMP[i % 3] : MUTED, strokeWidth: 1.6 }" vector-effect="non-scaling-stroke" /></svg>
          <span :style="{ color: COMP[i % 3] }">({{ 'abcdef'[i] }}) {{ dd.name }}</span>
        </button>
      </div>
      <div class="col">
        <LineChart
          :series="[...parts, { points: curve(grid, (x) => mixPdf1(x, d.m)), color: INK, width: 2.6 }]"
          :x-domain="range" :y-domain="[0, top]" :x-ticks="[]" :y-ticks="[]"
          :title="`(${'abcdef'[+pick]}) ${d.name}: K = ${d.m.p.length}`" :title-color="COMP[+pick % 3]"
        />
      </div>
    </div>
    <div class="controls">
      <Toggle v-model="showParts" label="show the weighted components p<sub>k</sub> f<sub>k</sub>" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 2fr; gap: 1.6rem; min-height: 0; }
.thumbs { display: grid; grid-template-rows: repeat(6, 1fr); gap: 0.3rem; min-height: 0; }
.thumbs button { display: grid; grid-template-columns: 4.5rem 1fr; gap: 0.6rem; align-items: center; border: 1px solid #eef0f2; border-radius: 6px; background: white; padding: 0.15rem 0.5rem; cursor: pointer; text-align: left; font-size: 0.78rem; }
.thumbs button.on { border-color: #9aa0a6; background: #f7f8f9; font-weight: 600; }
.thumbs svg { width: 100%; height: 1.7rem; }
.col { min-height: 0; }
</style>
