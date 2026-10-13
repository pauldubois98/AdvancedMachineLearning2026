// Canvas drawing shared by the interactive figures: the shaded decision
// field, its contours (f = -1, 0, +1) and the class markers.
import { INK, GREEN, RED, BLUE, rdbuR, rgb } from './theme'

export type Domain = [number, number, number, number] // x0, x1, y0, y1

export function dataDomain(X: number[][], pad = 0.7): Domain {
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity
  for (const p of X) {
    x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0])
    y0 = Math.min(y0, p[1]); y1 = Math.max(y1, p[1])
  }
  const px = pad * 1
  return [x0 - px, x1 + px, y0 - px, y1 + px]
}

/** Keep the data aspect square inside a w x h pixel box, as matplotlib's
 *  set_aspect("equal") does: widen the shorter data axis. */
export function equalise(d: Domain, w: number, h: number): Domain {
  const [x0, x1, y0, y1] = d
  const dx = x1 - x0
  const dy = y1 - y0
  const want = w / h
  const have = dx / dy
  if (have < want) {
    const extra = (dy * want - dx) / 2
    return [x0 - extra, x1 + extra, y0, y1]
  }
  const extra = (dx / want - dy) / 2
  return [x0, x1, y0 - extra, y1 + extra]
}

export interface Frame {
  ctx: CanvasRenderingContext2D
  w: number
  h: number
  d: Domain
  sx(v: number): number
  sy(v: number): number
}

/** Set up a canvas for the device pixel ratio and return pixel mappers. */
export function frame(canvas: HTMLCanvasElement, d: Domain): Frame {
  const dpr = window.devicePixelRatio || 1
  const w = canvas.clientWidth
  const h = canvas.clientHeight
  if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
    canvas.width = Math.round(w * dpr)
    canvas.height = Math.round(h * dpr)
  }
  const ctx = canvas.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.clearRect(0, 0, w, h)
  const [x0, x1, y0, y1] = d
  return {
    ctx, w, h, d,
    sx: (v) => ((v - x0) / (x1 - x0)) * w,
    sy: (v) => h - ((v - y0) / (y1 - y0)) * h,
  }
}

/** Evaluate f on a res x res grid over the frame's domain. */
export function sampleField(
  f: (x: number, y: number) => number,
  d: Domain,
  res: number,
): Float64Array {
  const [x0, x1, y0, y1] = d
  const g = new Float64Array(res * res)
  for (let j = 0; j < res; j++) {
    const yy = y0 + ((y1 - y0) * j) / (res - 1)
    for (let i = 0; i < res; i++) {
      g[j * res + i] = f(x0 + ((x1 - x0) * i) / (res - 1), yy)
    }
  }
  return g
}

/** Shade by sigmoid(f), the deck's convention, with bilinear smoothing. */
export function paintField(fr: Frame, g: Float64Array, res: number, alpha = 0.7) {
  const off = document.createElement('canvas')
  off.width = res
  off.height = res
  const octx = off.getContext('2d')!
  const img = octx.createImageData(res, res)
  for (let j = 0; j < res; j++) {
    for (let i = 0; i < res; i++) {
      const v = 1 / (1 + Math.exp(-g[j * res + i]))
      const [r, gg, b] = rdbuR(v)
      // row 0 of the image is the top of the canvas, row 0 of g is the bottom
      const k = ((res - 1 - j) * res + i) * 4
      img.data[k] = r
      img.data[k + 1] = gg
      img.data[k + 2] = b
      img.data[k + 3] = 255
    }
  }
  octx.putImageData(img, 0, 0)
  const { ctx } = fr
  ctx.save()
  ctx.globalAlpha = alpha
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
  ctx.drawImage(off, 0, 0, fr.w, fr.h)
  ctx.restore()
}

