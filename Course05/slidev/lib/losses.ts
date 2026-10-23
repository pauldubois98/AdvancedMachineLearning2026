// The entrywise divergences of the loss section, d(x, y) with x the data and
// y the model, and the beta family that holds all three.
export function dQuad(x: number, y: number) { return (x - y) ** 2 }
export function dKL(x: number, y: number) { return (x > 0 ? x * Math.log(x / y) : 0) - x + y }
export function dIS(x: number, y: number) { return x / y - Math.log(x / y) - 1 }
export function dBeta(x: number, y: number, b: number) {
  if (Math.abs(b - 1) < 1e-3) return dKL(x, y)
  if (Math.abs(b) < 1e-3) return dIS(x, y)
  return (x ** b + (b - 1) * y ** b - b * x * y ** (b - 1)) / (b * (b - 1))
}
export const range = (a: number, b: number, n: number) => Array.from({ length: n }, (_, i) => a + ((b - a) * i) / (n - 1))
