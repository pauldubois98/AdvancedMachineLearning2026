<!-- svm_kernels: four kernels, four shapes of boundary. Every knob the
     printed deck only showed three snapshots of is live here. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { moons, toPm1 } from '../lib/data'
import { KernelType, fitSvc, kernel } from '../lib/svm'
import { BLUE, GOLD, GREEN, MUTED, PURPLE, RED } from '../lib/theme'
import { dataDomain } from '../lib/plot'

const type = ref<KernelType>('rbf')
const C = ref(1)
const gamma = ref(0.5)
const degree = ref(3)
const coef0 = ref(1)

const data = moons(260, 0.22, 0)
const yPm = toPm1(data.y)
const domain = dataDomain(data.X, 0.7)

const model = computed(() =>
  fitSvc(data.X, yPm, C.value, kernel({
    type: type.value, gamma: gamma.value, degree: degree.value, coef0: coef0.value,
  })),
)
const errors = computed(() => {
  let n = 0
  for (let i = 0; i < data.X.length; i++)
    if (model.value.predict(data.X[i]) !== yPm[i]) n++
  return n
})
const accuracy = computed(() => 1 - errors.value / data.X.length)

const options = [
  { value: 'linear', label: 'linear', color: BLUE },
  { value: 'poly', label: 'polynomial', color: PURPLE },
  { value: 'rbf', label: 'RBF', color: GREEN },
  { value: 'sigmoid', label: 'sigmoid', color: GOLD },
]
const color = computed(() => options.find((o) => o.value === type.value)!.color)
const formula = computed(() => ({
  linear: 'k(x, x′) = xᵀx′',
  poly: 'k(x, x′) = (γ xᵀx′ + r)ᵖ',
  rbf: 'k(x, x′) = exp(−γ‖x − x′‖²)',
  sigmoid: 'k(x, x′) = tanh(γ xᵀx′ + r)',
}[type.value]))
const usesGamma = computed(() => type.value !== 'linear')
const usesCoef0 = computed(() => type.value === 'poly' || type.value === 'sigmoid')

function preset(t: KernelType, g: number, c: number) {
  type.value = t
  gamma.value = g
  C.value = c
}
</script>

<template>
  <div class="wrap">
    <FieldPlot
      :X="data.X" :y="data.y" :decision="model.decisionAt" :domain="domain"
      :margins="false" :point-size="11"
      :rings="[{ idx: model.sv, color: GREEN, size: 34, width: 1 }]"
    />
    <div class="side">
      <Choice v-model="type" :options="options" />
      <p class="formula" :style="{ color }">{{ formula }}</p>
      <div class="knobs">
        <Knob v-model="C" :min="0.01" :max="1000" log label="C" :color="color" />
        <Knob v-model="gamma" :min="0.01" :max="100" log label="γ" :color="color" :disabled="!usesGamma" />
        <Knob v-if="type === 'poly'" v-model="degree" :min="1" :max="8" :step="1" label="degree p" :digits="0" :color="color" />
        <Knob v-if="usesCoef0" v-model="coef0" :min="0" :max="3" :step="0.05" label="r" :digits="2" :color="color" />
      </div>
      <Readout
        :items="[
          { label: 'support vectors', value: `${model.sv.length} / ${data.X.length}`, color: GREEN },
          { label: 'training accuracy', value: `${(accuracy * 100).toFixed(1)}%`, color: errors ? MUTED : GREEN },
        ]"
      />
      <div class="presets">
        <span class="lab">try</span>
        <button @click="preset('linear', 0.5, 1)">linear</button>
        <button @click="preset('poly', 1, 1)">cubic</button>
        <button @click="preset('rbf', 0.5, 1)">RBF γ = 0.5</button>
        <button class="warn" @click="preset('rbf', 50, 1)">RBF γ = 50</button>
      </div>
      <p class="note" :style="{ color: gamma > 20 && usesGamma ? RED : MUTED }">
        <template v-if="usesGamma && gamma > 20">
          big γ: each point is treated as an island — almost every point becomes a
          support vector, and the boundary wraps the training set
        </template>
        <template v-else-if="type === 'linear'">
          one straight boundary, whatever the data looks like
        </template>
        <template v-else>
          γ sets how far one point's influence reaches; C still sets how much
          violation is allowed
        </template>
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.2fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; align-items: center; }
.side { display: flex; flex-direction: column; gap: 0.55rem; }
.formula { font-size: 0.88rem; margin: 0; font-weight: 600; }
.knobs { display: flex; flex-direction: column; gap: 0.4rem; }
.presets { display: flex; align-items: center; gap: 0.3rem; flex-wrap: wrap; }
.lab { color: v-bind(MUTED); font-size: 0.76rem; }
button {
  border: 1px solid #d8dadd; background: white; border-radius: 0.3rem;
  padding: 0.1rem 0.4rem; font-size: 0.72rem; cursor: pointer;
}
button:hover { border-color: v-bind(GREEN); color: v-bind(GREEN); }
button.warn:hover { border-color: v-bind(RED); color: v-bind(RED); }
.note { font-size: 0.75rem; margin: 0; line-height: 1.45; }
</style>
