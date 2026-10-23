<!-- factorization_columns: one column x_j is the same three parts w_k in
     different amounts h_j(k). Move the amounts and match the column by hand. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { mat } from '../lib/mat'
import { BLUE, GOLD, GREEN, INK, PURPLE } from '../lib/theme'

const idx = Array.from({ length: 14 }, (_, i) => i)
const atoms = [
  idx.map((i) => Math.exp(-(((i - 2.5) / 1.6) ** 2))),
  idx.map((i) => 0.9 * Math.exp(-(((i - 7.0) / 1.3) ** 2))),
  idx.map((i) => 0.8 * Math.exp(-(((i - 11.5) / 2.0) ** 2))),
]
const truth = [0.9, 0.35, 0.6]
const h = [ref(0.5), ref(0.5), ref(0.5)]
const strip = (v: number[]) => ({ ...mat(14, 1), a: Float64Array.from(v) })
const target = strip(idx.map((i) => truth.reduce((s, t, k) => s + t * atoms[k][i], 0)))
const model = computed(() => strip(idx.map((i) => h.reduce((s, t, k) => s + t.value * atoms[k][i], 0))))
const err = computed(() => Math.sqrt(idx.reduce((s, i) => s + (target.a[i] - model.value.a[i]) ** 2, 0)))
const parts = atoms.map(strip)
</script>

<template>
  <div class="wrap">
    <div class="note top">Every column of the table is the same few parts, in different amounts.</div>
    <div class="row">
      <div class="col">
        <MatView :M="target" ramp="x" :vmax="1" :border="BLUE" title="x<sub>j</sub>" :title-color="BLUE" />

      </div>
      <div class="op">≈</div>
      <div class="col">
        <MatView :M="model" ramp="x" :vmax="1" :border="GREEN" title="W h<sub>j</sub>" :title-color="GREEN" />

      </div>
      <div class="op">=</div>
      <template v-for="k in 3" :key="k">
        <div class="amount" :style="{ color: GOLD }">{{ h[k - 1].value.toFixed(2) }}<span class="note">×</span></div>
        <div class="col">
          <MatView :M="parts[k - 1]" ramp="w" :vmax="1" :border="PURPLE" :title="`w<sub>${k}</sub>`" :title-color="PURPLE" />
        </div>
        <div v-if="k < 3" class="op">+</div>
      </template>
      <div class="side legend">
        <p :style="{ color: PURPLE }">w<sub>k</sub>: the same for every column j</p>
        <p :style="{ color: GOLD }">h<sub>j</sub>: r numbers, one column at a time</p>
        <p class="note">x<sub>j</sub>: one face, one document, one pixel</p>
        <p :style="{ color: err < 0.05 ? GREEN : INK }">‖x<sub>j</sub> − W h<sub>j</sub>‖ = <b>{{ err.toFixed(2) }}</b>{{ err < 0.05 ? ': rebuilt' : '' }}</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-for="k in 3" :key="k" v-model="h[k - 1].value" :min="0" :max="1.5" :step="0.01" :label="`h<sub>j</sub>(${k})`" :color="GOLD" />
    </div>
    <div class="note bottom">h<sub>j</sub> is the new, r-dimensional description of x<sub>j</sub>. Find the three amounts that rebuild it.</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.5rem; height: 100%; min-height: 0; }
.top, .bottom { text-align: center; }
.row { display: flex; align-items: center; justify-content: center; gap: 0.7rem; min-height: 0; }
.col { width: 2.6rem; height: 13rem; display: flex; flex-direction: column; }
.col :deep(.mat) { height: 11rem; }
.col .cap { width: 7rem; margin-left: -2.2rem; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.7rem; line-height: 1.3; margin-top: 0.3rem; }
.op { font-size: 1.5rem; color: #9aa0a6; }
.amount { font-size: 1.1rem; font-variant-numeric: tabular-nums; }
.legend { width: 14rem; margin-left: 1.2rem; font-size: 0.8rem; }
</style>
