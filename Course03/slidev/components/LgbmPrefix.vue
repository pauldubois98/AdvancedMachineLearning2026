<!-- lgbm_prefix: why a histogram is enough. Both running totals, and the gain
     they feed; the cut on the slider is one column of the running rows. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { GAM, LAM, binFeature, gainOf, prefix, score, splitDemo } from '../lib/gbm'
import { BLUE, GREEN, INK, MUTED, PURPLE, RED } from '../lib/theme'

const cutBin = ref(4)
const N_BINS = 8
const demo = splitDemo()
const bins = binFeature(demo.X.map((r) => r[0]), demo.g, demo.h, N_BINS)
const pre = prefix(bins)

const at = computed(() => {
  const k = Math.round(cutBin.value)
  const GL = pre.cg[k]
  const HL = pre.ch[k]
  const GR = pre.G - GL
  const HR = pre.H - HL
  return {
    k, GL, HL, GR, HR,
    sL: score(GL, HL), sR: score(GR, HR), sN: score(pre.G, pre.H),
    gain: gainOf(GL, HL, GR, HR),
  }
})
</script>

<template>
  <div class="wrap">
    <table class="grid">
      <tbody>
        <tr class="head">
          <td class="lab">bin</td>
          <td v-for="(_, i) in bins.sumG" :key="i" :class="{ cut: i === at.k }">{{ i }}</td>
        </tr>
        <tr>
          <td class="lab">Σg</td>
          <td v-for="(v, i) in bins.sumG" :key="i" :class="{ cut: i === at.k }">{{ v.toFixed(1) }}</td>
        </tr>
        <tr>
          <td class="lab">Σh</td>
          <td v-for="(v, i) in bins.sumH" :key="i" :class="{ cut: i === at.k }">{{ v.toFixed(2) }}</td>
        </tr>
        <tr class="run">
          <td class="lab" :style="{ color: BLUE }">running Σg</td>
          <td v-for="(v, i) in pre.cg" :key="i" :class="{ on: i === at.k }" :style="{ color: BLUE }">{{ v.toFixed(1) }}</td>
        </tr>
        <tr class="run">
          <td class="lab" :style="{ color: PURPLE }">running Σh</td>
          <td v-for="(v, i) in pre.ch" :key="i" :class="{ on: i === at.k }" :style="{ color: PURPLE }">{{ v.toFixed(2) }}</td>
        </tr>
      </tbody>
    </table>
    <p class="split">
      cut after bin {{ at.k }}:
      <span :style="{ color: GREEN }">G<sub>L</sub> = {{ at.GL.toFixed(1) }}, H<sub>L</sub> = {{ at.HL.toFixed(2) }}</span>
      &nbsp;·&nbsp;
      <span :style="{ color: GREEN }">G<sub>R</sub> = G − G<sub>L</sub> = {{ at.GR.toFixed(1) }}, H<sub>R</sub> = {{ at.HR.toFixed(2) }}</span>
      &nbsp;·&nbsp;
      <span :style="{ color: MUTED }">whole node: G = {{ pre.G.toFixed(1) }}, H = {{ pre.H.toFixed(2) }} (the last cell of each running row)</span>
    </p>
    <p class="formula">
      gain = ½ [ s(G<sub>L</sub>,H<sub>L</sub>) + s(G<sub>R</sub>,H<sub>R</sub>) − s(G,H) ] − γ,
      &nbsp; s(G,H) = G²/(H+λ), &nbsp; λ = {{ LAM }}, γ = {{ GAM }}
    </p>
    <p class="numbers">
      = ½ [ {{ at.sL.toFixed(2) }} + {{ at.sR.toFixed(2) }} − {{ at.sN.toFixed(2) }} ] − {{ GAM }}
      = <b :style="{ color: at.gain > 0 ? GREEN : RED }">{{ at.gain.toFixed(2) }}</b>
    </p>
    <div class="knobs">
      <Knob v-model="cutBin" :min="0" :max="N_BINS - 2" :step="1" label="cut after bin" :digits="0" :color="GREEN" />
      <Readout :items="[{ label: 'candidates to try', value: `${N_BINS - 1}, one per bin edge`, color: GREEN }]" />
    </div>
    <p class="note">
      One sweep fills both running rows; after that every candidate split is a single
      subtraction, which is why the cost of the scan stops depending on the rows.
    </p>
  </div>
</template>

<style scoped>
.wrap { display: flex; flex-direction: column; justify-content: center; gap: 0.6rem; height: 100%; }
.grid { border-collapse: collapse; width: 100%; font-size: 0.82rem; font-variant-numeric: tabular-nums; }
.grid td { text-align: center; padding: 0.3rem 0.1rem; border: 1px solid #eef0f2; min-width: 3.4rem; }
.grid .lab { text-align: right; color: var(--muted); border: none; padding-right: 0.5rem; white-space: nowrap; }
.head td { color: var(--muted); font-size: 0.74rem; border: none; }
.grid td.cut { border-right: 2px solid var(--green); }
.grid td.on { outline: 2px solid var(--green); font-weight: 600; }
.split { font-size: 0.82rem; margin: 0; text-align: center; }
.formula { font-size: 0.86rem; margin: 0; text-align: center; }
.numbers { font-size: 0.95rem; margin: 0; text-align: center; font-variant-numeric: tabular-nums; }
.knobs { display: flex; gap: 2rem; align-items: center; justify-content: center; flex-wrap: wrap; }
.knobs > :first-child { min-width: 12rem; }
.note { font-size: 0.78rem; color: var(--muted); margin: 0; text-align: center; }
</style>
