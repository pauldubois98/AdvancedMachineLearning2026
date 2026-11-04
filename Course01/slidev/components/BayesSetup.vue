<!-- bayes_setup: prior × likelihood ∝ posterior, Gaussian and conjugate, so
     every curve is exact. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve } from '../lib/hist'
import { mean, normals, npdf } from '../lib/stats'
import { BLUE, GREEN, PURPLE } from '../lib/theme'

const pm = ref(0.8)
const ps = ref(1.0)
const n = ref(3)
const SD = 1.2
const all = normals(new Rng(2), 200, 3, SD)
const xb = computed(() => mean(all.slice(0, n.value)))
const ls = computed(() => SD / Math.sqrt(n.value))
const post = computed(() => {
  const a = 1 / ps.value ** 2, b = 1 / ls.value ** 2
  return { m: (a * pm.value + b * xb.value) / (a + b), s: 1 / Math.sqrt(a + b) }
})
const top = computed(() => Math.max(npdf(0, 0, ps.value), npdf(0, 0, ls.value), npdf(0, 0, post.value.s)) * 1.1)
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> n points from N(θ = 3, 1.2²), the mean θ unknown. Before the data, we believe θ ~ N(prior mean, prior sd²). The posterior combines that belief with the likelihood of the data.</div>
    <LineChart :series="[{ points: curve((t) => npdf(t, pm, ps), -1, 5), color: BLUE }, { points: curve((t) => npdf(t, xb, ls), -1, 5), color: GREEN }, { points: curve((t) => npdf(t, post.m, post.s), -1, 5), color: PURPLE, width: 3 }]"
      :ribbons="[{ points: curve((t) => npdf(t, post.m, post.s), -1, 5).map(([x, y]) => [x, 0, y]), color: PURPLE, alpha: 0.12 }]"
      :x-domain="[-1, 5]" :y-domain="[0, top]" :x-ticks="[-1, 0, 1, 2, 3, 4, 5]" :y-ticks="[]" x-label="θ"
      :labels="[{ x: -0.85, y: top * 0.93, text: 'prior p(θ)', color: BLUE }, { x: -0.85, y: top * 0.84, text: 'likelihood L(x; θ), rescaled', color: GREEN }, { x: -0.85, y: top * 0.75, text: 'posterior p(θ | x)', color: PURPLE }]" />
    <div class="foot">posterior mean <b :style="{ color: PURPLE }">{{ post.m.toFixed(2) }}</b>, between the prior mean <b :style="{ color: BLUE }">{{ pm.toFixed(2) }}</b> and x̄ = <b :style="{ color: GREEN }">{{ xb.toFixed(2) }}</b>, weighted by how sure each one is (sd {{ ps.toFixed(2) }} vs {{ ls.toFixed(2) }})</div>
    <div class="controls">
      <Knob v-model="pm" :min="-1" :max="5" :step="0.05" label="prior mean" :color="BLUE" />
      <Knob v-model="ps" :min="0.1" :max="5" log label="prior sd" :color="BLUE" />
      <Knob v-model="n" :min="1" :max="200" :step="1" :digits="0" label="n" :color="GREEN" />
    </div>
  </div>
</template>
