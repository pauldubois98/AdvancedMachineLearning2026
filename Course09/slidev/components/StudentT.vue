<!-- student_t: the map's kernel, Gaussian or Student-t with nu degrees of
     freedom (t-SNE uses nu = 1); at a given similarity the heavy tail sits
     farther away. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace } from '../lib/geom'
import { HIGH, MUTED, RED, TSNE_C } from '../lib/theme'

const nu = ref(1)
const level = ref(0.1)
const d = linspace(0, 6, 400)
const tk = (x: number) => (1 + (x * x) / nu.value) ** (-(nu.value + 1) / 2)
const dg = computed(() => Math.sqrt(-Math.log(level.value)))
const dt = computed(() => Math.sqrt(nu.value * (level.value ** (-2 / (nu.value + 1)) - 1)))
</script>

<template>
  <div class="cmp">
    <LineChart
      :series="[{ points: d.map((x) => [x, Math.exp(-x * x)]), color: HIGH, width: 2.4 }, { points: d.map((x) => [x, tk(x)]), color: TSNE_C, width: 2.6 }]"
      :hlines="[{ y: level, color: MUTED, dash: '4 4' }]" :vlines="[{ x: dg, color: HIGH, dash: '2 3' }, { x: Math.min(dt, 6), color: TSNE_C, dash: '2 3' }]"
      :arrows="[{ x0: dg, y0: level, x1: Math.min(dt, 6), y1: level, color: RED, width: 2 }]"
      :labels="[{ x: 4.2, y: 0.9, text: 'Gaussian exp(−d²) (SNE)', color: HIGH, anchor: 'start' }, { x: 4.2, y: 0.8, text: `Student-t, ν = ${nu.toPrecision(2)}`, color: TSNE_C, anchor: 'start' }]"
      :x-domain="[0, 6]" :y-domain="[0, 1.05]" :x-ticks="[0, 1, 2, 3, 4, 5, 6]" :y-ticks="[0, 0.5, 1]" x-label="distance in the map" y-label="similarity"
      :title="`the same similarity ${level.toFixed(2)} sits ${(dt / dg).toFixed(1)} times farther with the heavy tail`" />
    <div class="foot">With a heavy-tailed q, close neighbours are drawn a little closer and non-neighbours pushed away:
      room in the map for more points. t-SNE uses ν = 1; as ν grows the tail thins back towards a Gaussian.</div>
    <div class="controls">
      <Knob v-model="nu" :min="0.3" :max="100" log label="degrees of freedom ν" :color="TSNE_C" />
      <Knob v-model="level" :min="0.02" :max="0.6" :step="0.01" label="similarity level" :color="RED" />
    </div>
  </div>
</template>
