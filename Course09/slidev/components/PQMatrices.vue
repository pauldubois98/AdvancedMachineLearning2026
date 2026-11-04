<!-- pq_matrices: P, and Q at move t. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { TOY, TOY_N, toyP } from '../lib/data'
import { TOY_ITERS, toyRun } from '../lib/toyrun'
import { GREEN, HIGH, LOW } from '../lib/theme'

const t = ref(0)
const run = toyRun()
const { P } = toyP()
const vmax = (() => { const v = Array.from(P).filter((x) => x > 1e-9).sort((a, b) => a - b); return v[Math.floor(v.length * 0.95)] })()
const st = computed(() => run.emb(Math.round(t.value)))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Heat :M="P" :n="TOY_N" :groups="TOY.g" :vmax="vmax" title="P: the data" :title-color="HIGH" />
      <Heat :M="st.Q" :n="TOY_N" :groups="TOY.g" :vmax="vmax" :title="`Q at move ${Math.round(t)}: KL = ${st.kl.toFixed(3)}`" :title-color="Math.round(t) === TOY_ITERS ? GREEN : LOW" />
    </div>
    <div class="foot">At the start every pair is equally likely; the moves bring Q's blocks in line with P's.</div>
    <div class="controls"><Knob v-model="t" :min="0" :max="TOY_ITERS" :step="1" :digits="0" label="move t" :color="LOW" /></div>
  </div>
</template>
