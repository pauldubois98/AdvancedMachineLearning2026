<!-- complete_data_idea: suppose, for a moment, the labels were known. With
     them, each class is a plain Gaussian sample. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, ANIMAL_FIT, resp1 } from '../lib/gmm'
import { bars, edges, stacked } from '../lib/charts'
import { COMP, GREEN, INK } from '../lib/theme'

const known = ref(true)
const E = edges(81.5, 98.5, 1)
const z = ANIMALS.map((x) => (resp1(x, ANIMAL_FIT)[0] > 0.5 ? 0 : 1))
const groups = [ANIMALS.filter((_, i) => z[i] === 0), ANIMALS.filter((_, i) => z[i] === 1)]
const stats = groups.map((g) => {
  const m = g.reduce((a, b) => a + b, 0) / g.length
  return { n: g.length, m, s: Math.sqrt(g.reduce((a, b) => a + (b - m) ** 2, 0) / g.length) }
})
const theBars = computed(() => (known.value ? stacked(groups, E, COMP, { alpha: 0.8 }) : bars(ANIMALS, E, { alpha: 0.8 })))
</script>

<template>
  <div class="wrap">
    <div class="note top">Suppose, for a moment, that the labels were known</div>
    <div class="body">
      <div class="col">
        <LineChart
          :series="[]" :bars="theBars" :x-domain="[81, 99]" :y-domain="[0, 62]" x-label="length (mm)"
          :x-ticks="[82, 86, 90, 94, 98]" :y-ticks="[]" :title="known ? 'Wish data: (xᵢ, zᵢ)ᵢ' : 'Data: (xᵢ)ᵢ'" :title-color="known ? GREEN : INK"
        />
      </div>
      <div class="side">
        <div class="h" :style="{ color: GREEN }">With the labels</div>
        <p>— each class is a plain Gaussian sample</p>
        <p>— mean and variance, class by class</p>
        <p>— p<sub>k</sub> is just the share of the class</p>
        <p>— the estimation is a one-liner</p>
        <table v-if="known" class="plain" style="margin-top: 0.6rem">
          <tr><th></th><th>share</th><th>mean</th><th>sd</th></tr>
          <tr v-for="(s, k) in stats" :key="k" :style="{ color: COMP[k] }">
            <td>class {{ k + 1 }}</td><td>{{ (s.n / ANIMALS.length).toFixed(2) }}</td><td>{{ s.m.toFixed(1) }}</td><td>{{ s.s.toFixed(2) }}</td>
          </tr>
        </table>
        <p class="note" style="margin-top: 0.6rem">The labels are exactly the information the generator threw away.</p>
      </div>
    </div>
    <div class="controls">
      <Toggle v-model="known" label="pretend the labels are known" :color="GREEN" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; min-height: 0; }
.col { min-height: 0; }
.side { align-self: center; }
</style>
