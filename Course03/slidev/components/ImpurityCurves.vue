<!-- impurity: what "pure" means. The slider is the share of class 1 in the
     node; the three measures are read off at that share. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { entropy, gini, misclass } from '../lib/tree'
import { BLUE, GOLD, GREEN, INK, MUTED, RED } from '../lib/theme'

const p = ref(0.5)
const N = 40

const curves = computed(() => {
  const g: [number, number][] = []
  const e: [number, number][] = []
  const m: [number, number][] = []
  for (let i = 0; i <= 200; i++) {
    const q = i / 200
    g.push([q, gini([1 - q, q], 1)])
    e.push([q, entropy([1 - q, q], 1) / 2])
    m.push([q, misclass([1 - q, q], 1)])
  }
  return { g, e, m }
})

const at = computed(() => ({
  gini: gini([1 - p.value, p.value], 1),
  entropy: entropy([1 - p.value, p.value], 1),
  misclass: misclass([1 - p.value, p.value], 1),
}))

/** the node itself: N points, a share p of them class 1 */
const node = computed(() => {
  const rng = new Rng(3)
  const pts: { x: number; y: number; cls: number }[] = []
  const k = Math.round(p.value * N)
  for (let i = 0; i < N; i++)
    pts.push({ x: rng.uniform(0.06, 0.94), y: rng.uniform(0.2, 0.8), cls: i < k ? 1 : 0 })
  return pts
})
const verdict = computed(() =>
  at.value.gini < 0.05 ? 'pure: nothing left to split'
  : at.value.gini > 0.45 ? 'maximally impure: a 50/50 node'
  : 'in between',
)
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="[
        { points: curves.g, color: BLUE, width: 2.6 },
        { points: curves.e, color: GOLD, width: 2.6 },
        { points: curves.m, color: MUTED, width: 2.2, dash: '5,4' },
      ]"
      :vlines="[{ x: p, color: INK, dash: '' }]"
      :dots="[
        { x: p, y: at.gini, color: BLUE, r: 5 },
        { x: p, y: at.entropy / 2, color: GOLD, r: 5 },
        { x: p, y: at.misclass, color: MUTED, r: 5 },
      ]"
      :x-domain="[0, 1]" :y-domain="[0, 0.56]"
      :x-ticks="[0, 0.25, 0.5, 0.75, 1]" :y-ticks="[0, 0.25, 0.5]"
      x-label="share of class 1 in the node, p" y-label="impurity"
      title="maximal at 50/50, zero when pure"
      :labels="[
        { x: 0.03, y: 0.53, text: 'Gini  2p(1−p)', color: BLUE, size: 12 },
        { x: 0.03, y: 0.49, text: 'entropy (÷2)', color: GOLD, size: 12 },
        { x: 0.03, y: 0.45, text: 'misclassification', color: MUTED, size: 12 },
      ]"
    />
    <div class="right">
      <div class="node">
        <svg viewBox="0 0 300 120" preserveAspectRatio="xMidYMid meet">
          <rect x="4" y="4" width="292" height="112" rx="8" fill="#fbfbfc" stroke="#cccfd2" />
          <template v-for="(pt, i) in node" :key="i">
            <circle
              v-if="pt.cls === 0" :cx="pt.x * 292 + 4" :cy="pt.y * 112 + 4" r="4.6"
              :style="{ fill: BLUE }"
            />
            <polygon
              v-else
              :points="`${pt.x * 292 + 4},${pt.y * 112 - 1.4} ${pt.x * 292 + 9},${pt.y * 112 + 8.6} ${pt.x * 292 - 1},${pt.y * 112 + 8.6}`"
              :style="{ fill: RED }"
            />
          </template>
        </svg>
        <p class="verdict" :style="{ color: at.gini < 0.05 ? GREEN : at.gini > 0.45 ? RED : INK }">
          {{ verdict }}
        </p>
      </div>
      <div class="controls">
        <Knob v-model="p" :min="0" :max="1" label="share of class 1, p" :digits="2" />
        <Readout
          :items="[
            { label: 'Gini', value: at.gini.toFixed(3), color: BLUE },
            { label: 'entropy', value: at.entropy.toFixed(3), color: GOLD },
            { label: 'misclassification', value: at.misclass.toFixed(3), color: MUTED },
          ]"
        />
        <p class="note">
          a split is good when both children are purer: the score of a split is the
          impurity of its children, weighted by how many rows each one gets
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 1.4rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; min-height: 0; }
.node { display: flex; flex-direction: column; justify-content: center; min-height: 0; }
.node svg { width: 100%; max-height: 10rem; }
.verdict { text-align: center; font-size: 0.85rem; font-weight: 600; margin: 0.3rem 0 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
