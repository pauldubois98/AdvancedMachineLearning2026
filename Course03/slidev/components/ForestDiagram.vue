<!-- forest_diagram: two injections of randomness, one vote. The slider is how
     many trees the picture draws, which is the only thing M changes. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, GRID, MUTED } from '../lib/theme'

const M = ref(5)
const trees = computed(() => Array.from({ length: Math.round(M.value) }, (_, i) => i + 1))
const xs = computed(() => {
  const n = trees.value.length
  return trees.value.map((_, i) => 8 + ((i + 0.5) / n) * 64)
})
</script>

<template>
  <div class="wrap">
    <svg viewBox="0 0 100 62" preserveAspectRatio="xMidYMid meet">
      <g>
        <rect x="28" y="1" width="24" height="7" rx="2" fill="#fff" stroke="#1b1b1b" stroke-width="0.4" />
        <text x="40" y="5.6" class="mid t3">training data</text>
        <template v-for="(x, i) in xs" :key="i">
          <line :x1="40" :y1="8" :x2="x" :y2="14" :stroke="GRID" stroke-width="0.3" />
          <rect :x="x - 7" y="14" width="14" height="9" rx="2" fill="#fff" :stroke="BLUE" stroke-width="0.5" />
          <text :x="x" y="18.2" class="mid t2">bootstrap</text>
          <text :x="x" y="21.4" class="mid t2">sample {{ i + 1 }}</text>
          <line :x1="x" :y1="23" :x2="x" :y2="29" :stroke="GRID" stroke-width="0.3" />
          <rect :x="x - 7" y="29" width="14" height="9" rx="2" fill="#fff" :stroke="GREEN" stroke-width="0.5" />
          <text :x="x" y="33" class="mid t2">deep</text>
          <text :x="x" y="36.2" class="mid t2">tree {{ i + 1 }}</text>
          <line :x1="x" :y1="38" :x2="40" :y2="45" :stroke="GRID" stroke-width="0.3" />
        </template>
        <rect x="24" y="45" width="32" height="8" rx="2" fill="#fff" :stroke="GREEN" stroke-width="0.5" />
        <text x="40" y="50" class="mid t3">average / majority vote</text>
        <text x="76" y="18" class="t2b" :fill="BLUE">① rows drawn</text>
        <text x="76" y="21.5" class="t2b" :fill="BLUE">with replacement</text>
        <text x="76" y="33" class="t2b" :fill="GREEN">② √p random</text>
        <text x="76" y="36.5" class="t2b" :fill="GREEN">columns per split</text>
        <text x="40" y="59" class="mid t2m">
          the two are independent: either alone already decorrelates the trees, both together more
        </text>
      </g>
    </svg>
    <div class="controls">
      <Knob v-model="M" :min="2" :max="8" :step="1" label="trees in the picture, M" :digits="0" :color="GREEN" />
      <p class="note">
        a real forest sets M to a few hundred; the picture stops at eight for room.
        Nothing in the recipe changes with M, which is why more trees never hurts.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
svg { width: 100%; height: 100%; min-height: 0; }
.mid { text-anchor: middle; }
.t3 { font-size: 2.6px; fill: #1b1b1b; }
.t2 { font-size: 2.1px; fill: #1b1b1b; }
.t2b { font-size: 2.4px; }
.t2m { font-size: 2.3px; fill: #9aa0a6; }
.controls { display: flex; flex-direction: column; gap: 0.3rem; }
.controls > :first-child { max-width: 22rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