/** Marching squares, chained into polylines so dashes look like dashes. */
export function contour(
  g: Float64Array,
  res: number,
  level: number,
  d: Domain,
): [number, number][][] {
  const [x0, x1, y0, y1] = d
  const gx = (i: number) => x0 + ((x1 - x0) * i) / (res - 1)
  const gy = (j: number) => y0 + ((y1 - y0) * j) / (res - 1)
  const segs: [[number, number], [number, number]][] = []
  const interp = (
    va: number, vb: number,
    ax: number, ay: number, bx: number, by: number,
  ): [number, number] => {
    const t = (level - va) / (vb - va)
    return [ax + t * (bx - ax), ay + t * (by - ay)]
  }
  for (let j = 0; j < res - 1; j++) {
    for (let i = 0; i < res - 1; i++) {
      const v00 = g[j * res + i]
      const v10 = g[j * res + i + 1]
      const v11 = g[(j + 1) * res + i + 1]
      const v01 = g[(j + 1) * res + i]
      const idx =
        (v00 > level ? 1 : 0) | (v10 > level ? 2 : 0) |
        (v11 > level ? 4 : 0) | (v01 > level ? 8 : 0)
      if (idx === 0 || idx === 15) continue
      const X0 = gx(i), X1 = gx(i + 1), Y0 = gy(j), Y1 = gy(j + 1)
      const bottom = () => interp(v00, v10, X0, Y0, X1, Y0)
      const right = () => interp(v10, v11, X1, Y0, X1, Y1)
      const top = () => interp(v01, v11, X0, Y1, X1, Y1)
      const left = () => interp(v00, v01, X0, Y0, X0, Y1)
      const push = (a: [number, number], b: [number, number]) => segs.push([a, b])
      switch (idx) {
        case 1: case 14: push(left(), bottom()); break
        case 2: case 13: push(bottom(), right()); break
        case 3: case 12: push(left(), right()); break
        case 4: case 11: push(right(), top()); break
        case 6: case 9: push(bottom(), top()); break
        case 7: case 8: push(left(), top()); break
        case 5: push(left(), bottom()); push(right(), top()); break
        case 10: push(left(), top()); push(bottom(), right()); break
      }
    }
  }
  return chain(segs)
}

function chain(segs: [[number, number], [number, number]][]): [number, number][][] {
  const key = (p: [number, number]) => `${p[0].toFixed(9)},${p[1].toFixed(9)}`
  const ends = new Map<string, number[]>()
  segs.forEach((s, i) => {
    for (const p of s) {
      const k = key(p)
      if (!ends.has(k)) ends.set(k, [])
      ends.get(k)!.push(i)
    }
  })
  const used = new Array(segs.length).fill(false)
  const out: [number, number][][] = []
  const grow = (path: [number, number][], forward: boolean) => {
    for (;;) {
      const tip = forward ? path[path.length - 1] : path[0]
      const next = (ends.get(key(tip)) || []).find((i) => !used[i])
      if (next === undefined) return
      used[next] = true
      const [a, b] = segs[next]
      const other = key(a) === key(tip) ? b : a
      if (forward) path.push(other)
      else path.unshift(other)
    }
  }
  for (let i = 0; i < segs.length; i++) {
    if (used[i]) continue
    used[i] = true
    const path: [number, number][] = [segs[i][0], segs[i][1]]
    grow(path, true)
    grow(path, false)
    out.push(path)
  }
  return out
}

export function strokePath(
  fr: Frame,
  paths: [number, number][][],
  color: string,
  width = 1.8,
  dash: number[] = [],
) {
  const { ctx } = fr
  ctx.save()
  ctx.strokeStyle = color
  ctx.lineWidth = width
  ctx.setLineDash(dash)
  ctx.lineJoin = 'round'
  for (const path of paths) {
    ctx.beginPath()
    path.forEach(([x, y], i) => {
      const px = fr.sx(x)
      const py = fr.sy(y)
      if (i === 0) ctx.moveTo(px, py)
      else ctx.lineTo(px, py)
    })
    ctx.stroke()
  }
  ctx.restore()
}

/** Blue circles, red triangles, green squares: one marker per class, as
 *  in the deck. */
