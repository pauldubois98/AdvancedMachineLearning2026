<!-- use_anomaly: 1230 real connections to a web server, 30 of them attacks.
     k-means, then each connection is scored by its distance to the nearest
     centre; the farthest are flagged, and checked against the true labels. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { anomalyScores, http } from '../lib/real'
import { GOLD, INK, MUTED, RED, clusterColor } from '../lib/theme'

const k = ref(2)
const nFlag = ref(30)
const pts = http.X.map((p) => [p[1], p[2]])
const dom: [number, number, number, number] = [4.0, 12.0, 3.4, 12.0]

const res = computed(() => anomalyScores(k.value))
const flagged = computed(() => {
  const s = res.value.score
  return s.map((_, i) => i).sort((a, b) => s[b] - s[a]).slice(0, nFlag.value)
})
const hits = computed(() => flagged.value.filter((i) => http.attack[i]).length)
const nAttack = http.attack.filter(Boolean).length

const rings = computed(() =>
  flagged.value.map((i) => ({ x: pts[i][0], y: pts[i][1], r: 0.22, color: GOLD, alpha: 0 })),
)
const crosses = computed(() =>
  res.value.run.mu.map((m, c) => ({ x: m[1], y: m[2], color: res.value.big[c] ? clusterColor(c) : MUTED, size: 8 })),
)
const tags = computed(() => [
  ...pts.flatMap((p, i) => (http.attack[i] ? [{ x: p[0], y: p[1], text: '×', color: RED, size: 15 }] : [])),
  ...[[Math.log(100), '100 B'], [Math.log(1000), '1 kB'], [Math.log(1e4), '10 kB'], [Math.log(1e5), '100 kB']].flatMap(
    ([v, t]) => [
      { x: v as number, y: 3.6, text: t as string, color: MUTED, size: 11 },
      { x: 4.05, y: v as number, text: t as string, color: MUTED, size: 11, anchor: 'left' as CanvasTextAlign },
    ],
  ),
])
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot
        :X="pts" :labels="res.run.labels" :domain="dom" :point-size="2.2" :point-alpha="0.5"
        :circles="rings" :crosses="crosses" :tags="tags"
        title="1,230 connections to a web server: bytes sent by the client (→) and sent back (↑)"
      />
      <div class="side">
        <div class="h" :style="{ color: GOLD }">the score</div>
        <p>Distance to the nearest centre. The {{ nFlag }} farthest are ringed.</p>
        <div class="h" :style="{ color: RED }">the check</div>
        <p><b>{{ hits }}</b> of the {{ nFlag }} are real attacks (×), and {{ nAttack - hits }} of the {{ nAttack }} attacks are missed.</p>
        <p class="note">The attacks are a denial of service: huge requests that fit no group of users. Centres of clusters under 5% of the rows (grey) do not count, or a tight crowd of attacks would earn a centre of its own.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="k" :min="1" :max="6" :step="1" label="K, clusters" :digits="0" :color="INK" />
      <Knob v-model="nFlag" :min="5" :max="80" :step="5" label="flag the farthest" :digits="0" :color="GOLD" />
    </div>
    <div class="credit">data: KDD Cup 1999, http connections</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1.6fr 1fr; gap: 1.6rem; min-height: 0; }
.side { font-size: 0.85rem; display: flex; flex-direction: column; justify-content: center; }
.side .h { font-weight: 700; margin-top: 0.6rem; }
.side p { margin: 0.2rem 0; line-height: 1.45; }
.controls { display: flex; gap: 1.4rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 12rem; }
.credit { text-align: right; color: #9aa0a6; font-size: 0.6rem; }
</style>
