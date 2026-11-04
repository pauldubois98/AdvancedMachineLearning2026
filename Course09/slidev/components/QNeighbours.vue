<!-- q_neighbours: the map's bell on the followed point, at move t. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { TOY, TOY_D, TOY_N, toyP } from '../lib/data'
import { TOY_ITERS, toyRun } from '../lib/toyrun'
import { span, stripDots } from '../lib/strip'
import { HIGH, LOW, RED } from '../lib/theme'
import { linspace } from '../lib/geom'

const t = ref(0)
const i = TOY.star
const run = toyRun()
const Y = computed(() => run.Y[Math.round(t.value)])
const lim = span(run.Y[50], 0.08)
const q = computed(() => {
  const w = Y.value.map((v, j) => (j === i ? 0 : Math.exp(-((v - Y.value[i]) ** 2))))
  const s = w.reduce((a, b) => a + b, 0)
  return w.map((v) => v / s)
})
const { Pc } = toyP()
const order = Array.from({ length: TOY_N }, (_, j) => j).filter((j) => j !== i).sort((a, b) => TOY_D[i * TOY_N + a] - TOY_D[i * TOY_N + b])
const pmax = Math.max(...order.map((j) => Pc[i * TOY_N + j]))
const bars = computed(() => [
  ...order.map((j, k) => ({ x: k, y: Pc[i * TOY_N + j], w: 0.8, color: HIGH, alpha: 0.3 })),
  ...order.map((j, k) => ({ x: k, y: q.value[j], w: 0.4, color: LOW, alpha: 1 })),
])
const bell = computed(() => linspace(lim[0], lim[1], 400).map((u) => [u, 0.42 * Math.exp(-((u - Y.value[i]) ** 2)) - 0.02] as [number, number]))
const inside = computed(() => Y.value.filter((v) => Math.abs(v - Y.value[i]) < 1).length - 1)
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <LineChart :series="[{ points: [[lim[0], 0], [lim[1], 0]], color: '#cccfd2', width: 1.5 }, { points: bell, color: RED, width: 1.6 }]"
        :ribbons="[{ points: bell.map(([x, y]) => [x, -0.02, y]), color: RED, alpha: 0.1 }]"
        :dots="stripDots(Y, TOY.g, i)" :x-domain="lim" :y-domain="[-0.5, 0.5]" :axes="false"
        :title="`the map at move ${Math.round(t)}: the bell of fixed width 1/√2`" :title-color="LOW" />
      <LineChart :series="[]" :bars="bars" :x-domain="[-1, 44]" :y-domain="[0, pmax * 1.1]" :x-ticks="[]" :y-ticks="[]"
        :labels="[{ x: 30, y: pmax, text: 'pⱼ|ᵢ (data)', color: HIGH }, { x: 30, y: pmax * 0.88, text: 'qⱼ|ᵢ (map)', color: LOW }]"
        x-label="neighbours of the star, nearest in the data first" title="what the map says vs what the data say" />
    </div>
    <div class="foot">q<sub>j|i</sub> ∝ exp(−‖yᵢ − yⱼ‖²): the same bell as in the data, one fixed width. Within one unit of the star:
      <b>{{ inside }}</b> points.<span v-if="Math.round(t) < 30"> At the start all points sit in a spot far narrower than the bell, so every q is 1/44.</span></div>
    <div class="controls"><Knob v-model="t" :min="0" :max="TOY_ITERS" :step="1" :digits="0" label="move t" :color="LOW" /></div>
  </div>
</template>
