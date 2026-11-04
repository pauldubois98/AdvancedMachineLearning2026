<!-- dr_obstacles, concentration: in many dimensions all the distances
     between random points become nearly equal. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { histogram, linspace } from '../lib/geom'
import { pairDists } from '../lib/pairs'
import { Rng } from '../lib/rng'
import { GREEN, RED } from '../lib/theme'

const dim = ref(100)
const n = ref(120)
const D = computed(() => Math.round(dim.value))
const E = linspace(0, 2.2, 45)
function rel(d: number, m: number) {
  const r = new Rng(4)
  const v = pairDists(Array.from({ length: m }, () => Array.from({ length: d }, () => r.next())))
  const mu = v.reduce((a, b) => a + b, 0) / v.length
  return v.map((x) => x / mu)
}
const spread = (v: number[]) => Math.sqrt(v.reduce((a, b) => a + (b - 1) ** 2, 0) / v.length)
function hist(v: number[], color: string, dash?: string) {
  const h = histogram(v, E), w = E[1] - E[0], tot = v.length * w
  return { points: h.flatMap((c, j) => [[E[j], c / tot], [E[j + 1], c / tot]] as [number, number][]), color, width: 2, dash }
}
const c2 = computed(() => rel(2, Math.round(n.value)))
const cD = computed(() => rel(D.value, Math.round(n.value)))
const ymax = computed(() => { const h = histogram(cD.value, E); return 1.08 * Math.max(...h) / (cD.value.length * (E[1] - E[0])) })
const GRIDD = [1, 2, 3, 5, 8, 13, 20, 32, 50, 80, 130, 200, 320, 500, 1000]
const curve = computed(() => GRIDD.map((d) => [d, spread(rel(d, 60))] as [number, number]))
const sNow = computed(() => spread(cD.value))
const ratio = computed(() => Math.min(...cD.value) > 0 ? Math.max(...cD.value) / Math.min(...cD.value) : Infinity)
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> random points drawn uniformly in the cube [0, 1]<sup>d</sup>. <b>Left:</b> the histogram of all their pairwise distances, each divided by the mean distance, for d = 2 and for the chosen d. <b>Right:</b> how widely those distances spread around their mean (std / mean) as the dimension d grows.</div>
    <div class="r2">
      <LineChart :series="[hist(c2, GREEN, '5 4'), hist(cD, RED)]" :x-domain="[0, 2.2]" :y-domain="[0, ymax]"
        :x-ticks="[0, 0.5, 1, 1.5, 2]" :y-ticks="[]" x-label="distance / mean distance"
        :title="`distances between ${Math.round(n)} random points: d = 2 (dashed), d = ${D}`" />
      <LineChart :series="[{ points: curve, color: RED, width: 2.2 }]" :dots="[{ x: D, y: sNow, color: RED, r: 5 }]"
        log-x :x-domain="[1, 1000]" :y-domain="[0, 0.6]" :x-ticks="[1, 10, 100, 1000]" :y-ticks="[0, 0.2, 0.4, 0.6]"
        x-label="dimension d" y-label="spread (std / mean)" title="how much the distances differ" />
    </div>
    <div class="foot">In {{ D }} dimensions the farthest pair is only <b>{{ ratio.toFixed(1) }}×</b> farther than the nearest one:
      "near" and "far" lose their meaning, and a map has little contrast left to keep.</div>
    <div class="controls">
      <Knob v-model="dim" :min="1" :max="1000" log label="dimension d" :color="RED" />
      <Knob v-model="n" :min="20" :max="200" :step="1" :digits="0" label="number of points" :color="GREEN" />
    </div>
  </div>
</template>
