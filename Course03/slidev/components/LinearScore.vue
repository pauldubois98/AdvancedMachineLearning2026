<!-- svm_setting: one linear score per point, the sign picks the class.
     Click anywhere to score a test point. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sepBlobs, toPm1 } from '../lib/data'
import { fitSvc, kernel } from '../lib/svm'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const data = sepBlobs(80, 2.6, 3)
const yPm = toPm1(data.y)
const model = fitSvc(data.X, yPm, 1000, kernel({ type: 'linear' }))
const probe = ref<[number, number] | null>([1.6, -1.6])
const f = computed(() => (probe.value ? model.decision(probe.value) : null))
</script>

<template>
  <div class="two-col">
    <FieldPlot
      :X="data.X" :y="data.y" :decision="model.decisionAt" :margins="false"
      :point-size="26" :probe="probe" @pick="probe = $event"
    />
    <div class="side">
      <p class="eq">f(x) = w<sup>T</sup>x + b</p>
      <p class="sub">one linear score per point</p>
      <p class="eq" :style="{ color: GREEN }">ŷ = sign f(x)</p>
      <p class="sub">the sign picks the class</p>
      <div class="probe">
        <p class="hint">click the panel to score a point</p>
        <template v-if="probe && f !== null">
          <p>
            f(<span class="num">{{ probe[0].toFixed(2) }}</span>,
            <span class="num">{{ probe[1].toFixed(2) }}</span>) =
            <strong class="num" :style="{ color: f > 0 ? RED : BLUE }">{{ f.toFixed(2) }}</strong>
          </p>
          <p>
            ŷ = <strong :style="{ color: f > 0 ? RED : BLUE }">{{ f > 0 ? '+1' : '−1' }}</strong>
            <span class="sub"> — the labels are ±1 here, so y<sub>i</sub> f(x<sub>i</sub>) &gt; 0 means “right”</span>
          </p>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.two-col { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.2rem; height: 100%; min-height: 0; }
.side { display: flex; flex-direction: column; justify-content: center; gap: 0.1rem; }
.eq { font-size: 1.25rem; margin: 0.3rem 0 0; }
.sub { color: v-bind(MUTED); font-size: 0.8rem; margin: 0; }
.probe { margin-top: 1.1rem; border-top: 1px solid #e3e5e8; padding-top: 0.6rem; font-size: 0.95rem; }
.probe p { margin: 0.2rem 0; }
.hint { color: v-bind(MUTED); font-size: 0.75rem; }
.num { font-variant-numeric: tabular-nums; }
</style>
