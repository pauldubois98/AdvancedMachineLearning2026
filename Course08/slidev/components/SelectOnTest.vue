<!-- select_on_test: the winner's curse. Candidates (order-5 fits on random
     subsets of 40 points) are scored on a validation set, which also picks
     the winner; its validation score is then biased low. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmin, freshSin, mse, permutation, pick, polyFit, sinData } from '../lib/c08'
import { Rng } from '../lib/rng'
import { BLUE, GOLD, GREEN, MUTED, RED } from '../lib/theme'

const nCand = ref(10)
const nVal = ref(25)
const seed = ref(5)
const test = freshSin(3000, 99)
function draw(sd: number, k: number, nv: number) {
  const rng = new Rng(sd)
  const tr = sinData(40, 1000 + sd)
  const va = freshSin(nv, 5000 + sd)
  return Array.from({ length: k }, () => {
    const sub = pick(tr, permutation(40, rng).slice(0, 32))
    const w = polyFit(sub.x, sub.t, 5)
    return { val: mse(w, va), fresh: mse(w, test) }
  })
}
const cands = computed(() => draw(seed.value, nCand.value, nVal.value))
const k = computed(() => argmin(cands.value.map((c) => c.val)))
const best = computed(() => argmin(cands.value.map((c) => c.fresh)))
// the optimism of the winning score, averaged over many repetitions
const optimism = computed(() => {
  let g = 0
  const R = 60
  for (let r = 0; r < R; r++) {
    const c = draw(100 + r, nCand.value, nVal.value)
    const j = argmin(c.map((v) => v.val))
    g += c[j].fresh - c[j].val
  }
  return g / R
})
const ys = computed(() => cands.value.flatMap((c) => [c.val, c.fresh]))
const ylo = computed(() => Math.min(...ys.value) * 0.9)
const yhi = computed(() => Math.max(...ys.value) * 1.08)
</script>

<template>
  <div class="wrap">
    <div class="note top">{{ nCand }} candidates, scored on the set that also chooses between them</div>
    <div class="body">
      <LineChart
        :series="cands.map((c, i) => ({ points: [[i + 1, c.val], [i + 1, c.fresh]] as [number, number][], color: '#cccfd2', width: 1.6 }))"
        :dots="[
          ...cands.map((c, i) => ({ x: i + 1, y: c.val, color: GOLD, r: nCand > 25 ? 3 : 5 })),
          ...cands.map((c, i) => ({ x: i + 1, y: c.fresh, color: RED, r: nCand > 25 ? 3 : 5 })),
          { x: k + 1, y: cands[k].val, color: GREEN, r: 11, hollow: true },
          { x: best + 1, y: cands[best].fresh, color: RED, r: 10, hollow: true },
        ]"
        :labels="[{ x: 0.8, y: yhi * 0.985, text: '● score on that set', color: GOLD, size: 12 }, { x: 0.8, y: yhi * 0.985 - (yhi - ylo) * 0.07, text: '● score on fresh data', color: RED, size: 12 }]"
        :x-domain="[0.3, nCand + 0.7]" :y-domain="[ylo, yhi]" :y-ticks="[ylo, (ylo + yhi) / 2, yhi].map((v) => +v.toFixed(3))"
        :x-ticks="nCand <= 12 ? cands.map((_, i) => i + 1) : []" x-label="candidate model" y-label="squared error"
      />
      <div class="side">
        <p>Validation picks <b :style="{ color: GREEN }">candidate {{ k + 1 }}</b> (ring); the actual best on fresh data is <b :style="{ color: RED }">candidate {{ best + 1 }}</b>.</p>
        <p>The winning score is the smallest of {{ nCand }} noisy numbers, so it is biased low: on average it is
          <b :style="{ color: RED }">{{ optimism.toFixed(4) }}</b> below the winner's fresh score.</p>
        <p class="note">More candidates, or a smaller validation set: a larger bias.</p>
        <div class="bar">
          <span :style="{ background: BLUE, flex: 5 }">train</span>
          <span :style="{ background: GOLD, flex: 2 }">val.</span>
          <span :style="{ background: RED, flex: 2 }">test</span>
        </div>
        <p :style="{ color: GREEN }">fit on train, choose with validation, report on test</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="nCand" :min="2" :max="40" :step="1" :digits="0" label="candidates" />
      <Knob v-model="nVal" :min="5" :max="200" :step="1" :digits="0" label="validation points" :color="GOLD" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" :digits="0" label="draw" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.3rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; border-left: 1px solid #cccfd2; padding-left: 1.6rem; font-size: 0.9rem; }
.bar { display: flex; gap: 3px; margin-top: 1rem; }
.bar span { color: white; text-align: center; padding: 0.35rem 0; font-size: 0.85rem; }
</style>
