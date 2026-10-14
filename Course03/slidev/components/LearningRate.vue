<!-- learning_rate: eta and M are one knob in two halves. One boosting run per
     learning rate, measured on held-out rows, computed in the background. -->
<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { friedman1, split } from '../lib/databis'
import { fitBooster } from '../lib/boost'
import { BLUE, GOLD, GREEN, MUTED, RED } from '../lib/theme'

const M = ref(50)
const depth = ref('3')
const MAX = 200
const ETAS = [
  { eta: 0.5, color: RED },
  { eta: 0.2, color: GOLD },
  { eta: 0.05, color: BLUE },
  { eta: 0.01, color: GREEN },
]
const curves = ref<{ eta: number; color: string; points: [number, number][] }[]>([])
let token = 0

function run() {
  const mine = ++token
  curves.value = []
  const data = friedman1(300, 3, 0)
  const sp = split(data, 0.5, 0)
  let i = 0
  const one = () => {
    if (mine !== token) return
    const { eta, color } = ETAS[i]
    const b = fitBooster(sp.Xtr, sp.ytr, {
      nTrees: MAX, eta, maxDepth: Number(depth.value), loss: 'squared', seed: 0,
    })
    const stages = b.stages(sp.Xte)
    const points = stages
      .map((F, m) => {
        let s = 0
        for (let k = 0; k < sp.yte.length; k++) s += (sp.yte[k] - F[k]) ** 2
        return [m, s / sp.yte.length] as [number, number]
      })
      .slice(1)
    curves.value = [...curves.value, { eta, color, points }]
    if (++i < ETAS.length) setTimeout(one, 0)
  }
  setTimeout(one, 0)
}
onMounted(run)
watch(depth, run)
onBeforeUnmount(() => token++)

const series = computed(() => curves.value.map((c) => ({ points: c.points, color: c.color, width: 2.2 })))
const minima = computed(() =>
  curves.value.map((c) => {
    const b = c.points.reduce((a, p) => (p[1] < a[1] ? p : a))
    return { x: b[0], y: b[1], color: c.color, r: 5 }
  }),
)
const at = computed(() =>
  curves.value.map((c) => ({
    label: `η = ${c.eta}`,
    value: c.points[Math.round(M.value) - 1][1].toFixed(2),
    color: c.color,
  })),
)
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="series"
      :dots="[...minima, { x: M, y: 0, color: '#1b1b1b', r: 0 }]"
      :vlines="[{ x: M, color: '#1b1b1b', dash: '' }]"
      :x-domain="[1, MAX]" :y-domain="[8, 30]" log-x
      :x-ticks="[1, 10, 100]" :y-ticks="[10, 20, 30]"
      x-label="number of trees (log scale)" y-label="test MSE"
      title="small η reaches a lower minimum, and needs far more trees to get there"
      :labels="curves.map((c, i) => ({ x: 1.2, y: 29 - i * 1.6, text: `η = ${c.eta}`, color: c.color, size: 11.5 }))"
    />
    <div class="controls">
      <div class="knobs">
        <Knob v-model="M" :min="1" :max="MAX" :step="1" label="trees" :digits="0" />
        <Choice
          v-model="depth" label="depth of each tree"
          :options="[{ value: '2', label: '2' }, { value: '3', label: '3' }, { value: '4', label: '4' }]"
        />
        <Readout :items="at" />
      </div>
      <p class="note">
        <span v-if="curves.length < ETAS.length">Measuring… {{ curves.length }}/{{ ETAS.length }} runs</span>
        <span v-else>
          The dots are each run's best. Halving η roughly doubles the trees you need:
          they are not two knobs, they are a budget and how finely you spend it.
        </span>
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 1.8rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child { min-width: 11rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.5; }
</style>
