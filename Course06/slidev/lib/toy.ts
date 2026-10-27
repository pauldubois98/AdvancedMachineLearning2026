// A one-parameter caricature of the EM landscape (make_figures_c06.py's
// _elbo_toy): an observed log-likelihood L(t), and for each anchor tb the
// surrogate F(., q^t) that touches L at tb and lies below it everywhere.
export const L = (t: number) => -0.55 * (t - 1) ** 2 + 0.22 * Math.cos(2.1 * t) - 0.22
export const dL = (t: number) => -1.1 * (t - 1) - 0.462 * Math.sin(2.1 * t)
const C = 2.4 // a curvature steep enough to minorize L
export const G = (t: number, tb: number) => L(tb) + dL(tb) * (t - tb) - C * (t - tb) ** 2
/** the top of the surrogate built at tb: the M-step */
export const argmaxG = (tb: number) => tb + dL(tb) / (2 * C)
export const T_LO = -0.9
export const T_HI = 3.0
