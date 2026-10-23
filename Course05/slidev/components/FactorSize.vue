<!-- factorization_idea: X (p x n) against W (p x r) and H (r x n). The rank r
     moves the width of W and the height of H, and the count of numbers. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { mat } from '../lib/mat'
import { Rng } from '../lib/rng'
import { BLUE, GOLD, INK, PURPLE } from '../lib/theme'

const r = ref(16)
const p = 4096
const n = 400
const R_MAX = 128
function cells(rows: number, cols: number, seed: number) {
  const m = mat(rows, cols)
  const rng = new Rng(seed)
  for (let i = 0; i < m.a.length; i++) m.a[i] = rng.next() ** 1.4
  return m
}
const X = cells(12, 12, 3)
// one cell of W or H per 8 components, so the picture grows with r
const k = computed(() => Math.max(1, Math.round(r.value / 8)))
const Wm = computed(() => cells(12, k.value, 5))
const Hm = computed(() => cells(k.value, 12, 7))
const frac = computed(() => r.value / R_MAX)
const full = p * n
const small = computed(() => p * r.value + r.value * n)
const fmt = (v: number) => v.toLocaleString('en').replace(/,/g, ' ')
</script>

<template>
  <div class="wrap">
    <div class="note top">The table is big; the thing it describes may be small.</div>
    <div class="row">
      <div class="m x">
        <MatView :M="X" ramp="x" :border="BLUE" title="X" :title-color="BLUE" />
        <div class="cap">p × n<br><span :style="{ color: BLUE }">4096 pixels × 400 faces<br>= {{ fmt(full) }} numbers</span></div>
      </div>
      <div class="op">≈</div>
      <div class="m w" :style="{ width: `calc(${Math.max(frac, 0.04)} * 14rem)` }">
        <MatView :M="Wm" ramp="w" :border="PURPLE" title="W" :title-color="PURPLE" />
        <div class="cap">p × r</div>
      </div>
      <div class="op small">·</div>
      <div class="m h">
        <div class="hbox" :style="{ height: `calc(${Math.max(frac, 0.04)} * 14rem + 1.4rem)` }">
          <MatView :M="Hm" ramp="h" :border="GOLD" title="H" :title-color="GOLD" />
        </div>
        <div class="cap">r × n</div>
        <div class="count" :style="{ color: PURPLE }">
          r = {{ r }}<br>
          4096 × {{ r }} + {{ r }} × 400<br>= {{ fmt(small) }} numbers<br>
          <b>{{ (100 * small / full).toFixed(1) }}%</b> of the table
        </div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="r" :min="1" :max="R_MAX" :step="1" label="r, the rank" :digits="0" :color="INK" />
      <span class="note">A low-rank model: rank(WH) ≤ r &lt; min(p, n).</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.row { display: flex; align-items: flex-start; justify-content: center; gap: 1.2rem; min-height: 0; padding-top: 0.5rem; }
.m { display: flex; flex-direction: column; align-items: center; }
.m.x { width: 14rem; height: 17.5rem; }
.m.x :deep(.mat) { height: 15.4rem; width: 14rem; }
.m.w { height: 17.5rem; min-width: 1.2rem; transition: width 0.15s; }
.m.w :deep(.mat) { height: 15.4rem; width: 100%; }
.m.h { width: 14rem; }
.hbox { width: 14rem; transition: height 0.15s; }
.op { font-size: 2rem; color: #9aa0a6; align-self: center; }
.op.small { font-size: 1.4rem; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.75rem; margin-top: 0.25rem; line-height: 1.4; }
.count { margin-top: 0.8rem; text-align: center; font-size: 0.85rem; line-height: 1.45; }
</style>
