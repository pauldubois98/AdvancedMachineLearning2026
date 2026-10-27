<!-- covariance_shapes: four families, from rigid to free. Pick a family; the
     sliders only move what that family lets move. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Cov, Pt } from '../lib/gmm'
import { COMP, BLUE, GOLD, GREEN, PURPLE, INK } from '../lib/theme'

const fam = ref('full')
const FAMS = [
  { value: 'spherical', label: 'spherical', color: BLUE },
  { value: 'diag', label: 'diagonal', color: GOLD },
  { value: 'tied', label: 'tied', color: GREEN },
  { value: 'full', label: 'full', color: PURPLE },
]
const k = ref(0)
// one free shape per component, and one shared shape for the tied family:
// the family decides what survives of them
const sx = ref([0.75, 0.55, 0.72])
const sy = ref([0.5, 0.65, 0.35])
const rho = ref([0.75, -0.6, 0.1])
const tied = ref({ sx: 0.68, sy: 0.51, rho: 0.75 })
const centres: Pt[] = [[-0.85, 0.55], [0.85, 0.5], [0.05, -0.8]]
/** the values the family actually uses for component j */
function eff(j: number) {
  if (fam.value === 'tied') return { ...tied.value }
  const x = sx.value[j]
  if (fam.value === 'spherical') return { sx: x, sy: x, rho: 0 }
  if (fam.value === 'diag') return { sx: x, sy: sy.value[j], rho: 0 }
  return { sx: x, sy: sy.value[j], rho: rho.value[j] }
}
const S = computed<Cov[]>(() => [0, 1, 2].map((j) => {
  const e = eff(j)
  return [e.sx ** 2, e.rho * e.sx * e.sy, e.sy ** 2]
}))
const info = computed(() => ({
  spherical: { form: 'Σₖ = σₖ² I', cost: 'K' },
  diag: { form: 'Σₖ = diag(σₖ₁², …, σₖd²)', cost: 'K d' },
  tied: { form: 'Σₖ = Σ for all k', cost: 'd(d+1)/2' },
  full: { form: 'Σₖ free', cost: 'K d(d+1)/2' },
} as Record<string, { form: string; cost: string }>)[fam.value])
const free = computed(() => ({ sy: fam.value !== 'spherical', rho: fam.value === 'full' || fam.value === 'tied' }))
const cur = computed(() => eff(k.value))
function set(key: 'sx' | 'sy' | 'rho', v: number) {
  if (fam.value === 'tied') { tied.value = { ...tied.value, [key]: v }; return }
  const arr = key === 'sx' ? sx : key === 'sy' ? sy : rho
  const c = [...arr.value]; c[k.value] = v; arr.value = c
}
const famColor = computed(() => FAMS.find((f) => f.value === fam.value)!.color)
const editColor = computed(() => (fam.value === 'tied' ? INK : COMP[k.value]))
</script>

<template>
  <div class="wrap">
    <div class="note top">Four families of covariance, from rigid to free</div>
    <div class="body">
      <Plane
        :domain="[-2.6, 2.6, -2.5, 2.2]"
        :ellipses="S.map((s, j) => ({ mu: centres[j], S: s, color: COMP[j], width: j === k && fam !== 'tied' ? 2.4 : 1.5 }))"
        :markers="centres.map((c, j) => ({ at: c, color: COMP[j], size: 4 }))"
      />
      <div class="side">
        <div class="h" :style="{ color: famColor, fontSize: '1.1rem' }">{{ FAMS.find((f) => f.value === fam)!.label }}</div>
        <p style="font-size: 1rem">{{ info.form }}</p>
        <p class="note">{{ info.cost }} numbers for the spreads</p>
        <p class="note" style="margin-top: 1rem">Fewer parameters give a stabler fit on little data; more give shapes that follow the data.</p>
      </div>
    </div>
    <div class="controls">
      <Choice v-model="fam" :options="FAMS" label="family" />
      <Choice v-if="fam !== 'tied'" v-model="k" :options="[0, 1, 2].map((j) => ({ value: j as any, label: `comp. ${j + 1}`, color: COMP[j] }))" label="edit" />
      <span v-else class="note">one shape, shared by all three</span>
      <Knob :model-value="cur.sx" @update:model-value="(v: number) => set('sx', v)" :min="0.2" :max="1.2" :step="0.01" :label="fam === 'spherical' ? 'σ' : 'σ<sub>x</sub>'" :color="editColor" />
      <Knob :model-value="cur.sy" @update:model-value="(v: number) => set('sy', v)" :min="0.2" :max="1.2" :step="0.01" label="σ<sub>y</sub>" :color="editColor" :disabled="!free.sy" />
      <Knob :model-value="cur.rho" @update:model-value="(v: number) => set('rho', v)" :min="-0.95" :max="0.95" :step="0.01" label="correlation" :color="editColor" :disabled="!free.rho" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
.controls { gap: 0.9rem 1.2rem; }
.controls > .knob { min-width: 9rem; }
</style>
