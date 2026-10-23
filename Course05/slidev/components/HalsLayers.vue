<!-- hals_layers: WH is a sum of r rank-one layers w_k h^(k). Add them one by
     one and watch the sum become X. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { layers } from '../lib/data5'
import { col, mat, row } from '../lib/mat'
import { BLUE, GOLD, GREEN, INK, PURPLE } from '../lib/theme'

const { X, W, H } = layers
const colors = [PURPLE, GOLD, GREEN]
const m = ref(1)
const layer = (k: number) => {
  const out = mat(X.r, X.c)
  const w = col(W, k), h = row(H, k)
  for (let i = 0; i < X.r; i++) for (let j = 0; j < X.c; j++) out.a[i * X.c + j] = w[i] * h[j]
  return out
}
const L = [0, 1, 2].map(layer)
const sum = computed(() => { const out = mat(X.r, X.c); for (let k = 0; k < m.value; k++) L[k].a.forEach((v, i) => { out.a[i] += v }); return out })
const vmax = Math.max(...X.a)
const err = computed(() => { let e = 0, n = 0; X.a.forEach((v, i) => { e += (v - sum.value.a[i]) ** 2; n += v * v }); return Math.sqrt(e / n) })
</script>

<template>
  <div class="wrap">
    <div class="note top">Every factorization is a sum of r rank-one layers: WH = w₁h⁽¹⁾ + … + w<sub>r</sub>h⁽ʳ⁾</div>
    <div class="row">
      <MatView :M="X" ramp="x" :vmax="vmax" :border="BLUE" title="X" :title-color="BLUE" square />
      <span class="op">≈</span>
      <template v-for="k in 3" :key="k">
        <MatView :M="L[k - 1]" ramp="x" :vmax="vmax" :border="k <= m ? colors[k - 1] : '#dfe2e5'" :title="`w<sub>${k}</sub> h<sup>(${k})</sup>`" :title-color="k <= m ? colors[k - 1] : '#9aa0a6'" square :class="{ off: k > m }" />
        <span v-if="k < 3" class="op">+</span>
      </template>
      <span class="op">=</span>
      <MatView :M="sum" ramp="x" :vmax="vmax" :border="INK" :title="`the first ${m}`" square />
    </div>
    <div class="note center">One column of W times one row of H: a rank-one non-negative matrix, and the whole model is their sum.</div>
    <div class="controls">
      <Knob v-model="m" :min="1" :max="3" :step="1" label="layers summed" :digits="0" :color="INK" />
      <Readout :items="[{ label: 'relative error', value: `${(100 * err).toFixed(1)}%` }]" />
    </div>
    <div class="center" :style="{ color: GOLD }">MU moves all r layers at once. HALS moves one, exactly, holding the other r − 1 fixed.</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto auto; gap: 0.5rem; height: 100%; min-height: 0; }
.top, .center { text-align: center; }
.row { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr auto 1fr; gap: 0.5rem; align-items: center; min-height: 0; }
.row > :deep(.mat) { height: 100%; }
.op { color: #9aa0a6; font-size: 1.4rem; }
.off { opacity: 0.35; }
</style>
