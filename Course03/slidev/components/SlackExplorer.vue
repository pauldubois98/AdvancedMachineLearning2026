<!-- slack_idea: ξ_i is how far point i is from where it ought to be.
     Lower C and the model buys itself a wider street with more slack. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sepBlobs, toPm1 } from '../lib/data'
import { fitSvc, kernel } from '../lib/svm'
import { GOLD, GREEN, MUTED, RED } from '../lib/theme'

const C = ref(1)
const data = sepBlobs(90, 1.5, 5)
const yPm = toPm1(data.y)
const model = computed(() => fitSvc(data.X, yPm, C.value, kernel({ type: 'linear' })))

const slacks = computed(() =>
  data.X.map((x, i) => Math.max(0, 1 - yPm[i] * model.value.decision(x))),
)
const counts = computed(() => {
  let fine = 0, inside = 0, wrong = 0
  for (const xi of slacks.value) {
    if (xi <= 1e-9) fine++
    else if (xi <= 1) inside++
    else wrong++
  }
  return { fine, inside, wrong }
})
const total = computed(() => slacks.value.reduce((a, b) => a + b, 0))

/** the five worst points, with an arrow back to where they ought to be */
const arrows = computed(() => {
  const m = model.value
  if (!m.w) return []
  const w = m.w
  const n2 = w[0] * w[0] + w[1] * w[1]
  return slacks.value
    .map((xi, i) => ({ xi, i }))
    .sort((a, b) => b.xi - a.xi)
    .slice(0, 5)
    .filter((p) => p.xi > 1e-6)
    .map(({ i, xi }) => {
      const dir = [(yPm[i] * w[0] * xi) / n2, (yPm[i] * w[1] * xi) / n2]
      return {
        from: data.X[i] as [number, number],
        to: [data.X[i][0] + dir[0], data.X[i][1] + dir[1]] as [number, number],
        color: GOLD,
      }
    })
})
</script>

<template>
  <div class="wrap">
    <FieldPlot :X="data.X" :y="data.y" :decision="model.decisionAt" :arrows="arrows" :point-size="22" />
    <div class="side">
      <p class="head" :style="{ color: GOLD }">
        ξ<sub>i</sub> ≥ 0 : how far point i is from where it ought to be
      </p>
      <p class="eq">y<sub>i</sub>(w<sup>T</sup>x<sub>i</sub> + b) ≥ 1 − ξ<sub>i</sub></p>
      <Knob v-model="C" :min="0.01" :max="100" log label="C" :color="GREEN" />
      <table>
        <tr :style="{ color: GREEN }">
          <td>ξ<sub>i</sub> = 0</td><td class="muted">outside the street, fine</td>
          <td class="num">{{ counts.fine }}</td>
        </tr>
        <tr :style="{ color: GOLD }">
          <td>0 &lt; ξ<sub>i</sub> ≤ 1</td><td class="muted">inside it, still right</td>
          <td class="num">{{ counts.inside }}</td>
        </tr>
        <tr :style="{ color: RED }">
          <td>ξ<sub>i</sub> &gt; 1</td><td class="muted">on the wrong side</td>
          <td class="num">{{ counts.wrong }}</td>
        </tr>
      </table>
      <Readout
        :items="[
          { label: 'Σξ', value: total.toFixed(1), color: GOLD },
          { label: 'street', value: (model.marginWidth ?? 0).toFixed(2) },
          { label: 'cost C·Σξ', value: (C * total).toFixed(1), color: RED },
        ]"
      />
      <p class="note">and we pay C for every unit of ξ; the arrows show the five worst</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; align-items: center; }
.side { display: flex; flex-direction: column; gap: 0.5rem; }
.head { font-size: 0.92rem; margin: 0; font-weight: 600; }
.eq { font-size: 1rem; margin: 0; }
table { font-size: 0.8rem; border-collapse: collapse; }
td { padding: 0.08rem 0.7rem 0.08rem 0; }
.muted { color: v-bind(MUTED); }
.num { font-variant-numeric: tabular-nums; font-weight: 600; text-align: right; }
.note { font-size: 0.76rem; color: v-bind(MUTED); margin: 0; }
</style>
