<!-- sne_iterations: the toy's map, move by move, and its loss. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { TOY } from '../lib/data'
import { TOY_ITERS, toyRun } from '../lib/toyrun'
import { span, stripDots } from '../lib/strip'
import { GREEN, LOW } from '../lib/theme'

const t = ref(0)
const lr = ref(0.3)
const run = computed(() => toyRun(1, 'random', Math.round(lr.value * 100) / 100))
const T = computed(() => Math.round(t.value))
const Y = computed(() => run.value.Y[T.value])
const lim = computed(() => span(Y.value))
const kls = computed(() => run.value.kl.map((v, k) => [k, v] as [number, number]))
const top = computed(() => Math.max(...run.value.kl) * 1.05)
</script>

<template>
  <div class="cmp">
    <div class="r23" style="grid-template-columns: 1.6fr 1fr">
      <LineChart :series="[{ points: [[lim[0], 0], [lim[1], 0]], color: '#cccfd2', width: 1.5 }]" :dots="stripDots(Y, TOY.g, -1, 5)"
        :x-domain="lim" :y-domain="[-0.6, 0.6]" :axes="false" :title="`move ${T}: the map is ${(lim[1] - lim[0]).toPrecision(2)} wide (rescaled to fit)`" :title-color="LOW" />
      <LineChart :series="[{ points: kls, color: GREEN, width: 2.2 }]" :dots="[{ x: T, y: run.kl[T], color: GREEN, r: 5 }]"
        :x-domain="[0, TOY_ITERS]" :y-domain="[0, top]" :x-ticks="[0, 100, 200, 300]" :y-ticks="[0, 0.5, 1, 1.5]" x-label="move t"
        :title="`the loss: KL = ${run.kl[T].toFixed(3)}`" />
    </div>
    <div class="foot">One move: yᵢ ← yᵢ − η ∂C/∂yᵢ for every i (with momentum). The map first grows from its tiny start, then the groups separate.</div>
    <div class="controls">
      <Knob v-model="t" :min="0" :max="TOY_ITERS" :step="1" :digits="0" label="move t" :color="GREEN" />
      <Knob v-model="lr" :min="0.05" :max="3" log label="learning rate η" :color="LOW" />
    </div>
  </div>
</template>