export function drawPoints(
  fr: Frame,
  X: number[][],
  y: number[],
  size = 22,
  alpha = 1,
  palette: readonly string[] = [BLUE, RED, GREEN],
) {
  const { ctx } = fr
  const r = Math.sqrt(size / Math.PI) * 1.25
  ctx.save()
  ctx.globalAlpha = alpha
  for (let i = 0; i < X.length; i++) {
    const px = fr.sx(X[i][0])
    const py = fr.sy(X[i][1])
    const cls = y[i] < 0 ? 0 : y[i]
    ctx.fillStyle = palette[cls % palette.length]
    ctx.beginPath()
    if (cls === 1) {
      const s = r * 1.15
      ctx.moveTo(px, py - s)
      ctx.lineTo(px + s * 0.95, py + s * 0.72)
      ctx.lineTo(px - s * 0.95, py + s * 0.72)
      ctx.closePath()
    } else if (cls === 2) {
      const s = r * 0.95
      ctx.rect(px - s, py - s, 2 * s, 2 * s)
    } else {
      ctx.arc(px, py, r, 0, 2 * Math.PI)
    }
    ctx.fill()
  }
  ctx.restore()
}

/** Flat colour per winning class: the one-against-all / one-against-one maps. */
export function paintRegions(
  fr: Frame,
  labels: Int32Array,
  res: number,
  colors: readonly string[],
) {
  const off = document.createElement('canvas')
  off.width = res
  off.height = res
  const octx = off.getContext('2d')!
  const img = octx.createImageData(res, res)
  const rgbOf = colors.map((c) => {
    const m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(c)!
    return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)]
  })
  for (let j = 0; j < res; j++) {
    for (let i = 0; i < res; i++) {
      const c = rgbOf[labels[j * res + i] % rgbOf.length]
      const k = ((res - 1 - j) * res + i) * 4
      img.data[k] = c[0]
      img.data[k + 1] = c[1]
      img.data[k + 2] = c[2]
      img.data[k + 3] = 255
    }
  }
  octx.putImageData(img, 0, 0)
  const { ctx } = fr
  ctx.save()
  ctx.imageSmoothingEnabled = false
  ctx.drawImage(off, 0, 0, fr.w, fr.h)
  ctx.restore()
}

/** Open rings, the deck's way of circling support vectors / mistakes. */
export function ringPoints(
  fr: Frame,
  X: number[][],
  idx: number[],
  color = GREEN,
  size = 140,
  width = 2,
) {
  const { ctx } = fr
  const r = Math.sqrt(size / Math.PI) * 1.1
  ctx.save()
  ctx.strokeStyle = color
  ctx.lineWidth = width
  for (const i of idx) {
    ctx.beginPath()
    ctx.arc(fr.sx(X[i][0]), fr.sy(X[i][1]), r, 0, 2 * Math.PI)
    ctx.stroke()
  }
  ctx.restore()
}

/** A straight line y = a x + c across the frame. */
export function drawLine(
  fr: Frame,
  a: number,
  c: number,
  color = INK,
  width = 2,
  dash: number[] = [],
) {
  const [x0, x1] = [fr.d[0], fr.d[1]]
  strokePath(fr, [[[x0, a * x0 + c], [x1, a * x1 + c]]], color, width, dash)
}

/** The shaded street of half-width `half` (measured perpendicular). */
export function drawBand(
  fr: Frame,
  a: number,
  c: number,
  half: number,
  color: string,
  alpha = 0.3,
) {
  const [x0, x1] = [fr.d[0], fr.d[1]]
  const off = half * Math.hypot(a, 1)
  const { ctx } = fr
  ctx.save()
  ctx.globalAlpha = alpha
  ctx.fillStyle = color
  ctx.beginPath()
  ctx.moveTo(fr.sx(x0), fr.sy(a * x0 + c - off))
  ctx.lineTo(fr.sx(x1), fr.sy(a * x1 + c - off))
  ctx.lineTo(fr.sx(x1), fr.sy(a * x1 + c + off))
  ctx.lineTo(fr.sx(x0), fr.sy(a * x0 + c + off))
  ctx.closePath()
  ctx.fill()
  ctx.restore()
}

export const sigmoid = (z: number) => 1 / (1 + Math.exp(-z))
