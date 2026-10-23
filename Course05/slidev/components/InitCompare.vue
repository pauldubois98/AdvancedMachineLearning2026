<!-- init_compare: the loss of MU from each start, on 200 faces (the printed
     run, 64 x 64 pixels). Move the cursor along the passes and read off who
     is ahead, and by how many passes. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { initRace } from '../lib/data5'
import { BLUE, GOLD, GREEN, INK, PURPLE, RED } from '../lib/theme'
import { logTicks } from '../lib/ticks'

const t = ref(150)
const tr = initRace.traces
const randoms = Object.keys(tr).filter((k) => k.startsWith('random'))
const others = [
  { key: 'constant', name: 'constants', color: RED },
  { key: 'nndsvd', name: 'NNDSVD', color: GREEN },
  { key: 'cols', name: 'r columns of X', color: BLUE },
  { key: 'kmeans', name: 'k-means', color: PURPLE },
]
const N = tr.constant.length
const mean = Array.from({ length: N }, (_, i) => randoms.reduce((s, k) => s + tr[k][i], 0) / randoms.length)
const at = (k: string) => tr[k][Math.max(0, t.value - 1)]
// passes a random start needs to reach where this one starts
const head = (k: string) => { const i = mean.findIndex((m) => m <= tr[k][0]); return i < 0 ? N : i + 1 }
const all = [...randoms.map((k) => tr[k]), ...others.map((o) => tr[o.key])].flat()
const yd: [number, number] = [Math.min(...all) * 0.92, Math.max(...all) * 1.08]
const spread = computed(() => {
  const v = randoms.map((k) => at(k))
  return { lo: Math.min(...v), hi: Math.max(...v) }
})
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[...randoms.map((k) => ({ points: tr[k].map((v, i) => [i + 1, v]), color: GOLD, width: 1.3, opacity: 0.75 })), ...others.map((o) => ({ points: tr[o.key].map((v, i) => [i + 1, v]), color: o.color, width: 2.2 }))]"
        :vlines="[{ x: t, color: '#1b1b1b', dash: '4 3' }]"
        log-y :x-domain="[0, N]" :y-domain="yd" :y-ticks="logTicks(...yd)" x-label="pass" y-label="½‖X − WH‖²" :x-ticks="[0, 25, 50, 75, 100, 125, 150]"
        :title="`${initRace.faces} faces, r = ${initRace.r}`"
      />
      <div class="side">
        <div class="h">loss after {{ t }} passes</div>
        <table class="plain tab">
          <tbody>
            <tr><td :style="{ color: GOLD }">random, 5 starts</td><td class="num">{{ spread.lo.toFixed(0) }} to {{ spread.hi.toFixed(0) }}</td></tr>
            <tr v-for="o in others" :key="o.key">
              <td :style="{ color: o.color }">{{ o.name }}<br><span class="note">{{ o.key === 'constant' ? 'stuck: every column stays identical' : `starts ${head(o.key)} passes ahead of a random one` }}</span></td>
              <td class="num">{{ at(o.key).toFixed(0) }}</td>
            </tr>
          </tbody>
        </table>
        <p class="note">Different stationary points are found.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="t" :min="1" :max="N" :step="1" label="read at pass" :digits="0" :color="INK" />
    </div>
    <div class="credit">data: Olivetti faces, AT&amp;T Cambridge (64 × 64, the printed run)</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
.tab td { padding: 0.25rem 0.6rem 0.25rem 0; font-size: 0.8rem; }
.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
</style>
