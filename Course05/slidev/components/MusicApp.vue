<!-- app_music: NMF of the spectrogram, with the loss as a choice. The notes
     (W) and when each is struck (H) come out of X alone. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { music } from '../lib/data5'
import { col, mat, row } from '../lib/mat'
import { type Loss, fit, init, lossOf } from '../lib/nmf'
import { BLUE, GOLD, GREEN, INK, PURPLE, RED, MUTED } from '../lib/theme'

const { freqs, t, notes, X } = music
const colors = [BLUE, GREEN, RED, PURPLE, GOLD]
const loss = ref<Loss>('kl')
const r = ref(3)
const passes = ref(400)
const xmax = Math.max(...X.a)
const L = (() => { const m = mat(X.r, X.c); X.a.forEach((v, i) => { m.a[i] = Math.log1p((v / xmax) * 400) }); return m })()
function corr(a: ArrayLike<number>, b: ArrayLike<number>) {
  const m = a.length
  let ma = 0, mb = 0
  for (let i = 0; i < m; i++) { ma += a[i] / m; mb += b[i] / m }
  let sab = 0, saa = 0, sbb = 0
  for (let i = 0; i < m; i++) { sab += (a[i] - ma) * (b[i] - mb); saa += (a[i] - ma) ** 2; sbb += (b[i] - mb) ** 2 }
  return sab / Math.sqrt(saa * sbb || 1)
}
const res = computed(() => {
  const f = fit(X, init(X, r.value, 'nndsvd'), passes.value, 'mu', { loss: loss.value })
  const comps = Array.from({ length: r.value }, (_, k) => {
    const w = col(f.W, k)
    const c = notes.map((nt) => corr(nt, w))
    const s = c.indexOf(Math.max(...c))
    return { w, h: row(f.H, k), s, good: c[s] > 0.9 }
  }).sort((a, b) => a.s - b.s)
  return { comps, value: lossOf(X, f, loss.value) }
})
const norm = (v: ArrayLike<number>) => { const m = Math.max(...Array.from(v)) || 1; return Array.from(v, (x) => x / m) }
</script>

<template>
  <div class="wrap">
    <div class="note top">Power adds up when notes are played together, so the spectrogram really is a product.</div>
    <div class="body">
      <div class="col">
        <MatView :M="L" ramp="x" flip title="X: a power spectrogram" :title-color="BLUE" />
        <div class="cap">time →, frequency ↑ (log scale)</div>
      </div>
      <div class="col">
        <LineChart
          :series="res.comps.map((c, k) => ({ points: norm(c.w).map((v, i) => [v + 1.25 * k, freqs[i]]), color: c.good ? colors[c.s] : MUTED, width: 1.7 }))"
          :x-domain="[-0.1, 1.25 * r + 0.1]" :y-domain="[0, 1]" :axes="false" :title="`W: ${r} notes`" :title-color="PURPLE"
        />
        <div class="cap">grey: a component that matches no true note</div>
      </div>
      <div class="col">
        <LineChart
          :series="res.comps.map((c, k) => ({ points: norm(c.h).map((v, i) => [t[i], v + 1.2 * k]), color: c.good ? colors[c.s] : MUTED, width: 1.7 }))"
          :x-domain="[0, 1]" :y-domain="[-0.1, 1.2 * r + 0.1]" x-label="time" :x-ticks="[]" :y-ticks="[]" title="H: when each is struck" :title-color="GOLD"
        />
      </div>
    </div>
    <div class="controls">
      <Choice v-model="loss" label="loss" :options="[{ value: 'fro', label: 'Frobenius', color: BLUE }, { value: 'kl', label: 'KL', color: GREEN }, { value: 'is', label: 'Itakura–Saito', color: GOLD }]" />
      <Knob v-model="r" :min="2" :max="5" :step="1" label="r" :digits="0" :color="INK" />
      <Knob v-model="passes" :min="10" :max="800" :step="10" label="passes" :digits="0" :color="INK" />
    </div>
    <div class="note bottom">Itakura–Saito (or KL) is the loss of choice here: it treats a quiet harmonic like a loud one.</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top, .bottom { text-align: center; }
.body { display: grid; grid-template-columns: 1.4fr 0.8fr 1.4fr; gap: 1.4rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; gap: 0.3rem; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.75rem; line-height: 1.35; }
</style>
