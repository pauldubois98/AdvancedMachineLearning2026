<!-- tree_questions: the tree and the partition it draws are the same object.
     The three thresholds are the sliders, so moving one moves both pictures. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { treeToy } from '../lib/databis'
import { Node } from '../lib/tree'
import { logit } from '../lib/plot'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const t1 = ref(0.55)
const t2 = ref(0.62)
const t3 = ref(0.22)
const data = treeToy(0, 240)
const domain: [number, number, number, number] = [0, 1, 0, 1]

/** The hand-built tree of the printed figure, with its leaf shares measured
 *  on the rows that actually land in each box. */
const tree = computed(() => {
  const rows = [[], [], [], []] as number[][]
  for (let i = 0; i < data.X.length; i++) {
    const [a, b] = data.X[i]
    if (a > t1.value) rows[0].push(i)
    else if (b <= t2.value) rows[1].push(i)
    else if (a <= t3.value) rows[2].push(i)
    else rows[3].push(i)
  }
  const value = (idx: number[]) => {
    if (!idx.length) return [0.5, 0.5]
    const p = idx.reduce((s, i) => s + data.y[i], 0) / idx.length
    return [1 - p, p]
  }
  const leaf = (idx: number[]): Node => ({ value: value(idx), n: idx.length, impurity: 0 })
  const root: Node = {
    value: value(data.X.map((_, i) => i)), n: data.X.length, impurity: 0,
    feature: 0, threshold: t1.value,
    left: {
      value: value([...rows[1], ...rows[2], ...rows[3]]), n: 0, impurity: 0,
      feature: 1, threshold: t2.value,
      left: leaf(rows[1]),
      right: {
        value: value([...rows[2], ...rows[3]]), n: 0, impurity: 0,
        feature: 0, threshold: t3.value,
        left: leaf(rows[2]),
        right: leaf(rows[3]),
      },
    },
    right: leaf(rows[0]),
  }
  return { root, rows }
})

const predictProba = (x: number, y: number) => {
  let node = tree.value.root
  while (node.left) node = (node.feature === 0 ? x : y) <= node.threshold! ? node.left : node.right!
  return node.value[1]
}
const field = (x: number, y: number) => logit(predictProba(x, y))

const acc = computed(() => {
  let ok = 0
  for (let i = 0; i < data.X.length; i++) {
    const p = predictProba(data.X[i][0], data.X[i][1])
    if ((p > 0.5 ? 1 : 0) === data.y[i]) ok++
  }
  return ok / data.X.length
})

const cuts = computed(() => [
  { from: [t1.value, 0] as [number, number], to: [t1.value, 1] as [number, number], width: 2.2 },
  { from: [0, t2.value] as [number, number], to: [t1.value, t2.value] as [number, number], width: 2.2 },
  { from: [t3.value, t2.value] as [number, number], to: [t3.value, 1] as [number, number], width: 2.2 },
])
</script>

<template>
  <div class="wrap">
    <TreeDiagram
      :root="tree.root" :max-depth="3" title="three questions, four answers"
    />
    <div class="right">
      <FieldPlot
        :X="data.X" :y="data.y" :decision="field" :domain="domain" :margins="false"
        :boundary="false" :segments="cuts" :point-size="12" :field-alpha="0.55"
        title="every leaf is a rectangle of feature space"
      />
      <div class="controls">
        <Knob v-model="t1" :min="0.05" :max="0.95" label="root: x₁ ≤" :digits="2" :color="BLUE" />
        <Knob v-model="t2" :min="0.05" :max="0.95" label="then: x₂ ≤" :digits="2" :color="GREEN" />
        <Knob v-model="t3" :min="0.05" :max="0.95" label="then: x₁ ≤" :digits="2" :color="RED" />
        <Readout
          :items="[
            { label: 'training accuracy', value: (acc * 100).toFixed(1) + '%', color: acc > 0.9 ? GREEN : RED },
            { label: 'rows per leaf', value: tree.rows.map((r) => r.length).join(' / ') },
          ]"
        />
        <p class="note">The questions are axis-aligned, so the boxes are too.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.35rem; }
.note { font-size: 0.8rem; margin: 0; color: var(--muted); }
</style>
