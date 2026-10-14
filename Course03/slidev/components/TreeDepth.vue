<!-- tree_grow: depth is the capacity knob. One tree, refitted at every depth
     the slider stops on, with its leaf count and its training accuracy. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { treeToy, split } from '../lib/databis'
import { accuracy, fitTree } from '../lib/tree'
import { logit } from '../lib/plot'
import { GREEN, MUTED, RED } from '../lib/theme'

const depth = ref(2)
const minLeaf = ref(1)
const data = treeToy(0, 300)
const sp = split(data, 0.4, 2)

const tree = computed(() =>
  fitTree(sp.Xtr, sp.ytr, {
    maxDepth: depth.value >= 13 ? Infinity : depth.value,
    minSamplesLeaf: minLeaf.value,
    seed: 0,
  }),
)
const field = (x: number, y: number) => logit(tree.value.predict([x, y])[1])
const trainAcc = computed(() => accuracy(tree.value, sp.Xtr, sp.ytr))
const testAcc = computed(() => accuracy(tree.value, sp.Xte, sp.yte))
const label = computed(() => (depth.value >= 13 ? 'unlimited' : `depth ${depth.value}`))
</script>

<template>
  <div class="wrap">
    <FieldPlot
      :X="sp.Xtr" :y="sp.ytr" :decision="field" :domain="[0, 1, 0, 1]" :margins="false"
      :point-size="11" :field-alpha="0.6" :res="150"
      :title="`${label}, ${tree.nLeaves} leaves`"
    />
    <div class="right">
      <TreeDiagram :root="tree.root" :max-depth="Math.min(4, depth)" title="the tree it grew" />
      <div class="controls">
        <Knob v-model="depth" :min="1" :max="13" :step="1" label="max_depth" :digits="0" :color="GREEN" />
        <Knob v-model="minLeaf" :min="1" :max="30" :step="1" label="min_samples_leaf" :digits="0" :color="MUTED" />
        <Readout
          :items="[
            { label: 'leaves', value: String(tree.nLeaves) },
            { label: 'train accuracy', value: (trainAcc * 100).toFixed(1) + '%', color: GREEN },
            { label: 'test accuracy', value: (testAcc * 100).toFixed(1) + '%', color: testAcc < trainAcc - 0.06 ? RED : GREEN },
          ]"
        />
        <p class="note">
          deep enough and the training accuracy hits 100%: the tree can always carve
          one box per row. The test accuracy is what stops improving first.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1.05fr; gap: 1.4rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; min-height: 0; }
.controls { display: flex; flex-direction: column; gap: 0.4rem; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.45; }
</style>
