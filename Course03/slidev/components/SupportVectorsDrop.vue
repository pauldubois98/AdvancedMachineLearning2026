<!-- support_vectors: only the points on the margin carry α > 0. Throw the
     others away and refit: the same boundary comes back. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sepBlobs, toPm1 } from '../lib/data'
import { fitSvc, kernel } from '../lib/svm'
import { BLUE, GREEN, INK, MUTED } from '../lib/theme'
import { dataDomain } from '../lib/plot'

const data = sepBlobs(90, 2.6, 3)
const yPm = toPm1(data.y)
const full = fitSvc(data.X, yPm, 1000, kernel({ type: 'linear' }))
const domain = dataDomain(data.X, 0.7)

const dropped = ref(false)
const kept = computed(() => (dropped.value ? full.sv : data.X.map((_, i) => i)))
const sub = computed(() => {
  const X = kept.value.map((i) => data.X[i])
  const y = kept.value.map((i) => yPm[i])
  return fitSvc(X, y, 1000, kernel({ type: 'linear' }))
})
const shownX = computed(() => kept.value.map((i) => data.X[i]))
const shownY = computed(() => kept.value.map((i) => data.y[i]))
const svInShown = computed(() =>
  dropped.value ? sub.value.sv : full.sv,
)
const shift = computed(() => {
  // how far the refitted boundary moved, in decision-function terms
  let m = 0
  for (const p of data.X) m = Math.max(m, Math.abs(full.decision(p) - sub.value.decision(p)))
  return m
})
</script>

<template>
  <div class="wrap">
    <FieldPlot
      :X="shownX" :y="shownY" :decision="sub.decisionAt" :domain="domain"
      :rings="[{ idx: svInShown, color: GREEN }]" :point-size="dropped ? 40 : 26"
    />
    <div class="side">
      <Toggle v-model="dropped" label="keep only the support vectors" :color="GREEN" />
      <Readout
        :items="[
          { label: 'points used', value: String(kept.length), color: dropped ? GREEN : INK },
          { label: 'support vectors', value: String(full.sv.length), color: GREEN },
          { label: 'boundary moved by', value: shift.toExponential(1), color: shift < 1e-6 ? GREEN : INK },
        ]"
      />
      <div class="cases">
        <p class="head">two cases</p>
        <p :style="{ color: GREEN }">y<sub>i</sub> f(x<sub>i</sub>) = 1</p>
        <p class="sub">on the margin, α<sub>i</sub> &gt; 0</p>
        <p :style="{ color: BLUE }">y<sub>i</sub> f(x<sub>i</sub>) &gt; 1</p>
        <p class="sub">further away, α<sub>i</sub> = 0; the point can be thrown away</p>
      </div>
      <p class="note">
        {{ full.sv.length }} of {{ data.X.length }} points decide everything.
        That is why the prediction is a sum over the support vectors only.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; align-items: center; }
.side { display: flex; flex-direction: column; gap: 0.6rem; }
.cases p { margin: 0; font-size: 0.86rem; }
.head { font-weight: 600; margin-bottom: 0.2rem !important; }
.sub { color: v-bind(MUTED); font-size: 0.75rem !important; margin-bottom: 0.3rem !important; }
.note { font-size: 0.78rem; color: v-bind(MUTED); margin: 0; line-height: 1.45; }
</style>
