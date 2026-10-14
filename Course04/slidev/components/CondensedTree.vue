<!-- condensed_tree: the raw single-linkage tree beside the tree with the noise
     swept out. C_min decides how much is swept. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { densityData, distances } from '../lib/data4'
import { condense, condensedOwners, mstToLinkage, mutualReachability, primMst } from '../lib/density'
import { BLUE, GOLD, GREEN, GRID, MUTED } from '../lib/theme'

const cmin = ref(10)
const k = ref(5)
const X = densityData(7, 45, 28, 12)
const D = distances(X)
const Z = computed(() => mstToLinkage(primMst(mutualReachability(X, k.value, D).mr), X.length))
const cond = computed(() => condense(Z.value, cmin.value))
const owners = computed(() => condensedOwners(Z.value, cmin.value))
const palette = [GRID, BLUE, MUTED, GOLD, GREEN, '#6b46c1', '#0f9b8e', '#b5179e']
const colorOf = (cid: number) => palette[cid % palette.length]
const treeColor = (id: number) => {
  const cid = owners.value.get(id)
  return cid === undefined ? GRID : colorOf(cid)
}
const lamMax = 3.2
const nBranches = computed(() => cond.value.clusters.size)
const nLeaves = computed(() =>
  [...cond.value.clusters.values()].filter((c) => !c.children.length).length,
)
const labelOf = (cid: number, c: { size0: number; lamBirth: number; lamDeath: number }) => {
  if (cid === 0 || c.lamDeath - c.lamBirth < 0.05 * lamMax) return ''
  return `${c.size0} points`
}
</script>

<template>
  <div class="wrap">
    <Dendro
      :Z="Z" :color-of="treeColor" :width="0.8" y-label="d_mreach at the merge"
      title="raw tree: n − 1 merges" :title-color="MUTED"
    />
    <BarTree
      :clusters="cond.clusters" :lam-max="lamMax" :color-of="colorOf" :label-of="labelOf"
      :title="`condensed tree, C<sub>min</sub> = ${cmin}`" :title-color="BLUE"
    />
    <div class="right">
      <div class="note">at every split, ask whether both sides still hold
        C<sub>min</sub> points</div>
      <div class="controls">
        <Knob v-model="cmin" :min="2" :max="40" :step="1" label="C<sub>min</sub>" :digits="0" :color="BLUE" />
        <Knob v-model="k" :min="2" :max="15" :step="1" label="MinPts" :digits="0" :color="GREEN" />
      </div>
      <Readout
        :items="[
          { label: 'merges in the raw tree', value: String(Z.length), color: MUTED },
          { label: 'branches after condensing', value: String(nBranches), color: BLUE },
          { label: 'of which leaves', value: String(nLeaves), color: GREEN },
        ]"
      />
      <p class="note">A bar is as wide as the number of points still inside and
        as tall as the stretch of λ = 1/ε it survives. Raise C<sub>min</sub> and
        the small branches vanish into the trunk, because the sides that fall
        out are read as noise rather than as clusters.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 0.95fr 1.2fr 0.8fr; gap: 1.2rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; }
.controls { display: flex; flex-direction: column; gap: 0.35rem; }
</style>
