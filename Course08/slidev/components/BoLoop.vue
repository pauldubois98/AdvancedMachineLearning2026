<!-- bo_loop: the loop, run. Fit the surrogate on the trials so far, maximise
     the acquisition, evaluate there for real, add the result, and start
     again. The slider steps through the passes from three random starts. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmax, boTarget, ei, gp, linspace, ucb } from '../lib/c08'
import { Rng } from '../lib/rng'
import { BLUE, GOLD, GREEN, INK, MUTED, RED } from '../lib/theme'

const t = ref(0)
const acq = ref('ei')
const nStart = ref(3)
const seed = ref(3)
const T = 15
const G = linspace(0, 1, 300)
const TRUE_MIN = Math.min(...G.map(boTarget))
const run = computed(() => {
  const rng = new Rng(seed.value)
  const xs = Array.from({ length: nStart.value }, () => rng.next())
  const steps: { xs: number[]; mu: number[]; sd: number[]; a: number[]; next: number }[] = []
  for (let s = 0; s <= T; s++) {
    const ys = xs.map(boTarget)
    const post = gp(xs.map((x) => [x]), ys, G.map((x) => [x]), [0.12])
    const best = Math.min(...ys)
    const a = acq.value === 'ei'
      ? post.mu.map((m, i) => ei(m, post.sd[i], best))
      : post.mu.map((m, i) => ucb(m, post.sd[i], 2))
    const lo = Math.min(...a), hi = Math.max(...a)
    const next = G[argmax(a)]
    steps.push({ xs: [...xs], ...post, a: a.map((v) => (v - lo) / Math.max(hi - lo, 1e-12)), next })
    xs.push(next)
  }
  return steps
})
const st = computed(() => run.value[t.value])
const best = computed(() => Math.min(...st.value.xs.map(boTarget)))
const BOXES = [
  { h: 'fit the surrogate', s: 'on the trials already computed', c: BLUE },
  { h: 'maximise the acquisition', s: 'cheap: thousands of candidates', c: GREEN },
  { h: 'evaluate once, for real', s: 'one full CV run: minutes', c: RED },
  { h: 'add the result', s: 'and start again', c: GOLD },
]
</script>

<template>
  <div class="wrap">
    <div class="loop">
      <template v-for="(b, i) in BOXES" :key="i">
        <div class="box" :style="{ borderColor: b.c }"><b :style="{ color: b.c }">{{ b.h }}</b><span>{{ b.s }}</span></div>
        <span v-if="i < 3" class="arr">→</span>
      </template>
    </div>
    <div class="charts">
      <LineChart
        :series="[
          { points: G.map((x) => [x, boTarget(x)] as [number, number]), color: MUTED, width: 1.4, dash: '4 4' },
          { points: G.map((x, i) => [x, st.mu[i]] as [number, number]), color: BLUE, width: 2.6 },
        ]"
        :ribbons="[{ points: G.map((x, i) => [x, st.mu[i] - 2 * st.sd[i], st.mu[i] + 2 * st.sd[i]] as [number, number, number]), color: BLUE, alpha: 0.15 }]"
        :dots="[
          ...st.xs.map((x, i) => ({ x, y: boTarget(x), color: i < nStart ? MUTED : INK, r: 5.5 })),
          ...(t > 0 ? [{ x: st.xs.at(-1)!, y: boTarget(st.xs.at(-1)!), color: RED, r: 10, hollow: true }] : []),
        ]"
        :vlines="[{ x: st.next, color: GREEN, dash: '5 4' }]"
        :labels="[{ x: 0.01, y: 2.05, text: `pass ${t}: ${st.xs.length} trials, best ${best.toFixed(3)} (true minimum ${TRUE_MIN.toFixed(3)})`, color: INK, size: 13 }]"
        :x-domain="[0, 1]" :y-domain="[-1.5, 2.3]" :x-ticks="[]" :y-ticks="[-1, 0, 1, 2]" y-label="validation loss"
        :pad="{ l: 46, r: 14, t: 8, b: 8 }" :unit-height="230"
      />
      <LineChart
        :series="[{ points: G.map((x, i) => [x, st.a[i]] as [number, number]), color: GREEN, width: 2.4 }]"
        :vlines="[{ x: st.next, color: GREEN, dash: '5 4' }]"
        :x-domain="[0, 1]" :y-domain="[0, 1.1]" :x-ticks="[0, 0.2, 0.4, 0.6, 0.8, 1]" :y-ticks="[]"
        x-label="hyper-parameter x" :y-label="acq === 'ei' ? 'EI' : 'UCB'" :unit-height="130"
      />
    </div>
    <div class="controls">
      <Knob v-model="t" :min="0" :max="T" :step="1" :digits="0" label="pass" :color="GREEN" />
      <Choice v-model="acq" :options="[{ value: 'ei', label: 'expected improvement' }, { value: 'ucb', label: 'UCB, κ = 2' }]" />
      <Knob v-model="nStart" :min="1" :max="8" :step="1" :digits="0" label="random starts" />
      <Knob v-model="seed" :min="1" :max="30" :step="1" :digits="0" label="seed" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.loop { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr; align-items: center; gap: 0.4rem; }
.loop .box { border: 2px solid; border-radius: 8px; padding: 0.3rem 0.5rem; display: flex; flex-direction: column; text-align: center; font-size: 0.8rem; }
.loop .box span { color: #9aa0a6; font-size: 0.72rem; }
.arr { color: #9aa0a6; }
.charts { display: grid; grid-template-rows: 1.7fr 1fr; min-height: 0; }
</style>
