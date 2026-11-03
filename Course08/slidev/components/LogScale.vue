<!-- log_scale: the same budget of draws over the same range, uniform against
     log-uniform. A uniform draw almost never lands in the lower decades. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { sci } from '../lib/c08'
import { GREEN, INK, RED } from '../lib/theme'

const n = ref(40)
const lo = ref(-4)
const thr = ref(0.01)
const seed = ref(4)
const draws = computed(() => {
  const rng = new Rng(seed.value)
  const a = 10 ** lo.value
  return {
    lin: Array.from({ length: n.value }, () => a + (1 - a) * rng.next()),
    log: Array.from({ length: n.value }, () => 10 ** (lo.value * (1 - rng.next()))),
  }
})
const below = (v: number[]) => v.filter((x) => x < thr.value).length
const ticks = (v: number[]) => v.map((x) => ({ points: [[x, -0.5], [x, 0.5]] as [number, number][], width: 2.2 }))
const xd = computed(() => [10 ** lo.value * 0.6, 1.6] as [number, number])
const xt = computed(() => Array.from({ length: -lo.value + 1 }, (_, i) => 10 ** (lo.value + i)))
const range = computed(() => `[${sci(10 ** lo.value)}, 1]`)
</script>

<template>
  <div class="wrap">
    <div class="note top">Same range, same budget of {{ n }} draws</div>
    <div class="stack">
      <LineChart
        :series="ticks(draws.lin).map((s) => ({ ...s, color: RED }))" log-x :x-domain="xd" :y-domain="[-1, 1.6]"
        :x-ticks="xt" :y-ticks="[]" :vlines="[{ x: thr, color: INK }]"
        :labels="[{ x: xd[0] * 1.3, y: 1.05, text: `uniform on ${range}: ${below(draws.lin)} of ${n} draws below ${sci(thr)}`, color: RED, size: 15 }]"
        :pad="{ l: 14, r: 14, t: 6, b: 26 }" :unit-height="170"
      />
      <LineChart
        :series="ticks(draws.log).map((s) => ({ ...s, color: GREEN }))" log-x :x-domain="xd" :y-domain="[-1, 1.6]"
        :x-ticks="xt" :y-ticks="[]" :vlines="[{ x: thr, color: INK }]"
        :labels="[{ x: xd[0] * 1.3, y: 1.05, text: `log-uniform on ${range}: ${below(draws.log)} of ${n} draws below ${sci(thr)}`, color: GREEN, size: 15 }]"
        x-label="learning rate (log scale)" :pad="{ l: 14, r: 14, t: 6, b: 34 }" :unit-height="170"
      />
    </div>
    <div class="msg">Learning rates, <Tex formula="C" />, <Tex formula="\gamma" />, <Tex formula="\lambda" />: always log. Depths, counts, folds: linear integers.</div>
    <div class="controls">
      <Knob v-model="n" :min="5" :max="200" :step="1" :digits="0" label="draws" />
      <Knob v-model="lo" :min="-8" :max="-1" :step="1" :digits="0" label="lower end 10^" />
      <Knob v-model="thr" :min="1e-7" :max="0.5" log label="threshold" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" :digits="0" label="seed" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top, .msg { text-align: center; }
.stack { display: grid; grid-template-rows: 1fr 1fr; min-height: 0; }
.msg { font-size: 0.9rem; }
</style>
