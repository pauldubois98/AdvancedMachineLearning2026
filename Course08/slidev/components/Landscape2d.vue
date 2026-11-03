<!-- landscape_2d: a validation-AUC surface over (log10 learning rate, max
     depth), tilted: the two knobs are not independent. The white contour
     encloses every setting within a tolerance of the best; click to score a
     setting of your own. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { valSurface } from '../lib/c08'
import { INK, PURPLE, viridis } from '../lib/theme'

const LO = 0.375
const HI = 0.86
const tol = ref(0.02)
const at = ref<[number, number]>([-3, 11])
const auc = computed(() => valSurface(at.value[0], at.value[1]))
const field = (x: number, y: number) => (valSurface(x, y) - LO) / (HI - LO)
const levels = computed(() => [
  ...[0.45, 0.55, 0.65, 0.75, 0.8].map((l) => ({ f: valSurface, level: l, color: 'rgba(255,255,255,0.55)', width: 0.8 })),
  { f: valSurface, level: HI - tol.value, color: '#ffffff', width: 2.6 },
])
// the best depth for a given learning rate, and the reverse: the ridge
const bestDepth = (le: number) => 6 - (0.010 / 0.0044) * (le + 1.5)
const along = computed(() => bestDepth(at.value[0]))
</script>

<template>
  <div class="wrap">
    <div class="note top">Two knobs, and they are not independent</div>
    <div class="body">
      <Plane
        :domain="[-4, 0, 2, 14]" :equal="false" axes x-label="log₁₀ learning rate η" y-label="max depth"
        :field="field" :field-color="viridis" :field-res="120" :levels="levels"
        :markers="[{ at: [-1.5, 6], color: '#ffffff', shape: 'star', size: 11 }, { at: at, color: INK, shape: 'ring', size: 7 }]"
        pickable @pick="(x: number, y: number) => (at = [Math.min(0, Math.max(-4, x)), Math.min(14, Math.max(2, y))])"
      />
      <div class="side">
        <div class="h">Interpretation</div>
        <p>— no need for the exact best (the star), but a 'good region': inside the white contour the AUC is within {{ tol.toFixed(3) }} of it</p>
        <p>— the parameters are not independent: the best depth depends on η</p>
        <div class="h">Your setting (click the map)</div>
        <p>η = 10<sup>{{ at[0].toFixed(2) }}</sup>, depth {{ at[1].toFixed(1) }}: AUC <b>{{ auc.toFixed(4) }}</b></p>
        <p class="note">at this η the best depth would be {{ Math.min(14, Math.max(2, along)).toFixed(1) }}</p>
        <p :style="{ color: PURPLE }">The star is not worth chasing to the last decimal.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="tol" :min="0.002" :max="0.15" :step="0.002" :digits="3" label="tolerance" />
      <span class="note">colour: validation AUC, from {{ LO }} (purple) to {{ HI }} (yellow)</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.25fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; border-left: 1px solid #cccfd2; padding-left: 1.6rem; font-size: 0.9rem; }
</style>
