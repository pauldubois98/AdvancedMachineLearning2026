<!-- pca_vs_tsne_mnist: 5000 MNIST images, PCA beside t-SNE (computed by
     scripts/make_data_c09.py at three perplexities). -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { MNIST } from '../lib/data'
import { DIGIT, PCA_C, TSNE_C } from '../lib/theme'
import type { Pt } from '../lib/geom'

const perp = ref('30')
const hl = ref(-1)
const H = computed(() => Math.round(hl.value))
const colors = computed(() => MNIST.y.map((k) => (H.value < 0 || k === H.value ? DIGIT[k] : '#e3e5e8')))
const ts = computed(() => MNIST.tsne[Number(perp.value)] as Pt[])
function dom(P: Pt[]): [number, number, number, number] {
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity
  for (const [x, y] of P) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y) }
  const p = 0.04 * (x1 - x0)
  return [x0 - p, x1 + p, y0 - p, y1 + p]
}
const legend = DIGIT.map((c, k) => ({ k, c }))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Plane :X="MNIST.pca as Pt[]" :colors="colors" :size="1.6" :alpha="0.7" :domain="dom(MNIST.pca as Pt[])" title="PCA" :title-color="PCA_C" />
      <Plane :X="ts" :colors="colors" :size="1.6" :alpha="0.7" :domain="dom(ts)" :title="`t-SNE, perplexity ${perp}`" :title-color="TSNE_C" />
    </div>
    <div class="foot">5000 MNIST images (28 × 28 = 784 pixels). PCA mixes most digits in its two axes;
      t-SNE separates the ten classes without ever seeing the labels.
      <span class="legend"><span v-for="l in legend" :key="l.k" :style="{ color: l.c }">{{ l.k }}</span></span></div>
    <div class="controls">
      <Choice v-model="perp" label="perplexity" :options="MNIST.perps.map((p) => ({ value: String(p), label: String(p), color: TSNE_C }))" />
      <Knob v-model="hl" :min="-1" :max="9" :step="1" :digits="0" label="highlight digit (−1: all)" :color="H < 0 ? '#1b1b1b' : DIGIT[H]" />
    </div>
  </div>
</template>

<style scoped>
.legend { margin-left: 0.6rem; font-weight: 700; letter-spacing: 0.25rem; }
</style>
