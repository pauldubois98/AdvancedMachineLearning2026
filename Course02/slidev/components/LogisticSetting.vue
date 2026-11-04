<!-- logistic_setting: two classes, a linear boundary. Pull the classes apart
     and a hyperplane gets every point right; push them together and no
     linear model is perfect. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { blobs, fmt, logisticIrls, sigmoid } from '../lib/reg'
import { BLUE, INK, RED } from '../lib/theme'

const gap = ref(1.1)
const spread = ref(1.05)
const seed = ref(3)
const D = computed(() => blobs(new Rng(seed.value), 90, gap.value, spread.value))
const beta = computed(() => logisticIrls(D.value.X, D.value.y, 12).at(-1)!)
const score = (x: number, y: number) => beta.value[0] + beta.value[1] * x + beta.value[2] * y
const acc = computed(() => D.value.X.reduce((s, p, i) => s + ((score(p[0], p[1]) > 0 ? 1 : 0) === D.value.y[i] ? 1 : 0), 0) / D.value.X.length)
const pale = (v: number): [number, number, number] => (v > 0.5 ? [251, 236, 236] : [233, 240, 248])
</script>

<template>
  <div class="cmp">
    <Plane :X="D.X" :colors="D.y.map((c) => (c ? RED : BLUE))" :size="3.5" :alpha="0.75" :domain="[-5.5, 5.5, -4, 4]"
      :field="(x, y) => sigmoid(score(x, y))" :field-color="pale" :levels="[{ f: score, level: 0, color: INK, width: 2.4 }]" />
    <div class="foot">training accuracy <b>{{ fmt(100 * acc, 1) }} %</b>: {{ acc === 1 ? 'linearly separable, a hyperplane gets every point right' : 'no perfect linear model' }}</div>
    <div class="controls">
      <Knob v-model="gap" :min="0" :max="3" :step="0.01" label="class separation" :color="INK" />
      <Knob v-model="spread" :min="0.3" :max="2" :step="0.01" label="spread" :color="INK" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" :digits="0" label="new sample" :color="INK" />
    </div>
  </div>
</template>
