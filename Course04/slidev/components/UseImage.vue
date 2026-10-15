<!-- use_image: every pixel of a real photo is a point (r, g, b); k-means on a
     sample of them, then each pixel is painted in its centre's colour. The bar
     under the result is the palette, each centre as wide as its pixels. -->
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { assign, kmeans } from '../lib/cluster'
import { flower } from '../lib/real'
import { GREEN, INK } from '../lib/theme'
import { Rng } from '../lib/rng'

const k = ref(3)
const { width, height, px } = flower
const sample = (() => {
  const rng = new Rng(7)
  return Array.from({ length: 2500 }, () => px[Math.floor(rng.next() * px.length)])
})()

const quant = computed(() => {
  const run = kmeans(sample, k.value, 0, 6)
  const labels = assign(px, run.mu)
  const counts = run.mu.map(() => 0)
  labels.forEach((l) => counts[l]++)
  const palette = run.mu
    .map((m, c) => ({ color: `rgb(${m.map((v) => Math.round(255 * v)).join(',')})`, share: counts[c] / px.length }))
    .sort((a, b) => b.share - a.share)
  return { mu: run.mu, labels, palette }
})

const orig = ref<HTMLCanvasElement | null>(null)
const out = ref<HTMLCanvasElement | null>(null)
function paint(el: HTMLCanvasElement | null, colour: (i: number) => number[]) {
  if (!el) return
  el.width = width
  el.height = height
  const ctx = el.getContext('2d')!
  const img = ctx.createImageData(width, height)
  for (let i = 0; i < px.length; i++) {
    const c = colour(i)
    img.data[4 * i] = 255 * c[0]
    img.data[4 * i + 1] = 255 * c[1]
    img.data[4 * i + 2] = 255 * c[2]
    img.data[4 * i + 3] = 255
  }
  ctx.putImageData(img, 0, 0)
}
onMounted(() => {
  paint(orig.value, (i) => px[i])
  paint(out.value, (i) => quant.value.mu[quant.value.labels[i]])
})
watch(quant, (q) => paint(out.value, (i) => q.mu[q.labels[i]]))
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <figure>
        <figcaption>the photo: each pixel is a point (r, g, b)</figcaption>
        <canvas ref="orig" />
        <div class="note">16.7 million possible colours</div>
      </figure>
      <figure>
        <figcaption :style="{ color: GREEN }">K = {{ k }} colours: each pixel painted in its centre's colour</figcaption>
        <canvas ref="out" />
        <div class="palette">
          <span v-for="(p, i) in quant.palette" :key="i" :style="{ flexGrow: p.share, background: p.color }" />
        </div>
      </figure>
    </div>
    <div class="controls">
      <Knob v-model="k" :min="2" :max="12" :step="1" label="K, colours" :digits="0" :color="INK" />
      <span class="note">The bar is the palette: one centre per colour, as wide as the pixels it took.</span>
    </div>
    <div class="credit">photo: flickr/vultilion, CC BY 2.0 (scikit-learn sample image)</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6rem; min-height: 0; }
figure { margin: 0; display: flex; flex-direction: column; align-items: center; min-height: 0; gap: 0.3rem; }
figcaption { font-size: 0.82rem; font-weight: 600; text-align: center; }
canvas { width: 100%; aspect-ratio: 160 / 107; border-radius: 3px; }
.palette { display: flex; width: 100%; height: 14px; border-radius: 2px; overflow: hidden; }
.palette span { flex-basis: 0; }
.controls { display: flex; gap: 1.4rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 12rem; }
.credit { text-align: right; color: #9aa0a6; font-size: 0.6rem; }
</style>
