<!-- eq_gaussian_loss, eq_poisson_loss, eq_is_loss: the derivation of one loss
     from one noise model, next to that noise drawn. Move the model value y:
     the law of the data x moves with it, and so does the cost of the
     observed x. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { dIS, dKL, dQuad, range } from '../lib/losses'
import { niceTicks } from '../lib/ticks'
import { BLUE, GOLD, GREEN, INK } from '../lib/theme'

const props = defineProps<{ kind: 'gauss' | 'poisson' | 'exp' }>()
const color = { gauss: BLUE, poisson: GREEN, exp: GOLD }[props.kind]
const y = ref(props.kind === 'poisson' ? 4 : 2)
const x = ref(props.kind === 'poisson' ? 6 : 3)
const sigma = ref(0.8)
const XMAX = props.kind === 'poisson' ? 16 : 8

function logFact(k: number) { let s = 0; for (let i = 2; i <= k; i++) s += Math.log(i); return s }
const density = computed(() => {
  if (props.kind === 'poisson') {
    return Array.from({ length: XMAX + 1 }, (_, k) => [k, Math.exp(k * Math.log(y.value) - y.value - logFact(k))] as [number, number])
  }
  return range(0.001, XMAX, 240).map((v) => [v, props.kind === 'gauss'
    ? Math.exp(-((v - y.value) ** 2) / (2 * sigma.value ** 2)) / Math.sqrt(2 * Math.PI * sigma.value ** 2)
    : Math.exp(-v / y.value) / y.value] as [number, number])
})
const pMax = computed(() => Math.max(...density.value.map((p) => p[1])) * 1.15)
const d = (xx: number, yy: number) => (props.kind === 'gauss' ? dQuad(xx, yy) : props.kind === 'poisson' ? dKL(xx, yy) : dIS(xx, yy))
const lossCurve = computed(() => range(0.05, XMAX, 240).map((v) => [v, d(x.value, v)] as [number, number]))
const lossMax = computed(() => Math.min(Math.max(...lossCurve.value.map((p) => p[1])), props.kind === 'gauss' ? 20 : 8))

const text = {
  gauss: {
    head: 'Gaussian noise',
    law: 'x \\mid y \\sim \\mathcal{N}(y, \\sigma^2)',
    lawNote: 'i.e. x = y + ε: the error is added, and its size does not depend on y',
    steps: [
      ['p(x \\mid y) = \\frac{1}{\\sqrt{2\\pi\\sigma^2}}\\, \\exp\\!\\left(-\\frac{(x - y)^2}{2\\sigma^2}\\right)', ''],
      ['-\\log p(x \\mid y) = \\frac{(x - y)^2}{2\\sigma^2} + \\tfrac{1}{2}\\log(2\\pi\\sigma^2)', 'the last term has no y in it: drop it'],
      ['d(x, y) = (x - y)^2', 'already zero at x = y, so c(x) = 0; the factor 1/2σ² only rescales the whole loss'],
    ],
    box: 'D(X, WH) = \\|X - WH\\|_F^2', boxNote: 'the Frobenius norm, squared',
  },
  poisson: {
    head: 'Poisson counts',
    law: 'x \\mid y \\sim \\mathrm{Poisson}(y)',
    lawNote: 'how many times something happened: words, photons, clicks',
    steps: [
      ['p(x \\mid y) = \\frac{y^{x} e^{-y}}{x!}', ''],
      ['-\\log p(x \\mid y) = y - x \\log y + \\log(x!)', 'again, log(x!) carries no y'],
      ['d(x, y) = y - x \\log y + [\\,x \\log x - x\\,] = x \\log \\frac{x}{y} - x + y', 'the bracket is c(x), not free here: it is what makes d(x, x) = 0'],
    ],
    box: 'D(X, WH) = \\mathrm{KL}(X, WH)', boxNote: 'the generalized Kullback–Leibler divergence',
  },
  exp: {
    head: 'Multiplicative noise',
    law: 'x = y \\cdot \\varepsilon, \\;\\; \\varepsilon \\sim \\mathrm{Exp}(1)',
    lawNote: 'the error is a percentage, not an amount',
    steps: [
      ['p(x \\mid y) = \\frac{1}{y}\\, e^{-x/y}', 'the density of yε; also Gamma(1, y), the law of the power of a Gaussian signal'],
      ['-\\log p(x \\mid y) = \\frac{x}{y} + \\log y', ''],
      ['d(x, y) = \\frac{x}{y} + \\log y + [\\,-\\log x - 1\\,] = \\frac{x}{y} - \\log \\frac{x}{y} - 1', 'the bracket is c(x), again fixed by d(x, x) = 0'],
      ['d(\\lambda x, \\lambda y) = d(x, y)', 'the λ cancels inside both terms: scale invariance, for free'],
    ],
    box: 'D(X, WH) = D_{\\mathrm{IS}}(X, WH)', boxNote: 'Itakura–Saito',
  },
}[props.kind]
</script>

