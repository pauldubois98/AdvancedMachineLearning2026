<!-- extract_example: keep a cluster unless its children are worth more. The
     sliders are the stabilities, and the selection follows them bottom up. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { GREEN, GRID, INK, MUTED, RED } from '../lib/theme'

const stab = ref({ A1: 2, A2: 3, B1: 5, B2: 7, A: 6, B: 9, root: 10 })

/** excess of mass, bottom up: a parent survives only if it beats its children */
const result = computed(() => {
  const score: Record<string, number> = {}
  const chosen: Record<string, boolean> = {}
  for (const leaf of ['A1', 'A2', 'B1', 'B2']) {
    score[leaf] = stab.value[leaf as keyof typeof stab.value]
    chosen[leaf] = true
  }
  for (const [parent, kids] of [['A', ['A1', 'A2']], ['B', ['B1', 'B2']]] as [string, string[]][]) {
    const sum = kids.reduce((s, k) => s + score[k], 0)
    const own = stab.value[parent as keyof typeof stab.value]
    chosen[parent] = own >= sum
    score[parent] = Math.max(own, sum)
  }
  const sum = score.A + score.B
  chosen.root = stab.value.root >= sum
  score.root = Math.max(stab.value.root, sum)
  // the root is never a cluster of its own
  const selected: string[] = []
  const walk = (id: string, kids: Record<string, string[]>) => {
    if (id !== 'root' && chosen[id]) { selected.push(id); return }
    ;(kids[id] ?? []).forEach((k) => walk(k, kids))
  }
  walk('root', { root: ['A', 'B'], A: ['A1', 'A2'], B: ['B1', 'B2'] })
  return { score, chosen, selected }
})

const nodes: { id: string; x: number; y: number }[] = [
  { id: 'root', x: 50, y: 12 },
  { id: 'A', x: 24, y: 48 },
  { id: 'B', x: 76, y: 48 },
  { id: 'A1', x: 12, y: 84 },
  { id: 'A2', x: 36, y: 84 },
  { id: 'B1', x: 64, y: 84 },
  { id: 'B2', x: 88, y: 84 },
]
const edges: [string, string][] = [
  ['root', 'A'], ['root', 'B'], ['A', 'A1'], ['A', 'A2'], ['B', 'B1'], ['B', 'B2'],
]
const at = (id: string) => nodes.find((n) => n.id === id)!
const colorOf = (id: string) =>
  result.value.selected.includes(id) ? GREEN : id === 'root' ? MUTED : GRID
</script>

<template>
  <div class="wrap">
    <div class="tree">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none">
        <line
          v-for="([a, b], i) in edges" :key="i"
          :x1="at(a).x" :y1="at(a).y + 5" :x2="at(b).x" :y2="at(b).y - 5"
          :style="{ stroke: GRID, strokeWidth: 0.4 }"
        />
      </svg>
      <div
        v-for="n in nodes" :key="n.id" class="node"
        :style="{ left: `${n.x}%`, top: `${n.y}%`, borderColor: colorOf(n.id), color: result.selected.includes(n.id) ? GREEN : INK }"
      >
        {{ n.id === 'root' ? 'root' : n.id }}: {{ stab[n.id as keyof typeof stab] }}
        <span v-if="result.selected.includes(n.id)" class="kept">kept</span>
      </div>
      <div class="tests">
        <div class="test" :style="{ color: result.chosen.A ? RED : GREEN }">
          A: children {{ result.score.A1 + result.score.A2 }}
          {{ result.chosen.A ? '≤' : '>' }} {{ stab.A }}
          → {{ result.chosen.A ? 'keep A' : 'keep A₁ and A₂' }}
        </div>
        <div class="test" :style="{ color: result.chosen.B ? RED : GREEN }">
          B: children {{ result.score.B1 + result.score.B2 }}
          {{ result.chosen.B ? '≤' : '>' }} {{ stab.B }}
          → {{ result.chosen.B ? 'keep B' : 'keep B₁ and B₂' }}
        </div>
      </div>
    </div>
    <div class="right">
      <p class="note">Walk the condensed tree bottom up. At each node, compare
        its own stability with the total of its children: if the children are
        worth more, drop the parent and keep them; otherwise keep the parent and
        drop everything below it.</p>
      <div class="controls">
        <Knob v-model="stab.A1" :min="0" :max="20" :step="1" label="A₁" :digits="0" :color="GREEN" />
        <Knob v-model="stab.A2" :min="0" :max="20" :step="1" label="A₂" :digits="0" :color="GREEN" />
        <Knob v-model="stab.A" :min="0" :max="20" :step="1" label="A" :digits="0" :color="GREEN" />
        <Knob v-model="stab.B1" :min="0" :max="20" :step="1" label="B₁" :digits="0" :color="GREEN" />
        <Knob v-model="stab.B2" :min="0" :max="20" :step="1" label="B₂" :digits="0" :color="GREEN" />
        <Knob v-model="stab.B" :min="0" :max="20" :step="1" label="B" :digits="0" :color="GREEN" />
      </div>
      <Readout
        :items="[
          { label: 'clusters returned', value: result.selected.join(', ') || 'none', color: GREEN },
          { label: 'everything else', value: 'noise', color: MUTED },
        ]"
      />
      <p class="note">The root is never returned on its own: that would call
        the whole dataset one cluster. Raise A₁ and A₂ until they beat A and the
        answer becomes four clusters instead of three.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.tree { position: relative; min-height: 0; }
svg { position: absolute; inset: 0; width: 100%; height: 100%; }
.node {
  position: absolute; transform: translate(-50%, -50%);
  border: 1.8px solid; border-radius: 0.3rem; background: white;
  padding: 0.1rem 0.4rem; font-size: 0.78rem; white-space: nowrap;
}
.kept { font-size: 0.68rem; color: #00ab0e; margin-left: 0.25rem; }
.tests { position: absolute; left: 0; bottom: 0; font-size: 0.78rem; line-height: 1.6; }
.right { display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; }
.controls { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.3rem 0.9rem; }
</style>
