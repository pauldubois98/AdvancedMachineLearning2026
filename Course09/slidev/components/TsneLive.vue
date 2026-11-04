<!-- A live run, used by several slides: t-SNE (or SNE) on the 10-D blobs,
     the 600 digits or the swiss roll, optionally beside PCA. The map forms as
     you watch; any knob starts it again. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { DIGITS, blobs, swissRoll } from '../lib/data'
import { conditionalP, Embedding, jointP, pca, sqdist, type Kernel } from '../lib/sne'
import { useLiveRun } from '../lib/run'
import { COMP, DIGIT, GOLD, HIGH, PCA_C, TSNE_C, rgb, viridis } from '../lib/theme'
import type { Pt } from '../lib/geom'

const props = withDefaults(defineProps<{
  data: 'blobs' | 'digits' | 'roll'
  knobs?: string[]
  kernels?: Kernel[]
  showPca?: boolean
  perp?: number
  seed?: number
  iters?: number
  foot?: string
}>(), { knobs: () => ['perp'], kernels: () => ['t'], showPca: false, perp: 30, seed: 1, iters: 1000, foot: '' })

const perp = ref(props.perp)
const seed = ref(props.seed)
const wide = ref(2)
const far = ref(60)
const ds = computed(() => {
  if (props.data === 'digits') return { X: DIGITS.X, colors: DIGITS.y.map((k) => DIGIT[k]) }
  if (props.data === 'roll') {
    const r = swissRoll(600, 1.6)
    return { X: r.X, colors: r.t.map((t) => rgb(viridis((t - 1.5 * Math.PI) / (3 * Math.PI)))) }
  }
  const b = blobs({ wide: wide.value, far: far.value })
  return { X: b.X, colors: b.g.map((k) => COMP[k]) }
})
const P = computed(() => {
  const n = ds.value.X.length
  return jointP(conditionalP(sqdist(ds.value.X), n, Math.min(perp.value, (n - 1) / 3)).P, n)
})
const runs = props.kernels.map((k) => useLiveRun(
  () => new Embedding(P.value, ds.value.X.length, { kind: k, seed: Math.round(seed.value) }),
  [P, seed], props.iters))
const pcaPts = computed<Pt[]>(() => pca(ds.value.X, 2).Z.map((z) => [z[0], z[1]]))
function dom(Pp: number[][]): [number, number, number, number] {
  if (!Pp.length) return [-1, 1, -1, 1]
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity
  for (const [x, y] of Pp) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y) }
  const p = 0.06 * Math.max(x1 - x0, y1 - y0, 1e-6)
  return [x0 - p, x1 + p, y0 - p, y1 + p]
}
const size = computed(() => (props.data === 'blobs' ? 2.6 : 2.2))
const name = (k: Kernel) => (k === 't' ? 't-SNE' : 'SNE')
</script>

<template>
  <div class="cmp">
    <div :class="showPca || kernels.length > 1 ? 'r2' : ''" style="min-height: 0">
      <Plane v-if="showPca" :X="pcaPts" :colors="ds.colors" :size="size" :alpha="0.8" :domain="dom(pcaPts)" title="PCA" :title-color="PCA_C" />
      <Plane v-for="(r, k) in runs" :key="k" :X="r.pts.value as Pt[]" :colors="ds.colors" :size="size" :alpha="0.8" :domain="dom(r.pts.value)"
        :title="`${name(kernels[k])}: iteration ${r.it.value}, KL = ${r.kl.value.toFixed(3)}`"
        :title-color="kernels[k] === 't' ? TSNE_C : HIGH" />
    </div>
    <div class="foot" v-html="foot" />
    <div class="controls">
      <Knob v-if="knobs.includes('perp')" v-model="perp" :min="2" :max="150" log label="perplexity" :color="TSNE_C" />
      <Knob v-if="knobs.includes('seed')" v-model="seed" :min="1" :max="20" :step="1" :digits="0" label="seed" :color="GOLD" />
      <Knob v-if="knobs.includes('wide')" v-model="wide" :min="0.5" :max="5" :step="0.1" label="spread of the wide cluster" :color="COMP[0]" />
      <Knob v-if="knobs.includes('far')" v-model="far" :min="15" :max="150" :step="1" :digits="0" label="distance to the far cluster" :color="COMP[2]" />
      <button class="snap" @click="runs.forEach((r) => r.restart())">run again</button>
    </div>
  </div>
</template>

<style scoped>
.snap { border: 1px solid #d8dadd; border-radius: 0.3rem; padding: 0.16rem 0.6rem; font-size: 0.8rem; background: white; cursor: pointer; }
.snap:hover { border-color: #9aa0a6; }
</style>
