<!-- knob_rigid_vs_flexible: naive Bayes, LDA and QDA on two correlated
     Gaussians that share one covariance. Left: one sample of n per class and
     the three boundaries. Right: the mean test accuracy as n grows, with the
     current n marked. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { gaussAccuracy, gaussFit, twoGauss, type GaussKind } from '../lib/c08'
import { useSweep } from '../lib/sweep'
import { GREEN, INK, MUTED, PURPLE, RED } from '../lib/theme'

const MODELS: { k: GaussKind; name: string; color: string; dash: number[] }[] = [
  { k: 'nb', name: 'naive Bayes', color: RED, dash: [2, 4] },
  { k: 'lda', name: 'LDA', color: GREEN, dash: [] },
  { k: 'qda', name: 'QDA', color: PURPLE, dash: [8, 5] },
]
const test = twoGauss(1500, 0)
const n = ref(20)
const seed = ref(1)
const sample = computed(() => twoGauss(n.value, 1000 + seed.value))
const fits = computed(() => MODELS.map((m) => ({ ...m, f: gaussFit(sample.value, m.k) })))
const accs = computed(() => fits.value.map((m) => gaussAccuracy(m.f, test)))

const NS = [10, 15, 20, 30, 50, 100, 200, 500]
const REPS = 40
const sweep = useSweep(() => NS, (nn) => {
  const tot = [0, 0, 0]
  for (let r = 0; r < REPS; r++) {
    const d = twoGauss(nn, 5000 + r)
    MODELS.forEach((m, i) => { tot[i] += gaussAccuracy(gaussFit(d, m.k), test) })
  }
  return tot.map((t) => t / REPS)
})
const series = computed(() => MODELS.map((m, i) => ({
  points: NS.map((v, j) => [v, sweep.value[j]?.[i]] as [number, number | undefined])
    .filter((p) => p[1] !== undefined) as [number, number][],
  color: m.color, width: 2.4,
})))
const dots = computed(() => series.value.flatMap((s) => s.points.map(([x, y]) => ({ x, y, color: s.color, r: 3.2 }))))
const cls = computed(() => sample.value.y.map((c) => (c ? INK : MUTED)))
</script>

<template>
  <div class="wrap">
    <div class="body">
      <Plane
        :X="(sample.X as any)" :colors="cls" :size="3.4" :alpha="0.7" :domain="[-4.2, 4.2, -3.4, 3.4]"
        :levels="fits.map((m) => ({ f: m.f, level: 0, color: m.color, width: 2.4, dash: m.dash }))"
        :title="`one sample of ${2 * n}`"
      />
      <div class="side">
        <LineChart
          :series="series" :dots="dots" log-x :x-domain="[8, 600]" :y-domain="[0.78, 0.86]"
          :x-ticks="[10, 100, 500]" :y-ticks="[0.78, 0.8, 0.82, 0.84, 0.86]"
          :vlines="[{ x: n, color: INK, dash: '' }]"
          x-label="points per class (log)" y-label="mean test accuracy" title="as the sample grows" :unit-height="320"
        />
        <div class="legend">
          <span v-for="(m, i) in MODELS" :key="m.k" :style="{ color: m.color }">
            {{ m.name }}: <b>{{ (100 * accs[i]).toFixed(1) }}%</b>
          </span>
          <span class="note">on this sample</span>
        </div>
      </div>
    </div>
    <div class="msgs">
      <span :style="{ color: RED }">naive Bayes is too rigid: more data never fixes a bias.</span>
      <span :style="{ color: PURPLE }">QDA is too free: behind on small samples, level on large ones.</span>
      <span :style="{ color: GREEN }">LDA has the shape the data has.</span>
    </div>
    <div class="controls">
      <Knob v-model="n" :min="5" :max="300" :step="1" :digits="0" label="points per class n" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" :digits="0" label="sample" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1fr 1.1fr; gap: 2rem; min-height: 0; }
.side { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.legend { display: flex; gap: 1.2rem; font-size: 0.8rem; justify-content: center; align-items: baseline; }
.msgs { display: flex; flex-direction: column; align-items: center; font-size: 0.8rem; line-height: 1.4; }
</style>
