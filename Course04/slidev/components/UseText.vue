<!-- use_text: 1000 real newsgroup posts as TF-IDF vectors over 500 words,
     clustered with k-means. Each card lists the heaviest words of a centre,
     and which newsgroup most of its posts came from, which k-means never saw. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { kmeansSparse, news } from '../lib/real'
import { INK, clusterColor } from '../lib/theme'

const k = ref(4)
const cards = computed(() => {
  const { labels, mu } = kmeansSparse(k.value)
  const out = mu.map((m, c) => {
    const members = labels.map((l, i) => (l === c ? i : -1)).filter((i) => i >= 0)
    const counts = news.groups.map((_, g) => members.filter((i) => news.group[i] === g).length)
    const main = counts.indexOf(Math.max(...counts))
    const words = m.map((v, j) => [v, j]).sort((a, b) => b[0] - a[0]).slice(0, k.value > 4 ? 5 : 8).map(([, j]) => news.vocab[j])
    return { n: members.length, words, main, top: counts[main] }
  })
  // in the order of the newsgroup each card mostly holds, biggest first
  return out.sort((a, b) => a.main - b.main || b.n - a.n)
})
</script>

<template>
  <div class="wrap">
    <div class="head">1,000 newsgroup posts, each a TF-IDF vector over 500 words</div>
    <div class="cards" :style="{ gridTemplateColumns: `repeat(${Math.min(k, 4)}, 1fr)` }">
      <div v-for="(c, i) in cards" :key="i" class="card" :style="{ borderColor: clusterColor(i) }">
        <div class="title" :style="{ color: clusterColor(i) }">cluster {{ i + 1 }}, {{ c.n }} posts</div>
        <div class="words"><span v-for="w in c.words" :key="w">{{ w }}</span></div>
        <div class="from">{{ c.top }} of {{ c.n }} from {{ news.groups[c.main] }}</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="k" :min="2" :max="8" :step="1" label="K, clusters" :digits="0" :color="INK" />
      <span class="note">k-means never sees which newsgroup a post came from. Past K = 4, a topic splits in two.</span>
    </div>
    <div class="credit">data: 20 Newsgroups, headers and quotes removed</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.5rem; height: 100%; min-height: 0; }
.head { text-align: center; font-weight: 600; font-size: 0.82rem; }
.cards { display: grid; gap: 0.7rem; align-content: start; min-height: 0; }
.card { border: 1.6px solid; border-radius: 8px; padding: 0.45rem 0.8rem; text-align: center; display: flex; flex-direction: column; gap: 0.3rem; }
.title { font-weight: 700; font-size: 0.82rem; }
.words { display: flex; flex-direction: column; font-size: 0.9rem; line-height: 1.4; }
.from { color: #9aa0a6; font-size: 0.72rem; margin-top: auto; }
.controls { display: flex; gap: 1.4rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 12rem; }
.credit { text-align: right; color: #9aa0a6; font-size: 0.6rem; }
</style>
