<!-- app_topics: NMF of 1000 newsgroup posts, run live. Each card is a column
     of W read as its heaviest words; under it, which newsgroup the posts that
     lean on it mostly came from (NMF never saw that). -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { topics } from '../lib/data5'
import { col } from '../lib/mat'
import { type Fit, halsStep, init, order } from '../lib/nmf'
import { useRun } from '../lib/runner'
import { INK, clusterColor } from '../lib/theme'

const { X, vocab, groups, group } = topics
const r = ref(4)
const seed = ref(2)
const el = ref<HTMLElement | null>(null)
const PASSES = 60
const run = useRun<Fit>({
  el, key: () => [r.value, seed.value],
  make: () => init(X, r.value, 'random', seed.value),
  step: (f) => halsStep(X, f),
  passes: () => PASSES,
})
const cards = computed(() => {
  void run.tick.value
  const f = order(run.state.value)
  const n = X.c
  // each post goes to the topic it holds most of
  const hard = Array.from({ length: n }, (_, j) => {
    let b = 0
    for (let k = 1; k < r.value; k++) if (f.H.a[k * n + j] > f.H.a[b * n + j]) b = k
    return b
  })
  return Array.from({ length: r.value }, (_, k) => {
    const w = col(f.W, k)
    const words = Array.from(w, (v, i) => [v, i]).sort((a, b) => b[0] - a[0]).slice(0, r.value > 4 ? 5 : 8).map(([, i]) => vocab[i])
    const members = hard.map((h, j) => (h === k ? j : -1)).filter((j) => j >= 0)
    const counts = groups.map((_, g) => members.filter((j) => group[j] === g).length)
    const g = counts.indexOf(Math.max(...counts))
    return { words, n: members.length, top: counts[g], g }
  })
})
</script>

<template>
  <div ref="el" class="wrap">
    <div class="head">{{ X.c.toLocaleString('en') }} newsgroup posts × {{ X.r }} words (TF-IDF), NMF with r = {{ r }}</div>
    <div class="cards" :style="{ gridTemplateColumns: `repeat(${Math.min(r, 4)}, 1fr)` }">
      <div v-for="(c, k) in cards" :key="k" class="card" :style="{ borderColor: clusterColor(k) }">
        <div class="title" :style="{ color: clusterColor(k) }">topic {{ k + 1 }}</div>
        <div class="words"><span v-for="w in c.words" :key="w">{{ w }}</span></div>
        <div class="from">{{ c.top }} of {{ c.n }} posts<br>{{ groups[c.g] }}</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="r" :min="2" :max="8" :step="1" label="r, topics" :digits="0" :color="INK" />
      <Knob v-model="seed" :min="1" :max="20" :step="1" label="random start" :digits="0" :color="INK" />
      <span class="note">{{ run.pass.value < PASSES ? `pass ${run.pass.value}` : 'converged' }}. A column of W is a topic: the words it is made of. A column of H is how much of each topic one post holds.</span>
    </div>
    <div class="credit">data: 20 Newsgroups, headers and quotes removed</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.5rem; height: 100%; min-height: 0; }
.head { text-align: center; font-size: 0.95rem; }
.cards { display: grid; gap: 0.6rem; align-content: start; min-height: 0; overflow: hidden; }
.card { border: 1.6px solid; border-radius: 8px; padding: 0.4rem 0.7rem; display: flex; flex-direction: column; gap: 0.25rem; text-align: center; }
.title { font-weight: 700; font-size: 0.9rem; }
.words { display: flex; flex-direction: column; font-size: 0.85rem; line-height: 1.28; }
.from { color: #9aa0a6; font-size: 0.7rem; margin-top: auto; line-height: 1.3; }
</style>
