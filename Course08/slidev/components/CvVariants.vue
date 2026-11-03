<!-- cv_variants: four ways to cut the folds when the rows are not
     exchangeable. The round slider steps every scheme through its rounds:
     gold is held out, blue is trained on, grey is unused. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GOLD, GREEN, LIGHT, PURPLE, RED } from '../lib/theme'

const round = ref(1)
const k = computed(() => round.value - 1)
// stratified: 5 folds of 4 rows, the rare class once in each
const strat = computed(() => Array.from({ length: 5 }, (_, f) => ({ held: f === k.value, rows: [0, 1, 2, 3].map((j) => (j === 2 ? RED : BLUE)) })))
// grouped: 5 subjects, 4 rows each, shuffled in the table; a fold is a subject
const SUBJ = ['#fdd982', '#fbb447', '#f28a2a', '#d9590f', '#9c3407']
const ORDER = [0, 3, 1, 4, 0, 2, 3, 1, 2, 4, 1, 0, 4, 2, 3, 0, 1, 4, 2, 3]
// time series: train on the past, test on the next three
const ts = computed(() => {
  const end = 6 + 4 * (k.value % 3)
  return Array.from({ length: 20 }, (_, i) => (i < end ? BLUE : i < end + 3 ? GOLD : LIGHT))
})
// blocked: a 4 x 14 grid, a 2 x 3 block held out with a one-cell buffer
const blocked = computed(() => {
  const c0 = 1 + 3 * (k.value % 4)
  return Array.from({ length: 4 }, (_, r) => Array.from({ length: 14 }, (_, c) => {
    const inBlock = r >= 1 && r <= 2 && c >= c0 && c < c0 + 3
    const inBuf = r >= 0 && r <= 3 && c >= c0 - 1 && c < c0 + 4
    return inBlock ? GOLD : inBuf ? LIGHT : BLUE
  }))
})
</script>

<template>
  <div class="wrap">
    <div class="grid">
      <section>
        <h4 :style="{ color: BLUE }">stratified: imbalanced data</h4>
        <div class="folds">
          <div v-for="(f, i) in strat" :key="i" class="fold" :class="{ held: f.held }">
            <div class="cells"><span v-for="(c, j) in f.rows" :key="j" :style="{ background: c }" /></div>
            <div class="n">{{ i + 1 }}</div>
          </div>
        </div>
        <p class="note">Folds keep the same share of the rare class (red); fold {{ k % 5 + 1 }} is held out.</p>
      </section>
      <section>
        <h4 :style="{ color: GOLD }">grouped: separating the subjects</h4>
        <div class="cells line"><span v-for="(s, i) in ORDER" :key="i" :style="{ background: SUBJ[s], outline: s === k % 5 ? '2px solid #1b1b1b' : 'none' }" /></div>
        <div class="cells line groups">
          <template v-for="s in 5" :key="s">
            <span v-for="j in 4" :key="j" :style="{ background: SUBJ[s - 1], opacity: s - 1 === k % 5 ? 1 : 0.35 }" />
          </template>
        </div>
        <p class="note">Rows are regrouped: one fold per subject; subject {{ k % 5 + 1 }} held out.</p>
      </section>
      <section>
        <h4 :style="{ color: GREEN }">time series: ordered data</h4>
        <div class="cells line"><span v-for="(c, i) in ts" :key="i" :style="{ background: c }" /></div>
        <p class="note">Train on the past, score on the future → time</p>
      </section>
      <section>
        <h4 :style="{ color: PURPLE }">blocked: correlated neighbours</h4>
        <div class="block">
          <div v-for="(row, r) in blocked" :key="r" class="cells line"><span v-for="(c, j) in row" :key="j" :style="{ background: c }" /></div>
        </div>
        <p class="note">Neighbourhoods are held out together, with a buffer (grey)</p>
      </section>
    </div>
    <div class="controls">
      <Knob v-model="round" :min="1" :max="12" :step="1" :digits="0" label="round" />
      <span class="note">gold: held out · blue: trained on · grey: not used</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.grid { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 0.8rem 2.5rem; }
section { display: flex; flex-direction: column; gap: 0.45rem; justify-content: center; }
h4 { margin: 0; font-weight: 700; font-size: 1rem; }
.folds { display: flex; gap: 0.6rem; }
.fold { flex: 1; padding: 3px; border: 2px solid transparent; border-radius: 4px; }
.fold.held { border-color: #b7791f; background: #fdf8ef; }
.n { text-align: center; color: #9aa0a6; font-size: 0.75rem; }
.cells { display: flex; gap: 2px; }
.cells span { flex: 1; height: 2.2rem; }
.cells.line span { height: 1.5rem; }
.groups { gap: 2px; }
.groups span:nth-child(4n) { margin-right: 8px; }
.block { display: grid; gap: 2px; }
.block .cells span { height: 1.1rem; }
p { margin: 0; }
</style>
