<!-- eq_xgboost: every term of the objective is a thing you can point at, so
     every term here carries the number it currently has, on a tree that is
     actually grown with the lambda and gamma on the sliders. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { growTree, leafValue, score, splitDemo } from '../lib/gbm'
import { BLUE, GREEN, MUTED, PURPLE, RED } from '../lib/theme'

const lambda = ref(1)
const gamma = ref(0.5)
const demo = splitDemo()

const tree = computed(() =>
  growTree(demo.X, demo.g, demo.h, {
    mode: 'leaf', maxLeaves: 8, lambda: lambda.value, gamma: gamma.value,
  }),
)
const parts = computed(() => {
  const t = tree.value
  const ws = t.leaves.map((l) => leafValue(l.G, l.H, lambda.value))
  const fit = -0.5 * t.leaves.reduce((s, l) => s + score(l.G, l.H, lambda.value), 0)
  return {
    T: t.leaves.length,
    ws,
    fit,
    complexity: gamma.value * t.leaves.length,
    ridge: 0.5 * lambda.value * ws.reduce((s, w) => s + w * w, 0),
    biggest: Math.max(...ws.map(Math.abs)),
  }
})
</script>

<template>
  <div class="box">
    <div class="terms">
      <div class="term">
        <span class="sym" :style="{ color: BLUE }">−½ Σⱼ Gⱼ²/(Hⱼ+λ)</span>
        <span class="val" :style="{ color: BLUE }">{{ parts.fit.toFixed(2) }}</span>
        <span class="gloss">the loss term once every leaf takes its best value: how much the tree takes off (negative is better)</span>
      </div>
      <div class="plus">+</div>
      <div class="term">
        <span class="sym" :style="{ color: RED }">γ T</span>
        <span class="val" :style="{ color: RED }">{{ parts.complexity.toFixed(2) }}</span>
        <span class="gloss">γ is the price of one leaf: it charges for complexity, so it prunes</span>
      </div>
      <div class="plus">+</div>
      <div class="term">
        <span class="sym" :style="{ color: PURPLE }">½ λ Σⱼ wⱼ²</span>
        <span class="val" :style="{ color: PURPLE }">{{ parts.ridge.toFixed(2) }}</span>
        <span class="gloss">λ shrinks every leaf value toward 0: no leaf shouts</span>
      </div>
    </div>
    <div class="knobs">
      <Knob v-model="lambda" :min="0.01" :max="100" log label="λ" :color="PURPLE" />
      <Knob v-model="gamma" :min="0" :max="6" label="γ" :digits="2" :color="RED" />
      <Readout
        :items="[
          { label: 'leaves the tree keeps, T', value: String(parts.T), color: RED },
          { label: 'biggest leaf value', value: parts.biggest.toFixed(3), color: PURPLE },
          { label: 'objective', value: (parts.fit + parts.complexity + parts.ridge).toFixed(2) },
        ]"
      />
    </div>
    <div class="leaves">
      <span class="lab">leaf values wⱼ*</span>
      <span v-for="(w, i) in parts.ws" :key="i" class="chip" :style="{ color: w < 0 ? BLUE : RED }">
        {{ (w >= 0 ? '+' : '') + w.toFixed(2) }}
      </span>
    </div>
    <p class="note">
      T is the number of leaves, wⱼ the value the tree outputs in leaf j. Raise γ and
      the tree stops splitting; raise λ and it keeps its leaves but speaks more quietly.
    </p>
  </div>
</template>

<style scoped>
.box { display: flex; flex-direction: column; gap: 0.9rem; }
.terms { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap: 0 0.8rem; align-items: start; }
.term { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 0.2rem; }
.sym { font-size: 1rem; }
.val { font-size: 1.35rem; font-weight: 600; font-variant-numeric: tabular-nums; }
.gloss { font-size: 0.76rem; color: var(--muted); line-height: 1.4; }
.plus { font-size: 1.2rem; align-self: center; color: var(--muted); }
.knobs { display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; justify-content: center; }
.knobs > :nth-child(-n+2) { min-width: 10rem; }
.leaves { display: flex; gap: 0.5rem; align-items: baseline; justify-content: center; flex-wrap: wrap; font-size: 0.82rem; }
.lab { color: var(--muted); }
.chip { font-variant-numeric: tabular-nums; font-weight: 600; }
.note { font-size: 0.8rem; color: var(--muted); margin: 0; text-align: center; }
</style>
