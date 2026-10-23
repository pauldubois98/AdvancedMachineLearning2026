<!-- setup_topics: a post is a column of word weights; a topic (a column of W)
     is a list of words that go together; the post's column of H is its mix of
     topics. The NMF (r = 4) runs once when the slide is first shown. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { topics } from '../lib/data5'
import { col, row } from '../lib/mat'
import { type Fit, halsStep, init, order } from '../lib/nmf'
import { useRun } from '../lib/runner'
import { BLUE, GOLD, INK, PURPLE } from '../lib/theme'

const { X, vocab } = topics
const j = ref(3)
const k = ref(0)
const el = ref<HTMLElement | null>(null)
const PASSES = 60
const run = useRun<Fit>({ el, key: () => 0, make: () => init(X, 4, 'random', 2), step: (f) => halsStep(X, f), passes: () => PASSES })
const fitted = computed(() => { void run.tick.value; return order(run.state.value) })
function top(v: ArrayLike<number>, m: number) {
  return Array.from(v, (x, i) => [x, i]).sort((a, b) => b[0] - a[0]).slice(0, m).filter(([x]) => x > 0)
}
const post = computed(() => top(col(X, j.value), 7))
const topic = computed(() => top(col(fitted.value.W, k.value), 7))
const mix = computed(() => Array.from({ length: 4 }, (_, c) => row(fitted.value.H, c)[j.value]))
const bars = (items: number[][], color: string) => items.map(([v], i) => ({ x: items.length - i, y: v, y0: 0, w: 0.62, color }))
const words = (items: number[][]) => items.map(([, w], i) => ({ x: items.length - i, text: vocab[w] }))
</script>

<template>
  <div ref="el" class="wrap">
    <div class="note top">What the three matrices hold, for a pile of text</div>
    <div class="cols">
      <div class="col">
        <div class="h" :style="{ color: BLUE }">a column of X: one post</div>
        <HBars :items="post.map(([v, w]) => ({ label: vocab[w], value: v }))" :color="BLUE" />
        <div class="cap">one weight for each of the {{ vocab.length }} words in the vocabulary, and zero for every word absent</div>
        <div class="foot" :style="{ color: BLUE }">X is {{ X.r }} × {{ X.c }}: one column per post</div>
      </div>
      <div class="col">
        <div class="h" :style="{ color: PURPLE }">a column of W: topic {{ k + 1 }}</div>
        <HBars :items="topic.map(([v, w]) => ({ label: vocab[w], value: v }))" :color="PURPLE" />
        <div class="cap">one weight per word again: which words go together. This is what we are looking for.</div>
        <div class="foot" :style="{ color: PURPLE }">W is {{ X.r }} × r: one column per topic</div>
      </div>
      <div class="col">
        <div class="h" :style="{ color: GOLD }">a column of H: the mix</div>
        <LineChart
          :series="[]"
          :bars="mix.map((v, c) => ({ x: c + 1, y: v, y0: 0, w: 0.62, color: GOLD, alpha: c === k ? 1 : 0.5 }))"
          :labels="mix.map((v, c) => ({ x: c + 1, y: -Math.max(...mix, 1e-9) * 0.07, text: `topic ${c + 1}`, color: '#1b1b1b', size: 12 }))"
          :hlines="[{ y: 0, color: '#1b1b1b' }]"
          :x-domain="[0.4, 4.6]" :y-domain="[-Math.max(...mix, 1e-9) * 0.14, Math.max(...mix, 1e-9) * 1.1]" :axes="false"
        />
        <div class="cap">how much of each topic this one post is made of: r numbers, none of them negative</div>
        <div class="foot" :style="{ color: GOLD }">H is r × {{ X.c }}: one column per post</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="j" :min="0" :max="X.c - 1" :step="1" label="post j" :digits="0" :color="BLUE" />
      <Knob v-model="k" :min="0" :max="3" :step="1" label="topic k" :digits="0" :color="PURPLE" />
      <span class="note">{{ run.pass.value < PASSES ? `fitting, pass ${run.pass.value}…` : 'NMF with r = 4' }}</span>
    </div>
    <div class="credit">data: 20 Newsgroups, headers and quotes removed; TF-IDF</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.cols { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.6rem; min-height: 0; }
.col { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.3rem; min-height: 0; border-left: 1px solid #e3e5e8; padding-left: 1rem; }
.col:first-child { border-left: none; padding-left: 0; }
.h { text-align: center; font-weight: 600; font-size: 0.9rem; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.75rem; line-height: 1.35; }
.foot { text-align: center; font-size: 0.8rem; }
</style>
