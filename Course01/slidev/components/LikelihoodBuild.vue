<!-- likelihood_build: the likelihood of a candidate θ is the product of the
     density heights at the data points. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve, sci } from '../lib/hist'
import { normals, npdf } from '../lib/stats'
import { GREEN, INK, PURPLE, RED } from '../lib/theme'

const th = ref(0.3)
const x = normals(new Rng(19), 7, 2, 1)
const L = (m: number) => x.reduce((p, v) => p * npdf(v, m, 1), 1)
const Lc = curve(L, -1, 5)
const Lmax = Math.max(...Lc.map((p) => p[1]))
const best = Lc.reduce((a, b) => (b[1] > a[1] ? b : a))[0]
const good = computed(() => L(th.value) > 0.3 * Lmax)
const col = computed(() => (good.value ? GREEN : RED))
const dens = computed(() => curve((t) => npdf(t, th.value, 1), -2, 6))
const heights = computed(() => x.map((v) => npdf(v, th.value, 1)))
const segs = computed(() => x.map((v, i) => ({ points: [[v, 0], [v, heights.value[i]]] as [number, number][], color: col.value, width: 1.4 })))
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 7 points (the black ticks) from N(2, 1). The candidate model is N(θ, 1); each point contributes the height of its density at that point, and L(θ) is the product of the 7 heights.</div>
    <div class="r2">
      <LineChart :series="[{ points: dens, color: col }, ...segs]" :x-domain="[-2, 6]" :y-domain="[0, 0.46]" :x-ticks="[-2, 0, 2, 4, 6]" :y-ticks="[]" x-label="x"
        :dots="[...x.map((v, i) => ({ x: v, y: heights[i], color: col, r: 4 })), ...x.map((v) => ({ x: v, y: 0.004, color: INK, r: 2.5 }))]"
        :title="`the model N(θ = ${th.toFixed(2)}, 1)`" :title-color="col" />
      <LineChart :series="[{ points: Lc, color: PURPLE }]" :x-domain="[-1, 5]" :y-domain="[0, Lmax * 1.1]" :x-ticks="[0, 2, 4]" :y-ticks="[]" x-label="θ"
        :dots="[{ x: th, y: L(th), color: col, r: 6 }]" :vlines="[{ x: th, color: col, dash: '4,3' }]" title="L(θ)" :title-color="PURPLE" />
    </div>
    <div class="foot">L = ∏ f(xᵢ; θ) = <b :style="{ color: col }">{{ sci(L(th)) }}</b> &nbsp;·&nbsp; ℓ = Σ log f(xᵢ; θ) = <b :style="{ color: col }">{{ Math.log(L(th)).toFixed(1) }}</b> &nbsp;·&nbsp; the best θ is {{ best.toFixed(2) }}, the sample mean</div>
    <div class="controls"><Knob v-model="th" :min="-1" :max="5" :step="0.01" label="candidate θ" :color="col" /></div>
  </div>
</template>
