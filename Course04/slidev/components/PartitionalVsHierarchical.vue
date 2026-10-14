<!-- partitional_vs_hierarchical: the same points, read at one level or at
     several. The slider moves the sub-groups apart, so the nesting that the
     partitional view throws away becomes visible. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { BLUE, GREEN, RED, shades } from '../lib/theme'

const gap = ref(0.62)
const groups: [[number, number], string][] = [
  [[-1.7, -0.9], BLUE],
  [[1.8, -0.7], GREEN],
  [[0.1, 1.9], RED],
]
const offsets: [number, number][] = [[-1, -0.6], [1, -0.48], [0.03, 1.06]]

const data = computed(() => {
  const rng = new Rng(2)
  const X: number[][] = []
  const group: number[] = []
  const sub: number[] = []
  groups.forEach(([centre], gi) => {
    offsets.forEach((off, si) => {
      for (let i = 0; i < 26; i++) {
        X.push([
          rng.normal(centre[0] + gap.value * off[0], 0.2),
          rng.normal(centre[1] + gap.value * off[1], 0.2),
        ])
        group.push(gi)
        sub.push(gi * 3 + si)
      }
    })
  })
  return { X, group, sub }
})

const subColors = computed(() =>
  data.value.sub.map((s) => shades(groups[Math.floor(s / 3)][1], 3)[s % 3]),
)
const ellipses = computed(() =>
  groups.map(([centre, color]) => ({
    x: centre[0] + gap.value * 0.01,
    y: centre[1] + gap.value * 0.19,
    rx: 0.55 + 1.5 * gap.value,
    ry: 0.55 + 1.35 * gap.value,
    color,
  })),
)
const dom: [number, number, number, number] = [-4.2, 4.2, -3.2, 4.2]
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot
        :X="data.X" :labels="data.group" :domain="dom" :point-size="2.8"
        title="partitional" :title-color="BLUE"
      />
      <ClusterPlot
        :X="data.X" :colors="subColors" :domain="dom" :point-size="2.8" :ellipses="ellipses"
        title="hierarchical" :title-color="GREEN"
      />
      <div class="side">
        <p><em class="hl-blue">partitional</em><br />
          <span class="note">one level, K fixed in advance</span></p>
        <p><em class="hl-green">hierarchical</em><br />
          <span class="note">nested groups: each subset splits again</span></p>
        <p class="note">Both panels hold the same 234 points. Only the second
          records that each group is itself three groups.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="gap" :min="0" :max="1.3" label="how far the sub-groups sit apart" :color="GREEN" />
      <Readout
        :items="[
          { label: 'clusters, partitional', value: '3', color: BLUE },
          { label: 'clusters, hierarchical', value: '3 of 3', color: GREEN },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr 0.8fr; gap: 1rem; min-height: 0; }
.side { font-size: 0.85rem; align-self: center; }
.side p { margin: 0 0 0.7rem; line-height: 1.5; }
.controls { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 17rem; }
</style>