<template>
  <div class="wrap">
    <div class="deriv">
      <div class="head"><b :style="{ color }">{{ text.head }}</b> <Tex :formula="text.law" /> <span class="note">{{ text.lawNote }}</span></div>
      <div v-for="(s, i) in text.steps" :key="i" class="step">
        <Tex :formula="s[0]" display />
        <div v-if="s[1]" class="note">{{ s[1] }}</div>
      </div>
      <div class="box" :style="{ borderColor: color, color }"><Tex :formula="text.box" />, {{ text.boxNote }}</div>
    </div>
    <div class="live">
      <LineChart
        :series="kind === 'poisson' ? [] : [{ points: density, color, width: 2.2 }]"
        :bars="kind === 'poisson' ? density.map(([k, p]) => ({ x: k, y: p, y0: 0, w: 0.7, color, alpha: k === Math.round(x) ? 1 : 0.45 })) : []"
        :vlines="[{ x: x, color: '#1b1b1b', dash: '4 3' }, { x: y, color, dash: '2 3' }]"
        :x-domain="[kind === 'poisson' ? -0.6 : 0, XMAX]" :y-domain="[0, pMax]" x-label="x, the data" :x-ticks="niceTicks(0, XMAX, 4)" :y-ticks="[]"
        :title="`p(x | y): the law of the data, for y = ${y.toFixed(kind === 'poisson' ? 1 : 2)}`" :title-color="color"
      />
      <LineChart
        :series="[{ points: lossCurve, color, width: 2.2 }]"
        :dots="[{ x: y, y: d(x, y), color: '#1b1b1b', r: 4.5 }]"
        :vlines="[{ x: x, color: '#9aa0a6', dash: '4 3' }]"
        :x-domain="[0, XMAX]" :y-domain="[0, lossMax]" x-label="y, the model" :x-ticks="niceTicks(0, XMAX, 4)" :y-ticks="[]"
        :title="`d(x, y) for the observed x = ${x.toFixed(kind === 'poisson' ? 0 : 2)}: lowest at y = x`"
      />
      <div class="controls">
        <Knob v-model="y" :min="kind === 'poisson' ? 0.5 : 0.2" :max="XMAX * 0.8" :step="0.05" label="model y" :color="color" />
        <Knob v-model="x" :min="kind === 'poisson' ? 0 : 0.1" :max="XMAX * 0.9" :step="kind === 'poisson' ? 1 : 0.05" label="observed x" :digits="kind === 'poisson' ? 0 : 2" :color="INK" />
        <Knob v-if="kind === 'gauss'" v-model="sigma" :min="0.2" :max="2" :step="0.05" label="σ" :color="INK" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 1fr; gap: 1.8rem; height: 100%; min-height: 0; }
.deriv { display: flex; flex-direction: column; gap: 0.25rem; justify-content: center; font-size: 0.9rem; }
.deriv :deep(.katex-display) { margin: 0.15rem 0 0; text-align: left; }
.deriv :deep(.katex-display > .katex) { font-size: 1.1em; text-align: left; }
.head { font-size: 1rem; }
.step .note { font-size: 0.75rem; }
.box { border: 2px solid; border-radius: 10px; padding: 0.45rem; text-align: center; margin-top: 0.4rem; }
.live { display: grid; grid-template-rows: 1fr 1fr auto; gap: 0.4rem; min-height: 0; }
.live .controls > :deep(.knob) { min-width: 9rem; }
</style>
