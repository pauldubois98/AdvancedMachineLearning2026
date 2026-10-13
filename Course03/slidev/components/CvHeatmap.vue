<!-- kernel_cv: C and γ are chosen together, by cross-validation. The grid is
     cross-validated live, cell by cell; click any cell to see its boundary. -->
<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { moons, toPm1 } from '../lib/data'
import { crossValScore, fitSvc, kernel } from '../lib/svm'
import { GREEN, INK, MUTED, RED, greens, rgb } from '../lib/theme'
import { dataDomain } from '../lib/plot'

const gammas = [0.03, 0.1, 0.3, 1, 3, 10, 30]
const Cs = [0.03, 0.1, 1, 10, 100]

const data = moons(220, 0.28, 2)
const yPm = toPm1(data.y)
const domain = dataDomain(data.X, 0.7)

const scores = ref<(number | null)[][]>(Cs.map(() => gammas.map(() => null)))
const done = ref(0)
const sel = ref<[number, number]>([2, 3])

let timer: number | undefined
onMounted(() => {
  const jobs: [number, number][] = []
  for (let i = 0; i < Cs.length; i++) for (let j = 0; j < gammas.length; j++) jobs.push([i, j])
  let k = 0
  const tick = () => {
    const t0 = performance.now()
    while (k < jobs.length && performance.now() - t0 < 24) {
      const [i, j] = jobs[k++]
      scores.value[i][j] = crossValScore(
        data.X, yPm, Cs[i], kernel({ type: 'rbf', gamma: gammas[j] }), 4,
      )
      done.value = k
    }
    scores.value = [...scores.value]
    if (k < jobs.length) timer = window.setTimeout(tick, 0)
    else {
      // land on the best cell once everything is in
      let best: [number, number] = [0, 0]
      let bv = -1
      for (let i = 0; i < Cs.length; i++)
        for (let j = 0; j < gammas.length; j++)
          if ((scores.value[i][j] ?? -1) > bv) {
            bv = scores.value[i][j]!
            best = [i, j]
          }
      sel.value = best
    }
  }
  timer = window.setTimeout(tick, 60)
})
onBeforeUnmount(() => clearTimeout(timer))

const finished = computed(() => done.value === Cs.length * gammas.length)
const best = computed(() => {
  let b: [number, number] = [0, 0]
  let bv = -1
  for (let i = 0; i < Cs.length; i++)
    for (let j = 0; j < gammas.length; j++)
      if ((scores.value[i][j] ?? -1) > bv) {
        bv = scores.value[i][j]!
        b = [i, j]
      }
  return bv > 0 ? b : null
})
const model = computed(() =>
  fitSvc(data.X, yPm, Cs[sel.value[0]], kernel({ type: 'rbf', gamma: gammas[sel.value[1]] })),
)
const selScore = computed(() => scores.value[sel.value[0]][sel.value[1]])

function cellColor(v: number | null) {
  if (v === null) return '#f4f5f6'
  const t = Math.max(0, Math.min(1, (v - 0.72) / (1 - 0.72)))
  return rgb(greens(t))
}
</script>

<template>
  <div class="wrap">
    <div class="left">
      <p class="title">4-fold cross-validated accuracy</p>
      <div class="grid">
        <div class="corner" />
        <div v-for="(g, j) in gammas" :key="`g${j}`" class="colhead">{{ g }}</div>
        <template v-for="(c, i) in Cs" :key="`r${i}`">
          <div class="rowhead">{{ c }}</div>
          <button
            v-for="(g, j) in gammas" :key="`c${i}-${j}`" class="cell"
            :class="{ sel: sel[0] === i && sel[1] === j, best: best && best[0] === i && best[1] === j }"
            :style="{
              background: cellColor(scores[i][j]),
              color: (scores[i][j] ?? 0) > 0.93 ? 'white' : INK,
            }"
            @click="sel = [i, j]"
          >{{ scores[i][j] === null ? '·' : scores[i][j]!.toFixed(2) }}</button>
        </template>
      </div>
      <div class="axes"><span>γ →</span><span class="cax">C ↑</span></div>
      <p v-if="!finished" class="progress">
        fitting… {{ done }} / {{ Cs.length * gammas.length }} cells
      </p>
      <p v-else class="progress done">click a cell to see its boundary</p>
    </div>
    <div class="right">
      <FieldPlot
        :X="data.X" :y="data.y" :decision="model.decisionAt" :domain="domain"
        :margins="false" :point-size="12"
        :title="`C = ${Cs[sel[0]]},  γ = ${gammas[sel[1]]}`"
        :title-color="best && best[0] === sel[0] && best[1] === sel[1] ? RED : INK"
      />
      <Readout
        :items="[
          { label: 'CV accuracy', value: selScore === null ? '…' : `${(selScore * 100).toFixed(1)}%`, color: GREEN },
          { label: 'support vectors', value: String(model.sv.length), color: MUTED },
        ]"
      />
      <p class="note">
        too small a γ and the boundary is nearly straight; too large and every
        point is its own island. C and γ trade against each other, so they are
        searched together.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.25fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; align-items: center; }
.left { display: flex; flex-direction: column; gap: 0.3rem; }
.title { font-size: 0.85rem; font-weight: 600; margin: 0; text-align: center; }
.grid { display: grid; grid-template-columns: auto repeat(7, 1fr); gap: 2px; }
.colhead, .rowhead { font-size: 0.68rem; color: v-bind(MUTED); display: flex; align-items: center; justify-content: center; }
.rowhead { justify-content: flex-end; padding-right: 0.3rem; }
.cell {
  font-size: 0.68rem; padding: 0.3rem 0; border: 1px solid transparent;
  border-radius: 2px; cursor: pointer; font-variant-numeric: tabular-nums;
  transition: background 0.2s;
}
.cell.sel { border-color: v-bind(INK); font-weight: 700; }
.cell.best { outline: 2px solid v-bind(RED); outline-offset: -2px; }
.axes { display: flex; justify-content: space-between; font-size: 0.7rem; color: v-bind(MUTED); }
.progress { font-size: 0.72rem; color: v-bind(MUTED); margin: 0.2rem 0 0; text-align: center; }
.progress.done { color: v-bind(GREEN); }
.right { display: grid; grid-template-rows: 1fr auto auto; gap: 0.35rem; min-height: 0; height: 100%; }
.note { font-size: 0.74rem; color: v-bind(MUTED); margin: 0; line-height: 1.4; }
</style>
