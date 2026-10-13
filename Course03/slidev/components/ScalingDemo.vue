<!-- feature_scaling: the RBF measures distances, so a feature in silly units
     drowns the others. Turn the unit up and watch x₁ stop mattering. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { gammaScale, standardize, toPm1, unscaled } from '../lib/data'
import { fitSvc, kernel } from '../lib/svm'
import { GREEN, MUTED, RED } from '../lib/theme'

const scale = ref(400)
const standardise = ref(false)

const raw = computed(() => unscaled(scale.value, 140, 4))
const X = computed(() => (standardise.value ? standardize(raw.value.X) : raw.value.X))
const yPm = computed(() => toPm1(raw.value.y))
const model = computed(() =>
  fitSvc(X.value, yPm.value, 1, kernel({ type: 'rbf', gamma: gammaScale(X.value) })),
)
const accuracy = computed(() => {
  let ok = 0
  for (let i = 0; i < X.value.length; i++)
    if (model.value.predict(X.value[i]) === yPm.value[i]) ok++
  return ok / X.value.length
})

/** how much of the boundary's variation comes from x₁ */
const useOfX1 = computed(() => {
  const m = model.value
  const pts = X.value
  let dx1 = 0
  let dx2 = 0
  const sd = (j: number) => {
    const v = pts.map((p) => p[j])
    const mu = v.reduce((a, b) => a + b, 0) / v.length
    return Math.sqrt(v.reduce((a, b) => a + (b - mu) ** 2, 0) / v.length)
  }
  const s1 = sd(0)
  const s2 = sd(1)
  for (const p of pts) {
    dx1 += Math.abs(m.decision([p[0] + 0.1 * s1, p[1]]) - m.decision(p))
    dx2 += Math.abs(m.decision([p[0], p[1] + 0.1 * s2]) - m.decision(p))
  }
  return dx1 / (dx1 + dx2 || 1)
})
</script>

<template>
  <div class="wrap">
    <FieldPlot
      :X="X" :y="raw.y" :decision="model.decisionAt" :margins="false"
      :point-size="16" aspect="auto"
      :title="standardise ? 'after standardising' : 'as measured'"
      :title-color="standardise ? GREEN : RED"
    />
    <div class="side">
      <Knob v-model="scale" :min="1" :max="1000" log label="unit of x₂" :color="RED" :disabled="standardise" />
      <Toggle v-model="standardise" label="standardise both features" :color="GREEN" />
      <Readout
        :items="[
          { label: 'training accuracy', value: `${(accuracy * 100).toFixed(1)}%`, color: accuracy > 0.9 ? GREEN : RED },
          { label: 'support vectors', value: String(model.sv.length), color: MUTED },
        ]"
      />
      <div class="split">
        <p class="lab">how much the boundary uses each feature</p>
        <div class="bar">
          <div class="x1" :style="{ width: `${useOfX1 * 100}%` }">x₁</div>
          <div class="x2">x₂</div>
        </div>
        <p class="pct">
          <span :style="{ color: useOfX1 < 0.15 ? RED : GREEN }">{{ (useOfX1 * 100).toFixed(0) }}%</span>
          from x₁, {{ (100 - useOfX1 * 100).toFixed(0) }}% from x₂
        </p>
      </div>
      <p class="note">
        both features separate the classes equally well. The RBF only sees
        ‖x − x′‖, so whichever feature carries the larger numbers decides
        everything, until both are put on the same scale.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; align-items: center; }
.side { display: flex; flex-direction: column; gap: 0.6rem; }
.lab { font-size: 0.74rem; color: v-bind(MUTED); margin: 0 0 0.2rem; }
.bar { display: flex; height: 1.1rem; border-radius: 0.2rem; overflow: hidden; font-size: 0.68rem; color: white; }
.x1 { background: #2b6cb0; display: flex; align-items: center; justify-content: center; min-width: 0; transition: width 0.15s; }
.x2 { background: #c53030; flex: 1; display: flex; align-items: center; justify-content: center; }
.pct { font-size: 0.74rem; margin: 0.2rem 0 0; color: v-bind(MUTED); }
.note { font-size: 0.76rem; color: v-bind(MUTED); margin: 0; line-height: 1.45; }
</style>
