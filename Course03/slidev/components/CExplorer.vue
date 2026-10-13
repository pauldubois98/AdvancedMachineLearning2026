<!-- svm_c: C is the exchange rate between a wide street and few violations.
     Soft (small C): a wide street, violations tolerated.
     Hard (large C): a narrow street that fits the training points. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sepBlobs, toPm1 } from '../lib/data'
import { fitSvc, kernel } from '../lib/svm'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'
import { dataDomain } from '../lib/plot'

const C = ref(1)
const data = sepBlobs(160, 1.5, 5)
const yPm = toPm1(data.y)
const domain = dataDomain(data.X, 0.7)
const model = computed(() => fitSvc(data.X, yPm, C.value, kernel({ type: 'linear' })))

const errors = computed(() => {
  let n = 0
  for (let i = 0; i < data.X.length; i++)
    if (model.value.predict(data.X[i]) !== yPm[i]) n++
  return n
})
const tone = computed(() => (C.value < 0.2 ? GREEN : C.value > 20 ? RED : BLUE))

/** how the street and the support set move as C sweeps its whole range */
const sweep = (() => {
  const pts: { C: number; width: number; nsv: number }[] = []
  for (let i = 0; i <= 24; i++) {
    const c = 10 ** (-2 + (4 * i) / 24)
    const m = fitSvc(data.X, yPm, c, kernel({ type: 'linear' }))
    pts.push({ C: c, width: m.marginWidth ?? 0, nsv: m.sv.length })
  }
  return pts
})()
const widthSeries = sweep.map((p) => [p.C, p.width] as [number, number])
const svSeries = sweep.map((p) => [p.C, p.nsv / data.X.length] as [number, number])
</script>

<template>
  <div class="wrap">
    <FieldPlot
      :X="data.X" :y="data.y" :decision="model.decisionAt" :domain="domain"
      :rings="[{ idx: model.sv, color: GREEN, size: 46, width: 1.1 }]" :point-size="14"
    />
    <div class="right">
      <LineChart
        :series="[
          { points: widthSeries, color: '#b7791f', width: 2.4 },
          { points: svSeries, color: '#00ab0e', width: 2.2, dash: '5,4' },
        ]"
        :vlines="[{ x: C, color: tone, dash: '' }]"
        :x-domain="[0.01, 100]" :y-domain="[0, 2.6]" log-x
        :x-ticks="[0.01, 0.1, 1, 10, 100]" :y-ticks="[0, 1, 2]"
        x-label="C" title="street width and support-vector share"
        :labels="[
          { x: 0.02, y: 2.45, text: 'street width', color: '#b7791f', size: 12 },
          { x: 0.02, y: 2.15, text: 'share of points that are SVs', color: '#00ab0e', size: 12 },
        ]"
      />
      <div class="controls">
        <Knob v-model="C" :min="0.01" :max="100" log label="C" :color="tone" />
        <Readout
          :items="[
            { label: 'street', value: (model.marginWidth ?? 0).toFixed(2), color: '#b7791f' },
            { label: 'support vectors', value: `${model.sv.length} / ${data.X.length}`, color: GREEN },
            { label: 'training mistakes', value: String(errors), color: errors ? RED : GREEN },
          ]"
        />
        <p class="note" :style="{ color: tone }">
          <template v-if="C < 0.2">soft: a wide street, violations tolerated</template>
          <template v-else-if="C > 20">hard: a narrow street, fits the training points</template>
          <template v-else>in between: the usual compromise</template>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1.05fr; gap: 1.4rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.note { font-size: 0.8rem; margin: 0; font-weight: 600; }
</style>
