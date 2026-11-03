<!-- bo_acquisition: where to spend the next fit. Expected improvement and the
     confidence bound read the surrogate's mean (exploit) and band (explore);
     the dashed lines are their two recommendations. kappa trades the two. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmax, boTarget, ei, gp, linspace, ucb } from '../lib/c08'
import { BLUE, GOLD, GREEN, INK, MUTED, PURPLE } from '../lib/theme'

const XS = [0.08, 0.30, 0.42, 0.86, 0.65, 0.18, 0.97]
const n = ref(4)
const kappa = ref(2)
const xi = ref(0)
const G = linspace(0, 1, 300)
const xs = computed(() => XS.slice(0, n.value))
const ys = computed(() => xs.value.map(boTarget))
const post = computed(() => gp(xs.value.map((x) => [x]), ys.value, G.map((x) => [x]), [0.15]))
const best = computed(() => Math.min(...ys.value))
const norm = (v: number[]) => { const lo = Math.min(...v); const hi = Math.max(...v); return v.map((x) => (x - lo) / Math.max(hi - lo, 1e-12)) }
const eiV = computed(() => norm(post.value.mu.map((m, i) => ei(m, post.value.sd[i], best.value, xi.value))))
const ucbV = computed(() => norm(post.value.mu.map((m, i) => ucb(m, post.value.sd[i], kappa.value))))
const eiX = computed(() => G[argmax(eiV.value)])
const ucbX = computed(() => G[argmax(ucbV.value)])
</script>

<template>
  <div class="wrap">
    <div class="note top">Where to spend the next fit: exploit the mean, or explore the band</div>
    <div class="charts">
      <LineChart
        :series="[{ points: G.map((x, i) => [x, post.mu[i]] as [number, number]), color: BLUE, width: 2.6 }]"
        :ribbons="[{ points: G.map((x, i) => [x, post.mu[i] - 2 * post.sd[i], post.mu[i] + 2 * post.sd[i]] as [number, number, number]), color: BLUE, alpha: 0.15 }]"
        :dots="xs.map((x, i) => ({ x, y: ys[i], color: INK, r: 6 }))"
        :hlines="[{ y: best, color: MUTED, dash: '2 3' }]"
        :vlines="[{ x: eiX, color: GREEN, dash: '5 4' }, { x: ucbX, color: PURPLE, dash: '5 4' }]"
        :labels="[{ x: 0.99, y: best + 0.2, text: 'best f* so far', color: MUTED, size: 12, anchor: 'end' }]"
        :x-domain="[0, 1]" :y-domain="[-1.5, 2.3]" :x-ticks="[]" :y-ticks="[-1, 0, 1, 2]" y-label="validation loss"
        :pad="{ l: 46, r: 14, t: 8, b: 8 }" :unit-height="240"
      />
      <LineChart
        :series="[{ points: G.map((x, i) => [x, eiV[i]] as [number, number]), color: GREEN, width: 2.6 }, { points: G.map((x, i) => [x, ucbV[i]] as [number, number]), color: PURPLE, width: 2.6 }]"
        :vlines="[{ x: eiX, color: GREEN, dash: '5 4' }, { x: ucbX, color: PURPLE, dash: '5 4' }]"
        :labels="[{ x: 0.02, y: 0.95, text: 'expected improvement', color: GREEN, size: 12 }, { x: 0.3, y: 0.95, text: `UCB (κ = ${kappa.toFixed(1)})`, color: PURPLE, size: 12 }]"
        :x-domain="[0, 1]" :y-domain="[0, 1.12]" :x-ticks="[0, 0.2, 0.4, 0.6, 0.8, 1]" :y-ticks="[]" x-label="hyper-parameter x" y-label="acquisition"
        :unit-height="150"
      />
    </div>
    <div class="msg">Maximise the acquisition, never the expensive function itself. Small κ exploits the low mean; large κ explores the wide band.</div>
    <div class="controls">
      <Knob v-model="kappa" :min="0" :max="6" :step="0.1" :digits="1" label="UCB κ" :color="PURPLE" />
      <Knob v-model="xi" :min="0" :max="0.5" :step="0.01" label="EI margin ξ" :color="GREEN" />
      <Knob v-model="n" :min="1" :max="7" :step="1" :digits="0" label="measured points" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.3rem; height: 100%; min-height: 0; }
.top, .msg { text-align: center; }
.msg { font-size: 0.82rem; }
.charts { display: grid; grid-template-rows: 1.6fr 1fr; min-height: 0; }
</style>
