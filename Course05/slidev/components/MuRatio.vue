<!-- eq_mu_frobenius: the whole algorithm, and what the ratio does to one
     entry. Here [WᵀX]_kj = a and [WᵀWH]_kj = b H_kj + c, the other entries
     frozen: the ratio grows the entry while the model is too small, shrinks
     it while it is too big, and stops where the gradient is zero. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, INK, RED } from '../lib/theme'

const h = ref(0.3)
const a = 2.4, b = 1.5, c = 0.6
const fixed = (a - c) / b
const ratio = computed(() => a / (b * h.value + c))
const seq = computed(() => {
  const out = [h.value]
  for (let t = 0; t < 8; t++) { const v = out[out.length - 1]; out.push((v * a) / (b * v + c)) }
  return out
})
const verdict = computed(() => (Math.abs(ratio.value - 1) < 0.01 ? { t: 'ratio = 1: stop', c: BLUE } : ratio.value > 1 ? { t: 'ratio > 1: grow the entry', c: GREEN } : { t: 'ratio < 1: shrink it', c: RED }))
</script>

<template>
  <div class="wrap">
    <div class="note top">Lee and Seung, 1999: the whole algorithm, assuming X ≥ 0</div>
    <div class="hl-blue center">Frobenius norm ‖X − WH‖²<sub>F</sub></div>
    <div class="rules">
      <Tex formula="W \;\leftarrow\; W \odot \frac{X H^\top}{W H H^\top}" display />
      <Tex formula="H \;\leftarrow\; H \odot \frac{W^\top X}{W^\top W H}" display />
    </div>
    <div class="note center">⊙ and the fraction bar are entrywise. One pass costs two matrix products per factor: 𝒪(pnr).</div>
    <div class="demo">
      <div class="table">
        <div><b :style="{ color: GREEN }">ratio &gt; 1</b> the model is too small here: grow the entry</div>
        <div><b :style="{ color: RED }">ratio &lt; 1</b> the model is too big here: shrink it</div>
        <div><b :style="{ color: BLUE }">ratio = 1</b> stop: this is exactly ∇<sub>H</sub>F = 0 in direction kj</div>
      </div>
      <LineChart
        :series="[{ points: seq.map((v, t) => [t, v]), color: verdict.c, width: 2 }]"
        :dots="seq.map((v, t) => ({ x: t, y: v, color: t ? verdict.c : INK, r: t ? 3.5 : 5 }))"
        :hlines="[{ y: fixed, color: BLUE, dash: '4 3' }]"
        :x-domain="[-0.3, 8.3]" :y-domain="[0, 3]" x-label="pass" :x-ticks="[0, 2, 4, 6, 8]" :y-ticks="[0, 1, 2, 3]"
        :title="`H_kj over eight passes; ratio now ${ratio.toFixed(2)}`" :title-color="verdict.c"
      />
    </div>
    <div class="controls">
      <Knob v-model="h" :min="0.05" :max="3" :step="0.01" label="current H_kj" :color="INK" />
      <span :style="{ color: verdict.c, fontWeight: 600 }">{{ verdict.t }}</span>
      <span class="note">dashed: the fixed point, where [WᵀX]_kj = [WᵀWH]_kj</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto auto auto auto 1fr auto; gap: 0.3rem; height: 100%; min-height: 0; }
.center, .top { text-align: center; }
.rules { display: grid; grid-template-columns: 1fr 1fr; }
.demo { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; min-height: 0; align-items: center; }
.table { display: flex; flex-direction: column; gap: 0.6rem; font-size: 0.88rem; }
.table b { display: inline-block; width: 5.5rem; }
</style>
