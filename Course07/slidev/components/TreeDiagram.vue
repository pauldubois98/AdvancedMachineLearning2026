<!-- A fitted tree, drawn. Internal nodes carry their question, leaves their
     majority class; the width of a subtree is the number of leaves under it,
     which is how sklearn's plot_tree lays one out too. -->
<script setup lang="ts">
import { computed } from 'vue'
import { Node } from '../lib/tree'
import { BLUE, GREEN, GRID, INK, MUTED, RED } from '../lib/theme'

const props = withDefaults(
  defineProps<{
    root: Node
    /** column names, defaulting to x1, x2, ... */
    names?: string[]
    /** deeper nodes are drawn as a single grey stub */
    maxDepth?: number
    /** a row to route through the tree: its path is thickened */
    probe?: number[] | null
    classColors?: readonly string[]
    title?: string
    leafText?: 'class' | 'value'
  }>(),
  { names: () => [], maxDepth: 4, probe: null, classColors: () => [BLUE, RED, GREEN], title: '', leafText: 'class' },
)

interface Placed {
  node: Node
  x: number
  y: number
  depth: number
  stub: boolean
  onPath: boolean
}

const W = 520
const H = 290

const layout = computed(() => {
  const nodes: Placed[] = []
  const links: { a: Placed; b: Placed; label: string; onPath: boolean }[] = []
  const leavesUnder = (n: Node, d: number): number => {
    if (!n.left || d >= props.maxDepth) return 1
    return leavesUnder(n.left, d + 1) + leavesUnder(n.right!, d + 1)
  }
  const total = leavesUnder(props.root, 0)
  const depthOf = (n: Node, d: number): number =>
    !n.left || d >= props.maxDepth ? d : Math.max(depthOf(n.left, d + 1), depthOf(n.right!, d + 1))
  const maxD = Math.max(1, depthOf(props.root, 0))
  const dy = (H - 54) / maxD

  const place = (n: Node, lo: number, hi: number, d: number, onPath: boolean): Placed => {
    const stub = !!n.left && d >= props.maxDepth
    const p: Placed = {
      node: n,
      x: 28 + ((lo + hi) / 2 / total) * (W - 56),
      y: 26 + d * dy,
      depth: d,
      stub,
      onPath,
    }
    nodes.push(p)
    if (n.left && !stub) {
      const wl = leavesUnder(n.left, d + 1)
      const goesLeft = props.probe ? props.probe[n.feature!] <= n.threshold! : false
      const l = place(n.left, lo, lo + wl, d + 1, onPath && goesLeft)
      const r = place(n.right!, lo + wl, hi, d + 1, onPath && !goesLeft)
      links.push({ a: p, b: l, label: 'yes', onPath: l.onPath })
      links.push({ a: p, b: r, label: 'no', onPath: r.onPath })
    }
    return p
  }
  place(props.root, 0, total, 0, true)
  return { nodes, links }
})

const name = (f: number) => props.names[f] ?? `x${f + 1}`
function question(n: Node): string {
  return `${name(n.feature!)} ≤ ${n.threshold!.toFixed(2)}`
}
function leafLabel(n: Node): string {
  if (props.leafText === 'value') return n.value[0].toFixed(2)
  let arg = 0
  for (let k = 1; k < n.value.length; k++) if (n.value[k] > n.value[arg]) arg = k
  return `class ${arg}`
}
function leafColor(n: Node): string {
  if (props.leafText === 'value') return GREEN
  let arg = 0
  for (let k = 1; k < n.value.length; k++) if (n.value[k] > n.value[arg]) arg = k
  return props.classColors[arg % props.classColors.length]
}
function tint(n: Node): string {
  const c = leafColor(n)
  return c === BLUE ? '#e9f0f8' : c === RED ? '#fdeaea' : '#e8f7e9'
}
</script>

<template>
  <figure class="tree">
    <figcaption v-if="title">{{ title }}</figcaption>
    <svg :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="xMidYMid meet">
      <line
        v-for="(l, i) in layout.links" :key="`l${i}`"
        :x1="l.a.x" :y1="l.a.y + 11" :x2="l.b.x" :y2="l.b.y - 11"
        :style="{ stroke: probe && l.onPath ? GREEN : GRID, strokeWidth: probe && l.onPath ? 2.6 : 1.4 }"
      />
      <template v-for="(p, i) in layout.nodes" :key="`n${i}`">
        <g v-if="p.node.left && !p.stub">
          <rect
            :x="p.x - 46" :y="p.y - 11" width="92" height="22" rx="5"
            :style="{ fill: '#fff', stroke: INK, strokeWidth: 1.4 }"
          />
          <text :x="p.x" :y="p.y + 4" class="mid q">{{ question(p.node) }}</text>
        </g>
        <g v-else-if="p.stub">
          <circle :cx="p.x" :cy="p.y" r="7" :style="{ fill: '#fff', stroke: MUTED, strokeWidth: 1.4 }" />
          <text :x="p.x" :y="p.y + 20" class="mid tiny">…</text>
        </g>
        <g v-else>
          <rect
            :x="p.x - 32" :y="p.y - 11" width="64" height="22" rx="5"
            :style="{ fill: tint(p.node), stroke: leafColor(p.node), strokeWidth: 1.6 }"
          />
          <text :x="p.x" :y="p.y + 4" class="mid leaf" :style="{ fill: leafColor(p.node) }">
            {{ leafLabel(p.node) }}
          </text>
        </g>
      </template>
    </svg>
  </figure>
</template>

<style scoped>
.tree { display: flex; flex-direction: column; height: 100%; min-height: 0; margin: 0; }
figcaption { text-align: center; font-size: 0.82rem; font-weight: 600; margin-bottom: 0.1rem; }
svg { width: 100%; flex: 1 1 0; min-height: 0; display: block; }
.mid { text-anchor: middle; }
.q { font-size: 13px; fill: #1b1b1b; }
.leaf { font-size: 12.5px; font-weight: 600; }
.tiny { font-size: 11px; fill: #9aa0a6; }
</style>
