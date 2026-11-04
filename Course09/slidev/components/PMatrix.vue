<!-- p_matrix: every row at once, then symmetrised. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { TOY, TOY_N, toyP } from '../lib/data'
import { HIGH } from '../lib/theme'

const perp = ref(8)
const P = computed(() => toyP(perp.value))
const vmax = computed(() => { const v = Array.from(P.value.P).sort((a, b) => a - b); return v[Math.floor(v.length * 0.97)] })
const vmaxC = computed(() => { const v = Array.from(P.value.Pc).sort((a, b) => a - b); return v[Math.floor(v.length * 0.97)] })
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Heat :M="P.Pc" :n="TOY_N" :groups="TOY.g" :vmax="vmaxC" title="pⱼ|ᵢ: row i sums to 1" :title-color="HIGH" />
      <Heat :M="P.P" :n="TOY_N" :groups="TOY.g" :vmax="vmax" title="pᵢⱼ: symmetric, all sum to 1" :title-color="HIGH" />
    </div>
    <div class="foot">One row per point; the blocks: neighbours lie in the same group. A larger perplexity spreads each row over more neighbours.</div>
    <div class="controls"><Knob v-model="perp" :min="2" :max="40" :step="1" :digits="0" label="perplexity" :color="HIGH" /></div>
  </div>
</template>
