<!-- pruning: trials report a score each round; after a warm-up, a trial
     whose score falls below a percentile of the earlier trials' scores at the
     same round is stopped (the median pruner at 50%). How many are pruned,
     how much compute is saved, and whether the best trial survived. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { argmax } from '../lib/c08'
import { GREEN, MUTED, RED } from '../lib/theme'

const nTrials = ref(24)
const warm = ref(10)
const pct = ref(50)
const seed = ref(3)
const R = 100
const trials = computed(() => {
  const rng = new Rng(seed.value)
  return Array.from({ length: nTrials.value }, () => {
    const ceil = rng.uniform(0.70, 0.81)
    const tau = rng.uniform(8, 26)
    return Array.from({ length: R }, (_, r) => ceil * (1 - Math.exp(-(r + 1) / tau)) + rng.normal(0, 0.004))
  })
})
function quantile(v: number[], q: number) {
  const s = [...v].sort((a, b) => a - b)
  const i = (s.length - 1) * q
  const lo = Math.floor(i)
  return s[lo] + (s[Math.min(lo + 1, s.length - 1)] - s[lo]) * (i - lo)
}
// trials run one after the other; each is compared with the earlier ones
const result = computed(() => {
  const stopAt: number[] = []
  trials.value.forEach((c, k) => {
    let stop = R
    if (k >= 5) {
      for (let r = warm.value; r < R; r++) {
        const past = trials.value.slice(0, k).filter((_, j) => stopAt[j] > r).map((p) => p[r])
        if (past.length && c[r] < quantile(past, pct.value / 100)) { stop = r + 1; break }
      }
    }
    stopAt.push(stop)
  })
  return stopAt
})
const pruned = computed(() => result.value.filter((s) => s < R).length)
const saved = computed(() => 1 - result.value.reduce((a, s) => a + s, 0) / (R * nTrials.value))
const trueBest = computed(() => argmax(trials.value.map((c) => c[R - 1])))
const bestKept = computed(() => result.value[trueBest.value] === R)
</script>

<template>
  <div class="wrap">
    <div class="note top">Stop a hopeless trial before it finishes</div>
    <div class="body">
      <LineChart
        :series="trials.map((c, k) => ({
          points: c.slice(0, result[k]).map((v, r) => [r + 1, v] as [number, number]),
          color: result[k] === R ? GREEN : MUTED, width: result[k] === R ? 1.8 : 1.1, opacity: result[k] === R ? 0.9 : 0.75,
        }))"
        :dots="trials.flatMap((c, k) => (result[k] < R ? [{ x: result[k], y: c[result[k] - 1], color: RED, r: 3.5 }] : []))"
        :vlines="[{ x: warm, color: MUTED, dash: '3 3' }]"
        :x-domain="[0, 101]" :y-domain="[0, 0.86]" :x-ticks="[0, 20, 40, 60, 80, 100]" :y-ticks="[0, 0.2, 0.4, 0.6, 0.8]"
        x-label="rounds within one trial" y-label="validation AUC"
      />
      <div class="side">
        <pre class="code">for round in trial:
    s = score(round)
    report(s, round)

    if s &lt; percentile(past, round):
        prune(trial)</pre>
        <p>Here <b :style="{ color: RED }">{{ pruned }} of {{ nTrials }}</b> trials were pruned (red dots), saving
          <b>{{ (100 * saved).toFixed(0) }}%</b> of the rounds.</p>
        <p :style="{ color: bestKept ? GREEN : RED }">{{ bestKept ? 'The best trial survived: the budget goes to the survivors.' : 'The best trial was pruned: too aggressive.' }}</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="pct" :min="5" :max="95" :step="5" :digits="0" label="percentile" unit="%" :color="RED" />
      <Knob v-model="warm" :min="1" :max="60" :step="1" :digits="0" label="warm-up rounds" />
      <Knob v-model="nTrials" :min="6" :max="60" :step="1" :digits="0" label="trials" />
      <Knob v-model="seed" :min="1" :max="30" :step="1" :digits="0" label="seed" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.3fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; border-left: 1px solid #cccfd2; padding-left: 1.6rem; font-size: 0.9rem; }
.code { background: #f3f4f6; border-radius: 8px; padding: 0.7rem 1rem; font-size: 0.78rem; line-height: 1.55; margin: 0 0 0.8rem; }
</style>
