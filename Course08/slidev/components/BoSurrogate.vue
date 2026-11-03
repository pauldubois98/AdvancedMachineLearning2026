<!-- bo_surrogate: a few validation losses measured at known hyper-parameters
     (left), and what a Gaussian-process surrogate believes in between
     (right): a best guess, and a band that is tight where measured and wide
     where not. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { boTarget, gp, linspace } from '../lib/c08'
import { BLUE, GOLD, INK, MUTED, PURPLE } from '../lib/theme'

const XS = [0.08, 0.42, 0.88, 0.25, 0.65, 0.55, 0.98, 0.15, 0.75, 0.33]
const n = ref(3)
const ell = ref(0.15)
const showTruth = ref(false)
const G = linspace(0, 1, 240)
const xs = computed(() => XS.slice(0, n.value))
const ys = computed(() => xs.value.map(boTarget))
const post = computed(() => gp(xs.value.map((x) => [x]), ys.value, G.map((x) => [x]), [ell.value]))
const dots = computed(() => xs.value.map((x, i) => ({ x, y: ys.value[i], color: INK, r: 6 })))
const widest = computed(() => G[post.value.sd.indexOf(Math.max(...post.value.sd))])
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="xs.map((x, i) => ({ points: [[x, -1.5], [x, ys[i]]] as [number, number][], color: MUTED, width: 1.2, dash: '2 3' }))"
        :dots="dots" :labels="[{ x: 0.5, y: -1.2, text: 'curve between them is unknown', color: MUTED, size: 12, anchor: 'middle' }]"
        :x-domain="[0, 1]" :y-domain="[-1.5, 2.3]" :x-ticks="[0, 0.2, 0.4, 0.6, 0.8, 1]" :y-ticks="[-1, 0, 1, 2]"
        x-label="hyper-parameter x" y-label="validation loss" title="known numbers"
      />
      <LineChart
        :series="[
          { points: G.map((x, i) => [x, post.mu[i]] as [number, number]), color: BLUE, width: 2.8 },
          ...(showTruth ? [{ points: G.map((x) => [x, boTarget(x)] as [number, number]), color: INK, width: 1.6, dash: '5 4' }] : []),
        ]"
        :ribbons="[{ points: G.map((x, i) => [x, post.mu[i] - 2 * post.sd[i], post.mu[i] + 2 * post.sd[i]] as [number, number, number]), color: BLUE, alpha: 0.15 }]"
        :dots="dots"
        :labels="[
          { x: 0.03, y: 2.05, text: 'mean: the best guess', color: BLUE, size: 12 },
          { x: 0.03, y: 1.8, text: 'band: how wrong it could be (±2 sd)', color: BLUE, size: 12 },
          ...(n > 1 ? [{ x: xs[1], y: ys[1] - 0.45, text: 'tight where measured', color: GOLD, size: 12, anchor: 'middle' }] : []),
          { x: widest, y: -1.35, text: 'wide where not measured', color: PURPLE, size: 12, anchor: 'middle' },
        ]"
        :x-domain="[0, 1]" :y-domain="[-1.5, 2.3]" :x-ticks="[0, 0.2, 0.4, 0.6, 0.8, 1]" :y-ticks="[-1, 0, 1, 2]"
        x-label="hyper-parameter x" title="what the surrogate believes"
      />
    </div>
    <div class="controls">
      <Knob v-model="n" :min="0" :max="10" :step="1" :digits="0" label="measured points" />
      <Knob v-model="ell" :min="0.03" :max="0.6" :step="0.01" label="length-scale ℓ" :color="BLUE" />
      <Toggle v-model="showTruth" label="show the true curve" />
      <span class="note">the surrogate is nearly free to query</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; min-height: 0; }
</style>
