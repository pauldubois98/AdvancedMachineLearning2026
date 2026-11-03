<!-- svm_sigma and knob_svm_c: one RBF SVM on the moons, refitted as gamma (at
     C = 1) or C (at gamma = 2) moves. The right panel sweeps the knob over
     its whole range, training and test accuracy: they part ways at the
     flexible end. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { accuracy, fitSvc, kernel } from '../lib/svm'
import { moons } from '../lib/c08'
import { useSweep } from '../lib/sweep'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const props = defineProps<{ knob: 'gamma' | 'C' }>()
const isG = props.knob === 'gamma'
const train = isG ? moons(220, 0.3, 3) : moons(120, 0.3, 3)
const test = moons(1500, 0.3, 77)
const lo = isG ? 0.01 : 0.003
const hi = isG ? 1000 : 3000
const v = ref(isG ? 2 : 1)
const fit = (x: number) =>
  fitSvc(train.X, train.y, isG ? 1 : x, kernel({ type: 'rbf', gamma: isG ? x : 2 }), { maxPasses: 300 })
const model = computed(() => fit(v.value))
const trAcc = computed(() => accuracy(model.value, train.X, train.y))
const teAcc = computed(() => accuracy(model.value, test.X, test.y))

const grid = Array.from({ length: 15 }, (_, i) => 10 ** (Math.log10(lo) + (i * (Math.log10(hi) - Math.log10(lo))) / 14))
const sweep = useSweep(() => grid, (x) => {
  const m = fit(x)
  return { tr: accuracy(m, train.X, train.y), te: accuracy(m, test.X, test.y) }
})
const series = computed(() => {
  const pts = grid.map((x, i) => [x, sweep.value[i]] as const).filter((p) => p[1])
  return [
    { points: pts.map(([x, s]) => [x, s!.tr] as [number, number]), color: BLUE, width: 2.2 },
    { points: pts.map(([x, s]) => [x, s!.te] as [number, number]), color: RED, width: 2.2 },
  ]
})
const bestTe = computed(() => {
  let b = -1, bx = 0
  grid.forEach((x, i) => { const s = sweep.value[i]; if (s && s.te > b) { b = s.te; bx = x } })
  return b < 0 ? null : bx
})
const verdict = computed(() => {
  const r = Math.log10(v.value)
  const [a, b] = isG ? [-0.6, 1.3] : [-1.2, 1.6]
  return r < a ? { t: 'too small', c: RED } : r > b ? { t: 'too large', c: RED } : { t: 'about right', c: GREEN }
})
const sym = isG ? 'γ' : 'C'
const fieldColor = (f: number): [number, number, number] => (f >= 0 ? [232, 238, 245] : [250, 238, 238])
const domain: [number, number, number, number] = [-1.6, 2.6, -1.2, 1.7]
const pmColor = train.y.map((c) => (c > 0 ? BLUE : RED))
</script>

<template>
  <div class="wrap">
    <div class="body">
      <Plane
        :X="(train.X as any)" :colors="pmColor" :size="3.2" :domain="domain"
        :field="(x: number, y: number) => model.decisionAt(x, y)" :field-color="fieldColor" :field-res="110"
        :levels="[{ f: (x: number, y: number) => model.decisionAt(x, y), level: 0, color: INK, width: 2.2 }]"
        :title="`${sym} = ${v < 1 ? v.toPrecision(2) : v.toFixed(v < 10 ? 1 : 0)}: ${verdict.t}`" :title-color="verdict.c"
        :caption="`train ${(100 * trAcc).toFixed(0)}% · test ${(100 * teAcc).toFixed(0)}%`"
      />
      <div class="side">
        <LineChart
          :series="series" log-x :x-domain="[lo, hi]" :y-domain="[0.6, 1.0]"
          :x-ticks="isG ? [0.01, 1, 100] : [0.01, 1, 100]" :y-ticks="[0.6, 0.7, 0.8, 0.9, 1]"
          :vlines="[{ x: v, color: INK, dash: '' }, ...(bestTe ? [{ x: bestTe, color: GREEN }] : [])]"
          :labels="[{ x: lo * 1.6, y: 0.64, text: 'training', color: BLUE, size: 13 }, { x: lo * 1.6, y: 0.615, text: 'test (fresh moons)', color: RED, size: 13 }]"
          :x-label="sym" y-label="accuracy" :unit-height="340"
        />
        <p class="note">Training accuracy only climbs with {{ sym }}; the test accuracy peaks (green line) and falls back.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="v" :min="lo" :max="hi" log :label="isG ? 'kernel width γ' : 'soft margin C'" :color="verdict.c" />
      <span class="note">RBF SVM, {{ isG ? 'C = 1' : 'γ = 2' }}, {{ train.X.length }} training points; test on 1500 fresh ones.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.25fr 1fr; gap: 2rem; min-height: 0; }
.side { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
</style>
