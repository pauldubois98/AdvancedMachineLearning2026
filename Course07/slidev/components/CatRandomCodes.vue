<!-- cat_random_codes: why a random integer per category is a bad encoding. A
     split can only take an interval of the code line, so only k-1 of the
     2^(k-1)-1 groupings survive, and which ones is decided by the draw. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { BLUE, GREEN, GRID, MUTED, RED } from '../lib/theme'

const k = ref(6)
const draw = ref(1)
const DRAWS = 12
const CATS = [
  { name: 'Paris', n: 40, rate: 0.80 },
  { name: 'Berlin', n: 35, rate: 0.22 },
  { name: 'Madrid', n: 30, rate: 0.76 },
  { name: 'Rome', n: 45, rate: 0.25 },
  { name: 'Lisbon', n: 25, rate: 0.78 },
  { name: 'Vienna', n: 38, rate: 0.20 },
  { name: 'Dublin', n: 32, rate: 0.74 },
  { name: 'Oslo', n: 28, rate: 0.27 },
]
const K = computed(() => Math.round(k.value))
const used = computed(() => CATS.slice(0, K.value))

/** weighted variance reduction of one two-group split, the usual CART gain */
function gain(idx: number[], mask: number) {
  let nL = 0, sL = 0, nR = 0, sR = 0
  idx.forEach((c, b) => {
    const cat = CATS[c]
    if (mask & (1 << b)) { nL += cat.n; sL += cat.n * cat.rate }
    else { nR += cat.n; sR += cat.n * cat.rate }
  })
  if (!nL || !nR) return 0
  return (nL * nR / (nL + nR)) * (sL / nL - sR / nR) ** 2
}

/** the best of all 2^(k-1)-1 groupings: what the data actually asks for */
const best = computed(() => {
  const idx = used.value.map((_, i) => i)
  let top = { g: -1, mask: 0 }
  for (let m = 1; m < (1 << K.value) - 1; m++) {
    if (m & 1) continue // category 0 pinned right, so complements are not retried
    const g = gain(idx, m)
    if (g > top.g) top = { g, mask: m }
  }
  return top
})
const inBest = (i: number) => Boolean(best.value.mask & (1 << i))

/** the arbitrary code each category was handed */
function order(seed: number) {
  const rng = new Rng(seed * 101 + K.value * 7)
  const a = used.value.map((_, i) => i)
  for (let i = K.value - 1; i > 0; i--) {
    const j = Math.floor(rng.next() * (i + 1))
    const t = a[i]; a[i] = a[j]; a[j] = t
  }
  return a
}
/** the best a single threshold on that code line can do */
function reachable(seed: number) {
  const a = order(seed)
  let top = { g: -1, cut: 1 }
  for (let c = 1; c < K.value; c++) {
    let mask = 0
    for (let b = 0; b < c; b++) mask |= 1 << b
    const g = gain(a, mask)
    if (g > top.g) top = { g, cut: c }
  }
  return { ...top, order: a }
}
const here = computed(() => reachable(Math.round(draw.value)))
const cells = computed(() =>
  here.value.order.map((c, pos) => ({ ...CATS[c], code: pos + 1, high: inBest(c) })),
)
const share = computed(() => here.value.g / best.value.g)
/** how many of the twelve codings can express the grouping at all */
const hits = computed(() => {
  let n = 0
  for (let s = 1; s <= DRAWS; s++) if (reachable(s).g / best.value.g > 0.999) n++
  return n
})
const total = computed(() => (1 << (K.value - 1)) - 1)
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <div class="col">
        <h4>the categories, and how often they buy</h4>
        <div v-for="c in used" :key="c.name" class="bar">
          <span class="nm" :style="{ color: inBest(used.indexOf(c)) ? RED : BLUE }">{{ c.name }}</span>
          <span class="track">
            <span
              class="fill"
              :style="{ width: c.rate * 100 + '%', background: inBest(used.indexOf(c)) ? RED : BLUE }"
            />
          </span>
          <span class="pc">{{ (c.rate * 100).toFixed(0) }}%</span>
        </div>
        <p class="cap">
          The data wants one cut:
          <span :style="{ color: RED }">the low group</span> against
          <span :style="{ color: BLUE }">the high one</span>.
        </p>
      </div>
      <div class="col">
        <h4>the integer each one happened to be given</h4>
        <div class="line">
          <template v-for="(c, i) in cells" :key="c.name">
            <span v-if="i === here.cut" class="cut" :style="{ background: GREEN }" />
            <span
              class="cell"
              :style="{ borderColor: c.high ? RED : BLUE, color: c.high ? RED : BLUE }"
            >
              <b>{{ c.code }}</b><br>{{ c.name }}
            </span>
          </template>
        </div>
        <p class="cap">
          A split asks <i>x ≤ t</i>, so it can only cut this line
          <span :style="{ color: GREEN }">between two neighbours</span> —
          {{ K - 1 }} cuts, not {{ total }} groupings.
        </p>
        <p class="cap big" :style="{ color: share > 0.999 ? GREEN : RED }">
          the best cut here is worth {{ (share * 100).toFixed(0) }}% of that grouping
        </p>
      </div>
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="k" :min="4" :max="8" :step="1" label="categories" :digits="0" :color="MUTED" />
        <Knob v-model="draw" :min="1" :max="DRAWS" :step="1" label="redraw the codes" :digits="0" :color="GREEN" />
        <Readout
          :items="[
            { label: 'groupings of ' + K + ' categories', value: String(total), color: BLUE },
            { label: 'a code line can reach', value: String(K - 1), color: RED },
            { label: 'draws that reach the best one', value: hits + ' of ' + DRAWS, color: GREEN },
          ]"
        />
      </div>
      <p class="note">
        Numbering the categories invents an order and a distance nobody chose, and a tree
        can only take an interval of that line: {{ K - 1 }} of the {{ total }} ways to divide
        {{ K }} categories survive, and which ones is settled by the draw rather than by the data.
        Redraw and the model changes. The fix is not a cleverer number but a meaningful one —
        a statistic of the target, which is what the next slides build.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 0.95fr 1.05fr; gap: 1.6rem; min-height: 0; align-items: center; }
.col { display: flex; flex-direction: column; justify-content: center; gap: 0.3rem; }
h4 { margin: 0 0 0.3rem; font-size: 0.86rem; color: #4a4a4a; font-weight: 600; }
.bar { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; }
.nm { width: 4.4rem; }
.track { flex: 1 1 0; height: 0.62rem; background: #edeef0; border-radius: 0.31rem; overflow: hidden; }
.fill { display: block; height: 100%; }
.pc { width: 2.4rem; text-align: right; font-variant-numeric: tabular-nums; color: #4a4a4a; }
.line { display: flex; align-items: stretch; gap: 0.25rem; }
.cell {
  flex: 1 1 0; text-align: center; font-size: 0.72rem; line-height: 1.35;
  padding: 0.3rem 0.1rem; border: 1.4px solid; border-radius: 0.25rem;
}
.cell b { font-size: 0.86rem; }
.cut { width: 3px; border-radius: 2px; margin: 0 0.18rem; }
.cap { font-size: 0.76rem; margin: 0.35rem 0 0; color: #9aa0a6; line-height: 1.45; }
.cap.big { font-size: 0.84rem; font-weight: 600; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.knobs > :nth-child(-n+2) { min-width: 10rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
