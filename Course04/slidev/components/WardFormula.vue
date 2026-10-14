<!-- eq_ward: the Ward distance as a function of the two sizes. The factor in
     front is what keeps the tree balanced: big clusters are expensive to join. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, GOLD, RED } from '../lib/theme'

const ni = ref(10)
const nj = ref(10)
const dist = ref(2)

const factor = computed(() => Math.sqrt((2 * ni.value * nj.value) / (ni.value + nj.value)))
const D = computed(() => factor.value * dist.value)
const deltaJ = computed(() => ((ni.value * nj.value) / (ni.value + nj.value)) * dist.value ** 2)
/** the same curve for a singleton joining a cluster of growing size */
/** The y scale is drawn, so moving D(m_i, m_j) is visible on the axis and not
 *  only in the numbers. */
const yMax = computed(() => Math.max(3, Math.sqrt((2 * 80 * nj.value) / (80 + nj.value)) * dist.value * 1.08))
const yTicks = computed(() => {
  const step = niceStep(yMax.value / 4)
  const out: number[] = []
  for (let v = 0; v <= yMax.value; v += step) out.push(Number(v.toFixed(2)))
  return out
})
function niceStep(raw: number): number {
  const mag = 10 ** Math.floor(Math.log10(raw))
  const n = raw / mag
  return (n < 1.5 ? 1 : n < 3 ? 2 : n < 7 ? 5 : 10) * mag
}

const curve = computed(() =>
  Array.from({ length: 80 }, (_, i) => {
    const n = 1 + i
    return [n, Math.sqrt((2 * n * nj.value) / (n + nj.value)) * dist.value] as [number, number]
  }),
)
</script>

<template>
  <div class="wrap">
    <div class="left">
      <div class="formula">
        <Tex display formula='D(C_i, C_j) = \sqrt{\frac{2 n_i n_j}{n_i + n_j}}\; D(m_i, m_j), \qquad D^2 = 2\,\Delta J_w' />
      </div>
      <div class="controls">
        <Knob v-model="ni" :min="1" :max="80" :step="1" label="n<sub>i</sub>" :digits="0" :color="BLUE" />
        <Knob v-model="nj" :min="1" :max="80" :step="1" label="n<sub>j</sub>" :digits="0" :color="GREEN" />
        <Knob v-model="dist" :min="0.2" :max="6" label="D(m<sub>i</sub>, m<sub>j</sub>)" :color="GOLD" />
      </div>
      <Readout
        :items="[
          { label: 'size factor', value: factor.toFixed(2), color: RED },
          { label: 'Ward distance', value: D.toFixed(2), color: RED },
          { label: 'ΔJ<sub>w</sub>', value: deltaJ.toFixed(2) },
        ]"
      />
      <p class="note">Two singletons at distance d give exactly d, so the tree
        starts out in the units of the data. From there the factor grows: at
        n<sub>i</sub> = n<sub>j</sub> = n it is √n, so the same centre gap costs
        √n times more.</p>
      <p class="note">That is why Ward keeps clusters of similar size, and why
        it behaves like k-means read as a tree.</p>
    </div>
    <LineChart
      :series="[{ points: curve, color: RED, width: 2.4 }]"
      :dots="[{ x: ni, y: D, color: RED, r: 5 }]"
      :vlines="[{ x: ni, color: RED, dash: '' }]"
      :hlines="[{ y: dist, color: '#9aa0a6', dash: '4,4' }]"
      :labels="[{ x: 42, y: dist * 1.12, text: 'the raw centre gap', color: '#9aa0a6', size: 11 }]"
      :x-domain="[1, 80]" :y-domain="[0, yMax]"
      :x-ticks="[1, 20, 40, 60, 80]" :y-ticks="yTicks"
      x-label="n_i, with n_j fixed" y-label="Ward distance"
      title="the price of joining something big" :title-color="RED"
    />
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.05fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.left { display: flex; flex-direction: column; gap: 0.6rem; justify-content: center; }
.formula { font-size: 0.8rem; }
.controls { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem 1rem; }
</style>
