<!-- forest_features: both ends are worse than the middle. The curve is
     measured, one forest per value of max_features, in the background. -->
<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import { MF_KS, MfPoint, mfSweep } from '../lib/sweeps'
import { GOLD, GREEN, MUTED, RED } from '../lib/theme'

const k = ref(5)
const points = ref<MfPoint[]>([])
const stop = mfSweep((p) => (points.value = p))
onBeforeUnmount(stop)

const err = computed(() => points.value.map((p) => [p.k, p.err] as [number, number]))
const best = computed(() =>
  points.value.length ? points.value.reduce((a, b) => (b.err < a.err ? b : a)) : null,
)
const at = computed(() => points.value.find((p) => p.k === nearestK.value) ?? null)
const nearestK = computed(() =>
  MF_KS.reduce((a, b) => (Math.abs(b - k.value) < Math.abs(a - k.value) ? b : a)),
)
/** the dip is a couple of points deep, so the axis follows the data */
const yDomain = computed<[number, number]>(() => {
  if (!points.value.length) return [0, 0.2]
  const es = points.value.map((p) => p.err)
  const lo = Math.min(...es)
  const hi = Math.max(...es)
  const pad = Math.max(0.004, (hi - lo) * 0.45)
  return [Math.max(0, lo - pad), hi + pad * 1.6]
})
const ticks = computed(() => {
  const [lo, hi] = yDomain.value
  const step = (hi - lo) / 3
  return [0, 1, 2, 3].map((i) => Number((lo + i * step).toFixed(3)))
})
const done = computed(() => points.value.length === MF_KS.length)
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="[{ points: err, color: GREEN, width: 2.6 }]"
      :dots="[
        ...points.map((p) => ({ x: p.k, y: p.err, color: GREEN, r: 4 })),
        ...(at ? [{ x: at.k, y: at.err, color: '#1b1b1b', r: 6, hollow: true }] : []),
      ]"
      :vlines="[{ x: 5, color: MUTED, dash: '4,4' }]"
      :x-domain="[0, 26]" :y-domain="yDomain"
      :x-ticks="[1, 5, 10, 15, 20, 25]" :y-ticks="ticks"
      x-label="max_features, out of 25" y-label="test error"
      title="25 columns: 12 informative, 8 redundant, 5 noise"
      :labels="[{ x: 5.4, y: yDomain[1] - (yDomain[1] - yDomain[0]) * 0.06, text: 'the √p default', color: MUTED, size: 11 }]"
    />
    <div class="side">
      <h4 :style="{ color: GREEN }">both ends are worse than the middle</h4>
      <p class="box red">
        all columns allowed → every tree takes the same strong split first → ρ large
        → averaging buys almost nothing
      </p>
      <p class="box gold">
        one column allowed → the trees disagree, but each is barely better than
        chance → low ρ, high individual error
      </p>
      <Knob v-model="k" :min="1" :max="25" :step="1" label="max_features" :digits="0" :color="GREEN" />
      <Readout
        v-if="at"
        :items="[
          { label: 'test error', value: (at.err * 100).toFixed(1) + '%', color: GREEN },
          { label: 'one tree alone', value: (at.solo * 100).toFixed(1) + '%' },
          { label: 'ρ', value: at.rho.toFixed(2), color: RED },
        ]"
      />
      <p class="note">
        <span v-if="!done">Measuring… {{ points.length }}/{{ MF_KS.length }} forests fitted</span>
        <span v-else-if="best">√p is a default, not a law: here the best is {{ best.k }}.</span>
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.25fr 0.9fr; gap: 1.6rem; height: 100%; min-height: 0; }
.side { display: flex; flex-direction: column; justify-content: center; gap: 0.5rem; }
h4 { margin: 0; font-size: 0.95rem; }
.box { font-size: 0.8rem; margin: 0; line-height: 1.5; }
.red { color: var(--red); }
.gold { color: var(--gold); }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); }
</style>
