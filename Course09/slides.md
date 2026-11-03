---
title: |
  Session 9\
  Dimension Reduction
subtitle: |
  Advanced Machine Learning · MSc DSBA · 2026\
  \
  Paul Dubois
date: Week 8 — Lecture
---

# Dimension Reduction

## Crowding problem

![](img/crowding.png)

## No map is perfect

![](img/dr_obstacles.png)

# Reminders on PCA

## A linear projection

![](img/eq_pca_model.png)

## Example: 2D Gaussian

![](img/pca_gaussian.png)

## Two equivalent views

![](img/eq_pca_views.png)

## Algorithm

![](img/pca_algorithm.png)

## Limitation: non-linear structure

![](img/pca_nonlinear.png)

# Stochastic Neighbor Embedding

## Three steps
![](img/sne_steps.png)

## Example

![](img/sne_toy.png)

# Step 1: distances to probabilities

## Distances from one point

![](img/sne_distances.png)

## Similarity bell

![](img/sne_gaussian.png)

## Normalizing as a distribution

![](img/sne_normalise.png)

## Choosing the width σ

![](img/sigma_effect.png)

## Perplexity
![](img/eq_perplexity.png)

## Neighborhoods in the data

![](img/eq_sne_p.png)

## Probability similarity matrix
![](img/p_matrix.png)

# Step 2: initialize the map

## Random initialization

![](img/init_random.png)

## Initialization & convergence

![](img/init_choices.png)

# Step 3: measure, compare, move

## Probability similarity matrix in target space

![](img/eq_sne_q.png)

## Neighborhoods in the map

![](img/q_neighbours.png)

## Kullback–Leibler divergence

![](img/eq_kl.png)

## Asymmetry of KL in SNE

![](img/kl_asymmetry.png)

## Springs on one point

![](img/sne_forces.png)

## Gradient

![](img/eq_sne_gradient.png)

## Moving the points

![](img/sne_iterations.png)

## Compare P and Q
![](img/pq_matrices.png)

# t-SNE

## Heavy-tailed map

![](img/student_t.png)

## t-SNE principle

![](img/eq_tsne.png)

## Algorithm

![](img/tsne_algorithm.png)

## Effect of the perplexity

![](img/perplexity_effect.png)

## Initialization dependence
![](img/tsne_runs.png)

## PCA vs t-SNE

![](img/pca_vs_tsne.png)

## PCA vs t-SNE

![](img/tsne_pitfalls.png)

## PCA vs t-SNE

![](img/pca_vs_tsne_roll.png)

## PCA vs t-SNE

![](img/pca_vs_tsne_mnist.png)

## SNE vs t-SNE

![](img/sne_vs_tsne.png)
