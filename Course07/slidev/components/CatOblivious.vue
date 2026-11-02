<!-- cat_oblivious: one split per level turns the tree into a lookup table.
     Move the row's two features and watch the index it computes. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, GRID, INK, MUTED, PURPLE } from '../lib/theme'

const x3 = ref(0.2)
const x7 = ref(5)
const T1 = 0.4
const T2 = 2
const VALUES = [0.4, -1.2, 0.9, -0.1]

const bits = computed(() => {
  const b1 = x3.value < T1 ? 1 : 0
  const b2 = x7.value < T2 ? 1 : 0
  return { b1, b2, index: b1 * 2 + b2 }
})
const value = computed(() => VALUES[bits.value.index])
</script>

<template>
  <div class="wrap">
    <svg viewBox="0 0 100 52" preserveAspectRatio="xMidYMid meet">
      <!-- level 0: the test is answered once, and the answer is a bit -->
      <line x1="50" y1="8" x2="26" y2="20" :stroke="bits.b1 ? GRID : GREEN" :stroke-width="bits.b1 ? 0.4 : 0.8" />
      <line x1="50" y1="8" x2="74" y2="20" :stroke="bits.b1 ? GREEN : GRID" :stroke-width="bits.b1 ? 0.8 : 0.4" />
      <circle cx="50" cy="6" r="2.2" fill="#fff" :stroke="MUTED" stroke-width="0.4" />
      <text x="2" y="7" class="t" :fill="BLUE">x₃ &lt; {{ T1 }} ?</text>
      <text x="40" y="15" class="t2" :fill="MUTED">no 0</text>
      <text x="64" y="13" class="t2" :fill="MUTED">1 yes</text>
      <!-- level 1: the SAME test on both nodes -->
      <template v-for="(cx, i) in [26, 74]" :key="i">
        <circle :cx="cx" cy="22" r="2.2" fill="#fff" :stroke="MUTED" stroke-width="0.4" />
        <line
          :x1="cx" y1="24" :x2="cx - 10" y2="34"
          :stroke="bits.b1 === i && !bits.b2 ? GREEN : GRID"
          :stroke-width="bits.b1 === i && !bits.b2 ? 0.8 : 0.4"
        />
        <line
          :x1="cx" y1="24" :x2="cx + 10" y2="34"
          :stroke="bits.b1 === i && bits.b2 ? GREEN : GRID"
          :stroke-width="bits.b1 === i && bits.b2 ? 0.8 : 0.4"
        />
      </template>
      <text x="2" y="23" class="t" :fill="PURPLE">x₇ &lt; {{ T2 }} ?</text>
      <!-- the leaves, in the order the two bits index them -->
      <template v-for="(v, i) in VALUES" :key="i">
        <rect
          :x="[16, 36, 64, 84][i] - 8" y="34" width="16" height="9" rx="1.5" fill="#fff"
          :stroke="i === bits.index ? GREEN : GRID" :stroke-width="i === bits.index ? 0.9 : 0.4"
        />
        <text :x="[16, 36, 64, 84][i]" y="38" class="t2 mid" :fill="MUTED">[{{ i }}]</text>
        <text :x="[16, 36, 64, 84][i]" y="42" class="t mid" :fill="i === bits.index ? GREEN : INK">
          {{ (v >= 0 ? '+' : '') + v.toFixed(1) }}
        </text>
      </template>
      <text x="50" y="50" class="t2 mid" :fill="GREEN">four leaf values stored as one array of four numbers</text>
    </svg>
    <div class="side">
      <p class="lookup">
        <span :style="{ color: BLUE }">x₃ = {{ x3.toFixed(2) }}</span>
        → {{ bits.b1 ? 'yes → 1' : 'no → 0' }}<br />
        <span :style="{ color: PURPLE }">x₇ = {{ x7.toFixed(1) }}</span>
        → {{ bits.b2 ? 'yes → 1' : 'no → 0' }}<br />
        index = ({{ bits.b1 }},{{ bits.b2 }})₂ = <b>{{ bits.index }}</b>
        → <b :style="{ color: GREEN }">{{ (value >= 0 ? '+' : '') + value.toFixed(1) }}</b>
      </p>
      <div class="knobs">
        <Knob v-model="x3" :min="0" :max="1" label="x₃ of this row" :digits="2" :color="BLUE" />
        <Knob v-model="x7" :min="0" :max="8" label="x₇ of this row" :digits="1" :color="PURPLE" />
      </div>
      <p class="note">
        Every node of a level uses the same split, so the path is not a walk: it is two
        comparisons that produce two bits, and the bits are an array index. No branching,
        no pointer chasing, the same instructions for every row. This is why CatBoost
        predicts so fast, and it costs accuracy per tree, which it pays back in trees.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 1.6rem; height: 100%; min-height: 0; }
svg { width: 100%; height: 100%; min-height: 0; }
.t { font-size: 3px; }
.t2 { font-size: 2.4px; }
.mid { text-anchor: middle; }
.side { display: flex; flex-direction: column; justify-content: center; gap: 0.7rem; }
.lookup { font-size: 0.92rem; margin: 0; line-height: 1.7; }
.knobs { display: flex; flex-direction: column; gap: 0.35rem; }
.note { font-size: 0.78rem; color: var(--muted); margin: 0; line-height: 1.5; }
</style>
