<!-- squared_loss_pull: every residual is squared, so the far point owns most of
     the loss. Compare with |e|, which grows only linearly. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { fitLine, fmt, outlierBase } from '../lib/reg'
import { BLUE, GREEN, RED } from '../lib/theme'

const base = outlierBase(7)
const oy = ref(-5.4)
const kind = ref('sq')
const rho = (e: number) => (kind.value === 'sq' ? 0.5 * e * e : Math.abs(e))
const fit = computed(() => fitLine([...base.x, 2.35], [...base.y, oy.value]))
const res = computed(() => [...base.x, 2.35].map((v, i) => [...base.y, oy.value][i] - fit.value[0] - fit.value[1] * v))
const share = computed(() => { const l = res.value.map(rho), s = l.reduce((a, b) => a + b, 0); return l.map((v) => v / s) })
const span = computed(() => Math.max(...res.value.map(Math.abs)) * 1.1)
const order = computed(() => share.value.map((v, i) => [v, i]).sort((a, b) => b[0] - a[0]))
const bars = computed(() => order.value.map(([v, i], k) => ({ x: k, y: v, w: 0.8, color: i === 26 ? RED : BLUE, alpha: 0.9 })))
const col = computed(() => (kind.value === 'sq' ? RED : GREEN))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <LineChart :series="[{ points: curve(rho, -span, span), color: col, width: 2.8 }]"
        :dots="res.map((e, i) => ({ x: e, y: rho(e), color: i === 26 ? RED : BLUE, r: i === 26 ? 7 : 4 }))"
        :x-domain="[-span, span]" :y-domain="[0, rho(span)]" :x-ticks="[-4, -2, 0, 2, 4].filter((t) => Math.abs(t) < span)" :y-ticks="[]"
        x-label="residual eᵢ (from the least squares fit)" :y-label="kind === 'sq' ? 'ρ(e) = e²/2' : 'ρ(e) = |e|'" title="every residual goes through ρ" />
      <LineChart :series="[]" :bars="bars" :x-domain="[-0.8, 26.8]" :y-domain="[0, Math.max(0.2, share[26] * 1.15, order[0][0] * 1.15)]" :y-ticks="[0, 0.2, 0.4, 0.6, 0.8]"
        x-label="the 27 points, sorted" y-label="share of the total loss" title="who owns the loss" />
    </div>
    <div class="foot">the moved point carries <b :style="{ color: RED }">{{ fmt(100 * share[26], 0) }} %</b> of the {{ kind === 'sq' ? 'squared' : 'absolute' }} loss. {{ kind === 'sq' ? 'Twice as far away, four times as loud: least squares can not ignore a point.' : 'Twice as far away, twice as loud.' }}</div>
    <div class="controls">
      <Knob v-model="oy" :min="-10" :max="6" :step="0.05" label="the far point's y" :color="RED" />
      <Choice v-model="kind" :options="[{ value: 'sq', label: 'squared e²/2', color: RED }, { value: 'abs', label: 'absolute |e|', color: GREEN }]" />
    </div>
  </div>
</template>
