<!-- mreach_effect: the new distance against the old one, pair by pair. Nothing
     sits below the diagonal, and k decides how much of the cloud lifts off it. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { densityData, distances } from '../lib/data4'
import { mutualReachability } from '../lib/density'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const k = ref(5)
const X = densityData(7, 45, 30, 14)
const D = distances(X)
const mr = computed(() => mutualReachability(X, k.value, D).mr)
const pairs = computed(() => {
  const out: [number, number][] = []
  for (let i = 0; i < X.length; i++) {
    for (let j = i + 1; j < X.length; j++) out.push([D[i][j], mr.value[i][j]])
  }
  return out
})
/** The window that matters: a pair is only ever inflated up to a core
 *  distance, so beyond twice the largest one every pair sits on the diagonal. */
const core = computed(() => mutualReachability(X, k.value, D).core)
const lim = computed(() => Math.min(
  Math.max(...pairs.value.map((p) => p[0])) * 1.02,
  2.1 * Math.max(...core.value),
))
const shown = computed(() => pairs.value.filter((p) => p[0] <= lim.value && p[1] <= lim.value))
const unchanged = computed(() => pairs.value.filter((p) => p[1] - p[0] < 1e-12).length)
const inflated = computed(() => pairs.value.length - unchanged.value)
const worst = computed(() => Math.max(...pairs.value.map((p) => p[1] - p[0])))
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="shown.map((p) => [p[0], p[1]])" :point-size="1.6" :point-alpha="0.3"
      :colors="shown.map((p) => (p[1] - p[0] < 1e-12 ? GREEN : BLUE))"
      :domain="[-0.04 * lim, lim, -0.04 * lim, lim]" :aspect="'auto'"
      :edges="[
        { a: [0, 0], b: [lim, lim], color: MUTED, width: 1.4, dash: [6, 4] },
        { a: [0, 0], b: [lim, 0], color: '#1b1b1b', width: 1.1 },
        { a: [0, 0], b: [0, lim], color: '#1b1b1b', width: 1.1 },
      ]"
      :tags="[
        { x: lim * 0.74, y: lim * 0.66, text: 'd_mreach = d', color: MUTED, size: 11.5 },
        { x: lim * 0.5, y: -0.022 * lim, text: 'd (x_i, x_j)', color: '#1b1b1b', size: 12 },
        { x: 0.02 * lim, y: lim * 0.96, text: 'd_mreach', color: '#1b1b1b', size: 12, anchor: 'left' as CanvasTextAlign },
      ]"
      title="the new distance is never smaller than the old one" :title-color="BLUE"
    />
    <div class="right">
      <Knob v-model="k" :min="1" :max="20" :step="1" label="k" :digits="0" :color="BLUE" />
      <Readout
        :items="[
          { label: 'pairs', value: String(pairs.length) },
          { label: 'unchanged', value: `${unchanged} (${((unchanged / pairs.length) * 100).toFixed(0)}%)`, color: GREEN },
          { label: 'inflated', value: `${inflated}`, color: RED },
          { label: 'largest inflation', value: worst.toFixed(2), color: RED },
          { label: 'window shown', value: `d up to ${lim.toFixed(1)}; beyond it every pair is on the diagonal` },
        ]"
      />
      <p class="note">Green pairs are both in dense regions: they keep the
        distance they had, so the geography of the clusters is untouched.</p>
      <p class="note">Blue pairs involve at least one point whose core distance
        is larger than the gap, so they are pushed up to that core distance.
        Raising k lifts more and more of the cloud off the diagonal, until
        even the clusters start to be inflated.</p>
      <p class="note">Islands and sea: the sea is widened, the land does not
        move.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; }
</style>
