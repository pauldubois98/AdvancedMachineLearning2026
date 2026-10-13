<!-- not_separable: push the two clouds together until no line can get
     everything right, and the hard-margin problem stops having a solution. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sepBlobs, toPm1 } from '../lib/data'
import { fitSvc, kernel } from '../lib/svm'
import { GREEN, MUTED, RED } from '../lib/theme'
import { dataDomain } from '../lib/plot'

const gap = ref(1.5)
const soft = ref(true)

const data = computed(() => sepBlobs(160, gap.value, 5))
const yPm = computed(() => toPm1(data.value.y))
const model = computed(() =>
  fitSvc(data.value.X, yPm.value, soft.value ? 1 : 1e6, kernel({ type: 'linear' })),
)
const wrong = computed(() => {
  const out: number[] = []
  const m = model.value
  for (let i = 0; i < data.value.X.length; i++)
    if (m.predict(data.value.X[i]) !== yPm.value[i]) out.push(i)
  return out
})
const domain = computed(() => dataDomain(sepBlobs(160, 3.4, 5).X, 0.7))
const separable = computed(() => wrong.value.length === 0)
</script>

<template>
  <div class="wrap">
    <FieldPlot
      :X="data.X" :y="data.y" :decision="model.decisionAt" :domain="domain"
      :rings="[{ idx: wrong, color: RED, size: 110, width: 1.6 }]" :point-size="20"
    />
    <div class="side">
      <Knob v-model="gap" :min="0.2" :max="3.4" :step="0.02" label="push the clouds apart" :color="MUTED" />
      <Toggle v-model="soft" label="allow a few mistakes (soft margin, C = 1)" :color="GREEN" />
      <Readout
        :items="[
          { label: 'mistakes', value: String(wrong.length), color: wrong.length ? RED : GREEN },
          { label: 'support vectors', value: String(model.sv.length), color: GREEN },
          { label: 'street', value: (model.marginWidth ?? 0).toFixed(2) },
        ]"
      />
      <p class="note" :style="{ color: separable ? GREEN : RED }">
        <template v-if="separable">
          a gap exists: the hard-margin problem has a solution
        </template>
        <template v-else-if="soft">
          no line gets everything right — the {{ wrong.length }} circled points are
          the ones the soft margin gives up on
        </template>
        <template v-else>
          with no slack allowed the constraints cannot all hold at once:
          the hard-margin problem has no solution at all
        </template>
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; align-items: center; }
.side { display: flex; flex-direction: column; gap: 0.7rem; }
.note { font-size: 0.82rem; margin: 0; line-height: 1.5; }
</style>
