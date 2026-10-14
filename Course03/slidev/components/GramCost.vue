<!-- svm_cost: where the kernel SVM stops being the right tool. The Gram
     matrix is n × n, so the memory is the thing that bites first. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { GOLD, GREEN, INK, MUTED, RED } from '../lib/theme'

const n = ref(10000)

const bytes = computed(() => 8 * n.value * n.value)
function human(b: number): string {
  const u = ['B', 'kB', 'MB', 'GB', 'TB', 'PB']
  let i = 0
  while (b >= 1000 && i < u.length - 1) {
    b /= 1000
    i++
  }
  return `${b < 10 ? b.toFixed(1) : b.toFixed(0)} ${u[i]}`
}
const verdict = computed(() =>
  n.value <= 10000
    ? { text: 'any kernel is fine', color: GREEN }
    : n.value <= 100000
      ? { text: 'kernel SVM is painful: budget hours, or subsample', color: GOLD }
      : { text: 'LinearSVC, or a different model altogether', color: RED },
)

const ns: number[] = []
for (let i = 0; i <= 60; i++) ns.push(10 ** (2.4 + (4.6 * i) / 60))
// anchored on the measured fit times of the printed figure (~0.02 s at n = 250)
const kernelTime = ns.map((v) => [v, 0.02 * (v / 250) ** 2.4] as [number, number])
const linearTime = ns.map((v) => [v, 0.004 * (v / 250) ** 1.05] as [number, number])
const atN = computed(() => ({
  kernel: 0.02 * (n.value / 250) ** 2.4,
  linear: 0.004 * (n.value / 250) ** 1.05,
}))
function dur(s: number): string {
  if (s < 1) return `${(s * 1000).toFixed(0)} ms`
  if (s < 90) return `${s.toFixed(1)} s`
  if (s < 5400) return `${(s / 60).toFixed(0)} min`
  if (s < 86400 * 2) return `${(s / 3600).toFixed(1)} h`
  return `${(s / 86400).toFixed(0)} days`
}
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="[
        { points: kernelTime, color: RED, width: 2.6 },
        { points: linearTime, color: GREEN, width: 2.6 },
      ]"
      :vlines="[{ x: n, color: INK, dash: '3,3' }]"
      :dots="[
        { x: n, y: atN.kernel, color: RED, r: 4.5 },
        { x: n, y: atN.linear, color: GREEN, r: 4.5 },
      ]"
      :x-domain="[250, 1e7]" :y-domain="[0.001, 1e6]" log-x log-y
      x-label="training points n" y-label="fit time (s)"
      title="20 features"
      :labels="[
        { x: 2.5e6, y: 3e5, text: 'SVC (RBF)', color: RED, size: 12, anchor: 'end' },
        { x: 2e6, y: 1e2, text: 'LinearSVC', color: GREEN, size: 12, anchor: 'end' },
      ]"
    />
    <div class="side">
      <Knob v-model="n" :min="250" :max="10000000" log label="n" :color="INK" />
      <div class="cards">
        <div class="card">
          <p class="lab">Gram matrix, n × n</p>
          <p class="big" :style="{ color: verdict.color }">{{ human(bytes) }}</p>
        </div>
        <div class="card">
          <p class="lab">kernel fit</p>
          <p class="big" :style="{ color: RED }">{{ dur(atN.kernel) }}</p>
        </div>
        <div class="card">
          <p class="lab">linear fit</p>
          <p class="big" :style="{ color: GREEN }">{{ dur(atN.linear) }}</p>
        </div>
      </div>
      <p class="verdict" :style="{ color: verdict.color }">{{ verdict.text }}</p>
      <p class="note">
        The kernel fit grows like n² to n³, and the Gram matrix like n².
        Rules of thumb: below ~10 000 points, any kernel; above that, LinearSVC.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; align-items: center; }
.side { display: flex; flex-direction: column; gap: 0.6rem; }
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
.card { border: 1px solid #e3e5e8; border-radius: 0.35rem; padding: 0.4rem 0.5rem; }
.lab { font-size: 0.68rem; color: v-bind(MUTED); margin: 0; }
.big { font-size: 1rem; font-weight: 700; margin: 0.1rem 0 0; font-variant-numeric: tabular-nums; }
.verdict { font-size: 0.85rem; font-weight: 600; margin: 0; }
.note { font-size: 0.75rem; color: v-bind(MUTED); margin: 0; line-height: 1.45; }
</style>
