<!-- knob_nmf_rank: a 30 x 45 matrix built with a known rank plus noise.
     Entries are hidden under a random mask, NMF is fitted on the rest for
     every r, and both sets of entries are scored. The fitted ones only
     improve with r; the held-out ones bottom out near the true rank. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { nmfMasked, nmfToy } from '../lib/c08'
import { Rng } from '../lib/rng'
import { useSweep } from '../lib/sweep'
import { BLUE, GREEN, INK, RED } from '../lib/theme'

const rTrue = ref(4)
const noise = ref(0.12)
const hold = ref(0.2)
const r = ref(4)
const RS = Array.from({ length: 10 }, (_, i) => i + 1)
const MASKS = 2

// seed 9: the draw whose held-out error bottoms out at the true rank, as printed
const X = computed(() => nmfToy(9, 30, 45, rTrue.value, noise.value))
const masks = computed(() => Array.from({ length: MASKS }, (_, s) => {
  const rng = new Rng(100 + s)
  return Float64Array.from({ length: 30 * 45 }, () => (rng.next() > hold.value ? 1 : 0))
}))
const sweep = useSweep(() => RS, (rr) => {
  let tr = 0, ho = 0
  masks.value.forEach((mask, s) => {
    const R = nmfMasked(X.value, rr, 250, s, mask)
    let a = 0, na = 0, b = 0, nb = 0
    for (let i = 0; i < R.length; i++) {
      const e = (R[i] - X.value.v[i]) ** 2
      if (mask[i]) { a += e; na++ } else { b += e; nb++ }
    }
    tr += Math.sqrt(a / na)
    ho += Math.sqrt(b / Math.max(nb, 1))
  })
  return { tr: tr / MASKS, ho: ho / MASKS }
}, [rTrue, noise, hold])

const pts = (key: 'tr' | 'ho') => RS.map((x, i) => [x, sweep.value[i]?.[key]] as [number, number | undefined])
  .filter((p) => p[1] !== undefined) as [number, number][]
const fitted = computed(() => pts('tr'))
const held = computed(() => pts('ho'))
const best = computed(() => (held.value.length === RS.length ? held.value.reduce((a, b) => (b[1] < a[1] ? b : a))[0] : null))
const ymax = computed(() => Math.max(0.5, ...held.value.map((p) => p[1]), ...fitted.value.map((p) => p[1])) * 1.08)
const cur = computed(() => sweep.value[r.value - 1])
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[{ points: fitted, color: BLUE, width: 2.6 }, { points: held, color: RED, width: 2.6 }]"
        :dots="[
          ...fitted.map(([x, y]) => ({ x, y, color: BLUE, r: 4 })),
          ...held.map(([x, y]) => ({ x, y, color: RED, r: 4 })),
          ...(best ? [{ x: best, y: held[best - 1][1], color: GREEN, r: 11, hollow: true }] : []),
        ]"
        :vlines="[{ x: r, color: INK, dash: '' }, { x: rTrue, color: GREEN, dash: '3 3' }]"
        :labels="[{ x: 7.4, y: ymax * 0.9, text: 'entries held out', color: RED }, { x: 7.4, y: ymax * 0.82, text: 'entries used to fit', color: BLUE }]"
        :x-domain="[0.5, 10.5]" :y-domain="[0, ymax]" :x-ticks="RS" :y-ticks="[0, 0.25, 0.5, 0.75, 1, 1.25].filter((v) => v <= ymax)"
        x-label="rank r" y-label="RMS reconstruction error"
      />
      <div class="side">
        <div class="h">At r = {{ r }}</div>
        <p v-if="cur">fitted entries <b :style="{ color: BLUE }">{{ cur.tr.toFixed(3) }}</b></p>
        <p v-if="cur">held-out entries <b :style="{ color: RED }">{{ cur.ho.toFixed(3) }}</b></p>
        <div class="h">Choice</div>
        <p v-if="best">The held-out error is lowest at <b :style="{ color: GREEN }">r = {{ best }}</b>; the matrix was built with rank {{ rTrue }} (dashed).</p>
        <p v-else class="note">fitting r = 1 … 10 …</p>
        <p class="note">Cross-validation on a mask: hide entries, fit on the rest, score what was hidden. More noise makes the extra components fit noise sooner.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="r" :min="1" :max="10" :step="1" :digits="0" label="rank r" />
      <Knob v-model="rTrue" :min="1" :max="8" :step="1" :digits="0" label="true rank" :color="GREEN" />
      <Knob v-model="noise" :min="0.01" :max="0.5" :step="0.01" label="noise" />
      <Knob v-model="hold" :min="0.05" :max="0.5" :step="0.05" label="held out" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
</style>
