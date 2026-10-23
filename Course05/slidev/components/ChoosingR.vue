<!-- choosing_r: the training error always falls with r, so it never picks r.
     Hide some of the observed entries, fit on the rest, and score the hidden
     ones: that curve turns back up. The ratings table was built from 3 tastes. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ratings } from '../lib/data5'
import { mat, mul } from '../lib/mat'
import { fit, init } from '../lib/nmf'
import { Rng } from '../lib/rng'
import { BLUE, GREEN, INK, RED } from '../lib/theme'

const held = ref(0.2)
const seed = ref(1)
const full = ratings.full
const RS = Array.from({ length: 10 }, (_, i) => i + 1)
const curves = computed(() => {
  const rng = new Rng(seed.value * 31 + 5)
  const mask = mat(full.r, full.c)
  mask.a.forEach((_, i) => { mask.a[i] = rng.next() > held.value ? 1 : 0 })
  const train: [number, number][] = []
  const test: [number, number][] = []
  RS.forEach((r) => {
    const f = fit(full, init(full, r, 'random', seed.value), 600, 'mu', { mask })
    const Y = mul(f.W, f.H)
    let a = 0, na = 0, b = 0, nb = 0
    full.a.forEach((v, i) => { const e = (Y.a[i] - v) ** 2; if (mask.a[i]) { a += e; na++ } else { b += e; nb++ } })
    train.push([r, Math.sqrt(a / na)])
    test.push([r, Math.sqrt(b / Math.max(nb, 1))])
  })
  const best = test.reduce((m, p) => (p[1] < m[1] ? p : m))
  return { train, test, best }
})
</script>

<template>
  <div class="wrap">
    <div class="note top">Choosing r is the one parameter NMF cannot choose for itself</div>
    <div class="body">
      <LineChart
        :series="[{ points: curves.train, color: BLUE, width: 2.4 }, { points: curves.test, color: GREEN, width: 2.4 }]"
        :dots="[...curves.train.map(([x, y]) => ({ x, y, color: BLUE, r: 4 })), ...curves.test.map(([x, y]) => ({ x, y, color: GREEN, r: 4 })), { x: curves.best[0], y: curves.best[1], color: GREEN, r: 8, hollow: true }]"
        :labels="[{ x: 9.8, y: curves.train[9][1] - 0.05, text: 'entries fitted on', color: BLUE, size: 13, anchor: 'end' }, { x: 9.8, y: curves.test[9][1] + 0.06, text: 'entries held out', color: GREEN, size: 13, anchor: 'end' }]"
        :x-domain="[0.5, 10.5]" :y-domain="[0, Math.max(...curves.test.map((p) => p[1])) * 1.15]" x-label="r" y-label="RMS error (stars)" :x-ticks="RS"
        title="ratings table, built from 3 tastes"
      />
      <div class="side">
        <div class="h" :style="{ color: RED }">the training curve never rises</div>
        <p>A larger r always fits better, so the error alone never picks r for you.</p>
        <div class="h" :style="{ color: GREEN }">what people use instead</div>
        <p>— the elbow, if there is one</p>
        <p>— <b>held-out entries</b>: fit on a mask, score the rest (here: best r = {{ curves.best[0] }})</p>
        <p>— stability: do the components survive a restart?</p>
        <p>— domain knowledge: 3 materials, 20 topics</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="held" :min="0.05" :max="0.5" :step="0.01" label="share held out" :color="GREEN" />
      <Knob v-model="seed" :min="1" :max="20" :step="1" label="draw" :digits="0" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
</style>
