<!-- hals_residual: what layer k has to explain on its own: X with every other
     layer taken out. R_k has negative entries, and that is exactly where the
     constraint w_k h^(k) >= 0 bites. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { layers } from '../lib/data5'
import { col, mat, row } from '../lib/mat'
import { BLUE, GOLD, GREEN, INK, PURPLE, RED } from '../lib/theme'

const { X, W, H } = layers
const colors = [PURPLE, GOLD, GREEN]
const k = ref(0)
const layer = (q: number) => {
  const out = mat(X.r, X.c)
  const w = col(W, q), h = row(H, q)
  for (let i = 0; i < X.r; i++) for (let j = 0; j < X.c; j++) out.a[i * X.c + j] = w[i] * h[j]
  return out
}
const L = [0, 1, 2].map(layer)
const others = computed(() => { const o = mat(X.r, X.c); L.forEach((l, q) => { if (q !== k.value) l.a.forEach((v, i) => { o.a[i] += v }) }); return o })
const Rk = computed(() => ({ ...X, a: X.a.map((v, i) => v - others.value.a[i]) }))
const negs = computed(() => Rk.value.a.filter((v) => v < -1e-3).length)
const vmax = Math.max(...X.a)
</script>

<template>
  <div class="wrap">
    <div class="note top">What layer k has to explain on its own: X, with every other layer taken out</div>
    <div class="row">
      <MatView :M="X" ramp="x" :vmax="vmax" :border="BLUE" title="X" :title-color="BLUE" square />
      <span class="op">−</span>
      <MatView :M="others" ramp="x" :vmax="vmax" border="#9aa0a6" title="the other layers" title-color="#9aa0a6" square />
      <span class="op">=</span>
      <MatView :M="Rk" ramp="rdbu" signed :border="RED" :title="`R<sub>${k + 1}</sub>`" :title-color="RED" square caption="red positive, blue negative" />
      <span class="op">≈</span>
      <MatView :M="L[k]" ramp="x" :vmax="vmax" :border="colors[k]" :title="`w<sub>${k + 1}</sub> h<sup>(${k + 1})</sup>`" :title-color="colors[k]" square />
    </div>
    <Tex formula="\tfrac{1}{2}\|X - WH\|_F^2 = \tfrac{1}{2}\|R_k - w_k h^{(k)}\|_F^2" display />
    <div class="note center">With every other layer frozen, the problem is a single rank-one fit. R<sub>{{ k + 1 }}</sub> has {{ negs }} negative entries: fitting a non-negative layer to it is exactly where the constraint bites.</div>
    <div class="controls">
      <Knob v-model="k" :min="0" :max="2" :step="1" label="layer k" :digits="0" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top, .center { text-align: center; }
.row { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr; gap: 0.6rem; align-items: center; min-height: 0; }
.row > :deep(.mat) { height: 100%; }
.op { color: #9aa0a6; font-size: 1.4rem; }
</style>
