<!-- mixture_idea: the table of the 2023 lecture, and its bar chart. The
     slider sweeps a cut through the lengths: on each side, one bump. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMAL_COUNT, ANIMAL_LENGTH } from '../lib/gmm'
import { BLUE, GOLD, GRID, INK } from '../lib/theme'

const half = ANIMAL_LENGTH.length / 2
const rows = [0, 1].map((r) => ANIMAL_LENGTH.slice(r * half, (r + 1) * half).map((l, j) => ({ l, c: ANIMAL_COUNT[r * half + j] })))
const showPeaks = ref(true)
const barsData = computed(() => ANIMAL_LENGTH.map((l, i) => ({ x: l, y: ANIMAL_COUNT[i], w: 0.86, color: GRID, alpha: 0.75 })))
</script>

<template>
  <div class="wrap">
    <div class="note top">Lengths of small animals, collected in two regions</div>
    <div class="body">
      <div class="left">
        <table class="plain tab">
          <template v-for="(row, r) in rows" :key="r">
            <tr><th>length</th><td v-for="c in row" :key="c.l">{{ c.l }}</td></tr>
            <tr class="cnt"><th>count</th><td v-for="c in row" :key="c.l">{{ c.c }}</td></tr>
          </template>
        </table>
        <LineChart
          :series="[]" :bars="barsData"
          :labels="showPeaks ? [{ x: 86.3, y: 66, text: '▼', color: BLUE, size: 16, anchor: 'middle' }, { x: 92.3, y: 70, text: '▼', color: GOLD, size: 16, anchor: 'middle' }] : []"
          :x-domain="[81, 99]" :y-domain="[0, 75]" x-label="length (mm)" y-label="animals"
          :x-ticks="[82, 86, 90, 94, 98]" :y-ticks="[0, 20, 40, 60]" :unit-height="230"
        />
      </div>
      <div class="side">
        <div class="h">In the same sample:</div>
        <p>— Two peaks</p>
        <p>— No group label</p>
        <p class="note" style="margin-top: 1.5rem">Model the sample as a mixture of two populations</p>
        <Toggle v-model="showPeaks" label="mark the two peaks" :color="INK" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; min-height: 0; }
.left { display: grid; grid-template-rows: auto 1fr; gap: 0.6rem; min-height: 0; }
.tab { width: auto; font-size: 0.78rem; }
.tab th { padding-right: 0.8rem; border: none; }
.tab td { padding: 0.12rem 0.45rem; border: none; text-align: center; }
.tab tr.cnt td { border-bottom: 1px solid #eef0f2; }
.side { align-self: center; font-size: 0.95rem; }
</style>
