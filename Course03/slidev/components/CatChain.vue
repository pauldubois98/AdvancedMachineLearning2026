<!-- cat_chain: draw a random ordering, then walk it. Each row is encoded from
     the prefix that precedes it, so its own Buy is never in its numerator. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { BLUE, GREEN, MUTED, PURPLE, RED } from '../lib/theme'

const perm = ref(1)
const a = ref(1)
const ROWS = [
  { id: 1, country: 'France', buy: 1 },
  { id: 2, country: 'France', buy: 1 },
  { id: 3, country: 'France', buy: 0 },
  { id: 4, country: 'Germany', buy: 0 },
  { id: 5, country: 'Germany', buy: 0 },
]
const COLOR: Record<string, string> = { France: BLUE, Germany: PURPLE }
const prior = ROWS.reduce((s, r) => s + r.buy, 0) / ROWS.length

const order = computed(() => {
  const rng = new Rng(perm.value * 17)
  const idx = ROWS.map((_, i) => i)
  for (let i = idx.length - 1; i > 0; i--) {
    const j = Math.floor(rng.next() * (i + 1))
    const t = idx[i]
    idx[i] = idx[j]
    idx[j] = t
  }
  return idx.map((i) => ROWS[i])
})
const walked = computed(() => {
  const seen: Record<string, number[]> = {}
  return order.value.map((r, k) => {
    const hist = seen[r.country] ?? []
    const enc = (hist.reduce((s, v) => s + v, 0) + a.value * prior) / (hist.length + a.value)
    seen[r.country] = [...hist, r.buy]
    return { ...r, slot: 'ABCDE'[k], hist: [...hist], enc }
  })
})
</script>

<template>
  <div class="wrap">
    <div class="chain">
      <div v-for="(r, i) in walked" :key="r.id" class="link">
        <div class="chip" :style="{ borderColor: COLOR[r.country], color: COLOR[r.country] }">{{ r.slot }}</div>
        <p class="who">customer {{ r.id }}<br />{{ r.country }}, Buy = {{ r.buy }}</p>
        <span v-if="i < 4" class="arrow">→</span>
      </div>
    </div>
    <table class="plain">
      <thead>
        <tr><th></th><th>customer</th><th>country</th><th>Buy</th><th>earlier rows of the same country</th><th>encoding</th></tr>
      </thead>
      <tbody>
        <tr v-for="r in walked" :key="r.id">
          <td :style="{ color: COLOR[r.country], fontWeight: 600 }">{{ r.slot }}</td>
          <td>{{ r.id }}</td>
          <td :style="{ color: COLOR[r.country] }">{{ r.country }}</td>
          <td :style="{ color: r.buy ? BLUE : RED }">{{ r.buy }}</td>
          <td :style="{ color: MUTED }">
            {{ r.hist.length ? 'Buy = ' + r.hist.join(', ') : 'none yet, so only the prior' }}
          </td>
          <td :style="{ color: GREEN, fontWeight: 600 }">
            ({{ r.hist.reduce((s, v) => s + v, 0) }} + {{ (a * prior).toFixed(1) }}) /
            ({{ r.hist.length }} + {{ a.toFixed(1) }}) = {{ r.enc.toFixed(2) }}
          </td>
        </tr>
      </tbody>
    </table>
    <div class="knobs">
      <Knob v-model="perm" :min="1" :max="12" :step="1" label="draw another ordering" :digits="0" :color="GREEN" />
      <Knob v-model="a" :min="0.2" :max="6" label="prior weight a" :digits="1" :color="MUTED" />
      <Readout :items="[{ label: 'prior p', value: prior.toFixed(1), color: MUTED }]" />
    </div>
    <p class="note">
      the first row of a country has no history at all and gets the prior; later rows
      get more of their own country's record. The row's own Buy is never in its own
      numerator, and a different ordering gives a different, equally valid encoding,
      which is why CatBoost keeps several permutations rather than one.
    </p>
  </div>
</template>

<style scoped>
.wrap { display: flex; flex-direction: column; justify-content: center; gap: 0.7rem; height: 100%; }
.chain { display: flex; justify-content: center; gap: 0.3rem; }
.link { display: flex; align-items: center; gap: 0.3rem; }
.chip {
  border: 2px solid; border-radius: 0.3rem; width: 2rem; height: 2rem;
  display: flex; align-items: center; justify-content: center; font-weight: 600;
}
.who { font-size: 0.72rem; color: var(--muted); margin: 0; line-height: 1.3; }
.arrow { color: var(--muted); margin: 0 0.4rem; }
.knobs { display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; }
.knobs > :nth-child(-n+2) { min-width: 11rem; }
.note { font-size: 0.78rem; color: var(--muted); margin: 0; line-height: 1.5; }
td { font-variant-numeric: tabular-nums; }
</style>
