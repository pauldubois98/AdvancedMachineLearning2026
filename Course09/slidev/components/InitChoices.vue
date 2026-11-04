<!-- init_choices: the start, and where SNE ends from it. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { TOY } from '../lib/data'
import { TOY_ITERS, toyRun } from '../lib/toyrun'
import { span, stripDots } from '../lib/strip'
import { GREEN, LOW } from '../lib/theme'

const start = ref('random')
const seed = ref(1)
const runs = computed(() => [1, 2, 3, 4, 5, 6].map((s) => toyRun(s, 'random').kl[TOY_ITERS]))
const run = computed(() => toyRun(Math.round(seed.value), start.value as 'random' | 'pca'))
const y0 = computed(() => run.value.Y[0])
const y1 = computed(() => run.value.Y[TOY_ITERS])
const line = (l: [number, number]) => [{ points: [[l[0], 0], [l[1], 0]] as [number, number][], color: '#cccfd2', width: 1.5 }]
</script>

<template>
  <div class="cmp">
    <div class="stack">
      <LineChart :series="line(span(y0))" :dots="stripDots(y0, TOY.g)" :x-domain="span(y0)" :y-domain="[-0.6, 0.6]" :axes="false" :unit-height="160"
        :title="start === 'pca' ? 'start: the first PCA axis, scaled down' : `start: random, seed ${Math.round(seed)}`" :title-color="LOW" />
      <LineChart :series="line(span(y1))" :dots="stripDots(y1, TOY.g)" :x-domain="span(y1)" :y-domain="[-0.6, 0.6]" :axes="false" :unit-height="160"
        :title="`after ${TOY_ITERS} moves: KL = ${run.kl[TOY_ITERS].toFixed(3)}`" :title-color="GREEN" />
    </div>
    <div class="foot">Non-convex: the start decides which minimum is found (random seeds 1 to 6 end at KL
      {{ runs.map((v) => v.toFixed(3)).join(', ') }}). A PCA start keeps the global order.</div>
    <div class="controls">
      <Choice v-model="start" :options="[{ value: 'random', label: 'random start', color: LOW }, { value: 'pca', label: 'PCA start', color: '#6b46c1' }]" />
      <Knob v-model="seed" :min="1" :max="30" :step="1" :digits="0" label="seed" :color="LOW" :disabled="start === 'pca'" />
    </div>
  </div>
</template>
