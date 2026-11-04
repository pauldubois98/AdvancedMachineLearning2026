// A live t-SNE (or SNE) run: the optimisation goes on a few iterations per
// animation frame, so the map visibly forms, and starts again whenever its
// inputs change. Only the slide on screen computes: Slidev keeps its
// neighbours mounted, and five live runs at once would starve each other.
import { onBeforeUnmount, ref, shallowRef, watch, type WatchSource } from 'vue'
import { useIsSlideActive } from '@slidev/client'
import { Embedding } from './sne'

export function useLiveRun(make: () => Embedding | null, deps: WatchSource[], iters = 1000, budget = 28) {
  const pts = shallowRef<number[][]>([])
  const it = ref(0)
  const kl = ref(0)
  const running = ref(false)
  const active = useIsSlideActive()
  let e: Embedding | null = null
  let raf = 0
  let token = 0
  let stale = true // inputs changed since the last start

  function frame(my: number) {
    if (my !== token || !e) return
    if (!active.value) { running.value = false; return } // paused, resumed by the watch below
    const t0 = performance.now()
    while (e.it < iters && performance.now() - t0 < budget) e.step()
    pts.value = e.points()
    it.value = e.it
    kl.value = e.kl
    if (e.it < iters) raf = requestAnimationFrame(() => frame(my))
    else running.value = false
  }
  function go() {
    cancelAnimationFrame(raf)
    const my = ++token
    running.value = true
    raf = requestAnimationFrame(() => frame(my))
  }
  function restart() {
    if (!active.value) { stale = true; return }
    stale = false
    e = make()
    if (!e) return
    pts.value = e.points()
    it.value = 0
    kl.value = e.kl
    go()
  }
  let timer: ReturnType<typeof setTimeout> | undefined
  watch(deps, () => { clearTimeout(timer); timer = setTimeout(restart, 120) })
  watch(active, (on) => {
    if (!on) return
    if (stale || !e) restart()
    else if (e.it < iters) go()
  }, { immediate: true })
  onBeforeUnmount(() => { token++; cancelAnimationFrame(raf); clearTimeout(timer) })
  return { pts, it, kl, running, restart }
}
