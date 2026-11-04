<!-- logistic_fit: Newton / IRLS from β = 0, one weighted least squares step at
     a time; the objective falls fast. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { blobs, fmt, logisticIrls, logisticLoss, sigmoid } from '../lib/reg'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const gap = ref(1.5)
const k = ref(0)
const D = computed(() => blobs(new Rng(23), 80, gap.value, 1))
const hist = computed(() => logisticIrls(D.value.X, D.value.y, 8))
const b = computed(() => hist.value[k.value])
const score = (x: number, y: number) => b.value[0] + b.value[1] * x + b.value[2] * y
const losses = computed(() => hist.value.map((h, i) => [i, logisticLoss(D.value.X, D.value.y, h)] as [number, number]))
const pale = (v: number): [number, number, number] => (v > 0.5 ? [251, 236, 236] : [233, 240, 248])
const flat = computed(() => Math.abs(b.value[1]) + Math.abs(b.value[2]) < 1e-9)
</script>

<template>
  <div class="cmp">
    <div class="r2" style="grid-template-columns: 1.5fr 1fr">
      <Plane :X="D.X" :colors="D.y.map((c) => (c ? RED : BLUE))" :size="3" :alpha="0.7" :domain="[-5.5, 5.5, -4, 4]"
        :field="flat ? null : (x, y) => sigmoid(score(x, y))" :field-color="pale" :levels="flat ? [] : [{ f: score, level: 0, color: INK, width: 2.2 }]"
        :title="k === 0 ? 'k = 0 (β = 0): p = ½ everywhere' : `k = ${k}`" />
      <LineChart :series="[{ points: losses, color: GREEN, width: 2.4 }]" :dots="losses.map(([i, v]) => ({ x: i, y: v, color: i === k ? GREEN : MUTED, r: i === k ? 6 : 3.5 }))"
        :x-domain="[-0.3, 8.3]" :y-domain="[0, losses[0][1] * 1.05]" :x-ticks="[0, 2, 4, 6, 8]" :y-ticks="[]" x-label="iteration" y-label="F(β)" title="the objective" />
    </div>
    <div class="foot">a handful of weighted least squares steps: β = ({{ fmt(b[0]) }}, {{ fmt(b[1]) }}, {{ fmt(b[2]) }}), F = <b :style="{ color: GREEN }">{{ fmt(losses[k][1]) }}</b></div>
    <div class="controls">
      <Knob v-model="k" :min="0" :max="8" :step="1" :digits="0" label="iteration k" :color="GREEN" />
      <Knob v-model="gap" :min="0.3" :max="3" :step="0.01" label="class separation" :color="INK" />
    </div>
  </div>
</template>
