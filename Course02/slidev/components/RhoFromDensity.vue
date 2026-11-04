<!-- rho_from_density: a noise model is a loss, ρ = −log f. Gaussian noise
     gives squares, Laplace gives absolute values, Student's t gives a loss
     whose tails flatten; ν moves Student from Cauchy (ν = 1) towards Gauss. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { BLUE, GREEN, MUTED, PURPLE } from '../lib/theme'

const nu = ref(2)
const fams = computed(() => {
  const v = nu.value
  return [
    { name: 'Gaussian noise', color: BLUE, f: (e: number) => Math.exp(-0.5 * e * e), rho: (e: number) => 0.5 * e * e, formula: 'ρ(e) = e²/2', label: 'least squares' },
    { name: 'Laplace noise', color: GREEN, f: (e: number) => Math.exp(-Math.abs(e)), rho: (e: number) => Math.abs(e), formula: 'ρ(e) = |e|', label: 'least absolute deviations' },
    { name: `Student noise, ν = ${v.toFixed(1)}`, color: PURPLE, f: (e: number) => (1 + (e * e) / v) ** (-(v + 1) / 2), rho: (e: number) => ((v + 1) / 2) * Math.log1p((e * e) / v), formula: 'ρ(e) = ((ν+1)/2) log(1 + e²/ν)', label: 'heavy tails allowed' },
  ]
})
</script>

<template>
  <div class="cmp">
    <div class="r3">
      <div v-for="f in fams" :key="f.color" class="fam">
        <LineChart :series="[{ points: curve(f.f, -4.5, 4.5), color: f.color }, { points: curve((e) => Math.exp(-0.5 * e * e), -4.5, 4.5), color: MUTED, width: 1, dash: '4,3' }]"
          :ribbons="[{ points: curve(f.f, -4.5, 4.5).map(([x, y]) => [x, 0, y]), color: f.color, alpha: 0.12 }]"
          :x-domain="[-4.5, 4.5]" :y-domain="[0, 1.15]" :x-ticks="[0]" :y-ticks="[]" :title="f.name" :title-color="f.color" :unit-height="200" />
        <div class="formula" :style="{ color: f.color }">{{ f.formula }}</div>
        <LineChart :series="[{ points: curve(f.rho, -4.5, 4.5), color: f.color, width: 2.6 }]" :x-domain="[-4.5, 4.5]" :y-domain="[-0.3, 6]" :x-ticks="[0]" :y-ticks="[]" x-label="e" :unit-height="220" />
        <div class="note">{{ f.label }}</div>
      </div>
    </div>
    <div class="foot">a noise model is a loss: ρ = −log f, up to a constant. Dashed: the Gaussian, for comparison.</div>
    <div class="controls">
      <Knob v-model="nu" :min="0.5" :max="30" :step="0.1" :digits="1" label="Student ν" :color="PURPLE" />
    </div>
  </div>
</template>

<style scoped>
.fam { display: grid; grid-template-rows: 1fr auto 1.1fr auto; min-height: 0; text-align: center; }
.formula { font-size: 0.85rem; margin-top: 0.3rem; }
</style>
