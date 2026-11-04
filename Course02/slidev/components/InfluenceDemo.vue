<!-- influence_demo: drag one point up and down and watch the slope. Least
     squares follows it forever, Huber's pull is bounded, Tukey lets go. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { fitLine, fmt, irls, wHuber, wTukey } from '../lib/reg'
import { lineSeg } from '../lib/draw'
import { BLUE, GOLD, GRID, INK, MUTED, RED } from '../lib/theme'

const rng = new Rng(31)
const x = Array.from({ length: 17 }, (_, i) => -3 + (6 * i) / 16)
const y0 = x.map((v) => 0.6 + 1.1 * v + rng.normal(0, 0.45))
const MOVED = 13
const ty = ref(9)
const withY = (t: number) => y0.map((v, i) => (i === MOVED ? t : v))
const methods = [
  { name: 'least squares', color: GOLD, fit: (yy: number[]) => fitLine(x, yy) },
  { name: 'Huber', color: BLUE, fit: (yy: number[]) => irls(x, yy, (e) => wHuber(e, 1.345), 20).at(-1)!.beta },
  { name: 'Tukey', color: RED, fit: (yy: number[]) => irls(x, yy, (e) => wTukey(e, 4.685), 30).at(-1)!.beta },
]
const fits = computed(() => methods.map((m) => m.fit(withY(ty.value))))
const POS = Array.from({ length: 80 }, (_, i) => -12 + (26 * i) / 79)
const curves = methods.map((m) => POS.map((p) => [p, m.fit(withY(p))[1]] as [number, number]))
const others = x.map((v, i) => [v, y0[i]] as [number, number]).filter((_, i) => i !== MOVED)
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Plane :X="others" :colors="INK" :size="3.5" :alpha="0.6" :domain="[-3.5, 3.9, -12.5, 14.5]" :equal="false"
        :segments="methods.map((m, k) => lineSeg(fits[k], -3.5, 3.9, m.color, 2.4, k === 1 ? [7, 4] : []))"
        :markers="[{ at: [x[MOVED], ty], color: INK, shape: 'dot', size: 7 }]" title="influence of a point on the fit" />
      <LineChart :series="methods.map((m, k) => ({ points: curves[k], color: m.color, width: 2.6, dash: k === 0 ? '6,4' : '' }))"
        :hlines="[{ y: 1.1, color: GRID, dash: '2,3' }]" :vlines="[{ x: ty, color: INK, dash: '4,3' }]"
        :dots="methods.map((m, k) => ({ x: ty, y: fits[k][1], color: m.color, r: 5.5 }))"
        :labels="methods.map((m, k) => ({ x: 14.4, y: curves[k][79][1] + [0, 0.05, -0.05][k], text: m.name, color: m.color, size: 12 }))"
        :x-domain="[-12, 19]" :y-domain="[0.4, 1.9]" :x-ticks="[-10, -5, 0, 5, 10]" :y-ticks="[0.5, 1, 1.5]" x-label="y value of the moved point" y-label="slope β̂₁" title="influence" />
    </div>
    <div class="foot">slopes: <b :style="{ color: GOLD }">{{ fmt(fits[0][1]) }}</b> least squares, <b :style="{ color: BLUE }">{{ fmt(fits[1][1]) }}</b> Huber, <b :style="{ color: RED }">{{ fmt(fits[2][1]) }}</b> Tukey (truth 1.1)</div>
    <div class="controls">
      <Knob v-model="ty" :min="-12" :max="14" :step="0.05" label="the moved point's y" :color="INK" />
    </div>
  </div>
</template>
