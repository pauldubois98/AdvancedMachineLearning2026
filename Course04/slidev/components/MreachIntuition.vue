<!-- mreach_intuition: why the maximum. A thin path of stray points can bridge
     two blobs under d, but not under d_mreach. The slider adds stray points. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { bridgeData, distances } from '../lib/data4'
import { coreDistances, mutualReachability, mstToLinkage, primMst } from '../lib/density'
import { fclusterDist } from '../lib/hier'
import { BLUE, GREEN, MUTED, PURPLE, RED } from '../lib/theme'

const nBridge = ref(5)
const k = ref(4)
const t = ref(0.6)
const data = computed(() => bridgeData(Math.round(nBridge.value), 5, 0.3))
const D = computed(() => distances(data.value.X))
const core = computed(() => coreDistances(data.value.X, k.value, D.value))
const mr = computed(() => mutualReachability(data.value.X, k.value, D.value).mr)

/** Everything within `t` of each other, joined up: single linkage read at one
 *  threshold, which is what DBSCAN does. Groups of fewer than five points are
 *  drawn as noise rather than as clusters. */
function groupsAt(Dm: Float64Array[], thr: number): number[] {
  const raw = fclusterDist(mstToLinkage(primMst(Dm), data.value.X.length), thr)
  const counts = new Map<number, number>()
  raw.forEach((l) => counts.set(l, (counts.get(l) ?? 0) + 1))
  const keep = [...counts.entries()].filter(([, c]) => c >= 5).map(([l]) => l)
  const rank = new Map(keep.map((l, i) => [l, i]))
  return raw.map((l) => rank.get(l) ?? -1)
}
const plain = computed(() => groupsAt(D.value, t.value))
const trans = computed(() => groupsAt(mr.value, t.value))
const sizes = (labels: number[]) =>
  [...new Set(labels)].filter((l) => l >= 0)
    .map((l) => labels.filter((v) => v === l).length).sort((a, b) => b - a)
const bridged = (labels: number[]) => sizes(labels).length < 2
const colors = computed(() =>
  data.value.X.map((_, i) => (data.value.bridge.includes(i) ? RED : MUTED)),
)
const circles = computed(() =>
  data.value.bridge.map((i) => ({
    x: data.value.X[i][0], y: data.value.X[i][1], r: core.value[i],
    color: RED, alpha: 0.06, dash: [4, 3],
  })),
)
const dom: [number, number, number, number] = [-3.0, 3.0, -1.6, 1.6]
</script>

<template>
  <div class="wrap">
    <div class="left">
      <ClusterPlot
        :X="data.X" :colors="colors" :point-size="2.8" :domain="dom" :circles="circles"
        :edges="data.bridge.slice(0, -1).map((i, t) => ({ a: data.X[i] as [number, number], b: data.X[data.bridge[t + 1]] as [number, number], color: RED, width: 1.4 }))"
        title="the stray path, with its core circles" :title-color="RED"
      />
      <div class="panels">
        <ClusterPlot
          :X="data.X" :labels="plain" :point-size="2.4" :domain="dom"
          :title="`under d: ${bridged(plain) ? 'one cluster, bridged' : sizes(plain).length + ' clusters'}`"
          :title-color="bridged(plain) ? RED : GREEN"
        />
        <ClusterPlot
          :X="data.X" :labels="trans" :point-size="2.4" :domain="dom"
          :title="`under d<sub>mreach</sub>: ${bridged(trans) ? 'one cluster, bridged' : sizes(trans).length + ' clusters'}`"
          :title-color="bridged(trans) ? RED : GREEN"
        />
      </div>
    </div>
    <div class="right">
      <p><em class="hl-green">it puts a floor under every point</em><br />
        <span class="note">nothing can be nearer to x<sub>i</sub> than
        core<sub>k</sub>(x<sub>i</sub>), so a point in an empty region is far
        from everything, including the next stray point</span></p>
      <p><em class="hl-blue">it never shrinks a distance</em><br />
        <span class="note">dense pairs keep the distance they had; only the
        sparse ones move</span></p>
      <p><em style="color:#6b46c1;font-style:normal">it stays symmetric</em><br />
        <span class="note">it is the max of a symmetric list</span></p>
      <div class="controls">
        <Knob v-model="nBridge" :min="2" :max="24" :step="1" label="stray points in the path" :digits="0" :color="RED" />
        <Knob v-model="k" :min="2" :max="10" :step="1" label="k" :digits="0" :color="BLUE" />
        <Knob v-model="t" :min="0.15" :max="1.2" label="join everything closer than" :color="GREEN" />
      </div>
      <Readout
        :items="[
          { label: 'cluster sizes under d', value: sizes(plain).slice(0, 3).join(' / ') || 'none', color: RED },
          { label: 'under d<sub>mreach</sub>', value: sizes(trans).slice(0, 3).join(' / ') || 'none', color: GREEN },
          { label: 'core of a stray point', value: core[data.bridge[Math.floor(data.bridge.length / 2)]].toFixed(2), color: RED },
        ]"
      />
      <p class="note">At this threshold the strays are close enough to pass
        the join along under d, so the two blobs come out as one cluster. Under
        d<sub>mreach</sub> each stray sits at least its own core distance away
        from anything, so the chain never forms. Add enough strays and even
        d<sub>mreach</sub> gives in: a path dense enough to be a cluster of its
        own is no longer noise.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; }
.left { display: grid; grid-template-rows: 1.15fr 1fr; gap: 0.4rem; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.4rem; justify-content: center; font-size: 0.86rem; }
.right p { margin: 0; line-height: 1.45; }
.controls { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem 1rem; margin-top: 0.3rem; }
</style>
