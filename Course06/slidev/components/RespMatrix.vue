<!-- responsibility_matrix: one row per point, one column per component. The
     slider runs EM from a poor start: the table sharpens pass after pass. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, em1, resp1 } from '../lib/gmm'
import { Rng } from '../lib/rng'
import { COMP, GOLD, BLUE, INK } from '../lib/theme'

const rng = new Rng(3)
const idx = new Set<number>()
while (idx.size < 16) idx.add(Math.floor(rng.next() * ANIMALS.length))
const xs = [...idx].map((i) => ANIMALS[i]).sort((a, b) => a - b)
const hist = em1(ANIMALS, { p: [0.5, 0.5], mu: [88, 91], sd: [2.2, 2.2] }, 30)
const t = ref(30)
const g = computed(() => xs.map((x) => resp1(x, hist[t.value])))
const nk = computed(() => [0, 1].map((k) => ANIMALS.reduce((a, x) => a + resp1(x, hist[t.value])[k], 0)))
const shade = (v: number, k: number) => {
  const c = k ? [183, 121, 31] : [43, 108, 176]
  return `rgb(${Math.round(255 - v * (255 - c[0]))},${Math.round(255 - v * (255 - c[1]))},${Math.round(255 - v * (255 - c[2]))})`
}
</script>

<template>
  <div class="wrap">
    <div class="note top">One row per point, one column per component (16 of the {{ ANIMALS.length }} rows)</div>
    <div class="body">
      <div class="mat">
        <div class="head"><span>xᵢ</span><span :style="{ color: COMP[0] }">γᵢ₁</span><span :style="{ color: COMP[1] }">γᵢ₂</span><span>sum</span></div>
        <div v-for="(row, i) in g" :key="i" class="row">
          <span class="x">{{ xs[i] }}</span>
          <span v-for="k in [0, 1]" :key="k" class="cell" :style="{ background: shade(row[k], k), color: row[k] > 0.6 ? 'white' : INK }">{{ row[k].toFixed(3) }}</span>
          <span class="sum">{{ (row[0] + row[1]).toFixed(0) }}</span>
        </div>
      </div>
      <div class="side">
        <div class="h" :style="{ color: GOLD }">Properties</div>
        <p>— rows sum to one</p>
        <p>— column sums are the soft class sizes</p>
        <p class="big">n₁ = <b :style="{ color: COMP[0] }">{{ nk[0].toFixed(1) }}</b>, n₂ = <b :style="{ color: COMP[1] }">{{ nk[1].toFixed(1) }}</b></p>
        <p class="note">n<sub>k</sub> = γ<sub>1k</sub> + ⋯ + γ<sub>nk</sub> is a soft count: it need not be a whole number.</p>
        <p class="note">Pass {{ t }} of EM from a poor start (μ = 88, 91): {{ t === 0 ? 'the table is blurred' : 'watch it sharpen' }}.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="t" :min="0" :max="30" :step="1" label="EM pass t" :digits="0" :color="BLUE" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2.5rem; min-height: 0; }
.mat { display: grid; grid-auto-rows: 1fr; font-size: 0.72rem; font-variant-numeric: tabular-nums; min-height: 0; align-self: stretch; }
.head, .row { display: grid; grid-template-columns: 3rem 5rem 5rem 2.5rem; gap: 2px; align-items: stretch; }
.head span { color: #9aa0a6; text-align: center; }
.cell { display: flex; align-items: center; justify-content: center; border-radius: 2px; }
.x, .sum { display: flex; align-items: center; justify-content: center; color: #9aa0a6; }
.side { align-self: center; }
.big { font-size: 1.05rem; margin: 0.6rem 0; }
</style>
