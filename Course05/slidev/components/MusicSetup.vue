<!-- setup_music: a power spectrogram, cut into frames. A frame (a column of
     X) is the sum of the notes sounding in it (columns of W), each scaled by
     how loud it is right then (the rows of H, read at that instant). -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { music } from '../lib/data5'
import { mat } from '../lib/mat'
import { BLUE, GOLD, GREEN, INK, PURPLE, RED } from '../lib/theme'

const { freqs, t, notes, env, X } = music
const colors = [BLUE, GREEN, RED]
const j = ref(48)
const xmax = Math.max(...X.a)
// the spectrogram on a log scale, as the printed figure draws it
const L = (() => { const m = mat(X.r, X.c); X.a.forEach((v, i) => { m.a[i] = Math.log1p((v / xmax) * 400) }); return m })()
const frame = computed(() => freqs.map((f, i) => [f, X.a[i * X.c + j.value]] as [number, number]))
const amounts = computed(() => env.map((e) => e[j.value]))
</script>

<template>
  <div class="wrap">
    <div class="note top">What the three matrices hold, for a recording</div>
    <div class="body">
      <div class="col">
        <MatView :M="L" ramp="x" flip :hi-col="j" title="X: the power spectrogram" :title-color="BLUE" />
        <div class="cap">time →, frequency ↑, cut into short frames</div>
      </div>
      <div class="col">
        <LineChart :series="[{ points: frame, color: BLUE, width: 2 }]" :x-domain="[0, 1]" :y-domain="[0, Math.max(...X.a) * 0.9]" x-label="frequency" :x-ticks="[]" :y-ticks="[]" title="x<sub>j</sub>: a column of X" :title-color="BLUE" />
        <div class="cap">the power in that one frame, at each frequency</div>
      </div>
      <div class="col">
        <LineChart
          :series="notes.map((nt, k) => ({ points: freqs.map((f, i) => [f, nt[i] * (0.25 + amounts[k]) + 1.6 * k]), color: colors[k], width: 1.8 }))"
          :x-domain="[0, 1]" :y-domain="[-0.1, 4.7]" x-label="frequency" :x-ticks="[]" :y-ticks="[]" title="w<sub>k</sub>: three notes" :title-color="PURPLE"
        />
        <div class="cap">one note: its pitch and its harmonics, the same at every frame (drawn thicker as it sounds louder)</div>
      </div>
      <div class="col">
        <LineChart
          :series="env.map((e, k) => ({ points: t.map((tt, i) => [tt, e[i] + 1.25 * k]), color: colors[k], width: 1.8 }))"
          :dots="amounts.map((a, k) => ({ x: t[j], y: a + 1.25 * k, color: colors[k], r: 4 }))"
          :vlines="[{ x: t[j], color: '#1b1b1b', dash: '3 3' }]"
          :x-domain="[0, 1]" :y-domain="[-0.1, 3.7]" x-label="time" :x-ticks="[]" :y-ticks="[]" title="rows of H: loudness in time" :title-color="GOLD"
        />
        <div class="cap">when each note is struck, and how loud it is at every frame</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="j" :min="0" :max="X.c - 1" :step="1" label="frame j" :digits="0" :color="INK" />
    </div>
    <div class="bottom">A frame is the sum of the notes sounding in it, each scaled by how loud it is right then.</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top, .bottom { text-align: center; }
.bottom { font-size: 0.9rem; }
.body { display: grid; grid-template-columns: 1.2fr 1fr 1fr 1.2fr; gap: 1.2rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; gap: 0.3rem; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.75rem; line-height: 1.35; }
</style>
