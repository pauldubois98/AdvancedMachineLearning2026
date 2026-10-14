<!-- multiclass: the SVM only knows how to say ±1, so K classes are reduced to
     a set of two-class problems: one against all, or one against one. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { threeBlobs } from '../lib/data'
import { fitSvc, kernel } from '../lib/svm'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const mode = ref('none')
const data = threeBlobs(13, 45)
const K = 3

const ova = computed(() =>
  Array.from({ length: K }, (_, k) =>
    fitSvc(data.X, data.y.map((v) => (v === k ? 1 : -1)), 1, kernel({ type: 'linear' })),
  ),
)
const ovo = computed(() => {
  const out: { a: number; b: number; m: ReturnType<typeof fitSvc> }[] = []
  for (let a = 0; a < K; a++)
    for (let b = a + 1; b < K; b++) {
      const idx = data.X.map((_, i) => i).filter((i) => data.y[i] === a || data.y[i] === b)
      out.push({
        a, b,
        m: fitSvc(idx.map((i) => data.X[i]), idx.map((i) => (data.y[i] === a ? 1 : -1)), 1,
          kernel({ type: 'linear' })),
      })
    }
  return out
})

const regions = computed(() => {
  if (mode.value === 'ova') {
    const ms = ova.value
    return (x: number, y: number) => {
      let best = 0
      let bv = -Infinity
      for (let k = 0; k < K; k++) {
        const v = ms[k].decision([x, y])
        if (v > bv) {
          bv = v
          best = k
        }
      }
      return best
    }
  }
  if (mode.value === 'ovo') {
    const ps = ovo.value
    return (x: number, y: number) => {
      const votes = [0, 0, 0]
      for (const { a, b, m } of ps) votes[m.decision([x, y]) > 0 ? a : b]++
      let best = 0
      for (let k = 1; k < K; k++) if (votes[k] > votes[best]) best = k
      return best
    }
  }
  return null
})
const fits = computed(() => (mode.value === 'ova' ? K : mode.value === 'ovo' ? (K * (K - 1)) / 2 : 0))
</script>

<template>
  <div class="wrap">
    <FieldPlot
      :X="data.X" :y="data.y" :regions="regions" :domain="[-5, 5, -4, 5]"
      :point-size="16" :res="150"
      :title="mode === 'ova' ? 'one against all' : mode === 'ovo' ? 'one against one' : 'three classes'"
      :title-color="mode === 'ova' ? BLUE : mode === 'ovo' ? GREEN : INK"
    />
    <div class="side">
      <Choice
        v-model="mode"
        :options="[
          { value: 'none', label: 'just the data', color: INK },
          { value: 'ova', label: 'one against all', color: BLUE },
          { value: 'ovo', label: 'one against one', color: GREEN },
        ]"
      />
      <div class="explain">
        <template v-if="mode === 'none'">
          <p class="head">the SVM only knows how to say ±1</p>
          <p class="note">
            With K classes there is no single two-class problem to solve, so the
            problem is cut into several of them.
          </p>
        </template>
        <template v-else-if="mode === 'ova'">
          <p class="head" :style="{ color: BLUE }">K fits: class k against everything else</p>
          <p class="eq">k̂ = arg max<sub>k</sub> f<sub>k</sub>(x)</p>
          <p class="note">
            Cheap: K fits in all. But each fit sees an unbalanced problem, and the
            scores f<sub>k</sub> come from different models, so comparing them is a
            leap of faith.
          </p>
        </template>
        <template v-else>
          <p class="head" :style="{ color: GREEN }">K(K−1)/2 fits: every pair, then a majority vote</p>
          <p class="note">
            Each fit is small and balanced, but there are {{ (K * (K - 1)) / 2 }} of
            them here and ~K²/2 in general. This is what scikit-learn's SVC does.
          </p>
        </template>
      </div>
      <Readout
        v-if="mode !== 'none'"
        :items="[
          { label: 'fits', value: String(fits), color: mode === 'ova' ? BLUE : GREEN },
          { label: 'with K = 10 classes', value: mode === 'ova' ? '10 fits' : '45 fits', color: MUTED },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; align-items: center; }
.side { display: flex; flex-direction: column; gap: 0.7rem; }
.head { font-size: 0.9rem; font-weight: 600; margin: 0 0 0.3rem; }
.eq { font-size: 0.95rem; margin: 0 0 0.3rem; }
.note { font-size: 0.78rem; color: v-bind(MUTED); margin: 0; line-height: 1.5; }
</style>
