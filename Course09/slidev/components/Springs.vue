<!-- sne_forces: the springs on the followed point at move t. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { TOY, toyP } from '../lib/data'
import { TOY_ITERS, toyRun } from '../lib/toyrun'
import { forcesOn } from '../lib/sne'
import { span, stripDots } from '../lib/strip'
import { COMP, GREEN, INK, RED } from '../lib/theme'

const t = ref(40)
const i = TOY.star
const run = toyRun()
const st = computed(() => run.emb(Math.round(t.value)))
const y = computed(() => Array.from(st.value.Y))
const lim = computed(() => span(y.value, 0.1))
const { P } = toyP()
const f = computed(() => forcesOn(st.value, i))
const pick = computed(() => {
  const n = y.value.length
  const idx = f.value.map((_, j) => j).filter((j) => j !== i)
  const pull = idx.filter((j) => P[i * n + j] > st.value.Q[i * n + j]).sort((a, b) => Math.abs(f.value[b]) - Math.abs(f.value[a])).slice(0, 4)
  const push = idx.filter((j) => P[i * n + j] <= st.value.Q[i * n + j]).sort((a, b) => Math.abs(f.value[b]) - Math.abs(f.value[a])).slice(0, 4)
  return [...pull, ...push].sort((a, b) => y.value[a] - y.value[b])
})
const w = computed(() => lim.value[1] - lim.value[0])
const scale = computed(() => (0.3 * w.value) / Math.max(1e-30, ...pick.value.map((j) => Math.abs(f.value[j]))))
const arrows = computed(() => {
  const n = y.value.length
  const out = pick.value.map((j, r) => ({ x0: y.value[i], y0: 0.55 + r * 0.21, x1: y.value[i] + f.value[j] * scale.value, y1: 0.55 + r * 0.21,
    color: P[i * n + j] > st.value.Q[i * n + j] ? GREEN : RED, width: 2 }))
  const net = f.value.reduce((s, v) => s + v, 0)
  out.push({ x0: y.value[i], y0: -0.55, x1: y.value[i] + Math.sign(net) * 0.18 * w.value, y1: -0.55, color: INK, width: 3.2 })
  return out
})
const heads = computed(() => pick.value.map((j, r) => ({ x: y.value[j], y: 0.55 + r * 0.21, color: COMP[TOY.g[j]], r: 4.5 })))
</script>

<template>
  <div class="cmp">
    <LineChart :series="[{ points: [[lim[0], 0], [lim[1], 0]], color: '#cccfd2', width: 1.5 }]" :dots="[...stripDots(y, TOY.g, i), ...heads]" :arrows="arrows"
      :vlines="[{ x: y[i], color: RED, dash: '2 3' }]" :x-domain="lim" :y-domain="[-0.8, 2.4]" :axes="false"
      :labels="[{ x: y[i], y: -0.75, text: 'the sum of all 44 springs: the move of the star', color: INK }]"
      :title="`move ${Math.round(t)}: the star's four strongest pulls and pushes`" />
    <div class="foot">One spring per pair: p<sub>ij</sub> &gt; q<sub>ij</sub> pulls the points together (green),
      p<sub>ij</sub> &lt; q<sub>ij</sub> pushes them apart (red); force ∝ (p<sub>ij</sub> − q<sub>ij</sub>)(y<sub>j</sub> − y<sub>i</sub>).</div>
    <div class="controls"><Knob v-model="t" :min="0" :max="TOY_ITERS" :step="1" :digits="0" label="move t" :color="INK" /></div>
  </div>
</template>
