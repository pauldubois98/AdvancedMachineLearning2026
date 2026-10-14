<!-- xor_example: XOR has no line in (x1, x2). Morph into the first two
     coordinates of Φ and one horizontal line is enough. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { xor } from '../lib/data'
import { GREEN, INK, MUTED } from '../lib/theme'

const t = ref(0)
const data = xor()
const SQ2 = Math.SQRT2

/** (x1, x2) at t = 0, (√2·x1, √2·x1x2) at t = 1 */
const points = computed(() =>
  data.X.map(([a, b]) => [
    a * (1 - t.value) + SQ2 * a * t.value,
    b * (1 - t.value) + SQ2 * a * b * t.value,
  ]),
)
const separated = computed(() => t.value > 0.5)
</script>

<template>
  <div class="wrap">
    <FieldPlot
      :X="points" :y="data.y" :domain="[-2.5, 2.5, -2.5, 2.5]" :point-size="110"
      :lines="separated
        ? [{ a: 0, c: 0, color: INK, width: 2.4 }]
        : [{ a: 0, c: 0, color: '#cccfd2', width: 1 }, { a: 1e6, c: 0, color: '#cccfd2', width: 1 }]"
    />
    <div class="side">
      <p class="eq">Φ(x) = (√2·x₁, √2·x₁x₂, 1, √2·x₂, x₁², x₂²)</p>
      <p class="map" :style="{ color: GREEN }">ℝ² → ℝ⁶</p>
      <Knob v-model="t" :min="0" :max="1" :step="0.01" label="morph into Φ-space" :digits="2" :color="GREEN" />
      <p class="state">
        <template v-if="t < 0.02">
          <strong>the XOR classes</strong>: no line separates them in (x₁, x₂)
        </template>
        <template v-else-if="t > 0.98">
          <strong :style="{ color: GREEN }">in the (Φ₁, Φ₂) plane</strong>: separable,
          by one horizontal line
        </template>
        <template v-else>moving the points to (Φ₁, Φ₂) = (√2·x₁, √2·x₁x₂)…</template>
      </p>
      <p class="note">
        The SVM never computes Φ: the dual only ever asks for ⟨Φ(x), Φ(x′)⟩,
        which here is (1 + x<sup>T</sup>x′)², a polynomial kernel.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; align-items: center; }
.side { display: flex; flex-direction: column; gap: 0.55rem; }
.eq { font-size: 0.95rem; margin: 0; }
.map { font-size: 1.3rem; margin: 0; font-weight: 600; }
.state { font-size: 0.85rem; margin: 0; }
.note { font-size: 0.78rem; color: v-bind(MUTED); margin: 0; line-height: 1.45; }
</style>
