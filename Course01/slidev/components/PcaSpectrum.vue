<!-- pca_spectrum: the 1797 digits have 64 pixels, but a few components keep
     most of the variance; rebuild six digits from q of them. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import digits from '../../data/digits.json'
import { pcaFit, reconstruct } from '../lib/pca'
import { BLUE, GREEN, INK, PURPLE } from '../lib/theme'

const q = ref(10)
const D = digits as { X: number[][]; y: number[] }
const fit = pcaFit(D.X)
const tot = fit.values.reduce((a, b) => a + b, 0)
const cum: [number, number][] = []
fit.values.reduce((s, v, i) => { cum.push([i + 1, (s + v) / tot]); return s + v }, 0)
const kept = computed(() => cum[q.value - 1][1])
const PICK = [4, 10, 9, 13, 11, 6] // six of the digits: 4 0 9 3 1 6
const orig = PICK.map((i) => D.X[i])
const rec = computed(() => orig.map((x) => reconstruct(x, fit, q.value)))
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Computed live:</b> PCA on scikit-learn's 1797 handwritten digits, 8 × 8 pixels each, so 64 features. Each digit is rebuilt from its first q principal components: x̂ = μ + Σ<sub>j≤q</sub> (pⱼᵀ(x − μ)) pⱼ.</div>
    <div class="r2">
      <LineChart :series="[{ points: cum, color: BLUE }, { points: [[q, 0], [q, kept], [0, kept]], color: GREEN, width: 1.6, dash: '5,4' }]"
        :x-domain="[0, 64]" :y-domain="[0, 1.02]" :x-ticks="[0, 10, 20, 30, 40, 50, 60]" :y-ticks="[0, 0.2, 0.4, 0.6, 0.8, 1]"
        x-label="number of components q" y-label="variance kept" :dots="[{ x: q, y: kept, color: GREEN, r: 5 }]"
        title="64 pixels, most of them redundant" />
      <div class="digits">
        <span class="lab" :style="{ color: INK }">original</span>
        <DigitImg v-for="(x, i) in orig" :key="`o${i}`" :px="x" />
        <span class="lab" :style="{ color: GREEN }">q = {{ q }}</span>
        <DigitImg v-for="(x, i) in rec" :key="`r${i}`" :px="x" />
      </div>
    </div>
    <div class="foot">q = <b :style="{ color: GREEN }">{{ q }}</b> components keep <b :style="{ color: GREEN }">{{ (100 * kept).toFixed(0) }}%</b> of the variance: {{ q }} numbers per digit instead of 64.</div>
    <div class="controls"><Knob v-model="q" :min="1" :max="64" :step="1" :digits="0" label="components q" :color="PURPLE" /></div>
  </div>
</template>

<style scoped>
.digits { display: grid; grid-template-columns: auto repeat(6, 1fr); gap: 0.5rem; align-content: center; align-items: center; padding: 0 0.5rem; }
.lab { font-size: 0.85rem; text-align: right; padding-right: 0.3rem; white-space: nowrap; }
</style>
