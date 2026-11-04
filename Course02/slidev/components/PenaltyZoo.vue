<!-- penalty_zoo: ridge, lasso, best subset, and the family |β|^q that joins
     them: q = 2 is ridge, q = 1 the lasso, q → 0 counts the non-zeros. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { BLUE, GOLD, GREEN, RED } from '../lib/theme'

const q = ref(0.5)
const qcol = computed(() => (q.value >= 1.5 ? BLUE : q.value >= 0.75 ? GREEN : q.value > 0.05 ? GOLD : RED))
const zero = [[-2.2, 1], [-0.02, 1]] as [number, number][]
const zero2 = [[0.02, 1], [2.2, 1]] as [number, number][]
</script>

<template>
  <div class="cmp">
    <div class="r4">
      <div class="pz">
        <LineChart :series="[{ points: curve((b) => 0.5 * b * b, -2.2, 2.2), color: BLUE, width: 2.6 }]" :x-domain="[-2.2, 2.2]" :y-domain="[-0.15, 2.6]" :x-ticks="[0]" :y-ticks="[]" x-label="βⱼ" title="ridge: R(β) = ½‖β‖²" :title-color="BLUE" />
        <p>shrinks every coefficient</p><p class="note">explicit solution</p>
      </div>
      <div class="pz">
        <LineChart :series="[{ points: curve((b) => Math.abs(b), -2.2, 2.2), color: GREEN, width: 2.6 }]" :x-domain="[-2.2, 2.2]" :y-domain="[-0.15, 2.6]" :x-ticks="[0]" :y-ticks="[]" x-label="βⱼ" title="lasso: R(β) = ‖β‖₁" :title-color="GREEN" />
        <p>sets many of them to zero</p><p class="note">convex, not differentiable</p>
      </div>
      <div class="pz">
        <LineChart :series="[{ points: zero, color: RED, width: 2.6 }, { points: zero2, color: RED, width: 2.6 }]" :dots="[{ x: 0, y: 0, color: RED, r: 5 }, { x: 0, y: 1, color: RED, r: 5, hollow: true }]" :x-domain="[-2.2, 2.2]" :y-domain="[-0.15, 2.6]" :x-ticks="[0]" :y-ticks="[]" x-label="βⱼ" title="best subset: R(β) = ‖β‖₀" :title-color="RED" />
        <p>counts the ones you keep</p><p class="note">not convex, not differentiable</p>
      </div>
      <div class="pz">
        <LineChart :series="[{ points: curve((b) => Math.abs(b) ** q, -2.2, 2.2, 601), color: qcol, width: 2.6 }]" :x-domain="[-2.2, 2.2]" :y-domain="[-0.15, 2.6]" :x-ticks="[0]" :y-ticks="[]" x-label="βⱼ" :title="`in between: |βⱼ|^q, q = ${q.toFixed(2)}`" :title-color="qcol" />
        <p>{{ q >= 1 ? 'convex' : 'not convex' }}{{ q > 1 ? ', differentiable' : ', a kink at 0' }}</p><p class="note">q = 2 ridge, q = 1 lasso, q → 0 best subset</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="q" :min="0.02" :max="2.5" :step="0.01" label="exponent q" :color="qcol" />
    </div>
  </div>
</template>

<style scoped>
.pz { display: grid; grid-template-rows: 1fr auto auto; min-height: 0; text-align: center; font-size: 0.85rem; }
.pz p { margin: 0.15rem 0; }
.cmp { grid-template-rows: 1fr auto; }
</style>
