<!-- pca_nonlinear: the swiss roll, turned as you like; PCA flattens it, and
     how badly depends on how long the roll is. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { swissRoll } from '../lib/data'
import { pca } from '../lib/sne'
import { GREEN, HIGH, PCA_C, rgb, viridis } from '../lib/theme'
import type { Pt } from '../lib/geom'

const stretch = ref(1.6)
const az = ref(-35)
const roll = computed(() => swissRoll(600, stretch.value))
const tmin = 1.5 * Math.PI, tmax = 4.5 * Math.PI
const cols = computed(() => roll.value.t.map((t) => rgb(viridis((t - tmin) / (tmax - tmin)))))
const view = computed<Pt[]>(() => {
  // the spiral stands upright (x, z), the length of the roll runs into depth
  const a = (az.value * Math.PI) / 180, e = (20 * Math.PI) / 180
  const hc = 10.5 * stretch.value
  return roll.value.X.map(([x, h, z]) => {
    const xs = x * Math.cos(a) + (h - hc) * Math.sin(a)
    const depth = -x * Math.sin(a) + (h - hc) * Math.cos(a)
    return [xs, z * Math.cos(e) + depth * Math.sin(e)]
  })
})
const fit = computed(() => pca(roll.value.X, 2))
const Zp = computed<Pt[]>(() => fit.value.Z.map((z) => [z[0], z[1]]))
const unrolled = computed<Pt[]>(() => roll.value.X.map((x, i) => [roll.value.t[i], x[1]]))
const dom = (P: Pt[], pad = 0.06): [number, number, number, number] => {
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity
  for (const [x, y] of P) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y) }
  const px = (x1 - x0) * pad, py = (y1 - y0) * pad
  return [x0 - px, x1 + px, y0 - py, y1 + py]
}
const share = computed(() => { const v = fit.value.values; return (v[0] + v[1]) / (v[0] + v[1] + v[2]) })
</script>

<template>
  <div class="cmp">
    <div class="r3">
      <Plane :X="view" :colors="cols" :size="2.4" :domain="dom(view)" title="the swiss roll in 3-D" :title-color="HIGH" />
      <Plane :X="Zp" :colors="cols" :size="2.4" :domain="dom(Zp)" title="PCA: the best plane" :title-color="PCA_C" />
      <Plane :X="unrolled" :colors="cols" :size="2.4" :domain="dom(unrolled)" :equal="false" title="what we would like: unrolled" :title-color="GREEN" />
    </div>
    <div class="foot">Colour = position along the roll. PCA keeps {{ (100 * share).toFixed(0) }}% of the variance, yet it lays
      far-apart turns of the roll on top of each other: no plane can unroll it.</div>
    <div class="controls">
      <Knob v-model="stretch" :min="0.4" :max="2.5" :step="0.05" label="length of the roll" :color="HIGH" />
      <Knob v-model="az" :min="-180" :max="180" :step="1" :digits="0" label="turn the 3-D view" unit="°" :color="HIGH" />
    </div>
  </div>
</template>
