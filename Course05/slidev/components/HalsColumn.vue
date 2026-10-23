<!-- hals_column: one entry of w_k at a time. Its cost is a parabola in that
     entry alone, ½‖h‖² w² − [R h]_i w; the vertex is legal when [R h]_i > 0,
     and otherwise zero is the best legal value. So the clip is exact. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { range } from '../lib/losses'
import { GOLD, GREEN, INK, RED } from '../lib/theme'

const b = ref(0.6)
const hh = ref(1)
const f = (w: number) => 0.5 * hh.value * w * w - b.value * w
const vertex = computed(() => b.value / hh.value)
const best = computed(() => Math.max(0, vertex.value))
const ws = range(-1.3, 1.5, 200)
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[{ points: ws.map((w) => [w, f(w)]), color: INK, width: 2.4 }, ...(vertex < 0 ? [{ points: [[vertex, f(vertex)], [0, f(0)]] as [number, number][], color: RED, width: 1.6 }] : [])]"
        :bands="[{ x0: -1.3, x1: 0, color: '#edeef0', alpha: 1 }]"
        :dots="[{ x: vertex, y: f(vertex), color: vertex < 0 ? '#9aa0a6' : GREEN, r: 5 }, { x: best, y: f(best), color: vertex < 0 ? RED : GREEN, r: 6 }]"
        :labels="[{ x: -0.65, y: 0.95, text: 'forbidden', color: '#9aa0a6', size: 12 }]"
        :x-domain="[-1.3, 1.5]" :y-domain="[-0.7, 1.1]" x-label="the entry w_ik" :x-ticks="[0]" :y-ticks="[]"
        :title="vertex >= 0 ? `[R h]ᵢ = ${b.toFixed(2)} > 0: the vertex is legal, keep it` : `[R h]ᵢ = ${b.toFixed(2)} < 0: the vertex is forbidden, zero is the best legal value`"
        :title-color="vertex >= 0 ? GREEN : RED"
      />
      <div class="side">
        <div class="h" :style="{ color: GREEN }">Why the clip is exact here</div>
        <Tex formula="\tfrac12\|R_k - w_k h^{(k)}\|_F^2 = \sum_i \Big(\tfrac12\|h^{(k)}\|^2 w_{ik}^2 - [R_k h^{(k)\top}]_i\, w_{ik}\Big) + c" display />
        <p class="note">The p entries never meet: minimizing under w<sub>k</sub> ≥ 0 is p separate one-dimensional problems, each solved by its own clip.</p>
        <Tex formula="w_k \leftarrow \left[\frac{R_k h^{(k)\top}}{\|h^{(k)}\|^2}\right]_+" display />
        <p :style="{ color: RED }" class="small">In ALS the entries are coupled by (WᵀW)⁻¹, so clipping there is only a heuristic. Here it is the constrained optimum.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="b" :min="-1" :max="1" :step="0.01" label="[R h]ᵢ" :color="GOLD" />
      <Knob v-model="hh" :min="0.4" :max="2" :step="0.01" label="‖h‖²" :color="INK" />
      <Readout :items="[{ label: 'vertex', value: vertex.toFixed(2) }, { label: 'new w_ik', value: best.toFixed(2), color: GREEN }]" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.3fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
.small { font-size: 0.78rem; }
</style>
