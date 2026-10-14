<!-- condense_example: at every split, count the two sides. Only a split where
     both sides still hold C_min points adds a branch. C_min is the slider. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { GREEN, GOLD, MUTED, RED } from '../lib/theme'

const cmin = ref(5)
const cases = ref([
  { n: 14, a: 8, b: 6 },
  { n: 14, a: 12, b: 2 },
  { n: 6, a: 4, b: 2 },
])
const verdicts = computed(() =>
  cases.value.map((c) => {
    const bigA = c.a >= cmin.value
    const bigB = c.b >= cmin.value
    if (bigA && bigB) {
      return {
        ...c, color: GREEN, title: 'real split',
        why: `both sides are big enough: two new clusters of ${c.a} and ${c.b}`,
        kind: 'split' as const,
      }
    }
    if (bigA || bigB) {
      const keep = bigA ? c.a : c.b
      const drop = bigA ? c.b : c.a
      return {
        ...c, color: GOLD, title: 'some points fall out',
        why: `one side is too small: those ${drop} are noise, and the cluster carries on as ${keep}`,
        kind: 'fall' as const,
      }
    }
    return {
      ...c, color: RED, title: 'cluster dies',
      why: `neither side survives: its last ${c.n} points are all noise`,
      kind: 'die' as const,
    }
  }),
)
const branches = computed(() => verdicts.value.filter((v) => v.kind === 'split').length)
</script>

<template>
  <div class="wrap">
    <div class="head note">
      C<sub>min</sub> = {{ cmin }}: at every split of the single-linkage tree,
      count the two sides
    </div>
    <div class="cases">
      <div v-for="(v, i) in verdicts" :key="i" class="case">
        <div class="bar" :style="{ width: `${v.n * 7}px`, background: v.kind === 'die' ? RED : v.color }" />
        <div class="size">{{ v.n }}</div>
        <div class="sides">
          <div v-for="(m, s) in [v.a, v.b]" :key="s" class="side">
            <template v-if="m >= cmin">
              <div class="bar small" :style="{ width: `${m * 7}px`, background: v.color }" />
              <div class="size">{{ m }}</div>
            </template>
            <template v-else>
              <div class="dots">
                <span v-for="d in m" :key="d" class="dot" />
              </div>
              <div class="size" :style="{ color: MUTED }">{{ m }} → noise</div>
            </template>
          </div>
        </div>
        <div class="verdict" :style="{ color: v.color }">{{ v.title }}</div>
        <div class="note why">{{ v.why }}</div>
        <div class="knobs">
          <Knob v-model="cases[i].a" :min="1" :max="20" :step="1" label="left" :digits="0" :color="v.color" />
          <Knob v-model="cases[i].b" :min="1" :max="20" :step="1" label="right" :digits="0" :color="v.color" />
        </div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="cmin" :min="2" :max="14" :step="1" label="C<sub>min</sub>" :digits="0" :color="GREEN" />
      <Readout
        :items="[
          { label: 'cases that add a branch', value: `${branches} of 3`, color: GREEN },
        ]"
      />
      <span class="note">only a real split adds a branch, so the condensed tree
        has far fewer than n − 1 of them</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.head { text-align: center; }
.cases { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.6rem; align-items: start; align-content: center; }
.case { display: flex; flex-direction: column; align-items: center; gap: 0.2rem; }
.case + .case { border-left: 1px solid #cccfd2; padding-left: 1.6rem; }
.bar { height: 34px; border-radius: 2px; opacity: 0.85; }
.bar.small { height: 26px; }
.size { font-size: 0.78rem; }
.sides { display: flex; gap: 1.6rem; align-items: start; margin-top: 0.3rem; }
.side { display: flex; flex-direction: column; align-items: center; gap: 0.15rem; }
.dots { display: flex; flex-wrap: wrap; width: 46px; justify-content: center; gap: 2px; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: #9aa0a6; }
.verdict { font-size: 0.88rem; font-weight: 600; margin-top: 0.35rem; }
.why { text-align: center; max-width: 15rem; }
.knobs { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem; width: 100%; margin-top: 0.35rem; }
.controls { display: flex; gap: 1.4rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 11rem; }
</style>
