<!-- stability_example: one cluster of six points, one term per point. Move the
     moments at which points leave and watch the sum. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const lamBirth = ref(0.8)
const lamDeath = ref(2.6)
const leaves = ref([1.2, 1.5, 2.0])

const clipped = computed(() => leaves.value.map((l) => Math.min(Math.max(l, lamBirth.value), lamDeath.value)))
const early = computed(() => clipped.value.map((l) => l - lamBirth.value))
const stay = computed(() => 3 * (lamDeath.value - lamBirth.value))
const total = computed(() => early.value.reduce((s, v) => s + v, 0) + stay.value)
const lamMax = 3.0
const widths = [6, 5, 4, 3]
const edges = computed(() => [lamBirth.value, ...clipped.value, lamDeath.value])
const Y = (l: number) => 14 + ((l - 0.3) / (lamMax - 0.3)) * 252
</script>

<template>
  <div class="wrap">
    <div class="chart">
      <svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid meet">
        <line x1="44" x2="44" y1="14" y2="266" stroke="#1b1b1b" stroke-width="1.1" />
        <template v-for="t in [0.5, 1, 1.5, 2, 2.5, 3]" :key="t">
          <line :x1="40" :x2="44" :y1="Y(t)" :y2="Y(t)" stroke="#1b1b1b" />
          <text :x="37" :y="Y(t) + 4" class="tick">{{ t.toFixed(1) }}</text>
        </template>
        <rect
          v-for="(w, i) in widths" :key="`r${i}`"
          :x="190 - w * 13" :y="Y(edges[i])" :width="w * 26"
          :height="Math.max(0, Y(edges[i + 1]) - Y(edges[i]))"
          :style="{ fill: BLUE, fillOpacity: 0.3 }"
        />
        <template v-for="(l, i) in clipped" :key="`l${i}`">
          <line :x1="190 - widths[i] * 13" :x2="190 + widths[i] * 13" :y1="Y(l)" :y2="Y(l)" :stroke="RED" stroke-width="1.2" />
          <circle :cx="190 + widths[i] * 13 + 7" :cy="Y(l)" r="4" :fill="RED" />
          <text :x="190 + widths[i] * 13 + 14" :y="Y(l) + 4" :style="{ fill: RED, fontSize: '10.5px' }">
            x{{ i + 1 }} leaves at λ = {{ l.toFixed(2) }}
          </text>
        </template>
        <line :x1="44" :x2="390" :y1="Y(lamBirth)" :y2="Y(lamBirth)" :stroke="MUTED" stroke-width="1.2" stroke-dasharray="5,4" />
        <line :x1="44" :x2="390" :y1="Y(lamDeath)" :y2="Y(lamDeath)" :stroke="GREEN" stroke-width="1.2" stroke-dasharray="5,4" />
        <text :x="48" :y="Y(lamBirth) - 5" :style="{ fill: MUTED, fontSize: '10.5px' }">λ_birth = {{ lamBirth.toFixed(2) }}</text>
        <text :x="48" :y="Y(lamDeath) - 5" :style="{ fill: GREEN, fontSize: '10.5px' }">the cluster splits: the last 3 leave here</text>
        <text x="12" y="150" class="axis" transform="rotate(-90 12 150)">λ = 1/ε</text>
      </svg>
    </div>
    <div class="right">
      <div class="head" :style="{ color: BLUE }">one term per point</div>
      <table class="plain">
        <tr v-for="(l, i) in clipped" :key="i">
          <td>x<sub>{{ i + 1 }}</sub></td>
          <td class="note">{{ l.toFixed(2) }} − {{ lamBirth.toFixed(2) }}</td>
          <td :style="{ color: RED, fontWeight: 600 }">{{ early[i].toFixed(2) }}</td>
        </tr>
        <tr>
          <td>x<sub>4</sub>, x<sub>5</sub>, x<sub>6</sub></td>
          <td class="note">3 × ({{ lamDeath.toFixed(2) }} − {{ lamBirth.toFixed(2) }})</td>
          <td :style="{ color: GREEN, fontWeight: 600 }">{{ stay.toFixed(2) }}</td>
        </tr>
        <tr>
          <td><strong>stability</strong></td>
          <td />
          <td :style="{ fontWeight: 600, fontSize: '1.05rem' }">{{ total.toFixed(2) }}</td>
        </tr>
      </table>
      <div class="controls">
        <Knob v-model="lamBirth" :min="0.4" :max="1.6" label="λ<sub>birth</sub>" :color="MUTED" />
        <Knob v-model="lamDeath" :min="1.2" :max="3" label="λ<sub>death</sub>" :color="GREEN" />
        <Knob v-model="leaves[0]" :min="0.5" :max="3" label="x₁ leaves" :color="RED" />
        <Knob v-model="leaves[1]" :min="0.5" :max="3" label="x₂ leaves" :color="RED" />
        <Knob v-model="leaves[2]" :min="0.5" :max="3" label="x₃ leaves" :color="RED" />
      </div>
      <p class="note">A point that leaves early contributes almost nothing; the
        ones that stay to the end contribute the most. Push λ<sub>birth</sub> up
        towards the leaves and the whole stability collapses, which is why a
        cluster born late has to hold its points to be kept.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.chart { min-height: 0; }
svg { width: 100%; height: 100%; }
.tick { font-size: 11px; fill: #1b1b1b; text-anchor: end; }
.axis { font-size: 12px; fill: #1b1b1b; text-anchor: middle; }
.right { display: flex; flex-direction: column; gap: 0.45rem; justify-content: center; }
.head { font-size: 0.88rem; font-weight: 600; }
.controls { display: grid; grid-template-columns: 1fr 1fr; gap: 0.3rem 1rem; }
</style>
