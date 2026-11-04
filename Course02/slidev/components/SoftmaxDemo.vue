<!-- eq_softmax, live: three classes, class 3 the reference (its score is 0).
     Move the two log-odds and the three probabilities follow, adding to one. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, RED } from '../lib/theme'

const s1 = ref(1)
const s2 = ref(-0.5)
const p = computed(() => {
  const e = [Math.exp(s1.value), Math.exp(s2.value), 1], z = e[0] + e[1] + e[2]
  return e.map((v) => v / z)
})
const cols = [BLUE, RED, GREEN]
const best = computed(() => p.value.indexOf(Math.max(...p.value)))
</script>

<template>
  <div class="sm">
    <div class="knobs">
      <Knob v-model="s1" :min="-4" :max="4" :step="0.01" label="log-odds class 1 vs 3" :color="BLUE" />
      <Knob v-model="s2" :min="-4" :max="4" :step="0.01" label="log-odds class 2 vs 3" :color="RED" />
    </div>
    <div class="bars">
      <div v-for="(v, k) in p" :key="k" class="bar">
        <div class="fill" :style="{ width: `${100 * v}%`, background: cols[k], opacity: k === best ? 1 : 0.55 }" />
        <span class="lab">Pr(G = {{ k + 1 }} | x) = {{ v.toFixed(3) }}<b v-if="k === best"> ← k̂</b></span>
      </div>
      <div class="note">sum = {{ (p[0] + p[1] + p[2]).toFixed(3) }}</div>
    </div>
  </div>
</template>

<style scoped>
.sm { display: grid; grid-template-columns: 1fr 1.3fr; gap: 2rem; align-items: center; margin-top: 0.6rem; }
.knobs { display: grid; gap: 0.7rem; }
.bars { display: grid; gap: 0.35rem; font-size: 0.85rem; }
.bar { position: relative; height: 1.4rem; background: #f3f4f5; border-radius: 4px; overflow: hidden; }
.fill { position: absolute; inset: 0 auto 0 0; transition: width 0.1s; }
.lab { position: relative; padding-left: 0.5rem; line-height: 1.4rem; color: #1b1b1b; }
</style>
