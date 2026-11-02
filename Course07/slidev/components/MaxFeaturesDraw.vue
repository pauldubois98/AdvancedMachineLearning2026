<!-- max_features: what the knob literally does. A fresh draw of columns at
     every node, and the winner is the best of the drawn ones, never of all. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { BLUE, GREEN, GRID, MUTED, RED } from '../lib/theme'

const p = ref(12)
const k = ref(4)
const draw = ref(1)
const ROWS = ['root', 'left child', 'right child', 'and so on']

const rows = computed(() => {
  const rng = new Rng(draw.value * 101 + Math.round(p.value) * 7 + Math.round(k.value))
  const P = Math.round(p.value)
  const K = Math.min(Math.round(k.value), P)
  return ROWS.map((name) => {
    const all = Array.from({ length: P }, (_, i) => i)
    for (let i = P - 1; i > 0; i--) {
      const j = Math.floor(rng.next() * (i + 1))
      const t = all[i]
      all[i] = all[j]
      all[j] = t
    }
    const drawn = all.slice(0, K).sort((a, b) => a - b)
    return { name, drawn, winner: drawn[Math.floor(rng.next() * K)] }
  })
})
const sqrtP = computed(() => Math.round(Math.sqrt(Math.round(p.value))))
</script>

<template>
  <div class="wrap">
    <div class="grid">
      <p class="head">p = {{ Math.round(p) }} columns, max_features = {{ Math.min(Math.round(k), Math.round(p)) }}</p>
      <div v-for="r in rows" :key="r.name" class="row">
        <span class="name">{{ r.name }}</span>
        <span
          v-for="c in Math.round(p)" :key="c" class="cell"
          :style="{
            background: r.drawn.includes(c - 1) ? '#dce7f3' : '#fff',
            borderColor: c - 1 === r.winner ? GREEN : r.drawn.includes(c - 1) ? BLUE : GRID,
            borderWidth: c - 1 === r.winner ? '2.2px' : '1px',
            color: r.drawn.includes(c - 1) ? '#1b1b1b' : GRID,
          }"
        >x<sub>{{ c }}</sub></span>
        <span class="best" :style="{ color: GREEN }">best: x<sub>{{ r.winner + 1 }}</sub></span>
      </div>
      <p class="note red">A new draw at every node, not once per tree.</p>
    </div>
    <div class="side">
      <h4>at every split, the tree</h4>
      <ol>
        <li>draws max_features columns</li>
        <li>tries every threshold, on those</li>
        <li>keeps the best, then recurses</li>
      </ol>
      <h4>what to set it to</h4>
      <table class="plain">
        <tbody>
          <tr><td :style="{ color: GREEN }">√p = {{ sqrtP }}</td><td>classification default</td></tr>
          <tr><td :style="{ color: GREEN }">p/3 or all</td><td>regression defaults</td></tr>
          <tr><td :style="{ color: '#b7791f' }">1</td><td>most diversity, weakest trees</td></tr>
          <tr><td :style="{ color: RED }">all p</td><td>no column randomness: bagging</td></tr>
        </tbody>
      </table>
      <div class="knobs">
        <Knob v-model="p" :min="4" :max="20" :step="1" label="columns p" :digits="0" :color="MUTED" />
        <Knob v-model="k" :min="1" :max="20" :step="1" label="max_features" :digits="0" :color="BLUE" />
        <Knob v-model="draw" :min="1" :max="12" :step="1" label="redraw" :digits="0" :color="GREEN" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.25fr 0.95fr; gap: 1.6rem; height: 100%; min-height: 0; }
.grid { display: flex; flex-direction: column; justify-content: center; gap: 0.5rem; }
.head { text-align: center; font-size: 0.85rem; margin: 0 0 0.3rem; }
.row { display: flex; align-items: center; gap: 0.25rem; }
.name { width: 5.2rem; font-size: 0.78rem; color: var(--muted); }
.cell {
  flex: 1 1 0; text-align: center; font-size: 0.72rem; padding: 0.3rem 0;
  border-style: solid; border-radius: 0.2rem;
}
.best { width: 4.6rem; text-align: right; font-size: 0.78rem; }
.side { display: flex; flex-direction: column; justify-content: center; gap: 0.35rem; }
h4 { margin: 0.3rem 0 0; font-size: 0.9rem; }
ol { margin: 0; padding-left: 1.1rem; font-size: 0.82rem; line-height: 1.5; }
.knobs { display: flex; flex-direction: column; gap: 0.3rem; margin-top: 0.5rem; }
.note { font-size: 0.78rem; margin: 0.3rem 0 0; color: var(--muted); text-align: center; }
.red { color: var(--red); }
</style>
