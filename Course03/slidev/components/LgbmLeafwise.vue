<!-- lgbm_leafwise: same candidates, same gain, different next node. Both trees
     are grown for real, under the same budget of leaves, so the objective
     printed under them is the objective they actually reach. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { staircase } from '../lib/databis'
import { GbmNode, GrownTree, growTree, leafValue, treeObjective } from '../lib/gbm'
import { Node } from '../lib/tree'
import { GREEN, GOLD, MUTED } from '../lib/theme'

const leaves = ref(8)
const data = staircase(400, 2)
// log loss at the first tree: every prediction is 0.5, so g is ±0.5, h is 0.25
const g = data.y.map((v) => 0.5 - v)
const h = data.y.map(() => 0.25)

const level = computed(() =>
  growTree(data.X, g, h, { mode: 'level', maxLeaves: Math.round(leaves.value), minRows: 10 }),
)
const leaf = computed(() =>
  growTree(data.X, g, h, { mode: 'leaf', maxLeaves: Math.round(leaves.value), minRows: 10 }),
)

/** the grown tree, in the shape TreeDiagram draws */
function toNode(n: GbmNode): Node {
  const out: Node = { value: [leafValue(n.G, n.H)], n: n.rows.length, impurity: 0 }
  if (n.left) {
    out.feature = n.feature
    out.threshold = n.threshold
    out.left = toNode(n.left)
    out.right = toNode(n.right!)
  }
  return out
}
const depthOf = (t: GrownTree) => Math.max(...t.leaves.map((l) => l.depth))
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <div class="panel">
        <TreeDiagram
          :root="toNode(level.root)" :max-depth="5" leaf-text="value"
          title="level-wise (XGBoost default)"
        />
        <p class="cap">finishes a level before starting the next</p>
      </div>
      <div class="panel">
        <TreeDiagram
          :root="toNode(leaf.root)" :max-depth="5" leaf-text="value"
          title="leaf-wise / best-first (LightGBM)"
        />
        <p class="cap">keeps a queue of leaves and always splits the one offering the most, anywhere in the tree</p>
      </div>
    </div>
    <div class="controls">
      <div class="knobs">
        <Knob v-model="leaves" :min="2" :max="12" :step="1" label="budget: number of leaves" :digits="0" :color="GREEN" />
        <Readout
          :items="[
            { label: 'objective, level-wise', value: treeObjective(level).toFixed(3) },
            { label: 'leaf-wise', value: treeObjective(leaf).toFixed(3), color: GREEN },
            { label: 'depth reached', value: `${depthOf(level)} vs ${depthOf(leaf)}`, color: GOLD },
          ]"
        />
      </div>
      <p class="note">
        at the same number of leaves, best-first always reaches an objective at least
        as low: it spends every split where it pays most. It pays for that with depth,
        which is why LightGBM limits num_leaves rather than max_depth, and why a
        leaf-wise tree over-fits more readily on small data.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6rem; min-height: 0; }
.panel { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.cap { font-size: 0.78rem; color: var(--muted); margin: 0; text-align: center; line-height: 1.4; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.knobs { display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child { min-width: 13rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
