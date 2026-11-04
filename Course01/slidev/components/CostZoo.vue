<!-- cost_zoo: squared, absolute and 0-1 costs give the posterior mean, median
     and mode. Reshape the posterior and watch the three answers part. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { postGrid } from '../lib/post'
import { GOLD, GREEN, PURPLE, RED } from '../lib/theme'

const w = ref(0.65)
const gap = ref(2.2)
const P = computed(() => postGrid(w.value, 1.6, 0.75, 1.6 + gap.value, 0.55))
const cols = [GREEN, GOLD, RED]
const names = ['the posterior mean: MMSE', 'the posterior median', 'the posterior mode: MAP']
const titles = ['squared cost (θ − a)²', 'absolute cost |θ − a|', '0-1 cost 𝟙[θ ≠ a]']
const vals = computed(() => [P.value.mean, P.value.median, P.value.mode])
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>The posterior</b> is a mix of two bumps; the sliders set the weight of the left one and the distance between them. Each panel reports the answer that minimises one cost on average.</div>
    <div class="r3">
      <LineChart v-for="k in 3" :key="k" :series="[{ points: P.curve, color: PURPLE }]" :ribbons="[{ points: P.curve.map(([x, y]) => [x, 0, y]), color: PURPLE, alpha: 0.1 }]"
        :x-domain="[-1.5, 6.5]" :y-domain="[0, P.top * 1.2]" :x-ticks="[0, 2, 4, 6]" :y-ticks="[]" x-label="θ"
        :vlines="[{ x: vals[k - 1], color: cols[k - 1], dash: '' }]" :labels="[{ x: vals[k - 1] + 0.12, y: P.top * 1.08, text: vals[k - 1].toFixed(2), color: cols[k - 1] }]"
        :title="titles[k - 1]" :title-color="cols[k - 1]" />
    </div>
    <div class="r3 foot"><span v-for="k in 3" :key="k" :style="{ color: cols[k - 1] }">{{ names[k - 1] }}</span></div>
    <div class="controls">
      <Knob v-model="w" :min="0.05" :max="0.95" :step="0.01" label="weight of the left bump" :color="PURPLE" />
      <Knob v-model="gap" :min="0" :max="4" :step="0.02" label="distance between bumps" :color="PURPLE" />
    </div>
  </div>
</template>
