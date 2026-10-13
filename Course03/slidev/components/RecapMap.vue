<!-- svm_map: the whole lecture as four steps, each one a small change to the
     one before. Click a stage to be reminded what it bought. -->
<script setup lang="ts">
import { ref } from 'vue'
import { BLUE, GOLD, GREEN, MUTED, PURPLE } from '../lib/theme'

const stages = [
  {
    color: BLUE, title: 'widest street', sub: 'min ½‖w‖²',
    detail: 'Among the lines with no training error, pick the one with the widest empty band around it. The margin is 2/‖w‖, so widening it means shrinking ‖w‖.',
  },
  {
    color: GOLD, title: 'allow slack', sub: '+ C Σᵢ ξᵢ',
    detail: 'Real data overlaps. Let a point sit inside the street, or on the wrong side, and charge C per unit of violation. C is the one knob that trades margin against mistakes.',
  },
  {
    color: GREEN, title: 'go to the dual', sub: 'only xᵢᵀxⱼ left',
    detail: 'Rewriting the problem in the multipliers α leaves the data appearing only through inner products — and only the support vectors keep a non-zero α.',
  },
  {
    color: PURPLE, title: 'swap in a kernel', sub: 'k(xᵢ, xⱼ)',
    detail: 'Any inner product in any feature space will do, so replace xᵢᵀxⱼ by k(xᵢ, xⱼ). Curved boundaries at a linear price, and Φ is never built.',
  },
]
const open = ref(-1)
</script>

<template>
  <div class="wrap">
    <div class="row">
      <template v-for="(s, i) in stages" :key="i">
        <div
          class="stage" :class="{ on: open === i }"
          :style="{ borderColor: s.color, background: open === i ? `${s.color}12` : 'white' }"
          @mouseenter="open = i" @mouseleave="open = -1"
        >
          <p class="title" :style="{ color: s.color }">{{ s.title }}</p>
          <p class="sub">{{ s.sub }}</p>
        </div>
        <span v-if="i < stages.length - 1" class="arrow">→</span>
      </template>
    </div>
    <div class="detail" :style="{ borderColor: open >= 0 ? stages[open].color : 'transparent' }">
      <p v-if="open >= 0" :style="{ color: stages[open].color }">{{ stages[open].detail }}</p>
      <p v-else class="hint">hover a stage</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: flex; flex-direction: column; justify-content: center; gap: 1.4rem; height: 100%; }
.row { display: flex; align-items: center; justify-content: center; gap: 0.6rem; }
.stage {
  border: 2px solid; border-radius: 0.5rem; padding: 0.7rem 0.9rem;
  min-width: 9.5rem; text-align: center; transition: all 0.15s;
}
.title { font-weight: 700; font-size: 0.95rem; margin: 0; }
.sub { font-size: 0.82rem; margin: 0.25rem 0 0; }
.arrow { color: v-bind(MUTED); font-size: 1.1rem; }
.detail {
  border-left: 3px solid; padding: 0.3rem 0 0.3rem 0.9rem; min-height: 4.2rem;
  max-width: 48rem; margin: 0 auto; transition: border-color 0.15s;
}
.detail p { font-size: 0.86rem; margin: 0; line-height: 1.55; }
.hint { color: v-bind(MUTED); font-size: 0.8rem !important; }
</style>
