<!-- kmeans_vs_gmm: same data, same K. k-means cuts halfway between two
     centres; the mixture follows the shape of each cluster. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmax, em2, kmeans, kmeansStart, mixPdf2, resp2, sampleMix2, TWO_BLOBS } from '../lib/gmm'
import { COMP, GREEN, INK, RED } from '../lib/theme'

const seed = ref(3)
const n = ref(280)
const run = computed(() => {
  const { X } = sampleMix2(TWO_BLOBS, n.value, seed.value)
  const km = kmeans(X, 2, 0)
  const fit = em2(X, kmeansStart(X, 2, 0), 120).at(-1)!
  // name the mixture components after the nearest k-means centre
  const d = (a: number[], b: number[]) => (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
  const flip = d(fit.mu[0], km.centers[0]) > d(fit.mu[0], km.centers[1])
  const g = flip ? { p: [...fit.p].reverse(), mu: [...fit.mu].reverse(), S: [...fit.S].reverse() } : fit
  const zk = [...km.labels]
  const zg = X.map((x) => argmax(resp2(x, g)))
  const agree = zk.filter((v, i) => v === zg[i]).length / X.length
  const dmax = Math.max(...X.map((x) => mixPdf2(x, g)))
  return { X, km, g, zk, zg, dmax, agree: Math.max(agree, 1 - agree) }
})
</script>

<template>
  <div class="wrap">
    <div class="note top">Same data, same K</div>
    <div class="body">
      <Plane
        :X="run.X" :colors="run.zk.map((k) => COMP[k])" :size="3" :domain="[-3.6, 3.6, -2.8, 2.8]"
        :levels="[{ f: (x: number, y: number) => (x - run.km.centers[0][0]) ** 2 + (y - run.km.centers[0][1]) ** 2 - (x - run.km.centers[1][0]) ** 2 - (y - run.km.centers[1][1]) ** 2, level: 0, color: INK }]"
        :markers="run.km.centers.map((c) => ({ at: c, color: INK, shape: 'x', size: 7 }))"
        title="k-means" :title-color="RED"
      />
      <Plane
        :X="run.X" :colors="run.zg.map((k) => COMP[k])" :size="3" :domain="[-3.6, 3.6, -2.8, 2.8]"
        :levels="[{ f: (x: number, y: number) => (mixPdf2([x, y], run.g) > 0.004 * run.dmax ? resp2([x, y], run.g)[0] : NaN), level: 0.5, color: INK }]"
        :ellipses="run.g.mu.map((mu, k) => ({ mu, S: run.g.S[k], color: COMP[k], width: 1.4 }))"
        title="Gaussian mixture" :title-color="GREEN"
      />
      <div class="side">
        <div class="h" :style="{ color: GREEN }">GMM gives</div>
        <p>— a shape per cluster, not just a centre</p>
        <p>— a probability, not an assignment</p>
        <p class="note" style="margin-top: 0.6rem">The two labellings agree on {{ (100 * run.agree).toFixed(0) }}% of the {{ run.X.length }} points.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="seed" :min="1" :max="40" :step="1" label="sample seed" :digits="0" :color="INK" />
      <Knob v-model="n" :min="60" :max="1000" :step="10" label="n" :digits="0" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 1fr 0.7fr; gap: 1.2rem; min-height: 0; }
.side { align-self: center; }
</style>
