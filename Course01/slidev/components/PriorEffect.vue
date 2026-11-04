<!-- prior_effect: with few points the prior pulls the posterior; with many,
     the likelihood takes over. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve } from '../lib/hist'
import { mean, normals, npdf } from '../lib/stats'
import { BLUE, GREEN, MUTED, PURPLE } from '../lib/theme'

const n = ref(3)
const ps = ref(0.8)
const SD = 1.2, PM = 0, TRUE = 2.5
const all = normals(new Rng(2), 1000, TRUE, SD)
const N = computed(() => Math.round(n.value))
const xb = computed(() => mean(all.slice(0, N.value)))
const ls = computed(() => SD / Math.sqrt(N.value))
const post = computed(() => {
  const a = 1 / ps.value ** 2, b = 1 / ls.value ** 2
  return { m: (a * PM + b * xb.value) / (a + b), s: 1 / Math.sqrt(a + b), wp: a / (a + b) }
})
// each curve scaled to height 1, as the printed figure draws them
const bump = (m: number, s: number) => curve((t) => Math.exp(-0.5 * ((t - m) / s) ** 2), -1.5, 5, 500)
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> the first n points of one stream from N(2.5, 1.2²) (the dotted line is the true 2.5). The prior N(0, prior sd²) is wrong on purpose. Each curve is scaled to height 1.</div>
    <LineChart :series="[{ points: bump(PM, ps), color: BLUE }, { points: bump(xb, ls), color: GREEN }, { points: bump(post.m, post.s), color: PURPLE, width: 3 }]"
      :x-domain="[-1.5, 5]" :y-domain="[0, 1.12]" :x-ticks="[-1, 0, 1, 2, 3, 4, 5]" :y-ticks="[]" x-label="μ"
      :vlines="[{ x: TRUE, color: MUTED, dash: '2,3' }]"
      :labels="[{ x: -1.4, y: 1.04, text: 'prior', color: BLUE }, { x: -0.7, y: 1.04, text: 'likelihood', color: GREEN }, { x: 0.35, y: 1.04, text: 'posterior', color: PURPLE }]" />
    <div class="foot">n = <b>{{ N }}</b>: the prior carries <b :style="{ color: BLUE }">{{ (100 * post.wp).toFixed(0) }}%</b> of the weight; posterior mean <b :style="{ color: PURPLE }">{{ post.m.toFixed(2) }}</b> vs x̄ = <b :style="{ color: GREEN }">{{ xb.toFixed(2) }}</b>. As n grows the prior stops mattering; a narrow prior holds out longer.</div>
    <div class="controls">
      <Knob v-model="n" :min="1" :max="1000" log :step="0.01" label="n" :color="GREEN" />
      <Knob v-model="ps" :min="0.05" :max="5" log label="prior sd" :color="BLUE" />
    </div>
  </div>
</template>
