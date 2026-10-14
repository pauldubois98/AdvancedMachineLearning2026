<!-- stability_idea: stability is the area of the bar. Two sliders per bar, so
     the trade-off between "many points" and "for a long time" is visible. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { GREEN, MUTED, RED } from '../lib/theme'

const bars = ref([
  { points: 18, span: 2.4, name: 'stable', color: GREEN },
  { points: 36, span: 0.5, name: 'unstable', color: RED },
])
const lamBirth = 0.45
const lamMax = 3.2
const area = (b: { points: number; span: number }) => b.points * b.span
const winner = computed(() => (area(bars.value[0]) >= area(bars.value[1]) ? 0 : 1))
</script>

<template>
  <div class="wrap">
    <div class="chart">
      <svg viewBox="0 0 400 300" preserveAspectRatio="none">
        <line x1="44" x2="44" y1="12" y2="272" stroke="#1b1b1b" stroke-width="1.1" />
        <template v-for="t in [0, 0.8, 1.6, 2.4, 3.2]" :key="t">
          <line :x1="40" :x2="44" :y1="12 + (t / lamMax) * 260" :y2="12 + (t / lamMax) * 260" stroke="#1b1b1b" />
          <text :x="37" :y="16 + (t / lamMax) * 260" class="tick">{{ t.toFixed(1) }}</text>
        </template>
        <template v-for="(b, i) in bars" :key="i">
          <rect
            :x="120 + i * 150 - b.points * 2" :y="12 + (lamBirth / lamMax) * 260"
            :width="b.points * 4" :height="(b.span / lamMax) * 260"
            :style="{ fill: b.color, fillOpacity: 0.3, stroke: b.color, strokeWidth: 1.6 }"
          />
          <text :x="120 + i * 150" :y="12 + (lamBirth / lamMax) * 260 - 7" class="mid" :style="{ fill: b.color, fontSize: '12px' }">
            {{ b.name }}
          </text>
          <text
            :x="120 + i * 150" :y="12 + ((lamBirth + b.span) / lamMax) * 260 + 15"
            class="mid" :style="{ fill: MUTED, fontSize: '11px' }"
          >{{ b.points }} points × {{ b.span.toFixed(2) }} of λ</text>
          <text
            :x="120 + i * 150" :y="12 + ((lamBirth + b.span / 2) / lamMax) * 260 + 4"
            class="mid" :style="{ fill: b.color, fontSize: '12.5px', fontWeight: 600 }"
          >{{ area(b).toFixed(1) }}</text>
        </template>
        <text x="12" y="150" class="axis" transform="rotate(-90 12 150)">λ = 1/ε</text>
      </svg>
      <div class="note">area = points × how long they stay</div>
    </div>
    <div class="right">
      <div class="formula">
        <Tex display formula='\text{stability}(C) = \sum_{x_i \in C} \left(\lambda_i - \lambda_{\text{birth}}(C)\right)' />
      </div>
      <p class="note">λ<sub>birth</sub>: where the bar starts, i.e. the ε at
        which the cluster split off its parent.</p>
      <p class="note">λ<sub>i</sub>: where point x<sub>i</sub> leaves the bar,
        either by falling out as noise or because the cluster splits.</p>
      <div class="controls">
        <Knob v-model="bars[0].points" :min="2" :max="60" :step="1" label="points, stable" :digits="0" :color="GREEN" />
        <Knob v-model="bars[0].span" :min="0.1" :max="2.7" label="λ it survives" :color="GREEN" />
        <Knob v-model="bars[1].points" :min="2" :max="60" :step="1" label="points, unstable" :digits="0" :color="RED" />
        <Knob v-model="bars[1].span" :min="0.1" :max="2.7" label="λ it survives" :color="RED" />
      </div>
      <Readout
        :items="[
          { label: 'stability, left bar', value: area(bars[0]).toFixed(1), color: GREEN },
          { label: 'right bar', value: area(bars[1]).toFixed(1), color: RED },
          { label: 'the more stable one', value: bars[winner].name, color: bars[winner].color },
        ]"
      />
      <p class="note">A wide, short bar is a crowd that immediately falls
        apart; a narrow, tall one is a handful of points that stay together over
        a long range of ε. Stability prefers whichever has the greater area, so
        the comparison is between points and persistence.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 0.95fr 1.1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.chart { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.chart .note { text-align: center; }
svg { width: 100%; height: 100%; min-height: 0; }
.tick { font-size: 11px; fill: #1b1b1b; text-anchor: end; }
.axis { font-size: 12px; fill: #1b1b1b; text-anchor: middle; }
.mid { text-anchor: middle; }
.right { display: flex; flex-direction: column; gap: 0.4rem; justify-content: center; }
.formula { font-size: 0.86rem; }
.controls { display: grid; grid-template-columns: 1fr 1fr; gap: 0.3rem 1rem; }
</style>
