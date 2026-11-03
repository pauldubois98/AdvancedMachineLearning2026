<!-- The true-risk formula with its terms annotated. The terms are tagged with
     \htmlId, measured once rendered, and each label gets an arrow drawn to the
     term it names, so the arrows follow the formula whatever its width. -->
<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import katex from 'katex'
import { BLUE, GREEN, INK, PURPLE, RED } from '../lib/theme'

const html = katex.renderToString(
  String.raw`\htmlId{tr-R}{R(f)} \;=\; \htmlId{tr-E}{E}_{(X,T)}\big[\htmlId{tr-rho}{\rho}(f(\htmlId{tr-X}{X}), \htmlId{tr-T}{T})\big]`
  + String.raw` \;=\; \int \rho(f(x), t)\, \htmlId{tr-p}{p(x, t)}\, dx\, dt`,
  { displayMode: true, throwOnError: false, output: 'html', trust: true, strict: false },
)

// at: the label's centre, as a share of the width; top labels sit above the formula
const LABELS = [
  { id: 'tr-X', at: 0.3, top: true, color: BLUE, html: 'the data <i>X</i>' },
  { id: 'tr-T', at: 0.66, top: true, color: GREEN, html: 'the target <i>T</i>' },
  { id: 'tr-R', at: 0.1, top: false, color: INK, html: 'the risk of<br>the candidate <i>f</i>' },
  { id: 'tr-E', at: 0.32, top: false, color: PURPLE, html: 'over the law of the data,<br>not over our sample' },
  { id: 'tr-rho', at: 0.58, top: false, color: BLUE, html: 'the loss we chose:<br>squared, hinge, 0–1, …' },
  { id: 'tr-p', at: 0.88, top: false, color: RED, html: 'the law we<br>do not know' },
]

const root = ref<HTMLDivElement>()
const W = ref(800)
const H = ref(240)
const arrows = ref<{ x1: number; y1: number; x2: number; y2: number; color: string }[]>([])
const GAP = 6

function measure() {
  const el = root.value
  if (!el) return
  // the slide is scaled with a transform: bring rectangles back to CSS pixels
  const box = el.getBoundingClientRect()
  const k = box.width / el.offsetWidth || 1
  const rel = (r: DOMRect) => ({
    l: (r.left - box.left) / k, r: (r.right - box.left) / k,
    t: (r.top - box.top) / k, b: (r.bottom - box.top) / k,
  })
  W.value = el.offsetWidth
  H.value = el.offsetHeight
  arrows.value = LABELS.flatMap((L, i) => {
    const term = el.querySelector(`#${L.id}`)
    const lab = el.querySelector<HTMLElement>(`[data-lab="${i}"]`)
    if (!term || !lab) return []
    const a = rel(term.getBoundingClientRect())
    const b = rel(lab.getBoundingClientRect())
    const x2 = (a.l + a.r) / 2
    const x1 = Math.min(Math.max(x2, b.l + 8), b.r - 8)
    return [L.top
      ? { x1, y1: b.b + GAP, x2, y2: a.t - GAP, color: L.color }
      : { x1, y1: b.t - GAP, x2, y2: a.b + GAP, color: L.color }]
  })
}

let ro: ResizeObserver | undefined
onMounted(async () => {
  await nextTick()
  measure()
  ro = new ResizeObserver(measure)
  ro.observe(root.value!)
  document.fonts?.ready.then(measure)
})
onBeforeUnmount(() => ro?.disconnect())
</script>

<template>
  <div ref="root" class="tr">
    <div class="row top">
      <template v-for="(L, i) in LABELS" :key="i"><div v-if="L.top" :data-lab="i" class="lab" :style="{ left: `${L.at * 100}%`, color: L.color }" v-html="L.html" /></template>
    </div>
    <div class="formula" v-html="html" />
    <div class="row bottom">
      <template v-for="(L, i) in LABELS" :key="i"><div v-if="!L.top" :data-lab="i" class="lab" :style="{ left: `${L.at * 100}%`, color: L.color }" v-html="L.html" /></template>
    </div>
    <svg class="arrows" :viewBox="`0 0 ${W} ${H}`" :width="W" :height="H">
      <defs>
        <marker v-for="(a, i) in arrows" :id="`tr-head-${i}`" :key="i" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" :fill="a.color" />
        </marker>
      </defs>
      <line v-for="(a, i) in arrows" :key="i" :x1="a.x1" :y1="a.y1" :x2="a.x2" :y2="a.y2" :stroke="a.color" stroke-width="1.6" :marker-end="`url(#tr-head-${i})`" />
    </svg>
  </div>
</template>

<style scoped>
.tr { position: relative; }
.row { position: relative; height: 2.9rem; }
.row.top { height: 2.4rem; }
.lab { position: absolute; transform: translateX(-50%); white-space: nowrap; text-align: center; font-size: 0.85rem; line-height: 1.25; }
.row.top .lab { top: 0; }
.row.bottom .lab { bottom: 0; }
.formula { margin: 0.9rem 0; }
.formula :deep(.katex-display) { margin: 0; }
.formula :deep(.katex-display > .katex) { font-size: 1.7em; }
.arrows { position: absolute; inset: 0; pointer-events: none; overflow: visible; }
</style>
