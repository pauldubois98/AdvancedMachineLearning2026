<!-- crowding, part 2: in d dimensions almost all of a ball's points sit near
     its edge. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace } from '../lib/geom'
import { GREEN, RED } from '../lib/theme'

const d = ref(10)
const shellW = ref(0.1)
const D = computed(() => Math.max(1, Math.round(d.value)))
const rs = linspace(0, 1, 300)
const curve = (k: number) => rs.map((r) => [r, k * r ** (k - 1)] as [number, number])
const ymax = computed(() => Math.min(Math.max(D.value, 2) * 1.08, 60))
const share = computed(() => 1 - (1 - shellW.value) ** D.value)
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> points drawn uniformly inside a ball of radius 1 in d dimensions. The curve is the density of their distance to the centre, d·r<sup>d−1</sup> (dashed: d = 2). The shaded band is the outer shell of the ball, the chosen share of its radius, and the sentence below gives the share of the points that fall inside it, 1 − (1 − width)<sup>d</sup>.</div>
    <LineChart
      :series="[{ points: curve(2), color: GREEN, width: 2, dash: '5 4' }, { points: curve(D), color: RED, width: 2.6 }]"
      :bands="[{ x0: 1 - shellW, x1: 1, color: RED, alpha: 0.1 }]"
      :x-domain="[0, 1]" :y-domain="[0, ymax]" :x-ticks="[0, 0.2, 0.4, 0.6, 0.8, 1]" :y-ticks="[]"
      x-label="distance to the centre (radius 1)" :title="`where the points of a ball lie: d = 2 (dashed), d = ${D}`" />
    <div class="foot">In {{ D }} dimensions, <b>{{ (100 * share).toFixed(0) }}%</b> of a ball's points lie in its outer {{ (100 * shellW).toFixed(0) }}% (shaded):
      most neighbours sit at about the same distance, and a low-dimensional map has no room for them all.</div>
    <div class="controls">
      <Knob v-model="d" :min="1" :max="200" log label="dimension d" :color="RED" />
      <Knob v-model="shellW" :min="0.01" :max="0.5" :step="0.01" label="outer shell (share of the radius)" :color="RED" />
    </div>
  </div>
</template>
