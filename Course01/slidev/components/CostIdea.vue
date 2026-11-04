<!-- cost_idea: a posterior is a whole distribution; to report one number,
     choose the answer whose expected cost is smallest. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { GOLD, GREEN, PURPLE, RED } from '../lib/theme'
import { postGrid } from '../lib/post'

const a = ref(2.6)
const P = postGrid(0.65, 1.6, 0.75, 3.8, 0.55)
const cost = {
  sq: (t: number, v: number) => (t - v) ** 2,
  abs: (t: number, v: number) => Math.abs(t - v),
  zo: (t: number, v: number) => (Math.abs(t - v) > 0.12 ? 1 : 0),
}
const risk = (c: (t: number, v: number) => number, v: number) => P.grid.reduce((s, t, i) => s + c(t, v) * P.p[i], 0)
const curves = Object.fromEntries(Object.entries(cost).map(([k, c]) => [k, curve((v) => risk(c, v), -1.5, 6, 150)])) as Record<string, [number, number][]>
const mins = Object.fromEntries(Object.entries(curves).map(([k, c]) => [k, c.reduce((p, q) => (q[1] < p[1] ? q : p))[0]]))
const norm = (c: [number, number][]) => { const m = Math.max(...c.map((p) => p[1])); return c.map(([x, y]) => [x, y / m] as [number, number]) }
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>The posterior</b> p(θ | x) here has two bumps. Slide the answer θ̂; c(θ̂, a) is what it costs to answer θ̂ when the truth is a, and the right panel shows each cost averaged over the posterior (rescaled to 1).</div>
    <div class="r2">
      <LineChart :series="[{ points: P.curve, color: PURPLE }]" :ribbons="[{ points: P.curve.map(([x, y]) => [x, 0, y]), color: PURPLE, alpha: 0.12 }]"
        :x-domain="[-1.5, 6]" :y-domain="[0, P.top * 1.15]" :x-ticks="[0, 2, 4, 6]" :y-ticks="[]" x-label="θ"
        :vlines="[{ x: a, color: GREEN, dash: '' }]" :labels="[{ x: a + 0.1, y: P.top * 1.05, text: 'answer θ̂', color: GREEN }]" title="θ's distribution" :title-color="PURPLE" />
      <LineChart :series="[{ points: norm(curves.sq), color: GREEN }, { points: norm(curves.abs), color: GOLD }, { points: norm(curves.zo), color: RED }]"
        :x-domain="[-1.5, 6]" :y-domain="[0, 1.05]" :x-ticks="[0, 2, 4, 6]" :y-ticks="[0, 0.5, 1]" x-label="the answer θ̂"
        :vlines="[{ x: a, color: GREEN, dash: '' }]" :dots="[{ x: mins.sq, y: 0, color: GREEN, r: 5 }, { x: mins.abs, y: 0, color: GOLD, r: 5 }, { x: mins.zo, y: 0, color: RED, r: 5 }]"
        title="expected cost ∫ c(θ̂, a) p(a | x) da" />
    </div>
    <div class="foot">at θ̂ = {{ a.toFixed(2) }}: <b :style="{ color: GREEN }">squared {{ risk(cost.sq, a).toFixed(2) }}</b> · <b :style="{ color: GOLD }">absolute {{ risk(cost.abs, a).toFixed(2) }}</b> · <b :style="{ color: RED }">0-1 {{ risk(cost.zo, a).toFixed(2) }}</b>. Each cost has its own best answer (the dots): θ̂ = arg min ∫ c(θ̂, a) p(a | x) da.</div>
    <div class="controls"><Knob v-model="a" :min="-1" :max="5.5" :step="0.01" label="answer θ̂" :color="GREEN" /></div>
  </div>
</template>
