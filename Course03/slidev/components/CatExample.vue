<!-- cat_example: target encoding on five rows. Every row's own answer is one
     of the values averaged into its own feature; the toggle takes it out. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, MUTED, PURPLE, RED } from '../lib/theme'

const leaveOut = ref(false)
const a = ref(0)
const ROWS = [
  { id: 1, country: 'France', buy: 1 },
  { id: 2, country: 'France', buy: 1 },
  { id: 3, country: 'France', buy: 0 },
  { id: 4, country: 'Germany', buy: 0 },
  { id: 5, country: 'Germany', buy: 0 },
]
const COLOR: Record<string, string> = { France: BLUE, Germany: PURPLE }
const prior = ROWS.reduce((s, r) => s + r.buy, 0) / ROWS.length

const encoded = computed(() =>
  ROWS.map((r) => {
    const peers = ROWS.filter((o) => o.country === r.country && (!leaveOut.value || o.id !== r.id))
    const sum = peers.reduce((s, o) => s + o.buy, 0)
    return { ...r, enc: (sum + a.value * prior) / (peers.length + a.value), n: peers.length }
  }),
)
/** does the encoding still give the row's own label away? */
const leaks = computed(() => {
  const byEnc = new Map<string, number[]>()
  for (const r of encoded.value) {
    const k = r.enc.toFixed(3)
    byEnc.set(k, [...(byEnc.get(k) ?? []), r.buy])
  }
  return [...byEnc.values()].some((ys) => ys.length > 1 && ys.every((v) => v === ys[0]) && ys.length < 3)
    || [...byEnc.values()].some((ys) => ys.every((v) => v === ys[0]))
})
</script>

<template>
  <div class="wrap">
    <div class="left">
      <table class="plain">
        <thead>
          <tr><th>Customer</th><th>Country</th><th>Buy</th><th>target encoding</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in encoded" :key="r.id">
            <td>{{ r.id }}</td>
            <td :style="{ color: COLOR[r.country] }">{{ r.country }}</td>
            <td :style="{ color: r.buy ? BLUE : RED }">{{ r.buy }}</td>
            <td
              :style="{
                color: !leaveOut && (r.enc === 0 || r.enc === 1) ? RED : '#1b1b1b',
                fontWeight: 600,
              }"
            >{{ r.enc.toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
      <p class="note" :style="{ color: leaveOut ? GREEN : RED }">
        <template v-if="!leaveOut">
          each row's own Buy is one of the values averaged into its own encoding
        </template>
        <template v-else>
          leaving the row out takes your own answer out of your own average, and hands
          you the opposite one instead: customer 3, the only French customer who did not
          buy, now carries the highest encoding of the three
        </template>
      </p>
    </div>
    <div class="right">
      <p class="calc" :style="{ color: BLUE }">
        P(Buy = 1 | France) = {{ a > 0 ? `(2 + ${a.toFixed(1)}·0.4) / (3 + ${a.toFixed(1)})` : '2/3' }}
        = {{ ((2 + a * prior) / (3 + a)).toFixed(2) }}
      </p>
      <p class="calc" :style="{ color: PURPLE }">
        P(Buy = 1 | Germany) = {{ a > 0 ? `(0 + ${a.toFixed(1)}·0.4) / (2 + ${a.toFixed(1)})` : '0/2' }}
        = {{ ((0 + a * prior) / (2 + a)).toFixed(2) }}
      </p>
      <div class="knobs">
        <Toggle v-model="leaveOut" label="leave the row itself out of its own average" :color="GREEN" />
        <Knob v-model="a" :min="0" :max="10" label="prior weight a" :digits="1" :color="MUTED" />
      </div>
      <p class="note">
        the prior weight a pulls every category toward the base rate {{ prior.toFixed(1) }},
        which is a smoothing, not a fix: with a = 10 the German rows read 0.33 instead
        of 0.00, and still differ from the French ones by exactly their labels.
      </p>
      <p class="note red" v-if="!leaveOut">
        both German customers are handed the same number, and that number is their answer
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; height: 100%; align-items: center; }
.left, .right { display: flex; flex-direction: column; gap: 0.7rem; }
.calc { font-size: 1rem; margin: 0; }
.knobs { display: flex; flex-direction: column; gap: 0.5rem; }
.knobs > :nth-child(2) { max-width: 18rem; }
.note { font-size: 0.8rem; color: var(--muted); margin: 0; line-height: 1.5; }
.red { color: var(--red); }
td { font-variant-numeric: tabular-nums; }
</style>
