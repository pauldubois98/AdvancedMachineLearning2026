<!-- gmm_iris: three species of iris, two measurements. The mixture never sees
     the species; its components are matched to them afterwards. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmax, em2, kmeansStart, resp2, start2, type Pt } from '../lib/gmm'
import { IRIS_FEATURES, IRIS_X, IRIS_Y } from '../lib/iris'
import { fmt } from '../lib/charts'
import { COMP, GREEN, INK, MUTED } from '../lib/theme'

const pair = ref('petal')
const startKind = ref('kmeans')
const seed = ref(1)
const cols = computed(() => (pair.value === 'petal' ? [2, 3] : [0, 1]))
const X = computed<Pt[]>(() => IRIS_X.map((r) => [r[cols.value[0]], r[cols.value[1]]]))
const PERMS = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]]
const fit = computed(() => {
  const st = startKind.value === 'kmeans' ? kmeansStart(X.value, 3, 0) : start2(X.value, 3, seed.value)
  const m = em2(X.value, st, 300).at(-1)!
  const g = X.value.map((x) => resp2(x, m))
  const z = g.map(argmax)
  const best = PERMS.reduce((a, pm) => {
    const hit = z.filter((k, i) => pm[k] === IRIS_Y[i]).length
    return hit > a.hit ? { pm, hit } : a
  }, { pm: PERMS[0], hit: -1 })
  return { m, zz: z.map((k) => best.pm[k]), pm: best.pm, acc: best.hit / X.value.length, unsure: g.filter((r) => Math.max(...r) < 0.9).length }
})
const dom = computed<[number, number, number, number]>(() => {
  const xs = X.value.map((p) => p[0]), ys = X.value.map((p) => p[1])
  return [Math.min(...xs) - 0.3, Math.max(...xs) + 0.3, Math.min(...ys) - 0.3, Math.max(...ys) + 0.3]
})
</script>

<template>
  <div class="wrap">
    <div class="note top">Three flower species; the mixture never sees which is which</div>
    <div class="body">
      <Plane :X="X" :colors="IRIS_Y.map((k) => COMP[k])" :size="3.2" :domain="dom" :equal="false" axes
        :x-label="IRIS_FEATURES[cols[0]]" :y-label="IRIS_FEATURES[cols[1]]" title="the true species" :title-color="MUTED" />
      <Plane :X="X" :colors="fit.zz.map((k) => COMP[k])" :size="3.2" :domain="dom" :equal="false" axes
        :x-label="IRIS_FEATURES[cols[0]]" :y-label="IRIS_FEATURES[cols[1]]"
        :ellipses="fit.m.mu.map((mu, k) => ({ mu, S: fit.m.S[k], color: COMP[fit.pm[k]], width: 1.4 }))"
        title="the mixture's components" :title-color="GREEN" />
      <div class="side">
        <div class="h" :style="{ color: GREEN }">Results</div>
        <p>— <b>{{ (100 * fit.acc).toFixed(0) }}%</b> of the flowers land in the component of their own species</p>
        <p>— the two overlapping species are where the mistakes are made</p>
        <p>— {{ fit.unsure }} of the 150 carry no component above 0.9; a botanist would hesitate too</p>
        <p class="note">ℓ = {{ fmt(fit.m.ll, 1) }}. A random start can find a slightly higher ℓ and a worse match: the likelihood is not the species.</p>
        <p class="credit">data: Fisher's iris, scikit-learn</p>
      </div>
    </div>
    <div class="controls">
      <Choice v-model="pair" :options="[{ value: 'petal', label: 'petals' }, { value: 'sepal', label: 'sepals' }]" label="measure" />
      <Choice v-model="startKind" :options="[{ value: 'kmeans', label: 'k-means start' }, { value: 'random', label: 'random start' }]" label="start" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" label="seed" :digits="0" :color="INK" :disabled="startKind === 'kmeans'" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 1fr 0.85fr; gap: 1.4rem; min-height: 0; }
.side { align-self: center; font-size: 0.82rem; }
</style>
