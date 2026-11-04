<!-- thresholding: with orthonormal columns each penalty acts coordinate by
     coordinate on the least squares β̂ⱼ: weight decay, soft and hard
     thresholding. The slider moves λ; the dot follows one coefficient. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { fmt, hard, soft } from '../lib/reg'
import { BLUE, GRID, GREEN, INK, RED } from '../lib/theme'

const lam = ref(1)
const b = ref(1.8)
const maps = computed(() => [
  { name: 'ridge', f: (v: number) => v / (1 + lam.value), color: BLUE, formula: 'β̂ⱼ / (1 + λ)', label: 'weight decay' },
  { name: 'lasso', f: (v: number) => soft(v, lam.value), color: GREEN, formula: 'sign(β̂ⱼ)(|β̂ⱼ| − λ)₊', label: 'soft thresholding' },
  { name: 'best subset', f: (v: number) => hard(v, lam.value), color: RED, formula: 'β̂ⱼ · δ(β̂ⱼ² ≥ 2λ)', label: 'hard thresholding' },
])
</script>

<template>
  <div class="cmp">
    <div class="r3">
      <div v-for="m in maps" :key="m.name" class="th">
        <LineChart :series="[{ points: [[-3, -3], [3, 3]], color: GRID, dash: '5,4', width: 1.4 }, { points: curve(m.f, -3, 3, 601), color: m.color, width: 2.8 }]"
          :dots="[{ x: b, y: m.f(b), color: m.color, r: 5.5 }]" :vlines="m.name === 'lasso' ? [{ x: -lam, color: GREEN }, { x: lam, color: GREEN }] : m.name === 'best subset' ? [{ x: -Math.sqrt(2 * lam), color: RED }, { x: Math.sqrt(2 * lam), color: RED }] : []"
          :x-domain="[-3, 3]" :y-domain="[-3, 3]" :x-ticks="[-2, 0, 2]" :y-ticks="[-2, 0, 2]" x-label="β̂ⱼ from least squares" y-label="after the penalty"
          :title="`${m.name}: ${m.formula}`" :title-color="m.color" />
        <div class="cap" :style="{ color: m.color }">{{ m.label }}: {{ fmt(b) }} → {{ fmt(m.f(b)) }}</div>
      </div>
    </div>
    <div class="foot">orthonormal columns (XᵀX = I): each coefficient is treated on its own</div>
    <div class="controls">
      <Knob v-model="lam" :min="0" :max="2.5" :step="0.01" label="λ" :color="INK" />
      <Knob v-model="b" :min="-3" :max="3" :step="0.01" label="one β̂ⱼ" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.th { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
</style>
