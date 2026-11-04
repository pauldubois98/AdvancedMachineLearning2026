<!-- init_random: the map at t = 0. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { TOY, TOY_DOMAIN } from '../lib/data'
import { Rng } from '../lib/rng'
import { span, stripDots } from '../lib/strip'
import { COMP, HIGH, LOW, MUTED } from '../lib/theme'

const seed = ref(1)
const scale = ref(1e-4)
const Y = computed(() => { const r = new Rng(Math.round(seed.value)); return TOY.X.map(() => r.normal(0, scale.value)) })
const lim = computed(() => span(Y.value))
const SUP: Record<string, string> = { '-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹' }
const fmtE = (v: number) => { const [m, e] = v.toExponential(1).split('e'); const ex = String(Number(e)); return ex === '0' ? m : `${m} × 10${[...ex].map((c) => SUP[c]).join('')}` }
</script>

<template>
  <div class="cmp">
    <div class="r23">
      <Plane :X="TOY.X" :colors="TOY.g.map((k) => COMP[k])" :size="5" :domain="TOY_DOMAIN" title="data" :title-color="HIGH" />
      <LineChart :series="[{ points: [[lim[0], 0], [lim[1], 0]], color: '#cccfd2', width: 1.5 }]" :dots="stripDots(Y, TOY.g)"
        :x-domain="lim" :y-domain="[-0.6, 0.6]" :x-ticks="[]" :y-ticks="[]" :axes="false"
        :labels="[{ x: lim[0], y: -0.45, text: lim[0].toPrecision(2), color: MUTED, anchor: 'start' }, { x: lim[1], y: -0.45, text: lim[1].toPrecision(2), color: MUTED, anchor: 'end' }]"
        :title="`the map at t = 0: yᵢ ~ N(0, σ₀²), σ₀ = ${fmtE(scale)}`" :title-color="LOW" />
    </div>
    <div class="foot">Every point starts within a hair of 0, in a random order: the map knows nothing yet.<br>
      Tiny on purpose, so that no structure is imposed and the first moves are free to set the order.</div>
    <div class="controls">
      <Knob v-model="seed" :min="1" :max="30" :step="1" :digits="0" label="seed" :color="LOW" />
      <Knob v-model="scale" :min="1e-4" :max="1" log label="start spread σ₀" :color="LOW" />
    </div>
  </div>
</template>
